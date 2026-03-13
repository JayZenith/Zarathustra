from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from experiment_db import ExperimentDB, ExperimentRecord
from run_watcher import RunSummary, parse_run_log


REPO_ROOT = Path(__file__).resolve().parent
RUN_LOG_PATH = REPO_ROOT / "run.log"
RESULTS_TSV_PATH = REPO_ROOT / "results.tsv"


@dataclass(frozen=True)
class LoggedRun:
    commit_hash: str
    status: str
    summary: RunSummary | None
    experiment_id: int


def run_training(timeout_s: int = 720) -> int:
    completed = subprocess.run(
        f"uv run train.py > {RUN_LOG_PATH.name} 2>&1",
        shell=True,
        cwd=REPO_ROOT,
        timeout=timeout_s,
    )
    return int(completed.returncode)


def ingest_run(
    *,
    description: str,
    hypothesis: str = "",
    lesson: str = "",
    forced_status: str | None = None,
    signature: str = "",
) -> LoggedRun:
    commit_hash = _git_short_hash()
    log_text = RUN_LOG_PATH.read_text(encoding="utf-8", errors="replace") if RUN_LOG_PATH.exists() else ""
    summary = parse_run_log(log_text)

    if forced_status is not None:
        status = forced_status
    elif summary is None:
        status = "crash"
    else:
        status = _default_status(summary.val_bpb)

    val_bpb = 0.0 if summary is None else summary.val_bpb
    memory_gb = 0.0 if summary is None else round(summary.peak_vram_mb / 1024.0, 1)

    db = ExperimentDB()
    try:
        experiment_id = db.add_experiment(
            ExperimentRecord(
                commit_hash=commit_hash,
                val_bpb=val_bpb,
                memory_gb=memory_gb,
                status=status,
                description=description,
                signature=signature or _infer_signature(description, hypothesis),
                hypothesis=hypothesis,
                lesson=lesson,
            )
        )
    finally:
        db.close()

    _append_results_tsv(
        commit_hash=commit_hash,
        val_bpb=val_bpb,
        memory_gb=memory_gb,
        status=status,
        description=description,
    )
    return LoggedRun(
        commit_hash=commit_hash,
        status=status,
        summary=summary,
        experiment_id=experiment_id,
    )


def _default_status(val_bpb: float) -> str:
    db = ExperimentDB()
    try:
        best = db.best_experiment()
    finally:
        db.close()
    if best is None:
        return "keep"
    return "keep" if val_bpb < float(best["val_bpb"]) else "discard"


def _append_results_tsv(
    *,
    commit_hash: str,
    val_bpb: float,
    memory_gb: float,
    status: str,
    description: str,
) -> None:
    if not RESULTS_TSV_PATH.exists() or RESULTS_TSV_PATH.stat().st_size == 0:
        RESULTS_TSV_PATH.write_text("commit\tval_bpb\tmemory_gb\tstatus\tdescription\n", encoding="utf-8")
    with RESULTS_TSV_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{commit_hash}\t{val_bpb:.6f}\t{memory_gb:.1f}\t{status}\t{description}\n")


def _git_short_hash() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() or "nogit"


def _infer_signature(description: str, hypothesis: str) -> str:
    text = f"{description} {hypothesis}".lower()
    if "matrix_lr" in text or "matrix lr" in text:
        if any(term in text for term in ("lower", "less", "decrease", "reduce")):
            return "param:MATRIX_LR:down"
        if any(term in text for term in ("higher", "increase", "raise")):
            return "param:MATRIX_LR:up"
        return "param:MATRIX_LR"
    if "warmdown" in text:
        if any(term in text for term in ("higher", "increase", "longer", "more")):
            return "param:WARMDOWN_RATIO:up"
        if any(term in text for term in ("lower", "decrease", "reduce", "shorter", "less")):
            return "param:WARMDOWN_RATIO:down"
        return "param:WARMDOWN_RATIO"
    if "weight_decay" in text or "weight decay" in text or "wd" in text:
        if any(term in text for term in ("lower", "decrease", "reduce", "less")):
            return "param:WEIGHT_DECAY:down"
        if any(term in text for term in ("higher", "increase", "raise", "more")):
            return "param:WEIGHT_DECAY:up"
        return "param:WEIGHT_DECAY"
    if "embedding_lr" in text or "embedding lr" in text:
        if any(term in text for term in ("lower", "decrease", "reduce", "ablate", "less")):
            return "param:EMBEDDING_LR:down"
        if any(term in text for term in ("higher", "increase", "raise", "more")):
            return "param:EMBEDDING_LR:up"
        return "param:EMBEDDING_LR"
    if "final_lr" in text or "final lr" in text:
        if any(term in text for term in ("lower", "decrease", "reduce", "less")):
            return "param:FINAL_LR_FRAC:down"
        if any(term in text for term in ("higher", "increase", "raise", "more")):
            return "param:FINAL_LR_FRAC:up"
        return "param:FINAL_LR_FRAC"
    if "silu" in text or "relu" in text or "swiglu" in text:
        if "silu" in text:
            return "activation:SILU"
        if "swiglu" in text:
            return "activation:SWIGLU"
        return "activation"
    return ""
