# #451 입력 경계 읽기 전용 검수

2026-09-27 · automap_input_audit · 후보 codex/451-bag-talisman-target.

구체적인 새 입력 결함 없음. pressed/released 동기화와 capture가 홀드 이동·우클릭 스킬 누수를 막는다. 첫 Esc, I/X, UI 좌클릭, 벨트 숫자키의 처리 순서는 사양과 일치한다. 대화의 _close_windows → Inventory 닫기 훅은 선택을 취소한다. 지역 전환의 teleport_to는 버퍼와 Visual 발동 예약을 함께 정리한다. 원본 이동/소진과 적 소멸은 확정/버퍼 실행 단계에서 재검증한다.

지정한 작업 자리만 읽음. 수정·추가 시험·보드 변경 없음. 실제 입력 검수는 주 세션의 headless/창모드 73검사 로그를 별도로 참조한다.
