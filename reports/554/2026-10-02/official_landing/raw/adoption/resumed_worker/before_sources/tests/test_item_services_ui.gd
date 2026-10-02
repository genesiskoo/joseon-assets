extends SceneTree
## #554: 실제 Control의 읽기 모델·입력 계약. 경제/저장 성공을 흉내 내지 않는다.
const UI_SCENE = preload("res://ui/item_service_preview.tscn")
const UI_SCRIPT = preload("res://ui/item_service_preview.gd")
const BASE_IDS := ["paeraengi", "iron_sword", "cotton_robe", "mukham", "jade_charm", "silver_ring", "cotton_belt", "leather_shoes"]
var _n: int = 0
var _fails: Array[String] = []
var _ui: Control
var _gold_requests: Array = []
var _grid_requests: Array = []
var _recipes: Array = []
var _transmutes: Array = []
var _gambles: Array = []
var _closes: int = 0


func _check(condition: bool, title: String) -> void:
	_n += 1
	if not condition:
		_fails.append(title)
		push_error("FAIL: " + title)


func _init() -> void:
	_run.call_deferred()


func _snapshot(kind: String, available: bool = true) -> Dictionary:
	var s: Dictionary = {"kind": kind, "revision": 41, "available": available, "items": [],
		"carried_gold": 2000, "stored_gold": 3000, "unavailable_reason": "시험용 읽기 모델"}
	if kind == "cube":
		s.recipes = UI_SCRIPT.RECIPE_CATALOG.duplicate(true)
		for recipe in s.recipes:
			recipe.enabled = true
			recipe.disabled_reason = ""
		s.transmute_enabled = true
	elif kind == "gamble":
		s.offers = []
		for i in 8:
			s.offers.append({"slot": UI_SCRIPT.SLOTS[i], "base": ItemDb.get_def(BASE_IDS[i]), "quote_id": "unit-quote-%d" % i,
				"price": 200, "enabled": true, "disabled_reason": ""})
	return s


func _click(point: Vector2, button: int = MOUSE_BUTTON_LEFT) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	Input.parse_input_event(motion)
	await process_frame
	var press := InputEventMouseButton.new()
	press.position = point
	press.global_position = point
	press.button_index = button
	press.pressed = true
	Input.parse_input_event(press)
	await process_frame
	press = press.duplicate()
	press.pressed = false
	Input.parse_input_event(press)
	await process_frame


func _key(key: Key) -> void:
	var press := InputEventKey.new()
	press.keycode = key
	press.physical_keycode = key
	press.pressed = true
	Input.parse_input_event(press)
	await process_frame
	press = press.duplicate()
	press.pressed = false
	Input.parse_input_event(press)
	await process_frame


func _run() -> void:
	await process_frame
	root.content_scale_size = Vector2i(1280, 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280, 720)
	var bag := Inventory.new()
	bag.place(ItemInstance.create(ItemDb.get_def("hp_potion"), 3), Vector2i.ZERO)
	var original_inventory: Dictionary = bag.to_dict()
	var global_state: Node = root.get_node_or_null("GameState")
	var save_system: Node = root.get_node_or_null("SaveSystem")
	var original_global: Dictionary = global_state.get("inventory").to_dict() if global_state != null else {}
	var save_path: String = String(save_system.get("save_path")) if save_system != null else ""
	var original_save_exists: bool = not save_path.is_empty() and FileAccess.file_exists(save_path)
	var original_save: String = FileAccess.get_sha256(save_path) if original_save_exists else ""
	_ui = UI_SCENE.instantiate()
	_ui.bag_preview = bag
	root.add_child(_ui)
	_ui.gold_action_requested.connect(func(operation: StringName, amount: int, revision: int) -> void: _gold_requests.append([operation, amount, revision]))
	_ui.grid_action_requested.connect(func(kind: StringName, id: String, cell: Vector2i, button: int, revision: int) -> void: _grid_requests.append([kind, id, cell, button, revision]))
	_ui.recipe_selected.connect(func(id: StringName) -> void: _recipes.append(id))
	_ui.transmute_requested.connect(func(id: StringName, revision: int) -> void: _transmutes.append([id, revision]))
	_ui.gamble_requested.connect(func(slot: StringName, quote: String, revision: int) -> void: _gambles.append([slot, quote, revision]))
	_ui.close_requested.connect(func() -> void: _closes += 1)
	await process_frame
	_layout_checks()
	await _stash_checks()
	await _cube_checks()
	await _gamble_checks()
	_invalid_models()
	_check(bag.to_dict() == original_inventory, "서비스 입력 뒤 실제 로컬 Inventory 가방/엽전 무변경")
	if global_state != null:
		_check(global_state.get("inventory").to_dict() == original_global, "autoload가 있는 실행에서도 GameState 가방/엽전 무변경")
	if save_system != null:
		_check(FileAccess.file_exists(save_path) == original_save_exists, "세이브 파일 유무 무변경")
	if original_save_exists:
		_check(FileAccess.get_sha256(save_path) == original_save, "기존 세이브 SHA 무변경")
	print("ITEM_SERVICES_UI_BOUNDARY game_state_present=%s save_system_present=%s existing_save=%s" % [global_state != null, save_system != null, original_save_exists])
	_ui.queue_free()
	await process_frame
	print("ITEM_SERVICES_UI_TEST checks=%d fails=%d %s" % [_n, _fails.size(), "PASS" if _fails.is_empty() else "FAIL"])
	quit(0 if _fails.is_empty() else 1)


func _layout_checks() -> void:
	for size in [Vector2(1280, 720), Vector2(1920, 1080), Vector2(2560, 1440)]:
		var l: Dictionary = UI_SCRIPT.layout_for(size)
		_check(l.panel.position == Vector2(0, 32) and l.panel.size == Vector2(432, size.y - 192), "%s 왼쪽 고정 자리" % size)
		_check(l.bag.position.x == size.x - 432 and not l.panel.intersects(l.bag), "%s 가방과 서비스 비겹침" % size)
		_check(l.stash_grid.size == Vector2(400, 320) and l.panel.encloses(l.stash_grid), "%s 반닫이 80칸이 창 안" % size)
		_check(l.cube_grid.size == Vector2(160, 120) and l.panel.encloses(l.cube_grid), "%s 호리병 12칸이 창 안" % size)
		_check(l.offers.size() == 8, "%s D091 보부상 8부위" % size)
		for card in l.offers:
			_check(l.panel.encloses(card), "%s 보부상 클릭 사각형 창 안" % size)
		for key in ["close", "deposit", "withdraw", "recipe_list", "transmute", "amount_popup", "footer"]:
			_check(l.panel.encloses(l[key]), "%s %s 입력/표시 사각형 창 안" % [size, key])
		_check(not l.deposit.intersects(l.withdraw) and not l.transmute.intersects(l.recipe_list), "%s 실행 버튼 비겹침" % size)
	_check(not _ui._has_point(Vector2(640, 360)), "월드 가운데 포인터를 서비스가 잡지 않음")
	_ui.show_bag_preview = true
	_check(_ui._has_point(Vector2(900, 100)), "독립 검수판에서 가방 읽기 표본 영역만 추가")
	_ui.show_bag_preview = false
	_check(not _ui._has_point(Vector2(900, 100)), "실제 연결 기본 상태는 오른쪽 가방 포인터를 잡지 않음")


func _stash_checks() -> void:
	var item: ItemInstance = ItemInstance.create(ItemDb.get_def("iron_sword"))
	var state: Dictionary = _snapshot("stash")
	state.items = [{"instance_id": "unit-sword", "item": item, "cell": Vector2i(2, 2)}]
	var item_before: Dictionary = item.to_dict()
	_check(_ui.set_read_model(state), "실제 ItemDb 칼 읽기 모델 수용")
	var l: Dictionary = _ui.layout()
	_check(_ui.cell_at(l.stash_grid.position) == Vector2i.ZERO, "왼쪽 위 칸 포함")
	_check(_ui.cell_at(l.stash_grid.end) == Vector2i(-1, -1), "오른쪽 아래 끝 경계 제외")
	await _click(l.stash_grid.position + Vector2(2.5, 3.5) * 40)
	_check(_grid_requests.size() == 1 and _grid_requests[0] == [&"stash", "unit-sword", Vector2i(2, 3), MOUSE_BUTTON_LEFT, 41], "실제 GUI 클릭이 다칸 아이템 ID/칸/revision 전달")
	await _click(l.deposit.get_center())
	_check(_ui.get_node("GoldAmount").visible and _ui.get_node("GoldAmount").has_focus(), "실제 맡기기 클릭이 native LineEdit 열고 포커스")
	for value in ["0", "-1", "2001", "not-a-number", "9223372036854775808"]:
		_ui.get_node("GoldAmount").text = value
		_check(not _ui.confirm_gold(), "금액 %s 요청 거절" % value)
	_check(_gold_requests.is_empty(), "거절된 금액은 거래 요청 0개")
	_ui.get_node("GoldAmount").text = "0250"
	await _click(l.amount_confirm.get_center())
	_check(_gold_requests.size() == 1 and _gold_requests[0] == [&"deposit", 250, 41], "실제 확인 클릭이 금액/revision만 전달")
	_check(state.carried_gold == 2000 and state.stored_gold == 3000 and item.to_dict() == item_before, "입출금/칸 요청 뒤 원본 잔고·아이템 무변경")
	_check(_ui.begin_gold("withdraw"), "찾기 입력 열기")
	_ui.get_node("GoldAmount").text = "1500"
	await _key(KEY_ENTER)
	_check(_gold_requests.size() == 2 and _gold_requests[1] == [&"withdraw", 1500, 41], "native LineEdit Enter는 찾기 금액/revision 전달")
	_check(_ui.begin_gold("withdraw"), "Esc 검사 전 찾기 입력 다시 열기")
	await _key(KEY_ESCAPE)
	_check(not _ui.get_node("GoldAmount").visible and _closes == 0, "금액 창 Esc는 입력만 닫음")
	await _key(KEY_ESCAPE)
	_check(_closes == 1, "다음 Esc는 서비스 닫기 요청")
	_check(_ui.set_read_model(_snapshot("stash", false)) and not _ui.begin_gold("deposit"), "서비스 잠금 때 입출금 불가")
	await _click(l.stash_grid.get_center())
	_check(_grid_requests.size() == 1, "미연결 서비스 칸은 이동 요청 없음")


func _cube_checks() -> void:
	var state: Dictionary = _snapshot("cube")
	_check(_ui.set_read_model(state), "8개 조합 읽기 모델 수용")
	var l: Dictionary = _ui.layout()
	await _click(l.recipe_list.get_center(), MOUSE_BUTTON_WHEEL_DOWN)
	_check(_ui._recipe_offset == 1, "실제 목록 휠 한 행 스크롤")
	await _click(l.recipe_rows[0].get_center())
	_check(_recipes.size() == 1 and _recipes[0] == &"unsocket", "스크롤 뒤 첫 화면행은 조합2 선택")
	await _click(l.recipe_next.get_center())
	_check(_ui._recipe_offset == 2, "목록 아래 방향 버튼 실제 클릭")
	_ui.scroll_recipes(100)
	_check(_ui._recipe_offset == 5, "스크롤 끝은 6~8행")
	await _click(l.recipe_rows[2].get_center())
	_check(_recipes.back() == &"iron_scale_talisman", "끝 목록의 마지막 조합8 클릭")
	await _click(l.transmute.get_center())
	_check(_transmutes == [[&"iron_scale_talisman", 41]], "흔들기는 선택 조합 ID/revision 전달")
	var count: int = _recipes.size()
	await _click(Vector2(l.recipe_list.position.x + 20, l.recipe_list.position.y - 1))
	_check(_recipes.size() == count, "가려진 목록행/경계 밖 클릭 차단")
	state.transmute_enabled = false
	_check(_ui.set_read_model(state), "조건 미충족 조합 모델 수용")
	await _click(l.transmute.get_center())
	_check(_transmutes.size() == 1, "미충족 흔들기는 요청 없음")
	_check(state.recipes.size() == 8 and state.recipes[7].id == "iron_scale_talisman", "선택/스크롤은 원본 조합 목록 무변경")


func _gamble_checks() -> void:
	var state: Dictionary = _snapshot("gamble")
	_check(_ui.set_read_model(state), "D091 8부위 실제 ItemDb 견적 모델 수용")
	var l: Dictionary = _ui.layout()
	await _click(l.offers[3].get_center())
	_check(_gambles == [[&"offhand", "unit-quote-3", 41]], "보조 구매 클릭이 견적 ID/revision 전달")
	state.available = false
	_check(_ui.set_read_model(state), "미연결 보부상 잠금 모델 수용")
	await _click(l.offers[0].get_center())
	_check(_gambles.size() == 1, "미연결 구매 요청 없음")
	_check(state.offers[3].price == 200 and state.offers[3].base == ItemDb.get_def("mukham"), "구매 요청 뒤 원본 가격/정의 무변경")


func _invalid_models() -> void:
	var cases: Array[Dictionary] = []
	var s: Dictionary = _snapshot("stash")
	s.revision = -1
	cases.append(s)
	s = _snapshot("stash")
	s.carried_gold = -1
	cases.append(s)
	s = _snapshot("stash")
	s.items = [{"instance_id": "a", "item": ItemInstance.create(ItemDb.get_def("iron_sword")), "cell": Vector2i(9, 7)}]
	cases.append(s)
	s = _snapshot("stash")
	s.items = [{"instance_id": "a", "item": ItemInstance.create(ItemDb.get_def("hp_potion")), "cell": Vector2i.ZERO},
		{"instance_id": "b", "item": ItemInstance.create(ItemDb.get_def("mp_potion")), "cell": Vector2i.ZERO}]
	cases.append(s)
	s = _snapshot("stash")
	s.items = [{"instance_id": "a", "item": ItemInstance.create(ItemDb.get_def("hp_potion")), "cell": Vector2i.ZERO},
		{"instance_id": "a", "item": ItemInstance.create(ItemDb.get_def("mp_potion")), "cell": Vector2i(1, 0)}]
	cases.append(s)
	s = _snapshot("gamble")
	s.offers[0].slot = "weapon"
	cases.append(s)
	s = _snapshot("gamble")
	s.offers[0].quote_id = ""
	cases.append(s)
	s = _snapshot("gamble")
	s.offers[0].price = null
	cases.append(s)
	s = _snapshot("cube")
	s.recipes[0].id = s.recipes[1].id
	cases.append(s)
	s = _snapshot("cube")
	s.recipes.pop_back()
	cases.append(s)
	for i in cases.size():
		_check(not _ui.set_read_model(cases[i]), "잘못된 읽기 모델%d 거절" % i)
		_check(not _ui._available() and not _ui.begin_gold("deposit") and not _ui._can_transmute(), "잘못된 모델%d 뒤 기존 거래 가능 상태 제거" % i)
