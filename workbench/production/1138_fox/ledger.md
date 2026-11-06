# #1138 여우 몸 — Tripo 웹 (Hunyuan3D 접음, PD 11-05 「추천대로」)

> 옛 몸 = #512 Hunyuan3D v3 3뷰 → decimate 10k → rig_quadruped(선딜 0.3 · 덮치기 0.45 · 템포 1.105/1.17 = PD 「×1.3」) · ModelDef ×1.144. 같은 GLB = 여우 · 둔갑 여우 · 매구(EnemyDef 틴트).

## 1. 입력 원화 (Codex CLI gpt-5.6-sol)
| 판 | 무엇 | 독립 판독(Sonnet) |
|---|---|---|
| v1 | 옆·정면·뒤 (`art/codex_raw/prompt_v1.txt`) | 옆 ○ · 정면 ○ · 뒤 다시(꼬리 끝 흰 원반) |
| v2 | 뒤 편집(`prompt_v2.txt`) | 다시(엉덩이 넓음 · 가랑이 틈 낮음) |
| v3 | 뒤 편집(`prompt_v3.txt`) | **○** |
- 틀 = `art/frame_views.py` 2048² 네 칸(옆 v1 · 정면 v1 · 뒤 v3 · 오른쪽 = 옆 뒤집기).

## 2. Tripo 생성
| 작업 | 결과 | 크레딧 |
|---|---|---|
| `0eb518ca-3c6a-4cbe-bd74-e56d66d4c955` (「fox 3d model」 · §4.1 고정) | **한 번에 성공** — 11,462면 · 다리 넷 · 흰 가슴 · 흰 끝 긴 꼬리 | 40 (1,940 → 1,900) |

## 3. 손질·리그 (0크레딧 · `glb/post_tripo2.sh`)
- 크기 = **키 맞춤 ×1.7502**(키 0.871 = 옛 몸) — 꼬리를 곧게 뻗어 길이에 꼬리가 들어가서, 키×길이 기하평균이면 키가 24% 작아진다(흑랑과 다른 처방).
- rig_quadruped 선딜 0.3 · 덮치기 0.45 · 템포 1.105/1.17 → reweight limb(섞인 정점 147 → 7) → shrink · matte → `tone_keep_hue.py` 채도 ×0.8(0.638 → 0.550, 옛 0.512).
- 늘어남 최대 5.7cm(달리기). ModelDef(×1.144) = walk **0.816** · run **3.487** (옛 0.778 · 3.324) · 디딤 위상 같음.
- 옛·새 네 방향 = `glb/old_new_views_fox_dog.jpg`(1줄 옛 여우 · 2줄 새 여우).

## 4. 보관 · 비교 (2026-11-05)
- git = 입력 원화 · Codex 원본 · Tripo 원본 GLB · 최종 `glb/s6_color.glb` · 도구 · 사진. **중간 GLB(s1~s5 · 갈래본)는 git에 안 넣음** — 이 PC에만 둔다(다시 만들기 = §3 순서, `glb/post_tripo2.sh` + 몸별 손질).
- 비교 영상(왼쪽 지금 · 오른쪽 새, 걷기 → 달리기 한 바퀴 · 동작 확인 툴) = `reports/1138/1138_fox_compare.mp4` · 새 몸 네 방향 = `reports/1138/1138_fox_views_new.jpg` · PD 판정판 = https://claude.ai/artifact/7A9v8pEDbDNPhZT1fJhizE
- 자료관(D-109) = `card1138-yeou-model-tripo` = rejected — PD 11-05 「죄다 다리빙신」(`699ad6e2`) → 리그 고친 판 독립 판독 = 옛 몸이 나음 → PD 11-06 「기존 몸으로 쓰자」: 게임 = 옛 Hunyuan 몸 유지 · 다시 등록 안 함.
