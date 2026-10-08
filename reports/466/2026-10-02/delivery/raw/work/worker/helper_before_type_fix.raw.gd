extends E2eScenario
## #466: 승인 15종의 실제 가방·장비·커서·좌판·바닥 입력. 원화와 ItemDef는 변경하지 않는다.

const GROUPS := [
	{"label": "466_armor", "ids": ["jigap", "swaejagap", "gyeongbeongap", "dujeonggap", "silk_dopo", "hakchangui"], "size": [Vector2i(2, 3), Vector2i(2, 3), Vector2i(2, 3), Vector2i(2, 3), Vector2i(2, 3), Vector2i(2, 3)], "prices": [220, 260, 300, 360, 200, 280]},
	{"label": "466_accessories", "ids": ["pouch", "myeongdu", "yagwangju", "jade_ring", "gold_ring"], "size": [Vector2i(1, 1), Vector2i(1, 1), Vector2i(1, 1), Vector2i(1, 1), Vector2i(1, 1)], "prices": [90, 150, 400, 100, 160]},
	{"label": "466_gear_tomes", "ids": ["gwangdahoe", "mokhwa", "ident_tome", "portal_tome"], "size": [Vector2i(2, 1), Vector2i(2, 2), Vector2i(1, 2), Vector2i(1, 2)], "prices": [140, 160, 25, 40]},
]
const WORN := {"weapon": "hwando", "armor": "cotton_dopo", "boots": "leather_shoes", "head": "paeraengi", "offhand": "mukham", "belt": "cotton_belt", "ring1": "silver_ring", "ring2": "silver_ring", "amulet": "jade_charm"}


func run() -> void:
	var was_dev: bool = DevMode.is_active
	var help: String = t.main.hud_label.text
	DevMode.is_active = false
	t.main.hud_label.text = ""
	GameState.character.level = 30
	GameState.character.str = 80
	GameState.character.dex = 80
	GameState.character.spi = 80
	var before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()
	for group in GROUPS:
		await t.close_all()
		t.main.load_area(AreaDb.TOWN, 0, Level.SpawnHint.FROM_ENTRY)
		await t.frames(4)
		for i in group.ids.size():
			var id: String = group.ids[i]
			var d: ItemDef = ItemDb.get_def(id)
			t.check(d != null and d.size == group.size[i] and d.price == group.prices[i], "%s 기존 점유·가격" % id)
			if not before:
				t.check(d.icon != null and d.icon.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % id, "%s 승인 PNG 실제 로드" % id)
				t.check(d.icon.get_size() == Vector2(d.size) * 80.0, "%s 승인 캔버스 크기" % id)
		await _view(group)
		await t.close_all()
		for id in group.ids:
			await _bag_input(id)
		await _trade(group)
		await _floor(group.ids)
	DevMode.is_active = was_dev
	t.main.hud_label.text = help
	await t.close_all()


func _worn(overrides: Dictionary = {}) -> void:
	var inv: Inventory = GameState.inventory
	for key in WORN:
		inv.equip(key, ItemInstance.create(ItemDb.get_def(overrides.get(key, WORN[key]))))
	t.player().combat.recompute_stats()


func _shop() -> bool:
	await t.close_all()
	var npc: Node3D = null
	for n in t.tree.get_nodes_in_group("npc"):
		if "def" in n and n.def and n.def.id == "merchant":
			npc = n
			break
	if not t.check(npc != null and await t.talk_to(npc), "김 영감 실제 클릭 → 대화"):
		return false
	if not t.check(await t.talk_pick("shop"), "거래한다 실제 클릭 → 좌판"):
		return false
	return t.check(await t.wait_until(func() -> bool: return t.hud_panel("Vendor").visible and t.hud_panel("Inventory").visible, 2.0), "좌판·가방 함께 열림")


func _view(group: Dictionary) -> void:
	var inv: Inventory = GameState.inventory
	inv.clear_all()
	var armor: bool = group.label == "466_armor"
	var gear: bool = group.label == "466_gear_tomes"
	_worn({"armor": "hakchangui"} if armor else {"belt": "gwangdahoe", "boots": "mokhwa"} if gear else {})
	var stock: Array[ItemInstance] = []
	for i in group.ids.size():
		var id: String = group.ids[i]
		var d: ItemDef = ItemDb.get_def(id)
		stock.append(ItemInstance.create(d, 99 if d.max_stack > 1 else 1))
		if armor and i == 5:
			continue # 10×4 가방에는 2×3 다섯 벌. 여섯 번째 학창의는 실제 갑옷 칸과 좌판에 보인다.
		var pos := Vector2i([0, 2, 6, 8][i], 0) if gear else Vector2i(i * 2, 0)
		t.check(inv.place(ItemInstance.create(d, 12 if d.max_stack > 1 else 1), pos), "%s 비교 표본 실제 배치" % id)
	inv.gold = 20000
	inv.notify_changed()
	if not await _shop():
		return
	GameState.vendor_stock = stock
	inv.notify_changed()
	var bag: Node = t.hud_panel("Inventory")
	if gear:
		await t.click(bag._grid_rect().position + Vector2(6.5, 1.5) * bag.CELL)
		t.check(bag.held != null and bag.held.def.id == "ident_tome", "식별부첩 마지막 칸 → 실제 커서 그림")
	await t.mouse_move(Vector2(650, 450))
	await t.shot(group.label)
	if gear:
		await t.click(bag._grid_rect().position + Vector2(6.5, 0.5) * bag.CELL)
		t.check(bag.held == null, "촬영 뒤 식별부첩 원자리 복원")


func _bag_input(id: String) -> void:
	await t.close_all()
	var inv: Inventory = GameState.inventory
	inv.clear_all()
	_worn()
	var it := ItemInstance.create(ItemDb.get_def(id), 12 if ItemDb.get_def(id).max_stack > 1 else 1)
	t.check(inv.place(it, Vector2i.ZERO), "%s 입력 표본 배치" % id)
	await t.key(KEY_I)
	var bag: Node = t.hud_panel("Inventory")
	var tip: Node = t.main.get_node("HUD/Tooltip")
	var grid: Rect2 = bag._grid_rect()
	var last := grid.position + (Vector2(it.def.size) - Vector2(0.5, 0.5)) * bag.CELL
	await t.mouse_move(last)
	t.check(await t.wait_until(func() -> bool: return tip.current_rect.has_area() and tip.source_rect == Rect2(grid.position, Vector2(it.def.size) * bag.CELL), 1.0), "%s 마지막 점유칸 실제 툴팁·전체 영역" % id)
	t.check(not tip.current_rect.intersects(tip.source_rect), "%s 툴팁은 물체를 가리지 않음" % id)
	await t.click(last)
	t.check(bag.held == it and not inv.grid.has(it) and not tip.current_rect.has_area(), "%s 마지막 칸 → 같은 물체 커서·이전 툴팁 해제" % id)
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(it) == Vector2i.ZERO, "%s 되놓기 → 동일 물체·좌상단 복원" % id)
	if it.def.is_equipment():
		var key: String = inv.default_slot_for(it)
		var old: ItemInstance = inv.equipment[key]
		await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
		t.check(inv.equipment[key] == it and inv.grid.get(old) == Vector2i.ZERO and bag.held == null, "%s 우클릭 실제 장착·이전 물건 원자리" % id)
		if id == "gwangdahoe":
			t.check(inv.belt_capacity() == 6, "광다회 기존 벨트 6칸 유지")
		await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
		t.check(inv.equipment[key] == old and inv.grid.get(it) == Vector2i.ZERO, "%s 이전 장비 재장착·표본 복원" % id)
	await t.close_all()


func _trade(group: Dictionary) -> void:
	if not await _shop():
		return
	var inv: Inventory = GameState.inventory
	var vendor: Node = t.hud_panel("Vendor")
	var bag: Node = t.hud_panel("Inventory")
	var tip: Node = t.main.get_node("HUD/Tooltip")
	for i in group.ids.size():
		var id: String = group.ids[i]
		inv.clear_all()
		inv.gold = 20000
		var stock_item := ItemInstance.create(ItemDb.get_def(id), 99 if ItemDb.get_def(id).max_stack > 1 else 1)
		GameState.vendor_stock = [stock_item]
		inv.notify_changed()
		await t.mouse_move(vendor._row_rect(0).get_center())
		t.check(await t.wait_until(func() -> bool: return tip.current_rect.has_area() and tip.source_rect == vendor._row_rect(0), 1.0), "%s 48px 좌판 실제 행 툴팁" % id)
		t.check(Vendor.buy_price(stock_item) == group.prices[i] and Vendor.sell_price(stock_item) == maxi(1, group.prices[i] / 4) * stock_item.stack, "%s 기존 구매·판매 가격식" % id)
		await t.click(vendor._row_rect(0).get_center())
		var bought: ItemInstance = null
		for it in inv.grid:
			if it.def.id == id:
				bought = it
		if not t.check(bought != null and inv.gold == 20000 - group.prices[i], "%s 실제 구매·가방·엽전" % id):
			continue
		t.check((bought == stock_item and not vendor.stock().has(stock_item)) if bought.def.max_stack == 1 else (bought != stock_item and bought.stack == 1 and stock_item.stack == 99 and vendor.stock().has(stock_item)), "%s 장비 유한·부첩 무한 재고 보존" % id)
		var sale: int = Vendor.sell_price(bought)
		await t.click(bag._grid_rect().position + (Vector2(inv.grid[bought]) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
		t.check(not inv.grid.has(bought) and inv.gold == 20000 - group.prices[i] + sale, "%s 실제 우클릭 판매·가방 해제·엽전" % id)
	await t.close_all()


func _floor(ids: Array) -> void:
	var inv: Inventory = GameState.inventory
	var at: Vector3 = t.player().global_position + Vector3(1.6, 1.0, 1.6)
	await t.key_down(KEY_ALT)
	for id in ids:
		inv.clear_all()
		var it := ItemInstance.create(ItemDb.get_def(id))
		EventBus.loot_dropped.emit(it, at)
		var fi: FloorItem = null
		for node in t.tree.get_nodes_in_group("floor_item"):
			if node is FloorItem and node.item == it:
				fi = node
				break
		if not t.check(fi != null, "%s loot_dropped → 실제 바닥 물건" % id):
			continue
		t.check(await t.wait_until(func() -> bool: return fi.is_settled, 3.0), "%s 바닥 정착" % id)
		var fid: int = fi.get_instance_id()
		var label: Label3D = fi.get_node("Label")
		var screen: Vector2 = t.screen_of(label.global_position)
		await t.mouse_move(screen)
		t.check(await t.wait_until(func() -> bool: return GameState.hover == fi, 1.0), "%s 실제 이름표 호버" % id)
		await t.click(screen)
		t.check(await t.wait_until(func() -> bool:
			var n := instance_from_id(fid) as Node
			return inv.grid.has(it) and (n == null or n.is_queued_for_deletion()), 5.0), "%s 이름표 클릭 → 동일 물체 회수·바닥 해제" % id)
		await t.frames(2)
		if is_instance_valid(fi):
			fi.queue_free()
	await t.key_up(KEY_ALT)
