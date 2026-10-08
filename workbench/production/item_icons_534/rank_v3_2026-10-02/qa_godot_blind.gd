extends SceneTree
## Read-only current UiSkin rendering. Candidate textures use the official art path prefix in memory.

class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array[Dictionary] = []
	var mode := "actual"

	func label(at: Vector2, value: String, px: int = 15, strong: bool = false) -> void:
		if mode == "blind": return
		draw_string(heading if strong else body, at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color("e5d5bd") if strong else Color("b9ad99"))

	func icon(rect: Rect2, row: Dictionary, surface: String, black: bool = false, gray: bool = false, padding: float = 8.0) -> void:
		var tex: Texture2D = row.gray if gray else row.texture
		assert(tex.resource_path.begins_with("res://assets/sprites/ui/icons_a/"))
		if black:
			draw_rect(rect, Color.BLACK)
			draw_rect(rect, skin.SLOT_RIM, false, 1.0)
		elif surface == "belt":
			skin.slot(self, rect)
			var base: Color = row.color
			draw_rect(rect.grow(-8), Color(base.r * 0.35, base.g * 0.35, base.b * 0.35, 0.45))
			draw_rect(rect.grow(-8), Color(0.75, 0.72, 0.65), false, 1.0)
		else:
			skin.item_slot(self, rect, true)
		var shrink := minf(rect.size.x - padding * 2.0, rect.size.y - padding * 2.0) * (1.0 - float(row.spec.display_scale)) * 0.5
		assert(skin.item_icon(self, rect, tex, 1.0, padding + shrink))

	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 960), Color("211d19"))
		label(Vector2(24, 39), "#534 물약 단계 비교 · " + mode, 25, true)
		label(Vector2(24, 70), "기본40/25 → 2단80/50 → 3단140/90 · 모두 CONSUMABLE / tier1 / 1×1 / 스택10", 15)
		if mode == "overview":
			for i in rows.size():
				var row: Dictionary = rows[i]
				var x: float = 22.0 + (i % 3) * 419.0
				var y: float = 107.0 + floori(i / 3.0) * 412.0
				draw_rect(Rect2(x, y - 21, 403, 393), Color("29231e"))
				label(Vector2(x + 14, y + 8), row.spec.display_name + " · " + ("기본" if i % 3 == 0 else "%d단" % (i % 3 + 1)), 21, true)
				label(Vector2(x + 14, y + 34), "%s%d / ilvl%d" % [String(row.spec.resource).to_upper(), int(row.spec.power), int(row.spec.min_ilvl)], 14)
				var large_pad: float = 229.0 * (1.0 - float(row.spec.display_scale)) * 0.5
				assert(skin.item_icon(self, Rect2(x + 28, y + 44, 347, 229), row.source, 1.0, large_pad))
				label(Vector2(x + 14, y + 292), "승인 원화" if i % 3 == 0 else "Comfy clean 원화", 14)
				icon(Rect2(x + 214, y + 285, 80, 80), row, "bag", false, false, 6.0)
				icon(Rect2(x + 333, y + 313, 40, 40), row, "bag")
				label(Vector2(x + 215, y + 371), "80 출력", 14)
				label(Vector2(x + 332, y + 371), "가방40", 14)
		else:
			for i in rows.size():
				var row: Dictionary = rows[i]
				var x: float = 26.0 + (i % 3) * 419.0
				var y: float = 131.0 + floori(i / 3.0) * 307.0
				label(Vector2(x, y), row.spec.display_name + " · " + ("기본" if i % 3 == 0 else "%d단" % (i % 3 + 1)), 21, true)
				label(Vector2(x, y + 28), "%s%d / ilvl%d" % [String(row.spec.resource).to_upper(), int(row.spec.power), int(row.spec.min_ilvl)], 14)
				var settings: Array = [[40, 8.0, "bag", "가방40 · 여백8"], [48, 3.0, "vendor", "좌판48 · 여백3"], [42, 8.0, "belt", "현 벨트42 · 여백8"]]
				if mode == "belt_stress":
					settings = [[30, 8.0, "belt", "축소30 · 여백8"], [36, 8.0, "belt", "축소36 · 여백8"], [42, 8.0, "belt", "현 벨트42 · 여백8"]]
				for j in settings.size():
					var spec: Array = settings[j]
					var side: float = float(spec[0])
					var sx: float = x + 44.0 + j * 116.0
					label(Vector2(sx - 22, y + 63), String(spec[3]), 13)
					var rect := Rect2(sx + (48.0 - side) * 0.5, y + 88, side, side)
					icon(rect, row, String(spec[2]), mode == "black" or mode == "grayscale", mode == "grayscale", float(spec[1]))
					label(Vector2(sx - 13, y + 172), "실제 크기", 13)
					if j == 1:
						icon(Rect2(x + 50, y + 183, 80, 80), row, "bag", mode == "black" or mode == "grayscale", mode == "grayscale", 6.0)
				label(Vector2(x + 158, y + 217), row.spec.item_id, 14)
				label(Vector2(x + 158, y + 244), "기본 원화 · 크기 후보" if i % 3 == 0 else "80×80 RGBA 후보", 14)
		label(Vector2(24, 919), "현재 UiSkin + 물약별 표시비율 후보 0.75 / 0.86 / 1.0 · 게임 미반입", 15)
		label(Vector2(24, 944), "투명 여백은 UI가 제거함: 표시비율 별도 반입 필요 · 30/36은 벨트 축소 검수", 14)


var pack_root := ""
var out_dir := ""
var mode := "actual"


func _initialize() -> void:
	_launch.call_deferred()


func _texture(path: String, resource_path: String) -> ImageTexture:
	var raw := Image.load_from_file(path)
	assert(raw != null)
	var tex := ImageTexture.create_from_image(raw)
	tex.take_over_path(resource_path)
	return tex


func _launch() -> void:
	await process_frame
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="): pack_root = arg.trim_prefix("--root=")
		if arg.begins_with("--out="): out_dir = arg.trim_prefix("--out=")
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
	assert(not pack_root.is_empty() and not out_dir.is_empty())
	assert(mode in ["overview", "actual", "belt_stress", "black", "grayscale", "blind"])
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.card == 534 and manifest.items.size() == 4 and manifest.references.size() == 2)
	var specs: Array = []
	for family in ["hp", "mp"]:
		for ref in manifest.references:
			if ref.resource == family: specs.append(ref)
		for spec in manifest.items:
			if spec.resource == family: specs.append(spec)
	assert(specs.size() == 6)
	if mode == "blind":
		var shuffled: Array = []
		for index in [0, 5, 1, 4, 2, 3]: shuffled.append(specs[index])
		specs = shuffled
	var plate := Plate.new()
	plate.skin = load("res://ui/ui_skin.gd")
	plate.body = load("res://ui/ui_fonts.gd").body()
	plate.heading = load("res://ui/ui_fonts.gd").heading()
	plate.mode = mode
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = Vector2i(1280, 960)
	root.title = "#534 potion icons read-only UiSkin QA"
	for spec in specs:
		var uid: String = spec.item_id
		var def = load("res://data/items/%s.tres" % uid)
		assert(def != null and def.size == Vector2i(1, 1) and def.tier == 1 and def.max_stack == 10 and def.slot == 6)
		assert(def.power == spec.power and def.min_ilvl == spec.min_ilvl)
		var shared: String = "res://assets/sprites/ui/icons_a/items/%s_potion.png" % spec.resource
		assert(def.icon.resource_path == shared)
		var basic: bool = spec.efficacy_stage == 1
		var packed: String = spec.candidate_game_path if basic else spec.game_path
		var texture_path: String = "res://assets/sprites/ui/icons_a/qa534rankv3/current_%s.png" % uid if basic else "res://assets/sprites/ui/icons_a/qa534rankv3/candidate_%s.png" % uid
		var tex := _texture(pack_root.path_join(packed), texture_path)
		assert(tex.get_size() == Vector2(80, 80))
		var src := _texture(pack_root.path_join(spec.source_path), "res://assets/sprites/ui/icons_a/qa534rankv3/source_%s.png" % uid)
		var gray: Image = tex.get_image().duplicate()
		for y in gray.get_height():
			for x in gray.get_width():
				var c: Color = gray.get_pixel(x, y)
				var luminance: float = c.r * 0.2126 + c.g * 0.7152 + c.b * 0.0722
				gray.set_pixel(x, y, Color(luminance, luminance, luminance, c.a))
		var gray_tex := ImageTexture.create_from_image(gray)
		gray_tex.take_over_path("res://assets/sprites/ui/icons_a/qa534rankv3/gray_%s.png" % uid)
		plate.rows.append({"spec": spec, "texture": tex, "source": src, "gray": gray_tex, "color": def.color})
		# Candidate icon paths are distinct, so taking them over must never alter the shared definitions.
		assert(def.icon.resource_path == shared)
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png" % mode)) == OK)
	print("GODOT_534_PASS mode=", mode, " items=6 candidate4/scale_proposal/existing1x1/tier1/RGBA80/bag40p8/vendor48p3/belt42p8/stress30-36/resource_paths/render validated; definitions unchanged")
	quit(0)
