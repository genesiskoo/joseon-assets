extends Control
## #554: 읽기 모델과 의도 신호만 가진 서비스 창. 경제·저장·원본 아이템에 쓰지 않는다.
const SKIN = preload("res://ui/ui_skin.gd")
const FONTS = preload("res://ui/ui_fonts.gd")
## 기존 InventoryUi의 D-091 자리만 공유한다. 스크립트 preload는 독립 -s에 EventBus를 요구하므로 쓰지 않는다.
const BAG_EQUIP_LAYOUT := {
	"weapon": [112, 102, 56, 84, "오른손"], "armor": [188, 102, 56, 84, "갑옷"], "amulet": [256, 54, 28, 28, "호신부"],
	"ring1": [152, 192, 28, 28, "반지"], "ring2": [252, 192, 28, 28, "반지"], "boots": [188, 226, 56, 56, "신발"], "belt": [188, 192, 56, 28, "허리띠"],
	"head": [188, 40, 56, 56, "머리"], "offhand": [264, 102, 56, 84, "보조"],
}
const BAG_GRID_Y := 248
const CELL := 40.0
const WIDTH := 432.0
const FONT_S := 14
const FONT_M := 15
const FONT_L := 18
const KINDS := ["stash", "cube", "gamble"]
const TITLES := {"stash": "반닫이", "cube": "호리병", "gamble": "보부상 보따리"}
const SLOTS := ["head", "weapon", "armor", "offhand", "amulet", "ring", "belt", "boots"]
const SLOT_NAMES := ["머리", "칼", "옷", "보조", "호신부", "가락지", "허리띠", "신"]
const SLOT_ENUMS := [ItemDef.Slot.HEAD, ItemDef.Slot.WEAPON, ItemDef.Slot.ARMOR, ItemDef.Slot.OFFHAND,
	ItemDef.Slot.AMULET, ItemDef.Slot.RING, ItemDef.Slot.BELT, ItemDef.Slot.BOOTS]
const RECIPE_CATALOG := [
	{"id": "jade_upgrade", "title": "옥 합치기", "ingredients": "같은 옥 · 같은 단 3개", "result": "한 단 위 옥 1개"},
	{"id": "unsocket", "title": "옥 빼기", "ingredients": "옥이 박힌 장비 + 귀환부 1", "result": "빈 홈 장비 · 박힌 옥은 소실"},
	{"id": "rejuvenation", "title": "청심환 만들기", "ingredients": "탕약 3 + 영약 3 + 깨진 옥 1", "result": "청심환 1개"},
	{"id": "reroll_magic", "title": "매직 다시 굴리기", "ingredients": "매직 장비 + 흠 있는 옥 3", "result": "같은 베이스 새 매직 장비"},
	{"id": "add_sockets", "title": "홈 뚫기", "ingredients": "보통·상품 칼/옷 + 서로 다른 온전한 옥 3", "result": "엽전 300 · 홈 수는 조합 서비스가 판정"},
	{"id": "paper_scrolls", "title": "두루마리 만들기", "ingredients": "괴황지 2 + 경면주사 1", "result": "식별부 3 / 귀환부 1 선택"},
	{"id": "white_fur_talisman", "title": "흰 털 빙결부", "ingredients": "장산범 흰 털 + 빙결부 3", "result": "특수 빙결부 · 후속 판정 후보"},
	{"id": "iron_scale_talisman", "title": "쇠녹임 화염부", "ingredients": "불가살이 쇠비늘 + 화염부 3", "result": "특수 화염부 · 후속 판정 후보"},
]

signal close_requested
signal grid_action_requested(kind: StringName, instance_id: String, cell: Vector2i, mouse_button: int, revision: int)
signal gold_action_requested(operation: StringName, amount: int, revision: int)
signal recipe_selected(recipe_id: StringName)
signal transmute_requested(recipe_id: StringName, revision: int)
signal gamble_requested(slot: StringName, quote_id: String, revision: int)

var kind: String = "stash"
var show_bag_preview: bool = false
var bag_preview: Inventory
var _model: Dictionary = {}
var _font: Font
var _heading: Font
var _mouse := Vector2(-1, -1)
var _recipe_offset: int = 0
var _selected_recipe: String = ""
var _status: String = ""
var _gold_operation: String = ""
var _amount: LineEdit


func _ready() -> void:
	_font = FONTS.body()
	_heading = FONTS.heading()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_amount = LineEdit.new()
	_amount.name = "GoldAmount"
	_amount.placeholder_text = "엽전 수를 입력하세요"
	_amount.max_length = 19
	_amount.add_theme_font_override("font", _font)
	_amount.add_theme_font_size_override("font_size", FONT_M)
	_amount.add_theme_color_override("font_color", SKIN.TEXT_BRIGHT)
	_amount.add_theme_color_override("font_placeholder_color", SKIN.TEXT_SOFT)
	var edit_style := StyleBoxFlat.new()
	edit_style.bg_color = SKIN.ROW
	edit_style.border_color = SKIN.FRAME
	edit_style.set_border_width_all(1)
	edit_style.content_margin_left = 8
	edit_style.content_margin_right = 8
	_amount.add_theme_stylebox_override("normal", edit_style)
	var focus_style := edit_style.duplicate() as StyleBoxFlat
	focus_style.border_color = SKIN.FRAME_HIGHLIGHT
	_amount.add_theme_stylebox_override("focus", focus_style)
	_amount.visible = false
	_amount.text_changed.connect(func(_text: String) -> void: queue_redraw())
	_amount.text_submitted.connect(func(_text: String) -> void: confirm_gold())
	add_child(_amount)
	get_viewport().size_changed.connect(_layout_amount)
	_layout_amount()


## 잘못된 모델은 이전 거래 가능 상태를 남기지 않는다.
func set_read_model(snapshot: Dictionary) -> bool:
	_gold_operation = ""
	if _amount != null:
		_amount.visible = false
	if not _valid_model(snapshot):
		_model = {"revision": 0, "available": false, "items": [], "unavailable_reason": "읽기 모델 오류 — 거래 잠금"}
		_status = "읽기 모델 오류 — 거래 잠금"
		queue_redraw()
		return false
	kind = String(snapshot.kind)
	_model = snapshot.duplicate(true)
	_recipe_offset = 0
	if kind == "cube":
		_selected_recipe = String(_model.recipes[0].id)
	else:
		_selected_recipe = ""
	_status = ""
	queue_redraw()
	return true


func _valid_model(s: Dictionary) -> bool:
	if typeof(s.get("kind")) != TYPE_STRING or String(s.kind) not in KINDS or typeof(s.get("revision")) != TYPE_INT or int(s.revision) < 0 or typeof(s.get("available")) != TYPE_BOOL:
		return false
	for key in ["carried_gold", "stored_gold"]:
		var amount: Variant = s.get(key)
		if amount != null and (typeof(amount) != TYPE_INT or int(amount) < 0):
			return false
	if typeof(s.get("items", [])) != TYPE_ARRAY:
		return false
	if s.kind == "gamble" and not s.get("items", []).is_empty():
		return false
	var dims := Vector2i(10, 8) if s.kind == "stash" else Vector2i(4, 3)
	var ids: Dictionary = {}
	var rects: Array[Rect2i] = []
	for entry in s.get("items", []):
		if not (entry is Dictionary) or not (entry.get("item") is ItemInstance) or not (entry.item.def is ItemDef) or typeof(entry.get("cell")) != TYPE_VECTOR2I or typeof(entry.get("instance_id")) != TYPE_STRING:
			return false
		var id: String = entry.instance_id
		var r := Rect2i(entry.cell, entry.item.def.size)
		if id.is_empty() or ids.has(id) or r.size.x <= 0 or r.size.y <= 0 or not Rect2i(Vector2i.ZERO, dims).encloses(r):
			return false
		for other in rects:
			if other.intersects(r):
				return false
		ids[id] = true
		rects.append(r)
	if s.kind == "cube":
		if typeof(s.get("recipes")) != TYPE_ARRAY or s.recipes.size() != RECIPE_CATALOG.size() or typeof(s.get("transmute_enabled")) != TYPE_BOOL:
			return false
		var recipes: Dictionary = {}
		for recipe in s.recipes:
			if not (recipe is Dictionary) or typeof(recipe.get("id")) != TYPE_STRING or String(recipe.id).is_empty() or recipes.has(recipe.id) or typeof(recipe.get("enabled")) != TYPE_BOOL:
				return false
			for key in ["title", "ingredients", "result"]:
				if typeof(recipe.get(key)) != TYPE_STRING:
					return false
			recipes[recipe.id] = true
	elif s.kind == "gamble":
		if typeof(s.get("offers")) != TYPE_ARRAY or s.offers.size() != SLOTS.size():
			return false
		var slots: Dictionary = {}
		for offer in s.offers:
			if not (offer is Dictionary) or typeof(offer.get("slot")) != TYPE_STRING or String(offer.slot) not in SLOTS or not (offer.get("base") is ItemDef) or typeof(offer.get("enabled")) != TYPE_BOOL or typeof(offer.get("quote_id")) != TYPE_STRING:
				return false
			var slot: String = offer.slot
			var i: int = SLOTS.find(slot)
			var price: Variant = offer.get("price")
			if slots.has(slot) or offer.base.slot != SLOT_ENUMS[i] or (price != null and (typeof(price) != TYPE_INT or int(price) < 0)):
				return false
			if offer.enabled and (price == null or String(offer.quote_id).is_empty()):
				return false
			slots[slot] = true
	return true


## 그리기·입력·시험이 공유하는 논리 좌표. 기존 canvas_items 확대 정책을 따른다.
static func layout_for(view: Vector2) -> Dictionary:
	var pr := Rect2(0, 32, WIDTH, maxf(1, view.y - 192))
	var bottom: float = pr.end.y
	var cards: Array[Rect2] = []
	for i in 8:
		cards.append(Rect2(16 + (i % 2) * 208, 96 + (i / 2) * 92, 192, 84))
	var rows: Array[Rect2] = []
	for i in 3:
		rows.append(Rect2(16, 250 + i * 56, 400, 54))
	return {"panel": pr, "close": Rect2(397, 39, 26, 26), "stash_grid": Rect2(16, 96, 400, 320),
		"cube_grid": Rect2(136, 96, 160, 120), "deposit": Rect2(16, bottom - 81, 192, 36),
		"withdraw": Rect2(224, bottom - 81, 192, 36), "recipe_list": Rect2(16, 250, 400, 168),
		"recipe_rows": rows, "recipe_prev": Rect2(356, 224, 28, 24), "recipe_next": Rect2(388, 224, 28, 24),
		"transmute": Rect2(112, bottom - 72, 208, 36), "offers": cards,
		"footer": Rect2(40, bottom - 33, 352, 22), "bag": Rect2(view.x - WIDTH, 32, WIDTH, pr.size.y),
		"amount_popup": Rect2(32, 176, 368, 190), "amount_edit": Rect2(48, 235, 336, 36),
		"amount_confirm": Rect2(48, 295, 156, 36), "amount_cancel": Rect2(228, 295, 156, 36)}


func layout() -> Dictionary:
	return layout_for(get_viewport_rect().size)


func grid_rect() -> Rect2:
	var l := layout()
	return l.stash_grid if kind == "stash" else l.cube_grid if kind == "cube" else Rect2()


func cell_at(point: Vector2) -> Vector2i:
	var r := grid_rect()
	return Vector2i((point - r.position) / CELL) if r.has_point(point) else Vector2i(-1, -1)


func _has_point(point: Vector2) -> bool:
	return layout().panel.has_point(point) or (show_bag_preview and layout().bag.has_point(point))


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		_mouse = event.position
		queue_redraw()
	elif event is InputEventMouseButton and event.pressed:
		_mouse = event.position
		handle_pointer(event.position, event.button_index)
		accept_event()


func _input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel") and not event.is_echo():
		handle_escape()
		get_viewport().set_input_as_handled()


func handle_escape() -> void:
	if not _gold_operation.is_empty():
		_cancel_gold()
	else:
		close_requested.emit()


func handle_pointer(point: Vector2, button: int) -> void:
	var l := layout()
	if not _gold_operation.is_empty():
		if button == MOUSE_BUTTON_LEFT:
			if l.amount_cancel.has_point(point):
				_cancel_gold()
			elif l.amount_confirm.has_point(point):
				confirm_gold()
		return
	if button == MOUSE_BUTTON_LEFT and l.close.has_point(point):
		close_requested.emit()
		return
	if kind == "cube" and l.recipe_list.has_point(point) and button in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
		scroll_recipes(-1 if button == MOUSE_BUTTON_WHEEL_UP else 1)
		return
	if button not in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		return
	var cell := cell_at(point)
	if cell.x >= 0:
		if _available():
			var instance_id := ""
			for entry in _model.get("items", []):
				if Rect2i(entry.cell, entry.item.def.size).has_point(cell):
					instance_id = entry.instance_id
			grid_action_requested.emit(StringName(kind), instance_id, cell, button, _revision())
		else:
			_status = String(_model.get("unavailable_reason", "서비스 미연결"))
	elif button == MOUSE_BUTTON_LEFT:
		if kind == "stash":
			if l.deposit.has_point(point):
				begin_gold("deposit")
			elif l.withdraw.has_point(point):
				begin_gold("withdraw")
		elif kind == "cube":
			if l.recipe_prev.has_point(point):
				scroll_recipes(-1)
			elif l.recipe_next.has_point(point):
				scroll_recipes(1)
			elif l.transmute.has_point(point) and _can_transmute():
				transmute_requested.emit(StringName(_selected_recipe), _revision())
			else:
				for i in l.recipe_rows.size():
					if l.recipe_rows[i].has_point(point):
						var recipes: Array = _model.get("recipes", [])
						if _recipe_offset + i < recipes.size():
							_selected_recipe = String(recipes[_recipe_offset + i].id)
							recipe_selected.emit(StringName(_selected_recipe))
		elif kind == "gamble":
			for i in SLOTS.size():
				if l.offers[i].has_point(point):
					var offer := _offer(SLOTS[i])
					if _can_gamble(offer):
						gamble_requested.emit(StringName(SLOTS[i]), String(offer.quote_id), _revision())
					else:
						_status = String(offer.get("disabled_reason", "견적 대기 · 거래 미연결"))
	queue_redraw()


func scroll_recipes(delta: int) -> void:
	_recipe_offset = clampi(_recipe_offset + delta, 0, maxi(0, _model.get("recipes", []).size() - 3))
	queue_redraw()


func begin_gold(operation: String) -> bool:
	if kind != "stash" or operation not in ["deposit", "withdraw"] or not _available() or _gold_source(operation) <= 0 or _amount == null:
		return false
	_gold_operation = operation
	_amount.text = ""
	_amount.visible = true
	_layout_amount()
	_amount.grab_focus()
	queue_redraw()
	return true


func _gold_source(operation: String) -> int:
	var value: Variant = _model.get("carried_gold") if operation == "deposit" else _model.get("stored_gold")
	return int(value) if value != null else 0


func parsed_gold_amount(value: String) -> int:
	var clean := value.strip_edges()
	if clean.is_empty() or not clean.is_valid_int() or clean.begins_with("-") or clean.begins_with("+"):
		return 0
	while clean.length() > 1 and clean.begins_with("0"):
		clean = clean.substr(1)
	if clean.length() > 19 or (clean.length() == 19 and clean > "9223372036854775807"):
		return 0
	return clean.to_int()


func can_confirm_gold() -> bool:
	if _amount == null or _gold_operation.is_empty() or not _available():
		return false
	var amount := parsed_gold_amount(_amount.text)
	return amount > 0 and amount <= _gold_source(_gold_operation)


func confirm_gold() -> bool:
	if not can_confirm_gold():
		_status = "잔고 이내의 양수를 입력하세요"
		queue_redraw()
		return false
	var operation := StringName(_gold_operation)
	var amount := parsed_gold_amount(_amount.text)
	_cancel_gold()
	_status = ""
	gold_action_requested.emit(operation, amount, _revision())
	return true


func _cancel_gold() -> void:
	_gold_operation = ""
	if _amount != null:
		_amount.visible = false
	queue_redraw()


func _layout_amount() -> void:
	if _amount != null:
		var r: Rect2 = layout().amount_edit
		_amount.position = r.position
		_amount.size = r.size


func _available() -> bool:
	return bool(_model.get("available", false))


func _revision() -> int:
	return int(_model.get("revision", 0))


func _recipe() -> Dictionary:
	for recipe in _model.get("recipes", []):
		if String(recipe.id) == _selected_recipe:
			return recipe
	return {}


func _can_transmute() -> bool:
	return _available() and bool(_model.get("transmute_enabled", false)) and bool(_recipe().get("enabled", false))


func _offer(slot: String) -> Dictionary:
	for offer in _model.get("offers", []):
		if String(offer.slot) == slot:
			return offer
	return {}


func _can_gamble(offer: Dictionary) -> bool:
	return _available() and bool(offer.get("enabled", false)) and offer.get("price") != null and not String(offer.get("quote_id", "")).is_empty()


func _text(point: Vector2, value: String, width: float = 400, color: Color = SKIN.TEXT, heading: bool = false, px: int = FONT_M) -> void:
	var font: Font = _heading if heading else _font
	if font == null:
		return
	var fitted := value
	if font.get_string_size(fitted, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width:
		while not fitted.is_empty() and font.get_string_size(fitted + "…", HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width:
			fitted = fitted.left(fitted.length() - 1)
		fitted += "…"
	draw_string(font, point.round(), fitted, HORIZONTAL_ALIGNMENT_LEFT, width, px, color)


func _button(r: Rect2, title: String, enabled: bool) -> void:
	SKIN.button(self, r, (1 if r.has_point(_mouse) else 0) if enabled else 2)
	var width: float = _heading.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_M).x
	var base: float = (_heading.get_ascent(FONT_M) - _heading.get_descent(FONT_M)) * 0.5
	_text(r.get_center() + Vector2(-width * 0.5, base), title, r.size.x - 12, SKIN.TITLE if enabled else SKIN.TEXT_DIM, true)


func _frame(r: Rect2, title: String, closable: bool) -> void:
	SKIN.panel(self, r)
	var width: float = _heading.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_L).x
	SKIN.title_tab(self, Rect2(r.get_center().x - width * 0.5 - 16, r.position.y + 5, width + 32, 30))
	_text(Vector2(r.get_center().x - width * 0.5, r.position.y + 26), title, width + 1, SKIN.TITLE, true, FONT_L)
	if closable:
		var xr: Rect2 = layout().close
		draw_rect(xr, Color(0.12, 0.07, 0.06))
		draw_rect(xr, Color(0.45, 0.25, 0.19), false)
		draw_line(xr.position + Vector2(8, 8), xr.end - Vector2(8, 8), Color(0.8, 0.38, 0.28), 2)
		draw_line(xr.position + Vector2(18, 8), xr.position + Vector2(8, 18), Color(0.8, 0.38, 0.28), 2)


func _draw_grid(r: Rect2, dims: Vector2i, entries: Array) -> void:
	for y in dims.y:
		for x in dims.x:
			SKIN.item_slot(self, Rect2(r.position + Vector2(x, y) * CELL, Vector2(CELL, CELL)))
	for entry in entries:
		var item: ItemInstance = entry.item
		var box := Rect2(r.position + Vector2(entry.cell) * CELL, Vector2(item.def.size) * CELL)
		SKIN.item_slot(self, box, true, item.color())
		SKIN.item_icon(self, box, item.def.icon, 1, 3)
		if item.stack > 1:
			_text(box.position + Vector2(4, 15), str(item.stack), box.size.x - 8, SKIN.TEXT_BRIGHT, false, FONT_S)
	if r.has_point(_mouse):
		SKIN.item_focus(self, Rect2(r.position + Vector2(Vector2i((_mouse - r.position) / CELL)) * CELL, Vector2(CELL, CELL)))


func _draw() -> void:
	if _font == null or _heading == null:
		return
	var l := layout()
	_frame(l.panel, String(TITLES[kind]), true)
	match kind:
		"stash":
			_text(Vector2(16, 80), "개인 보관함 · 10 × 8", 400, SKIN.TEXT_SOFT)
			_draw_grid(l.stash_grid, Vector2i(10, 8), _model.get("items", []))
			_text(Vector2(16, 439), "보관 엽전  %s" % _gold_label("stored_gold"), 400, SKIN.PRICE)
			_text(Vector2(16, 461), "휴대 엽전  %s" % _gold_label("carried_gold"), 400, SKIN.TEXT_SOFT)
			_button(l.deposit, "맡기기", _available() and _gold_source("deposit") > 0)
			_button(l.withdraw, "찾기", _available() and _gold_source("withdraw") > 0)
		"cube":
			_text(Vector2(16, 80), "물건을 넣고 조합을 고릅니다 · 4 × 3", 400, SKIN.TEXT_SOFT)
			_draw_grid(l.cube_grid, Vector2i(4, 3), _model.get("items", []))
			var recipes: Array = _model.get("recipes", [])
			_text(Vector2(16, 243), "조합  %d–%d / %d · 휠로 이동" % [_recipe_offset + 1, mini(_recipe_offset + 3, recipes.size()), recipes.size()], 330, SKIN.TITLE, true)
			_button(l.recipe_prev, "↑", _recipe_offset > 0)
			_button(l.recipe_next, "↓", _recipe_offset + 3 < recipes.size())
			for i in l.recipe_rows.size():
				if _recipe_offset + i >= recipes.size():
					break
				var recipe: Dictionary = recipes[_recipe_offset + i]
				var row: Rect2 = l.recipe_rows[i]
				draw_rect(row, SKIN.ROW_HOVER if row.has_point(_mouse) or recipe.id == _selected_recipe else SKIN.ROW)
				if recipe.id == _selected_recipe:
					draw_rect(row.grow(-0.5), SKIN.FRAME_HIGHLIGHT, false)
				_text(row.position + Vector2(10, 20), "%d. %s" % [_recipe_offset + i + 1, recipe.title], 380, SKIN.TEXT_BRIGHT)
				_text(row.position + Vector2(10, 42), String(recipe.ingredients), 380, SKIN.TEXT_SOFT, false, FONT_S)
			var selected := _recipe()
			_text(Vector2(16, 442), "결과  %s" % selected.get("result", "조합 목록 미연결"), 400, SKIN.PRICE, false, FONT_S)
			_text(Vector2(16, 464), String(selected.get("disabled_reason", "")), 400, SKIN.TEXT_SOFT, false, FONT_S)
			_button(l.transmute, "흔들기", _can_transmute())
		"gamble":
			_text(Vector2(16, 80), "미식별 보따리 · 부위를 고릅니다", 400, SKIN.TEXT_SOFT)
			for i in SLOTS.size():
				var row: Rect2 = l.offers[i]
				var offer := _offer(SLOTS[i])
				var enabled := _can_gamble(offer)
				draw_rect(row, SKIN.ROW_HOVER if row.has_point(_mouse) else SKIN.ROW)
				draw_rect(row.grow(-0.5), SKIN.FRAME, false)
				var icon := Rect2(row.position + Vector2(8, 8), Vector2(56, 64))
				SKIN.item_slot(self, icon, true)
				if offer.get("base") is ItemDef:
					SKIN.item_icon(self, icon, offer.base.icon, 1, 5)
				_text(row.position + Vector2(74, 25), SLOT_NAMES[i], 108, SKIN.TITLE, true)
				_text(row.position + Vector2(74, 47), "엽전 %s" % offer.get("price") if offer.get("price") != null else "견적 대기", 108, SKIN.PRICE if enabled else SKIN.TEXT_SOFT, false, FONT_S)
				_text(row.position + Vector2(74, 69), "구매" if enabled else "거래 미연결", 108, SKIN.TEXT if enabled else SKIN.TEXT_DIM, false, FONT_S)
	var footer: String = _status if not _status.is_empty() else String(_model.get("unavailable_reason", "요청 결과는 서비스가 갱신합니다"))
	_text(l.footer.position + Vector2(0, 16), footer, l.footer.size.x, SKIN.TEXT_SOFT, false, FONT_S)
	if show_bag_preview:
		_draw_bag(l.bag)
	if not _gold_operation.is_empty():
		draw_rect(l.panel, Color(0.02, 0.02, 0.02, 0.72))
		SKIN.panel(self, l.amount_popup)
		_text(Vector2(48, 214), "엽전 맡기기" if _gold_operation == "deposit" else "엽전 찾기", 330, SKIN.TITLE, true, FONT_L)
		_text(Vector2(48, 289), "가능한 양  %d" % _gold_source(_gold_operation), 330, SKIN.TEXT_SOFT, false, FONT_S)
		_button(l.amount_confirm, "확인", can_confirm_gold())
		_button(l.amount_cancel, "취소", true)


func _gold_label(key: String) -> String:
	return str(_model[key]) if _model.get(key) != null else "—"


func _draw_bag(pr: Rect2) -> void:
	_frame(pr, "도호의 가방", false)
	if bag_preview == null:
		return
	for key in BAG_EQUIP_LAYOUT:
		var values: Array = BAG_EQUIP_LAYOUT[key]
		var r := Rect2(pr.position + Vector2(values[0], values[1]), Vector2(values[2], values[3]))
		var item: ItemInstance = bag_preview.equipment.get(key)
		SKIN.item_slot(self, r, item != null, item.color() if item != null else SKIN.SLOT_RIM)
		if item != null:
			SKIN.item_icon(self, r, item.def.icon, 1, 3)
	var entries: Array = []
	for item in bag_preview.grid:
		entries.append({"item": item, "cell": bag_preview.grid[item]})
	_draw_grid(Rect2(pr.position + Vector2(16, 40 + BAG_GRID_Y), Vector2(400, 160)), Vector2i(10, 4), entries)
	_text(pr.position + Vector2(40, pr.size.y - 17), "읽기 표본 · 실제 가방/엽전/저장 미연결", 352, SKIN.TEXT_SOFT, false, FONT_S)
