# #504 속성 표식 5종 — 원화 크기 검수 준비

미채택 원화 후보다. 게임 한자 교체·게임 반입·실게임 before/after 사진은 이 폴더의 산출물이 아니다.

두 라운드 모두 HOLD이며 native 알파 합성·실제 크기 검수를 기다린다. 생성 원본10장과 v2 알파 추출본5장을 보존하며, 이 검수 작업은 PNG의 색·알파·모양·여백을 변경하지 않는다.

- `original`: `reports/504/2026-10-02_round1/{fire,cold,lightning,sal,soul}.png` — 1024×1024 RGBA, alpha 0~254. 원본 자체가 검수판 입력이다.
- `revision1`: `reports/504/2026-10-02_revision1/{fire,cold,lightning,sal,soul}_v2_raw.png` — 1024×1024 RGBA, alpha 255인 검은 배경 생성 원본5장. 검수판에는 넣지 않는다.
- `revision1` 검수판 입력: 같은 폴더의 `{id}_v2.png` — alpha 0~255인 별도 추출본5장. 각 raw/추출본의 decoded RGB SHA-256은 같다. 알파만 다르다.

실제 발주 설정은 `CLOUD_CONFIG.json`, `CLOUD_REVISION1.json`과 각 라운드의 `.prompt.txt`·`.api.json`·`.job.json`·`.history.json`이 기준이다. v2는 검은 배경 Cloud edit → SplitImageWithAlpha → BiRefNetRMBG foreground alpha → SaveImageAdvanced 경로다. 원본 PNG와 API/job 기록은 그대로 보존했다. `REVISION_SCOPE.json` 등의 옛 후광/혼불 홈 누락 문구는 당시 요청 기록이며 최종 실패 판정으로 읽지 않는다. 아래 알파 검사로 원본 혼불 홈 누락 의견도 정정했다.

## 준비된 파일

- `manifest.json`: 두 라운드·raw/알파 추출본 구분, PNG·프롬프트 SHA-256, 팔레트, 검수 크기/배경/모드, 미반입 상태.
- `qa/source_check.json`: PNG15장의 크기·RGBA·알파 nonempty·threshold별 bbox·foreground RGB, 후보10장의 12/14/16/18/24px 알파 정량 검사, raw/추출본 RGB 일치 및 생성 기록 해시. Pillow 수치는 native 렌더의 시각 판정을 대신하지 않는다.
- `qa/visual_review.json`: PNG15장을 직접 본 비교 의견과 알파 검증에 따른 정정. 두 라운드 모두 HOLD이며 이 subagent는 native 캡처를 수행하지 않았다.
- `qa/project.godot`: 독립 Godot 프로젝트 및 부모 프로젝트의 재귀 스캔을 막는 표식.
- `qa/element_mark_board.gd`: 원본 `Image.load_from_file` → `ImageTexture`, CanvasItem 선형 필터로 그리는 독립 검수판. 게임 코드와 무관하다.
- `qa/analyze_sources.py`: 두 라운드 측정·manifest 재생성기. PNG·프롬프트·API/job 기록에는 쓰지 않는다.

## 정량 측정 재실행

```powershell
python C:/workspace/joseon/._tmp/assets_504/workbench/production/element_marks_504/qa/analyze_sources.py
```

후보10장은 1024/RGBA/투명·nonempty 알파/밝은 중성 foreground 기본 검사를 모두 통과했다. v2 raw의 불투명 검은 배경은 별도 보존 계약이므로 후보의 투명 검사와 섞지 않는다. 측정 실행 성공은 원화 수용이 아니며 시각 판정은 HOLD다.

## root용 native 캡처 CLI

```powershell
godot --path C:/workspace/joseon/._tmp/assets_504/workbench/production/element_marks_504/qa --script element_mark_board.gd -- --round=original --mode=all
godot --path C:/workspace/joseon/._tmp/assets_504/workbench/production/element_marks_504/qa --script element_mark_board.gd -- --round=revision1 --mode=all
```

`--round` 기본값은 `original`이다. 각 라운드의 source 폴더와 `{id}.png`/`{id}_v2.png` 이름을 자동 선택한다. 기본 출력 폴더도 아래처럼 나뉘어 서로 덮어쓰지 않는다.

- `qa/native/original/`
- `qa/native/revision1/`

다른 체크아웃에서 재현하려면 `--sources=<선택 라운드의 후보5 절대폴더>`를 추가한다. 파일명 suffix는 `--round`가 결정한다. `--out=<고유 절대폴더>`로 저장 위치를 지정할 수 있다. `--mode=color`, `gray`, `white`도 각각 지원한다.

실제 표시 장치와 Compatibility 렌더러가 필요하다. `--headless`의 dummy display는 명시적으로 거부한다. root가 정상 native renderer로 캡처하며, 이 subagent는 창을 띄우거나 캡처하지 않았다.

각 CLI는 같은 배치의 1280×800 PNG3과 `native_capture.json`을 선택 라운드의 출력 폴더에 저장한다. 제목과 receipt에 라운드를 적는다.

- `godot_504_color.png`: 기존 불/한기/벼락/살/영기 RGB 틴트.
- `godot_504_gray.png`: 기존 저항 회색 `(0.63,0.65,0.68)`.
- `godot_504_white.png`: 모두 같은 흰색으로 실루엣을 비교.

각 검수판은 후보80px 참고 행과 실제12/14/16/18/24px 행을 함께 보여준다. 매 칸 왼쪽은 어두운 UI `(0.05,0.045,0.06)`, 오른쪽은 밝은 흙색 비교 swatch `(0.62,0.56,0.46)`다. 흙색은 가독성 검사용 대표색이다. 후보 전체1024 사각형을 그대로 맞춰 그려 알파·여백 차이를 유지한다.

이 구조를 택한 이유는 동일한 native sampler·크기·배경에서 납품 후보를 직접 비교하기 위해서다. 사전 합성·축소 접촉표는 해당 native 샘플링을 재현하지 않아 이 단계의 검수 대안에서 제외했다. `project.godot` 표식은 qa 폴더의 독립 프로젝트 경계를 유지하므로 지우지 않는다.

Label3D 외곽선·부모 피해 숫자 펀치·약점1.5배·실제 HUD/툴팁 배치는 재현하지 않는다. 이미지 후보가 12px에서 구별되는지 보는 판이다. 현재 게임 색 사전 값만 복사했으며 게임 caller·수치·폰트·원본파일은 수정하지 않았다.

## 현재 리스크

1차 RGB 뷰의 넓은 겉보기 후광만으로 실제 후광이나 no-glow 실패를 확정하지 않는다. alpha>=16 bbox는 주 모양 가까이에 잡힌다. 원본 불꽃·눈꽃의 alpha>0 bbox는 좌/하단 경계에 닿지만 alpha>=16 여백은 각각 최소50/65px다. v2 후보5장의 alpha>=16 최소 여백은 모두69px 이상이다.

| 모양 | 1차 저알파 가중 총량 | v2 저알파 가중 총량 | 12px에서 확인할 것 |
|---|---:|---:|---|
| 불꽃 | 0.7693% | 0.2273% | 세 갈래와 두 홈이 열려 있는가 |
| 눈꽃 | 1.1656% | 0.5170% | 여섯 끝과 간격이 유지되는가 |
| 벼락 | 0.9640% | 0.4357% | 좁은 몸통·꺾임·아래 끝의 무게가 충분한가 |
| 살 | 0.7442% | 0.3933% | 중앙 빈 공간과 열린 코일을 읽을 수 있는가 |
| 혼불 | 0.6442% | 0.2556% | 한 갈고리 끝·초승달로 불꽃과 구별되는가 |

여기서 저알파 총량은 alpha1~127 픽셀의 alpha 가중합을 전체 alpha 가중합으로 나눈 값이다. 낮아졌다는 사실만으로 native 축소 가독성이 좋아졌다고 판정하지 않는다.

혼불 정정: 이전의 “1차 내부 홈 없음” 의견은 RGB 뷰만 보고 내린 오류였다. 원본도 alpha<128 내부 영역이31,198px 있으며 v2는26,850px다. 원본 `(400,760)`·`(620,780)`·`(500,800)`은 RGB가 거의 흰색이어도 alpha가0·1·0으로 내부를 비운다. v2의 해당 alpha는 모두0이다. 설명용 Pillow 12px 축소에서 두 라운드 모두 내부 빈 픽셀3개가 남는다. native 합성에서 실제 초승달 모양과 불꽃↔혼불 구분을 비교해야 한다. v2의 투명 영역에 남은 검은 RGB가 경계 샘플링에 영향을 주는지도 같은 판에서 본다.

벼락은 설명용 Pillow 12px alpha>=128 영역이 두 라운드 모두 너비4픽셀로 좁다. v2 혼불의 외곽은 다른 네 붓 모양보다 매끈하다. 이 두 항목도 root가 실제12/14/16/18/24px 칸에서 판단한다.

native PNG/receipt와 시각 검토가 있어야 캡처 성공·축소 가독성 결과를 추가할 수 있다. 이 subagent는 helper와 정량 검사만 준비했으며 창 제어·캡처·유료 생성·게임 caller 수정은 하지 않았다. 실제 게임 반입과 before/after 검수는 원화 채택 이후 별도 단계다.
