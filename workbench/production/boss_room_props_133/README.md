# #133 보스 방 기존 에셋 재사용 납품

새 이미지·모델 생성 없이 기존 승인 에셋의 원천, 실제 규격, 수명 제약을 Claude #344로 넘긴다. 이 폴더에는 README와 manifest만 납품한다. 실제 보스 방 배치·광원·흑랑 알베도는 #344의 별도 작업이며, 새 인게임 사진이나 배치 완료를 뜻하지 않는다.

## 납품 파일과 검수 원문

- `reuse_manifest.json`: 게임 `art/dungeon_props_133/reuse_manifest_2026-10-01.json`과 바이트 동일. 개별 SHA, GLB 실측, 코드 SHA, 소비 API, 사용 금지와 후속 수용 기준 포함.
- `reports/133/chain_model_check.raw.log` · `chain_model_check.exit.json`: 현재 게임 사슬의 Godot 검수 원문 / 종료 코드 0 · RESULT PASS.
- `reports/133/source_measurements_2026-10-01.json`: GLB 노드 변환을 적용한 파일 실측. 실제 맵 배치 후 치수가 아님.
- `reports/133/source_audit_2026-10-01.json`: 현재 코드·텍스처·메타·지도 구조 대조 38항목 PASS 원문.
- `reports/133/runtime_baseline_2026-10-01.json`: 게임 tracked runtime·시험·도구 3210파일 SHA 기준선.
- `reports/133/handoff_verification_2026-10-01.json` · 문서예산/diff-check 원문: 납품 종료 검증.

## 재사용 항목

| 항목 | 현재 승인 원천 | #344 계약 |
|---|---|---|
| 바닥 사슬 | `C:/workspace/joseon-assets/workbench/production/art_514/glb_graded/chain.glb`, 게임 `assets/models/props/chain.glb`과 동일 SHA | `PropMeshes.instance("chain_floor")`; 기존 h 비율 맞춤·원래 표면 재질 유지. `"chain"`은 벽걸이 코드 메시 |
| 재 얼룩 | `actors/kill_fx.gd`의 `stain_texture()` 64×64×3, `ASH_MARK=(0.08,0.07,0.065,0.88)` | 마스크·색만 사용. 전투 `stain()` 금지. 별도 정적 레벨 수명·무광·비충돌·피 설정 독립 |
| 재 더미 | `world/town_dressing.gd`의 Ash 원통 반지름 0.52/0.54, 높이 0.04, 로컬 Y0.02, 색 `(0.09,0.085,0.08)`, roughness1 | 모양·재질 계열만 빌림. 화톳불 전체·광원 추가가 아님 |
| 그을음 | `world/field_builder.gd` `md.r`, `world/town_ground.gd` `fire_center` | 국소 마스크만 빌림. 전역 바닥 알베도 교체 금지 |
| 불씨·불꽃 | `torch_embers` 10입자/1.6초/scale0.45 loop, `torch_flame` 기존 시트295×640/59×128/실제21프레임/12fps/메타units0.55/blend4 | 기존 Vfx attach, 레벨 소유 부모, loop128·torch48 상한 유지. 불꽃 메타 units와 기존 cue scale0.5는 별개 |
| 던전 먼지 | 기존 `dungeon_dust` ambient | 재사용; 중복 배치를 필수로 하지 않음. 퇴층 후 루프 정리 |

사슬 = 4370 tris, 파일 실측1×0.161269×1, 발Y0, static mesh1, 내장1024² JPEG, metallic0/roughness0.8/emission0. SHA `cba1428c4f157b259f67aee62b60ed1c7279604af44ace1561caacb7d837cc63`. 원천은 canonical checkout 파일 SHA를 직접 대조했고, 사슬은 추적된 게임 파일과도 동일하다. 원화·GLB 원천은 이번 자산 기준 HEAD에 없으므로 이번 카드가 이 파일들을 새로 Git 반입했다고 주장하지 않는다. 이번 폴더로 복사하거나 원본을 수정하지 않았다.

## #344 수용 기준

28×28 지도·14×13 전투 방·기둥 넷·3칸 복도, 계단·클릭 이동·돌격 경로를 유지한다. 흑랑은 불개이므로 승인 `den_boss.png`의 중앙 봉인 문양은 쓰지 않는다. 승인 원화 SHA는 manifest에 고정했다.

환경 재는 >20초 후에도 유지하고 피 설정·전투 자국32풀에 간섭하지 않는다. `KillFx.stain()`의 20초 흐림·공용 풀은 재사용하지 않으며 `burn_ash`(1.3초 처치 단발)를 ambient로 attach하지 않는다. 불꽃·불씨·먼지의 루프를 합쳐 전역128, 층당 횃불48 상한을 유지하고 레벨 종료 때 정리한다.

배치 후 전후 사진은 동일 카메라·줌·빛/노출·해상도·대표 시드를 사용한다. 후속 검증 = E2E `dungeon_layout` · `boss_floor` · `heukrang_pounce`, 단위 `test_vfx`. #133에서는 배치·이 후속 시험을 수행하지 않았다.

## 선택 후보

#132 `bone_heap`은 PD 미판정인 선택 의존성(pending_pd, enabled=false)이다. 7755tris/약1.277×0.5×0.9715/1K, SHA `3311ebe92829ec64601d21c16e48631da7bd60fbd517056131b7f7d18b066320`. 원본은 #132에 그대로 보존한다. #133은 메타데이터만 참조하며 승인 전 반입·배치하지 않는다.

게임 명세 = `docs/design/dungeon_props_133.md`. 보드 #344 인계·착륙·완료는 root가 담당한다.
