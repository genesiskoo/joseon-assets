#!/usr/bin/env bash
# #1138 새 몸 녹화 — 이 작업 트리에서만 잠깐 바꿔 끼우고(커밋 안 함) 녹화한 뒤 반드시 되돌린다.
set -uo pipefail
WT=/c/workspace/joseon/.claude/worktrees/1036-claude-play-2ef896
S="${S:?scratchpad 폴더 (rec_tour.py · rec/ 가 있는 곳)}"
NEW="C:/workspace/joseon-assets/workbench/production/1138_heukrang/glb/s7_slate.glb"
cd "$WT"
restore() {
  echo "== 되돌리기"
  git checkout -- assets/models/boss_heukrang data/models/boss_heukrang.tres
  git clean -fq assets/models/boss_heukrang
  godot --headless --import >/dev/null 2>&1
  git status --short assets/models/boss_heukrang data/models/boss_heukrang.tres
  echo "== 되돌림 끝 ($(git status --short | wc -l) 줄 바뀜)"
}
trap restore EXIT
cp "$NEW" assets/models/boss_heukrang/boss_heukrang.glb
python - "$WT/data/models/boss_heukrang.tres" <<'PY'
import sys, re
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t = re.sub(r"^walk_speed = .*$", "walk_speed = 1.179", t, flags=re.M)
t = re.sub(r"^run_speed = .*$", "run_speed = 4.572", t, flags=re.M)
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("tres: walk 1.179 · run 4.572 (step_phases 같음)")
PY
echo "== import"
godot --headless --import 2>&1 | grep -iE "error|fail" | head -5
ls assets/models/boss_heukrang/
echo "== 녹화 (새 몸)"
PYTHONIOENCODING=utf-8 python "$S/rec_tour.py" . new "$S/rec"
