# H1 적 4종 · 3D 제작 준비

사용자가 승인한 H1 확장 계획 5단계의 산적·박쥐·부적술사·흑랑 제작 묶음이다. 원화 4장은 직접 검수를 마쳤지만, **현재 실제 적 3D 모델은 0개**다. 첫 산적 생성은 실행 전에 자동 승인 심사에서 거절됐다. 사용자에게 원화 4장의 Meshy 전송과 최대 120 credits 생성을 명시 승인받는 동안 전송·생성·리깅은 보류한다.

| ID | 외형·규격 | 전달물 상태 |
|---|---|---|
| bandit | 1.5m, 헤진 삼베·두건·빈손, 목제 곤봉 별도 | 입력·SHA·미실행 요청 준비 |
| bat | 높이 0.7m / 날개폭 1.2m, 자흑색 두 날개·두 뒷다리 | 입력·SHA·미실행 요청 준비 |
| talisman_master | 1.6m, 흰 도포·창백한 탈·양손목 부적, 투사체 별도 | 입력·SHA·미실행 요청 준비 |
| boss_heukrang | 2.4m, 검은 사족 늑대·붉은 눈 | 입력·SHA·미실행 요청 준비 |

목표는 각 8,000 triangles 이하, 내장 albedo 1,024px 이하, 무광 재질, 발 y=0, +Z 정면이다. 서비스는 2K가 최소이므로 최초 생성 뒤 최소한의 로컬 축소·축척 정리가 필요하다. 박쥐 높이와 날개폭은 모두 계약검사로 판정하며 단일비례 스케일로 둘 다 맞지 않으면 변형을 숨기지 않고 차이를 보고한다.

## 준비한 호출

공식 Meshy MCP 스냅샷에서 `meshy_image_to_3d`를 사용한다. D-069에 따라 `ai_model: meshy-7`을 명시한다. 스키마가 `latest + remove_lighting`는 Meshy 6을 유지한다고 안내하므로 해당 조합은 쓰지 않는다. PBR=false, 8k triangles, T-pose는 인간형만 요청하며 박쥐·사족 늑대에 인간 자세나 Mixamo 동작을 강제로 적용하지 않는다.

- 잔액: 2,543 credits (2026-09-17 08:10:37 KST, 공유 계정의 읽기 스냅샷)
- 이 묶음 생성 실행: 0회 / 생성 작업 ID: 없음 / 이 묶음 생성 비용: 0 credits
- 계획 상한: 모델과 텍스처 4개 × 30 = 120 credits. 리깅은 원형 시각 검수 이후 별도 단계다.
- 전체 입력 파일은 로컬 `inputs/concept.png`, 원본 경로와 SHA는 각 `input_manifest.json`에 있다.
- API 키·환경변수·data URI·base64 원문은 저장하거나 출력하지 않았다.
- 거절 원문과 적용 범위: `REVIEW_BLOCK.md`.

## 독립 검사 도구

`tools/review.gd`는 원본 GLB를 읽기만 하고 mesh/UV/albedo 크기/metallic/roughness/축척/발 높이/본/클립을 JSON으로 기록한다. 정면 +Z와 형상은 실제 렌더를 직접 확인해야 한다. 정적 이미지가 통과해도 리깅·5동작·game-ready 판정은 따로 남긴다. 모델이 없으면 자리표시자를 생성하지 않고 오류를 낸다.

`tools/capture.ps1`로 숨겨진 독립 Godot 프로세스에서 두 가지 모드를 실행한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/capture.ps1 -Model <absolute-candidate.glb> -Id bandit -Height 1.5 -Output <absolute-render-dir> -Mode neutral
powershell -NoProfile -ExecutionPolicy Bypass -File tools/capture.ps1 -Model <absolute-candidate.glb> -Id bandit -Height 1.5 -Output <absolute-render-dir> -Mode actual
```

`neutral`은 근접·흰 중립광이다. `actual`은 현재 게임과 같은 ortho 11 / pitch 35.264 / yaw 45 / 1280×720, 저장된 던전 Environment와 플레이어 광원(검수실 위치 x=1,z=1)을 쓴다. 바닥은 평평한 검수용 면이며 환경 타일 결과나 실제 전투 배치로 표시하지 않는다. 전체 조도를 올리거나 모델 재질을 암묵적으로 고치지 않는다.

검사 도구는 기존 도호의 읽기 스냅샷으로 실제 렌더와 JSON 생성을 확인했다. 테스트 이미지는 `tmp/h1_enemy_pack/smoke_reference/`에만 두고 **적 산출물로 갤러리·최종 결과에 포함하지 않는다**. 기존 게임·편집기·Blender 프로세스를 중단하지 않았고 원본 게임 자산도 변경하지 않았다.

## 애니메이션 범위

기존 적 GLB는 아직 없고 모델 설정 파일만 있다. 인간형 산적·부적술사는 Meshy 리그가 합격하면 기존 Mixamo/현재 도호 클립 재타겟 가능성을 검토한다. 곤봉 타격과 부적 투척은 검술 클립을 이름만 바꾸어 완료 처리하지 않는다. 박쥐와 흑랑은 날개·사족 전용 본 및 동작이 필요하고 현재 인간 클립은 재사용 불가다.

## 왜 이 구성인가

입력 원화, 미실행 요청, 실제 모델, 계약검사, 렌더를 분리해 승인 대기 상태와 제작 완료를 혼동하지 않도록 했다. 기존 게임에 후보를 바로 복사하는 방법은 아직 없는 3D 원형과 애니 검수를 건너뛰므로 사용하지 않는다. 모든 후보는 외부 에셋 저장소에 남기며 공식 반입은 파일 채택 후 D-064 절차로 진행한다.
