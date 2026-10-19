# #825 도호 목소리 재오디션 (2026-10-19)

PD 10-18: 「도호 성우가 AI스러워서 거슬림」 → 10-19 「ElevenLabs 한국어 성우 3~4명 + 연기 설정 바꿔 같은 대사 3줄로 오디션」.

- 대사: 능청 `NPC_SHAMAN_OFFER_2` · 허세 `NPC_MERCHANT_AFTER_2` · 진지 `EV_GUMIHO_INTRO_5` (앞뒤 문맥 = 게임 대본, `plan_manifest_snapshot.json`).
- 성우: 지금(K-Actor Lee) + 라이브러리 한국어 남성 611명 중 대화체 4 — Theo `CxErO97xpQgQXYmapDKX` · Harry Kim `pb3lVZVjdFWbkhPKlelB` · Yohan Koo `4JJwo477JUAx3HV0T7n7` · Mr. K `LKOcTG4J4tYTPR9DnLeM` (내레이션 위주 목소리는 뺌). 목록 `library_ko_male.json`.
- 설정: 자연 = eleven_v4 · 안정 0.5 · 유사 0.75 · 태그 없음(지금 게임 설정) / 연기 = 안정 0.0 · 연기 태그([casually]·[chuckles]·[pause] 등).
- 생성 27개(지금 성우 자연 3개는 게임 음원 그대로) · 요청 1,145자 · 실제 소모(character-cost 합) 540자. 영수증 `audio/*.json`(요청·SHA·request-id).
- 듣기: −20 LUFS·TP −1.5로 맞춘 `listen/*.mp3` → 판 https://claude.ai/artifact/4iEixBoqQqnKRZCTwncHUP (`a825_page.py` + `a825_page.html`).
- 재현: `python a825_search.py` → `python a825_generate.py`(성공 영수증 있으면 건너뜀) → ffmpeg loudnorm → `python a825_page.py <out.html>`.
