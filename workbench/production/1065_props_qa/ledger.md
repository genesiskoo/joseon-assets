# #1065 새 소품 6종 — 장부 (2026-11-01)

PD 11-01 「추천대로 진행」(#1057 Q-a). 바이블 = `docs/design/modeling_bible.md` §3 · 정본 조사 = `docs/design/prop_audit_2026-11-01.md` §2.
원화 = Codex CLI(gpt-5.6-sol 내장 image_gen, 1024², 저장소 밖 scratchpad) · 3D = Meshy `meshy_image_to_3d` (latest = 7.1 · remesh · triangle · 2k · PBR 끔 · image_enhancement 끔 · auto_size 끔).
Meshy 잔액 전 3,783 → 후 3,603 (6 × 30 = 180).

| 물건 | 게임 id | 칸 | 입력 | 작업 id | 면 상한 | 결과 면 | 반입 텍스처 | 판정 | 차감 |
|---|---|---|---|---|---:|---:|---|---|---:|
| 혼례 비녀 | honrye_binyeo | 바닥 | input/honrye_binyeo.png (1차는 댕기와 같은 그림이 나와 버림 → 다시) | 01a194f8-f088-7677-97c7-743a23b119f9 | 1,200 | 1,217 | 256 | 채택 | 30 |
| 나무 새 | namu_sae | 바닥 | input/namu_sae.png | 01a194f8-fb4b-77db-8d02-f7c2c800608b | 1,200 | 1,252 | 256 | 채택 | 30 |
| 빨간 댕기 | ppalgan_daenggi | 바닥 | input/ppalgan_daenggi.png | 01a194f9-0736-70bf-ba0c-bbbc2ef8bfa6 | 1,200 | 1,235 | 256 | 채택 | 30 |
| 산딸기 한 줌 | sanddalgi | 바닥 | input/sanddalgi.png | 01a194f9-1325-731a-8680-ec9c01cc0ec8 | 1,200 | 1,013 | 256 | 채택(알갱이 결은 면 수에 뭉개짐 — 바닥 30px라 둠) | 30 |
| 깨는 궤짝 | wood_crate (몸 Body · 뚜껑 Lid) | 중간 | input/loot_chest.png | 01a194f9-1edb-736c-8a32-1fc7ca796e05 | 3,000 | 2,701 → 자른 뒤 2,927 | 512 | 채택 | 30 |
| 옹기 | onggi_jar | 작은 | input/onggi_jar.png | 01a194f9-29f6-7073-a714-490441fd6fd0 | 1,500 | 1,566 | 512 | 채택(알베도 채도 0.54 → 0.27 · 대비 ×1.8 — look_audit 띠) | 30 |

## 반입 손질
- 궤짝 · 옹기 = scratchpad `fit_split.py`(Blender 헤드리스): 발 y 0 · XZ 가운데 · 크기(옹기 키 0.72 = 옛 모델 · 궤짝 가로 0.9 → 0.90 × 0.52 × 0.66).
- 궤짝 = 키 0.81에서 자름 → 노드 Body · Lid(자른 면 = 어두운 속 재질 Inner). 게임 `actors/loot_prop.gd`가 Lid를 경첩에 단다.
- 바닥 넷 = `albedo_ops.py shrink --max 256 --name basecolor` → `intake_model.ps1 -Budget drop`.
- 폴더: input/(원화) · glb/(Meshy 원본) · fit/(맞춤·자름) · intake/(반입본) · preview/(렌더 · 시트).
