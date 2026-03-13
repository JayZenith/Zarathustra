# zarathustra runtime

This is the narrow live loop for the agent.

## Cycle

1. Read the current state:

```bash
python3 agent_cycle.py
```

2. Decide the next `train.py` edit from the printed actions.
   Treat them as suggestions, not commands.

3. Make the edit in `train.py`.

4. Commit the code change.

5. Run one training cycle:

```bash
python3 one_cycle.py --description "<what changed>" --hypothesis "<why this might help>" --lesson "<what this result would mean>"
```

6. Read the new state again:

```bash
python3 agent_cycle.py
python3 loop_controller.py show
```

7. Repeat.

## External loop

If your agent CLI does not stay alive by itself, use:

```bash
python3 prompt_builder.py
python3 agent_runtime.py --agent-cmd 'claude -p "$(cat {prompt_file})"' --cycles 5
```

This is the narrow runtime glue:
- refresh state
- build prompt from repo files
- invoke the agent CLI
- let the agent do exactly one cycle
- repeat

## Rules

- Always run `python3 agent_cycle.py` before a new edit.
- Always run `python3 one_cycle.py ...` after a committed edit.
- Always include a concrete `--lesson` when running `python3 one_cycle.py ...`.
- After every run, read `AGENT_HANDOFF.md` or run `python3 agent_cycle.py`.
- Use paper tools when bottlenecked, missing context, or deepening a promising direction.
- Keep edits small unless the evidence clearly supports a larger move.
- Override the rule engine when the evidence contradicts it.
