# 독립 후보 재현

이 폴더는 게임 메인 프로젝트와 별도인 Godot 프로젝트다. 기존 게임/Blender 창을 중지하지 않는다. 산출물 보존을 위해 재현할 때는 이 폴더를 새 `tmp` 폴더로 복사해 실행한다. 런타임 경로는 `run_review.ps1`의 설치 경로를 따른다. 새 설치는 필요하지 않다.

## 실제 렌더 재실행

1. `models/` 14개와 `props/` 4개, `reference_actor/`의 H1 참고 사본을 유지한다.
2. PowerShell에서 `./run_review.ps1 -RenderOnly`를 실행한다. 별도 숨김 background 프로세스로 1280×720 캡처와 보고서를 갱신한다. `-RenderOnly`는 이미 생성된 GLB만 읽으므로 원본 게임 타일이 없어도 된다.
3. `review_stdout.log`, `review_stderr.log`, `render_report.json`을 확인한다. 프로세스 시간 초과 시 runner는 자신이 시작한 Process 객체만 종료한다.

## 18 GLB 재생성

1. `module_report.json.sources`의 8개 원본을 `C:/workspace/joseon/assets/models/tilekit_stone/`에서 작업 사본의 `source/`로 복사하고 SHA256을 비교한다. 원본은 수정하지 않는다.
2. Blender 5.2.2 LTS를 `--background --factory-startup --python prepare_stairs.py`로 별도 실행한다. 후보 `prepared/`에 계단 단순화본이 생긴다.
3. `./run_review.ps1`은 모듈 생성, 소품 생성, 독립 headless import, 실제 GPU 렌더를 차례로 수행한다.
4. Python 3.13 표준 라이브러리로 `python audit_glb.py`를 실행하면 내보낸 GLB 자체를 다시 읽어 winding·노멀·삼각형·해시·외부 의존성을 확인한다. `python finalize_package.py`는 원본 보존 해시를 확인하고 목록·갤러리·QA 문서를 만든다.

## 코드와 검사 구분

- `build_modules.gd`: 환경 14종. 기존 floor/wall 복사본 winding 교정, 재질 보존, 새 모듈의 정확한 치수.
- `build_props.gd`: 검/검집/곤봉/부적 4종. 실제 검 원점과 길이, double-sided 무두께 부적.
- `review.gd`: 실제 GLB import·카메라·조명·복제 배치·가림 진단·RightHand 부착·9포즈 캡처.
- `tools/weapon_socket.gd`, `tools/model_check.gd`, `actors/*`, `world/*`, `references/*`: 필요한 기존 게임 도구/카메라/광원/셰이더의 읽기 전용 시점 사본. 주 프로젝트 동작을 바꾸지 않는다.
- `h1_hand_measured_fist.json`, `measure_h1_hand.py`: 열린 손 원본을 읽어 측정했던 중간 진단. 최종 주먹 교정 JSON을 대체하지 않는다.
- `h1_socket_correction.json`: 실제 렌더에 사용한 현재 H1 소켓과 샘플. `09/10` 렌더는 GT1 값 비교용, `11_*`가 H1 측정값.
- `textures/H1_matte_atlas.png`: 공급 TEX01 원본과 SHA256이 같은 1254×1254 PNG. `atlas_layout.json`의 UV offset/scale을 정점에 굽는다. 기본 픽셀을 편집·분할·축소하지 않는다. 직접 GLTFDocument로 읽는 검수 씬은 표준 mipmap/anisotropic 필터만 런타임 생성한다.
- `12/13/14` 캡처는 최종 GLB 형상에 원래 단색 재질만 오버라이드한 control이다. 최종 도호·카메라·조명을 동일하게 유지하여 `01b/02/07` 재질판과 비교한다.

## 원시 로그

최종 `build_*`, `props_build_*`, `import_*`, `review_*`, `socket_measure_*` 로그를 보존한다. `build_initial_raw.log`는 최초 sandbox 로그 디렉터리/인증서 관련 메시지, `socket_probe_engine.log`는 독립 프로젝트의 `ActorVisual` 클래스 사본 누락으로 실패했던 최초 원문이다. 필요한 읽기 전용 사본 등록 후 최종 실행은 오류 없이 끝났다. 과거 실패를 최종 통과로 숨기거나 최초 로그를 수정하지 않았다.

## 예산 및 제외 사항

18개 후보가 산출물이다. `reference_actor/`의 캐릭터는 소켓·크기 비교용 복사본이며 이 18종 수량에서 제외한다. 모든 후보 GLB는 텍스처/버퍼를 내부에 포함한다. 임포트 캐시, `.godot/`, `.import`, `.uid`, 사용자 로그 폴더는 배포 묶음에 포함하지 않는다. 이 예제는 충돌·길찾기·게임플레이의 통과 증거가 아니다.
