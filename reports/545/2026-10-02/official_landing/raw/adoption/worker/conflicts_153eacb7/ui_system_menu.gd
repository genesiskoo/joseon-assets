extends PanelUi
## Esc 메뉴·설정. 게임 정지는 SceneTree 하나로, 메뉴와 UI 소리만 예외 (#156).
<<<<<<< HEAD
const BUILD_INFO = preload("res://core/build_info.gd")
=======
signal title_settings_closed
var _from_title := false

>>>>>>> 153eacb7 (feat(#550): add safe character profiles and title menus)
const MENU_SIZE := Vector2(456, 400)
const SETTINGS_SIZE := Vector2(456, 550)
const BUTTON_SIZE := Vector2(300, 42)
const BUS_LABELS: Array[String] = ["전체", "음악", "효과음", "UI"]
var main: Node
var settings_open := false:
	set(value):
		settings_open = value
		if _version_label != null:
			_layout_version_label()
var _drag_volume := -1
var _error := ""
var _version_label: Label


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	z_index = 220
	visible = false
	closable_by_esc = false
	super._ready()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_version_label = Label.new()
	_version_label.name = "BuildVersion"
	_version_label.text = BUILD_INFO.label()
	_version_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_version_label.add_theme_font_override("font", _font)
	_version_label.add_theme_font_size_override("font_size", FONT_MIN)
	_version_label.add_theme_color_override("font_color", UiSkin.TEXT_DIM)
	add_child(_version_label)
	_version_label.minimum_size_changed.connect(_layout_version_label)
	get_viewport().size_changed.connect(_layout_version_label)
	_layout_version_label()


func _layout_version_label() -> void:
	var extent := _version_label.get_minimum_size().ceil()
	_version_label.size = extent
	_version_label.position = (menu_rect().end - Vector2(24, 10) - extent).round()


func panel_rect() -> Rect2:
	return Rect2(Vector2.ZERO, get_viewport_rect().size)


func menu_rect() -> Rect2:
	var size := SETTINGS_SIZE if settings_open else MENU_SIZE
	return Rect2((get_viewport_rect().size - size) * 0.5, size)


func button_rect(i: int) -> Rect2:
	var r := menu_rect()
	return Rect2(Vector2(r.get_center().x - BUTTON_SIZE.x * 0.5, r.position.y + 110 + i * 58), BUTTON_SIZE)


func volume_rect(i: int) -> Rect2:
	return Rect2(menu_rect().position + Vector2(122, 104 + i * 60), Vector2(228, 28))


func display_rect() -> Rect2:
	return Rect2(menu_rect().position + Vector2(174, 346), Vector2(202, 38))


func blood_rect() -> Rect2:
	return Rect2(menu_rect().position + Vector2(174, 400), Vector2(202, 38))


func back_rect() -> Rect2:
	return Rect2(menu_rect().position + Vector2(128, 454), Vector2(200, 38))


func _update_capture() -> void:
	GameState.set_ui_capture(name, visible)


## #550: 타이틀의 설정은 같은 슬라이더·설정 저장을 쓴다. 닫을 때 게임을 재개하지 않는다.
func open_title_settings() -> void:
	if main == null or not main.title_ui.visible:
		return
	_from_title = true
	settings_open = true
	_error = ""
	z_index = 260
	super.set_open(true)
	main.pause_world(true)


func set_open(open: bool) -> void:
	if open == visible:
		return
	if not open and _from_title:
		_drag_volume = -1
		_from_title = false
		settings_open = false
		super.set_open(false)
		z_index = 220
		GameState.mark_ui_click()
		title_settings_closed.emit()
		return
	if open:
		if main == null or not main._started or main._dying or main.title_ui.visible:
			return
		settings_open = false
		_error = ""
		main.player.menu_pause_started()
		GameState.hover = null
		super.set_open(true)
		main.pause_world(true)
	else:
		_drag_volume = -1
		settings_open = false
		super.set_open(false)
		main.player.menu_pause_ended()
		GameState.mark_ui_click()
		main.pause_world(false)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and not event.is_echo() and not visible:
		if PanelUi.esc_closed_frame == Engine.get_process_frames():
			return
		set_open(true)
		if visible:
			get_viewport().set_input_as_handled()


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_cancel") and not event.is_echo():
		if _from_title:
			set_open(false)
		elif settings_open:
			settings_open = false
			_drag_volume = -1
			_error = ""
			queue_redraw()
		else:
			set_open(false)
		get_viewport().set_input_as_handled()
		return
	if event is InputEventMouseMotion:
		_mouse = event.position
		if _drag_volume >= 0:
			_change_volume(_drag_volume, _mouse.x)
		queue_redraw()
	elif event is InputEventMouseButton:
		_mouse = event.position
		if event.button_index == MOUSE_BUTTON_LEFT:
			GameState.mark_ui_click()
			if event.pressed:
				_on_click(_mouse, event.button_index)
			else:
				_drag_volume = -1
		queue_redraw()
	# 다른 키/클릭도 월드 입력으로 남기지 않는다.
	get_viewport().set_input_as_handled()


func _change_volume(i: int, x: float) -> void:
	var r := volume_rect(i)
	var amount := snappedf(clampf((x - r.position.x) / r.size.x, 0.0, 1.0), 0.01)
	if not GameSettings.set_volume(GameSettings.BUSES[i], amount):
		_error = GameSettings.last_error
	else:
		_error = ""


func _on_click(pos: Vector2, button: int) -> void:
	if button != MOUSE_BUTTON_LEFT:
		return
	if settings_open:
		for i in GameSettings.BUSES.size():
			if volume_rect(i).grow(8).has_point(pos):
				_drag_volume = i
				_change_volume(i, pos.x)
				return
		if display_rect().has_point(pos):
			if not GameSettings.set_fullscreen(not GameSettings.fullscreen):
				_error = GameSettings.last_error
			Audio.play_ui("ui_open")
		elif blood_rect().has_point(pos):
			if not GameSettings.set_blood_fx(not GameSettings.blood_fx):
				_error = GameSettings.last_error
			Audio.play_ui("ui_open")
		elif back_rect().has_point(pos):
			if _from_title:
				set_open(false)
				return
			settings_open = false
			_error = ""
			Audio.play_ui("ui_close")
		return
	if button_rect(0).has_point(pos):
		set_open(false)
	elif button_rect(1).has_point(pos):
		settings_open = true
		_error = ""
		Audio.play_ui("ui_open")
	elif button_rect(2).has_point(pos) or button_rect(3).has_point(pos):
		if not SaveSystem.save_now("system menu"):
			_error = SaveSystem.last_error
			return
		if button_rect(2).has_point(pos):
			main.show_title()
		else:
			get_tree().quit()


func _draw() -> void:
	if not visible:
		return
	UiSkin.screen_backdrop(self, panel_rect(), 0.78)
	var r := menu_rect()
	UiSkin.panel(self, r)
	var label := "설정" if settings_open else "잠시 쉬어 가기"
	var tw := _title_font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 26).x
	draw_string(_title_font, Vector2(r.get_center().x - tw * 0.5, r.position.y + 57).round(), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(0.95, 0.88, 0.7))
	if settings_open:
		for i in GameSettings.BUSES.size():
			var vr := volume_rect(i)
			var value: float = GameSettings.volume(GameSettings.BUSES[i])
			text(Vector2(r.position.x + 42, vr.get_center().y + 5), BUS_LABELS[i], 16)
			var track := Rect2(vr.position + Vector2(0, 10), Vector2(vr.size.x, 8))
			draw_bar(track, value, Color(0.65, 0.53, 0.31), Color(0.075, 0.075, 0.075))
			var knob := Rect2(Vector2(vr.position.x + value * vr.size.x - 5, vr.position.y + 4), Vector2(10, 20))
			draw_rect(knob, Color(0.94, 0.85, 0.61))
			text(Vector2(vr.end.x + 18, vr.get_center().y + 5), "%d%%" % roundi(value * 100), 15)
		text(r.position + Vector2(42, 371), "화면", 16)
		draw_button(display_rect(), "전체 화면" if GameSettings.fullscreen else "창 모드", true)
		text(r.position + Vector2(42, 425), "피 표현", 16)
		draw_button(blood_rect(), "켬" if GameSettings.blood_fx else "끔", true)
		draw_button(back_rect(), "돌아가기", true)
	else:
		var labels := ["게임으로 돌아가기", "설정", "저장 후 타이틀", "저장 후 종료"]
		for i in labels.size():
			draw_button(button_rect(i), labels[i], true)
	var hint := "설정은 자동 저장됩니다" if settings_open else "Esc  게임으로 돌아가기"
	if _error != "":
		hint = _error
	text(r.position + Vector2(48, r.size.y - 36), fit_text(hint, r.size.x - 96, FONT_MIN), FONT_MIN, Color(1.0, 0.65, 0.42) if _error != "" else Color(0.7, 0.65, 0.55))
