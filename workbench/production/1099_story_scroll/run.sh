#!/bin/bash
# #1099 이야기 두루마리 겹 — 한 장씩 순서대로, 실패하면 한 번 더
C="$(cd "$(dirname "$0")" && pwd)"; B="$C/../board/img"; V="$C/../concept/v3/s0/s0.png"
HEAD="Use your built-in image generation tool to create ONE image and save it as a PNG in the current folder with the exact file name given below. You may read your own image-generation skill instructions. Do not write code. Generate once, save, and stop."
JOBS=${@:-L01_landscape L02_village L03_villagers L04_jumo_child L05_hound L06_tiger L07_bulgasari L08_chain_broken L09_slashes L10_nine_streams L11_doho_pass L12_doho_cave L13_doho_leave}
for job in $JOBS; do
  D="$C/out/$job"; mkdir -p "$D"; cd "$D"
  case $job in
    L01_*) cp "$V" layout_s0.png; cp "$B/inwang.jpg" .; IMGS=(-i layout_s0.png -i inwang.jpg);;
    L02_*) cp "$V" layout_s0.png; IMGS=(-i layout_s0.png);;
    L03_*|L04_*|L11_*|L12_*|L13_*) cp "$B/liangkai_immortal.jpg" "$B/kim_giryeo.jpg" .; IMGS=(-i liangkai_immortal.jpg -i kim_giryeo.jpg);;
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
