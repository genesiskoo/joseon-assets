## #460: 승인 T2 검4를 실제 가방/장비/커서/좌판과 이름표 회수로 검수한다.
func _sword_review() -> void:
	await t.close_all()
	t.main.load_area(AreaDb.TOWN, 0, Level.SpawnHint.FROM_ENTRY)
	await t.frames(4)
	var bag: Node = t.hud_panel("Inventory")
	var tip: Node = t.main.get_node("HUD/Tooltip")
	var inv: Inventory = GameState.inventory
	inv.clear_all()
	GameState.character.level = 10
	GameState.character.str = 45
	GameState.character.dex = 40
	GameState.character.spi = 40
	t.player().combat.recompute_stats()
	var ids := ["bongukgeom", "jedokgeom", "ssangsudo", "saingeom"]
	var specimens: Dictionary = {}
	var before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()
	for i in ids.size():
		var id: String = ids[i]
		var it := ItemInstance.create(ItemDb.get_def(id))
		specimens[id] = it
		t.check(it.def.size == Vector2i(1, 3) and it.def.tier == 2 and it.def.max_stack == 1, "%s 현재 T2/1×3/쌓기1" % id)
		t.check(inv.place(it, Vector2i(i, 0)), "%s 실제 1×3 배치" % id)
		if not before:
			t.check(it.def.icon != null and it.def.icon.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % id, "%s 승인 #459 PNG 로드" % id)
			t.check(it.def.icon.get_size() == Vector2(80, 240), "%s 80×240 원본 텍스처" % id)
	var anchor_positions := {"hwando": Vector2i(5, 0), "yedo": Vector2i(6, 0), "leather_shoes": Vector2i(8, 0)}
	for id in anchor_positions:
		t.check(inv.place(ItemInstance.create(ItemDb.get_def(id)), anchor_positions[id]), "%s 기존 기준물체 배치" % id)
	for key in WORN:
		var result: Dictionary = inv.equip(key, ItemInstance.create(ItemDb.get_def(WORN[key])))
		t.check(result.ok, "%s 같은 초기 장비 표본" % key)
	var offhand: ItemInstance = inv.equipment.offhand
	inv.gold = 3750
	inv.notify_changed()
	await t.key(KEY_I)
	var grid: Rect2 = bag._grid_rect()
	await t.mouse_move(grid.position + Vector2(3.5, 0.5) * bag.CELL)
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("사인검"), 1.0), "사인검 실제 가방 호버")
	t.check(tip.source_rect.size.is_equal_approx(Vector2(40, 120)) and not tip.current_rect.intersects(tip.source_rect), "1×3 전체 툴팁 source·그림 영역 비침범")
	await t.frames(2)
	await t.shot("sword_inventory")
	for id in ["bongukgeom", "jedokgeom", "ssangsudo"]:
		var it: ItemInstance = specimens[id]
		var pos: Vector2i = inv.grid[it]
		var previous: ItemInstance = inv.equipment.weapon
		await t.click(grid.position + (Vector2(pos) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
		t.check(inv.equipment.weapon == it and not inv.grid.has(it), "%s 실제 우클릭 착용·같은 인스턴스" % id)
		var expected_previous := Vector2i(4, 0) if id == "ssangsudo" else pos
		t.check(inv.grid.get(previous) == expected_previous and bag.held == null, "%s 교환 후 이전 1×3 무기 가방 보존" % id)
	t.check(specimens.ssangsudo.def.two_handed and inv.offhand_blocked(), "쌍수도 기존 양손·보조 차단")
	t.check(inv.equipment.offhand == null and inv.grid.get(offhand) == Vector2i(2, 0), "쌍수도 착용 → 묵함 먼저 가방 회수·보조칸 비움")
	await t.click(grid.position + (Vector2(inv.grid[offhand]) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.offhand == null and inv.grid.has(offhand), "양손 착용 중 묵함 재착용 거절·물건 보존")
	t.check(String(bag.get("_msg")) == "두 손 무기를 쥐고 있다", "양손 보조 거절 안내")
	var ritual: ItemInstance = specimens.saingeom
	var ritual_pos: Vector2i = inv.grid[ritual]
	await t.click(grid.position + (Vector2(ritual_pos) + Vector2(0.5, 2.5)) * bag.CELL)
	t.check(bag.held == ritual and not inv.grid.has(ritual), "사인검 마지막 점유칸 클릭 → 같은 검 커서")
	t.check(not tip.current_rect.has_area(), "held 검은 이전 호버 툴팁을 지움")
	await t.mouse_move(Vector2(655, 510))
	await t.frames(2)
	await t.shot("sword_held_twohand")
	await t.click(grid.position + (Vector2(ritual_pos) + Vector2(0.5, 0.5)) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(ritual) == ritual_pos, "긴 검 되놓기 → 원래 1×3 자리")
	await t.click(grid.position + (Vector2(ritual_pos) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.weapon == ritual and not inv.offhand_blocked(), "사인검 실제 착용 → 양손 차단 해제")
	await t.click(grid.position + (Vector2(inv.grid[offhand]) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.offhand == offhand and not inv.grid.has(offhand), "한손 검에서 묵함 실제 재착용")
	await t.click(bag._equip_rect("weapon").get_center(), MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.weapon == null and inv.grid.has(ritual) and bag.held == null, "무기칸 우클릭 → 사인검 가방 해제")
	await t.close_all()
	var merchant: Node3D = null
	for npc in t.tree.get_nodes_in_group("npc"):
		if "def" in npc and npc.def and npc.def.id == "merchant":
			merchant = npc
			break
	if not t.check(merchant != null and await t.talk_to(merchant), "김 영감 실제 클릭 → 대화"):
		return
	if not t.check(await t.talk_pick("shop"), "거래한다 실제 선택 → 좌판"):
		return
	var vendor: Node = t.hud_panel("Vendor")
	t.check(await t.wait_until(func() -> bool: return vendor.visible and bag.visible, 2.0), "검4 좌판·가방 실제 열림")
	var stock: Array[ItemInstance] = []
	for id in ids:
		stock.append(ItemInstance.create(ItemDb.get_def(id)))
	GameState.vendor_stock = stock
	inv.notify_changed()
	await t.frames(2)
	await t.mouse_move(vendor._row_rect(3).get_center())
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("사인검"), 1.0), "48px 좌판 사인검 실제 호버")
	t.check(tip.source_rect.is_equal_approx(vendor._row_rect(3)) and not tip.current_rect.intersects(tip.source_rect), "좌판 툴팁 현재 행·그림 비침범")
	await t.frames(2)
	await t.shot("sword_vendor")
	var original_gold: int = inv.gold
	var total_buy := 0
	var total_sell := 0
	for i in ids.size():
		var bought: ItemInstance = vendor.stock()[0]
		t.check(bought.def.id == ids[i], "검4 고정 진열 순서 보존")
		var price: int = Vendor.buy_price(bought)
		var sale: int = Vendor.sell_price(bought)
		t.check(price == [250, 250, 300, 280][i] and sale == [62, 62, 75, 70][i], "%s 기존 구매/판매 가격" % ids[i])
		var gold_before: int = inv.gold
		await t.click(vendor._row_rect(0).get_center())
		t.check(inv.grid.has(bought) and inv.gold == gold_before - price and not vendor.stock().has(bought), "%s 실제 행 구매·같은 검·골드·재고 이동" % ids[i])
		await t.click(bag._grid_rect().position + (Vector2(inv.grid[bought]) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
		t.check(not inv.grid.has(bought) and inv.gold == gold_before - price + sale, "%s 실제 가방 우클릭 판매·같은 검·가격" % ids[i])
		total_buy += price
		total_sell += sale
	t.check(total_buy == 1080 and total_sell == 269 and inv.gold == original_gold - 811, "검4 거래 합계·가격 보존")
	await t.close_all()
	t.main.load_area(AreaDb.TOWN, 0, Level.SpawnHint.FROM_ENTRY)
	await t.frames(4)
	inv.clear_all()
	inv.notify_changed()
	var p: Node3D = t.player()
	var drops: Array[ItemInstance] = []
	seed(E2e.SEED)
	for id in ids:
		var it := ItemInstance.create(ItemDb.get_def(id))
		drops.append(it)
		EventBus.loot_dropped.emit(it, p.global_position + Vector3(1.6, 1.0, 1.6))
	var fis: Array[FloorItem] = []
	for node in t.tree.get_nodes_in_group("floor_item"):
		if node is FloorItem and drops.has(node.item):
			fis.append(node)
	t.check(await t.wait_until(func() -> bool:
		for fi in fis:
			if not fi.is_settled:
				return false
		return fis.size() == 4, 3.0), "검4 실제 loot_dropped → 모두 바닥 정착")
	await t.key_down(KEY_ALT)
	await t.frames(5)
	for it in drops:
		var fi: FloorItem = null
		for node in t.tree.get_nodes_in_group("floor_item"):
			if node is FloorItem and node.item == it:
				fi = node
				break
		if not t.check(fi != null, "%s 실제 바닥 표본 있음" % it.def.id):
			continue
		var fid: int = fi.get_instance_id()
		var label: Label3D = fi.get_node("Label")
		var at: Vector2 = t.screen_of(label.global_position)
		await t.mouse_move(at)
		t.check(await t.wait_until(func() -> bool: return GameState.hover == fi, 1.0), "%s 현재 이름표 실제 호버" % it.def.id)
		await t.click(at)
		t.check(await t.wait_until(func() -> bool:
			var node := instance_from_id(fid) as Node
			return inv.grid.has(it) and (node == null or node.is_queued_for_deletion()), 5.0), "%s 이름표 클릭 → 걸어가 같은 검 가방 회수" % it.def.id)
		t.check(it.def.size == Vector2i(1, 3) and inv.grid.has(it), "%s 회수 뒤 기존 1×3 물건 보존" % it.def.id)
		await t.frames(2)
	t.check(inv.grid.size() == 4, "선택한 검4만 실제 가방 회수")
	await t.key_up(KEY_ALT)
	for fi in fis:
		if is_instance_valid(fi):
			fi.queue_free()
	await t.close_all()
