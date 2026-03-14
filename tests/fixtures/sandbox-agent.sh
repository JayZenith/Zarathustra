#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$ZARATHUSTRA_PROGRAM")" && pwd)"
STATE_FILE=".zar_agent_state"
RUN_LOG="run.log"

cat "$ZARATHUSTRA_HANDOFF" >/dev/null

if [[ ! -f "$STATE_FILE" ]]; then
  python3 train.py | tee "$RUN_LOG"
  bun run "$ROOT/src/cli/index.ts" experiment-log '{"hypothesis":"sandbox baseline","status":"completed","change_summary":"baseline config","primary_metric":"val_loss","metrics":{"val_loss":0.373686,"val_acc":0.875000,"runtime_sec":0.126}}'
  python3 - <<'PY'
import json
from pathlib import Path
p = Path("config.json")
cfg = json.loads(p.read_text())
cfg["hidden_size"] = 24
cfg["epochs"] = 240
cfg["learning_rate"] = 0.06
cfg["weight_decay"] = 0.0
p.write_text(json.dumps(cfg, indent=2) + "\n")
PY
  echo first > "$STATE_FILE"
  exit 0
fi

python3 train.py | tee "$RUN_LOG"
bun run "$ROOT/src/cli/index.ts" experiment-log '{"hypothesis":"sandbox tuned config","status":"completed","change_summary":"hidden_size 24, epochs 240, lr 0.06, wd 0.0","primary_metric":"val_loss","metrics":{"val_loss":0.250231,"val_acc":0.875000,"runtime_sec":0.538}}'
echo next > "$STATE_FILE"
