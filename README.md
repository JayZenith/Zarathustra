# zarathustra

`zarathustra` is an `autoresearch`-style training repo with stricter research
memory.

It directly contains the training target:

- `prepare.py` — fixed data prep and evaluation
- `train.py` — mutable training file

And it adds:

- `experiments.db` for durable experiment memory
- structured observations and lessons
- run log parsing
- next-experiment suggestion
- targeted paper search/fetch/summarization

## Main files

- `prepare.py` — fixed training prep/eval
- `train.py` — the file the agent edits
- `program.md` — main agent instructions
- `tools.md` — exact CLI tools and rules
- `cli.py` — entrypoint for research memory and paper tools
- `experiment_db.py` — SQLite schema and access layer
- `rule_engine.py` — exploit vs explore vs paper lookup

## Scope

This project is intentionally narrow:

- one training target
- one mutable training file
- one experiment database
- targeted paper use only when needed

No UI, no provider abstraction, no generic agent platform.
