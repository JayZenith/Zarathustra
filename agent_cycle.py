from __future__ import annotations

import argparse

from next_experiment import choose_next_experiment
from research_memory import summarize_recent
from rule_engine import decide_next_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print the next zarathustra agent cycle.")
    parser.add_argument("--limit", type=int, default=8, help="How many recent experiments to summarize.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    recent = summarize_recent(limit=args.limit)
    decision = decide_next_action()
    idea = choose_next_experiment()

    print("=== Recent Experiments ===")
    print(recent)
    print()
    print("=== Rule Decision (Advisory) ===")
    print(f"action: {decision.action}")
    print(f"topic: {decision.topic}")
    print(f"reason: {decision.reason}")
    print()
    print("=== Next Agent Actions (Advisory) ===")

    if decision.action == "exploit":
        print(f"1. Stay local in topic: {decision.topic}")
        print("2. Make one small ablation or refinement around the current winning direction.")
        if idea is not None:
            print(f"3. Candidate fallback idea: {idea.description}")
            print(f"   hypothesis: {idea.hypothesis}")
    elif decision.action == "read_notes":
        print(f"1. Read stored paper notes for topic: {decision.topic}")
        print(f"   command: python3 cli.py paper-notes --topic {decision.topic}")
        print("2. Use those notes to propose one concrete train.py edit.")
    elif decision.action == "search_papers":
        print(f"1. Search papers for topic: {decision.topic}")
        print(
            "   command: python3 cli.py paper-search-store "
            f'--query "{decision.topic} transformer short training runs" --topic {decision.topic}'
        )
        print("2. Read the stored notes.")
        print(f"   command: python3 cli.py paper-notes --topic {decision.topic}")
        print("3. Use one paper-backed idea to modify train.py.")
    else:
        print("1. Explore a new small direction.")
        if idea is not None:
            print(f"2. Suggested fallback idea: {idea.description}")
            print(f"   hypothesis: {idea.hypothesis}")

    if idea is not None and decision.action in {"exploit", "explore"}:
        print(f"Fallback idea: {idea.description}")
        print(f"Fallback hypothesis: {idea.hypothesis}")

    print()
    print("=== Training Command ===")
    print(
        'python3 one_cycle.py --description "<what changed>" '
        '--hypothesis "<why this might help>"'
    )
    print()
    print("=== Compact Brief Command ===")
    print("python3 agent_brief.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
