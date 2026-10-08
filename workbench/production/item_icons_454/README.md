# #454 D1 퀘스트 봉인물3 후보

흑랑의 봉인패·장산범의 봉인고리·불가살이의 사슬 조각. 내장 image_gen/transparent_background=true로 독립 생성3회. 수정 대상 없이 참고2장의 화풍만 사용했다. 원본 source/items는1254×1254 RGBA, 반입용 후보 game/items는80×80 RGBA. 사양 BRIEF.md, 실제 프롬프트 PROMPTS.md, 생성 출처 generation_sources.json, 원본/패킹 SHA manifest.json, 현재 파일 보존 current_game_snapshot.json, 검증/한계 QA.md·verification.json.

원화 확대/파일 축소 qa/overview.jpg, 실제 UiSkin 전후 qa/ui_before.jpg·qa/ui_after.jpg,30/48/60px qa/ui_sizes.jpg. 전체 캡처와 raw 로그 reports/454/2026-09-27. 실제 게임 미반입·PD 확인 후보. 핵심잔여55에 포함되지 않는 추가3종이다.

재현: python prepare_assets.py로 동일 패킹과 확대판 생성. Godot --path=<현재 게임> -s=<이 폴더/qa_godot.gd> -- --root=<이 폴더> --mode=<before|after|sizes> --out=<qa>를 실행한다. 현재 정의·공통 UiSkin만 읽고 후보를 짧은 검수 프로세스 메모리에만 올린다.
