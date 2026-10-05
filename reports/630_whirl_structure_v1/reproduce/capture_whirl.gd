extends Node
## #630 capture QA only: actual actor/combat, native time, fixed same fixture.
const E2E_TOOLS := preload("res://tests/e2e/e2e.gd")
const RUNNER := preload("res://tests/e2e/e2e_runner.gd")
const AREA_TITLE := preload("res://ui/area_title.gd")
const FRAMES := 240
const HOLD_START := 30
const HOLD_END := 180
const HP := 100000.0
var phase := "before"

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

func _button(t: E2e, point: Vector3, pressed: bool) -> void:
	# No awaited helper frames: one exact timeline; retain E2E pointer gate mark.
	var at: Vector2 = t.screen_of(point)
	var motion := t.mouse_event(InputEventMouseMotion.new(), at)
	Input.parse_input_event(motion)
	var ev := t.mouse_event(InputEventMouseButton.new(), at) as InputEventMouseButton
	ev.button_index = MOUSE_BUTTON_RIGHT
	ev.pressed = pressed
	Input.parse_input_event(ev)

func _skill_i(c: Node, id: String) -> int:
	for i in c.skills.size():
		if c.skills[i].id == id:
			return i
	return -1

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

func _stats(c: Node) -> Dictionary:
	var result := {}
	for key in ["str", "dex", "vit", "spi", "dmg_min", "dmg_max", "accuracy", "crit_chance", "attack_speed", "attack_range", "move_speed", "max_hp", "max_mp", "mp_regen"]:
		result[key] = c.stats.get(key, 0)
	return result

func _learn(t: E2e, c: Node, skill: String, level: int) -> void:
	var ch: Dictionary = GameState.character
	ch.skills = GameState.skill_tree.new_skills()
	ch.skill_points = 999
	ch.level = 30
	var whirl: int = _skill_i(c, "whirl")
	var storm: int = _skill_i(c, "blade_storm")
	var target: int = whirl if skill == "whirl" else storm
	var prerequisite_levels := level if skill == "whirl" else 1
	for i in prerequisite_levels:
		t.check(Progression.learn_skill(ch, c.skills[whirl]), "capture learn whirl %d" % (i + 1))
	if skill != "whirl":
		for i in level:
			t.check(Progression.learn_skill(ch, c.skills[storm]), "capture learn storm %d" % (i + 1))
	c.recompute_stats()
	c.active_skill = target
	t.check_eq(c.skill_level(target), level, "%s actual skill level" % skill)

func _capture() -> void:
	var main: Node = load("res://world/main.tscn").instantiate()
	get_tree().root.add_child(main)
	get_tree().current_scene = main
	await _frames(2)
	var gate := RUNNER.InputGate.new()
	get_tree().root.add_child(gate)
	gate.set_active(true)
	AREA_TITLE.enabled = false
	E2E_TOOLS.reset_game(get_tree(), main)
	var t := E2E_TOOLS.new(get_tree(), main, "video630", false)
	await t.go_down(1)
	await t.remove_enemies()
	await _frames(12)
	var p: Node3D = t.player()
	var c: Node = p.combat
	var effects: Node = get_tree().root.get_node("Vfx")
	var stage := _open_spot(t.level())
	if not t.check(not stage.is_empty(), "same clear stage radius >=4"):
		print("VIDEO630 phase=%s checks=%d fails=%d FAIL" % [phase, t.checks, t.fails.size()])
		get_tree().quit(1)
		return
	var origin: Vector3 = stage.center
	p.teleport_to(origin)
	t.camera().snap_to_target()
	t.camera().focus_on(origin, 0.0)
	main.get_node("HUD").visible = false
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	DamageCalc.sure_hit = true
	GameState.character.level = 30
	c.recompute_stats()
	c.stats.crit_chance = 0.0
	t.check(p.visual().weapon_node() != null, "actual equipped sword")
	var enemies: Array[Enemy] = []
	var positions: Array[Vector3] = []
	for radius in [1.7, 3.1]:
		for i in 4:
			var angle := TAU * float(i) / 4.0 + 0.25
			var pos := origin + Vector3(cos(angle), 0.0, sin(angle)) * float(radius)
			positions.append(pos)
			enemies.append(await t.spawn_enemy("bandit", pos, 1, {"hp": HP, "frozen": true}))
	await _frames(90)
	var fixture := {"fps": 60, "speed": 1.0, "area": GameState.area_id, "floor": GameState.floor_no, "stage": str(origin), "free_radius": stage.free, "camera_rotation": str(t.camera().rotation_degrees), "camera_size": t.camera().size, "weapon": String(p.visual().weapon_node().name), "player_model": p.visual().model.resource_path, "hp": HP, "target_positions": positions.map(func(v: Vector3) -> String: return str(v)), "rng_seed": 630, "game_state_seed": 20260916, "character_level": 30, "base_stats": _stats(c), "setup": "same frozen high-HP target rings; crit_chance0/sure_hit; no balance modifications"}
	print("FIXTURE630 " + JSON.stringify(fixture))
	for skill in ["whirl", "blade_storm"]:
		for level in [1, 5, 10]:
			_learn(t, c, skill, level)
			c.end_storm()
			c.clear_target()
			p.stop_moving()
			p.teleport_to(origin)
			p.face_toward(origin + Vector3.RIGHT)
			c._attack_timer = 0.0
			c.stats.crit_chance = 0.0
			c.mp = c.max_mp
			c.cooldowns.fill(0.0)
			for i in enemies.size():
				enemies[i].hp = HP
				enemies[i].global_position = positions[i]
			await _frames(60)
			seed(630)
			GameState.rng.seed = 20260916
			effects._rng.seed = 630
			c._rng.seed = 630
			var label := ("whirl" if skill == "whirl" else "storm") + str(level)
			var rng_before := str(c._rng.state)
			var state_rng_before := str(GameState.rng.state)
			var mp_before: float = c.mp
			var seq: int = effects.seq
			var hp_last: Array[float] = []
			for e in enemies:
				hp_last.append(e.hp)
			var hit_events := []
			var drawing_frames := 0
			var camera_frames := []
			var actor_frames := []
			var mp_debit := 0.0
			var storm_frames := 0
			var stats := _stats(c)
			_mark(label, "BEGIN")
			for frame in FRAMES:
				if frame == HOLD_START:
					if skill == "whirl":
						var mp0: float = c.mp
						c.cast_active(origin + Vector3.RIGHT * 2.0)
						mp_debit += mp0 - c.mp
					else:
						_button(t, origin, true)
				if frame == HOLD_END and skill != "whirl":
					_button(t, origin, false)
				if p.visual().trail_drawing():
					drawing_frames += 1
				if c.storming():
					storm_frames += 1
				camera_frames.append(str(t.camera().global_position))
				actor_frames.append(str(p.global_position))
				for i in enemies.size():
					if enemies[i].hp < hp_last[i]:
						hit_events.append({"frame": frame, "enemy": i, "damage": hp_last[i] - enemies[i].hp})
						hp_last[i] = enemies[i].hp
				await _frames(1)
			_mark(label, "END")
			var damage := 0.0
			var targets_hit := 0
			for e in enemies:
				damage += HP - e.hp
				if e.hp < HP:
					targets_hit += 1
			if skill != "whirl":
				mp_debit = c.storm_mp_used
			t.check(not c.storming(), label + " ended by release")
			t.check(drawing_frames > 10, label + " live blade ribbon")
			t.check(hit_events.size() >= 4, label + " actual hit events")
			t.check(mp_debit > 0.0, label + " actual MP debit")
			t.check(p.global_position.distance_to(origin) < 0.1, label + " same stationary actor")
			var report := {"segment": label, "skill": skill, "level": level, "frames": FRAMES, "hit_events": hit_events, "targets_hit": targets_hit, "damage": damage, "mp_net_used": mp_before - c.mp, "mp_debit": mp_debit, "rng_before": rng_before, "rng_after": str(c._rng.state), "state_rng_before": state_rng_before, "state_rng_after": str(GameState.rng.state), "drawing_frames": drawing_frames, "storm_frames": storm_frames, "storm_revs": c.storm_revs if skill != "whirl" else 0, "storm_hits": c.storm_hits if skill != "whirl" else 0, "attack_interval": c.attack_interval(), "radius": c.last_area.get("radius", 0.0), "stats": stats, "camera_frames": camera_frames, "actor_frames": actor_frames}
			print("COMBAT630 " + JSON.stringify(report))
			c.clear_target()
			p.stop_moving()
			await _frames(60)
	print("VIDEO630 phase=%s checks=%d fails=%d %s" % [phase, t.checks, t.fails.size(), "PASS" if t.fails.is_empty() else "FAIL"])
	get_tree().quit(0 if t.fails.is_empty() else 1)