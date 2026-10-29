# PD 판정 (#992)

**2026-10-29 PD 승인**(지휘 세션 전달) — 달래·갑돌 대화 정지 초상 4장 반입 + Tripo 3D 120크레딧.

- 달래 = 원화 B 처음 판(`concept/child_b.png`) · 갑돌 = 원화 J(`concept/youth_j.png`) — 외형 정본 = 게임 저장소 `docs/design/new_npc_looks_992.md`.
- 대화 초상 = BCA 없는 인물 정지 틀(#662, 억쇠와 같다). 게임 반입 이름 = `game/<id>/<표정>.png`.
- **반입본 = 원본에서 알파만 손질, RGB 바이트 그대로**(억쇠 `eoksoe_625/ACCEPTANCE.md` 규칙):
  1. 알파 ×255/253 — 원본 알파 최대가 254일 때만. 이번 네 장은 원본 최대가 이미 255라 늘리지 않았다.
  2. 보이지 않는 알파 1~2 → 0 — 사용 영역이 보이는 몸과 같아지게(표정 틀 = neutral 틀 ±6px). 달래 두 장 = (178, 108)–(909, 1535) · 갑돌 두 장 = (118, 118)–(994, 1535).
- 원본 SHA = 달래 neutral `82ea3d1f866519dba8b984fd61836426695443ace033a022f27f6e93a724eb15` · sad `e22aab561e7449348f544da582e303efb590b6846828014083a45afce0f896fd` · 갑돌 neutral `8d230eb9e77e72c4a57514ff002fba1ca242322b58553bf92ab7a6e578d065e5` · smile `5020b96f901d263fc69a6c1db66402d3fce1d2a96fc40219719c55ad1386ee54`.

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
| dallae/neutral | `workbench/production/992_new_npcs/game/dallae/neutral.png` (= `dallae/portrait/neutral.png` 알파 손질) | `ae43a011c39ac7ec8ea51f7d2609902bf6c72aef14058c6cffc0e56fdd78a2b9` |
| dallae/sad | `workbench/production/992_new_npcs/game/dallae/sad.png` (= `dallae/portrait/sad.png` 알파 손질) | `665f9383af39d583cc352c4f7e162a3248cb6631aa2f91167242614c7db2d025` |
| gapdol/neutral | `workbench/production/992_new_npcs/game/gapdol/neutral.png` (= `gapdol/portrait/neutral.png` 알파 손질) | `813a85b0b4197591fd7d0b92866c2630a5afc8830c2d8100aab3e63e2c9bb43a` |
| gapdol/smile | `workbench/production/992_new_npcs/game/gapdol/smile.png` (= `gapdol/portrait/smile.png` 알파 손질) | `ef62b9ffb3e39f94fad6818a10a8e3a4e59bc1fe3011aa8424ee0155185de951` |
