extends Node
## #672 capture only: actual status triggers, normal native clocks, isolated save context.
const E2E_TOOLS := preload("res://tests/e2e/e2e.gd")
const RUNNER := preload("res://tests/e2e/e2e_runner.gd")
const AREA_TITLE := preload("res://ui/area_title.gd")
const TALISMAN := preload("res://actors/talisman_shot.gd")
const PROJECTILE := preload("res://actors/projectile.gd")
const FRAMES := 360
const START := 30
const HP := 100000.0
var phase := "before"
var status_events := []
var collecting_status := false
var tracked := {}
var ordinal := 0
var frame_no := -1
var tick_events := []
var current_label := ""
var player_ref: Node
var enemy_refs := []

func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--phase="):
			phase = arg.trim_prefix("--phase=")
	call_deferred("_capture")

func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame

func _mark(label: String, edge: String) -> void:
	print("CAPTURE %s %s %d" % [label, edge, Engine.get_process_frames()])

func _free_len(level: Node, from: Vector3, dir: Vector3, cap: float) -> float:
	var d := 0.0
	while d < cap:
		if not level.is_cell_walkable(Level.world_to_cell(from + dir * (d + 0.1))):
			return d
		d += 0.1
	return cap

func _open_spot(level: Node) -> Dictionary:
	var best := {}
	for r in level.map.rooms:
		var rr := r as Rect2i
		var center: Vector3 = Level.cell_to_world(rr.position + rr.size / 2)
		if not level.is_cell_walkable(Level.world_to_cell(center)):
			continue
		var free := 99.0
		for i in 16:
			var angle := TAU * float(i) / 16.0
			free = minf(free, _free_len(level, center, Vector3(cos(angle), 0.0, sin(angle)), 5.0))
		if free >= 4.0 and (best.is_empty() or free > float(best.free)):
			best = {"center": center, "free": free}
	return best

func _shot_exit(id: int) -> void:
	if not tracked.has(id):
		return
	var rec: Dictionary = tracked[id]
	var n: Node = rec.ref.get_ref()
	if not is_instance_valid(n):
		return
	rec.final_rng = str(n._rng.state)
	rec.exit_frame = frame_no
	rec.exit_position = str(n.global_position)
	if rec.kind == "talisman":
		rec.ended = n.ended
		rec.hits = n.hits

func _observe_shots(level: Node) -> void:
	for n in level.find_children("*", "Area3D", true, false):
		var script = n.get_script()
		if script != TALISMAN and script != PROJECTILE:
			continue
		var id: int = n.get_instance_id()
		if not tracked.has(id):
			var shot_seed := 632 + ordinal
			n._rng.seed = shot_seed
			var rec := {"ordinal": ordinal, "kind": "talisman" if script == TALISMAN else "enemy", "seed": shot_seed, "initial_rng": str(n._rng.state), "born_frame": frame_no, "born_engine_frame": Engine.get_process_frames(), "initial_velocity": str(n.velocity), "initial_speed": n.velocity.length(), "frames": [], "ref": weakref(n)}
			if script == TALISMAN:
				rec.merge({"item": n.def.id, "element": String(n.def.talisman_element), "mult": n.mult, "look_scale": n.look_scale, "radius": n.burst_radius(), "mods": n.mods.duplicate(true), "base_speed": n.def.throw_speed, "base_range": n.def.throw_range, "base_dot_sec": n.def.dot_sec, "base_status_sec": n.def.status_sec})
			else:
				rec.merge({"element": String(n.element), "look": String(n.look), "dmg_min": n.dmg_min, "dmg_max": n.dmg_max, "share": n.share, "accuracy": n.accuracy, "native_lifetime": n.lifetime})
			tracked[id] = rec
			n.tree_exiting.connect(_shot_exit.bind(id), CONNECT_ONE_SHOT)
			ordinal += 1
		tracked[id].frames.append({"frame": frame_no, "position": str(n.global_position), "velocity": str(n.velocity), "rng": str(n._rng.state)})


var damage_events := []
var input_edges := []
const STATUS_KEYS := ["chill_left", "frozen_left", "freeze_guard_left", "burn_dps", "burn_left", "ticks", "_burn_acc", "_burn_carry", "sal_dps", "sal_left", "sal_ticks", "sal_damage", "_sal_acc", "_sal_carry", "curse_left", "curse_pct", "salpuri_left"]

func _f64(v: float) -> String:
	return PackedFloat64Array([v]).to_byte_array().hex_encode()

func _status(n: Node) -> Dictionary:
	var c: Node = n.combat if n == player_ref else n
	var st = c._status
	var out := {"mask": c.status_mask(), "kind": st.kind, "can_freeze": st.can_freeze}
	for key in STATUS_KEYS:
		var v = st.get(key)
		out[key] = v
		if v is float:
			out[key + "_f64"] = _f64(v)
	return out

func _animation(n: Node) -> Dictionary:
	var visual: Node = n._visual
	var anim: AnimationPlayer = visual._anim
	return {"clip": String(anim.current_animation) if anim != null else "", "position": anim.current_animation_position if anim != null else 0.0, "speed": anim.speed_scale if anim != null else 0.0, "playing": anim.is_playing() if anim != null else false, "swing_busy": visual.swing_busy(), "anim_frozen": visual.is_anim_frozen()}

func _tick(actor: Node, amount: int, element: StringName) -> void:
	tick_events.append({"frame": frame_no, "actor": -1 if actor == player_ref else enemy_refs.find(actor), "amount": amount, "element": String(element)})

func _damage(source: Node, target: Node, amount: int) -> void:
	damage_events.append({"frame": frame_no, "source": -1 if source == player_ref else enemy_refs.find(source), "target": -1 if target == player_ref else enemy_refs.find(target), "amount": amount})

func _left(t: RefCounted, pos: Vector2, down: bool) -> void:
	Input.parse_input_event(t.mouse_event(InputEventMouseMotion.new(), pos))
	var ev := t.mouse_event(InputEventMouseButton.new(), pos) as InputEventMouseButton
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = down
	Input.parse_input_event(ev)
	input_edges.append({"frame": frame_no, "kind": "native_left", "down": down, "screen": str(pos)})

func _key(t: RefCounted, code: Key, down: bool) -> void:
	t._key_state(code, down)
	input_edges.append({"frame": frame_no, "kind": "native_key", "key": int(code), "down": down})

func _isolated_reset(main: Node) -> void:
	# Equivalent existing E2E reset except its shared save_e2e filename is NEVER used.
	for n in get_tree().get_nodes_in_group("panel_ui"):
		if n.visible and n.closable_by_esc:
			n.set_open(false)
	EventTrigger.armed = false
	EnemyDeath.reset_memory()
	GameState.run_seed = 20260916
	GameState.rng.seed = 20260916
	main.start_game(false)
	GameState.run_seed = 20260916
	GameState.rng.seed = 20260916

func _status_event(actor: Node, mask: int) -> void:
	if not collecting_status or (actor != player_ref and not enemy_refs.has(actor)):
		return
	status_events.append({"frame": frame_no, "engine_frame": Engine.get_process_frames(), "physics_frame": Engine.get_physics_frames(), "game_clock": GameClock.now, "game_clock_f64": _f64(GameClock.now), "actor": -1 if actor == player_ref else enemy_refs.find(actor), "mask": mask, "state_at_event": _status(actor)})

func _capture() -> void:
	SaveSystem.use_save_context("user://video672_capture.json")
	var main: Node = load("res://world/main.tscn").instantiate()
	get_tree().root.add_child(main)
	get_tree().current_scene = main
	await _frames(2)
	var gate := RUNNER.InputGate.new()
	get_tree().root.add_child(gate)
	gate.set_active(true)
	AREA_TITLE.enabled = false
	_isolated_reset(main)
	var t := E2E_TOOLS.new(get_tree(), main, "video672", false)
	t.check(SaveSystem.save_path == "user://video672_capture.json" and SaveSystem.active_profile_id.is_empty(), "save context isolated before Main and reset")
	await t.go_down(1)
	await t.remove_enemies()
	await _frames(12)
	var p: Node3D = t.player()
	player_ref = p
	var c: Node = p.combat
	var effects: Node = get_tree().root.get_node("Vfx")
	var stage := _open_spot(t.level())
	if not t.check(not stage.is_empty(), "same clear five-unit flight stage"):
		get_tree().quit(1)
		return
	var center: Vector3 = stage.center
	var origin := center - Vector3.RIGHT * 1.75
	p.teleport_to(origin)
	t.camera().snap_to_target()
	t.camera().focus_on(center, 0.0)
	main.get_node("HUD").visible = false
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	EventBus.status_tick.connect(_tick)
	EventBus.damage_dealt.connect(_damage)
	EventBus.status_changed.connect(_status_event)
	print("FIXTURE672 " + JSON.stringify({"fps": 60, "speed": 1.0, "area": GameState.area_id, "floor": GameState.floor_no, "center": str(center), "origin": str(origin), "target_origin": str(origin + Vector3.RIGHT * 5.0), "distance": 5.0, "camera_rotation": str(t.camera().rotation_degrees), "camera_size": t.camera().size, "player_model": p.visual().model.resource_path, "game_seed": 20260916, "combat_seed": 632, "enemy_seed": 672, "independent_projectile_seed_base": 632, "frames_per_segment": FRAMES, "save_context": SaveSystem.save_path, "active_profile": SaveSystem.active_profile_id, "note": "actual belt throw/enemy AI shot; SPI150/areaLv16 high; single stationary target; native status expiry; no forced damage; intended AFTER speed and travel timing differences"}))
	for label in ["fire", "cold", "lightning", "sal"]:
		current_label = label
		for n in get_tree().get_nodes_in_group("enemy"):
			n.queue_free()
		for n in t.level().find_children("*", "Area3D", true, false):
			if n.get_script() == TALISMAN or n.get_script() == PROJECTILE:
				n.queue_free()
		await _frames(4)
		c.reset_session()
		p.stop_moving()
		p.teleport_to(origin)
		p.face_toward(origin + Vector3.RIGHT)
		c.clear_status()
		GameState.character.level = 30
		GameState.character.spi = 150.0
		var inv: Inventory = GameState.inventory
		var sword := ItemInstance.create(ItemDb.get_def("iron_sword"))
		inv.equip("weapon", sword)
		c.recompute_stats()
		c.hp = c.max_hp
		c.mp = c.max_mp
		c.talisman_cd = 0.0
		var item := "talisman_fire" if label == "fire" else ("talisman_ice" if label == "cold" else ("talisman_thunder" if label == "lightning" else ""))
		inv.belt_take(1)
		if item != "":
			inv.belt_put(1, ItemInstance.create(ItemDb.get_def(item), 5))
		enemy_refs.clear()
		var area_level := 16 if label == "sal" else 1
		var def := E2E_TOOLS.enemy_def("nachalnyeo" if label == "sal" else "bandit").duplicate() as EnemyDef
		def.move_speed = 0.0
		if label != "sal":
			def.attack_range = 0.0
			def.aggro_range = 0.0
			def.keep_distance_min = 0.0
			def.keep_distance_max = 0.0
		var e: Enemy = await t.spawn_enemy(def, origin + Vector3.RIGHT * 5.0, area_level, {"hp": HP, "frames": 0})
		e.seed_rng(672)
		if label == "sal":
			e.set_physics_process(false)
			for hook in e.hooks:
				if hook.get_script().resource_path.ends_with("pull.gd"):
					hook._awake = true
					hook._t = -99.0
		enemy_refs.append(e)
		await _frames(60)
		var attack_screen: Vector2 = t.screen_of(e.global_position + Vector3(0.0, 0.94, 0.0))
		await t.mouse_move(attack_screen)
		await _frames(4)
		t.check(p.pick_at(attack_screen) == e, label + " exact real single target aim")
		tracked.clear()
		ordinal = 0
		tick_events.clear()
		damage_events.clear()
		input_edges.clear()
		status_events.clear()
		seed(672)
		GameState.rng.seed = 20260916
		effects._rng.seed = 672
		c._rng.seed = 632
		e.seed_rng(672)
		var report := {"segment": label, "frames": FRAMES, "trigger": "actual_nachalnyeo_one_orb" if label == "sal" else "actual_belt_throw", "end_mechanism": "natural_duration", "stats": c.stats.duplicate(true), "weapon": sword.to_dict(), "item": item, "stack_before": inv.belt[1].stack if inv.belt[1] != null else 0, "mp_before": c.mp, "hp_before": c.hp, "enemy_hp_before": e.hp, "enemy_def": def.id, "area_level": area_level, "enemy_damage": str(e.attack_damage()), "enemy_damage_mult": e._dmg_k(), "enemy_projectile_base_speed": def.projectile_speed, "attack_screen": str(attack_screen), "actor_origin": str(origin), "target_origin": str(e.global_position), "player_rng_before": str(c._rng.state), "enemy_rng_before": str(e._rng.state), "state_rng_before": str(GameState.rng.state), "hit_events": [], "actor_frames": [], "camera_frames": [], "target_frames": [], "player_status_frames": [], "enemy_status_frames": [], "animation_frames": [], "combat_frames": [], "clock_frames": [], "talisman_cd_frames": [], "time_scale_frames": [], "rng_frames": []}
		var hp_last := [c.hp, e.hp]
		var stopped_repeat := false
		collecting_status = true
		_mark(label, "BEGIN")
		for frame in FRAMES:
			frame_no = frame
			if frame == START:
				if label == "sal":
					e._cooldown = 0.0
					e.set_physics_process(true)
					input_edges.append({"frame": frame, "kind": "fixture_release_native_enemy_ai"})
				else:
					_key(t, KEY_2, true)
			if frame == START + 2 and label != "sal":
				_key(t, KEY_2, false)
			_observe_shots(t.level())
			if label == "sal" and not tracked.is_empty() and not stopped_repeat:
				e._cooldown = 999.0
				stopped_repeat = true
				input_edges.append({"frame": frame, "kind": "fixture_stop_repeat_after_actual_one_shot"})
			report.actor_frames.append(str(p.global_position))
			report.camera_frames.append(str(t.camera().global_position))
			report.target_frames.append(str(e.global_position))
			report.player_status_frames.append(_status(p))
			report.enemy_status_frames.append(_status(e))
			report.animation_frames.append({"player": _animation(p), "enemy": _animation(e)})
			report.combat_frames.append({"attack_timer": c._attack_timer, "target": 0 if c.target == e else -1, "pending": p.pending_command(), "enemy_state": e.state, "enemy_cooldown": e._cooldown})
			report.clock_frames.append({"process": Engine.get_process_frames(), "physics": Engine.get_physics_frames(), "game_clock": GameClock.now, "game_clock_f64": _f64(GameClock.now)})
			report.talisman_cd_frames.append(c.talisman_cd)
			report.time_scale_frames.append(Engine.time_scale)
			report.rng_frames.append({"player": str(c._rng.state), "enemy": str(e._rng.state), "state": str(GameState.rng.state)})
			var hp_now := [c.hp, e.hp]
			for i in 2:
				if hp_now[i] < hp_last[i]:
					report.hit_events.append({"frame": frame, "actor": i - 1, "damage": hp_last[i] - hp_now[i]})
			hp_last = hp_now
			await _frames(1)
		_mark(label, "END")
		collecting_status = false
		report.player_rng_after = str(c._rng.state)
		report.enemy_rng_after = str(e._rng.state)
		report.state_rng_after = str(GameState.rng.state)
		report.mp_after = c.mp
		report.hp_after = c.hp
		report.enemy_hp_after = e.hp
		report.stack_after = inv.belt[1].stack if inv.belt[1] != null else 0
		report.stats_after = c.stats.duplicate(true)
		report.status_ticks = tick_events.duplicate(true)
		report.status_events = status_events.duplicate(true)
		report.damage_events = damage_events.duplicate(true)
		report.input_edges = input_edges.duplicate(true)
		report.shots = []
		for rec in tracked.values():
			var plain: Dictionary = rec.duplicate(true)
			plain.erase("ref")
			report.shots.append(plain)
		t.check(report.hit_events.size() > 0, label + " actual damage")
		t.check(c.mp == float(report.mp_before), label + " MP unchanged")
		t.check(report.shots.size() == 1, label + " exactly one actual projectile")
		t.check(report.stack_after == (0 if label == "sal" else 4), label + " actual belt debit")
		t.check(report.actor_frames.all(func(pos) -> bool: return pos == str(origin)) and report.target_frames.all(func(pos) -> bool: return pos == str(origin + Vector3.RIGHT * 5.0)), label + " stationary same five-unit actors")
		var first_hit: int = report.hit_events[0].frame if not report.hit_events.is_empty() else -1
		t.check(report.shots.size() == 1 and report.shots[0].seed == 632 and int(report.shots[0].born_frame) < first_hit, label + " private RNG fixed before actual first hit")
		var states: Array = report.player_status_frames if label == "sal" else report.enemy_status_frames
		var bit := 4 if label == "fire" else (2 if label == "cold" else (16 if label == "sal" else 0))
		if bit > 0:
			t.check(states.any(func(row) -> bool: return bool(int(row.mask) & bit)), label + " actual status active")
			t.check(not (int(states[-1].mask) & bit), label + " complete natural status expiry in six seconds")
		if label != "sal":
			t.check(report.shots.size() == 1 and report.shots[0].hits == 1, label + " current AOE/single one target hit")
			t.check(report.shots.size() == 1 and report.shots[0].mult == 2.5, label + " normal SPI150 strength")
		else:
			t.check(c.hp > 0.0 and not c.is_salpuri(), "actual enemy sal survives; no cure or forced status")
		t.check(SaveSystem.save_path == "user://video672_capture.json" and SaveSystem.active_profile_id.is_empty(), label + " save context remained isolated")
		print("COMBAT672 " + JSON.stringify(report))
		await _frames(60)
	EventBus.status_tick.disconnect(_tick)
	EventBus.damage_dealt.disconnect(_damage)
	EventBus.status_changed.disconnect(_status_event)
	print("VIDEO672 phase=%s checks=%d fails=%d %s" % [phase, t.checks, t.fails.size(), "PASS" if t.fails.is_empty() else "FAIL"])
	get_tree().quit(0 if t.fails.is_empty() else 1)