extends "res://tests/e2e/scenarios/_feel_numbers_demo.gd"
## #721: select one existing deterministic production showcase clip per recording.
## No production logic changes. Showcase fixture damage/dummies are inherited and disclosed.
var selected_clip := "03_fire"
var photo_label := ""
var _photo_done := false
var _capture_ticks := 0

func _plate_arg() -> String:
	return "A"  # Current production default damage numbers; N716 remains a candidate.

func _one(p: Node3D, home: Vector3, fwd: Vector3, side: Vector3, name: String, layout: Array, hp: float, body: Callable) -> void:
	if name != selected_clip:
		return
	_photo_done = false
	_capture_ticks = 0
	await super._one(p, home, fwd, side, name, layout, hp, body)
	if photo_label != "":
		t.check(_photo_done, "Marketing action screenshot saved: " + photo_label)

func _tick(n: int) -> void:
	for i in n:
		await super._tick(1)
		if _clip == "" or photo_label == "" or _photo_done:
			continue
		_capture_ticks += 1
		var hit := false
		for count in _hits.values():
			hit = hit or int(count) > 0
		# First visible impact, still within status/element display; flurry shows its second hit.
		var ready: bool = hit and _capture_ticks >= 45
		if selected_clip == "09_flurry":
			ready = _hit_n(0) >= 2
		if ready:
			_photo_done = true
			await RenderingServer.frame_post_draw
			var img := t.tree.root.get_viewport().get_texture().get_image()
			if t.check(img.get_size() == Vector2i(3840, 2160), "Native 4K action viewport"):
				await t.shot(photo_label)
