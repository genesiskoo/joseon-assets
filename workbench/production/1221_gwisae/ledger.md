# #1221 귀새 G3 — 3D 장부 (modeling_bible §6)

**바이블 칸** = 인물 · 사람형(§2) · **서비스** = Tripo 웹(§4, D-114) · **면 수 상한** = Polycount 12,000 · Triangle · 반입 8,000~15,000 · 텍스처 2K 생성 → 반입 1,024 · `-Budget char` · **예산** = ⏳ PD 결정 대기(추천 60크레딧 = 3D 40 + 리깅 Mixamo 20).

키 1.65m(도호 1.7 기준) · 정면 = +Z · 리깅 = Humanoid Mixamo 65뼈 · 반입 뒤 우리 쪽 = 단검 소켓 · 홍사 끈 SpringBone · 허리 탈 둘.

## 입력 원화 시안 (2026-11-08 · PD 판정 대기)

도구 = Codex CLI `exec` · `gpt-5.6-sol` · 내장 image_gen · scratchpad에서 실행. 참조 순서 = ① G02 보드 가운데 열 잘라낸 것(`sheets/approved-2026-09-17/catalog_gwisae_G01-G03.png`) ② G02 탈 확대(`video/MV_작두신내림_2026-10-26/refs/gwisae_G02_mask.png`) ③ H1 시트 왼쪽(화풍만, `sheets/approved-2026-09-17-h1/K2_H_doho_hero_options.png`).

| 파일 | 무엇 | SHA-256 | 판정 |
|---|---|---|---|
| `art/gwisae_apose_a.png` | A — G02 그대로, 긴 분할 외투(무릎 위) · 넓은 소매 | `8a2fd6ec1db17cfaaddc04f995ab1b10f6822af45dbea23d31755e6c7b07ff2a` | 대기 |
| `art/gwisae_apose_b.png` | B — 짧은 분할 외투(허벅지 중간) · 좁은 소매 · 무릎 아래 바지 드러남 | `fdaa6f3262a0c806fe1d2968166506ca10e58fd6c171e5df4c2a191487e8c71d` | 대기 |

프롬프트 = `art/gwisae_apose_<a|b>.prompt.txt`. 공통: 탈 쓴 채(감은 초승달 눈 · 무표정 붉은 입) · 손 비움 · 단검 뺌(소켓으로 따로) · 홍사 = 오른 허리 감은 고리 · 여분 탈 둘 = 왼 허리 · 끈·술은 아래로 짧게.

## 3D (채택 + 예산 뒤)

| 물건 | 게임 id | 입력 그림 | 서비스 | 작업 id | 설정 | 결과 면 수 | 텍스처 | 판정 | 차감 | 잔액(전 → 후) |
|---|---|---|---|---|---|---|---|---|---|---|
| 귀새 몸 | `gwisae` | — | Tripo 웹 HD | — | H3.1 · Triangle · 12,000 · Ultra 켬 · 2K · PBR 끔 · 조명 지우기 · Private | — | — | — | — | — |
| 귀새 리깅 | 〃 | — | Tripo 웹 Rig · Humanoid · Mixamo | — | idle · walk(무료) | — | — | — | — | — |
