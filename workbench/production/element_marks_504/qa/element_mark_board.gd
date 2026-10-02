extends SceneTree
## #504 source QA only: selected PNG -> ImageTexture -> native linear sampling.
## No game nodes, glyph replacement, in-helper alpha cleanup, crop, or source-file write.

const IDS := ["fire", "cold", "lightning", "sal", "soul"]
const SIZES := [12, 14, 16, 18, 24]
const TINTS := {
	"fire": Color(1.0, 0.49, 0.29),
	"cold": Color(0.51, 0.81, 1.0),
	"lightning": Color(0.94, 0.83, 0.38),
	"sal": Color(0.7, 0.48, 0.82),
	"soul": Color(0.55, 0.92, 0.75),
}
const GRAY := Color(0.63, 0.65, 0.68)
const MODES := ["color", "gray", "white"]

class Board extends Node2D:
	var images: Array[Dictionary] = []
	var mode := "color"
	var source_round := "original"
	var body: Font
	const DARK := Color(0.05, 0.045, 0.06)
	const SOIL := Color(0.62, 0.56, 0.46)
	const TEXT := Color(0.90, 0.87, 0.80)

	func label(pos: Vector2, value: String, size: int = 15) -> void:
		draw_string(body, pos, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, TEXT)

	func tint(id: String) -> Color:
		if mode == "gray":
			return GRAY
		if mode == "white":
			return Color.WHITE
		return TINTS[id]

	func pair(x: float, y: float, side: int, texture: Texture2D, color: Color, height: float) -> void:
		for j in range(2):
			var block := Rect2(x + j * 108.0, y, 104.0, height)
			draw_rect(block, DARK if j == 0 else SOIL)
			var at := block.get_center() - Vector2.ONE * float(side) * 0.5
			draw_texture_rect(texture, Rect2(at, Vector2.ONE * side), false, color)

	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 800), Color(0.08, 0.07, 0.09))
		label(Vector2(24, 34), "#504 ELEMENT MARKS | " + source_round.to_upper() + " | " + mode.to_upper() + " | SOURCE QA - NOT GAME INTEGRATION", 19)
		label(Vector2(24, 63), "Selected 1024 RGBA -> ImageTexture. Native linear filter. No in-helper crop, alpha cleanup, or shape edit.", 15)
		label(Vector2(24, 89), "Each pair: dark UI (left) / representative light-soil swatch (right). Whole PNG canvas fitted at the stated size.", 15)
		label(Vector2(24, 122), "80 px context row; source fringe and any glow remain visible.", 15)
		for i in images.size():
			var entry := images[i]
			var x := 80.0 + i * 238.0
			label(Vector2(x, 148), String(entry.id).to_upper(), 18)
			pair(x, 158.0, 80, entry.texture, tint(entry.id), 126.0)
		label(Vector2(24, 315), "Actual-size rows: compare silhouettes before reading the element color.", 15)
		for k in SIZES.size():
			var y := 337.0 + k * 74.0
			label(Vector2(16, y + 38.0), "%d px" % SIZES[k], 15)
			for i in images.size():
				var entry := images[i]
				pair(80.0 + i * 238.0, y, SIZES[k], entry.texture, tint(entry.id), 66.0)
		label(Vector2(24, 744), "WHITE = equal hue; GRAY = existing resisted tint; COLOR = current ElementMarks palette. PNG RGB is multiplied as supplied.", 14)
		label(Vector2(24, 772), "No Label3D outline, combat punch, weak-target scaling, HUD binding, or tooltip binding is claimed by this board.", 14)

var source_dir := ""
var out_dir := ""
var requested_mode := "all"
var requested_round := "original"

func _initialize() -> void:
	call_deferred("_launch")

func _fail(message: String) -> void:
	push_error(message)
	quit(2)

func _launch() -> void:
	await process_frame
	var qa_dir := ProjectSettings.globalize_path("res://").trim_suffix("/")
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--round="):
			requested_round = arg.trim_prefix("--round=")
		elif arg.begins_with("--sources="):
			source_dir = arg.trim_prefix("--sources=")
		elif arg.begins_with("--out="):
			out_dir = arg.trim_prefix("--out=")
		elif arg.begins_with("--mode="):
			requested_mode = arg.trim_prefix("--mode=")
	if requested_round != "original" and requested_round != "revision1":
		_fail("Unknown --round. Use original or revision1.")
		return
	var source_suffix := "_v2" if requested_round == "revision1" else ""
	var report_folder := "2026-10-02_revision1" if requested_round == "revision1" else "2026-10-02_round1"
	if source_dir.is_empty():
		source_dir = qa_dir.path_join("../../../../reports/504/" + report_folder).simplify_path()
	if out_dir.is_empty():
		out_dir = qa_dir.path_join("native/" + requested_round)
	if DisplayServer.get_name() == "headless":
		_fail("#504 capture requires a native rendering display; the headless dummy display is unsupported.")
		return
	if requested_mode != "all" and not MODES.has(requested_mode):
		_fail("Unknown --mode. Use all, color, gray, or white.")
		return
	if DirAccess.make_dir_recursive_absolute(out_dir) != OK:
		_fail("Cannot create output directory: " + out_dir)
		return
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = Vector2i(1280, 800)
	root.title = "#504 Source Size QA - Not Game Integration"
	var board := Board.new()
	board.body = ThemeDB.fallback_font
	board.source_round = requested_round
	board.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	for id in IDS:
		var path := source_dir.path_join(id + source_suffix + ".png")
		var raw := Image.load_from_file(path)
		if raw == null or raw.is_empty() or raw.get_size() != Vector2i(1024, 1024):
			_fail("Missing or invalid selected 1024 PNG: " + path)
			return
		if raw.get_format() != Image.FORMAT_RGBA8 or not raw.get_used_rect().has_area():
			_fail("RGBA8 with a nonempty alpha footprint is required: " + path)
			return
		board.images.append({"id": id, "texture": ImageTexture.create_from_image(raw)})
	root.add_child(board)
	var run_modes: Array = MODES if requested_mode == "all" else [requested_mode]
	var outputs: Array[String] = []
	for mode in run_modes:
		board.mode = mode
		board.queue_redraw()
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		var frame := root.get_texture().get_image()
		if frame == null or frame.is_empty() or frame.get_size() != Vector2i(1280, 800):
			_fail("Native viewport capture is empty or does not match 1280x800.")
			return
		var output := out_dir.path_join("godot_504_" + mode + ".png")
		if frame.save_png(output) != OK:
			_fail("Cannot save native source QA capture: " + output)
			return
		outputs.append(output)
		print("SOURCE_QA_CAPTURE #504 round=", requested_round, " mode=", mode, " size=1280x800 candidates=5 output=", output)
	var receipt := {
		"card": 504,
		"scope": "standalone source-concept size/color QA, not game integration",
		"round": requested_round,
		"source_filename_suffix": source_suffix,
		"renderer": RenderingServer.get_current_rendering_method(),
		"display": DisplayServer.get_name(),
		"source_directory": source_dir,
		"original_ids": IDS,
		"sizes_px": SIZES,
		"modes": run_modes,
		"outputs": outputs,
		"acceptance": "not determined by capture; requires visual review",
	}
	var log_file := FileAccess.open(out_dir.path_join("native_capture.json"), FileAccess.WRITE)
	if log_file == null:
		_fail("Cannot write native capture receipt.")
		return
	log_file.store_string(JSON.stringify(receipt, "\t") + "\n")
	log_file.close()
	quit(0)
