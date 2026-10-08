# #491 T3 갑·포3 원화 검수

2026-09-28. 엄심갑(eomsimgap)·수은갑(sueungap)·심의(geuksang_dopo) 신규원화3. 정본 item_catalog_v2 §1.2·§1.3 / item_system_v2 §4.3, 예정T3/ARMOR/2×3/160×240 RGBA. 실제 ItemDef는 아직 없으며 게임반입은 #272 뒤 최종정의/점유와 재대조한다. 현재 승인 핵심 잔여31, 이번3이 전부채택될 때만28(현정의4·설계24)로 갱신한다.

## 원본·형태

내장 imagegen 신규3회, native1024×1536 RGBA/알파0~254. `source/items/`는 native 사본과 SHA-256이 같고 정확한 프롬프트와 native 경로는 `PROMPTS.md`·`generation_sources.json`에 있다. 최고 알파를 255로 올리거나 원본을 수작업 편집하지 않았다. 기존 공통 알파16·사방8%여백·Lanczos 비율 패킹으로 최종160×240 PNG3를 만들었다. alpha 최대254는 8비트 투명 PNG의 유효한 거의불투명 값이며 공통검사는250이상을 허용한다. 처음 정확히255를 요구한 검사 실패 전문은 `reports/491/2026-09-28/packing_initial_stderr.txt`에 보존했다.

직접 검수: 엄심갑은 둥근 호심경과 빈 가죽/직물 끈이고 전신갑옷으로 바꾸지 않았다. native 중앙위 빈 공간(512,150)의 알파0을 확인한다. 수은갑은 정교한 은빛 철판·남색 안감·작은 황동 마감의 가공세계 최상급갑옷이다. 실제 수은처리 고증이나 제작법을 주장하지 않는다. 심의는 흰 비단 예복·검은 가장자리·흰 허리끈·정돈된 긴 주름이다. 사람/마네킹/손/머리/무기/글자/로고/외부오라가 없다.

## 실제 UiSkin

현재 게임 UiSkin의 item_slot/item_icon을 사용해 예정 영역에 메모리 후보 PNG만 렌더했다. 신규 ItemDef나 PNG를 게임에 설치하지 않았다. 비교는 #464 PD채택 경번갑·두정갑·학창의의 최종 PNG3이며 해당 비교그림도 아직게임반입전임을 검토판에 명시한다. T2 실제정의의 tier2/size2×3, 승인비교 SHA3, 모든 후보/참조의 resource_path를 검사한다. 서로 다른물체의 길이와 실루엣을 같게 왜곡하지 않는다.

| 모드 | 내용 | 최종 결과 |
|---|---|---|
| forty | 가방40px·검정40px·좌판48px칸 | PASS |
| sizes | 실제 UiSkin30/48/60px칸 | PASS |
| black_sizes | 검정30/48/60px칸 | PASS |
| base_compare | 같은 UiSkin30/40/60px에서 승인T2 원화와 비교 | PASS |
| grayscale | 실제 UiSkin30/48/60px의 무채색 분석 | PASS |

최종5회 모두 `approvedT2references/resource_paths/render validated` 표식이 있으며 SCRIPT ERROR/엔진 ERROR0, stderr는 비어 있다. 최종 native3/종합판/모드5를 직접검수했다. 둥근금속판·철판배열·흰주름이 색을 뺀 뒤에도 구별된다. 30px에서는 미세새김/직물문양이 약해지며40px 이상에서 주요형태·재질·깃/허리끈을읽는다. 미세문양의 완전한 가독성을 주장하지 않는다.

최초 검수 스크립트에서 Image.duplicate의 자료형이 명시되지 않아 Color/명도float 추론이 실패했다. Image/Color/float를 명시한 뒤5모드를 모두재실행했다. 당시 스크립트와 stdout/stderr 전문은 `reports/491/2026-09-28/initial_qa_parse/`에 기각본으로 보존했다. 그림과 게임 UiSkin은 이 문제로 변경하지 않았다. 최종 qa/verification와 최초기각로그를 구별한다.

## 보존·기록

현재 icons_a PNG42·H1 PNG19·모든 ItemDef/UniqueDef·관련UI 등154파일은 전후 SHA-256이 같다. 정본 catalog/system 문서와 승인T2 참조SHA3도 동일하다. 예정 ItemDef가 아직없는 것을 확인했다. 기존검·물약폴리싱, 수치/세이브/3D/애니메이션 변경은 없다.

JPG6장/폭1280/각300KB미만은 게임 `docs/art/491_d1_t3_armor/`에 둔다. native/PNG/raw는 자산 이작업폴더와 `reports/491/2026-09-28/`에 보존한다. `verification.json`은 해시·알파·투명부분샘플·Godot로그·JPG용량을 기록한다. 아직미채택·미게임반입·미push이며 PD확인에서멈춘다.

## 재현

자산작업트리에서 `python workbench/production/item_icons_491/review_491.py --defer-game-gallery`로 원본/패킹/참조/문서 SHA, 현재런타임불변, 투명부분과최종Godot로그/검토판규격을 확인한다. 재촬영은 게임작업트리 프로젝트에서 `qa_godot.gd`를 실행하고 `--root=<이작업폴더> --out=<이작업폴더/qa> --mode=<위5개모드>`를 준다. stdout/stderr는 모드별 reports에 보존한다. 게임작업트리 `python tools/doc_budget.py`와 `git diff --check`로 문서 규약도 검사한다.
