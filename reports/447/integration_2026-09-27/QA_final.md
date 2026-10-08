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


## 승인 후 최종 착륙 (#449 선행 보수 뒤)

PD 「확인 다음」 승인 후 최초 전체 검사에서 기존 회귀 3건과 전체 제한시간 부족이 드러났다. 카드 #449에서 제품의 잠수 최종 격자 거리 계약과 시험 준비/실행기만 보수했다. 같은 자리에서 #449 단위53·전체 E2E97/97·도구층 모두 PASS 후 main30af0bd2에 착륙했다. #447을 이 main 위로 재배치했고, 의뢰 출력 표식의 동일 보수는 #449로 합쳐져 #447 diff에서 빠졌다.

최종 #447은 승인 PNG6/다른 ItemDef 필드6/기존 아이콘17 해시 보존, 변경 아이템 단위시험 PASS, 관련 UI8종374검사 PASS를 다시 확인했다. 부팅/러너 빠른 검사도 별도 실행한다. 전체 회귀는 같은 자리의 #449 통과 결과와 재배치 후 변경 영역 재검을 합산해 사용하며, #447 자체에서 전체97을 새로 돌렸다고 주장하지 않는다. 이 최근 검증 뒤 `wt.py land --no-test`로 착륙한다. 처음 실패와 최종 raw 로그는 자산 저장소 reports/449 및 reports/447에 보존한다. 미push.
