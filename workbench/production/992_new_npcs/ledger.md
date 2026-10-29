# #992 달래 · 갑돌 — 3D 장부 (modeling_bible §6)

**바이블 칸** = 인물 · NPC(§2) · **서비스** = Tripo 웹(§4, D-114) · **면 수 상한** = Polycount 12,000 · Triangle · 반입 8,000~15,000 · 텍스처 2K 생성 → 반입 1,024 · `-Budget char` · **예산** = 인물당 60크레딧(3D 40 + 리깅 Mixamo 20) × 2 = **120크레딧 — PD 승인 2026-10-29(지휘 세션 전달)**.

키: 달래 1.3m · 갑돌 1.75m(도호 1.7 기준) · 정면 = +Z · 리깅 = Humanoid Mixamo 65뼈.

| 물건 | 게임 id | 입력 그림 | 서비스 | 작업 id | 설정 | 결과 면 수 | 텍스처 | 판정 | 차감 | 잔액(전 → 후) |
|---|---|---|---|---|---|---|---|---|---|---|
| 달래 몸 | `dallae` | `dallae/modeling/front_apose.png` (SHA `4a3828fd…`) | Tripo 웹 HD · 정면 한 장(첫 아이콘) | `3f1dcf18-1523-4a35-aef2-b83c7368dbfe` | H3.1 · Triangle · 12,000 · Ultra 켬 · AI Complete 끔 · 2K · PBR 끔 · 조명 지우기 · Private | Triangle 11,071 · 정점 8,973 | 2K → 반입 1,024 | 채택(앞·옆·뒤 통과 — 손가락 분리 · 땋은 머리 · 댕기 · 앞치마) | 40 | 2,180 → 2,140 |
| 갑돌 몸 | `gapdol` | `gapdol/modeling/front_apose.png` (SHA `bf0325fc…`) | 〃 | `31b58319-11bb-4d6e-b04b-b0af83699aac` | 〃 | Triangle 11,708 · 정점 8,320 | 2K → 반입 1,024 | 채택(앞·옆·뒤 통과 — 패랭이 · 땋은 머리 · 짚신) · 밝기 0.530 = look_audit 밴드(≤0.45) 밖 → **PD 판정 10-29 「그대로 둠」** | 40 | 2,140 → 2,100 |
| 달래 리깅 | 〃 | — | Tripo 웹 Rig · Humanoid · Mixamo | 위와 같음 | 동작 프리셋 idle · walk(무료) | 65뼈 `mixamorig_*` · idle 15.33s · walk 2.33s | — | 채택 | 20 | 2,100 → 2,060(둘 합) |
| 갑돌 리깅 | 〃 | — | 〃 | 위와 같음 | 〃 | 〃 | — | 채택 | 20 | 〃 |

**합계 120크레딧**(예산 그대로) · 잔액 2,180 → 2,060.

| 파일 | SHA-256 | 비고 |
|---|---|---|
| `dallae/modeling/tripo_web_992/dallae_tripo_idle_walk.glb` | `3974b100fcbcf73969873b772904370924ec2bffd4efab552f184a4c82edff10` | Tripo 내보내기 원본(GLB · 2k · 뼈대 · 동작 2 · stay in place) |
| `gapdol/modeling/tripo_web_992/gapdol_tripo_idle_walk.glb` | `85d4b61b3a9d9b964820f96a4aa9046b708e9669ad90d09f1349ab50f32f17e2` | 〃 |
| `game/dallae/dallae.glb` | `1b9ab9162124711725a74ff82d634de14298b6493cf540ee679c5ebbe205c984` | `albedo_ops shrink --max 1024 --name basecolor` → `matte` = 게임 `assets/models/dallae/dallae.glb` 같은 바이트 |
| `game/gapdol/gapdol.glb` | `e2cffa9f0074eef391715701ebd35d0f104e7b3cc3df0fb70cfb3be7399781a8` | 〃 `assets/models/gapdol/gapdol.glb` |

반입(2026-10-29, `intake_model.ps1 -Height`): 둘 다 원본 키 0.98 → ModelDef scale 달래 1.329 · 갑돌 1.785 · .import = 억쇠·주모와 같이(60fps · 고정 트랙 유지 · 최적화 끔) · 영상 `reports/992/dallae_gapdol_walk.mp4`.

메모: 갑돌 패랭이는 몸과 한 덩어리로 생성(떼어 내 따로 만들지 않음 — 벗는 동작 없음). 달래 손목 댕기도 몸에 붙임. attack·hit·die 클립은 없다(NPC — 마을 대기·걷기만). 감염된 달래(#993)는 별도 몸.
