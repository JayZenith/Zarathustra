from __future__ import annotations

import argparse

from next_experiment import choose_next_experiment
from research_memory import summarize_recent
from rule_engine import decide_next_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a compact zarathustra agent brief.")
    parser.add_argument("--limit", type=int, default=6)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    recent = summarize_recent(limit=args.limit)
    decision = decide_next_action()
    idea = choose_next_experiment()

    print("Recent:")
    print(recent)
    print()
    print(f"Decision: {decision.action} | topic={decision.topic}")
    print(f"Reason: {decision.reason}")
    if idea is not None:
        print()
        print(f"Suggested idea: {idea.description}")
        print(f"Hypothesis: {idea.hypothesis}")
    print()
    print("Required commands:")
    print("1. python3 agent_cycle.py")
    print('2. edit train.py')
    print('3. python3 one_cycle.py --description "<change>" --hypothesis "<why>"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
