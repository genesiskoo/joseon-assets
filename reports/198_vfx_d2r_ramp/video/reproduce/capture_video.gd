extends Node
## #198 video QA only. Normal project scene starts after autoload registration.
const E2E_TOOLS := preload("res://tests/e2e/e2e.gd")
const RUNNER := preload("res://tests/e2e/e2e_runner.gd")
const AREA_TITLE := preload("res://ui/area_title.gd")

func _ready() -> void:
	call_deferred("_capture")

func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame

func _mark(label: String, edge: String) -> void:
	print("CAPTURE %s %s %d" % [label, edge, Engine.get_process_frames()])

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
	var t := E2E_TOOLS.new(get_tree(), main, "video198", false)
	await t.go_down(1)
	await t.remove_enemies()
	await _frames(12)
	var p: Node3D = t.player()
	t.camera().snap_to_target()
	t.camera().focus_on(p.global_position, 0.0)
	main.get_node("HUD").visible = false
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	var effects: Node = get_tree().root.get_node("Vfx")
	var pos: Vector3 = p.global_position + Vector3(-1.3, 1.0, 1.3)
	await _frames(30)
	var variants := [["fire", effects.TALISMAN_FIRE], ["cold", effects.TALISMAN_COLD], ["sal", effects.SAL]]
	for variant in variants:
		for phase in ["before", "after"]:
			var label: String = "%s_%s" % [variant[0], phase]
			_mark(label, "BEGIN")
			await _frames(30)
			for replay in 3:
				var made: bool = effects.play("fire_burst", pos, {"color": variant[1], "ramp": "" if phase == "before" else variant[0], "scale": 2.8, "blend": "add", "hdr": 3.0})
				t.check(made, label + " animation replay")
				var spr: AnimatedSprite3D = effects.last_sheet("fire_burst")
				t.check(spr != null and is_equal_approx(spr.speed_scale, 1.0), label + " native speed")
				await _frames(60)
				t.check(effects.last_sheet("fire_burst") == null, label + " sheet released")
			await _frames(30)
			_mark(label, "END")
			await _frames(20)
	for cue in ["fire_burst", "sal_burst", "talisman_fire_hit"]:
		_mark("actual_" + cue, "BEGIN")
		await _frames(30)
		for replay in 3:
			effects._rng.seed = 198000 + replay
			t.check(effects.play(cue, pos), "actual " + cue + " replay")
			await _frames(60)
		await _frames(30)
		_mark("actual_" + cue, "END")
		await _frames(20)
	print("VIDEO198 checks=%d fails=%d %s" % [t.checks, t.fails.size(), "PASS" if t.fails.is_empty() else "FAIL"])
	get_tree().quit(0 if t.fails.is_empty() else 1)
