extends SceneTree
## Candidate-only textures drawn by actual game UiSkin; no asset intake.
class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array = []
	var mode := "forty"
	func label(pos: Vector2, value: String, size: int = 15, strong: bool = false) -> void:
		draw_string(heading if strong else body, pos, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color("e5d5bd") if strong else Color("a79b87"))
	func item(rect: Rect2, texture: Texture2D, black: bool = false) -> void:
		if black:
			draw_rect(rect, Color.BLACK)
			draw_rect(rect, skin.SLOT_RIM, false, 1.0)
		else:
			skin.item_slot(self, rect, true)
		assert(skin.item_icon(self, rect, texture, 1.0, 8.0))
	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 760), Color("211d19"))
		label(Vector2(25, 40), "#469 광다회·목화·부첩2 · 실제 UiSkin · " + mode, 24, true)
		label(Vector2(25, 73), "실제 점유: 2×1 / 2×2 / 1×2 / 1×2 · 후보는 메모리에서만 검수 · 게임 미반입", 15)
		for i in rows.size():
			var row: Dictionary = rows[i]
			var spec: Dictionary = row.spec
			var x: float = 25.0 + i * 308.0
			label(Vector2(x, 112), spec.display_name, 21, true)
			if mode == "forty":
				var sizes: Array = [40, 40, 48]
				var ys: Array = [165.0, 345.0, 535.0]
				var names: Array = ["가방40px", "검정40px", "좌판48px"]
				for j in 3:
					label(Vector2(x, ys[j] - 18.0), names[j], 15)
					item(Rect2(x+70.0, ys[j], spec.grid_w*sizes[j], spec.grid_h*sizes[j]),row.future,j==1)
			else:
				for j in 3:
					var side: int = [30, 48, 60][j]
					var y: float = [165.0, 340.0, 530.0][j]
					label(Vector2(x, y-18.0), "%dpx × %d×%d칸" % [side,spec.grid_w,spec.grid_h], 15)
					item(Rect2(x+70.0,y,spec.grid_w*side,spec.grid_h*side),row.future,mode=="black_sizes")
		label(Vector2(25, 735), "직조 띠 / 검은 장화 / 황토·적색 종이첩 / 남색 천 부첩 · 기존 정의·PNG42 보존", 16)

var pack_root := ""
var out_dir := ""
var mode := "forty"
func _initialize() -> void:
	call_deferred("_launch")
func _launch() -> void:
	await process_frame
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="): pack_root=arg.trim_prefix("--root=")
		if arg.begins_with("--out="): out_dir=arg.trim_prefix("--out=")
		if arg.begins_with("--mode="): mode=arg.trim_prefix("--mode=")
	assert(not pack_root.is_empty() and not out_dir.is_empty())
	var manifest=JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.items.size()==4)
	var plate:=Plate.new()
	plate.skin=load("res://ui/ui_skin.gd")
	plate.body=ThemeDB.fallback_font
	plate.heading=load("res://ui/ui_fonts.gd").heading()
	plate.mode=mode
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_DISABLED
	root.size=Vector2i(1280,760)
	root.title="#469 D1 장비·부첩 검수"
	for spec in manifest.items:
		var def=load("res://data/items/%s.tres" % spec.item_id)
		assert(def != null and def.icon != null)
		assert(def.display_name==spec.display_name and def.size==Vector2i(spec.grid_w,spec.grid_h))
		assert(def.slot==spec.slot and def.tier==spec.tier and def.max_stack==spec.max_stack)
		var image:=Image.load_from_file(pack_root.path_join(spec.game_path))
		assert(image != null and image.get_size()==Vector2i(spec.output_width,spec.output_height))
		var tex:=ImageTexture.create_from_image(image)
		tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.item_id)
		plate.rows.append({"definition":def,"future":tex,"spec":spec})
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png"%mode))==OK)
	print("GODOT_D1_469_PASS mode=",mode," items=",manifest.items.size()," footprint/name/tier/stack/render validated; no runtime intake")
	quit(0)
