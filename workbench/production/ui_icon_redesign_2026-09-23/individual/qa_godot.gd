extends Node2D
## #393: 실제 Godot 4.7 CanvasItem 렌더러에서 30/48/60px와 다칸 소지품을 촬영한다.

const SIZES := [30, 48, 60]
const SKILLS := ["slash", "lunge", "whirlwind", "fire_talisman", "frost_talisman", "power_shield"]
const ITEMS := [
	["hwando", 1, 3], ["cotton_dopo", 2, 3], ["leather_shoes", 2, 2],
	["paeraengi", 2, 2], ["mukham", 1, 2], ["cotton_belt", 2, 1],
	["silver_ring", 1, 1], ["jade_charm", 1, 1], ["hp_potion", 1, 1],
	["mp_potion", 1, 1], ["talisman_fire", 1, 1],
]
const BACK := Color("241e1a")
const SLOT := Color("171513")
const RIM := Color("655443")
const TEXT := Color("e5d5bd")

var _kind := "skills"
var _font: Font
var _height := 670
var _textures: Dictionary = {}


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--kind=items":
			_kind = "items"
	_font = ThemeDB.fallback_font
	for name in SKILLS:
		_textures[name] = load("res://game/skills/%s.png" % name)
	for spec in ITEMS:
		_textures[spec[0]] = load("res://game/items/%s.png" % spec[0])
	if _kind == "items":
		_height = 1550
	get_window().size = Vector2i(880, _height)
	queue_redraw()
	call_deferred("_capture")


func _draw() -> void:
	draw_rect(Rect2(0, 0, 880, _height), BACK)
	draw_string(_font, Vector2(18, 31), "#393 Godot 4.7 — %s" % _kind, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, TEXT)
	for column in SIZES.size():
		draw_string(_font, Vector2(185 + column * 217, 55), "%dpx" % SIZES[column], HORIZONTAL_ALIGNMENT_LEFT, -1, 15, TEXT)
	if _kind == "skills":
		_draw_skills()
	else:
		_draw_items()


func _draw_skills() -> void:
	for row in SKILLS.size():
		var y := 73.0 + row * 90.0
		draw_string(_font, Vector2(18, y + 24), SKILLS[row], HORIZONTAL_ALIGNMENT_LEFT, 145, 16, TEXT)
		var texture := _textures[SKILLS[row]] as Texture2D
		for column in SIZES.size():
			var size: int = SIZES[column]
			var r := Rect2(180 + column * 217, y, size, size)
			draw_rect(r.grow(2), SLOT)
			draw_rect(r.grow(2), RIM, false, 1.0)
			draw_texture_rect(texture, r, false)


func _draw_items() -> void:
	var y := 72.0
	for spec in ITEMS:
		var name: String = spec[0]
		var cells_x: int = spec[1]
		var cells_y: int = spec[2]
		draw_string(_font, Vector2(18, y + 24), "%s  %d×%d" % [name, cells_x, cells_y], HORIZONTAL_ALIGNMENT_LEFT, 150, 14, TEXT)
		var texture := _textures[name] as Texture2D
		for column in SIZES.size():
			var size: int = SIZES[column]
			var r := Rect2(180 + column * 217, y, cells_x * size, cells_y * size)
			draw_rect(r, SLOT)
			draw_rect(r, RIM, false, 1.0)
			draw_texture_rect(texture, r, false)
		y += cells_y * 60 + 28


func _capture() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().create_timer(0.25).timeout
	var out := "res://qa/godot_%s_30_48_60.png" % _kind
	var err := get_viewport().get_texture().get_image().save_png(out)
	print("GODOT_ICON_QA %s %s" % ["PASS" if err == OK else "FAIL", ProjectSettings.globalize_path(out)])
	get_tree().quit(0 if err == OK else 1)
