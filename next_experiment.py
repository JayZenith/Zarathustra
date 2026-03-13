from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from experiment_db import DEFAULT_DB_PATH, ExperimentDB
from rule_engine import decide_next_action


@dataclass(frozen=True)
class ExperimentIdea:
    description: str
    hypothesis: str
    topic: str


IDEAS = [
    ExperimentIdea(
        description="slightly lower matrix learning rate",
        hypothesis="A100 may prefer a less aggressive matrix LR because step count is lower than H100.",
        topic="optimizer",
    ),
    ExperimentIdea(
        description="slightly higher warmdown ratio",
        hypothesis="Longer high-LR time before decay may improve short-budget results.",
        topic="schedule",
    ),
    ExperimentIdea(
        description="small weight decay reduction",
        hypothesis="The current run may be slightly over-regularized under a fixed 5-minute budget.",
        topic="regularization",
    ),
    ExperimentIdea(
        description="ablate embedding learning rate",
        hypothesis="Embedding LR may be higher leverage than broader architecture changes at this scale.",
        topic="optimizer",
    ),
    ExperimentIdea(
        description="slightly lower final learning rate fraction",
        hypothesis="A gentler ending LR may reduce final-run instability in fixed-time training.",
        topic="schedule",
    ),
    ExperimentIdea(
        description="test one simpler activation swap",
        hypothesis="Activation shape may improve optimization without widening the model.",
        topic="architecture",
    ),
]


def choose_next_experiment(db_path: Path = DEFAULT_DB_PATH) -> ExperimentIdea | None:
    db = ExperimentDB(db_path)
    try:
        decision = decide_next_action(db_path=db_path)
        recent = db.recent_experiments(limit=12)
        tried = {row["description"] for row in recent}
        rejected_topics = _recent_rejected_topics(db, recent)

        preferred_topics = _topic_priority(decision.topic)
        for topic in preferred_topics:
            if topic in rejected_topics and topic == decision.topic:
                continue
            for idea in IDEAS:
                if idea.topic != topic:
                    continue
                if idea.description in tried:
                    continue
                return idea

        for idea in IDEAS:
            if idea.topic in rejected_topics:
                continue
            if idea.description not in tried:
                return idea
        return None
    finally:
        db.close()


def _topic_priority(primary: str) -> tuple[str, ...]:
    order = ["optimizer", "schedule", "regularization", "architecture", "general"]
    if primary in order:
        return tuple([primary] + [topic for topic in order if topic != primary])
    return tuple(order)


def _recent_rejected_topics(db: ExperimentDB, recent: list[object]) -> set[str]:
    rejected: set[str] = set()
    for row in recent[:4]:
        if row["status"] != "discard":  # type: ignore[index]
            continue
        topic = _infer_topic(row["description"])  # type: ignore[index]
        rejected.add(topic)

    for topic in list(rejected):
        notes = db.observations_by_topic(topic, limit=3)
        text = " ".join(row["note"].lower() for row in notes)
        if any(term in text for term in ("not supported", "worse", "hurt", "avoid")):
            rejected.add(topic)
    return rejected


def _infer_topic(description: str) -> str:
    text = description.lower()
    if any(term in text for term in ("lr", "beta", "momentum", "muon", "adam", "embedding")):
        return "optimizer"
    if any(term in text for term in ("warm", "schedule", "decay", "final_lr")):
        return "schedule"
    if any(term in text for term in ("wd", "weight decay", "regular")):
        return "regularization"
    if any(term in text for term in ("depth", "glu", "relu", "silu", "rope", "window")):
        return "architecture"
    return "general"
