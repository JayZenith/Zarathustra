from __future__ import annotations

import argparse

from experiment_db import ExperimentDB, ExperimentRecord
from experiment_runner import ingest_run
from next_experiment import choose_next_experiment
from paper_fetch import fetch_arxiv_entry
from paper_notes import fetch_and_store, find_notes, search_and_store
from paper_search import search_arxiv
from paper_summarize import format_summary, summarize_paper
from research_memory import record_lesson, summarize_recent
from rule_engine import decide_next_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="zarathustra research tools")
    sub = parser.add_subparsers(dest="command", required=True)

    log_exp = sub.add_parser("log-experiment")
    log_exp.add_argument("--commit", required=True)
    log_exp.add_argument("--val-bpb", type=float, required=True)
    log_exp.add_argument("--memory-gb", type=float, required=True)
    log_exp.add_argument("--status", required=True, choices=("keep", "discard", "crash"))
    log_exp.add_argument("--description", required=True)
    log_exp.add_argument("--signature", default="")
    log_exp.add_argument("--hypothesis", default="")
    log_exp.add_argument("--lesson", default="")

    note = sub.add_parser("record-lesson")
    note.add_argument("--topic", required=True)
    note.add_argument("--hypothesis", required=True)
    note.add_argument("--outcome", required=True)
    note.add_argument("--lesson", required=True)
    note.add_argument("--experiment-id", type=int)

    recent = sub.add_parser("recent")
    recent.add_argument("--limit", type=int, default=8)

    nxt = sub.add_parser("next-experiment")

    decide = sub.add_parser("decide")

    search = sub.add_parser("paper-search")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)

    store = sub.add_parser("paper-search-store")
    store.add_argument("--query", required=True)
    store.add_argument("--topic", required=True)
    store.add_argument("--limit", type=int, default=3)

    fetch = sub.add_parser("paper-fetch")
    fetch.add_argument("--url", required=True)

    fetch_store = sub.add_parser("paper-fetch-store")
    fetch_store.add_argument("--url", required=True)
    fetch_store.add_argument("--topic", required=True)

    notes = sub.add_parser("paper-notes")
    notes.add_argument("--topic", required=True)

    summarize = sub.add_parser("paper-summarize")
    summarize.add_argument("--title", required=True)
    summarize.add_argument("--abstract", required=True)
    summarize.add_argument("--topic", required=True)

    ingest = sub.add_parser("ingest-run")
    ingest.add_argument("--description", required=True)
    ingest.add_argument("--signature", default="")
    ingest.add_argument("--hypothesis", default="")
    ingest.add_argument("--lesson", default="")
    ingest.add_argument("--status", choices=("keep", "discard", "crash"))

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "log-experiment":
        db = ExperimentDB()
        try:
            exp_id = db.add_experiment(
                ExperimentRecord(
                    commit_hash=args.commit,
                    val_bpb=args.val_bpb,
                    memory_gb=args.memory_gb,
                    status=args.status,
                    description=args.description,
                    signature=args.signature,
                    hypothesis=args.hypothesis,
                    lesson=args.lesson,
                )
            )
        finally:
            db.close()
        print(exp_id)
        return 0

    if args.command == "record-lesson":
        record_lesson(
            topic=args.topic,
            hypothesis=args.hypothesis,
            outcome=args.outcome,
            lesson=args.lesson,
            experiment_id=args.experiment_id,
        )
        return 0

    if args.command == "recent":
        print(summarize_recent(limit=args.limit))
        return 0

    if args.command == "next-experiment":
        idea = choose_next_experiment()
        print(idea)
        return 0

    if args.command == "decide":
        print(decide_next_action())
        return 0

    if args.command == "paper-search":
        for candidate in search_arxiv(args.query, limit=args.limit):
            print(f"{candidate.title}\n{candidate.url}\n{candidate.published}\n")
        return 0

    if args.command == "paper-search-store":
        for candidate in search_and_store(query=args.query, topic=args.topic, limit=args.limit):
            print(candidate.title)
        return 0

    if args.command == "paper-fetch":
        paper = fetch_arxiv_entry(args.url)
        print(paper)
        return 0

    if args.command == "paper-fetch-store":
        fetch_and_store(url=args.url, topic=args.topic)
        print("stored")
        return 0

    if args.command == "paper-notes":
        for note in find_notes(args.topic):
            print(note)
            print()
        return 0

    if args.command == "paper-summarize":
        print(format_summary(summarize_paper(title=args.title, abstract=args.abstract, topic=args.topic)))
        return 0

    if args.command == "ingest-run":
        print(
            ingest_run(
                description=args.description,
                signature=args.signature,
                hypothesis=args.hypothesis,
                lesson=args.lesson,
                forced_status=args.status,
            )
        )
        return 0

    parser.error("unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
