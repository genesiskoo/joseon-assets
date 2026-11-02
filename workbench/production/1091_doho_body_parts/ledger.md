# #1091 도호 몸·옷 분리 시험 — 장부 (2026-11-02~)

- 카드: https://github.com/genesiskoo/joseon-hunters/issues/1091 · 게임 자리 = `claude/1091-doho-body-parts`
- 바이블 칸 = 인물(char) · 서비스 = 몸 Tripo 웹 · 원화 Codex CLI · 면 수 상한 = 몸 Polycount 12,000(옷 파츠 더해 반입 합 ≤ 15,000, 숨긴 면 지운 뒤)
- 예산 = Tripo 웹 60(3D 40 + 리깅 20) · 다시 뽑기 1회 여유 +60 · Tripo 분할·보정은 PD 허락 뒤
- 겉모습은 지금 도호 그대로(D-091 겉모습 고정) — 장비 외형 교체는 범위 밖

## 참조 (ref/)
- `h1_doho_front_tpose.png` = h1-style-expansion-2026-09-17/04_doho_front.png (H1 승인 화풍 · 얼굴 · 체형)
- `game_doho_now_front.png` = 962_doho_282b/shots1/new80_front.png (지금 게임 도호 = Tripo 282b0028 다시 굽기)

## 1단계 원화 (art/) — Codex CLI(gpt-5.6-sol 내장 image_gen) · scratchpad에서

| 판 | 내용 | 입력 | 결과 | 판정 |
|---|---|---|---|---|
| A | 흰 저고리 + 검은 바지 + 토시 + **지금 장화** · 상투·망건 · A포즈 | ref 둘 | `art/doho_body_A.png` 1024×1536 | **채택**(PD 11-02 「A로 진행」) |
| B | 같음 + 장화 대신 **버선·행전** | ref 둘 | `art/doho_body_B.png` 1024×1536 | 안 씀 |

- Codex 한 번 = 두 장(54,463 토큰) · 잔여량 생성 전 78% → 뒤 77%(리셋 11-06 01:48)
- §5.4 점검(독립 서브에이전트): 두 판 모두 1~7·9 ○ · 8 ✗ = 참조가 T포즈라 생긴 차이 + 도포가 없어 어깨가 좁아 보이고 머리가 살짝 작아 보임
- 겹치기 위험(점검 메모): 바지 옆 부풂 → 도포 안 관통(허벅지 숨김으로 막을 곳) · 깃이 목에 바짝 붙음(목 이음매) · 토시·소매 경계 융합 · 저고리 고름이 붉은 띠 자리와 겹침

## 2단계 3D (Tripo 웹) — PD 원화 채택 · 견적 허락 뒤

| 물건 | 작업 id | 설정 | Topology · Faces · Vertices | 차감 | 잔액 전 · 후 | 판정 |
|---|---|---|---|---|---|---|
| 몸 3D | `6f422034-2190-41ef-8e9a-1cb1fc3af931` | HD Model · 단일 이미지(원화 A 정면) · H3.1 · Ultra 켬 · AI Complete 끔 · 2K · 조명 지우기 · PBR 끔 · Triangle · 12,000 · Parts·8K 끔 · Private | Triangle · 11,786 · 8,024 (62초) | 40 | 2,240 → 2,200 | 통과 — 정면·옆·뒤 손·팔·다리·뒷면 OK (`review/body_raw_vs_now_fsb.jpg`) |
| 몸 리깅 | 같은 id (`/workspace/rigging/…`) | Humanoid · Mixamo 프리셋 | 뼈 54 + 끝점 11 = Mixamo 65 · 영향 최대 4 평균 2.31 | 20 | 2,200 → 2,180 | 통과 — `review/rig_inspect/` 가중치 경계 정상 · 바지에 손가락 무게 없음 |

- 받은 파일(크레딧 0): `src/body_6f422034_raw.glb`(리깅 전 · 977KB) · `src/body_6f422034_rigged.glb`(Export Skeleton 켬 · GLB · 2k · 1.19MB)
- Tripo GLB에 **정점 42개 Icosphere**가 섞여 온다(최상위 · 무게 없음) → 반입 전에 지운다 · `rig_inspect.py`는 정점 많은 메시를 고르게 고침(#1091)
- 원래 키 0.981(Tripo 단위) → 반입 때 1.7로
- 이 카드 Tripo 합계 = 60(허락 60 그대로) · 다시 뽑기 여유 60 안 씀

- 브라우저 = ego lite(PD 로그인 그대로) · 작업 공간 13 · 상세 `studio.tripo3d.ai/workspace/generate/<작업 id>`

## 3~6단계 (11-02) — 크레딧 0
- 대본 = 게임 저장소 `tools/blender/body_parts.py`(몸 준비 · 옷 떼기 · 관절 옮기기 · 숨김 · 가중치) · `tools/blender/parts_audit.py`(관통 · 이음매)
- `try1/` = cloth_w transfer(몸에서 옮김 + 보조 뼈 몫 유지) · **12,669 tri**(몸 6,657 · 도포 3,958 · 띠 910 · 흑립 1,144) · 숨김 5,129면 · `report.json` · `audit.json`
- `try2_keep/` = cloth_w keep(지금 옷 무게 그대로) — 이음매가 3~4cm 더 벌어짐 → transfer가 낫다
- 고친 것: try1 첫 판 = 등·위팔 저고리가 도포 밖(쉰 자세부터) → 가까운 옷 면 바깥쪽 판정 추가 · 둘째 = 갓끈 덮개가 얼굴 지움 → 덮개에서 뺌
- 게임 자리 반입(시험): `assets/models/doho_bp/` + `data/models/doho_bp.tres` · 정리 = `docs/design/doho_body_parts_2026-11-02.md`

## 채택 전 증거 둘 (PD 11-02 「1」) — 크레딧 0
- `try3_crotch/` = 가랑이 막 펴기만(늘어남 그대로 — 원인은 자락) · `try4_hybrid/` = **섞음**(골반 아래 자락 지금 무게) = 반입판
- `stretch/` = skin_stretch_probe json(doho · doho_bp · keep · try3 · hybrid · 비틀기 둘) · `twist_test/` = 비틀기 계획 · 손질판 GLB · audit
- 늘어남(옷 켬) 지금 → 섞음: 9.3→6.8 · 15.6→12.3 · 25.6→24.2 · 28.5→23.4cm · 몸통·어깨(달리기) 최대 6.9→4.3 · 상위1% 3.2→2.1cm
- 영상 reports/1091: 1091_all_close/game.mp4(섞음판으로 다시) · 1091_twist_run_close.mp4

## 갈아입히기 시험 (PD 11-02 「옷을 바꿔 입혀봐야 알수있겠다」) — 크레딧 0
- 대본 = `body_parts.py --outfit=<인물 GLB>|none` · 옷 = 게임 안 기존 인물에서 떼어 옴(머리·손·발 면 · 살색 · 수염 뺌) · 무게 = 그 옷 원래 무게(`--outfit_w=source`, 몸에서 옮기면 노인 소매·자락이 60~105cm 찢어짐)
- `outfit_bandit/` = 산적 옷 · 8,766 tri · `outfit_elder/` = 노인 도포 · 10,326 tri · `outfit_none/` = 바지저고리만 · 12,668 tri(흑립 · 도포 없는 몸 그대로) — 각 report.json · audit.json
- 늘어남(걷기/달리기/참격/회오리 cm): 산적 9.0/9.0/10.3/9.8 · 노인 8.0/11.4/18.9/12.4 · 옷 없음 5.5/11.4/14.6/12.3 (도포 섞음판 6.8/12.3/24.2/23.4)
- 관통: 산적 10~12% · 노인 16~21% · 이음매 최대 산적 6.5~7.6 · 노인 9.0~14.4cm — 옷마다 숨김을 따로 구웠다(실제 갈아입히기는 숨김 판 = 2단계)
- 영상 reports/1091: 1091_outfit_all.mp4(넷 나란히 걷기·달리기·회오리) · 클립별 1091_outfit_{walk,run,skill_whirl}.mp4 · 사진 = 게임 저장소 docs/art/1091_doho_body_parts/outfits_rest.jpg
- 게임 자리 반입(시험): `assets/models/doho_{bandit,elder,none}/` + `data/models/doho_{bandit,elder,none}.tres`

## 새 옷 = 두정갑 (PD 11-02 「두정갑」 · 「A (무릎) · 60 승인」)
- 원화 `outfit_armor/art/` = Codex 1회(57,015 토큰 · 잔여 99% · 리셋 11-09 17:55) · A 무릎 길이(**채택**) · B 허벅지 길이 · prompt.txt
- Tripo: 3D `9fe4d3a6-49a1-4700-922f-2c8335fbaf2f` · HD · H3.1 · Ultra 켬 · AI Complete 끔 · 2K · 조명 지우기 · PBR 끔 · Triangle · 12,000 → **11,413 tri**(58초) · 40 · 2,180 → 2,140 · 리깅 Humanoid Mixamo 20 · 2,140 → 2,120 · 합 60(허락 그대로)
- 받은 파일(크레딧 0): `outfit_armor/src/armor_9fe4d3a6_raw.glb`(1.12MB) · `armor_9fe4d3a6_rigged.glb`(Export Skeleton · 1.36MB) · 리깅 전 확인 `review/armor_raw_fsb.jpg` 통과
- `body_parts.py --outfit` → `outfit_armor/doho_armor.glb` · 옷 10,037 + 몸 2,914 + 흑립 1,144 = 14,095 · report.json · audit.json
- 늘어남 8.3/12.0/9.7/8.3cm(`stretch/doho_armor.json`) · 관통 126~156/1,147 · 이음매 최대 6.3~8.1cm
- 게임 자리 반입(시험): `assets/models/doho_armor/` + `data/models/doho_armor.tres`

## 두정갑 옷 질 손질 (PD 11-02 「옷 질 먼저」) — 크레딧 0
- 잰 원인: 남색 채도 0.14(도포 0.36~0.38 · 밝기는 같음) · 붉은 단 채도 0.32(도포 띠 0.58) · 밑단 큰 검은 덩어리 = 한 면 재질 → 자락 안쪽에 외곽선 껍데기만 · 자락 위 검은 줄 = 겉자락 바로 밑 바지의 껍데기가 뚫고 나옴(징 무늬 아님)
- 도구: 게임 저장소 `tools/outfit_grade.py`(UV 칠 텍셀만 재서 남색·붉은 군집을 지금 도호 알베도 색으로 비율 이동 + 두 면 재질) · `body_parts.py --self_cull=0.02`(덮인 옷 속 겹 지움, 두정갑 307면)
- `outfit_armor/doho_armor_c.glb` = 색만(시험판) · `grade.json` · 두 면 시험판 d는 지움
- 남은 잔 검은 줄 = 외곽선 껍데기(외곽선 끄고 찍어 확인) — GLB가 UV 이음매마다 갈라 둔 정점(8,054 중 3,190) → `body_parts.py --seam_normal=0.0005`(같은 자리 정점 법선 평균 · 모양 그대로) · 속 겹 4cm(`--self_cull=0.04`) — 둘 다 기본값으로 · 처음엔 정점을 붙였다가(remove_doubles) 앞 트임까지 꿰매 참격 늘어남 9.7 → 23.3cm → 법선만으로 바꿈
- 시험 갈래 사진 = reports/1091/frames/armor{d,fg,h,i,_nooutline}_walk010.png(걷기 10번째 칸 · 스윕 PNG는 지움, 다시 찍기 = model_viewer --compare): 속 겹 5cm만 = 그대로 · 겉면 고르기 = 더 나쁨(옵션 지움) · 붙이기+2cm = 크게 줄어듦 · 붙이기+4cm = 가장 깨끗(채택)
- `outfit_armor_v2/` = **손질판**: doho_armor_raw.glb(body_parts 이음매 법선 + 속 겹 4cm) → doho_armor.glb(outfit_grade) · 13,748 tri(옷 9,705 · 몸 2,899 · 흑립 1,144) · report.json · audit.json(관통 110~156/1,124 · 이음매 6.3~8.1cm) · 늘어남 8.3/12.3/9.7/8.3cm(`stretch/doho_armor_v2.json`, 손질 전과 같음) · grade.json
- 영상 reports/1091: 1091_armorv2_all.mp4(지금 도호 · 손질 전 · 손질 후 — 걷기·달리기·참격·회오리) · 클립별 1091_armorv2_*.mp4 · 사진 = 게임 저장소 docs/art/1091_doho_body_parts/armor_fix.jpg
- 게임 자리: `assets/models/doho_armor/` = 손질판으로 다시 반입(시험판 c~i는 지움)
- 반입 검사(색만 판): 채도 0.115 WARN → 0.205 통과 · 남은 WARN = 텍셀 밀도
- git에 넣는 것 = 장부 · `src/`(Tripo 원본 GLB · 몸·두정갑) · `outfit_armor/art/` · `review/` · report·audit·grade·stretch json · reports/1091 영상·frames — 중간 GLB(`try*/`·`outfit_*/doho_*.glb`·`twist_test/`)는 `body_parts.py`로 다시 뽑는 산출물이라 git 밖(카드 합 ≥ 50MB 규칙, 로컬 보관)
