# zarathustra tools

Use these commands from `/home/jay-zenith/Desktop/zarathustra`.

## Agent glue

Print the current research state and next actions:

```bash
python3 agent_cycle.py
python3 agent_brief.py
```

## Training run

Run one actual training cycle:

```bash
python3 one_cycle.py --description "batch reduction test" --hypothesis "more steps help on A100"
```

If training was run separately and only the log needs to be recorded:

```bash
python3 cli.py ingest-run --description "batch reduction test" --hypothesis "more steps help on A100"
```

## Experiment memory

```bash
python3 cli.py log-experiment --commit abc1234 --val-bpb 1.041706 --memory-gb 30.4 --status keep --description "halve batch" --hypothesis "more steps help on A100" --lesson "batch reduction improved bpb"
```

```bash
python3 cli.py recent
python3 cli.py next-experiment
python3 cli.py decide
```

## Research notes

```bash
python3 cli.py record-lesson --topic optimizer --hypothesis "more steps help" --outcome improved --lesson "batch reduction improved bpb"
```

## Paper workflow

Check stored notes first:

```bash
python3 cli.py paper-notes --topic optimizer
```

Search ArXiv only when bottlenecked:

```bash
python3 cli.py paper-search --query "transformer optimizer warmup short training runs"
python3 cli.py paper-search-store --query "transformer optimizer warmup short training runs" --topic optimizer
```

Fetch one paper directly:

```bash
python3 cli.py paper-fetch --url "https://arxiv.org/abs/2401.00001"
python3 cli.py paper-fetch-store --url "https://arxiv.org/abs/2401.00001" --topic optimizer
```

## Rules

- Use `python3 cli.py decide` after each experiment block.
- Prefer `python3 agent_cycle.py` as the main entrypoint for the live loop.
- If decision is `exploit`, stay local around the winning change.
- If decision is `read_notes`, query stored notes before more edits.
- If decision is `search_papers`, run a narrow search tied to the bottleneck topic.
- Do not browse papers broadly when local optimization is still working.
