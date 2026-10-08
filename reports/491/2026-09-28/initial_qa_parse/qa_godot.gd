extends SceneTree
## Planned T3 art rendered through current UiSkin without installing definitions.
class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array = []
	var mode := "forty"
	func label(pos: Vector2, value: String, size: int = 15, strong: bool = false) -> void:
		draw_string(heading if strong else body, pos, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color("e5d5bd") if strong else Color("a79b87"))
	func item(rect: Rect2, texture: Texture2D, black: bool = false) -> void:
		assert(texture.resource_path.begins_with("res://assets/sprites/ui/icons_a/"))
		if black:
			draw_rect(rect, Color.BLACK)
			draw_rect(rect, skin.SLOT_RIM, false, 1.0)
		else:
			skin.item_slot(self, rect, true)
		assert(skin.item_icon(self, rect, texture, 1.0, 8.0))
	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 760), Color("211d19"))
		label(Vector2(25, 40), "#491 T3 갑·포3 · 실제 UiSkin · " + mode, 23, true)
		label(Vector2(25, 73), "예정2×3 사양 · T3 데이터 미구현 · 후보 PNG만 메모리 렌더 · #272 게임반입 선행", 15)
		for i in rows.size():
			var row: Dictionary = rows[i]
			var x: float = 25.0 + i * 414.0
			label(Vector2(x, 112), row.spec.display_name, 20, true)
			label(Vector2(x, 138), "예정T3 · 2×3", 14)
			if mode == "forty":
				for j in 3:
					var side: int = [40, 40, 48][j]
					var y: float = [177.0, 340.0, 520.0][j]
					label(Vector2(x, y - 17), ["가방40px칸", "검정40px칸", "좌판48px칸"][j], 14)
					item(Rect2(x + (390.0 - side * 2) / 2, y, side * 2, side * 3), row.future, j == 1)
			elif mode == "base_compare":
				for j in 3:
					var side: int = [30, 40, 60][j]
					var y: float = [195.0, 360.0, 530.0][j]
					label(Vector2(x, y - 18), "%dpx · %s / 후보" % [side, row.spec.reference_display_name], 14)
					item(Rect2(x + 40 + (120.0 - side * 2) / 2, y, side * 2, side * 3), row.reference, true)
					item(Rect2(x + 225 + (120.0 - side * 2) / 2, y, side * 2, side * 3), row.future, true)
			else:
				for j in 3:
					var side: int = [30, 48, 60][j]
					var y: float = [177.0, 340.0, 520.0][j]
					label(Vector2(x, y - 18), "%dpx칸 · 예정2×3" % side, 14)
					item(Rect2(x + (390.0 - side * 2) / 2, y, side * 2, side * 3), row.gray if mode == "grayscale" else row.future, mode != "sizes")
		label(Vector2(25, 732), "승인T2 비교: #464 경번갑/두정갑/학창의(미게임반입) · 후보 출력160×240RGBA", 15)
		label(Vector2(25, 751), "기존PNG42/H1PNG19·정의/UI 보존 · 게임 설치와 구별 · UiSkin8px패딩·자연 비율 유지", 13)

var pack_root := ""
var out_dir := ""
var mode := "forty"
func _initialize() -> void:
	call_deferred("_launch")
func _launch() -> void:
	await process_frame
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="): pack_root = arg.trim_prefix("--root=")
		if arg.begins_with("--out="): out_dir = arg.trim_prefix("--out=")
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
	assert(not pack_root.is_empty() and not out_dir.is_empty())
	assert(mode in ["forty", "sizes", "black_sizes", "base_compare", "grayscale"])
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.items.size() == 3 and manifest.definition_state == "design_only")
	var plate := Plate.new()
	plate.skin = load("res://ui/ui_skin.gd")
	plate.body = ThemeDB.fallback_font
	plate.heading = load("res://ui/ui_fonts.gd").heading()
	plate.mode = mode
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = Vector2i(1280, 760)
	root.title = "#491 T3 armor artwork QA"
	for spec in manifest.items:
		assert(spec.grid_w == 2 and spec.grid_h == 3 and spec.definition_state == "design_only")
		assert(not FileAccess.file_exists(spec.planned_definition_path))
		var previous = load("res://data/items/%s.tres" % spec.reference_id)
		assert(previous != null and previous.size == Vector2i(2, 3) and previous.tier == 2)
		var raw := Image.load_from_file(pack_root.path_join(spec.game_path))
		assert(raw != null and raw.get_size() == Vector2i(160, 240))
		var tex := ImageTexture.create_from_image(raw)
		tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.item_id)
		var ref_raw := Image.load_from_file(spec.reference_path)
		assert(ref_raw != null and ref_raw.get_size() == Vector2i(160, 240))
		var ref_tex := ImageTexture.create_from_image(ref_raw)
		ref_tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.reference_id)
		var gray := raw.duplicate()
		for y in gray.get_height():
			for x in gray.get_width():
				var c := gray.get_pixel(x, y)
				var v := c.r * 0.2126 + c.g * 0.7152 + c.b * 0.0722
				gray.set_pixel(x, y, Color(v, v, v, c.a))
		var gray_tex := ImageTexture.create_from_image(gray)
		gray_tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s_gray.png" % spec.item_id)
		plate.rows.append({"spec": spec, "future": tex, "reference": ref_tex, "gray": gray_tex})
	for row in plate.rows:
		assert(row.future.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % row.spec.item_id)
		assert(row.reference.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % row.spec.reference_id)
		assert(row.gray.resource_path.ends_with("_gray.png"))
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png" % mode)) == OK)
	print("GODOT_D1_491_PASS mode=", mode, " items=3 RGBA160x240/planned2x3/approvedT2references/resource_paths/render validated; no T3 item definitions or intake installed")
	quit(0)
