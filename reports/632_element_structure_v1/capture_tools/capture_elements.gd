extends Node
## #632 capture only: real belt throws / real enemy sal shots, normal time.
const E2E_TOOLS := preload("res://tests/e2e/e2e.gd")
const RUNNER := preload("res://tests/e2e/e2e_runner.gd")
const AREA_TITLE := preload("res://ui/area_title.gd")
const TALISMAN := preload("res://actors/talisman_shot.gd")
const PROJECTILE := preload("res://actors/projectile.gd")
const FRAMES := 180
const START := 30
const HP := 100000.0
var phase := "before"
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
			var rec := {"ordinal": ordinal, "kind": "talisman" if script == TALISMAN else "enemy", "seed": shot_seed, "initial_rng": str(n._rng.state), "born_frame": frame_no, "frames": [], "ref": weakref(n)}
			if script == TALISMAN:
				rec.merge({"item": n.def.id, "element": String(n.def.talisman_element), "mult": n.mult, "look_scale": n.look_scale, "radius": n.burst_radius(), "mods": n.mods.duplicate(true)})
			else:
				rec.merge({"element": String(n.element), "look": String(n.look), "dmg_min": n.dmg_min, "dmg_max": n.dmg_max, "share": n.share, "accuracy": n.accuracy})
			tracked[id] = rec
			n.tree_exiting.connect(_shot_exit.bind(id), CONNECT_ONE_SHOT)
			ordinal += 1
		tracked[id].frames.append({"frame": frame_no, "position": str(n.global_position), "velocity": str(n.velocity), "rng": str(n._rng.state)})

func _status(n: Node) -> Dictionary:
	var s: Node = n.combat if n == player_ref else n
	var out := {"mask": s.status_mask()}
	for key in ["chill_left", "frozen_left", "freeze_guard_left", "burn_dps", "burn_left", "sal_dps", "sal_left"]:
		out[key] = s._status.get(key)
	return out

func _tick(actor: Node, amount: int, element: StringName) -> void:
	var index := -1 if actor == player_ref else enemy_refs.find(actor)
	tick_events.append({"frame": frame_no, "actor": index, "amount": amount, "element": String(element)})

func _stats(c: Node) -> Dictionary:
	return c.stats.duplicate(true)

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
	var t := E2E_TOOLS.new(get_tree(), main, "video632", false)
	await t.go_down(1)
	await t.remove_enemies()
	await _frames(12)
	var p: Node3D = t.player()
	player_ref = p
	var c: Node = p.combat
	var effects: Node = get_tree().root.get_node("Vfx")
	var stage := _open_spot(t.level())
	if not t.check(not stage.is_empty(), "same clear stage"):
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
	print("FIXTURE632 " + JSON.stringify({"fps": 60, "speed": 1.0, "area": GameState.area_id, "floor": GameState.floor_no, "center": str(center), "origin": str(origin), "camera_rotation": str(t.camera().rotation_degrees), "camera_size": t.camera().size, "player_model": p.visual().model.resource_path, "weapon": GameState.inventory.equipment.get("weapon").def.id, "game_seed": 20260916, "combat_seed": 632, "independent_projectile_seed_base": 632, "frames_per_segment": FRAMES, "note": "normal StatsCalc SPI20/150; actual enemy areaLv1/16; no forced cosmetic effect or chain"}))
	for element in ["fire", "cold", "lightning", "sal"]:
		for strength in ["low", "strong"]:
			current_label = element + "_" + strength
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
			GameState.character.level = 30
			GameState.character.spi = 150.0 if strength == "strong" and element != "sal" else 20.0
			c.recompute_stats()
			c.hp = c.max_hp
			c.mp = c.max_mp
			c.talisman_cd = 0.0
			c.clear_status()
			var inv: Inventory = GameState.inventory
			var item := "talisman_fire" if element == "fire" else ("talisman_ice" if element == "cold" else "talisman_thunder")
			if element != "sal":
				inv.belt_put(1, ItemInstance.create(ItemDb.get_def(item), 5))
			enemy_refs.clear()
			var positions := []
			var area_level := 16 if strength == "strong" and element == "sal" else 1
			if element != "sal":
				for offset in [Vector3(4,0,0), Vector3(4,0,-0.65), Vector3(4,0,0.65), Vector3(4,0,2.8)]:
					var def := E2E_TOOLS.enemy_def("bandit").duplicate() as EnemyDef
					def.move_speed = 0.0
					def.attack_range = 0.0
					def.aggro_range = 0.0
					def.keep_distance_min = 0.0
					def.keep_distance_max = 0.0
					var e: Enemy = await t.spawn_enemy(def, origin + offset, 1, {"hp": HP, "frames": 0})
					e.seed_rng(632 + enemy_refs.size())
					enemy_refs.append(e)
					positions.append(str(e.global_position))
			else:
				var def := E2E_TOOLS.enemy_def("nachalnyeo").duplicate() as EnemyDef
				def.move_speed = 0.0
				var e: Enemy = await t.spawn_enemy(def, origin + Vector3.RIGHT * 5.0, area_level, {"hp": HP, "frames": 0})
				e.seed_rng(632)
				e.set_physics_process(false)
				for hook in e.hooks:
					if hook.get_script().resource_path.ends_with("pull.gd"):
						hook._awake = true
						hook._t = -99.0
				enemy_refs.append(e)
				positions.append(str(e.global_position))
			await _frames(60)
			if element != "sal":
				await t.mouse_move(t.screen_of((enemy_refs[0] as Enemy).global_position + Vector3(0, 0.94, 0)))
				await _frames(4)
			tracked.clear()
			ordinal = 0
			tick_events.clear()
			seed(632)
			GameState.rng.seed = 20260916
			effects._rng.seed = 632
			c._rng.seed = 632
			var initial_rng := str(c._rng.state)
			var state_rng := str(GameState.rng.state)
			var hp_last := [c.hp]
			for e in enemy_refs:
				hp_last.append(e.hp)
			var report := {"segment": current_label, "element": element, "strength": strength, "frames": FRAMES, "stats": _stats(c), "item": item if element != "sal" else "", "stack_before": 5 if element != "sal" else 0, "mp_before": c.mp, "hp_before": c.hp, "area_level": area_level, "positions": positions, "player_rng_before": initial_rng, "state_rng_before": state_rng, "hit_events": [], "actor_frames": [], "camera_frames": [], "target_frames": [], "player_status_frames": [], "enemy_status_frames": [], "talisman_cd_frames": [], "time_scale_frames": [], "enemy_rng_before": enemy_refs.map(func(e) -> String: return str(e._rng.state))}
			if element == "sal":
				report.enemy_damage = str((enemy_refs[0] as Enemy).attack_damage())
				report.enemy_damage_mult = (enemy_refs[0] as Enemy)._dmg_k()
			_mark(current_label, "BEGIN")
			for frame in FRAMES:
				frame_no = frame
				if frame == START:
					if element != "sal":
						t._key_state(KEY_2, true)
					else:
						(enemy_refs[0] as Enemy)._cooldown = 0.0
						(enemy_refs[0] as Enemy).set_physics_process(true)
				if frame == START + 1 and element != "sal":
					t._key_state(KEY_2, false)
				_observe_shots(t.level())
				if element == "sal" and c.is_sal():
					(enemy_refs[0] as Enemy)._cooldown = 999.0
				report.actor_frames.append(str(p.global_position))
				report.camera_frames.append(str(t.camera().global_position))
				report.player_status_frames.append(_status(p))
				report.talisman_cd_frames.append(c.talisman_cd)
				report.time_scale_frames.append(Engine.time_scale)
				var target_frame := []
				var status_frame := []
				for e in enemy_refs:
					target_frame.append(str(e.global_position))
					status_frame.append(_status(e))
				report.target_frames.append(target_frame)
				report.enemy_status_frames.append(status_frame)
				var hp_now := [c.hp]
				for e in enemy_refs:
					hp_now.append(e.hp)
				for i in hp_now.size():
					if hp_now[i] < hp_last[i]:
						report.hit_events.append({"frame": frame, "actor": i - 1, "damage": hp_last[i] - hp_now[i]})
				hp_last = hp_now
				await _frames(1)
			_mark(current_label, "END")
			report.enemy_rng_after = enemy_refs.map(func(e) -> String: return str(e._rng.state))
			report.player_rng_after = str(c._rng.state)
			report.state_rng_after = str(GameState.rng.state)
			report.mp_after = c.mp
			report.hp_after = c.hp
			report.stack_after = inv.belt[1].stack if element != "sal" and inv.belt[1] != null else 0
			report.status_ticks = tick_events.duplicate(true)
			report.shots = []
			for rec in tracked.values():
				var plain: Dictionary = rec.duplicate(true)
				plain.erase("ref")
				report.shots.append(plain)
			t.check(report.shots.size() == 1, current_label + " one actual projectile")
			t.check(report.hit_events.size() > 0, current_label + " actual damage")
			t.check(is_equal_approx(c.mp, float(report.mp_before)), current_label + " no spell MP cost")
			if element != "sal":
				t.check(report.stack_after == 4, current_label + " one actual belt item consumed")
				t.check(int(report.shots[0].get("hits", 0)) == (1 if element == "lightning" else 3), current_label + " actual AOE/single target count")
				t.check(report.shots[0].mult >= 2.5 if strength == "strong" else report.shots[0].mult < 1.75, current_label + " normal SPI strength")
			else:
				t.check(c.is_sal(), current_label + " actual sal status from enemy orb")
				t.check(c.hp > 0.0, current_label + " actor survives")
			print("COMBAT632 " + JSON.stringify(report))
			await _frames(60)
	EventBus.status_tick.disconnect(_tick)
	print("VIDEO632 phase=%s checks=%d fails=%d %s" % [phase, t.checks, t.fails.size(), "PASS" if t.fails.is_empty() else "FAIL"])
	get_tree().quit(0 if t.fails.is_empty() else 1)