# #447 반입 QA — 2026-09-27

## 결과

- 승인 #446 assets main f7483c3에서 PNG6 정확 복사, SHA-256·RGBA/알파·최종크기·점유6/6 PASS.
- 여섯 ItemDef에서 icon 선언과 load_steps 외 데이터 필드 해시 동일6/6. Renderer는 변경0.
- 기존 #439 승인 파일17/17 해시 동일; 가방 하단 패랭이·가죽신·면 허리띠는 실제 전후 동일픽셀3/3.
- 반입 전 직접 창 모드 icon_intake58검사·stderr0. 반입 후 창 모드8종374검사·러너 자기검사5/5 PASS.
- 단위53종 검증 완료: 첫 전체 실행에서52종 PASS, 의뢰 기록1종은 출력 계약 미일치로 FAIL. tests/test_quest_journal.gd의 출력 한 줄을 공통 QUEST_JOURNAL_TEST fails=0 PASS 형식으로 바꾸고 동일 tools/test.ps1 Invoke-UnitScript로 해당 검사 재검 PASS(1.7초). 검사 본문/의뢰 구현은 불변. 처음 실패 로그도 보존한다.
- 설정 쓰기/재부팅 읽기·도구 자기검사·문서 예산 PASS. wt.py 자기검사117검사 PASS(80초).
- site_gate PASS(6초): 부팅 SCRIPT ERROR0·오토로드10/10·주 장면 OK, 러너 자기검사5/5. 직접 GODOT_BIN exe를 사용했고 개인 godot.bat는 변경하지 않았다.
- docs/art = 동일 구도 전후3쌍, JPG6 모두1280×720·300KB 이하. 원본16PNG·raw 로그·verification·검증 도구는 assets reports/447/integration_2026-09-27.

## 실제 입력과 화면

가방6/장비9/매직 피주 테두리/미식별 인장 표시, 긴 예도 마지막 점유 칸 집기·held 툴팁 숨김·원자리 되놓기, 피주↔삿갓 우클릭 장착 교체, 김 영감 실제 대화·거래, 여섯 재고와 인장 행 호버, 구매·판매 물건/가격 이동을 검사했다. 툴팁은 텍스트 전용이며 그림은 가방·장비·held·좌판에서 검수했다. 표본의 매직/미식별/재고는 ItemInstance만 변경한다.

인장1×1/작은 허리 칸의 전대는 세부문양보다 실루엣 중심으로 읽힌다. 승인 PNG를 추가 보정하지 않았다. 같은 창구도·물체·커서 좌표를 유지했으며 마을 불/플레이어 애니메이션·도력 회복 등 시간 흐름은 전후에 다를 수 있다.

## 재현

`tools/test.ps1 -E2e -Scenario icon_intake,equipment_ui,inactive_gear,ui_tooltips,item_ui,pickup_equip,vendor_quest,belt_unify -Windowed -Shots`

단위 = `tools/test.ps1 -Unit`. 의뢰 검사 표식 보수 전 첫 로그(447_unit.log)와 원래 러너 단일 재검(447_unit_quest_retry.log)은 자산 저장소에 함께 보존한다. 대량사진/영상은 게임 저장소에 넣지 않는다.
