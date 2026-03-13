# zarathustra

Use this repo as the training research repo.

Read:
- `README.md`
- `prepare.py`
- `train.py`
- `tools.md`
- `program.md`

Goal:
- keep durable experiment memory
- record explicit hypotheses and lessons
- support better research from evidence

Focus on:
1. recording every experiment cleanly
2. writing what was learned
3. avoiding repeated failed ideas
4. using recent evidence to choose the next experiment yourself

Paper workflow:
- First query stored paper notes by topic.
- Search for papers when a concrete bottleneck appears, notes are missing, or a promising direction needs deeper grounding.
- Store every useful paper summary back into the database.
- Do not browse papers broadly during productive local optimization.

All tool usage should go through `python3 cli.py ...`.
Use `python3 agent_cycle.py` at the start of each research cycle.

Training workflow:
- `prepare.py` is fixed. Do not modify it.
- `train.py` is the mutable surface.
- Run training with `uv run train.py > run.log 2>&1`.
- Parse results from `run.log`.
- Log experiment outcomes into `experiments.db`.
- Every experiment must include an explicit lesson.
- When running `python3 one_cycle.py ...`, always pass:
  - `--description`
  - `--hypothesis`
  - `--lesson`

Decision policy:
- The repo provides memory, retrieval, and logging.
- You choose the next experiment from the evidence.
- The hard requirements are memory, logging, and evidence-based reasoning.
