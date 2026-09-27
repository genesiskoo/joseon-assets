# #467 D1 장신구5 후보 검수

- 선택 후보: 복주머니·명두·야광주 v2·옥가락지·금가락지. 정확한 원본 경로와 프롬프트는 `generation_sources.json`, 원본/80×80 해시는 `manifest.json`.
- 생산: native `image_gen` 5종 + 야광주 대상 편집1. 원본 모두 1254×1254 RGBA/실제 투명, 후보 패킹 모두 80×80 RGBA/알파 0–255. 야광주 원안 및 80×80 패킹은 `source/items/yagwangju.png`·`game/variants/yagwangju_v1.png`에 보존했고, 짧은 걸이/큰 구슬 v2를 `source/items/yagwangju_v2.png`와 최종 후보 `game/items/yagwangju.png`로 선택했다.
- 실제 게임 `UiSkin.item_slot`·`UiSkin.item_icon`: 가방40px, 검정40px, 좌판48px, 검정30px, 슬롯48·60px 검수 모두 통과. 30px에서 세부 마감은 줄어도 천/금속/구슬/두 반지의 큰 색과 형태는 구분된다. `qa/godot_forty.png`, `qa/godot_sizes.png`는 렌더 원본이며 JPG 3장은 게임 `docs/art/467_d1_accessories`와 `reports/467/2026-09-28`에 복사했다.
- `verification.json`: 기존 아이콘 PNG42개는 메인/작업 트리 바이트 일치, 총 런타임 파일109개는 줄끝 정규화 후 일치. `coin.tres`·`ident_scroll.tres`·`town_portal.tres` 3개의 바이트 차이는 Godot의 줄끝 형식뿐이며 Git 작업 트리는 깨끗하다. 선택한 다섯 ItemDef의 SHA는 manifest와 일치한다.
- 두 Godot 렌더는 `GODOT_D1_467_PASS` 및 exit0. `godot.bat` 실행기에서 `'M' is not recognized as an internal or external command, operable program or batch file.` 한 줄이 각 실행 앞에 출력됐으나 Godot SCRIPT ERROR/엔진 ERROR는 없었다. 해당 원문은 `reports/467/2026-09-28/godot_stdout.txt`에 보존한다.
- 판정: **PD 확인용 후보이며 아직 게임에 반입하지 않았다.** #274 승인 잔여51 유지. 다른 미제작 아이콘과 기존 검·물약의 후속 폴리싱은 별도 카드.
