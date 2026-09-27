extends SceneTree
## Draw #467 candidate PNGs through the real UiSkin without runtime intake.

class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array = []
	var mode := "forty"
	func label(at: Vector2, value: String, size: int = 15, strong: bool = false) -> void:
		draw_string(heading if strong else body, at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color("e5d5bd") if strong else Color("a79b87"))
	func item(rect: Rect2, texture: Texture2D, black: bool = false) -> void:
		if black:
			draw_rect(rect, Color.BLACK)
			draw_rect(rect, skin.SLOT_RIM, false, 1.0)
		else:
			skin.item_slot(self, rect, true)
		assert(skin.item_icon(self, rect, texture, 1.0, 8.0))
	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 680), Color("211d19"))
		label(Vector2(25, 40), "#467 D1 장신구 5종 · 실제 공통 UiSkin", 24, true)
		label(Vector2(25, 70), "후보 전용 임시 텍스처 · 게임 ItemDef / 기존 PNG 미변경", 15)
		for i in rows.size():
			var row: Dictionary = rows[i]
			var x: float = 27.0 + i * 247.0
			label(Vector2(x, 117), row.spec.display_name + "  T%d" % row.spec.tier, 20, true)
			if mode == "forty":
				label(Vector2(x, 160), "가방 40px", 15)
				item(Rect2(x + 85, 180, 40, 40), row.future)
				label(Vector2(x, 286), "검정 슬롯 40px", 15)
				item(Rect2(x + 85, 310, 40, 40), row.future, true)
				label(Vector2(x, 416), "좌판 48px", 15)
				item(Rect2(x + 80, 450, 48, 48), row.future)
				label(Vector2(x, 590), row.spec.item_id, 16)
			else:
				for j in 3:
					var side: int = [30, 48, 60][j]
					var y: float = [180.0, 320.0, 480.0][j]
					label(Vector2(x, y - 20.0), "%dpx / 1칸" % side, 15)
					item(Rect2(x + 80, y, side, side), row.future, j == 0)
		label(Vector2(26, 648), "물체 자체의 천·놋쇠·구슬·옥·금 구별 / 외부 등급테두리·후광 없음", 16)

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
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.items.size() == 5)
	var plate := Plate.new()
	plate.skin = load("res://ui/ui_skin.gd")
	plate.body = ThemeDB.fallback_font
	plate.heading = load("res://ui/ui_fonts.gd").heading()
	plate.mode = mode
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = Vector2i(1280, 680)
	root.title = "#467 D1 장신구 시안 검수"
	for spec in manifest.items:
		var def = load("res://data/items/%s.tres" % spec.item_id)
		assert(def != null and def.icon != null)
		assert(def.display_name == spec.display_name and def.tier == spec.tier)
		assert(def.size == Vector2i(1, 1) and spec.grid_w == 1 and spec.grid_h == 1)
		assert(def.slot == spec.slot)
		var image := Image.load_from_file(pack_root.path_join("game/items/%s.png" % spec.item_id))
		assert(image != null and image.get_size() == Vector2i(80, 80))
		var texture := ImageTexture.create_from_image(image)
		texture.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.item_id)
		plate.rows.append({"definition": def, "future": texture, "spec": spec})
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.35).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png" % mode)) == OK)
	print("GODOT_D1_467_PASS mode=", mode, " items=", manifest.items.size(), " footprint/name/tier/render validated; no runtime intake")
	quit(0)
