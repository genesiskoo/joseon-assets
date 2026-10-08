# #448 D1 소지품 2차 납품 후보 (상위 #274)

현재 실제 정의가 있으며 icon=null인 T2 머리·보조4 + 소모품2의 독립 물체 원화다. #446/#393 승인 화풍으로 내장 image_gen을 항목별1회 사용했다. 게임 반입은 아직 하지 않았다.

|id|이름|점유|최종PNG|
|---|---|---:|---:|
|jeongjagwan|정자관|2×2|160×160|
|cheomju|첨주|2×2|160×160|
|yundo|윤도|2×2|160×160|
|bujeok_mokpan|부적 목판|2×2|160×160|
|rejuv|청심환|1×1|80×80|
|talisman_thunder|벽력부|1×1|80×80|

BRIEF.md는 정본과 제작 해석, PROMPTS.md / generation_sources.json은 실제 프롬프트·내장 생성 원본출처, inputs.json은 점유/현재데이터 경로, manifest.json은 원본/패킹/현재ItemDef 해시다. source/items는 생성 원본 그대로, game/items는 기존 alpha16·8%여백·LANCZOS 패킹 결과다. 부적목판 원본 알파는0~254(나머지0~255)이고 보이는 외곽 후광 영역의 실제알파는0이었다. 원본의 near-opaque254를 그대로 유지하므로 불필요한 배경 제거/알파 증폭을 하지 않았다. 검수는 투명0와 객체>=250을 확인한다.

prepare_assets.py는 원본 패킹과 접촉판·외부Godot검수 대본을 준비한다. python prepare_assets.py 뒤 현재 게임 경로로 Godot --script <절대qa_godot.gd> -- --root=<이폴더> --out=<이폴더/qa> --mode=before|after|sizes. 세 raw로그는 reports/448/integration_2026-09-27/godot_<mode>.log와godot_<mode>_errors.log에 저장한다. python finish_review.py가 해시·알파·현재데이터 불변·실제 캡처3회와 승인 기준 동일픽셀을 검증해 gallery4장과verification을 기록한다.

## 왜 이 구조인가

현재 점유와 공통 UiSkin을 기준으로 그림을 독립 물체로 만들면 가방·장비·상점에 비율을 공유할 수 있다. 정사각 장식 액자로 통일하는 대안은 점유와 긴 물체의 형태를 흐려 기각했다. 원본을 남기고 패킹만 결정적으로 수행해 후속 반입·교체를 재현한다. 유니크 전용그림·아직 없는 ItemDef는 이 묶음에 넣지 않았다.

#274 핵심잔여67에서 이번 후보6을 채택하면61. 이 수치는 정의만 있는 품목과 설계에만 있는 품목을 포함한 상위 목록 기준이며, 현재 데이터6개를 미리 채택으로 세지 않는다.
