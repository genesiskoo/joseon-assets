# #910 대사 310줄 재녹음 (ElevenLabs v4, 2026-10-27~28)

대본 = #910 낭독판(D-115 구미호 가면 사다리 줄 포함). 도호 성우 = Taemin(`Ir7oQcBXWiq4oFGROCfj`, 오디션 PD 선택 — 오디션 원본은 게임 저장소 기록 `docs/design/audio_910_log.md`). 나머지 배역은 #613 그대로.

- `raw/` = ElevenLabs 원본 mp3(인물별 · 파일 이름에 요청 SHA) · `receipts/` = 줄마다 요청·응답 영수증 · `plans/` = 고정 계획 · `sources/` = 대본 출처
- `manifest.json` · `intake.json` · `intake_records/` · `qa.json` = 반입(-18 LUFS · TP ≤ -1.5 · PCM16 모노 44.1k)과 실측 검사 · `credit_ledger/` · `preflight.json` = 크레딧 기록
- `audio_910_result.json` = 게임에 들어간 장부(310줄 · 원본/게임 WAV SHA · 길이 · LUFS · TP) · `audio_910_log.md` = 판정·함정·시험 기록
- `qa/` = 생성·반입·단위·e2e 실행 로그 전문 · `errors/` = 첫 실행에서 멈춘 한 줄(`python -I` 함정)

크레딧: 오디션 320 · 본 녹음 3,922. 게임용 WAV(122MB)는 게임 저장소 `assets/audio/voice/`에만 둔다(장부 SHA로 대조).
PD 판정(10-28) = 청취판 뒤 「이대로 승인 합쳐」 — 다시 뽑은 줄 0.
