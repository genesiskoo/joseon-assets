# #1221 귀새 G3 — 3D 장부 (modeling_bible §6)

**바이블 칸** = 인물 · 사람형(§2) · **서비스** = Tripo 웹(§4, D-114) · **면 수 상한** = Polycount 12,000 · Triangle · 반입 8,000~15,000 · 텍스처 2K 생성 → 반입 1,024 · `-Budget char` · **예산** = **60크레딧 = 3D 40 + 리깅 Mixamo 20 — PD 승인 2026-11-08 「B 채택 · 60크레딧」**.

키 1.65m(도호 1.7 기준) · 정면 = +Z · 리깅 = Humanoid Mixamo 65뼈 · 반입 뒤 우리 쪽 = 단검 소켓 · 홍사 끈 SpringBone · 허리 탈 둘.

## 입력 원화 시안 (2026-11-08 · PD 판정 = B)

도구 = Codex CLI `exec` · `gpt-5.6-sol` · 내장 image_gen · scratchpad에서 실행. 참조 순서 = ① G02 보드 가운데 열 잘라낸 것(`sheets/approved-2026-09-17/catalog_gwisae_G01-G03.png`) ② G02 탈 확대(`video/MV_작두신내림_2026-10-26/refs/gwisae_G02_mask.png`) ③ H1 시트 왼쪽(화풍만, `sheets/approved-2026-09-17-h1/K2_H_doho_hero_options.png`).

| 파일 | 무엇 | SHA-256 | 판정 |
|---|---|---|---|
| `art/gwisae_apose_a.png` | A — G02 그대로, 긴 분할 외투(무릎 위) · 넓은 소매 | `8a2fd6ec1db17cfaaddc04f995ab1b10f6822af45dbea23d31755e6c7b07ff2a` | 기각(B 채택) |
| `art/gwisae_apose_b.png` | B — 짧은 분할 외투(허벅지 중간) · 좁은 소매 · 무릎 아래 바지 드러남 | `fdaa6f3262a0c806fe1d2968166506ca10e58fd6c171e5df4c2a191487e8c71d` | ✅ 채택 (PD 11-08 「B 채택 · 60크레딧」) |

프롬프트 = `art/gwisae_apose_<a|b>.prompt.txt`. 공통: 탈 쓴 채(감은 초승달 눈 · 무표정 붉은 입) · 손 비움 · 단검 뺌(소켓으로 따로) · 홍사 = 오른 허리 감은 고리 · 여분 탈 둘 = 왼 허리 · 끈·술은 아래로 짧게.

## 3D (2026-11-08)

브라우저 = ego 브라우저(PD 로그인 상태 그대로) · Tripo 웹 화면은 홈 → 3D Workspace → Model(HD Model) · 입력 = 첫 아이콘(사진 한 장).

| 물건 | 게임 id | 입력 그림 | 서비스 | 작업 id | 설정 | 결과 면 수 | 텍스처 | 판정 | 차감 | 잔액(전 → 후) |
|---|---|---|---|---|---|---|---|---|---|---|
| 귀새 몸 | `gwisae` | `art/gwisae_apose_b.png` (SHA `fdaa6f32…`) | Tripo 웹 HD · 정면 한 장 | `8a95ac26-a47e-4d25-85d8-221f96f40da8` | H3.1 · Triangle · 12,000 · Ultra 켬 · AI Complete 끔 · 2K · PBR 끔 · 조명 지우기 · Private · Parts·8K 끔 | Triangle 11,174 · 정점 9,115 | 2K → 반입 1,024 | 채택(앞·옆·뒤 통과 — 팔·몸통 떨어짐 · 손가락 분리 · 포니테일 등 뒤 허리까지 · 탈·홍사 고리·허리 탈 둘 형태 유지) | 40 | 1,765 → 1,725 |
| 귀새 리깅 | 〃 | — | Tripo 웹 Rig · Humanoid · Mixamo | 위와 같음 | 동작 프리셋 idle · walk(무료) | 65뼈 `mixamorig:*` · idle 15.33s · walk 2.33s | — | 채택 | 20 | 1,725 → 1,705 |

**합계 60크레딧**(예산 그대로) · 잔액 1,765 → 1,705.

| 파일 | SHA-256 | 비고 |
|---|---|---|
| `modeling/tripo_web_1221/gwisae_tripo_idle_walk.glb` | `2979b652ec5c5619b372dc26a3f70957111eb64a02d27019b4bb56bb6c2bd592` | Tripo 내보내기 원본(GLB · 2k · 뼈대 · 동작 2 · stay in place · 1,592,460 B) · 원본 키 0.98 → 1.65면 scale ≈ 1.684 · 금속 0 |

## 다음 (반입 · 이 카드)

- `albedo_ops.py shrink --max 1024 --name basecolor` → `matte` → `intake_model.ps1 -Id gwisae -Height 1.65` → `data/models/gwisae.tres`.
- 단검 소켓(오른손 `weapon_socket`) · 홍사 끈 · 포니테일 SpringBone = 보조 뼈 추가(Tripo Mixamo 뼈대엔 머리카락·끈 뼈가 없다 — rig_fix 보조 뼈) · 허리 탈 둘 = 지금은 몸과 한 덩어리(탈 바꿈 때 얼굴 탈을 갈아끼우려면 떼어 낼지 = 판단 거리).
