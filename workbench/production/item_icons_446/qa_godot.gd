extends SceneTree
## #446: current ItemDef and UiSkin, candidate art in memory only. No installation.

class Plate extends Node2D:
	var skin
	var body: Font
	var heading: Font
	var rows: Array = []
	var references: Array = []
	var mode := "before"
	var dimensions := Vector2i(1280, 720)

	func label(at: Vector2, text: String, size: int = 16, bright: bool = false) -> void:
		draw_string(heading if bright else body, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color("e5d5bd") if bright else Color("a79b87"))

	func object_at(r: Rect2, row: Dictionary, future: bool, black: bool = false) -> void:
		if black:
			draw_rect(r, Color.BLACK)
			draw_rect(r, skin.SLOT_RIM, false, 1.0)
		else:
			skin.item_slot(self, r, true)
		var art = row.future if future else row.definition.icon
		if not skin.item_icon(self, r, art, 1.0, 8.0):
			var fs := 20 if r.size.x >= 80 else 16
			draw_string(body, r.position + Vector2(r.size.x * .5 - fs * .5, r.size.y * .5 + fs * .4), row.definition.glyph, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, row.definition.color)

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, dimensions), Color("211d19"))
		var title := "기존 표시" if mode == "before" else "후보 그림"
		if mode == "sizes": title = "30·48·60px 칸 크기 검수"
		label(Vector2(26, 36), "D1 소지품 확장 1차 · " + title, 24, true)
		label(Vector2(26, 65), "게임 공통 UiSkin 렌더 검수 · 후보 PNG는 게임에 설치하지 않음", 15)
		if mode == "sizes":
			for i in rows.size():
				var row: Dictionary = rows[i]
				var x := 25 + (i % 2) * 630
				var y := 85 + (i / 2) * 227
				label(Vector2(x, y + 22), "%s · %s" % [row.spec.display_name, row.spec.item_id], 17, true)
				for j in 3:
					var side: int = [30, 48, 60][j]
					var r := Rect2(x + 45 + j * 181, y + 42, side * row.spec.grid_w, side * row.spec.grid_h)
					object_at(r, row, true)
					label(Vector2(r.position.x, y + 225), "%dpx/칸" % side, 14)
			return
		for i in rows.size():
			var row: Dictionary = rows[i]
			var x := 34 + i * 205
			label(Vector2(x, 110), row.spec.display_name, 19, true)
			label(Vector2(x, 136), "%d×%d칸" % [row.spec.grid_w, row.spec.grid_h], 15)
			var w: float = row.spec.grid_w * 40
			var h: float = row.spec.grid_h * 40
			object_at(Rect2(x + (156 - w) / 2, 175, w, h), row, mode != "before")
			object_at(Rect2(x + (156 - w) / 2, 364, w, h), row, mode != "before", true)
		label(Vector2(28, 338), "검정 바탕", 15)
		label(Vector2(28, 548), "같은 화풍 기준 · 기존 채택 D1", 18, true)
		for i in references.size():
			var row: Dictionary = references[i]
			var w: float = row.spec.grid_w * 40
			var h: float = row.spec.grid_h * 40
			var r := Rect2(320 + i * 223, 560, w, h)
			object_at(r, row, false)
			label(Vector2(320 + i * 223, 703), row.spec.display_name, 15)

var out_dir := ""
var mode := "before"
var pack_root := ""

func _initialize() -> void:
	_launch.call_deferred()

func _launch() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="): pack_root = arg.trim_prefix("--root=")
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
		if arg.begins_with("--out="): out_dir = arg.trim_prefix("--out=")
	if pack_root.is_empty() or out_dir.is_empty():
		push_error("root and out are required")
		quit(1)
		return
	var config = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	var plate := Plate.new()
	plate.skin = load("res://ui/ui_skin.gd")
	var fonts = load("res://ui/ui_fonts.gd")
	plate.body = ThemeDB.fallback_font
	plate.heading = fonts.heading()
	plate.mode = mode
	plate.dimensions = Vector2i(1280, 790 if mode == "sizes" else 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = plate.dimensions
	root.title = "#446 D1 소지품 후보 검수"
	for spec in config.items:
		var definition = load("res://data/items/%s.tres" % spec.item_id)
		assert(definition != null, "missing current definition")
		assert(definition.size == Vector2i(spec.grid_w, spec.grid_h), "footprint mismatch")
		assert(definition.display_name == spec.display_name, "name mismatch")
		var im := Image.load_from_file(pack_root.path_join("game/items/%s.png" % spec.item_id))
		assert(im != null and im.get_size() == Vector2i(spec.output_width, spec.output_height), "packed PNG mismatch")
		var texture := ImageTexture.create_from_image(im)
		# Virtual future resource identity selects the real alpha-aware UiSkin path.
		# No file is written to res://assets, and this process is short-lived.
		texture.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.item_id)
		plate.rows.append({"definition": definition, "future": texture, "spec": spec})
	for id in ["paeraengi", "leather_shoes", "cotton_belt"]:
		var definition = load("res://data/items/%s.tres" % id)
		plate.references.append({"definition": definition, "future": null, "spec": {"display_name": definition.display_name, "grid_w": definition.size.x, "grid_h": definition.size.y}})
	root.add_child(plate)
	plate.queue_redraw()
	_capture.call_deferred(plate)

func _capture(plate: Plate) -> void:
	await process_frame
	await process_frame
	await create_timer(.35).timeout
	var image := root.get_texture().get_image()
	assert(image.get_size() == plate.dimensions, "capture dimensions mismatch")
	var path := out_dir.path_join("godot_%s.png" % mode)
	var err := image.save_png(path)
	print("GODOT_D1_446 %s %s · items6/footprints6/names6/alphaPNG6" % ["PASS" if err == OK else "FAIL", path])
	quit(0 if err == OK else 1)
