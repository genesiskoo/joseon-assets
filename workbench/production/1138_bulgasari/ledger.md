# #1138 불가살이 몸 — Tripo 웹 (Hunyuan3D 접음, PD 11-05 「추천대로」)

> 옛 몸 = #512 Hunyuan3D v3 3뷰(Higgsfield) → decimate 10k → rig_quadruped(선딜 0.5 · 덮치기 0.5 · 템포 1.1/1.6) → #847 reweight body-reach 2.4 → #1199 bulgasari_clips(코·포효·삼키기 · 달리기 보폭 ×0.68).
> 새 몸 = 같은 길을 Tripo 메시 위에 다시(0크레딧). 생성 전 칸 = 카드 #1138 댓글(11-05).

## 1. 입력 원화 (Codex CLI gpt-5.6-sol 내장 image_gen)
| 판 | 무엇 | 판정 |
|---|---|---|
| v1 (11-05) | 옆(왼)·정면·뒤 — 참조 = catalog `boss_bulgasari.png` + art_512 옆 · `art/codex_raw/prompt_v1.txt`(흑랑 v3 규칙: 배 선 아래 없음 · 정면 앞다리 둘만 · 뒤 꼬리 수평) | 독립 판독(Sonnet) **셋 다 ○**(위 여백만 얇음 → 틀 맞추기가 해결) |
- 틀 = `art/frame_views.py`(흑랑과 같음) → 2048² 네 칸 · 같은 몸 키 · 오른쪽 = 왼쪽 뒤집기. Codex 주간 39% → 37%(다섯 몸 첫 판 15장 합).

## 2. Tripo 생성
| 작업 | 설정 | 결과 | 크레딧 |
|---|---|---|---|
| `ae95ac07-140e-4595-82c5-72b1ff9c11d1` (제목 「spiked boar 3d model」) | 바이블 §4.1 고정(H3.1 · Triangle 12,000 · Ultra Mesh · 2K · PBR 끔 · Remove Lighting · Private · Parts·8K 끔) · 여러 방향 네 칸 | **한 번에 성공** — 11,363면 · 다리 넷 · 가시 · 돼지 코 · 짧은 꼬리 (80초) | 40 (1,980 → 1,940) |
- 내보내기 = GLB 2K(0크레딧) → `tripo/bulgasari_tripo_ae95ac07_raw.glb` · 네 방향 = `tripo/raw_views.jpg`.

## 3. 손질·리그 (0크레딧 · `glb/post_tripo2.sh`)
| 단계 | 명령 요지 | 결과 |
|---|---|---|
| s1 | bake_transform yaw 0 · ×1.2037(키×길이 기하평균 = 옛 몸) | 키 0.740 · 길이 1.177 (옛 0.815 · 1.068 — 길고 낮다) |
| s2 | decimate 12,000 · 1024 | 11,363 그대로 |
| s3 | rig_quadruped 선딜 0.5 · 덮치기 0.5 · 템포 1.1/1.6 · limb | 클립 9 · 땅 못 닿음 0mm |
| s4 | quad_rig reweight limb · body-reach 2.4 (#847) | 섞인 정점 37 → 2 |
| s4b | bulgasari_clips --stride 0.68 (#1199) | 코 0.6087 · 포효 0.625 · 삼키기 · 달리기 다시 |
| s5 | albedo shrink 1024 · matte | |
| s6 | `glb/tone_keep_hue.py` --lum 0.146 --contrast 2.2 --sat 1.8 --mix 0.45 | 밝기 = 옛 몸(0.146 — 게임 틴트 ×1.4가 올린다) · 분홍 코 · 녹슨 가시 살림 · 옛 몸 푸른 숯빛 45% 섞음 |
- 늘어남 최대 6.1cm(코) — 옛 몸 #847 뒤 8.6cm. look_audit = 옛 몸처럼 밝기·대비 WARN(틴트 전) · 채도 0.073(옛 0.269 = 짙은 푸른빛).
- ModelDef (×2.86) = walk **1.698** · run **5.282** (옛 1.843 · 5.731) · 디딤 위상 같음 → 반입 때 쇠먹이(×1.29) = 0.766 · 2.382.
- **다리가 짧아 걷기 상한**: 쫓기 3.2 = 걷기 1.885배(1.8 넘음) → 반입 때 `loco_scale_max 1.9`(어린 흑랑과 같은 처방 · 1판 처방 — 2판 반입값 2.1, §5) — 시험으로 확인.
- 옛·새 네 방향 = `glb/old_new_views.jpg`(위 옛 · 아래 새).

## 4. 보관 · 비교 (2026-11-05)
- git = 입력 원화 · Codex 원본 · Tripo 원본 GLB · 최종 `glb/s6_color.glb` · 도구 · 사진. **중간 GLB(s1~s5 · 갈래본)는 git에 안 넣음** — 이 PC에만 둔다(다시 만들기 = §3 순서, `glb/post_tripo2.sh` + 몸별 손질).
- 비교 영상(왼쪽 지금 · 오른쪽 새, 걷기 → 달리기 한 바퀴 · 동작 확인 툴) = `reports/1138/1138_bulgasari_compare.mp4` · 새 몸 네 방향 = `reports/1138/1138_bulgasari_views_new.jpg` · PD 판정판 = https://claude.ai/artifact/7A9v8pEDbDNPhZT1fJhizE
- 자료관(D-109) = `card1138-bulgasari-model-tripo` = rejected(1판 — 다리 column 배치, 「죄다 다리빙신」, `699ad6e2`) · 2판 = `card1138-bulgasari-model-tripo-v2` approved(§6).

## 5. 2판 — 다리 리그 고침 (2026-11-05, PD 「죄다 다리빙신」 뒤)
- 1판(glb/s6_color.glb)은 리그 옛 배치(column: 뿌리 = 좌우 발 가운데 · 무릎 키 28% · 발목 12%)라 다리가 구겨짐 → 게임 커밋 `dfe617772` `rig_quadruped --legs=track`(monster_motion_v2 §4.11).
- 굽기: `glb/s2_dec.glb` → `rig_quadruped --windup=0.5 --pounce-windup=0.5 --walk-tempo=1.1 --run-tempo=1.6 --body-reach=2.4 --paw-frac=0.05 --paw-split=cluster --weights=limb --legs=track --leg-h=0.42,0.30,0.10,0.42,0.20,0.05 --leg-freeze=0.27` → `bulgasari_clips.py --stride 0.68`(#1199) → `albedo_ops shrink 1024 · matte` → 알베도 = 1판 s6_color 그대로 이식 → `cut_leg_bridges.py`(6삼각형 · 11-06부터 게임 `python tools/quad_rig.py cut-bridges`, #1216) = **`glb/s7_track.glb`(반입 후보)**.
- 숫자: 못 닿음 0(걷기·달리기) · 가슴 내림 2.8 · 9.3cm · 늘어남 걷기 2.6 · 달리기 2.5 · 코 9.9cm · ModelDef(×2.86) 걷기 1.561 · 달리기 4.854 · 쇠먹이(×1.29) 0.704 · 2.189 · 쫓기 3.2 = 걷기 2.05배 → `loco_scale_max 2.1`.
- 블라인드 독립 판독(Sonnet): 걷기·달리기 4·4 (옛 몸 2·2) — 출시 가능. 띠 = `reports/1138/legs/3_bulgasari_walk_old_vs_fixed.jpg`.
- 곧게 세우기 0.42(기본)면 앞다리 뿌리가 발 뒤 9cm(배 쪽으로 휜 중심선)라 걷기 9cm · 달리기 18cm 못 닿았다 → 0.27(배 밑 높이).
- 전/후 영상(같은 구도 · 왼쪽 옛 몸 · 오른쪽 2판) = `reports/1138/bulgasari_v2/` — 인게임(진짜 게임 셸 · 코·포효·삼키기·죽기) + 동작 확인 툴 한 바퀴(걷기 1.56 → 달리기 4.85, 걷기 상한 2.1).
- 블라인드 독립 판독 2(이 영상 칸 · Sonnet): 걷기 4 · 달리기 4 · 인게임 3 (옛 몸 3 · 3 · 2) — 셋 다 2판이 낫다 · 남은 것 = 걷기 몇 칸 뒷발이 몸 밖으로 벌어지고 살짝 들림 · 인게임은 어두워 관절 판정 어려움. PD 판정판 3판 = https://claude.ai/artifact/7A9v8pEDbDNPhZT1fJhizE

## 6. 반입 (2026-11-05 PD 「합쳐」)
- 게임 `a4d0c810f` · 반입본 = `glb/s7_track.glb` 그대로(게임 `boss_bulgasari.glb` sha256 `3e3983a2…` = 같은 바이트).
- ModelDef 불가살이(×2.86) walk 1.561 · run 4.854 · `loco_scale_max 2.1` · 키 2.12 / 쇠먹이(×1.29) 0.704 · 2.189 · 키 0.95 · 쇠먹이 맏이 = 쇠먹이 ModelDef × size_mult 1.3.
- 자료관 `card1138-bulgasari-model-tripo-v2` = approved(`3460d757`).
- 인게임 전/후 = 게임 `docs/art/1138_bulgasari/ingame_before_after.jpg` · 옛 Hunyuan 몸 텍스처 `boss_bulgasari_texture_20250901.png` 지움(게임 `2b0fb4539`).
