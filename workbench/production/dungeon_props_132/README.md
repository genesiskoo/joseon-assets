# #132 던전 소품 모델링 입력

승인 #336 소품 판 `props_den.png`·`props_bongmil.png`에서 물건별 형태를 분리한 투명 PNG다. GPT Image 내장 도구로 물건을 한 장에 하나씩 다시 그렸고, 이는 원화 제작 당시 기록이며, 현재 3D 후보와 게임 반입 여부는 아래 준비본 v2 절에서 구분한다. 횃불·바위는 #321 모델이 있어 중복 제작하지 않는다.

| 파일 | 지역 | 원화 단계 계획 W×D×H(유닛, 실측 아님) | 배치 |
|---|---|---|---|
| `refs/bone_heap.png` | 흑랑 굴 | 1.5×1.0×0.5 | 방 가장자리 |
| `refs/roots.png` | 흑랑 굴 | 1.3×0.3×1.6 | 벽·천장 쪽 |
| `refs/nest.png` | 흑랑 굴 | 1.4×1.2×0.4 | 방 구석 |
| `refs/palisade.png` | 흑랑 굴 | 1.8×0.3×1.7 | 막힌 통로·외곽 |
| `refs/seal_stone.png` | 봉밀굴 | 1.8×1.8×0.25 | 봉인실 중심, 전투 구역 바깥 |
| `refs/pillar.png` | 봉밀굴 | 0.7×0.7×2.0 | 외곽 |
| `refs/broken_statue.png` | 봉밀굴 | 0.9×0.9×1.3 | 외곽·기둥 근처 |

## PD 채택 및 후속 제작 — 2026-10-01

PD 「전부 확인 채택한다」로 위 7종 모델링 입력 형태를 채택했다. 봉인석의 강한 발광은 별도 효과와 모델 재질을 구분하여 낮추고, 파손 석상은 파손 정도가 실루엣에서 읽히도록 후속 3D 후보에서 보완한다. 기존 #321 횃불·바위는 재생성하지 않는다.

후속 제작 경로는 최신 **D-095 Comfy Cloud 3D 파이프라인**과 `joseon/docs/design/comfy_3d_pipeline.md`, 진행 카드 #531/#532를 따른다. 2026-09-25에 확인한 Tripo H3.1 40크레딧/건·최대 280크레딧은 당시 견적 이력이며 현재 가격이나 현 필수 승인 조건이 아니다. 실제 변환 전에는 현재 도구·견적·중복 제작을 대조한다.

`reports/132/`은 PD 검토용 축소 연락판이다. 출력 규격은 `joseon/docs/design/art_3d_pipeline.md §2`의 GLB·바닥 y=0·1유닛=1타일이다. 채택 기록 갱신 시점에 신규 생성 제출·GLB 제작·게임 반입·main 착륙은 하지 않았다. 형상 승인과 모델링 완료를 별도 상태로 기록한다.

## 3D 납품 후보 v2 — 2026-10-01

Comfy Cloud Tripo H3.1(v3.1-20260211) 성공 raw GLB7종과 준비본 v2 GLB7종을 보존했다. 생성 제출은8회이며 둥지 v1의 HTTP429 확정 실패 뒤 v2를 별도 제출해 성공했다. v1 둥지 GLB는 없고 runtime_prior_v1은 변환 이력7종이다. 신규 3D 결과는 PD 검토 후보이며 게임 반입·런타임 배치·main 착륙은 하지 않았다.

| 준비본 | 실제 삼각형 | 실제 X×Y×Z (폭×높이×깊이, u) | 실제 X×Z footprint / AABB 면적 |
|---|---:|---|---|
| models/bone_heap.glb | 7,755 | 1.277×0.500×0.972 | 1.277×0.972 / 1.241u² |
| models/roots.glb | 7,534 | 1.050×1.600×0.592 | 1.050×0.592 / 0.622u² |
| models/nest.glb | 5,874 | 1.206×0.391×1.200 | 1.206×1.200 / 1.447u² |
| models/palisade.glb | 5,652 | 1.800×1.308×0.298 | 1.800×0.298 / 0.537u² |
| models/seal_stone.glb | 5,840 | 1.281×0.250×1.277 | 1.281×1.277 / 1.635u² |
| models/pillar.glb | 5,799 | 0.944×2.000×0.938 | 0.944×0.938 / 0.885u² |
| models/broken_statue.glb | 7,858 | 0.774×1.300×0.611 | 0.774×0.611 / 0.473u² |

삼각형 정본은 Godot V2 model_check와 실제 GLB primitive이며 뷰어의 외곽선 중복 수치는 제외했다. 7종 모두 한 장1024²·발Y0·XZ 중앙pivot·Y축−90° 회전·균일 배율·금속0·거칠기1·emission0이다. 현재 크기는 실제 bounds와 runtime_v2 기록을 대조한 값이며 위 원화 계획표의 값으로 대신하지 않는다. footprint는 메시 AABB의 XZ 사각형이고 던전 충돌·통행 면적이 아니다.

봉인돌의 푸른 고리와 기둥/석재에 남은 색은 알베도에 구워진 색이다. emission0과 별개로 푸른 색 자체가 남는다. 파손 석상의 끊긴 팔 단면은 실제 정면/아이소에서 읽힌다. 전투 바닥·클릭면·길폭·어두운 던전 조명은 모델 뷰어7렌더만으로 판정하지 않는다.

기계 검수판4장 = reports/132/review_v2/01_den_source_glb.jpg, 02_bongmil_source_glb.jpg, 03_den_godot.jpg, 04_bongmil_godot.jpg. 모두1280폭·300KB 이하. 원화→GLB3뷰는 동일 패널/fit 기준이고 Godot 렌더는 동일 화면 영역만 확대했다. 그림을 다시 그리거나 모델/재질을 수정하지 않았다.

검수 원문과 SHA/실측 납품 manifest = reports/132/review_v2/manifest.json. 제작 raw = reports/132/comfy_h31/, Godot 실제 모델 검사/렌더 = reports/132/godot_v2/. review_build_raw.log는 288 checks/fails0, 보호 입력113개 SHA불변을 기록한다. 승인 원화7SHA·raw/준비본7SHA·균일 배율·실제 치수·바닥·재질·canonical 삼각형·게임 검수판 복사를 대조했다.

검수판 재현(유료 호출 없음): python reports/132/make_review_132.py --game-tools <joseon>/tools --game-review <joseon>/docs/art/132_dungeon_props_review. prepare_h31.py는 root가 실행한 변환기이며 새 모델을 준비하지 않으려면 재실행하지 않고 기존 v2 측정/원문을 읽는다.
