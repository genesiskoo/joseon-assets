extends SceneTree
## #536 실제 PlayerCombat·흑랑 층 파수 둘·P2 박쥐 둘의 private RNG 재생/분리/정리 검사.
## godot --headless -s tests/test_balance_rng.gd
## 실제 DUNGEON_LEVEL의 생성 루프/ready를 사용하고, 단위 검산 동안만 각 몸의 physics를 끈다.

const FIXTURE := preload("res://tests/fixtures/balance_combat_rng.gd")
const BASE := 20260916

var _n := 0
var _fails: Array[String] = []
var _dungeon_script: Script
var _bus: Node
var _player: Node3D
var _boss: Node3D
var _guards: Array[Node] = []
var _summons: Array[Node] = []
var _first_draws: Array[float] = []
var _original: Dictionary = {}


class PrepKeyProbe extends Node:
	var events: Array[Dictionary] = []
	func _input(event: InputEvent) -> void:
		if event is InputEventKey and event.physical_keycode in [KEY_F11, KEY_F12, KEY_BRACKETRIGHT, KEY_V]:
			events.append({"key": event.physical_keycode, "pressed": event.pressed, "tick": Engine.get_physics_frames()})


func _check(cond: bool, msg: String) -> void:
	_n += 1
	if not cond:
		push_error("FAIL: " + msg)
		_fails.append(msg)


func _rng(actor: Node) -> RandomNumberGenerator:
	return actor.get("_rng") as RandomNumberGenerator


func _fresh(seed: int) -> RandomNumberGenerator:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	return rng


func _init() -> void:
	await process_frame
	await physics_frame
	_dungeon_script = load("res://world/dungeon_level.gd")
	_bus = root.get_node("EventBus")
	var scenario_script: GDScript = load("res://tests/e2e/scenarios/balance_boss.gd")
	var sure0 := DamageCalc.sure_hit
	DamageCalc.sure_hit = false
	_seed_formula()
	_player = (load("res://actors/player.tscn") as PackedScene).instantiate()
	root.add_child(_player)
	_player.process_mode = Node.PROCESS_MODE_DISABLED
	_player.global_position = Vector3.ZERO
	var combat: Node = _player.get_node("Combat")
	_rng(combat).seed = 7001
	_rng(combat).randf()
	_original[combat] = [_rng(combat).seed, _rng(combat).state]
	var notes: Array[String] = []
	# 앞 관찰자는 ready.randomize가 끝난 원 상태만 기억하고 소비하지 않는다.
	node_added.connect(_before_seed_added)
	var replay := FIXTURE.new()
	root.add_child(replay)
	replay.begin(combat, BASE, 3, 1, AreaDb.DEFAULT_DUNGEON, _boss_floor(), func(line: String) -> void: notes.append(line))
	_check(replay.actor_count() == 1 and replay.is_active() and _rng(combat).seed == 23271941,
		"go_down 전 영속 도호 고정과 관찰 설치")
	# 뒤 관찰자는 ready 직후 첫 굴림을 바로 써도 이미 고정된 상태여야 한다.
	node_added.connect(_after_seed_added)
	var stage := _spawn_level()
	_check(_guards.size() == 2 and replay.guard_count() == 2 and replay.actor_count() == 4,
		"실제 흑랑 층 생성으로 기존 파수 둘·흑랑을 모두 포착")
	_check(_rng(_boss).seed == 23272950, "기존 흑랑 역할 시드는 그대로")
	for i in _guards.size():
		_check((_guards[i] as Node3D).global_position == stage.map.cell_to_world(stage.map.guard_cells[i]),
			"파수 %d는 preset 생성 루프의 guard_cells 순서와 실제 칸 일치" % (i + 1))
	_boss.call("_enter_phase2")
	node_added.disconnect(_before_seed_added)
	node_added.disconnect(_after_seed_added)
	_check(_summons.size() == 2 and replay.spawn_count() == 2 and replay.actor_count() == 6,
		"진짜 흑랑 P2 박쥐 둘 포함 여섯 실전 몸")
	_check(_first_draws.size() == 4, "기존 파수·P2 박쥐 네 몸 첫 소비 관측")
	var initial_all := _initial_rows(replay.snapshot())
	_check(notes.size() == 6 and notes[0].contains("seed=23271941 initial=") and notes[2].contains("guard_bat2") and notes[5].contains("summon_bat2"),
		"여섯 스트림 seed·초기 state 로그")
	var observed_before := replay.snapshot()
	replay.observe_guard("unit_read_only")
	_check(replay.snapshot() == observed_before, "파수 진단 관찰은 여섯 RNG 상태를 읽기만 함")
	_stream_isolation(replay, combat)
	replay.rewind()
	var all_bats: Array[Node] = _guards + _summons
	var first := _combat_trace(combat, _boss, all_bats)
	var first_end := replay.snapshot()
	var consumed_pc := _rng(combat).state
	combat.call("reset_session")
	_check(_rng(combat).state == consumed_pc, "게임 reset_session은 private RNG를 되돌리지 않음 — fixture 경계")
	replay.rewind()
	var second := _combat_trace(combat, _boss, all_bats)
	_check(first == second and first_end == replay.snapshot(), "실제 명중·피해·치명과 여섯 몸 종료 state 정확 재생")
	_check(first.hits > 0 and first.hits < first.attacks and not DamageCalc.sure_hit, "실제 받은 공격에 명중·빗나감 모두 있음 · sure_hit 끔")
	_check(first.out_hits > 0 and first.out_hits < 12, "진짜 도호 _land도 명중률 그대로 맞거나 빗나감")
	var final_rows: Array[Dictionary] = replay.finish()
	_check(final_rows == first_end and notes.filter(func(line: String) -> bool: return line.contains("흑랑 RNG")).size() == 12 and notes.back().contains(" final="), "여섯 종료 state 기록")
	var restored := true
	for actor in _original:
		restored = restored and _rng(actor).seed == _original[actor][0] and _rng(actor).state == _original[actor][1]
	_check(restored and _original.size() == 6, "영속 도호·흑랑·파수·소환 모두 원 seed/state 복원")
	_check(not replay.is_active() and not node_added.is_connected(Callable(replay, "_on_node_added")) and not _bus.level_loaded.is_connected(Callable(replay, "_on_level_loaded")),
		"판 끝 node_added·level_loaded 관찰 연결 해제")
	var after: Node = (load("res://actors/enemy.tscn") as PackedScene).instantiate()
	after.set("def", load("res://data/enemies/bat.tres"))
	after.call("seed_rng", 88001)
	stage.get("_enemies").add_child(after)
	after.process_mode = Node.PROCESS_MODE_DISABLED
	_check(_rng(after).seed == 88001 and replay.spawn_count() == 2, "판 끝 뒤 실제 후속 몸 독립 seed를 덮어쓰지 않음")
	replay.free()
	stage.free()
	_original.clear()
	# restart처럼 새 층/새 파수/새 흑랑/P2를 세워도 ObjectID·ready.randomize와 무관하다.
	replay = FIXTURE.new()
	root.add_child(replay)
	replay.begin(combat, BASE, 3, 1, AreaDb.DEFAULT_DUNGEON, _boss_floor())
	stage = _spawn_level()
	_boss = _level_boss(stage)
	_boss.call("_enter_phase2")
	_check(_initial_rows(replay.snapshot()) == initial_all, "restart의 새 층·여섯 실제 몸도 동일 초기 스트림")
	replay.finish()
	replay.free()
	stage.free()
	# 대상 층 중간 삭제는 Main에 남은 fixture까지 정리한다.
	var original := [_rng(combat).seed, _rng(combat).state]
	var connections0 := node_added.get_connections().size()
	var loaded0: int = _bus.level_loaded.get_connections().size()
	replay = FIXTURE.new()
	root.add_child(replay)
	replay.begin(combat, BASE, 5, 2, AreaDb.DEFAULT_DUNGEON, _boss_floor())
	stage = _spawn_level()
	_rng(combat).randf()
	_check(replay.guard_count() == 2 and node_added.get_connections().size() == connections0 + 1, "입장한 판 관찰 연결과 파수 둘")
	stage.free()
	_check(_rng(combat).seed == original[0] and _rng(combat).state == original[1] and node_added.get_connections().size() == connections0 and _bus.level_loaded.get_connections().size() == loaded0,
		"중간 대상 층 종료는 도호 복원·모든 관찰 연결 해제")
	replay.free()
	# 입장 전 조기 return은 실제 대본의 정리 메서드를 거친다.
	replay = FIXTURE.new()
	root.add_child(replay)
	replay.begin(combat, BASE, 3, 2, AreaDb.DEFAULT_DUNGEON, _boss_floor())
	_rng(combat).randf()
	var scenario: RefCounted = scenario_script.new()
	scenario.set("_replay", replay)
	scenario.call("_dispose_replay")
	_check(not replay.is_active() and _rng(combat).state == original[1] and node_added.get_connections().size() == connections0 and _bus.level_loaded.get_connections().size() == loaded0,
		"go_down 전 준비 실패/return 정리는 도호 state와 관찰 연결 복원")
	scenario = null
	await process_frame
	# 끊긴 대본이 직접 return하지 못해도 다음 대본의 실제 마을 level_loaded에서 정리한다.
	replay = FIXTURE.new()
	root.add_child(replay)
	replay.begin(combat, BASE, 3, 3, AreaDb.DEFAULT_DUNGEON, _boss_floor())
	_rng(combat).randf()
	var town := (load("res://world/town.tscn") as PackedScene).instantiate()
	_bus.level_loaded.emit(town)
	_check(not replay.is_active() and _rng(combat).seed == original[0] and _rng(combat).state == original[1] and node_added.get_connections().size() == connections0 and _bus.level_loaded.get_connections().size() == loaded0,
		"대상 층 전 중단도 다음 마을 리셋에 RNG/연결 누출 없음")
	town.free()
	replay.free()
	# 대본 객체 소멸도 중간 fixture를 정리한다.
	replay = FIXTURE.new()
	root.add_child(replay)
	replay.begin(combat, BASE, 5, 1, AreaDb.DEFAULT_DUNGEON, _boss_floor())
	_rng(combat).randf()
	scenario = scenario_script.new()
	scenario.set("_replay", replay)
	scenario = null
	_check(not replay.is_active() and _rng(combat).state == original[1] and node_added.get_connections().size() == connections0 and _bus.level_loaded.get_connections().size() == loaded0,
		"대본 PREDELETE도 입장 전 fixture 정리")
	await process_frame
	var probe := PrepKeyProbe.new()
	root.add_child(probe)
	var tools: RefCounted = (load("res://tests/e2e/e2e.gd") as GDScript).new(self, root, "balance_rng_unit", false)
	scenario = scenario_script.new()
	scenario.call("setup", tools)
	await scenario.call("_prepare_key", KEY_F12, 6)
	await scenario.call("_prepare_key", KEY_F11, 5)
	_check(tools.get("checks") == 2 and tools.get("fails").is_empty(), "로컬 준비 입력은 사전 고정6/5 physics ticks 정확히 대기")
	_check(probe.events.size() == 4 and probe.events[0].pressed and not probe.events[1].pressed and probe.events[1].tick - probe.events[0].tick == 1 and probe.events[2].pressed and not probe.events[3].pressed and probe.events[3].tick - probe.events[2].tick == 1, "실제 InputEventKey press/release 경로와1틱 홀드 유지")
	var combat_tick0 := Engine.get_physics_frames()
	tools.call("_key_state", KEY_F12, true)
	# 단위 probe는 누적 입력을 지금 전달해 이벤트의 실제 tick을 기록한다.
	Input.flush_buffered_events()
	await scenario.call("_combat_ticks")
	tools.call("_key_state", KEY_F12, false)
	Input.flush_buffered_events()
	_check(Engine.get_physics_frames() - combat_tick0 == 6, "로컬 전투 대기는 준비 끝 물리 경계에서 정확히6틱")
	print("BALANCE_RNG_INPUT_PROBE ", probe.events)
	_check(probe.events.size() == 6 and probe.events[4].pressed and not probe.events[5].pressed and probe.events[5].tick - probe.events[4].tick == 6,
		"실제 전투 입력 probe의 두 이벤트 간격6틱 — process_frame 대기 아님")
	scenario = null
	probe.free()
	_player.free()
	await _prepare_level_ticks(scenario_script)
	DamageCalc.sure_hit = sure0
	await create_timer(1.2).timeout
	print("BALANCE_RNG_TEST checks=%d fails=%d %s" % [_n, _fails.size(), "PASS" if _fails.is_empty() else "FAIL"])
	quit(1 if not _fails.is_empty() else 0)


func _seed_formula() -> void:
	_check(FIXTURE.seed_for(BASE, 3, 1, FIXTURE.PLAYER) == 23271941 and FIXTURE.seed_for(BASE, 5, 3, FIXTURE.BOSS) == 25292970,
		"첫 실행 전 승인한 base·정수식·기존 role1~3 유지")
	_check(FIXTURE.seed_for(BASE, 3, 1, FIXTURE.GUARD_BAT, 1) == 23275069 and FIXTURE.seed_for(BASE, 3, 1, FIXTURE.GUARD_BAT, 2) == 23275170,
		"실전 누락 보완 guard role4·ordinal1/2 golden 시드")
	var seeds: Dictionary = {}
	for level in [3, 5]:
		for attempt in range(1, 4):
			for role in [FIXTURE.PLAYER, FIXTURE.BOSS, FIXTURE.SUMMON_BAT, FIXTURE.GUARD_BAT]:
				for ordinal in ([1, 2] if role in [FIXTURE.SUMMON_BAT, FIXTURE.GUARD_BAT] else [0]):
					seeds[FIXTURE.seed_for(BASE, level, attempt, role, ordinal)] = true
	_check(seeds.size() == 36, "Lv3/Lv5 세 판·초기4몸/P2소환2몸 총36개 독립 seed")


func _boss_floor() -> int:
	return AreaDb.get_def(AreaDb.DEFAULT_DUNGEON).boss_floor


func _spawn_level() -> Node3D:
	var stage := (load("res://world/dungeon_level.tscn") as PackedScene).instantiate() as Node3D
	stage.configure(AreaDb.get_def(AreaDb.DEFAULT_DUNGEON), _boss_floor())
	root.add_child(stage)
	stage.process_mode = Node.PROCESS_MODE_DISABLED
	return stage


func _level_boss(stage: Node3D) -> Node3D:
	for actor in stage.get("_enemies").get_children():
		if actor.is_in_group("boss"):
			return actor as Node3D
	return null


func _is_target_enemy(node: Node) -> bool:
	if not node.has_method("seed_rng") or node.get_parent() == null:
		return false
	var stage := node.get_parent().get_parent()
	return stage != null and stage.get_script() == _dungeon_script and stage.area.id == AreaDb.DEFAULT_DUNGEON and stage.floor_no == _boss_floor()


func _before_seed_added(node: Node) -> void:
	if _is_target_enemy(node):
		node.ready.connect(func() -> void: _original[node] = [_rng(node).seed, _rng(node).state], CONNECT_ONE_SHOT)


func _after_seed_added(node: Node) -> void:
	if not _is_target_enemy(node):
		return
	node.process_mode = Node.PROCESS_MODE_DISABLED
	var def = node.get("def")
	if String(def.id) == "boss_heukrang":
		_boss = node as Node3D
		node.ready.connect(func() -> void:
			_check(_rng(node).seed == 23272950 and _rng(node).state == _fresh(23272950).state, "흑랑 첫 소비 전 fixed seed/state"), CONNECT_ONE_SHOT)
	elif String(def.id) == "bat":
		var summon := is_instance_valid(_boss) and bool(_boss.get("_phase2"))
		var role: int = FIXTURE.SUMMON_BAT if summon else FIXTURE.GUARD_BAT
		if summon:
			_summons.append(node)
		else:
			_guards.append(node)
		var ordinal := _summons.size() if summon else _guards.size()
		node.ready.connect(func() -> void:
			var seed := FIXTURE.seed_for(BASE, 3, 1, role, ordinal)
			_check(_rng(node).seed == seed and _rng(node).state == _fresh(seed).state, "%s %d ready 직후 첫 소비 전 seed/state" % ["소환" if summon else "파수", ordinal])
			var draw := _rng(node).randf()
			_check(draw == _fresh(seed).randf(), "%s %d 첫 굴림도 승인 스트림" % ["소환" if summon else "파수", ordinal])
			_first_draws.append(draw), CONNECT_ONE_SHOT)


func _initial_rows(rows: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for row in rows:
		out.append({"role": row.role, "ordinal": row.ordinal, "seed": row.seed, "initial": row.initial})
	return out


func _stream_isolation(replay: Node, combat: Node) -> void:
	replay.call("rewind")
	var before: Array[Dictionary] = replay.call("snapshot")
	for i in 20:
		_rng(combat).randf()
	var after: Array[Dictionary] = replay.call("snapshot")
	var others_same := before.size() == 6 and after.size() == 6
	for i in range(1, mini(before.size(), after.size())):
		others_same = others_same and before[i] == after[i]
	_check(others_same and before[0].final != after[0].final, "도호 소비가 흑랑·파수·소환 다섯 몸의 스트림을 움직이지 않음")
	replay.call("rewind")
	_check(replay.call("snapshot") == before, "rewind는 여섯 실제 몸의 초기 state 모두 복구")


func _combat_trace(combat: Node, boss: Node, bats: Array[Node]) -> Dictionary:
	combat.call("reset_session")
	combat.set("hp", combat.get("max_hp"))
	boss.set("hp", 5000.0)   # 단위 검산 중 드랍/레벨업을 막는 표적. 실제 e2e 수치는 그대로.
	var blows: Array = []
	var out_hits := 0
	for i in 12:
		combat.set("hp", combat.get("max_hp"))
		var dealt: int = combat.call("_land", boss, 1.0, false)
		out_hits += 1 if dealt > 0 else 0
		var got: int = combat.call("receive_attack", _rng(boss), 2.0, 6.0, 55.0, 1.0)
		var bat_blows: Array[int] = []
		for bat in bats:
			bat_blows.append(combat.call("receive_attack", _rng(bat), 1.0, 3.0, 55.0, 1.0))
		blows.append([dealt, bool(boss.get("last_hit_crit")), got, bat_blows])
	return {"blows": blows, "attacks": int(combat.get("attacks_received")), "hits": int(combat.get("hits_received")), "out_hits": out_hits}


## 실제 Main/DevKeys의 ]·V 이벤트를 사용한다. 층 이동/텔레포트 함수를 직접 부르지 않는다.
func _prepare_level_ticks(scenario_script: GDScript) -> void:
	var saves: Node = root.get_node("SaveSystem")
	var save_path0: String = saves.get("save_path")
	saves.set("save_path", "user://balance_rng_536_prep_test.json")
	saves.call("delete_save")
	var main: Node = (load("res://world/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	current_scene = main
	# -s에는 --e2e 인자가 없으므로 실제 러너와 같은 컷인 생략/새 판 계약을 적용한다.
	main.set("_skip_cinematics", true)
	var e2e_script: GDScript = load("res://tests/e2e/e2e.gd")
	e2e_script.reset_game(self, main)
	var tools: RefCounted = e2e_script.new(self, main, "balance_rng_main_unit", false)
	var scenario: RefCounted = scenario_script.new()
	scenario.call("setup", tools)
	var probe := PrepKeyProbe.new()
	root.add_child(probe)
	var loads: Array[Dictionary] = []
	var record_load := func(level: Node) -> void:
		if level.get_script() == _dungeon_script:
			loads.append({"floor": int(level.get("floor_no")), "tick": Engine.get_physics_frames()})
	_bus.level_loaded.connect(record_load)
	var replay := FIXTURE.new()
	main.add_child(replay)
	replay.begin(main.player.combat, BASE, 3, 1, AreaDb.DEFAULT_DUNGEON, _boss_floor())
	for i in _boss_floor():
		await scenario.call("_prepare_key", KEY_BRACKETRIGHT, 6)
	var presses: Array = probe.events.filter(func(event: Dictionary) -> bool: return event.key == KEY_BRACKETRIGHT and event.pressed)
	var same_tick := presses.size() == _boss_floor() and loads.size() == _boss_floor()
	for i in mini(presses.size(), loads.size()):
		same_tick = same_tick and presses[i].tick == loads[i].tick and loads[i].floor == i + 1
	_check(same_tick, "실제 ] InputEvent와 Main의 각 층 level_loaded는 같은 physics tick")
	_check(int(root.get_node("GameState").get("floor_no")) == _boss_floor() and replay.guard_count() == 2 and replay.actor_count() == 4,
		"실제 키 입장에서도 도호/흑랑/기존 파수 둘의 첫 소비 전 고정")
	var entered_pos: Vector3 = main.player.global_position
	await scenario.call("_prepare_key", KEY_V, 5)
	var v_events: Array = probe.events.filter(func(event: Dictionary) -> bool: return event.key == KEY_V)
	_check(v_events.size() == 2 and v_events[0].pressed and not v_events[1].pressed and v_events[1].tick - v_events[0].tick == 1 and Engine.get_physics_frames() - v_events[0].tick == 5 and main.player.global_position != entered_pos,
		"실제 V press/release는 같은 입력 경로와1/5틱으로 보스 접근")
	_check(tools.get("checks") == _boss_floor() + 1 and tools.get("fails").is_empty(), "실제 Main 준비 키 전체6/5틱 검사")
	print("BALANCE_RNG_LEVEL_TICKS loads=", loads, " events=", probe.events)
	replay.finish()
	replay.free()
	_bus.level_loaded.disconnect(record_load)
	scenario = null
	probe.free()
	main.queue_free()
	await process_frame
	saves.call("delete_save")
	saves.set("save_path", save_path0)
