# 최종 잔여 아이템 원화 납품 · #274

#274의 이번 납품은 오방옥 5색×4단 20종과 호리병 1종을 Comfy Cloud 결과 그대로 보존하고 실제 UiSkin 함수로 확인하는 아트 후보 21종이다. 적옥 1·4단의 최초 RGBA 4채널→BiRefNet RGB 3채널 실패 원문과 성공 v2를 함께 남기고, canonical 제작 키에는 성공 v2만 매핑한다. 원본 raw와 분리 clean을 나누며, clean의 알파를 임의로 깎거나 다시 그리지 않고 premultiplied Lanczos로 비율 보존 축소·중앙 패딩만 수행한다. 오방옥 80×80/1×1, 호리병 80×160/1×2는 사양 기반 임시 제작 규격이며 실제 ItemDef/GemDef ID·홈 수·4단 최종 이름은 #265에서 대조할 null/미확정 값으로 남긴다. 가방40·좌판48·원화80과 어두운 칸·무채색·검정 합성으로 세공·손상·재질 품질 차이를 검수하고, 오방옥에는 물약 벨트 역할을 부여하지 않는다. 기존 PNG·ItemDef·효능·세이브·UI 코드는 변경하지 않는다. 이전 잔여28 원장을 보존한 채 #496 채택3 이후 승인 잔여25를 유지하고 candidate_ready21/pending_child5344를 별도로 기록한다. 이 구조는 원천 증거와 후보 평가를 실제 반입 정의에서 분리할 수 있어 채택했으며, 아이콘 제작 키로 게임 ID나 이름을 확정하는 방식은 정의·세이브 계약을 먼저 정해야 하므로 제외한다.

## 1. 납품과 생성 원문

- 자산 `workbench/production/item_icons_274_final/`: `prepare_274.py` · `review_274.py` · `qa_godot.gd` · `manifest.json` · `source/items/`(raw/clean 42장) · `game/items/`(임시 규격21장) · `qa/`(진단 전용).
- `reports/274/comfy_final_icons/`: root가 만든23 제출의 API 그래프·job·history·prompt, 성공21의 generated raw/clean 원문. 첫 적옥1/4 실패2도 원문 전체를 보존하고 v2만 canonical 제작 키에 선택했다.
- `reports/274/packing_final_2026-10-01/`: 알파·마진·종횡비·비밀 검사, actual UiSkin PNG/로그/JSON, 검수 결과·수작업 눈 검수 기록·SHA 기준선.
- 게임 [새 후보 원장](../../art/item_catalog_274/candidate_final_2026-10-01.json): 승인 잔여25 / 후보 ready21 / 별도 #534 물약4. 이전9/29 잔여28과 #496 후보 원장은 그대로 둔다.

Cloud 실행 그래프 = `OpenAIGPTImageNodeV2`(gpt-image-2.5-flare high) → `SplitImageWithAlpha` RGB → `BiRefNetRMBG`. 분리 전후 원화 RGB는21종 모두 정확히 같다. 모델이 만든 알파와 분리 clean 알파는 각각 통계를 보존하며, 최종 clean/패킹 PNG는 RGBA·alpha0..255다. 프롬프트 파일의 마지막 줄바꿈도 그대로 보존하므로 파일 SHA와 실제 실행 프롬프트 문자열 SHA를 별도로 기록했다.

## 2. 임시 규격·정의 경계

| 대상 | 수량 | 아트 패킹 규격 | 현재 상태 |
|---|---:|---|---|
| 오방옥 | 적·흑·청·백·황 × 4 =20 | 80×80, 1×1 제작 가정 | `design_only`. 실제 ItemDef/GemDef ID·홈·효능·등급은 null |
| 호리병 | 1 | 80×160, 1×2 사양 기반 검수 | `design_only`. 조합 창·ItemDef·저장 기능을 만들지 않음 |
| 상위 물약 | 4 | 별도 #534 | 이번21종에 포함하지 않음 |

4단 이름은 `맑은`과 `영롱한` 중 확정하지 않는다. 검수판의 `4단(명칭 미정)`은 제작 단계 표기이며 게임 문자열이 아니다. 실제 바인딩·최종 점유·홈 수는 #265 정의 반입에서 대조한다. 이전 승인 아이콘·ItemDef·효능·세이브·UI 코드는 변경하지 않았다.

패킹은 clean 알파의 전체 유효영역을 자르고, premultiplied Lanczos로 균일 축소한 뒤 중앙 패딩한다. 원본 알파 threshold·수작업 픽셀·마스크 보정은 없다. 모든 출력 모서리는 alpha0, 외곽 여백은 최소6px다. 무채색 이미지는 QA 진단용으로만 만들며 생산 PNG 색을 바꾸지 않는다.

## 3. 실제 UiSkin 검수판

| 판 | 보는 항목 |
|---|---|
| [어두운 칸](../art/274_final_item_art/godot_actual.jpg) | 원화 축소80, 가방40·padding8, 좌판48·padding3, 5색×4단 |
| [무채색](../art/274_final_item_art/godot_grayscale.jpg) | 같은 UI 크기에서 손상·윤곽·세공 차이 |
| [검정 합성](../art/274_final_item_art/godot_black.jpg) | 흑옥 가시성·경계·보이는 사각 배경·알파 halo 진단 |
| [호리병](../art/274_final_item_art/godot_horibyeong.jpg) | raw/clean 동일 RGB, 전체 끈·마개, 40×80 가방/48 좌판/80×160 임시 출력 |

렌더는 현재 `UiSkin.item_slot/item_icon`·선형 필터·같은 콘텐츠 영역을 사용한다. 메모리의 독립 `res://assets/sprites/ui/icons_a/qa274/` 텍스처 경로를 통해 기존 원화용 그리기 분기를 탔으며 기존 파일을 덮지 않았다. 후보는 ItemDef를 만들거나 실제 보유품으로 추가하지 않았다. 검수 JPG4장 모두1280폭·300KB 이하이며 원본 PNG/대량 알파 자료는 자산 reports에 보존한다.

## 4. 눈 검수와 한계

80px 원화·48px 좌판에서1단 깨짐,2단 대각 균열,3단 온전한 윤곽,4단 매끈한 마감이 읽힌다. 흑옥은 회색 반사와 외곽으로 검정 칸에서도 남고, 호리병의 박 두 마디·마개·허리끈 전체가1×2 검수 영역에 들어간다.

현재 가방40·padding8은 옥의 실제 콘텐츠를 약24px 높이로 그린다. 작은 크기에서는 특히3/4단의 재질·세공 차이가 약해지는 한계가 있다. 이번 카드에서 UI 여백을 바꾸지 않았으며 채택 판단에 이 조건을 함께 제시한다. 자동 PASS는 알파·SHA·규격·렌더 확인이고 PD의 미술 채택을 대신하지 않는다. 상세 판단은 자산 `visual_findings.json`에 남긴다.

## 5. 검증·후속

- raw/clean RGB21 동일, 원본·receipt SHA 유지, alpha·마진·종횡비21 통과.
- Godot actual/grayscale/black/horibyeong4 모드 렌더 통과.
- 비대상 tracked runtime·시험·도구3210파일, root Cloud 원문137파일, 이전 원장16파일 SHA 불변.
- Cloud 그래프·job/history·프롬프트 등을 포함한 원천 텍스트94파일 비밀 검사 통과.
- PD 채택 → #265 실제 정의 대조 → 별도 아이콘 반입. 그 전에는 승인 잔여25를 줄이지 않는다.

재현: 자산 폴더에서 `python prepare_274.py` → `python review_274.py --prepare-qa` → 게임 WT를 --path로 둔 Godot --script `qa_godot.gd`의4모드 렌더 → `python review_274.py`. 정확한 원본 SHA·job ID·그래프·프롬프트 경로는 manifest를 따른다. 보드·PD 질문·착륙·유료 제출은 root 담당이다.
