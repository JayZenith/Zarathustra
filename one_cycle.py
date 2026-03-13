from __future__ import annotations

import argparse

from experiment_runner import ingest_run, run_training


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one zarathustra training cycle.")
    parser.add_argument("--description", required=True)
    parser.add_argument("--hypothesis", default="")
    parser.add_argument("--lesson", default="")
    parser.add_argument("--timeout", type=int, default=720)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    exit_code = run_training(timeout_s=args.timeout)
    result = ingest_run(
        description=args.description,
        hypothesis=args.hypothesis,
        lesson=args.lesson if exit_code == 0 else "training run crashed or failed to produce a summary",
    )
    print(result)
    return 0 if exit_code == 0 else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
