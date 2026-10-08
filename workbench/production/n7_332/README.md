# #332 몬스터 N7 — 새 3D 모델 4 (2026-09-24, PD 「만들어」)

원화 = `workbench/production/catalog_320/img/new_{dueoksini,imugi,meokjine,mukeungeomi}.png`(#333, Seedream 5.0 Pro).

## 단계 · 크레딧
| 단계 | 서비스 | 결과 | 크레딧 |
|---|---|---|---|
| 원화 → 흰 바탕 세 방향(i2i) | Meshy nano-banana-pro · `generate_multi_view` | `{dueoksini,imugi,centipede,spider}_{0,1,2}.png` → 손질 `clean/*.png`(1024² 투명 · 피사체 82%) | 9 × 4 = 36 |
| 두억시니 메시 | Meshy 7 multi-image · A자세 · remesh 12k | `models/dueoksini/dueoksini_mesh.glb` (12,327 tri) — task 01a0d3d8-31b6-732d-8e95-39aef9d0a445 | 30 |
| 두억시니 리깅 | Meshy rig · 키 2.8 | rig task 01a0d3db-0600-73fe-a70b-ccc094013b72 (walk·run 무료) | 5 |
| 두억시니 동작 6 | Meshy animate | idle 0 · attack 128 Heavy Hammer Swing · attack_punch 214 Punch Forward with Both Fists · slam 127 Charged Ground Slam · hit 178 · die 8 → `models/dueoksini/dueoksini.glb`(merge_anims, 클립 8) | 18 |
| 이무기 메시 | Meshy 7 multi-image · remesh 12k | `models/imugi/imugi_mesh.glb` (12,536 tri) — task 01a0d3d8-39ef-75cf-bc83-79a991b745a5 | 30 |
| 지네 · 거미 메시 | Higgsfield `hunyuan3d_v3_image_to_3d` (다리 많은 것 = Hunyuan, 흑랑 전례) | `*_hunyuan.glb`(각 약 50만 tri · 4096 텍스처) — job 1a00b552… · df6a6e08… | 15 × 2 = 30 (Higgsfield) |
| 지네 · 거미 다시 굽기 | Meshy remesh 12k(텍스처 다시 굽기) | `models/centipede/centipede.glb` · `models/spider/spider.glb` — task 01a0d3dd-fcb0… · 01a0d3de-092b… | 5 × 2 = 10 |

합계 = Meshy 129 · Higgsfield 30 (예산 140~230 안).

## 판 사진
- `332_inputs_12.jpg` — 3D 입력 12장(두억시니는 T 대신 A자세로 나옴 → A자세로 뽑음)
- `332_models_render16.jpg` — 모델 넷 × 네 방향(Blender Workbench, 게임 각 · 옆 · 위 · 앞)

## 반입 메모 (게임 쪽 #332 후속)
- 이무기·지네 = 긴 몸(EnemyDef.Body.SERPENT): 머리는 ActorVisual 모델, 꼬리는 `SerpentTail` 마디 메시 — 메시를 **머리(든 목 부분) + 몸 마디 하나(+ 꼬리 끝)**로 잘라 쓴다. 지네는 원화보다 짧고 통통하게 나왔다 — 길이는 마디 수로.
- 거미·두억시니 = 적 데이터가 아직 없다(범굴·폐광 지역 데이터 뒤) → ModelDef만 먼저.
- 두억시니 리깅본은 발광·금속 흔적(Meshy) → `albedo_ops.py dielectric`, 게임은 발광 끔.
- 지네·거미 remesh본은 뷰어 기준 약 2.5만 tri · 텍스처 4096 → `decimate_glb.py --tex=1024`(비율 5% 아래 금지).
- 큰 중간 파일(클립별 GLB · Hunyuan 원본)은 저장소에 넣지 않는다 — task/job id로 다시 받는다.
