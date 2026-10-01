# #543 보스 조우 검사와 물리 경계

전체 통합 검사 116종 중 story_cutin의 26개 판정에서 실제 11m 조우와 Esc 복귀 두 판정이 실패했다. 나머지 115개 시나리오는 통과했다. 수정 범위는 검사 대본이며 승인 원화, 실제 Boss 조우 신호, 11m 계약, 게임 정지와 Esc 복귀, 기존 26개 판정 및 전투 수치를 유지한다.

## 규칙과 구조

정지 해제 후 process frame 두 개를 기다리는 대신 실제 컷인이 보일 때까지 최대 1초 기다린다. 기존 E2e.wait_until의 process delta 제한을 사용하므로 컷인이 세계를 정지해도 끝없이 기다리지 않는다. 기존 판정에서 boss 종류, 세계 정지, 실제 조우 신호 1회를 계속 검사하고 intro_sent도 확인한다. 컷인 전후와 Esc 후 물리 틱, 신호 수, intro_sent, 화면·메뉴·정지 상태를 전문 로그에 남긴다.

Boss._physics_process가 조우 신호를 만들지만 E2e.frames는 process frame만 기다린다. headless shot은 즉시 끝나고 key는 대기 전에 Esc를 전달한다. 조우가 아직 발생하지 않으면 Esc는 시스템 메뉴를 열어 다시 정지할 수 있다. 실패 원문에는 당시 물리 틱 수가 없어 0틱 여부는 확정할 수 없으며, 이 설명은 코드 경계에서 도출한 원인 추론이다. 이를 관측 로그와 제한된 조건 대기로 검증한다. runtime Boss나 컷인을 바꾸거나 신호를 직접 내보내는 방식은 실제 조우를 검증하지 못하므로 채택하지 않는다.

## 검증 자료

최초 실패 후보: 850a0b8e66039556294bf02d56b11c05422d0411. 원본 전체 로그는 reports/543/2026-10-01/before_full_e2e.godot.raw.log 및 before_full_landing.stdout.raw.log에 보존한다. focused story_cutin 26개와 수정 후 전체 회귀를 통과한 뒤 착륙한다. 검사 대본만 바뀌므로 새 시각 후보나 원화 채택은 추가하지 않는다.
focused 결과: 26/26 PASS, 러너 자기검사 5/5 PASS. 실제 관측은 물리 tick60→61 한 틱에 intro=false→true, 신호0→1, boss 컷인 표시와 세계 정지였다. Esc 후 tick63에서 컷인·정지·메뉴가 모두 false였다. 전문은 focused_story_cutin.godot.raw.log 및 focused_story_cutin.stdout.raw.log에 보존한다. 전체 회귀는 착륙 도구의 필수 게이트로 이어서 실행한다.
