# #833 여성형 몬스터 f4 편입 — 장부 (Tripo 웹)

PD 10-22: 「원화 그대로 가고 tripo 집어넣어서 정식 몬스터 편입 파이프라인 태워」 — A포즈 다시 그리기 · 노출선/왜색 수정 없이 f4 원화를 그대로 입력.
바이블 칸 = 인물·사람형 몬스터 (modeling_bible §2·§4) · 서비스 = Tripo 웹(Chrome, PD 로그인) · 생성 상한 12,000 tri · 반입 8,000~15,000 · `-Budget char`.
설정(§4.1, 생성 직전 눈으로 확인): H3.1 · HD Model · 단일 이미지 · Ultra 켬 · AI Complete 끔 · Texture 2K · Remove Lighting 켬 · PBR 끔 · Triangle · Polycount 12,000 · Private · Parts·8K 끔.

| 시각 | 대상 | 입력 | 작업 | task | 차감 | 잔액 | 결과 · 판정 |
|---|---|---|---|---|---:|---:|---|
| 10-22 | 01 의녀귀 | 01_uinyeogwi_3.png | 이미지→3D | a2cda0fb-9a7c-4c75-a937-94d54ad5debf | 40 | 3000→2960 | |
| 10-22 | 04 홀린 무녀 | 04_hollin_mudang_3.png | 이미지→3D | 7b2a7a2e-9e09-4e65-88b6-10ba0a2a9070 | 40 | →2920 | Triangle 11,267 · 통과(방울·칼 붙은 채) |
| 10-22 | 07 각시귀신 | 07_gaksi_gwisin_2.png | 이미지→3D | 6195d258-0c32-4096-83fe-1fca2eda106b | 40 | →2880 | Triangle 11,233 · 긴 소매가 바닥까지 몸에 붙은 덩어리(원화 그대로) |
| 10-22 | 01·07·04 | — | Auto Rig Humanoid · Mixamo 65 | a2cda0fb · 6195d258 · 7b2a7a2e | 60 | →2820 | 세 몸 리깅 |
| 10-22 | 01·04·07 | — | 프리셋 동작 6 (idle · walk · run · slash · hit_to_body_01 · fall) | 〃 | 0 | 2820 | 프리셋 하나 붙이는 데 ≈ 80~90초 — 앞 것이 끝나기 전에 누르면 안 붙는다 |
| 10-22 | 01·04·07 | — | Export GLB 2k · 뼈대 · 6동작 · stay in Place | 〃 | 0 | 2820 | tripo_uinyeogwi.glb · tripo_hollin_mudang.glb · tripo_gaksi_gwisin_v2.glb |

## 손질 · 반입
- `albedo_ops shrink --max 1024 --name basecolor` → `matte` → uinyeogwi.glb · hollin_mudang.glb · gaksi_gwisin.glb → `intake_model.ps1 -Height 1.6 -Budget char`.
- model_check: 키 0.98 → scale 1.633 · look_audit: 의녀귀 채도·빛 구움 · 각시귀신 빛 구움(경고만) · 무녀 OK.
- 합계 차감 180 (3D 120 + 리깅 60) · 동작 · 내보내기 0. 잔액 3000 → 2820.

## A포즈 원화 (PD 10-22 2차 「원화부터 점검 · A포즈 뽑아봐, gpt grok 둘다」) — 3D 몸 셋(d588dc18)은 착륙 안 함
| 서비스 | 결과 | 사용량 |
|---|---|---|
| Codex CLI (ChatGPT · gpt-5.6-sol · 내장 image_gen, 원화 참조 -i) | 종마다 2장 = 6장 `apose/*_gpt_{1,2}.png` | 주간 사용 23% · 남음 77% (리셋 10-27) |
| Grok CLI (grok.com · image_edit, 원화 참조) | 종마다 2장 = 6장 `apose/*_grok_{1,2}.png` | 세션 셋 ≈ $0.06 · $0.13 · (셋째 기록 없음) |
- 비교판 `apose/sheet_<종>.jpg` (원화 · GPT 1·2 · Grok 1·2).

## 2차 3D — A포즈 GPT 2 입력 (PD 10-22 「gpt로 가자」) · 설정 같음(H3.1 · Triangle · 12,000 · Ultra · 2K · 조명 지우기)
| 대상 | 입력 | task | 차감 | 잔액 | 결과 |
|---|---|---|---:|---:|---|
| 01 의녀귀 | apose/uinyeogwi_gpt_2.png | 6acae60c-6f42-4cc0-95ec-1f11032ca96c | 40 | | Triangle 11,827 · 팔·손가락 분리 통과 |
| 04 홀린 무녀 | apose/hollin_mudang_gpt_2.png | dab8c1d4-40ef-4242-8a7d-eb7758a0f0ff | 40 | | Triangle 11,221 · 통과(넓은 소매는 팔 따라감) |
| 07 각시귀신 | apose/gaksi_gwisin_gpt_2.png | 74616f8d-3eec-4635-bced-51f46674e291 | 40 | 2820→2700 | Triangle 11,554 · 긴 소매가 무릎까지 늘어짐(치마와 떨어짐) |
- 정면·옆 = apose/3d2_front_side.jpg. 리깅 전 PD 점검.

## 2차 리깅 · 동작 (PD 10-22 「리깅 진행해」 · 「추천대로」)
- 리깅 Humanoid · Mixamo 65 × 3 = 60 (2700 → 2640) · 프리셋 idle · walk · run (+ slash · hit · fall 셋, 지금은 _preset · 안 씀) = 0
- PD 3차 「몬스터 다 똑같다 — 성격에 맞게」 → 기획 joseon design/f4_motion_833.md → Tripo AI 문장 → 동작 종마다 5(대기 · 공격 · 시전 · 맞기 · 죽기) = 15 × 20 = 300 (2640 → 2340)
  - 각시귀신 74616f8d: Eerie ghost bride idle · Sleeve Whip · Formal Wedding bow(시전) · Front Impact(맞기) · Death Pose
  - 홀린 무녀 dab8c1d4: Shaman Dance idle · Ritual Spin Dance(공격) · Bell Ritual Dance(시전) · Startled Retreat(맞기) · Backward Collapse(죽기 — 생성 뒤 안 붙어 눌러서 붙임, 추가 차감 0)
  - 의녀귀 6acae60c: Idle Nurse Loop · Precise Needle(공격) · Needle Throw(시전) · Neck Snap(맞기) · Slumping(죽기) — 이 모델만 붙이기(retarget)가 한 개 3~5분
- 함정: AI 동작은 생성 뒤 모델에 바로 안 붙는 것이 있다 → Export 목록 수로 확인, 빠진 건 AI Animation 목록에서 눌러 붙임(무료) · 클립 이름 = 문장 앞 64자 → rename_clips(JSON만)로 idle · attack · cast · hit · die
- 내보내기 gaksi_gwisin_v4 · hollin_mudang_v4 (11동작) · uinyeogwi_v4 (9동작)
- 누계 #833 Tripo 사용 = 1차 180 + 2차 3D 120 + 리깅 60 + AI 동작 300 = 660 · 잔액 2340

## 3차 — 맞기 크게 다시 (PD 10-23 「추천대로」)
- 각시귀신 74616f8d: AI 「Big violent hit reaction … staggers two steps back」 2초 → 클립 hit (옛 hit = hit_v1) · 20
- 의녀귀 6acae60c: AI 「Big violent hit reaction … head snaps violently」 2초 → hit (옛 = hit_v1) · 20
- 잔액 2340 → 2260 (이 둘 40 · 나머지 40은 같은 계정 다른 세션 — #896 /monster-make 시범 추정)
- 내보내기 gaksi_gwisin_v5 (12동작) · uinyeogwi_v5 (10동작)

## 4차 — 맞기 확정 · 자료관 (PD 10-23 「추천대로」)
- 프리셋 맞기 4(hit_to_body_02 · head · side · stomach) 붙여 내보냄(크레딧 0) — 각시귀신은 stomach 안 붙음 · 비교 영상 reports/833/833_hit_candidates.mp4
- 확정: 의녀귀 = hit_to_head · 각시귀신 = hit_to_body_02 · 홀린 무녀 = AI 맞기 그대로
- 최종 반입 원본(git): uinyeogwi_v6.glb · hollin_mudang_v4.glb · gaksi_gwisin_v6.glb
- git에 안 올린 것(로컬 · 카드 합 50MB 넘음): tripo_*.glb · v2~v5 · *n.glb · 손질본 — 필요하면 Tripo 웹 작업 id로 다시 내보내기(크레딧 0)
- 자료관: card833-{uinyeogwi,hollin_mudang,gaksi_gwisin}-{apose,model} 6건 + 인물 3 · --dry-run 오류 48 → 48(추가 0)
