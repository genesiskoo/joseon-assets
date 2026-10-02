extends SceneTree
## #498: native comparison of unapproved candidates. No game scenes or saves run.

const SKIN := preload("res://ui_skin_snapshot.gd")
const REVISED := ["seal_array", "blade_storm", "breath", "pouch"]
const MODES := ["overview", "sizes_a", "sizes_b", "revisions"]

class Plate extends Node2D:

	var font: Font
	var rows: Array[Dictionary] = []
	var before: Dictionary = {}
	var mode := "overview"

	func label(at: Vector2, value: String, px: int = 16, bright: bool = false) -> void:
		draw_string(font, at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color("e5d5bd") if bright else Color("b9ad99"))

	func icon(rect: Rect2, texture: Texture2D, padding: float = 0.0, slot: bool = false) -> void:
		if slot:
			SKIN.slot(self, rect)
		assert(SKIN.item_icon(self, rect, texture, 1.0, padding))

	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 720), Color("211d19"))
		label(Vector2(24, 32), "#498 신규10종 후보 · " + mode + " · 게임 반입 0종", 22, true)
		if mode == "overview":
			_draw_overview()
		elif mode == "revisions":
			_draw_revisions()
		else:
			_draw_sizes()

	func _draw_overview() -> void:
		label(Vector2(24, 62), "기존 승인 3종", 17, true)
		for i in 3:
			var row: Dictionary = rows[i]
			var x: float = 268.0 + i * 246.0
			icon(Rect2(x, 68, 128, 128), row.texture)
			label(Vector2(x, 217), row.spec.display_name + " · " + row.spec.id, 15)
		label(Vector2(24, 256), "새 후보 10종 · 원화 전체를 128×128로만 축소", 17, true)
		for i in 10:
			var row: Dictionary = rows[i + 3]
			var x: float = 44.0 + (i % 5) * 246.0
			var y: float = 274.0 + floori(i / 5.0) * 201.0
			icon(Rect2(x, y, 128, 128), row.texture)
			label(Vector2(x, y + 150), row.spec.display_name, 17, true)
			label(Vector2(x, y + 174), row.spec.id + " · " + row.spec.selected_version, 13)
		label(Vector2(24, 702), "승인 아이콘은 원본128 그대로 · 신규는 1024→128 Lanczos · 색/알파/구도 편집 없음", 14)

	func _draw_sizes() -> void:
		var specs: Array = [[30, 0.0, false, 320.0, "이미지30"], [48, 0.0, false, 430.0, "이미지48"], [60, 0.0, false, 550.0, "이미지60"], [30, 3.0, true, 700.0, "HUD30/p3"], [60, 5.0, true, 835.0, "HUD60/p5"], [48, 3.0, true, 1000.0, "스킬48/p3"]]
		for spec in specs:
			label(Vector2(float(spec[3]) - 5, 67), String(spec[4]), 15, true)
		var indices: Array[int] = [0, 1, 2, 3, 4, 5, 6] if mode == "sizes_a" else [0, 1, 2, 7, 8, 9, 10, 11, 12]
		var step: float = 80.0 if mode == "sizes_a" else 68.0
		for i in indices.size():
			var row: Dictionary = rows[indices[i]]
			var y: float = 83.0 + i * step
			label(Vector2(24, y + 22), row.spec.display_name, 17, true)
			label(Vector2(24, y + 45), row.spec.id + " · " + row.spec.kind, 13)
			for spec in specs:
				var side := float(spec[0])
				icon(Rect2(float(spec[3]), y + (60.0 - side) * 0.5, side, side), row.texture, float(spec[1]), bool(spec[2]))
		label(Vector2(24, 717), "현재 UiSkin/slot 스냅샷 · 선형 필터/알파 경계 크롭 · p=그림 여백 · 게임 미반입", 12)

	func _draw_revisions() -> void:
		label(Vector2(24, 59), "보완4의 같은 슬롯 비교 · 원본10의 나머지6장은 이 화면에 없음", 15)
		for heading in [["before128", 237], ["after128", 415], ["before30", 596], ["after30", 688], ["before48/p3", 802], ["after48/p3", 915], ["before60/p5", 1020], ["after60/p5", 1143]]:
			label(Vector2(float(heading[1]), 82), String(heading[0]), 12, true)
		for i in REVISED.size():
			var uid: String = REVISED[i]
			var row: Dictionary = {}
			for candidate in rows:
				if candidate.spec.id == uid: row = candidate
			assert(not row.is_empty())
			var y: float = 96.0 + i * 145.0
			label(Vector2(24, y + 40), row.spec.display_name, 18, true)
			label(Vector2(24, y + 64), uid, 13)
			for setting in [[128, 0.0, 239.0, 418.0], [30, 3.0, 606.0, 697.0], [48, 3.0, 818.0, 928.0], [60, 5.0, 1032.0, 1152.0]]:
				var side: float = float(setting[0])
				var top: float = y + (128.0 - side) * 0.5
				icon(Rect2(float(setting[2]), top, side, side), before[uid], float(setting[1]), true)
				icon(Rect2(float(setting[3]), top, side, side), row.texture, float(setting[1]), true)
		label(Vector2(24, 705), "before=round1 · after=revision1 · 4보완을 후보로 선택 · 원본14 모두 보존 · 실제 신규 반입 0", 14)

var pack_root := ""
var out_dir := ""
var mode := "overview"
var verify_only := false

func _initialize() -> void:
	_launch.call_deferred()

func _texture(path: String, virtual_path: String) -> ImageTexture:
	var raw := Image.load_from_file(path)
	assert(raw != null and raw.get_size() == Vector2i(128, 128), "Missing/invalid icon: " + path)
	var texture := ImageTexture.create_from_image(raw)
	texture.take_over_path("res://assets/sprites/ui/icons_a/qa498/" + virtual_path + ".png")
	return texture

func _launch() -> void:
	await process_frame
	pack_root = ProjectSettings.globalize_path("res://..").simplify_path()
	out_dir = pack_root.path_join("../../../reports/498/native_qa").simplify_path()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
		if arg.begins_with("--out="): out_dir = arg.trim_prefix("--out=")
		if arg == "--verify-only": verify_only = true
	assert(mode in MODES, "Unknown mode")
	assert(ProjectSettings.get_setting("application/config/name") == "Joseon Hunters Icon QA 498")
	assert(not OS.get_user_data_dir().replace("\\", "/").ends_with("Joseon Hunters"))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.card == 498 and manifest.candidates.size() == 10 and manifest.originals.size() == 14)
	assert(manifest.game_intake_count == 0 and not manifest.runtime_connected)
	var plate := Plate.new()
	var system_font := SystemFont.new()
	system_font.font_names = PackedStringArray(["Malgun Gothic", "Noto Sans CJK KR", "sans-serif"])
	plate.font = system_font
	plate.mode = mode
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	for spec in manifest.existing_approved + manifest.candidates:
		var uid: String = spec.id
		var texture := _texture(pack_root.path_join(spec.game_path), uid)
		plate.rows.append({"spec": spec, "texture": texture})
	for uid in REVISED:
		plate.before[uid] = _texture(pack_root.path_join("qa/revision_before/%s.png" % uid), "before_" + uid)
	assert(plate.rows.size() == 13 and plate.before.size() == 4)
	if verify_only:
		print("GODOT_498_VERIFY_PASS originals14/candidates10/approved3/revision4/RGBA128/intake0/isolated_userdir=", OS.get_user_data_dir())
		plate.free()
		quit(0)
		return
	assert(DisplayServer.get_name() != "headless", "Native capture requires window mode; use --verify-only for headless")
	assert(DirAccess.make_dir_recursive_absolute(out_dir) == OK)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = Vector2i(1280, 720)
	root.title = "#498 skill icon candidates — native QA " + mode
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	var capture := root.get_texture().get_image()
	assert(capture.get_size() == Vector2i(1280, 720))
	var output := out_dir.path_join("native_%s.png" % mode)
	assert(capture.save_png(output) == OK)
	print("GODOT_498_CAPTURE_PASS mode=", mode, " width1280/height720/UiSkinSnapshot/linear/intake0 output=", output)
	quit(0)
