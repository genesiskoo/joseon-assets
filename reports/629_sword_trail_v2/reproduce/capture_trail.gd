extends Node
## #629: real actor/combat MovieMaker QA. Starts after project autoloads.
const E2E_TOOLS := preload("res://tests/e2e/e2e.gd")
const RUNNER := preload("res://tests/e2e/e2e_runner.gd")
const AREA_TITLE := preload("res://ui/area_title.gd")
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

func _count(effects: Node, since: int, cue: String) -> int:
	return effects.recent(since).count(cue)

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
	var t := E2E_TOOLS.new(get_tree(), main, "video629", false)
	await t.go_down(1)
	await t.remove_enemies()
	await _frames(12)
	var p: Node3D = t.player()
	var c: Node = p.combat
	var effects: Node = get_tree().root.get_node("Vfx")
	DamageCalc.sure_hit = true
	t.camera().snap_to_target()
	t.camera().focus_on(p.global_position, 0.0)
	main.get_node("HUD").visible = false
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	var ch: Dictionary = GameState.character
	ch.level = 6
	ch.skill_points = int(ch.get("skill_points", 0)) + 2
	t.check(Progression.learn_skill(ch, c.skills[1]), "capture: dash prerequisite")
	t.check(Progression.learn_skill(ch, c.skills[2]), "capture: learn whirl")
	var origin: Vector3 = p.global_position
	var e: Enemy = await t.spawn_enemy("bandit", origin + Vector3(1.1, 0.0, 0.0), 1, {"hp": 100000.0, "frozen": true})
	t.check(p.visual().weapon_node() != null, "actual equipped sword")
	await _frames(90)
	var reports := []
	for kind in ["basic", "slash", "whirl", "crit"]:
		c.clear_target()
		p.stop_moving()
		p.face_toward(e.global_position)
		c._attack_timer = 0.0
		c.stats.crit_chance = 1.0 if kind == "crit" else 0.0
		c.mp = c.max_mp
		c.cooldowns.fill(0.0)
		seed(629)
		GameState.rng.seed = 20260916
		effects._rng.seed = 629
		c._rng.seed = 629
		var rng_before := str(c._rng.state)
		var hp_before: float = e.hp
		var mp_before: float = c.mp
		var seq: int = effects.seq
		var drawing_frames := 0
		var gold_frames := 0
		var actual_hits := 0
		var hp_previous: float = e.hp
		var hit_frames := []
		var mp_debit := 0.0
		var stopped := false
		_mark(kind, "BEGIN")
		for frame in 270:
			if frame == 30:
				if kind in ["basic", "crit"]:
					c.set_target(e)
				else:
					c.active_skill = 0 if kind == "slash" else 2
					var mp0: float = c.mp
					c.cast_active(origin + Vector3(2.0, 0.0, 0.0))
					mp_debit += mp0 - c.mp
			if frame == 150 and kind in ["slash", "whirl"]:
				c.cooldowns.fill(0.0)
				var mp0: float = c.mp
				c.cast_active(origin + Vector3(2.0, 0.0, 0.0))
				mp_debit += mp0 - c.mp
			if kind in ["basic", "crit"] and not stopped and _count(effects, seq, "sword_trail") >= 3:
				c.clear_target()
				p.stop_moving()
				stopped = true
			if p.visual().trail_drawing():
				drawing_frames += 1
				var tr: Node = p.visual().get_node("SwordTrail")
				if tr.has_method("is_critical") and tr.call("is_critical"):
					gold_frames += 1
			if e.hp < hp_previous:
				actual_hits += 1
				hit_frames.append(frame)
				hp_previous = e.hp
			await _frames(1)
		_mark(kind, "END")
		c.clear_target()
		p.stop_moving()
		var expected := 3 if kind in ["basic", "crit"] else 2
		t.check_eq(_count(effects, seq, "sword_trail"), expected, kind + " actual swings")
		t.check(drawing_frames > 10, kind + " live blade ribbon drawn")
		t.check(actual_hits >= expected, kind + " actual enemy hits")
		t.check(_count(effects, seq, "hit_crit") == (actual_hits if kind == "crit" else 0), kind + " resolved critical result")
		var report := {"segment": kind, "frames": 270, "hits": actual_hits, "hit_frames": hit_frames, "swings": _count(effects, seq, "sword_trail"), "crit_hits": _count(effects, seq, "hit_crit"), "damage": hp_before - e.hp, "mp_net_used": mp_before - c.mp, "mp_debit": mp_debit, "rng_before": rng_before, "rng_after": str(c._rng.state), "drawing_frames": drawing_frames, "gold_frames": gold_frames, "attack_interval": c.attack_interval(), "position": str(p.global_position)}
		print("COMBAT629 " + JSON.stringify(report))
		reports.append(report)
		await _frames(90)
	print("VIDEO629 phase=%s checks=%d fails=%d %s" % [phase, t.checks, t.fails.size(), "PASS" if t.fails.is_empty() else "FAIL"])
	get_tree().quit(0 if t.fails.is_empty() else 1)
