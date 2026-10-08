# D1 T1 소지품 6종 납품 후보 (#446, 상위 #274)

채택한 #393/#439 화풍의 현재 T1 미제작6종. 게임 반입은 아직 하지 않았다.

| id | 이름 | 점유 | 최종 PNG |
|---|---|---:|---:|
|satgat|삿갓|2×2|160×160|
|piju|피주|2×2|160×160|
|injang|인장|1×1|80×80|
|yedo|예도|1×3|80×240|
|mituri|미투리|2×2|160×160|
|jeondae|전대|2×1|160×80|

source/items = 내장 image_gen 투명 원본6장, game/items = 점유×80px 투명PNG6장. generation_sources.json/PROMPTS.md = 실제 프롬프트6개·원본출처, manifest.json = 원본/산출물/현재ItemDef해시 및알파/크기. prepare_assets.py = 승인#393 alpha16·8%여백·LANCZOS 패킹/검수판. qa_godot.gd = 현재게임공통 UiSkin을 사용한 외부 검수대본. qa = 실제GPU캡처와Pillow확대판. 재실행은 python prepare_assets.py, 이후 현재게임경로로 Godot --script <절대qa_godot.gd> -- --root=<이폴더> --out=<이폴더/qa> --mode=before|after|sizes. finish_review.py가 세 실행 raw로그 및 원본/가공본을 검증하고4장jpg+verification을 기록한다. qa_godot의 가상리소스명은 이짧은프로세스에만 있고게임파일을 쓰지 않는다.

## 전체 카탈로그

catalog_274.json = 읽기 조사 결과. 핵심미제작73장(현재정의42/설계만31), 현재모든장비를 D1로 바꾸려면 핵심밖 추가10. 이번6장이 채택되면 핵심잔여67. 승인D1 소지품11+스킬6은 원본·가공본·반입본해시17/17 일치, 소지품별칭5는 그대로 재사용한다. 옥20·호리병·운룡검은 아직ItemDef가 없으며 대표유니크전용PNG 반입은 UniqueDef가아이콘을 읽는경로부터 필요하다. 미구현품목이나 이름제안을 실제 확정데이터처럼 만들지 않았다.

## 구조 선택

물체를 칸배경과 분리하면 칼/띠/갓의 실제점유와비율을 가방·장비·상점에 공유할 수 있다. 정사각 액자에 통일하는 대안은 긴칼과넓은띠의형태를 잃어 기각했다. 원본을 남기고 패킹만 결정적으로 수행해 후속교체를 재현한다.
