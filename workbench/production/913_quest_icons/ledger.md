# #913 의뢰 기록 보스 아이콘 — Pixellab 심볼(청동 봉인 메달)

- 게임 자리: `assets/sprites/ui/quest/<id>.png` (128×128 RGBA) · `ui/quest_journal_ui.gd` ICONS · 64칸에 선형 필터로 그림
- 서비스: Pixellab MCP `create_image_pro`(Pro) · 128×128 · 투명 배경 · 한 번에 후보 4장 · 10회/호출
- 참조: 게임 보스 모델 렌더(`tools/model_viewer.tscn --clean --zoom=1.8 --yaw=15`, 구미호 = `gumiho_y2 --zoom=3 --yaw=45`) + 흑랑 원화 `h1-style-expansion-2026-09-17/3d_enemies/boss_heukrang/inputs_v3/01_front.png`
- PD 판정(2026-10-26): 1·2차(글만으로 생성)는 「조선헌터스 몬스터랑 전혀 안닮았음」 기각 → 3차 A(D2R식 초상)·B(심볼) 중 **B 채택**

| id | 채택 | 원본 job | sha256(앞 16) | 바이트 |
|---|---|---|---|---|
| heukrang | B1-3 | db0de06a-9160-4378-9f6d-74e6b02d7db8 #2 | 186af67d00657353 | 23,414 |
| jangsanbeom | B2-2 | 9889d7ec-c633-479d-86ab-2a1115dd5e5d #1 | dacf7a0407904f64 | 15,031 |
| bulgasari | B3-1 | 52d634ad-2af0-45a0-ae1e-6a16bdfbd673 #0 | b1f87f268c5fbcd0 | 16,845 |
| gumiho | B4-3 | c9f1d2c6-ee92-4491-9e54-02fb5723d14c #2 | 39e093b436a4ed03 | 17,542 |

- `candidates/` = 3차 후보 32장(A_* D2R식 · B_* 심볼, 번호 = 판정판 번호)
- 비용: 1차 40 + 2차 80 + 3차 80 = 200회(구독 생성 횟수, 현금 0) · 남은 1,780 (리셋 2026-11-24)
- 판정판·비교 사진: 게임 저장소 `docs/art/913_quest_icons/`
