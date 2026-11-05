#!/usr/bin/env bash
# #1138 Tripo GLB → 게임 판 단계본 (0크레딧) — 몸마다 인자만 다르다 (흑랑 post_tripo.sh 일반화)
# 쓰기: BODY=bulgasari NAME=불가살이 ID=boss_bulgasari MDSCALE=2.86 RIG="--windup=0.5 ..." RW="--body-reach 2.4" EXTRA="python tools/bulgasari_clips.py --stride 0.68" \
#       bash post_tripo2.sh <tripo.glb> <yaw> <scale>
set -euo pipefail
SRC="$1"; YAW="${2:-0}"; SCALE="${3:-1}"
WT=/c/workspace/joseon/.claude/worktrees/1036-claude-play-2ef896
OUT=/c/workspace/joseon-assets/workbench/production/1138_${BODY}/glb
OUTW="C:/workspace/joseon-assets/workbench/production/1138_${BODY}/glb"
BL="/e/SteamLibrary/steamapps/common/Blender/blender.exe"
mkdir -p "$OUT"
cd "$WT"
flt() { grep -v "^\[DevMode\]\|godot_ai\|ObjectDB\|resources still\|at: \|^Godot Engine" ; }
echo "== 1 정면·크기·바닥·가운데 (bake_transform yaw=$YAW scale=$SCALE)"
godot --headless -s tools/bake_transform.gd -- --src="$SRC" --out="$OUTW/s1_baked.glb" --yaw="$YAW" --scale="$SCALE" --floor --center 2>&1 | flt | tail -4
echo "== 2 감량·텍스처 1024 (decimate 12000)"
"$BL" --background --factory-startup --python tools/blender/decimate_glb.py -- --src="$OUTW/s1_baked.glb" --out="$OUTW/s2_dec.glb" --tris=12000 --tex=1024 --floor --center 2>&1 | grep -E "==|WARN|tri|Error|error" | tail -5
echo "== 3 네발 리그 + v2 클립 (rig_quadruped $RIG)"
"$BL" --background --factory-startup --python tools/blender/rig_quadruped.py -- --src="$OUTW/s2_dec.glb" --out="$OUTW/s3_rig.glb" --name="$NAME" $RIG --paw-frac=0.05 --paw-split=cluster --weights=limb 2>&1 | grep -E "^==|WARN|경고|Error|error|못|forward|정면" | tail -14
echo "== 4 가중치 limb 다시 칠하기 (Tripo 메시 = 열 가중치가 붙어 limb를 건너뛴다 — LESSONS #1138) $RW"
python tools/quad_rig.py reweight --glb "$OUTW/s3_rig.glb" --out "$OUTW/s4_limb.glb" --mode limb --paw-frac 0.05 --paw-split cluster ${RW:-} 2>&1 | tail -4
CUR="$OUTW/s4_limb.glb"
if [ -n "${EXTRA:-}" ]; then
  echo "== 4b 추가 클립: $EXTRA"
  $EXTRA --glb "$CUR" --out "$OUTW/s4b_clips.glb" 2>&1 | tail -6
  CUR="$OUTW/s4b_clips.glb"
fi
echo "== 5 알베도 1024 · 무광"
python tools/albedo_ops.py shrink --glb "$CUR" --out "$OUTW/s5_final.glb" --max 1024 --name basecolor 2>&1 | tail -2
python tools/albedo_ops.py matte --glb "$OUTW/s5_final.glb" 2>&1 | tail -2
echo "== 6 늘어남 · 클립"
python tools/quad_rig.py stretch --glb "$OUTW/s5_final.glb" 2>&1 | tail -12
echo "== 7 ModelDef 값 (measure · scale $MDSCALE)"
python tools/quad_gait.py measure --glb "$OUTW/s5_final.glb" --scale "$MDSCALE" ${MEASURE:-} 2>&1 | tail -12
