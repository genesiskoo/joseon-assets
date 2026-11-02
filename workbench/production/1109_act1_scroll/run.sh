#!/bin/bash
# #1109 1막 두루마리판 새 겹 — 한 장씩 순서대로, 실패하면 한 번 더
C="$(cd "$(dirname "$0")" && pwd)"; R="C:/Users/FORYOU~1/AppData/Local/Temp/claude/C--workspace-joseon/d9053215-8579-45d5-96d9-055c3ad8ca14/scratchpad"
L01="C:/workspace/joseon-assets/workbench/production/1099_story_scroll/clean/L01_landscape.png"
HEAD="Use your built-in image generation tool to create ONE image and save it as a PNG in the current folder with the exact file name given below. You may read your own image-generation skill instructions. Do not write code. Generate once, save, and stop."
JOBS=${@:-A1_chain_seal A2_sansin_tiger A3_road A4_far_village A5_far_people A6_smoke_fox A7_smoke_shapes A8_smoke_trail A9_footprints}
for job in $JOBS; do
  D="$C/out/$job"; mkdir -p "$D"; cd "$D"
  case $job in
    A3_*|A4_*) cp "$L01" style_ref.png; IMGS=(-i style_ref.png);;
    A5_*|A7_*) cp "$R/board/img/liangkai_immortal.jpg" "$R/board/img/kim_giryeo.jpg" . 2>/dev/null; IMGS=(-i liangkai_immortal.jpg -i kim_giryeo.jpg);;
    *) IMGS=();;
  esac
  P="$HEAD

$(cat "$C/$job.txt")

$(cat "$C/common.txt")"
  for try in 1 2; do
    echo "=== $job try$try $(date +%T)"
    timeout 600 codex exec --skip-git-repo-check -s workspace-write -m gpt-5.6-sol -c service_tier=default "$P" "${IMGS[@]}" > log$try.txt 2>&1
    [ -f "$job.png" ] && break
  done
  if [ -f "$job.png" ]; then echo "$job OK $(sha256sum "$job.png" | cut -c1-16)"; else echo "$job MISSING"; tail -3 log2.txt; fi
done
echo "=== done $(date +%T)"
