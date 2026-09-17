# H1 독립 3D 검수씬

**제작 결과:** 실제 H1 모델 2개·24본·3클립·1280×720 검수와 도호 주먹/검 소켓 교정 완료, 총80 credits(2623→2543). 로컬 교정 추가 비용0. 그립 교정·기술 검사·클립/재질 보존 통과와 최종 시각 승인 보류를 분리했다. 상세 결과는 [TRIAL_RESULTS.md](TRIAL_RESULTS.md), 생성물 루트는 `C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/`다.

소유 영역: `C:/workspace/joseon/tmp/h1_3d_trial/`와 아트 저장소 `workbench/production/h1-style-expansion-2026-09-17/3d_trial/`. 메인 프로젝트·에디터·Blender·저장 데이터는 수정하거나 종료하지 않는다.

카메라는 현재 메인 게임의 **ortho 11 / pitch 35.264 / yaw 45 / distance 30**, 캡처는 **1280×720**이다. 실제 던전 Environment의 전체 속성과 플레이어 반경광을 추출하고 현재 횃불 스크립트·석실 floor/wall/stairs GLB·텍스처를 재사용한다. 배치는 작은 독립 검수 방이며 실제 레벨 배치/전투 통합을 뜻하지 않는다.

## 준비와 실행

```powershell
& ./tmp/h1_3d_trial/prepare_trial.ps1
godot --headless --path C:/workspace/joseon/tmp/h1_3d_trial --editor --import --quit
& ./tmp/h1_3d_trial/capture_trial.ps1 -Mode assembly_reference -SwordProxy
```

`assembly_reference`는 현재 게임 모델을 **CURRENT_REFERENCE_NOT_H1.glb**라는 별도 사본으로 로드하며 모든 캡처/보고서에 H1 결과가 아님을 표시한다. NPC 자리는 회색 기준자로 보인다. H1 모델이 준비되면:

```powershell
& ./tmp/h1_3d_trial/capture_trial.ps1 -Mode h1_trial -Doho C:/.../H1_doho.glb -Merchant C:/.../H1_merchant.glb -SwordProxy -Socket C:/.../3d_trial/fist/H1_doho_socket.json -Output C:/.../3d_trial/captures/h1_trial
```

외부 GLB는 `GLTFDocument`의 `append_from_file`/`generate_scene`으로 로드한다. 도호 1.7m, 상인 1.6m로 표시하며 적용한 scale과 원본 AABB 높이를 보고서에 함께 적는다. 검 프록시는 현재 ActorVisual의 임시 검을 재사용하며 새 리그의 손잡이 정렬은 별도 확인해야 한다. 프록시를 실제 승인 무기로 기록하지 않는다.

idle/walk/attack 각각 세 시점의 PNG와 `report.json`, raw stdout/stderr 로그를 남긴다. 상인은 해당 장면에서 idle을 사용한다. 애니가 없으면 `available:false`로 기록하며 정지 그림을 애니 성공으로 취급하지 않는다. 보고서에는 원본 hash·삼각형·본·클립·실제 투영 크기·카메라 설정을 담는다.

기존 제작 코드를 독립 폴더에 스냅샷해 같은 로딩·크기 측정·무기 소켓 기준을 쓰는 구조다. 별도 간이 렌더러를 쓰면 실제 게임의 재질·카메라·리그 처리가 달라질 수 있어, 현재 Godot 코드와 환경을 재사용한다. `references/source_fingerprints.json`이 복사 시점과 원본 SHA256을 기록한다.

현재 GLB가 H1으로 자동 교체되거나 메인 게임에 반입되는 동작은 없다. 승인된 생성·리깅·상인 retexture만 완료했으며 추가 유료 요청은 실행하지 않는다.
