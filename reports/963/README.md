# #963 렌더 효과 실험장 P1 — 6자리 전체 촬영 (2026-10-28)

게임 저장소 `tools/render_lab.py` 결과. 효과 하나만 껐다 켜서 같은 자리·같은 카메라로 찍었다(33쌍).

- `video/<자리>__<효과>__side.mp4` — 같은 판에서 두 번 찍은 끔 | 켬 나란히 (웹용 다시 굽기, 1920폭 crf 27)
- `video/<자리>__<효과>__blink.mp4` — 한 판 안에서 1.5초마다 끔↔켬 (1280폭)
- `manifest.json` — 효과·자리·파일 목록 · `scores.json` — 바뀐 화면 %·세기·밝기·색 세기·가운데÷가장자리·GPU ms(끔/켬 3바퀴 중앙값)
- 판정판(채택/보류/기각 + 메모) = https://claude.ai/artifact/W5TrJaidaVqQdiFsJUwp8T (판정은 아티팩트 db `verdicts`)

원본(PNG 전/후·차이 지도·원 해상도 영상·Movie Maker AVI, 229MB) = `D:\joseon_archive\2026-10-28\render_lab_963\` (manifest sha256 bd0bcebf0e77dd9a…). git엔 웹용만.
