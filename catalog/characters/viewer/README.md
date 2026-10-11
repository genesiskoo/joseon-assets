# 조회본 빌드

JSON 데이터만 수정하고 이 도구로 조회본을 다시 만듭니다. 입력의 승인·연결 상태를 수정하거나 원본을 이동하지 않습니다. Pillow가 필요합니다.

```powershell
python catalog/characters/viewer/build_catalogue.py --catalog catalog/characters/catalog.json --assets-root C:/workspace/joseon-assets --game-root C:/workspace/joseon --output catalog/characters --standalone-url file:///C:/workspace/joseon-assets/catalog/characters/index.html
python catalog/characters/viewer/test_viewer.py
```

- `index.html`: 이미지·데이터를 포함한 독립 조회본. 원본 링크는 실제 파일의 절대 file URI입니다. 로컬 경로를 복사해 파일 탐색기에서 열 수도 있습니다. 원본 저장소 위치를 바꾸면 다시 빌드하세요.
- `inline.html`: host 테마를 사용하는 fragment. fetch·외부 리소스 없이 이미지·데이터 포함. 기본 950,000바이트 이하로 크기를 조절합니다. 원본은 펼침 정보의 경로를 복사해 로컬 파일 탐색기로 엽니다. 브라우저가 file URI를 차단할 수 있어 인라인 원본 링크는 노출하지 않습니다. 본진이 대화용 writable 경로로 복사합니다.
- `previews/`: 원본 SHA와 crop_rect를 기록한 WebP 파생본·manifest·build-report. 원본은 변경하지 않습니다.
- `--mode standalone|inline|both`로 선택하고 `--inline-budget`으로 상한을 지정합니다.

패널 좌표가 명시되면 해당 범위의 파생 이미지를 만들고 표시합니다. 위치 이름만 있으면 자르기를 추정하지 않고 원본 보드와 선택범위 경고를 보여줍니다. GLB만 연결된 항목은 렌더를 가짜로 만들지 않고 미확인 타일을 표시합니다. 이미지 경로 없음은 미확인 표시, 명시 SHA 불일치는 빌드 실패입니다. 판정·로드·월드 표시의 자동 승격은 없습니다.

검색·역할·승인/연결/재확인 필터, 원화 버전 선택, 초상/모델 렌더/게임 화면 비교, 확대, 근거 펼침을 지원합니다. 650px 이하에서는 비교 칸을 세로로 쌓습니다. 인라인 UI 상태 저장은 host 지원이 있을 때만 사용하며 독립 조회본도 작동합니다.

선택 입력 --validation <C-check-output.json>은 C의 capture_checks만 읽어 해당 asset_id의 조회용 runtime.freshness를 대체합니다. 원화 판정·로드·월드 표시는 바꾸지 않습니다. --assets-overlay <staging-worktree>는 canonical assets에 없는 미착륙 파일만 읽는 임시 입력이며, 착륙 후에는 없이 재빌드하세요.

