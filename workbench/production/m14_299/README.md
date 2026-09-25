# #299 몬스터 M14 1차 — 캡슐 일곱 → 모델 넷 (2026-09-25, PD 「모델 만들어」)

원화 = `workbench/production/catalog_320/img/`(#320, Seedream 5.0 Pro — #318 「원화 단계 없이 3뷰 i2i부터」): `mob_wandering_soul`(소복 귀신) · `mob_lured_archer` + `mob_lured_spearwoman`(홀린 여궁) · `mob_nachalnyeo_1`(나찰녀) · `mob_wild_dog_plague`(역병 든 들개). 후보 판 = `299_concepts12.jpg`.

## 단계 · 크레딧
| 단계 | 서비스 | 결과 | 크레딧 |
|---|---|---|---|
| 원화 → 흰 바탕 세 방향(i2i) | Meshy nano-banana-pro · `generate_multi_view` | `{sobok,yeogung,nachal,dog}_{0,1,2}.png` → `clean/`(1024² 투명 · 피사체 82%, 332_clean.py) · 판 `299_inputs_12.jpg` | 9 × 4 = 36 |
| 소복 귀신 메시(정지 · 떠다님) | Meshy 7 multi-image · remesh 12k | `models/sobok_gwisin/sobok_gwisin_mesh.glb` — task 01a0d887-e137-76b9-8e51-98f08bcf6bf4 | 30 |
| 홀린 여궁 메시(두 발) | Meshy 7 multi-image · A자세 · remesh 12k | `models/hollin_yeogung/hollin_yeogung_mesh.glb` — task 01a0d887-e98e-74f0-84e2-e8a48b8e2a34 | 30 |
| 홀린 여궁 리깅 | Meshy rig · 키 1.55 | rig 01a0d88b-b24a-70f9-9b2c-49e2f9511c76 (walk·run 무료) | 5 |
| 홀린 여궁 동작 5 | Meshy animate | idle 0 · attack_bow 224 Archery Shot · attack_spear 240 Thrust Slash · hit 178 · die 8 → `models/hollin_yeogung/clips/clips_*.glb`(합치기 = 반입 카드) | 15 |
| 나찰녀 메시(정지 · 떠다님) | Meshy 7 multi-image · remesh 12k | `models/nachalnyeo/nachalnyeo_mesh.glb` — task 01a0d887-f155-73b9-8971-e917e2aa2ebd | 30 |
| 역병 든 들개 메시(네발) | Higgsfield `hunyuan3d_v3_image_to_3d`(흑랑 길) | `models/plague_dog/plague_dog_hunyuan.glb`(35MB) — job c7373fc8-b3a5-42cf-a51a-ca33fbf517ef | Higgsfield 1회 |
| 들개 다시 굽기 | Meshy remesh 12k | `models/plague_dog/plague_dog_mesh.glb`(16MB · 텍스처 큼 → decimate --tex=1024) — task 01a0d88d-59c4-758f-b914-0edd5ec8f1be | 5 |

합계 = Meshy 151 · Higgsfield Hunyuan 1회(사양 §12.1 · §17.9 추정 ≈ 180 안). 혼불 = 코드 공 + 있는 불꽃 시트(0).

## 판
- `299_models_render9.jpg` — 소복 귀신 · 홀린 여궁 · 나찰녀 × 정면 · 게임 각 · 옆(Blender Workbench)
- `299_dog_render4.jpg` — 들개 네 방향

## 반입 메모 (게임 쪽)
- 소복 귀신 = 떠도는 넋·객귀·물귀신 한 모델 + 색(틴트) · 키 1.6 + 0.3 떠 있음(가족 키 하나로 — #437 발견).
- 홀린 여궁 = 활·창 한 몸 · 무기는 코드 소품(활·창, 0) · 활 = attack_bow · 창 = attack_spear.
- 나찰녀 = 정지 메시 + 코드 흔들림 · 키 1.7 + 0.2 떠 있음 · 살 구슬은 이펙트(#357).
- 들개 = 네발 절차 클립(`rig_quadruped.py`, 흑랑 #79 길) · 어깨 0.75 · 몸길이 1.5.
- 큰 중간 파일(클립별 GLB · Hunyuan 원본)은 저장소에 넣지 않는다 — task/job id로 다시 받는다.
