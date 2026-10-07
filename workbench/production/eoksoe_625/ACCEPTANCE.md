# PD 판정

**2026-10-07 PD 채택 = B (마르고 노련한 장돌뱅이)** — 판단 보드 3번 「B로가자 A는 김영감이랑 이미지가 겹침」. A는 채택하지 않는다(원본은 이 폴더에 그대로 보존).

- 대화 초상 = B neutral_r2 · smile_r1 정지 2장(BCA 없는 인물 = 정지, #662). 게임 반입 이름 = `game/eoksoe/<표정>.png`.
- **반입본 = 원본에서 알파만 ×255/253**(몸 안쪽 253 → 255 · 가장자리 비례 · 투명 0은 그대로 · RGB 바이트 그대로). 까닭: 생성기 알파 최대가 254라 `portrait_intake` 계약 「알파 255 있음(불투명한 몸)」에 걸렸다(이미 들어간 김 영감 승인본도 몸 안쪽 대부분 253 · 최대 255 몇 점). smile 은 몸 위로 떨어진 알파 1 점 2개(원본 y45 x761~763)도 지웠다 — Godot 사용 영역이 neutral 틀과 어긋나 test_dialogue 「표정 틀 = neutral ±6px」에 걸렸다. 원본 SHA = neutral_r2 `204d88a1e938136e235a88d413276cc54ecb0e9d0d2d3b10ba3eee717b715614` · smile_r1 `b400532d813b5fbf5cbc58159ce223734d0c04a3489e0824087ac1c76a1f1eba`.
- 3D = B 네 방향 T포즈(`B/modeling/`)로 Tripo 웹 여러 방향 생성(#673) → `B/modeling/tripo_web_673/`.
- 봇짐(`B/props/botjim.png`)은 몸과 분리한 소품 — 3D·등 부착은 따로.

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
| eoksoe/neutral | `workbench/production/eoksoe_625/game/eoksoe/neutral.png` (= `B/portrait/neutral_r2.png` 알파 ×255/253) | `0af35fdecbadae1c95354b4b9060a50bada30ca037b0aa98ea9768dd4205dbab` |
| eoksoe/smile | `workbench/production/eoksoe_625/game/eoksoe/smile.png` (= `B/portrait/smile_r1.png` 알파 ×255/253 · 몸 위 알파 1 점 2개 지움) | `8de9dbeeb501900b0b6b5ce35fff62370d4bf2c9a46ac1411b19d62c2f3c1cb2` |
