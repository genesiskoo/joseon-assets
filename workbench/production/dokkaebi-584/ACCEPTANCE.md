# #584 도깨비 — 게임 반입 기록 (2026-11-13)

## PD 판정
- 2026-10-09 「두번째로 가자」 = I v2 외형 채택(원본 SHA `3f9500d0e9cab16a97c4f5165dda5e25e8987b19f3e5d25e783377c709ea2b6e`, 기록 = 브랜치 `codex/584-dokkaebi` `revisions/20261009_approved_I/ACCEPTANCE.md`).
- 2026-10-12 판단 보드 4 「추천대로」 = 파생 6장(중립·웃음 초상 + 빈손 4뷰) 승인.
- 2026-10-18 판정판 「추천대로」 = Tripo #762 3D 도깨비 채택 → 반입. 시선·옷 차이는 그대로 둔다.
- 2026-11-02 「전부 추천대로」(#1131) = 반입을 지휘(claude)로.

## 3D
- Tripo 웹 작업 `30c0c203-e7d6-447c-b8f1-9c2e17060aae`(Tripo H3.1 · 2K) → 웹 Export GLB · 텍스처 2k · 뼈대 켬 · 동작 3(idle · 껄껄 웃기 · 느릿한 걸음) · stay in place · **크레딧 0**(잔액 1,385 그대로).
- 뼈대 = Mixamo 65 · 삼각형 14,105. Tripo 쪽에는 동작이 셋뿐 — 10-18 메모의 「방망이로 두드려 조합」 「손짓하며 말하기」는 없다.
- 게임본 = `albedo_ops shrink --max 1024 --name basecolor` → `matte` → 동작 이름 idle · laugh · walk(그 밖은 바이트 그대로) → `intake_model.ps1 -Budget char -Height 2.2`(목표 키 2.2 = 가안, ModelDef scale 2.244).

## 대화 초상 — 반입본 손질
원본 = `revisions/20261009_approved_I/{neutral,smile}.png`(브랜치 `codex/584-dokkaebi` c180bf2d). 반입본만 고쳤다(원본 바이트 그대로):
1. 알파 ×255/253(반올림 · 255 자름) — 생성기 알파 최대 254 → 「불투명한 몸」 계약.
2. 알파 1~2 → 0 — 보이지 않는 테두리를 지워 표정 틀을 맞춘다.
3. **그림 전체를 아래로 40px** (위에 투명 줄, 아래 40px 잘림 · 화소 값 그대로) — 머리 위 여백 5.4%·5.2% → 8.0%·7.8%(계약 8% ± 1.5%). 잘린 아래 40px = 허벅지 아래 끝, 띠가 가리는 자리.

- 원본 SHA = neutral `c59c3ef44daba27ef34da2cfa32e038fcc25bc9a1f7da430b134b6a0f83e129e` · smile `c9b1cf0bf216c06717fde8ed9b8ebd2bbefd94c1164fbc3dedb13d54654ee6c3`.

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
| dokkaebi/neutral | `workbench/production/dokkaebi-584/game/dokkaebi/neutral.png` (= 원본 neutral 알파 손질 + 40px 내림) | `0117c2d7e4b71d5ba071b33ef54d314b563f4fe8dcbbf051a6bd97a6e4da4c1f` |
| dokkaebi/smile | `workbench/production/dokkaebi-584/game/dokkaebi/smile.png` (= 원본 smile 알파 손질 + 40px 내림) | `ceb3f8f696f75010716e9ca8343ca2eb2f05f179f1b8d4a7479a515f414ed2bf` |
| dokkaebi/model | `workbench/production/dokkaebi-584/game/dokkaebi/dokkaebi.glb` | `c703760064e3997ccc8fbfc92312acb6578e5ca4cc621919d4c2e8d2e11a2955` |
| dokkaebi/tripo_export | `workbench/production/dokkaebi-584/modeling/tripo_web_584/dokkaebi_tripo_idle_laugh_walk.glb` (Tripo 내보내기 원본) | `6956feebbaf041309e00360764e58913319dfb05d236942cf12ced9beb37840b` |
