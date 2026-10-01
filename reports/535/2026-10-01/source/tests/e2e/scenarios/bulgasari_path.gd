extends E2eScenario
## #535: 큰 불가살이가 화로 북면에 붙은 실제 실패 좌표에서 바닥 칼을 먹는다.
## 칼은 item_dropped(제자리 낙하)로 놓고, 화로 네 개·상자 충돌·몸·AI를 그대로 둔다.
## 화로는 douse() 정상 상태로 식힌다: 실제 실패도 이 화로를 먹고 식은 다음 먹기에서 막혔다.
## 기제의 6초/1.3 도착/5% 회복을 늘리거나 칼을 대본이 지우지 않는다.

const MINE := &"soeburi"
const START := Vector3(3.99967, 0.0, 13.09992)
const SWORD_AT := Vector3(6.826933, 0.0, 11.78921)
const PLAYER_AT := Vector3(14.5, 0.0, 11.5)
const BLOCK_CELL := Vector2i(4, 14)
const TICK_MARGIN := 1.0 / 30.0


func _boss(lvl: Node) -> Node:
	for b in t.tree.get_nodes_in_group("boss"):
		if lvl.is_ancestor_of(b):
			return b
	return null


func _flat(a: Vector3, b: Vector3) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()


func _floor_sword(item: ItemInstance) -> Node3D:
	for n in t.tree.get_nodes_in_group("floor_item"):
		if n.get("item") == item:
			return n as Node3D
	return null


func _brazier_box(lvl: Node) -> CollisionShape3D:
	var body := lvl.get_node_or_null("Geometry/BrazierBody") as StaticBody3D
	if body == null:
		return null
	for n in body.get_children():
		var col := n as CollisionShape3D
		if col and col.shape is BoxShape3D and Level.world_to_cell(col.global_position) == BLOCK_CELL:
			return col
	return null


func run() -> void:
	t.main.load_area(MINE, 3, Level.SpawnHint.FROM_ABOVE)
	var loaded: bool = await t.wait_until(func() -> bool:
		return GameState.area_id == MINE and GameState.floor_no == 3 and t.level() != null and _boss(t.level()) != null, 8.0)
	if not t.check(loaded, "쇠부리 폐광 3층 실제 불가살이"):
		return
	await t.frames(4)
	var lvl: Node = t.level()
	var boss: Node = _boss(lvl)
	var k: Dictionary = boss.get_script().get_script_constant_map()
	t.check(float(k.EAT_SEC) == 6.0 and float(k.EAT_ARRIVE) == 1.3 and float(k.EAT_HEAL) == 0.05,
		"먹기 원래 계약 = 6초 · 도착 1.3 · 회복 5%")
	var capsule := boss.get_node("Collision") as CollisionShape3D
	t.check(capsule.shape is CapsuleShape3D and is_equal_approx((capsule.shape as CapsuleShape3D).radius, 0.9) and not capsule.disabled,
		"실제 큰 몸 캡슐 반지름 0.9 · 충돌 켬")
	t.check(boss._visual.is_model_loaded() and boss.is_physics_processing(), "실제 불가살이 모델 · AI 물리 틱 켬")
	var box := _brazier_box(lvl)
	t.check(box != null and not box.disabled and (box.shape as BoxShape3D).size.x == 1.0 and (box.shape as BoxShape3D).size.z == 1.0
		and not lvl.is_cell_walkable(BLOCK_CELL), "실패 화로 (4,14) = 1×1 실제 상자 충돌 · 막는 칸")
	var braziers := lvl.get_node("Geometry/Braziers")
	t.check(braziers.get_child_count() == 4, "화로 넷 유지")
	for br in braziers.get_children():
		br.douse()
	# 보스 싸움 대본과 같은 셋업: 파수만 치운다.
	for e in t.tree.get_nodes_in_group("enemy"):
		if lvl.is_ancestor_of(e) and not e.is_in_group("boss"):
			e.queue_free()
	await t.frames(2)
	# 보스가 아직 입구의 도호를 못 본 상태에서 칼부터 실제로 착지시킨다.
	var sword := ItemInstance.create(ItemDb.get_def("long_sword"))
	EventBus.item_dropped.emit(sword, SWORD_AT)
	var settled: bool = await t.wait_until(func() -> bool:
		var fi := _floor_sword(sword)
		return fi != null and bool(fi.get("is_settled")), 2.0)
	var fi := _floor_sword(sword)
	if not t.check(settled and fi != null and _flat(fi.global_position, SWORD_AT) < 0.001,
		"실제 바닥 장검 착지 = 고정 실패 좌표 %s" % SWORD_AT):
		return
	boss.hp = boss.max_hp * 0.8
	var hp0: float = boss.hp
	var tries0: int = boss.eat_tries
	var ate0: int = boss.items_eaten
	t.player().teleport_to(PLAYER_AT)
	t.player().heal_full()
	t.camera().snap_to_target()
	boss.global_position = START
	boss.velocity = Vector3.ZERO
	boss.wake()
	t.check(not t.tree.paused and not t.main.story_cutin.visible and _flat(boss.global_position, START) < 0.001,
		"컷인·세계 정지 없음 · 시작 = 화로 북면 실패 좌표 %s" % START)
	var began: bool = await t.wait_until(func() -> bool: return boss.busy_kind() == &"eat_item", 1.0)
	if not t.check(began and boss._eat_target == fi, "실제 AI가 바닥 칼 먹기 BUSY에 진입"):
		return
	var started := t.game_time()
	var trace: Array[String] = []
	var next_sample := 0.0
	while int(boss.items_eaten) == ate0 and t.game_time() - started <= float(k.EAT_SEC) + TICK_MARGIN:
		var elapsed := t.game_time() - started
		if elapsed >= next_sample:
			trace.append("%.2f초 몸 %s · 칼 거리 %.3f · 붙듦 %s · 먹은 %d" % [elapsed,
				Vector2(boss.global_position.x, boss.global_position.z), _flat(boss.global_position, SWORD_AT), boss.busy_kind(), int(boss.items_eaten)])
			next_sample += 0.5
		if float(t.player().combat.hp) < float(t.player().combat.max_hp) * 0.4:
			t.player().heal_full()
		await t.tree.physics_frame
	var elapsed := t.game_time() - started
	var ate: bool = int(boss.items_eaten) == ate0 + 1
	for line in trace:
		t.note("화로 경로 %s" % line)
	t.note("먹기 끝 %.3f초 · 몸 %s · 칼 %s · 거리 %.3f · 시도 %d · 먹은 %d · HP %.1f → %.1f" % [elapsed,
		boss.global_position, fi.global_position if is_instance_valid(fi) else "없음", _flat(boss.global_position, SWORD_AT),
		int(boss.eat_tries) - tries0, int(boss.items_eaten) - ate0, hp0, float(boss.hp)])
	t.check(ate and elapsed <= float(k.EAT_SEC) + TICK_MARGIN and int(boss.eat_tries) == tries0 + 1,
		"첫 먹기 6초 안에 장검 하나를 먹음 · 재시도 없음")
	t.check(ate and _flat(boss.global_position, SWORD_AT) <= float(k.EAT_ARRIVE) + 0.01,
		"실제 큰 몸이 원래 먹기 도착 1.3 안에 닿음")
	await t.frames(2)
	t.check(ate and (not is_instance_valid(fi) or fi.is_queued_for_deletion()), "먹은 실제 바닥 칼이 사라짐")
	t.check(ate and absf(float(boss.hp) - hp0 - float(boss.max_hp) * float(k.EAT_HEAL)) < 0.5,
		"원래 생명 5%% 회복 (%.1f → %.1f)" % [hp0, float(boss.hp)])
	t.check(ate and boss.busy_kind() != &"eat_item" and boss.is_physics_processing(), "먹기 붙듦을 풀고 AI가 계속 돎")
	t.check(box != null and not box.disabled and not lvl.is_cell_walkable(BLOCK_CELL) and braziers.get_child_count() == 4,
		"먹은 뒤에도 실제 화로 상자 충돌 · 화로 넷 유지")
