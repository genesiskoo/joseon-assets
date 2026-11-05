# #1138 흑랑 Tripo 시험 1벌 장부 (Hunyuan3D 유래 몸 교체 — 첫 벌)

- 까닭 = PD 11-03 「Hunyuan3D 접어」(#1128) → 몸은 D-114대로 Tripo 웹 · PD 11-05 「추천대로」 = 흑랑 하나 먼저(40~80크레딧) → 결과 보고 나머지(몸 5 · 소품 2)를 PD가 정함.
- 바이블 칸 = §2 네발 몬스터(Polycount 12,000 — 같은 GLB를 어린 흑랑이 같이 써서 보스 몸 22,000 대신) · 서비스 = Tripo 웹(PD 구독) · 반입 칸 = `boss`(id 추정) · 반입은 안 함(PD 판정 뒤).
- 지금 게임 몸 = Hunyuan3D v3(Higgsfield, 09-20 · 작업 7d6932e4-b694-47f5-ac02-bd77c256143b) 149,638 → 10,000 · 뼈 19 · 클립 9 · 키 0.79 · 깊이 1.09(모델 단위) · ModelDef scale 2.2.

## 1. 입력 원화

| 판 | 무엇 | 서비스 | 판정 |
|---|---|---|---|
| 옛 4뷰 (09-17) | 정면·옆·뒤·3/4 · 순검정 긴 털 (`D:\joseon_archive\2026-10-11\_tmp\a622\workbench\production\h1-style-expansion-2026-09-17\3d_enemies\boss_heukrang\inputs_v3`) | Codex image_gen (H1-E04) | **못 씀** — 09-20 같은 4뷰로 Tripo H3.1 = 납작한 가죽(art_3d_pipeline_log §15.1 6차) · 앞 가슴 털이 앞다리 사이 · 뒤 꼬리가 뒷다리 사이 · 3/4는 Tripo 칸 밖 |
| v1 (11-05) | 옆(왼)·정면·뒤 — 참조 = 옛 컨셉 + 옆 · `codex_raw/prompt_v1.txt` | Codex CLI gpt-5.6-sol 내장 image_gen | 독립 판독(Sonnet) **셋 다 다시** — 정면·뒤 = 다리 넷이 한 줄(뒷다리가 앞다리 바깥에) · 정면 웃는 입(D-086) · 몸 너무 넓음 · 옆 = 배 아래 늘어진 털 · 뒤 = 꼬리가 뒷다리 사이 |
| v2 (11-05) | 옆 = v1 편집(배·가슴 털만 다듬음, `prompt_side_v2.txt`) · 정면·뒤 = 옆 v1 참조로 새로(`prompt_v2.txt`) | 같음 | 2차 판독 — **정면 ○ · 옆 ○** · 뒤 다시(꼬리가 옆모습의 수평과 달리 늘어짐 · 뒷발에 발톱이 보임) · 「세트는 생성기에 보내도 됨」 · 붙일 때 생긴 옅은 사각 경계 → `frame_views.py` 바탕 순백 |
| 틀 맞춤 | 네 칸(앞·왼·오른·뒤)을 2048² 같은 배율 · 같은 바닥 줄 · 오른 = 왼 좌우 뒤집기 (`frame_views.py`) — Tripo 칸 아이콘으로 「Left = 머리가 그림 왼쪽」 확인(눈 x 6.6/20) | — | `1_front.png` · `2_left.png` · `4_right.png` · `3_back.png` |
| v3 (11-05) | 뒤 = v2 편집(꼬리를 옆모습처럼 수평 → 엉덩이 가운데 둥근 덩어리 · 뒷발 뒤꿈치, `prompt_back_v3.txt`) · 정면 = v2 판에서 Codex가 다시 다듬은 것(가슴 털 짧음, `v2b_front_rgba.png` → 흰 바탕) · 옆 = v2 | 같음 | 3차 판독 **정면 ○ · 옆 ○ · 뒤 ○ — 「생성기에 보내도 됨」**(남은 흠 사소: 정면 입꼬리 살짝 · 다리가 컨셉보다 가늘고 곧음 · 꼬리 뿌리가 뒷다리에 조금 가까움) → **채택** `sheet_v3.jpg` |
- Codex 생성 = 9장(v1 세션 4 · 옆 편집 1 · v2 세션 3 · 뒤 v3 1) · 잔여량(주간): 시작 39% 남음(리셋 11-09 17:55) → 끝 39%(반올림 같음).
- Codex CLI 함정: `-s workspace-write`의 윈도 샌드박스 도우미가 「program not found」로 실패 → 참조 그림을 경로로 못 읽고(대화에 붙인 `-i` 그림으로 대신) 결과는 `~/.codex/generated_images/<세션>/`에 남는다 — 거기서 바로 가져오면 된다(Codex가 자기 PowerShell 복사로 옮기기도 함).

## 2. Tripo 생성

| 무엇 | 작업 id | 설정 | 차감 · 잔액 | 결과 |
|---|---|---|---|---|
| 흑랑 여러 방향(앞·왼·오른·뒤 = `art/1_front · 2_left · 4_right · 3_back`) | `c4bae842-f160-4bb1-89d4-6946013d3f17` (Tripo 제목 「dark wolf 3d model」) | HD Model · 큐브 아이콘(여러 방향) · H3.1 · Ultra Mesh 켬 · Texture 켬 2K · PBR 끔 · Remove Lighting 켬 · Triangle · Polycount 12,000 · Private · Parts·8K 끔 (생성 직전 화면에서 다시 읽음) | 40 · 2,020 → 1,980 | **채택** — 약 1분 · Triangle · 면 11,436 · 정점 9,475 · 2K · **다리 넷 분리 · 꼬리·갈기·붉은 눈**(09-20 「납작한 가죽」 재현 안 됨) · 무료 다시 뽑기 ×3 남음(안 씀) |
| 내보내기 | 같음 | Export → GLB · 2k (크레딧 0) | 0 · 1,980 | `tripo/heukrang_tripo_c4bae842_raw.glb` 971KB · `tripo/raw_views.jpg` |
- 쓴 크레딧 합 = **40** (예산 40~80 안 · Tripo 리깅 20 안 씀).
- 올리기 함정(ego-browser): 칸에 그림이 들어가면 그 칸의 `input[type=file]`이 사라져 순번으로 고르면 다음 그림이 엇갈린 칸(·자산 올리기 칸)에 들어간다 → 새로 고침 뒤 **칸 이름으로** 하나씩. 잘못 들어간 PNG는 3D 올리기에서 거절돼 자산이 안 생겼다(잔액 그대로 확인). 칸 순서 = Front · Left · Right · Back · Left 아이콘 = 머리가 그림 왼쪽.

## 3. 손질 · 리그 (우리 도구 · 크레딧 0) — `glb/`

| 단계 | 파일 | 명령 | 결과 |
|---|---|---|---|
| 원본 | `tripo/…_raw.glb` | — | 높이 0.595 · 폭 0.273 · 길이 0.978(Tripo 정규화) · 정면 +Z · 금속 0 · 거칠기 0.9 · 알베도 평균 0.241 |
| s1 크기 | `s1_baked.glb` | `godot --headless -s tools/bake_transform.gd -- --src=… --out=… --yaw=0 --scale=1.2166 --floor --center` | 지금 몸과 **같은 덩치**(키×길이 기하 평균 0.928) → 키 0.724 · 길이 1.190 · 폭 0.332 (지금 몸 0.790 · 1.090 · 0.428) — 반입 때 ModelDef scale 한 칸으로 바꿀 수 있다 |
| s2 텍스처 | `s2_dec.glb` | `blender --background --factory-startup --python tools/blender/decimate_glb.py -- --tris=12000 --tex=1024 --floor --center` | 11,436 그대로(상한 안) · 2048 → 1024 |
| s3 리그 | `s3_rig.glb` | `rig_quadruped.py -- --name=흑랑 --windup=0.4 --pounce-windup=0.5 --walk-tempo=1.2 --run-tempo=1.4 --paw-frac=0.05 --paw-split=cluster --weights=limb` | 앞 = −Y(=glTF +Z) 자동(차 11.8%) · 뼈 19 · 클립 9 · 걷기 0.536 · 달리기 2.078 u/s · 디딤 위상 = 지금 몸과 같다 · ⚠ 아래 함정 |
| s4 값 | `s4_baked.glb` · `s4_bake_report.json` | `python tools/quad_gait.py bake … --scale 2.2 --move 4.0 --walk 1.2 --json` | ModelDef = walk_speed **1.179** · run_speed **4.572** · step_phases 걷기 (0.258, 0.754) · 달리기 (0.044, 0.446) · hit 1.0 · 물기 타격 0.6 |
| s5 가중치 | `s5_limb.glb` | `python tools/quad_rig.py reweight --glb s4 --out s5 --paw-frac 0.05 --paw-split cluster --mode limb` | 섞임 정점 37 → 1 · **이음매 31~53cm → 0** · 가장 큰 늘어남 run 6.9cm(지금 몸 8.1) |
| s6 손질 | `s6_final.glb` | `albedo_ops.py shrink --max 1024 --name basecolor` → `albedo_ops.py matte` | 그림 이름 basecolor · 거칠기 0.9 → 1 · model_check **PASS**(Skeleton3D 1 · 클립 9 · 11,436 · 1024) |
| s7 색 | `s7_slate.glb` | `colorize.py`(이 폴더 — 밝기 결은 Tripo 그대로 · 빛깔 = 지금 흑랑 알베도 평균색 · 대비 ×1.4 · 붉은 눈 유지) | look_audit **PASS** 밝기 0.248 · 채도 0.185 · 대비 0.056 (지금 몸 0.220 · 0.184 · 0.085) — 그대로(s6)는 채도 0.075 · 대비 0.039 = 밴드 밖 |

**함정 (다음 몸 5개에도 걸린다)**
- **Tripo 메시는 깨끗해서 Blender 자동(heat) 가중치가 붙는다(9,391/9,475) → `rig_quadruped`가 `--weights=limb`를 건너뛴다**(limb는 자동이 절반 넘게 실패할 때만 — Hunyuan 몸 전제). 그대로 두면 UV 이음매 정점이 갈라져 걷기 31cm · 죽기 53cm 찢어짐 → 리그 뒤 `quad_rig.py reweight --mode limb`로 다시 칠해야 한다(또는 도구가 `--weights` 를 늘 따르게 고침 — 후속 후보).
- Blender 내보내기가 무게 없는 정점 때문에 `neutral_bone`(무게 0)을 하나 붙인다 → 뼈 20(지금 몸 19). 해 없음.
- `tex_grade` 채도 올리기는 Tripo 알베도의 옅은 보랏빛을 키워 **자주색 늑대**가 된다(채도 ×2.15 = 밴드는 통과해도 기각) → 빛깔을 바꾸는 칠(`colorize.py`)로.
- 사진: `tripo/raw_views.jpg`(생성 원본 앞·옆·뒤·게임 각도) · 리그 뒤 지금 몸과 나란히 = joseon-assets `reports/1138/1138_heukrang_views_old_new.jpg`.

## 4. 비교 영상 (반입 없이)

- `reports/1138/1138_heukrang_compare.mp4` (20초 · 왼쪽 지금 · 오른쪽 새 몸) · 장면 넷 = `1138_heukrang_compare_frames.jpg`.
- 찍은 길 = 동작 확인 툴 `tools/motion_viewer.tscn -- --model=boss_heukrang --record=…` 「한 바퀴」(게임의 ActorVisual 함수를 정한 틱으로 — 대기 → 쫓아옴 → 물기 ×2 → 맞기 ×2 → 죽기) · ① `--set=move_speed=1.2`(쫓아옴 = 걷기) ② 데이터 그대로(보스 쫓기 4.0 = 달리기) · 1280×720 창 · e2e 단독 잠금 안(render_lab.E2eLock) · 같은 구도 = 게임 각도.
- 새 몸은 작업 트리(1036 자리)에서만 잠깐 바꿔 끼웠다: `assets/models/boss_heukrang/boss_heukrang.glb` ← `s7_slate.glb` · `data/models/boss_heukrang.tres` walk 1.179 · run 4.572 → 녹화 → `git checkout` + `git clean` + 임포트로 되돌림(바뀐 줄 0 확인). 커밋·착륙 없음.
- 스크립트 = `reports/1138/scripts/`(rec_tour.py · swap_record.sh · compose.py).
- 눈으로 본 것: 새 몸은 걷기·달리기에서 다리 넷이 또렷하고 등이 곧다 · 죽기는 옆으로 누운 늑대로 읽힌다 · 꼬리는 Tripo가 위로 휘게 만들어 걷는 내내 들려 있다(입력 원화는 수평) · 덩치는 키×길이로 맞춰 길고 낮다.

## 5. 남은 것 (PD 판정 뒤)

- 반입(이 카드): `s7_slate.glb` → `.\tools\intake_model.ps1 -Src … -Id boss_heukrang -Budget boss` · ModelDef walk_speed 1.179 · run_speed 4.572(디딤 위상 그대로) · eorin_heukrang 같은 GLB · #1197이 quad_gait를 먼저 바꾸면 같은 굽기 다시(s3 명령 → reweight limb → s6·s7) · 시험(test_quad_family · heukrang e2e · walk_audit) · 생성 출처 장부 「교체됨 → Tripo c4bae842」 · 옛 GLB는 git.
- 나머지 몸 5(장산범 · 불가살이 · 여우 · 들개 · 지네)·소품 2 = PD가 이 결과를 보고 정함.

## 5. 반입 · 착륙 (2026-11-05, PD 「추천대로」 = 결정 ① 「합쳐」)
- 게임 main `c69e1e68` art(#1138) 반입 + `b236a22a` test(#1138) vfx_cues 怒 높이 테두리 0.2 — 착륙 e2e 39/39 · 반입본 = `glb/s7_slate.glb` 그대로 · 어린 흑랑 `loco_scale_max 1.9`.
- 인게임 전/후 사진 = 게임 `docs/art/1138_heukrang/ingame_before_after.jpg` · 새 몸 네 방향 = `reports/1138/1138_heukrang_views_new.jpg`.
- 자료관(D-109) = `card1138-heukrang-model-tripo` approved(근거 = PD 「추천대로」) · runtime_inventory 흑랑 두 줄 새로 · 검사 새 오류 0(150 → 150 — 남은 150은 다른 카드의 낡은 촬영 해시, 그중 card744 옛 구미호 렌더 1건은 흑랑 GLB 해시가 바뀌어 생김 · 보존 규칙대로 그대로).
