from __future__ import annotations

import argparse

from experiment_db import ExperimentDB
from research_memory import summarize_recent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print the current zarathustra research state.")
    parser.add_argument("--limit", type=int, default=8, help="How many recent experiments to summarize.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    recent = summarize_recent(limit=args.limit)
    db = ExperimentDB()
    try:
        best = db.best_experiment()
    finally:
        db.close()

    print("=== Recent Experiments ===")
    print(recent)
    print()
    print("=== Current Best ===")
    if best is None:
        print("No experiments logged yet.")
    else:
        print(f'val_bpb: {float(best["val_bpb"]):.6f}')
        print(f'status: {best["status"]}')
        print(f'description: {best["description"]}')
        if best["lesson"]:
            print(f'lesson: {best["lesson"]}')
    print()
    print("=== Research Reminders ===")
    print("1. Use recent experiments, lessons, and paper notes as evidence.")
    print("2. Choose the next edit yourself; the repo does not prescribe it.")
    print("3. Record a concrete lesson every run.")
    print("4. Query paper notes or search papers when evidence is weak or bottlenecked.")

    print()
    print("=== Training Command ===")
    print(
        'python3 one_cycle.py --description "<what changed>" '
        '--hypothesis "<why this might help>" '
        '--lesson "<what was learned>"'
    )
    print()
    print("=== Useful Commands ===")
    print("python3 cli.py recent")
    print("python3 cli.py paper-notes --topic <topic>")
    print('python3 cli.py paper-search-store --query "<query>" --topic <topic>')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
