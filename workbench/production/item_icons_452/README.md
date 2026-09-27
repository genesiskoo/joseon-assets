# #452 D1 재료 아이콘6 후보

사양: BRIEF.md. 실제 생성 프롬프트: PROMPTS.md. 내장 image_gen/transparent_background=true로 물체별1회 생성했다. 원본 source/items는1254×1254 RGBA, 반입용 후보 game/items는 모두80×80 RGBA. generation_sources.json/manifest.json에 생성 경로·원본/후보 SHA256을 기록했다. 두 참조 이미지는 화풍만 참조했으며 수정 대상이 아니다.

원화/파일 축소는 qa/overview.jpg, 실제 공유 UiSkin 렌더 전후는 qa/ui_before.jpg/qa/ui_after.jpg, 크기 검수는 qa/ui_sizes.jpg. 검증과 한계는 QA.md, 기계 판정은 verification.json. raw는 reports/452/2026-09-27. 실제 게임 반입은 채택 뒤 별도 카드다.

재현: `python prepare_assets.py`로 같은80px패킹/확대판을 만든다. Godot를 현재 게임 --path로 실행하고 이 폴더 qa_godot.gd를 -s에 주며 --root=<생산폴더> --mode=<before|after|sizes> --out=<qa폴더>를 전달한다. 게임 ItemDef/공유UiSkin을 읽으며 후보PNG를 게임 경로에 쓰지 않는다.
