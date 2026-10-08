# #536 후속 수정 검토안 — 아직 미적용

현재 main37467dc5의 단위·도구와 전체 E2E116/116은 통과했다. #536의 단독/전체 동일 전투 재현은 아직 완료되지 않았다. 최신 전체 실행에서 초기12스트림은 같았고 Lv3 파수2 종료 state와 실제 공격/명중41/25→40/25, 최저HP32→34가 달랐다. 승패와 최종HP는 같다.

첫 확인된 배치 차이는 V 준비 뒤 도호(10.5,8.5)→(10.5,9.5)이다. 층 전환의 queue_free와 새 층 생성 경계가 유력하지만 첫 물리 충돌 관측이 없어 원인은 미확정이다.

승인 요청 범위는 #536의 깨끗한 작업 트리 rebase, 한정된 읽기 관측(흑랑 초기/첫 물리 전후·옛 층 충돌체·현재 층 소속), 증거가 뒷받침할 때 아래 검사 대본 수정, 기존 단위+focused2회+최종전체회귀, 카드 커밋이다. 관측 연결은 기존 종료/조기실패 정리 경계를 따른다.

```diff
 func _prepare_key(keycode: Key, ticks: int) -> void:
-	await t.tree.physics_frame
+	if keycode == KEY_BRACKETRIGHT:
+		await t.tree.process_frame
+	else:
+		await t.tree.physics_frame
 	var tick0 := Engine.get_physics_frames()
 	t._key_state(keycode, true)
 	Input.flush_buffered_events()
```

층 내려가기 입력만 process_frame에서 전달한다. 이후 실제 press부터 세는6물리틱, V의5틱, 전투6틱, 고정시드식·실제 명중·게임AI/위치/타이머/수치·45초/8초/3판·승패 기준은 유지한다. 변경되는 파일은 검사 대본·사양·검사 전용 관측 및 관련 단위뿐이다. 유료 생성이나 push는 없다. 이 제안은 실제 원인 검증 이전에 게임 동작을 수정하거나 성공을 보장하지 않는다.

자동 승인 검토가 앞선 읽기 전용 감사의 범위를 이유로 rebase를 두 번 거절해 후속 구현은 실행되지 않았다. 원래 작업 트리 HEAD82fdb019, 미커밋0, 기존raw50개가 보존됐다.
