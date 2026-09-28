# #483 원화 검수 (2026-09-28)

내장 image_gen으로 원화3종을 각각 만들고 장산범의 눈은 실제 축소에서 눈빛 대비가 약해 한 번 보강했다(생성3+정밀 편집1). 최종 선택은 거울 v2이며 원안 native/source·정확한 프롬프트·80px 패킹·최초 UiSkin 렌더·raw는 source/items/u_jangsanbeom_eye.png와 variants/v1/에 보존했다. 최종 프롬프트는 PROMPTS.md, 최초 프롬프트는 variants/v1/generation_sources.json에 있다. 모든 native는1254×1254 RGBA이며 출력3은80×80, 알파0~255다. 원본/후보/베이스 참조/대상 UniqueDef·ItemDef SHA를 대조했다.

실제 Godot4.7.2/UiSkin을 후보 메모리 Texture2D로 실행해 forty(가방40/검정40/좌판48), sizes(30/48/60), black_sizes, base_compare(채택 베이스와30/40/60)을 검사했다. 두 반복 각각4모드 PASS/오류0, stdout/stderr 원문을 보존했다. 마지막 생성 이후 재검수한 결과와 모든 해시는 verification.json 및 reports/483/2026-09-28에 있다. 게임 PNG42·아이템/유니크 정의·주요 아이콘 표시 코드까지135파일이 작업 전과 바이트 동일하다.

시각 판정: 곡선의 밝은 송곳니와 어두운 옥 마감, 금속 둥근 거울과 큰 호박색 눈빛, 붉은 속무늬 유백 구슬이 서로 및 일반 베이스와 구별된다. 거울 v2는40/48px에서 눈빛이 원안보다 또렷하며 전후 검토판은 동일 UiSkin/카메라/배율의 컷을 확대 없이 나란히 배치했다. 30px에서는 세부 문양보다 실루엣과 큰 색 면을 기준으로 확인한다. 실제 UiSkin의8px 패딩은 원화 때문에 바꾸지 않았다.

후보 산출물은 게임에 설치되지 않았다. 현재 UniqueDef.icon/전용 ItemInstance 그림 선택 경로가 없어 후속 반입에서 전용 그림 선택·fallback·미식별 정책을 정하고 가방/장착/커서/좌판/이름표 회수를 검증해야 한다. 수치·드랍·세이브·3D모델은 바꾸지 않았다. 기존 검과 물약의 폴리싱은 이번 제작 범위 밖이다.

재현: python prepare_483.py는 제작 전 스냅샷용이므로 현재 증거를 덮어쓰지 말고 별도 출력으로 실행한다. python pack_483.py → Godot 직접 실행파일에 --path <게임작업트리> -s <qa_godot.gd> -- --root=<이 폴더> --out=<qa> --mode=<4모드> (stdout/stderr reports에 저장) → python review_483.py. Windows GUI 바이너리는 Start-Process -WindowStyle Hidden -Wait -PassThru로 종료까지 기다린다. preserve_v1.py는 첫 검수 이후 v2 선택 전 실행했으며 과거 증거를 다시 쓰지 않는다.
