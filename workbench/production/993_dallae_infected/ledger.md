# #993 감염된 달래 (`dallae_infected`) — /monster-make 장부

정본 = 게임 `docs/design/story_depth_2026-10-29.md §4.4`(D-120) · `storyline_d120.md §6.3`(브랜치 claude/story-d120) · 기준 얼굴 = #992 달래(`992_new_npcs/concept/child_b.png` SHA `e3e9dc4b…` · A포즈 `4a3828fd…` · 3D Tripo `3f1dcf18…`).

## 기획서 (1단계 초안 — narrative-world + system-balance 합침 · PD 판정 전)

| 칸 | 내용 |
|---|---|
| 이름 · id | 달래(네임드 이름표 「달래」) · `dallae_infected` — 심굴 네임드 여우누이(`yeounui`) 자리 갈음(데이터 #991) |
| 가족 · 변종 | 새 가족(아이 몸 — 단독 네임드). **몸은 #992 달래 재사용 + 겉칠 추천**(system-balance) |
| 부류 · 쪽 | 사람 · 역병 쪽(혼을 먹힌 「텅 빈 사람」) · `kind = 사람 · plague = true` |
| 몸 형태 | 두 발 사람형(키 1.3m) |
| 자리 · 레벨 | 봉밀굴 3층(심굴) · 지역 12 + 네임드 2 = 14 |
| 행동 틀 · 기믹 | 돌진(DASH): 0.6초 웅크림 예고 → 곧게 달려듦(속도 8 · 길이 4) · 기믹 = 새 `cling`(매달림 — 1.5초 이동 ×0.5 · 재발 4초 · 조작 안 뺏음) |
| 수치 | 체력 180 · 피해 3~5(같은 층 잡몹보다 낮음) · 쿨 1.6 / 선딜 0.5 · 이동 3.8 · 방어 0 / 회피 15 · 넉백 0 · 경험치 60 · 싸움 15~25초(평타 12~15) |
| 속성 · 막이 | 물리 50 + 살 50 · 막이 = 살 +75만(불·벼락 약점 없음 — 사람) |
| 처치 | `death_style = ink_dissolve` 고정(불 재·얼음 박살·두 동강 없음) · 피 0 · 시체 없음 · 무릎 → 겉칠 걷힘(잠깐 원래 얼굴) → 먹으로 풀림 · 드랍 = 유품 하나(나무 새 / 3번 안 했으면 빨간 댕기) · 무작위 드랍 끔 · 유품 = 이야기 물건(장착 X 권고) |
| 외형 후보 | **A 번지는 먹**(손끝·소매·치맛단·땋은 머리 끝에서 먹이 번져 오름 · 눈 검푸른 한 점 — 추천) · **B 꼬리 그림자**(색 바램 + 바닥 그림자가 아홉 꼬리 여우 — 그림자는 이펙트로) · **C 먹 안개**(검푸른 먹 김이 피어오름 · 먹 눈물 한 줄 — 귀신처럼 읽힐 위험 중간) |
| 피할 것 | 몬스터 능청 · 웃는 얼굴 · 공격 도술 · 노출 · 왜색 + 상처·피·고름·핏줄·갈라진 피부 · 이빨 · 발톱 · 뒤틀린 관절 · 흰자위 눈 · 깜짝 공포 · 무당·소복 귀신 결 · 무기 든 손 |
| 동작 | idle·walk = #992 몸(0) · run·hit · 달려들기 준비 = Mixamo · 붙잡기 = Mixamo 먼저 → 없으면 Tripo AI 20 · 무릎 주저앉기(die 대신) = Mixamo kneel → 안 맞으면 Tripo AI 20 · 쓰러져 누운 대기(스위치 끈 장면) = Mixamo |
| 이펙트 큐 | 예고 `enemy_windup` · 붙잡힘 = 살 겉칠(#906) · 먹 풀림 = D-118 「몸이 먹으로 풀림」 큐 재사용(확인 필요) · 네임드 발밑 먹 원 끔 · 붓 이름 없음 · 「풀림 + 유품」 묶음 = 이펙트 카드 따로 |
| 소리 | 기합·신음·사망 없음 · 짚신·숨·천 · 처치 = 먹 풀리는 소리 · 비명 없음 · 한마디 = 대사 음성(#994) |
| 한마디 후보 | 등장 「도사 아재… 엄마가 기다리래요.」 / 「도사 아재, 여기 안 추워요. 같이 있어요.」 · 끝 「도사 아재… 엄마는 어디 갔어요?」 / 「도사 아재… 나, 이제 집에 가도 돼요?」(#990이 다듬음) |
| 싸움 칸 스위치 | `story_fight = false` → 어그로·공격·기믹·경험치·피격 끔 · 누운 대기 → 다가가면 장면(원래 얼굴 → 먹 풀림 → 유품) |
| 바이블 칸 · 면 수 | 인물·NPC · Polycount 12,000(별 모델일 때만) |
| 예산(견적) | **추천 = 몸 재사용 + 겉칠: Tripo AI 동작 0~40** · 별 모델이면 3D 40 + 리깅 20 + 여유 60 + AI 동작 20×1~2 = 140~160 · 이미지(Codex) = 시안 6 + 다듬기 2 + A포즈 0~3 |

락 후보(지휘 판단): 감염된 달래 = D-080 처치 연출 · D-084 네임드 드랍 · D-110 쓰임 줄의 예외(먹 풀림 고정 · 유품 하나) / `monsters_v2 §4.3 ⑨`(몬스터는 말하지 않는다)와 끝 한마디 = 「풀린 뒤의 아이는 몬스터가 아니다」.

## PD 지시

- **2026-10-29 「구미호 그림자는 빼고 피부 촛점 충혈 이렇게 다시생성」** → B(꼬리 그림자) 기각 · 감염 표현에 **잿빛 피부 · 풀린 초점 · 충혈된 눈** 추가(수위 기준 갱신: 먹·그림자 + 피부색·눈 — 상처·피·피부 훼손·피눈물은 계속 없음). 2차 시안 = A+(먹 + 피부·눈) · C+(먹 안개 + 피부·눈) · D(피부·눈만) × 2.

- **2026-10-29 「A+2」** → ① 외형 = A+2(먹 번짐 + 잿빛 피부·풀린 초점·충혈 · 고개 숙임) 채택 · 나머지 시안 기각.
- **2026-10-29 「추천대로」** → ② 몸 = #992 달래 몸 재사용 + 먹 겉칠(3·4단계 skip) · ③ 붙잡기 = 새 「매달림」 기믹 · ④ 유품 = 부모 찾기 한 판 나무 새 · 안 한 판 빨간 댕기(이야기 물건) · ⑤ 예산 = Tripo 40까지 · Codex 5장까지.

## 원화 시안 (1단계 · Codex gpt-5.6-sol · 참조 = child_b + H1)

| 시안 | 파일 | SHA-256 | 판정 |
|---|---|---|---|
| A1 번지는 먹 | `concept/dallae_inf_a1.png` | `239c04bf2cf79346a9901c985147bfea8557ef1b9a77cfb6a992e742ab67ad6a` | 기각 — PD 10-29 「A+2」 |
| A2 번지는 먹(고개 숙임) | `concept/dallae_inf_a2.png` | `49659a61525ccdea75befc487838fe23b32ac1691bf5742e275136e465d2eef3` | 기각 — PD 10-29 「A+2」 |
| B1 꼬리 그림자 | `concept/dallae_inf_b1.png` | `8ff803e03674b1171161eed7ca9771b88956ef2f950a0ab2f78e0ea94804f341` | **기각** — PD 10-29 「구미호 그림자는 빼고」 |
| B2 꼬리 그림자(고개 숙임) | `concept/dallae_inf_b2.png` | `61ad032ebfd0ae41e3abc4cc807c21f0ca0f5dba3c2322f7397bc49f12a45928` | **기각** — PD 10-29 「구미호 그림자는 빼고」 |
| C1 먹 안개(먹 눈물) | `concept/dallae_inf_c1.png` | `cf4f2b6edad253b00788f69ce15aec5442af91957b180f50d1b0d2462882ebe8` | 기각 — PD 10-29 「A+2」 |
| C2 먹 안개 | `concept/dallae_inf_c2.png` | `39d3e3b8564a4808d1696ed480794aaa0870a5ac61981471410b6704f2d92abb` | 기각 — PD 10-29 「A+2」 |
| **2차** A+1 먹 + 피부·눈 | `concept/dallae_inf_ap1.png` | `e8212adea6702abcbb4358bc17dd88595fe92c2a741cfc8d091fab4af1123481` | 기각 — PD 10-29 「A+2」 |
| A+2 (고개 숙임) | `concept/dallae_inf_ap2.png` | `35963176face9b57e45b41f534867d8f22d9d73cda283038f3a20516e910e280` | **채택** — PD 10-29 「A+2」 |
| C+1 먹 안개 + 피부·눈 | `concept/dallae_inf_cp1.png` | `d1f7936adc911425ddb0fda466ad2749753af4b368dfdc1592a5a7ae66c2e1db` | 기각 — PD 10-29 「A+2」 |
| C+2 (고개 숙임) | `concept/dallae_inf_cp2.png` | `a542f3036c1d6a2705b20012a22e437ae21d41798d7ebe31157229391075aae0` | 기각 — PD 10-29 「A+2」 |
| D1 피부·눈만 | `concept/dallae_inf_d1.png` | `13246f255ffaaa4ac830d5f973df7b18986fc4afe15c0c6328ba74178cd484af` | 기각 — PD 10-29 「A+2」 |
| D2 (고개 숙임) | `concept/dallae_inf_d2.png` | `8bddc8d598e3d8b0a209403c56a030c480bd987e1f3e3953494c0fab91f4c525` | 기각 — PD 10-29 「A+2」 |

## 크레딧 · 이미지

| 단계 | 서비스 | 작업 id | 차감 | 잔액(전 → 후) |
|---|---|---|---|---|
| 1 원화 시안 6 | Codex CLI gpt-5.6-sol(내장 image_gen) | — | 이미지 6 | Codex 주간 창 남음 54%(리셋 11-04 17:30) · Tripo 0(2,060 그대로) |
| 1 원화 2차 6(PD 지시) | Codex CLI gpt-5.6-sol | — | 이미지 6 | Codex 주간 창 남음 53%(리셋 11-04 17:30) · Tripo 0 |
| 5 동작 무료 프리셋 8 | Tripo 웹 Animate(달래 리그 · ego jaehoi 프로필) | `3f1dcf18-1523-4a35-aef2-b83c7368dbfe` | 0 | 2,060 → 2,060 |
| 5 AI 동작 매달림 | Tripo Text to Motion | 같은 리그 | 20 | 2,060 → 2,040 |
| 5 AI 동작 무릎(기록 재사용) | Tripo AI Animation 기록 | 같은 리그 | 0 | 2,040 → 2,040 |

## 동작 (5단계)

- 내보낸 GLB = `tripo_web_993/dallae_presets_10.glb`(SHA `6c73e98f…` · 클립 10: idle · walk · run · hit_to_body_01 · hug · defeat_02 · defeat_03 · sob · depressed · jump · 텍스처 2K — 반입 때 1,024) · 띠 = `reports/993/motions_a.jpg` · `motions_b.jpg`.
- 판독(Claude): 쓸 것 = depressed(감염 대기) · defeat_03(쓰러져 엎드림 = 죽음 앞부분 · 대안 장면 누운 자세) · sob(잠깐 원래 얼굴) · hit_to_body_01(맞음) · run(달려듦). 약함 = hug(끌어안기로 안 읽힘) · jump(작은 콩) · defeat_02(서서 고개만).
- 빠진 것 = **매달림(달려들어 허리를 끌어안음)** · **무릎 꿇고 주저앉기** → Tripo AI 동작 20 × 2 = 40(예산 안) — PD 10-29 「40 써서 만들기」.
- 매달림 = Tripo Text to Motion 새로 생성(「Lunging Embrace」 · 4초 · 문장 = 「A small thin girl lunges forward two quick steps and throws both arms tightly around someone's waist at her chest height, pressing her face against them and clinging on, holding still while clinging」) · **20크레딧** · 2,060 → 2,040.
- 무릎 꿇기 = 계정 AI 동작 기록의 「Slumping to the Ground」(문장 「Death: the knees buckle and she sinks down into a kneeling seat…」)를 달래 리그에 다시 붙임 · **0크레딧**(잔액 그대로 확인) → 두 번째 생성은 안 함(20 아낌).
- GLB = `tripo_web_993/dallae_motions_12.glb`(내보내기 원본 SHA `eb77e5a6…`) → 클립 이름만 바꾼 `dallae_motions_12_named.glb`(SHA `aec1c81e…` · `cling` · `kneel`) · 띠 `reports/993/motions_c.jpg`.
- 쓸 클립(초안): 대기 = depressed · 걷기 = walk · 달려듦 = run · 공격(매달림) = cling · 맞음 = hit_to_body_01 · 죽음 = kneel(무릎 → 옆으로 쓰러짐) · 잠깐 원래 얼굴 = sob · 대안 장면 누운 자세 = defeat_03 끝 · 안 씀 = hug · jump · defeat_02.
