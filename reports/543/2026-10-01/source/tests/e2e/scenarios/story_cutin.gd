extends E2eScenario
## #96: 새 판의 판소리 사설, 확정 원화 보스 조우, 입력·정지·복귀를 실제 씬에서 확인한다.


func run() -> void:
	var cutin: StoryCutinUi = t.main.story_cutin
	var menu: Node = t.hud_panel("SystemMenu")
	t.check(not cutin.visible and t.main._skip_cinematics, "E2E에서는 보통 컷인이 자동으로 끼어들지 않음")
	await t.shot("before_opening")
	t.main._skip_cinematics = false
	t.main.start_game(false)
	await t.frames(2)
	t.check(cutin.visible and cutin._kind == "opening" and cutin._page == 0 and t.tree.paused, "새 판 → 사설 첫 장·세계 정지")
	t.check(bool(GameState.flags.get("opening_pending", false)), "오프닝 미완료 상태가 자동 저장됨")
	t.main.show_title()
	t.main.start_game(true)
	await t.frames(2)
	t.check(cutin.visible and cutin._kind == "opening" and cutin._page == 0 and t.tree.paused, "도중 타이틀 → 이어하기에도 사설 재개")
	await t.shot("opening_1")
	await t.click(Vector2(1160, 610))
	t.check(cutin.visible and cutin._page == 1 and t.tree.paused, "클릭 → 둘째 장, 세계는 정지")
	await t.key(KEY_ENTER)
	t.check(cutin.visible and cutin._page == 2, "Enter → 셋째 장")
	await t.shot("opening_3")
	await t.key(KEY_SPACE)
	t.check(cutin.visible and cutin._page == 3, "Space → 넷째 장")
	await t.click(Vector2(1160, 610))
	t.check(cutin.visible and cutin._page == 4, "클릭 → 마지막 장")
	await t.shot("opening_5")
	await t.key(KEY_ESCAPE)
	t.check(not cutin.visible and not t.tree.paused and not menu.visible and GameState.is_town(), "Esc → 사설 건너뛰고 같은 못골 판")
	t.check(not GameState.flags.has("opening_pending") and not (SaveSystem.read_checked().get("flags", {}) as Dictionary).has("opening_pending"), "사설 종료 시 미완료 표식과 저장 파일 정리")
	t.check(not cutin.open_boss("unknown") and not cutin.visible, "등록되지 않은 보스 원화는 컷인을 열지 않음")
	var boss_floor: int = AreaDb.get_def(&"heukrang_gul").boss_floor
	t.main.load_area(&"heukrang_gul", boss_floor, Level.SpawnHint.DEFAULT)
	await t.frames(3)
	var boss := t.tree.get_first_node_in_group("boss") as Boss
	if not t.check(boss != null and boss.def != null and boss.def.id == "boss_heukrang", "실제 흑랑 보스 층"):
		return
	t.main._skip_cinematics = true
	t.player().teleport_to(boss.global_position + Vector3(0, 0, 4))
	t.camera().snap_to_target()
	t.main.pause_world(true)
	await t.shot("before_boss")
	boss._intro_sent = false
	var signals: Array[Node] = []
	var observe := func(found: Node) -> void: signals.append(found)
	EventBus.boss_spotted.connect(observe)
	t.main._skip_cinematics = false
	var encounter_tick := Engine.get_physics_frames()
	t.note("컷인 조우 before tick=%d intro=%s signals=%d visible=%s kind=%s paused=%s menu=%s distance=%.3f" % [
		encounter_tick, boss._intro_sent, signals.size(), cutin.visible, cutin._kind, t.tree.paused, menu.visible,
		boss.global_position.distance_to(t.player().global_position)])
	t.main.pause_world(false)
	# #543: 실제 조우는 물리 틱에서 열린다. process frame 수 대신 실제 화면을 제한 시간 안에 기다린다.
	var opened := await t.wait_until(func() -> bool: return cutin.visible, 1.0)
	t.note("컷인 조우 after tick=%d delta=%d opened=%s intro=%s signals=%d visible=%s kind=%s paused=%s menu=%s" % [
		Engine.get_physics_frames(), Engine.get_physics_frames() - encounter_tick, opened, boss._intro_sent,
		signals.size(), cutin.visible, cutin._kind, t.tree.paused, menu.visible])
	t.check(opened and cutin.visible and cutin._kind == "boss" and t.tree.paused and boss._intro_sent and signals.size() == 1, "실제 11m 조우 → 원화 컷인·세계 정지")
	await t.shot("boss_heukrang")
	await t.key(KEY_ESCAPE)
	t.note("컷인 Esc tick=%d intro=%s signals=%d visible=%s paused=%s menu=%s" % [
		Engine.get_physics_frames(), boss._intro_sent, signals.size(), cutin.visible, t.tree.paused, menu.visible])
	t.check(not cutin.visible and not t.tree.paused and not menu.visible, "Esc → 같은 보스 전투로 복귀")
	for id in ["boss_jangsanbeom", "boss_bulgasari"]:
		t.check(cutin.open_boss(id), "%s 승인 원화 대응" % id)
		t.check(cutin.visible and cutin._boss.has("art"), "%s 컷인 자산" % id)
		cutin.dismiss()
	# 자동 신호는 보스 인스턴스당 한 번. 뒤따르는 물리 틱에 같은 컷인이 다시 열리지 않는다.
	t.main._skip_cinematics = true
	await t.frames(3)
	t.check(not cutin.visible and boss._intro_sent and signals.size() == 1, "같은 보스는 다시 컷인을 열지 않음")
	await _check_boss_guards(cutin, signals)
	EventBus.boss_spotted.disconnect(observe)


## 최신 장산범은 본체와 허상이 같은 Boss 상속 몸이다. 실제 허상 인스턴스로 생산·소비 양쪽 문턱을 확인한다.
func _check_boss_guards(cutin: StoryCutinUi, signals: Array[Node]) -> void:
	t.main._skip_cinematics = false
	signals.clear()
	var illusion: Node3D = preload("res://actors/boss_jangsanbeom.tscn").instantiate()
	illusion.set("def", preload("res://data/enemies/boss_jangsanbeom.tres"))
	illusion.set("illusion", true)
	illusion.set_physics_process(false)
	illusion.position = t.player().global_position + Vector3(1, 0, 1)
	t.level().add_child(illusion)
	t.check(illusion is Boss and not illusion.is_in_group("boss") and illusion.is_in_group("boss_illusion"), "실제 장산범 허상은 Boss 상속·보스 무리 밖")
	illusion.call("_physics_process", 0.0)
	t.check(signals.is_empty() and not bool(illusion.get("_intro_sent")) and not cutin.visible and not t.tree.paused, "11m 안 허상 물리 틱 → 조우 신호 0·컷인 0·정지 0")
	EventBus.boss_spotted.emit(illusion)
	t.check(not cutin.visible and not t.tree.paused, "외부 허상 조우 신호도 셸에서 거부·정지 0")
	cutin.dismiss()
	illusion.queue_free()
	await t.frames(2)
	# 원화 없는 실제 보스 조우는 이름 대응에서 끝나며 판을 멈추지 않는다.
	signals.clear()
	var unknown := preload("res://actors/boss.tscn").instantiate() as Boss
	unknown.def = (preload("res://data/enemies/boss_heukrang.tres") as EnemyDef).duplicate() as EnemyDef
	unknown.def.id = "boss_unknown_cutin_test"
	unknown.set_physics_process(false)
	unknown.position = t.player().global_position + Vector3(1, 0, 1)
	t.level().add_child(unknown)
	unknown._physics_process(0.0)
	t.check(unknown._intro_sent and signals.size() == 1 and not cutin.visible and not t.tree.paused, "미등록 원화 보스 실제 조우 → 신호 1·컷인 0·정지 0")
	cutin.dismiss()
	unknown.queue_free()
	await t.frames(2)
	# 본체는 같은 상속 구조에서도 실제 보스 무리로 한 번만 컷인을 연다.
	t.main._skip_cinematics = true
	t.main.load_area(&"beomgul", 3, Level.SpawnHint.DEFAULT)
	await t.frames(3)
	var master := t.tree.get_first_node_in_group("boss") as Boss
	if t.check(master != null and master.def.id == "boss_jangsanbeom", "실제 장산범 본체 층"):
		t.player().teleport_to(master.global_position + Vector3(0, 0, 4))
		master._intro_sent = false
		signals.clear()
		t.main._skip_cinematics = false
		var opened := await t.wait_until(func() -> bool: return cutin.visible, 1.0)
		t.check(opened and cutin._kind == "boss" and String(cutin._boss.get("title", "")) == "장산범" and t.tree.paused and signals.size() == 1, "장산범 본체 조우 → 장산범 원화·세계 정지·신호 1")
		cutin.dismiss()
		await t.frames(3)
		t.check(not cutin.visible and not t.tree.paused and master._intro_sent and signals.size() == 1, "장산범 본체 컷인 종료 → 재조우 정지 0")
	t.main._skip_cinematics = true
