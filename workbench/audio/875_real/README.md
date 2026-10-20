# #875 국악기 효과음 2차 — 실제 녹음 기반

- 판정판: https://claude.ai/artifact/Ut3wruGBhcnCCSw4dW9r37 · 사양: joseon `docs/design/gugak_sfx_plan.md` §7
- git에 든 것: `made/`(게임용으로 만든 소리, 13MB) · `gongu/CREDITS.md`·`gongu/_ledger.json`(라이선스 장부) · `commons/_ledger.json` · 이 README.
- git 밖(로컬, 큼): `gongu/`(공유마당 원본 249개, 567MB) · `slices/`(한 타 조각, 100MB) · `freesound/` · `commons/*.ogg`. 다시 받기 = 장부의 쪽 주소. 보관 정리 때 D:\joseon_archive로.
- 라이선스: 공유마당 한국저작권위원회·김용배·아이티앤 = CC BY 4.0(242개 확인) — **출시 크레딧 표시 의무** · 전주 MKH418 7개 = 이용조건 미확인(안 씀) · Freesound kynodelia = CC0 · 위키미디어 Mjphome = CC BY-SA 4.0(분석 참고만, 게임 안 넣음).
- 만든 법: `tools/sound_slice.py` → `tools/sound_analyze.py` → `tools/gugak_make.py` (joseon 저장소).
