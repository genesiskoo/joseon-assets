# #1138 역병 든 들개 몸 — Tripo 웹 (Hunyuan3D 접음, PD 11-05 「추천대로」)

> 옛 몸 = #299 Higgsfield Hunyuan3D v3 → Meshy remesh 12k → bake_transform yaw −90 ×0.66 → rig_quadruped → #501 quad_gait(선딜 0.30) → #522 reweight → #889 die. ModelDef ×1.0 · target_height 0.97(test_models SIZE_299 ±0.05).

## 1. 입력 원화 (Codex CLI gpt-5.6-sol)
| 판 | 무엇 | 독립 판독(Sonnet) |
|---|---|---|
| v1 | 옆·정면·뒤 — 참조 = catalog `mob_wild_dog_plague.png` (art_512 3뷰 없음) | 정면 ○ · 옆 다시(다리 틈 · 꼬리 위로) · 뒤 다시(꼬리가 얼굴처럼) |
| v2 | 옆 · 뒤 편집 | 뒤 ○ · 옆 다시(뒷다리 정강이 겹침) |
| v3 | 옆 편집(뒷다리 엇갈림 · 꼬리 엉덩이 높이) | **○** |
- 틀 = 옆 v3 · 정면 v1 · 뒤 v2 → 2048² 네 칸.

## 2. Tripo 생성
| 작업 | 결과 | 크레딧 |
|---|---|---|
| `31a74e41-a869-45f3-bb24-19988b6af190` (§4.1 고정) | **한 번에 성공** — 11,556면 · 갈비 드러난 마른 몸 · 회녹색 헌 데 · 곧은 꼬리 | 40 (1,900 → 1,860) |

## 3. 손질·리그 (0크레딧)
- 크기 = **키 맞춤 ×1.9194**(키 0.970 = 옛 몸 · 시험이 0.97 ±0.05로 묶음) → 길이 1.88(꼬리 포함, 옛 1.32).
- rig_quadruped 선딜 0.3 · 덮치기 0.45 · 템포 1.0/1.0 (die = 지금 quad_gait = #889 옆으로 눕기) → reweight limb(141 → 0) → shrink · matte → `tone_keep_hue.py` 밝기 0.469 → 0.393(옛 몸) · 채도 ×0.85.
- 늘어남 최대 7.9cm(pounce_air). ModelDef(×1.0) = walk **0.875** · run **3.961** (옛 0.845 · 3.823) · 디딤 위상 같음.
- 옛·새 네 방향 = `glb/old_new_views_fox_dog.jpg`(3줄 옛 들개 · 4줄 새 들개).

## 4. 보관 · 비교 (2026-11-05)
- git = 입력 원화 · Codex 원본 · Tripo 원본 GLB · 최종 `glb/s6_color.glb` · 도구 · 사진. **중간 GLB(s1~s5 · 갈래본)는 git에 안 넣음** — 이 PC에만 둔다(다시 만들기 = §3 순서, `glb/post_tripo2.sh` + 몸별 손질).
- 비교 영상(왼쪽 지금 · 오른쪽 새, 걷기 → 달리기 한 바퀴 · 동작 확인 툴) = `reports/1138/1138_plague_dog_compare.mp4` · 새 몸 네 방향 = `reports/1138/1138_plague_dog_views_new.jpg` · PD 판정판 = https://claude.ai/artifact/7A9v8pEDbDNPhZT1fJhizE
- 자료관(D-109) = `card1138-plague_dog-model-tripo` (unreviewed — PD 판정 뒤 갱신).
