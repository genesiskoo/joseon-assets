# #487 T3 칼3·운룡검 원화 검수

2026-09-28. 최종 후보는 운검(ungeom), 환두대도(keun_kal), 칠성검(chilseonggeom **v2**), 운룡검(u_yongcheon)이다. 네 물체의 재질·날·마감으로 T3와 유니크의 가치를 보여준다. 사양 기반 원화이며 실제 T3 ItemDef/UniqueDef와 게임 반입은 아직 없다. 데이터 작업 #272 뒤 최종 정의와 점유 칸을 다시 대조해야 한다.

## 원본과 패킹

- 내장 imagegen 신규 생성 4회와 칠성검 정밀 편집 1회. 모든 native는 724×2172 RGBA, 알파 범위 0–255다.
- `source/items/`의 native 사본은 생성 파일과 SHA-256이 같다. `generation_sources.json`과 `PROMPTS.md`에 정확한 프롬프트·생성 경로·칠성검 편집 참조를 보존했다.
- 최종 `game/items/`는 모두 80×240 RGBA, 예정 점유 1×3이다. 공통 알파 16 기준 경계·사방 8% 여백·Lanczos 비율 보존으로 패킹했다. 그림의 형태를 손으로 다시 그리지 않았다.
- 칠성검 첫 원안은 별점 8개였다. 선택된 v2는 직접 눈으로 센 손잡이 쪽 3점 + 국자 쪽 4점 = **7점**이다. 원안 native와 최초 프롬프트·패킹·검토판은 `variants/v1/`에 그대로 남겼다. 이 점수 판정은 자동 이미지 인식 검사라고 주장하지 않는다.
- 환두대도 고리 내부 native (360, 105)의 RGBA는 (0, 0, 0, 0)이다. 원화의 빈 고리도 직접 확인했다.
- 운검은 쪽빛 손잡이와 담청옥, 환두대도는 넓은 날과 고리 꼭지, 칠성검은 붉은 끈과 칠성 새김, 운룡검은 유백색 손잡이와 옥·금속의 운룡/구름 장식으로 구분한다. 외부 오라·불꽃·글자·로고는 없다.

## 실제 UiSkin 검수

게임의 현재 `UiSkin`을 실행해 메모리의 후보 PNG와 예정 1×3 영역을 그렸다. 검토용 Texture2D 경로만 메모리에서 설정했으며 게임 PNG를 설치하거나 새 아이템 정의를 만들지 않았다. 모든 후보/참조 경로를 그리기 전에 검사한다.

| 모드 | 검수 내용 | 결과 |
|---|---|---|
| forty | 가방 40px 칸·검정 40px 칸·좌판 48px 칸 | PASS |
| sizes | 실제 UiSkin 30/48/60px 칸 | PASS |
| black_sizes | 검정 바탕의 실제 30/48/60px 칸 | PASS |
| base_compare | 현재 T2 본국검·쌍수도·사인검과 후보 비교; 운룡검은 이번 운검 후보와 비교 | PASS |
| constellation_pair | 같은 원화 부분/배율과 40/60px 칸의 원안 8점 → v2 7점 전후 | PASS |

최종 5회 모두 `currentT2references/resource_paths/render validated` 표식이 있으며 SCRIPT ERROR/엔진 ERROR가 없고 stderr는 비어 있다. `forty`, `sizes`, `black_sizes`, `base_compare`, `constellation_pair`와 원화 종합판을 직접 검수했다. 30px 칸에서는 미세한 새김이 약해지고, 40px 이상에서 주요 형태·재질·손잡이 차이를 읽는다. 작은 아이콘에서 별점 7개를 각각 쉽게 셀 수 있다고 주장하지 않는다.

첫 비교 렌더는 같은 배치 운검을 운룡검의 참조로 새 Texture2D에 중복 `take_over_path`하면서 기존 운검의 경로가 지워져 짧게 찌그러졌다. 직접 검수로 발견한 **검수 도구 문제**였다. 같은 배치 참조는 기존 운검 Texture2D를 공유하도록 고치고 경로 검사를 추가한 뒤 5모드를 모두 다시 실행했다. 첫 렌더·raw·검수 스크립트·verification은 `variants/qa_path_collision/`에 기각본으로 보존했다. 최종 `qa/`와 `verification.json`은 재실행 결과다. 원화와 게임 런타임에는 이 문제로 인한 변경이 없다.

## 보존·기록

현재 `icons_a` PNG 42개와 `icons_h1` PNG 19개, 모든 ItemDef/UniqueDef 및 관련 UI를 합친 154개 파일은 작업 전후 SHA-256이 동일하다. 정본 `item_catalog_v2.md`·`item_system_v2.md`도 동일하다. 모든 예정 정의 경로가 아직 존재하지 않는 것을 확인했다. 기존 칼·물약 폴리싱, 수치·세이브·3D·애니메이션 변경은 없다.

최종 JPG는 6장, 각각 폭 1280·300KB 미만이다. 게임 `docs/art/487_d1_t3_swords/`에는 이 JPG와 설명만 둔다. native·PNG·raw·기각 렌더는 자산 저장소의 이 작업 폴더 및 `reports/487/2026-09-28/`에 있다. 해시·알파·로그·JPG 용량은 `verification.json`에 기록했다.

#274 승인 핵심 잔여는 **35개**를 유지한다. 이번 후보 4개가 전부 채택될 때만 31개(현재 정의 4·설계 27)로 갱신한다. 이 카드는 PD 확인에서 멈추며 아직 자산 main 병합·실제 게임 반입·push를 하지 않는다.

## 재현

자산 작업 트리에서 `python workbench/production/item_icons_487/review_487.py --defer-game-gallery`로 native/원안 해시, 예정 규격, 고리 알파, 현재 런타임 보존, 최종 5개 raw와 JPG 규격을 다시 검사한다. Godot 재촬영은 `qa_godot.gd`를 게임 작업 트리 프로젝트에서 실행하고 `--pack=<이 작업 폴더> --out=<이 작업 폴더/qa> --mode=<위 5개 모드>`를 준다. 실행 stdout/stderr는 모드별로 reports에 보존한다. 게임 작업 트리의 `python tools/doc_budget.py`와 `git diff --check`로 문서 규약도 확인한다.
