## 승인 봉인물3: 실제 입력으로 표시·팔기/버리기 금지·이름표 줍기를 비교한다.
func _seal_review() -> void:
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
	var ids := ["seal_heukrang", "seal_jangsanbeom", "seal_bulgasari"]
	var specimens: Array[ItemInstance] = []
	var before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()
	for i in ids.size():
		var id: String = ids[i]
		var it := ItemInstance.create(ItemDb.get_def(id))
		specimens.append(it)
		t.check(inv.place(it, Vector2i(i, 0)), "%s 봉인물1×1 실제 배치" % id)
		t.check(it.def.quest_item and it.def.max_stack == 1 and it.stack == 1 and not it.def.can_discard(),
			"%s 퀘스트/쌓기1/버림 금지 보존" % id)
		if not before:
			t.check(it.def.icon != null and it.def.icon.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % id,
				"%s ItemDb → 승인 #454 PNG" % id)
	for i in 3:
		var id: String = ["satgat", "piju", "injang"][i]
		t.check(inv.place(ItemInstance.create(ItemDb.get_def(id)), Vector2i(i * 2, 2)), "%s 기존 기준물체 배치" % id)
	for key in WORN:
		inv.equip(key, ItemInstance.create(ItemDb.get_def(WORN[key])))
	inv.gold = 3750
	inv.notify_changed()
	await t.key(KEY_I)
	var grid: Rect2 = bag._grid_rect()
	await t.mouse_move(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("흑랑의 봉인패"), 1.0), "봉인패 실제 가방 호버")
	t.check(not tip.current_rect.intersects(tip.source_rect), "봉인패 툴팁이 원래 칸을 가리지 않음")
	await t.frames(2)
	await t.shot("seal_inventory")
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == specimens[0] and not inv.grid.has(specimens[0]), "봉인패 클릭 → 같은 물건 커서")
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(specimens[0]) == Vector2i.ZERO, "봉인패 되놓기 → 원래 칸")
	var floor_before: int = t.tree.get_nodes_in_group("floor_item").size()
	for i in ids.size():
		await t.click(grid.position + Vector2(i + 0.5, 0.5) * bag.CELL, MOUSE_BUTTON_LEFT, false, true)
		t.check(inv.grid.get(specimens[i]) == Vector2i(i, 0) and bag.held == null,
			"%s 실제Ctrl클릭 → 버림 거부·원자리" % ids[i])
	t.check(t.tree.get_nodes_in_group("floor_item").size() == floor_before, "Ctrl버림 거부 후 바닥 물건 추가 없음")
	await t.close_all()
	var merchant: Node3D = null
	for npc in t.tree.get_nodes_in_group("npc"):
		if "def" in npc and npc.def and npc.def.id == "merchant":
			merchant = npc
			break
	if not t.check(merchant != null and await t.talk_to(merchant), "봉인물 검수 김 영감 실제 클릭 → 대화"):
		return
	if not t.check(await t.talk_pick("shop"), "거래한다 실제 선택 → 좌판"):
		return
	var vendor: Node = t.hud_panel("Vendor")
	t.check(await t.wait_until(func() -> bool: return vendor.visible and bag.visible, 2.0), "좌판·가방 실제 열림")
	var gold_before: int = inv.gold
	var stock_before: Array = vendor.stock().duplicate()
	grid = bag._grid_rect()
	for i in ids.size():
		await t.click(grid.position + Vector2(i + 0.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
		t.check(inv.grid.get(specimens[i]) == Vector2i(i, 0) and inv.gold == gold_before,
			"%s 실제 우클릭 판매 거부·같은 물건/엽전" % ids[i])
	t.check(vendor.stock() == stock_before, "봉인물 판매 거부 후 재고 그대로")
	await t.mouse_move(grid.position + Vector2(1.5, 0.5) * bag.CELL)
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("장산범의 봉인고리"), 1.0), "좌판 열린 가방 봉인고리 실제 호버")
	t.check(not tip.current_rect.intersects(tip.source_rect), "봉인고리 툴팁이 원래 칸을 가리지 않음")
	await t.frames(2)
	await t.shot("seal_vendor_refused")
	await t.close_all()
	t.main.load_area(AreaDb.TOWN, 0, Level.SpawnHint.FROM_ENTRY)
	await t.frames(4)
	var p: Node3D = t.player()
	seed(E2e.SEED)
	for it in specimens:
		inv.grid.erase(it)
		EventBus.loot_dropped.emit(it, p.global_position + Vector3(1.6, 1.0, 1.6))
	inv.notify_changed()
	var floors: Array[FloorItem] = []
	for node in t.tree.get_nodes_in_group("floor_item"):
		if node is FloorItem and specimens.has(node.item):
			floors.append(node)
	t.check(await t.wait_until(func() -> bool:
		for fi in floors:
			if not fi.is_settled:
				return false
		return floors.size() == 3, 3.0), "봉인물3 실제 loot_dropped → 바닥 정착")
	await t.key_down(KEY_ALT)
	await t.frames(5)
	for i in specimens.size():
		var floor: FloorItem = null
		for fi in floors:
			if is_instance_valid(fi) and fi.item == specimens[i]:
				floor = fi
				break
		if not t.check(floor != null, "%s 바닥 표본 존재" % ids[i]):
			continue
		var label: Label3D = floor.get_node("Label")
		var at: Vector2 = t.screen_of(label.global_position)
		await t.mouse_move(at)
		t.check(await t.wait_until(func() -> bool: return GameState.hover == floor, 1.0), "%s 실제 이름표 호버" % ids[i])
		var floor_id: int = floor.get_instance_id()
		await t.click(at)
		t.check(await t.wait_until(func() -> bool:
			var node := instance_from_id(floor_id) as Node
			return node == null or node.is_queued_for_deletion(), 5.0), "%s 이름표 클릭 → 걸어가 회수" % ids[i])
		t.check(inv.grid.has(specimens[i]) and specimens[i].stack == 1 and inv.grid.get(specimens[i]) == Vector2i(i, 0),
			"%s 회수 → 같은 물건·쌓기1·원자리, 병합 안 함" % ids[i])
	await t.key_up(KEY_ALT)
	await t.key(KEY_I)
	await t.wait_until(func() -> bool: return t.camera().call("ui_framing_settled"), 1.0)
	await t.mouse_move(bag._grid_rect().position + Vector2(2.5, 0.5) * bag.CELL)
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("불가살이의 사슬 조각"), 1.0), "회수한 사슬 조각 실제 가방 호버")
	await t.frames(2)
	await t.shot("seal_drop_recovered")
	await t.close_all()
