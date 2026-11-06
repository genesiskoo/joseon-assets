# #1138 장산범 몸 — Tripo 웹 (Hunyuan3D 접음, PD 11-05 「추천대로」)

> 옛 몸 = #512 Hunyuan3D v3 3뷰 → decimate 10k → rig_quadruped(선딜 0.4 · 덮치기 0.5 · 템포 1.2/1.4) · ModelDef ×2.64(어린 장산범 ×1.32 = 같은 GLB).

## 1. 입력 원화 (Codex CLI gpt-5.6-sol)
| 판 | 무엇 | 독립 판독(Sonnet) |
|---|---|---|
| v1 | 옆·정면·뒤 (`prompt_v1.txt` — 털은 굵게 뭉쳐 배 선까지) | 셋 다 다시(긴 털이 배 선 아래 · 다리 가림) |
| v2 | 셋 다 털 다듬기 편집 | 옆 ○ · 정면 ○ · 뒤 다시(엉덩이 털이 허벅지 덮음) |
| v3 | 뒤 편집 | 다시(꼬리가 털 소용돌이로 뭉개짐) |
| v4 | 뒤 편집(꼬리 = 또렷한 짧은 뭉치 · 뒤꿈치) | **○** |
- 함정: Codex CLI를 `&` 없이 백그라운드로 돌리면 stdin을 기다리며 멈춘다(「Reading additional input from stdin」) → `< /dev/null`.

## 2. Tripo 생성
| 작업 | 결과 | 크레딧 |
|---|---|---|
| `2d1f5bca-5e7c-4e4f-9fbc-86e245e90495` (§4.1 고정) | **한 번에 성공** — 11,704면 · 뭉친 흰 털 · 푸른 눈 · 다리 넷 · 곧은 꼬리 | 40 (1,860 → 1,820) |
- 내보내기 저장이 EBUSY로 한 번 실패 → 받은 파일(`~/.ego-browser/state/downloads/…`)을 손으로 복사(같은 바이트).

## 3. 손질·리그 (0크레딧)
- 크기 = 키 맞춤 ×1.7133(키 0.795 = 옛 몸 · 곧은 꼬리가 길이에 들어감).
- rig_quadruped 선딜 0.4 · 덮치기 0.5 · 템포 1.2/1.4 → reweight limb **body-reach 3.0**(섞인 정점 238 → 13) → **`cut_leg_bridges.py`**(두 다리를 잇던 긴 털 막 48삼각형 = 0.41%를 넓이 0으로 — 걷기 늘어남 14.5 → 9.2cm · 11-06부터 게임 `python tools/quad_rig.py cut-bridges`, #1216) → shrink · matte → `tone_keep_hue.py` 밝기 0.680 → 0.563(옛 몸) · 채도 ×1.3 · 옛 몸 빛깔 20%.
- 늘어남 최대 9.2cm(걷기 · 뒷발) — 옛 몸 6.9cm보다 크다(긴 털 몸) · 섞인 정점 13(옛 26).
- ModelDef(×2.64) = walk **1.600** · run **6.202** (옛 1.525 · 5.914) · 디딤 위상 같음 → 어린 장산범(×1.32) = 0.800 · 3.101.
- 모양: 옛 몸보다 길고 낮다(머리 숙인 덩치 → 긴 흰 털 사냥개 꼴) — PD 판정 칸.

## 4. 보관 · 비교 (2026-11-05)
- git = 입력 원화 · Codex 원본 · Tripo 원본 GLB · 최종 `glb/s6_color.glb` · 도구 · 사진. **중간 GLB(s1~s5 · 갈래본)는 git에 안 넣음** — 이 PC에만 둔다(다시 만들기 = §3 순서, `glb/post_tripo2.sh` + 몸별 손질).
- 비교 영상(왼쪽 지금 · 오른쪽 새, 걷기 → 달리기 한 바퀴 · 동작 확인 툴) = `reports/1138/1138_jangsanbeom_compare.mp4` · 새 몸 네 방향 = `reports/1138/1138_jangsanbeom_views_new.jpg` · PD 판정판 = https://claude.ai/artifact/7A9v8pEDbDNPhZT1fJhizE
- 자료관(D-109) = `card1138-jangsanbeom-model-tripo` = rejected — PD 11-05 「죄다 다리빙신」(`699ad6e2`) → 리그 고친 판 독립 판독 = 옛 몸이 나음 → PD 11-06 「기존 몸으로 쓰자」: 게임 = 옛 Hunyuan 몸 유지 · 다시 등록 안 함.
