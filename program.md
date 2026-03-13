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
- choose better next experiments from evidence

Focus on:
1. recording every experiment cleanly
2. writing what was learned
3. avoiding repeated failed ideas
4. proposing the next experiment from evidence

Paper workflow:
- First query stored paper notes by topic.
- Only search for papers when a concrete bottleneck appears or notes are missing.
- Store every useful paper summary back into the database.
- Do not browse papers broadly during productive local optimization.

All tool usage should go through `python3 cli.py ...`.

Training workflow:
- `prepare.py` is fixed. Do not modify it.
- `train.py` is the mutable surface.
- Run training with `uv run train.py > run.log 2>&1`.
- Parse results from `run.log`.
- Log experiment outcomes into `experiments.db`.
