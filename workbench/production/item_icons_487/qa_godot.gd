extends SceneTree
## Planned T3 art only; actual UiSkin rendering without creating item definitions.
class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array = []
	var mode := "forty"
	var constellation_before: Texture2D
	var detail_before: Texture2D
	var detail_after: Texture2D
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
	func constellation_pair() -> void:
		label(Vector2(25, 40), "#487 칠성검 · 원화 금속점8 → 7 · 같은 영역/배율의 전후", 23, true)
		label(Vector2(25, 74), "칠성 사양: 위쪽 손잡이3점 + 아래쪽 사각그릇4점 · 원안/프롬프트/패킹 보존", 15)
		for i in 2:
			var x: float = 25.0 + i * 625.0
			label(Vector2(x, 116), "BEFORE · 원안8점" if i == 0 else "AFTER · v2 7점", 21, true)
			label(Vector2(x, 153), "원화 부분 · 동일150×430 영역", 14)
			var texture: Texture2D = detail_before if i == 0 else detail_after
			draw_rect(Rect2(x + 74, 175, 180, 516), Color.BLACK)
			draw_texture_rect_region(texture, Rect2(x + 74, 175, 180, 516), Rect2(270, 620, 150, 430))
			label(Vector2(x + 328, 188), "실제UiSkin40px칸", 14)
			item(Rect2(x + 393, 211, 40, 120), constellation_before if i == 0 else rows[2].future, true)
			label(Vector2(x + 328, 406), "실제UiSkin60px칸", 14)
			item(Rect2(x + 383, 430, 60, 180), constellation_before if i == 0 else rows[2].future, true)
		label(Vector2(25, 731), "중간점 하나 제거·새김선 연결 · 형상/재질 방향 유지 · 물리적 금속새김이며 외부 광원효과 없음", 14)
		label(Vector2(25, 752), "신규그림 후보/게임미반입 · 예정1×3 사양 · 실제ItemDef/UniqueDef 검증은 #272 뒤", 13)
	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 760), Color("211d19"))
		if mode == "constellation_pair":
			constellation_pair()
			return
		label(Vector2(25, 40), "#487 T3 칼3·운룡검 · 실제 UiSkin · " + mode, 23, true)
		label(Vector2(25, 73), "예정1×3 사양 · T3 데이터 미구현 · 후보 메모리 PNG만 렌더 · #272 게임반입 선행", 15)
		for i in rows.size():
			var row: Dictionary = rows[i]
			var x: float = 25.0 + i * 308.0
			label(Vector2(x, 112), row.spec.display_name, 20, true)
			label(Vector2(x, 138), "예정T3 · 1×3", 14)
			if mode == "forty":
				var sizes: Array = [40, 40, 48]
				var ys: Array = [177.0, 340.0, 520.0]
				var names: Array = ["가방40px칸", "검정40px칸", "좌판48px칸"]
				for j in 3:
					label(Vector2(x, ys[j] - 17.0), names[j], 14)
					item(Rect2(x + (285.0 - sizes[j]) / 2, ys[j], sizes[j], sizes[j] * 3), row.future, j == 1)
			elif mode == "base_compare":
				for j in 3:
					var side: int = [30, 40, 60][j]
					var y: float = [195.0, 360.0, 530.0][j]
					label(Vector2(x, y - 18.0), "%dpx · %s / 후보" % [side, row.spec.reference_display_name], 14)
					item(Rect2(x + 47.0 + (80.0 - side) / 2, y, side, side * 3), row.reference, true)
					item(Rect2(x + 197.0 + (80.0 - side) / 2, y, side, side * 3), row.future, true)
			else:
				for j in 3:
					var side: int = [30, 48, 60][j]
					var y: float = [177.0, 340.0, 520.0][j]
					label(Vector2(x, y - 18.0), "%dpx칸 · 예정1×3" % side, 14)
					item(Rect2(x + (285.0 - side) / 2, y, side, side * 3), row.future, mode == "black_sizes")
		label(Vector2(25, 732), "비교: T2 본국검/쌍수도/사인검 · 운룡검은 이번 운검 후보 · 모든 출력80×240RGBA", 15)
		label(Vector2(25, 751), "기존PNG42/H1PNG19·정의/UI 보존 · 실제 게임 설치/아이템 구현과 구별 · UiSkin8px패딩 그대로", 13)

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
	assert(mode in ["forty", "sizes", "black_sizes", "base_compare", "constellation_pair"])
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.items.size() == 4 and manifest.definition_state == "design_only")
	var plate := Plate.new()
	plate.skin = load("res://ui/ui_skin.gd")
	plate.body = ThemeDB.fallback_font
	plate.heading = load("res://ui/ui_fonts.gd").heading()
	plate.mode = mode
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = Vector2i(1280, 760)
	root.title = "#487 T3 칼 원화 검수"
	for spec in manifest.items:
		assert(spec.grid_w == 1 and spec.grid_h == 3 and spec.definition_state == "design_only")
		assert(not FileAccess.file_exists(spec.planned_definition_path))
		if spec.reference_status == "current_approved_T2_game_icon":
			var previous = load("res://data/items/%s.tres" % spec.reference_id)
			assert(previous != null and previous.size == Vector2i(1, 3) and previous.tier == 2)
		var raw := Image.load_from_file(pack_root.path_join(spec.game_path))
		assert(raw != null and raw.get_size() == Vector2i(80, 240))
		var tex := ImageTexture.create_from_image(raw)
		tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.item_id)
		var ref_raw := Image.load_from_file(spec.reference_path)
		assert(ref_raw != null)
		var ref_tex: Texture2D
		if spec.reference_status == "same_batch_planned_T3_base_candidate":
			assert(plate.rows[0].spec.item_id == spec.reference_id)
			ref_tex = plate.rows[0].future
		else:
			ref_tex = ImageTexture.create_from_image(ref_raw)
			ref_tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.reference_id)
		plate.rows.append({"spec": spec, "future": tex, "reference": ref_tex})
	for row in plate.rows:
		assert(row.future.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % row.spec.item_id)
		assert(row.reference.resource_path.begins_with("res://assets/sprites/ui/icons_a/"))
	if mode == "constellation_pair":
		var before := Image.load_from_file(pack_root.path_join("variants/v1/game/items/chilseonggeom.png"))
		assert(before != null and before.get_size() == Vector2i(80, 240))
		plate.constellation_before = ImageTexture.create_from_image(before)
		plate.constellation_before.take_over_path("res://assets/sprites/ui/icons_a/items/chilseonggeom_before.png")
		var old_source := Image.load_from_file(pack_root.path_join("source/items/chilseonggeom.png"))
		var new_source := Image.load_from_file(pack_root.path_join(manifest.items[2].source_path))
		assert(old_source != null and new_source != null)
		assert(old_source.get_size() == Vector2i(724, 2172) and new_source.get_size() == old_source.get_size())
		plate.detail_before = ImageTexture.create_from_image(old_source)
		plate.detail_after = ImageTexture.create_from_image(new_source)
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png" % mode)) == OK)
	print("GODOT_D1_487_PASS mode=", mode, " items=4 RGBA80x240/planned1x3/currentT2references/resource_paths/render validated; no T3 item definitions or intake installed")
	quit(0)
