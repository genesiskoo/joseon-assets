# #1157 도호 스킬 v3 새 칸 아이콘 14 — 채택 · 게임 반입

- 생성: Codex CLI 내장 image_gen (`codex exec -m gpt-5.6-sol`, 2026-11-05) · 칸마다 A(인물 중심) · B(큰 모티프) 2장 = 28장 · 원본 1254×1254 RGB.
- 참조: H1 판(왼쪽 인물만) · #498 승인 붓 원화 · 옛 아이콘 seal_array · whirlwind · hide.
- 갈래 색 줄: 호풍환우 = 먹구름·잿빛 바람 + 쪽빛 물기, 벼락 = 상아빛 금 / 둔갑·환술 = 종이(한지 + 주사) · 부적(겨자빛 부적 + 먹 사슬) · 그림자(먹·남색 + 붉은 띠 한 점).
- 지시문 = `prompts/` (`slots.py`가 만든다) · 축소 = `exports/<A|B>_<id>_{128,64,40}.png` · SHA = `outputs.json` · Claude 추천 = `rec.json`.
- 판정판: https://claude.ai/artifact/DDw9rVCrB3t9u2CCeKh2xj (db `verdicts/<id>` = {pick, note})

## 채택 (2026-11-05 PD 「추천대로 반입」)
- 14칸 모두 Claude 추천대로: 돌개바람 B · 소나기 B · 젖은 하늘 B · 짙은 안개 A · 하늘 기운 B · 용오름 A · 호풍환우 A · 종이 병사 B · 허수아비 A · 종이 숙련 B · 속박부 B · 퇴마 기운 A · 그림자 칼 B · 신장 부르기 A.
- 반입 = `exports/<채택>_<id>_128.png` 바이트 그대로 → 게임 `assets/sprites/ui/icons_a/skills/<id>.png` (무손실 · 밉맵 끔) · 칸 = `data/skills/v5/<id>.tres` icon. 게임 SHA = `adopted.json` (= 게임 `tests/test_skills.gd` V5_INTAKE).
- 원본 `raw/` (28장 ≈ 79MB)은 저장소에 넣지 않는다(#579, 카드 합 ≥ 50MB) — 드라이브 `JoseonHunters_raw/1157/`로 옮길 몫(G: 켠 뒤). 원본 SHA = `outputs.json`.
- 판정판 `board.html`(3MB, 그림 내장)도 저장소 밖 — 아티팩트 주소로 본다.
