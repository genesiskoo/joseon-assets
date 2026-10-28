# #910 대사 재녹음 기록 (2026-10-27~28)

> 장부 = `audio_910_result.json`(310줄 · 화자·원문·출처·성우·요청/원본/게임 SHA·길이·LUFS·TP). 옛 #777 장부 `audio_777_result.json`은 기록용으로 남긴다. 시험 `tests/test_dialogue_voice.gd`가 새 장부를 읽는다.

## 판정 (PD 10-27)
- 대본 = #910 낭독판 그대로 승인(D-115 가면 사다리 줄 포함).
- 재녹음 판정 넷 = 추천대로: ① 도호 = 오디션 ② 범위 = 310줄 전부(v4는 앞뒤 대사를 문맥으로 읽어 이웃이 바뀐 줄도 억양이 달라진다) ③ 구미호 본체 = 주모 성우·같은 설정(반말로만 갈림) ④ 예산 = 1만 크레딧 안.
- 도호 오디션 = 새 대본 다섯 줄 × 성우 다섯(옛 Professional K-Actor Lee + 공유 라이브러리 후보 Yeon Taek·Taemin·Kyle·Hojin Lim) → PD **Taemin** 선택(`Ir7oQcBXWiq4oFGROCfj`). `audio_cast_613.json` 도호 칸만 바꿈 — 나머지 배역 그대로.

## 생성
- `voice_batch.py --plan → --preflight → --generate --workers 3 → --intake --verify` (eleven_v4 · ko · 안정 0.5 · 닮음 0.75 · 앞뒤 대사 문맥).
- 310줄 · 8,774자 · 교체 275 · 새 ID 35 · 옛 대본에서 빠진 WAV 2개(NPC_SHAMAN_DONE_3 · NPC_SHAMAN_PROXY_1)는 지우지 않고 둠.
- 크레딧(계정 조회): 오디션 320 · 본 녹음 3,922 · 남은 양 134,503 / 197,804.
- 함정: `python -I`로 돌리면 `voice_batch.py`가 옆 모듈 `audio_intake`를 못 찾아 첫 줄 생성 뒤 멈춘다(그 한 줄은 과금됨) — 이 도구는 `-I` 없이 돌린다.

## 시험
- `test_bulgasari.gd` — 「칼이 안 든다」가 도호 바크 뒤에 뜨는지 보는 기다림이 3초였는데, 새 바크(2.56초 + 사라짐 0.35 + 줄 간격)가 넘겨 5초로 늘림. 게임 동작은 그대로.
- `world/stairs.gd` — 봉밀굴 문 앞 첫 혼잣말 녹음이 2.6초 → 2.9초로 길어져 문 안내 글이 혼잣말 위에 포개졌다(e2e bongmil_walk). 미룸 = 바크가 정한 시간(`Bark.display_sec`) + 0.1초로 고침 — 게임 결함.
- `boss_greetings.gd` — 촌장 쇠부리 폐광 인사의 도호 줄을 새 대본으로.

## 판정 (PD 10-28)
- 청취판(https://claude.ai/artifact/3jGGi3fiFMKX6Znev6M47t) 뒤 「이대로 승인 합쳐」 — 다시 뽑은 줄 0.
- 원본(mp3·영수증·계획·QA) = joseon-assets `reports/910_dialogue_voice/`.
