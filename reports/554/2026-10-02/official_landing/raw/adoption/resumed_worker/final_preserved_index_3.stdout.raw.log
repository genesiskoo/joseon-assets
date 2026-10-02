extends Node
## #554 검수 전용. game main, GameState.inventory, SaveSystem, 경제 서비스에 연결하지 않는다.
const UI_SCENE = preload("res://ui/item_service_preview.tscn")
const UI_SCRIPT = preload("res://ui/item_service_preview.gd")
const FONTS = preload("res://ui/ui_fonts.gd")
const SAMPLE_IDS := ["paeraengi", "iron_sword", "cotton_robe", "mukham", "jade_charm", "silver_ring", "cotton_belt", "leather_shoes"]
var _ui: Control
var _banner: Label
var _request_label: Label
var _shots: String = ""
var _kind: String = "stash"
var _requested_size := Vector2i(1280, 720)


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--kind="):
			_kind = arg.trim_prefix("--kind=")
		elif arg.begins_with("--shots="):
			_shots = arg.trim_prefix("--shots=")
		elif arg.begins_with("--size="):
			var pieces: PackedStringArray = arg.trim_prefix("--size=").split("x")
			if pieces.size() == 2 and pieces[0].is_valid_int() and pieces[1].is_valid_int():
				_requested_size = Vector2i(pieces[0].to_int(), pieces[1].to_int())
	if _kind not in UI_SCRIPT.KINDS or _requested_size not in [Vector2i(1280, 720), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
		push_error("ITEM_SERVICE_VIEWER: --kind=stash|cube|gamble, --size=1280x720|1920x1080|2560x1440 필요")
		get_tree().quit(1)
		return
	if not _shots.is_empty() and DisplayServer.get_name() == "headless":
		push_error("ITEM_SERVICE_VIEWER: --shots는 실제 렌더 창에서만 지원")
		get_tree().quit(1)
		return
	get_window().title = "조선헌터스 · 아이템 서비스 독립 UI 검수판 #554"
	get_window().mode = Window.MODE_WINDOWED
	get_window().size = _requested_size
	get_window().content_scale_size = Vector2i(1280, 720)
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var back := ColorRect.new()
	back.color = Color(0.035, 0.037, 0.035)
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(back)
	_ui = UI_SCENE.instantiate()
	_ui.show_bag_preview = true
	_ui.bag_preview = _sample_bag()
	add_child(_ui)
	_ui.close_requested.connect(func() -> void: get_tree().quit())
	_ui.recipe_selected.connect(func(id: StringName) -> void: _request_label.text = "목록 선택: %s · 거래/조합 실행 없음" % id)
	_ui.grid_action_requested.connect(func(_kind_value: StringName, _id: String, _cell: Vector2i, _button: int, _revision: int) -> void: _request_label.text = "칸 요청만 기록 · 원본 무변경")
	_ui.gold_action_requested.connect(func(_operation: StringName, _amount: int, _revision: int) -> void: _request_label.text = "엽전 요청만 기록 · 경제 미연결")
	_ui.transmute_requested.connect(func(_id: StringName, _revision: int) -> void: _request_label.text = "조합 요청만 기록 · 재료 소비 없음")
	_ui.gamble_requested.connect(func(_slot: StringName, _quote: String, _revision: int) -> void: _request_label.text = "구매 요청만 기록 · 상품 생성 없음")
	_banner = Label.new()
	_banner.text = "독립 UI 검수판 · 거래/저장 미연결    1 반닫이 / 2 호리병 / 3 보부상 / Esc 종료"
	_banner.add_theme_font_override("font", FONTS.body())
	_banner.add_theme_font_size_override("font_size", 14)
	_banner.modulate = Color(0.78, 0.72, 0.57)
	_banner.position = Vector2(16, 6)
	_banner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_banner)
	_request_label = Label.new()
	_request_label.text = "기존 ItemDb · 로컬 Inventory의 읽기 표본입니다."
	_request_label.add_theme_font_size_override("font_size", 14)
	_request_label.position = Vector2(448, 646)
	_request_label.size = Vector2(384, 60)
	_request_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_request_label.modulate = Color(0.68, 0.66, 0.60)
	_request_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_request_label)
	_show_kind(_kind)
	if not _shots.is_empty():
		_capture.call_deferred()


func _item(id: String, count: int = 1) -> ItemInstance:
	return ItemInstance.create(ItemDb.get_def(id), count)


func _sample_bag() -> Inventory:
	var bag := Inventory.new()
	bag.place(_item("hp_potion", 3), Vector2i(0, 0))
	bag.place(_item("mp_potion", 3), Vector2i(1, 0))
	bag.place(_item("hp_potion_2", 2), Vector2i(2, 0))
	bag.place(_item("mp_potion_2", 2), Vector2i(3, 0))
	bag.place(_item("ident_scroll", 4), Vector2i(5, 0))
	bag.place(_item("town_portal", 2), Vector2i(6, 0))
	bag.place(_item("talisman_fire", 3), Vector2i(8, 0))
	bag.place(_item("long_sword"), Vector2i(0, 1))
	bag.place(_item("leather_shoes"), Vector2i(2, 1))
	bag.place(_item("goehwangji", 5), Vector2i(5, 2))
	bag.equipment.weapon = _item("iron_sword")
	bag.equipment.armor = _item("cotton_robe")
	bag.equipment.head = _item("paeraengi")
	bag.equipment.offhand = _item("mukham")
	bag.equipment.belt = _item("cotton_belt")
	bag.equipment.boots = _item("straw_shoes")
	return bag


func _show_kind(kind_value: String) -> void:
	_kind = kind_value
	var s: Dictionary = {"kind": _kind, "revision": 0, "available": false, "items": [],
		"carried_gold": null, "stored_gold": null, "unavailable_reason": "서비스 미연결 · 거래/저장 없음"}
	if _kind == "stash":
		s.items = [{"instance_id": "preview-robe", "item": _item("quilted_robe"), "cell": Vector2i(0, 0)},
			{"instance_id": "preview-sword", "item": _item("hwando"), "cell": Vector2i(3, 0)},
			{"instance_id": "preview-head", "item": _item("satgat"), "cell": Vector2i(5, 0)},
			{"instance_id": "preview-boots", "item": _item("leather_shoes"), "cell": Vector2i(0, 4)},
			{"instance_id": "preview-fire", "item": _item("talisman_fire", 5), "cell": Vector2i(3, 4)},
			{"instance_id": "preview-paper", "item": _item("goehwangji", 5), "cell": Vector2i(5, 4)}]
	elif _kind == "cube":
		s.items = [{"instance_id": "preview-paper", "item": _item("goehwangji", 2), "cell": Vector2i(0, 0)},
			{"instance_id": "preview-ink", "item": _item("gyeongmyeonjusa", 1), "cell": Vector2i(2, 0)}]
		s.recipes = UI_SCRIPT.RECIPE_CATALOG.duplicate(true)
		for recipe in s.recipes:
			recipe.enabled = false
			recipe.disabled_reason = "조합 서비스 미연결 · 실행 잠금"
		s.transmute_enabled = false
	else:
		s.offers = []
		for i in UI_SCRIPT.SLOTS.size():
			s.offers.append({"slot": UI_SCRIPT.SLOTS[i], "base": ItemDb.get_def(SAMPLE_IDS[i]), "quote_id": "", "price": null,
				"enabled": false, "disabled_reason": "견적 대기 · 거래 미연결"})
	if not _ui.set_read_model(s):
		push_error("ITEM_SERVICE_VIEWER: 실제 정의 표본 모델 거절")
		get_tree().quit(1)


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var keys := [KEY_1, KEY_2, KEY_3]
		var i: int = keys.find(event.keycode)
		if i >= 0:
			_show_kind(UI_SCRIPT.KINDS[i])
			get_viewport().set_input_as_handled()


func _capture() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var out: String = ProjectSettings.globalize_path(_shots)
	var err: int = DirAccess.make_dir_recursive_absolute(out)
	if err != OK:
		push_error("ITEM_SERVICE_VIEWER: 촬영 폴더 실패 %d %s" % [err, out])
		get_tree().quit(1)
		return
	var path: String = out.path_join("%s_%dx%d.png" % [_kind, _requested_size.x, _requested_size.y])
	var img: Image = get_viewport().get_texture().get_image()
	err = img.save_png(path)
	print("ITEM_SERVICE_VIEWER kind=%s requested=%s pixels=%s canvas=%s save=%d path=%s" % [_kind, _requested_size, img.get_size(), get_viewport().get_visible_rect().size, err, path])
	get_tree().quit(0 if err == OK else 1)
