# #485 원화 검수 (2026-09-28)

내장 image_gen으로 장검·짚신·도포·사인검4종을 각각 생성했다. native RGBA는 검 두 종724×2172, 짚신1254×1254, 날개옷1024×1536이다. 요청 비율과 실제 산출 크기를 구별해 manifest.json에 기록하고 원본은 변경 없이 source/items에 복사했다. 정확한 프롬프트와 native 경로는 generation_sources.json·PROMPTS.md에 있다. 알파16·사방8%여백·Lanczos 비율보존의 공통 패킹으로 80×240/160×160/160×240/80×240 RGBA를 만들었다. 모든 패킹 결과의 알파는0~255이며 경계 밖 투명 여백을 확인했다. 날개옷 원본의 최대 알파는254이고 주변 회색 RGB는 실제 알파0이다(robe_alpha_probe.json). 원화를 수정하거나 알파를 강제로255로 올리지 않았다.

실제 Godot4.7.2/UiSkin을 후보 메모리 Texture2D로 실행해 forty(40px 가방/검정/48px 좌판), sizes(30/48/60px칸), black_sizes, base_compare(기본과후보30/40/60px칸)을 검사했다. UniqueDef 이름·베이스와 ItemDef 점유·장착·tier·stack도 읽어 확인했다. 4모드 PASS, SCRIPT ERROR/ERROR0, stderr4개 모두 빈 파일이다. stdout/stderr 원문·렌더PNG는 reports/485/2026-09-28에, 검수 해시와JPG5장은 verification.json 및 게임 docs/art/485_d1_unique_equipment에 있다. 각JPG는1280폭/300KB미만이다.

시각 판정: 쇠 먹는 이빨은 짙은 쇠와 가는 밝은 양날·송곳니 꼭지, 축지 짚신은 촘촘한 엮임과 짧은 쪽빛 매듭, 선녀 날개옷은 교차 깃·넓은 소매·유백 비단, 사인참사검은 금빛 장식과 반사광이 있는 곧은 날로 구별된다. 검정칸에서도 주요 윤곽이 남고 날개옷에 외부 후광이 없다. 무채색에서 짚신의 엮임/천의 주름/검날 경계를 확인했다. 30px에서는 금속 새김·검 손잡이의 세부가 약해지며40px에서는 큰 실루엣/재질차, 60px에서 장식까지 읽는 수준이다. 검 두 종은 모두 장검의 가늘고 긴 물체이며 실루엣만으로 차이를 과장하지 않았다. UiSkin8px패딩과 표시 코드에 수정은 없다.

비단 도포 비교 그림은 #464 채택 자산이며 아직 #466 반입 전이다. 다른 셋은 현재 게임 베이스 그림이다. 원본·후보·베이스참조·대상정의 SHA를 대조했다. 제작 전후 기존icons_a PNG42/H1 PNG19·모든ItemDef/UniqueDef·관련UI런타임까지154파일이 바이트동일하다. 게임 수치·드랍·세이브·3D모델은 바꾸지 않았다.

현재 후보는 미채택·미게임반입이다. UniqueDef 전용그림 선택 선행 #484 뒤 채택된4종을 별도 반입 카드로 연결해야 한다. 승인핵심잔여39는 유지한다. 전부 채택될 경우에만 잔여35(대표유니크1·T3베이스9·오방옥20·호리병1·상위물약4)로 바뀐다. 기존 검·물약 후속 폴리싱은 이번 작업 범위 밖이다.

재현: prepare_485.py는 최초 스냅샷이므로 기존 증거를 덮어쓰지 않는다. python pack_485.py → Godot 직접 실행파일에 --path <게임작업트리> -s <qa_godot.gd> -- --root=<이 폴더> --out=<qa> --mode=<4모드> (stdout/stderr reports에 저장) → python review_485.py. Windows GUI 바이너리는 Start-Process -WindowStyle Hidden -Wait -PassThru로 종료까지 기다린다. finish_docs_485.py는 문서/검토판/후보 수량 기록만 작성한다.
