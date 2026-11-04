#!/usr/bin/env bash
# #1138 Tripo GLB → 게임 판 단계본 (0크레딧): 정면·크기 굽기 → 감량·텍스처 → 네발 리그 + v2 클립 → ModelDef 값 재기
# 쓰기: bash post_tripo.sh <tripo.glb> <yaw> <scale>
set -euo pipefail
SRC="$1"; YAW="${2:-0}"; SCALE="${3:-1}"
WT=/c/workspace/joseon/.claude/worktrees/1036-claude-play-2ef896
OUT=/c/workspace/joseon-assets/workbench/production/1138_heukrang/glb
BL="/e/SteamLibrary/steamapps/common/Blender/blender.exe"
mkdir -p "$OUT"
cd "$WT"
echo "== 1 정면·크기·바닥·가운데 (bake_transform, yaw=$YAW scale=$SCALE)"
godot --headless -s tools/bake_transform.gd -- --src="$SRC" --out="$OUT/s1_baked.glb" --yaw="$YAW" --scale="$SCALE" --floor --center 2>&1 | grep -v "^\[DevMode\]\|godot_ai\|ObjectDB\|resources still\|at: " | tail -6
echo "== 2 감량·텍스처 1024 (decimate_glb, 12000)"
"$BL" --background --factory-startup --python tools/blender/decimate_glb.py -- --src="$OUT/s1_baked.glb" --out="$OUT/s2_dec.glb" --tris=12000 --tex=1024 --floor --center 2>&1 | grep -E "==|WARN|tri|ratio|Error|error" | tail -8
echo "== 3 네발 리그 + v2 클립 (rig_quadruped — #512 털 몸 길 + 흑랑 굽기 인자 #506)"
"$BL" --background --factory-startup --python tools/blender/rig_quadruped.py -- --src="$OUT/s2_dec.glb" --out="$OUT/s3_rig.glb" --name=흑랑 \
  --windup=0.4 --pounce-windup=0.5 --walk-tempo=1.2 --run-tempo=1.4 --paw-frac=0.05 --paw-split=cluster --weights=limb 2>&1 | grep -E "^==|WARN|경고|Error|error|못" | tail -30
echo "== 4 ModelDef 값 (quad_gait bake 다시 = 같은 값 · --scale 2.2)"
python tools/quad_gait.py bake --glb "$OUT/s3_rig.glb" --out "$OUT/s4_baked.glb" --windup 0.4 --pounce-windup 0.5 --walk-tempo 1.2 --run-tempo 1.4 --scale 2.2 --json "$OUT/s4_bake_report.json" > /dev/null
python -c "import json;r=json.load(open(r'$OUT/s4_bake_report.json',encoding='utf-8'));print(json.dumps(r['modeldef'],ensure_ascii=False));print(json.dumps(r.get('gallery',{}),ensure_ascii=False)[:600])"
echo "== 5 늘어남 · model_check"
python tools/quad_rig.py stretch --glb "$OUT/s4_baked.glb" 2>&1 | tail -14
godot --headless -s tools/model_check.gd -- "$OUT/s4_baked.glb" --id=boss_heukrang 2>&1 | grep -v "^\[DevMode\]\|godot_ai\|ObjectDB\|resources still\|at: \|^Godot Engine" | tail -16
