## #453: 승인 재료6종의 실제 가방·할매 좌판·이름표 줍기를 같은 표본으로 촬영한다.
func _material_review() -> void:
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
	var ids := ["goehwangji", "gyeongmyeonjusa", "heukrang_tooth", "jangsanbeom_fur", "bulgasari_scale", "gumiho_tail"]
	var quantities := [18, 7, 3, 2, 4, 5]
	var specimens: Dictionary = {}
	var before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()
	for i in ids.size():
		var id: String = ids[i]
		var it := ItemInstance.create(ItemDb.get_def(id), quantities[i])
		specimens[id] = it
		t.check(inv.place(it, Vector2i(i, 0)), "%s 재료 1×1 실제 배치" % id)
		if not before:
			t.check(it.def.icon != null and it.def.icon.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % id,
				"%s ItemDb → 승인 #452 PNG" % id)
	for i in 3:
		var anchor_id: String = ["satgat", "piju", "injang"][i]
		t.check(inv.place(ItemInstance.create(ItemDb.get_def(anchor_id)), Vector2i(i * 2, 2)), "%s 기존 기준물체 배치" % anchor_id)
	for key in WORN:
		inv.equip(key, ItemInstance.create(ItemDb.get_def(WORN[key])))
	inv.gold = 3750
	inv.notify_changed()
	await t.key(KEY_I)
	var grid: Rect2 = bag._grid_rect()
	await t.mouse_move(grid.position + Vector2(2.5, 0.5) * bag.CELL)
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("흑랑 이빨"), 1.0), "흑랑 이빨 실제 가방 호버")
	t.check(not tip.current_rect.intersects(tip.source_rect), "재료 툴팁이 원래 칸을 가리지 않음")
	await t.frames(2)
	await t.shot("material_inventory")
	# 종이를 집어서 원래 자리에 되놓은 뒤, 다른 종이3장과 합친다. 최대20·남은1장도 실제 클릭 경로다.
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == specimens.goehwangji and not inv.grid.has(specimens.goehwangji), "괴황지 클릭 → 같은 스택18 커서")
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(specimens.goehwangji) == Vector2i.ZERO, "괴황지 되놓기 → 원래 칸")
	var extra := ItemInstance.create(ItemDb.get_def("goehwangji"), 3)
	inv.place(extra, Vector2i(0, 1))
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	await t.click(grid.position + Vector2(0.5, 1.5) * bag.CELL)
	t.check(extra.stack == 20 and bag.held == specimens.goehwangji and bag.held.stack == 1, "18+3 → 쌓기20·커서1장, 원래 한도 유지")
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.has(specimens.goehwangji), "병합 나머지1장 되놓기")
	await t.close_all()
	# 그림 때문에 상품 목록이 달라지지 않는다. 해금 전/후 실제 npc_stock과 실제 대화 길을 사용한다.
	GameState.flags["boss_killed_heukrang_gul"] = false
	t.check(Vendor.npc_stock("shaman", GameState.flags).is_empty(), "흑랑 처치 전 할매 재료 진열 없음")
	GameState.flags["boss_killed_heukrang_gul"] = true
	var shaman: Node3D = null
	for npc in t.tree.get_nodes_in_group("npc"):
		if "def" in npc and npc.def and npc.def.id == "shaman":
			shaman = npc
			break
	if not t.check(shaman != null and await t.talk_to(shaman), "무당 할매 실제 클릭 → 대화"):
		return
	if not t.check(await t.talk_pick("shop"), "부적을 산다 실제 선택 → 좌판"):
		return
	var vendor: Node = t.hud_panel("Vendor")
	t.check(await t.wait_until(func() -> bool: return vendor.visible and bag.visible, 2.0), "할매 좌판·가방 함께 열림")
	var stock: Array = vendor.stock()
	var goe_row := -1
	var jusa_row := -1
	var has_boss_material := false
	for i in stock.size():
		if stock[i].def.id == "goehwangji":
			goe_row = i
		elif stock[i].def.id == "gyeongmyeonjusa":
			jusa_row = i
		elif String(stock[i].def.id) in ids.slice(2):
			has_boss_material = true
	if not t.check(goe_row >= 0 and jusa_row >= 0 and not has_boss_material, "해금된 실제 진열 = 일반 재료2·보스 재료4 없음"):
		return
	await t.mouse_move(vendor._row_rect(jusa_row).get_center())
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("경면주사"), 1.0), "실제 좌판 경면주사 호버")
	t.check(tip.source_rect.is_equal_approx(vendor._row_rect(jusa_row)) and not tip.current_rect.intersects(tip.source_rect), "좌판 툴팁이 현재 행을 가리지 않음")
	await t.frames(2)
	await t.shot("material_vendor")
	var gold_before: int = inv.gold
	var jusa_before: int = specimens.gyeongmyeonjusa.stack
	await t.click(vendor._row_rect(jusa_row).get_center())
	t.check(inv.gold == gold_before - 25 and specimens.gyeongmyeonjusa.stack == jusa_before + 1, "주사 구매 → 기존 스택+1·25엽전 차감")
	gold_before = inv.gold
	await t.click(vendor._row_rect(goe_row).get_center())
	t.check(inv.gold == gold_before - 10 and specimens.goehwangji.stack == 2, "괴황지 구매 → 남은 스택1+1·10엽전 차감")
	var tail: ItemInstance = specimens.gumiho_tail
	var sale: int = Vendor.sell_price(tail)
	gold_before = inv.gold
	await t.click(bag._grid_rect().position + Vector2(5.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(not inv.grid.has(tail) and inv.gold == gold_before + sale, "보스 재료 스택5 실제 우클릭 판매·기존 가격")
	# 세 번째 검수에는 팔기 전과 같은 보스 표본을 되돌린다. 제품 정의/재고에는 쓰지 않는다.
	inv.place(tail, Vector2i(5, 0))
	await t.close_all()
	t.main.load_area(AreaDb.TOWN, 0, Level.SpawnHint.FROM_ENTRY)
	await t.frames(4)
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
		return fis.size() == 6, 3.0), "재료6 실제 loot_dropped → 바닥 정착")
	await t.key_down(KEY_ALT)
	await t.frames(5)
	var fang: FloorItem = null
	for fi in fis:
		if fi.item == drops[2]:
			fang = fi
			break
	if not t.check(fang != null, "흑랑 이빨 드랍 존재"):
		await t.key_up(KEY_ALT)
		return
	var label: Label3D = fang.get_node("Label")
	var at: Vector2 = t.screen_of(label.global_position)
	await t.mouse_move(at)
	t.check(await t.wait_until(func() -> bool: return GameState.hover == fang, 1.0), "실제 바닥 이름표 호버 = 흑랑 이빨")
	var fid: int = fang.get_instance_id()
	var tooth_before: int = specimens.heukrang_tooth.stack
	await t.click(at)
	t.check(await t.wait_until(func() -> bool:
		var node := instance_from_id(fid) as Node
		return node == null or node.is_queued_for_deletion(), 5.0), "이름표 클릭 → 걸어가 이빨 회수")
	t.check(specimens.heukrang_tooth.stack == tooth_before + 1 and inv.grid.has(specimens.heukrang_tooth), "회수한 이빨은 기존 스택3→4 병합")
	var remaining := 0
	for fi in fis:
		if is_instance_valid(fi) and not fi.is_queued_for_deletion():
			remaining += 1
	t.check(remaining == 5, "선택한 이빨만 회수·다른5종은 바닥 보존")
	await t.key(KEY_I)
	await t.wait_until(func() -> bool: return t.camera().call("ui_framing_settled"), 1.0)
	await t.mouse_move(bag._grid_rect().position + Vector2(2.5, 0.5) * bag.CELL)
	t.check(await t.wait_until(func() -> bool: return _t1_tip_name(tip).contains("흑랑 이빨"), 1.0), "드랍 회수 후 같은 그림/이름 가방 호버")
	await t.frames(2)
	await t.shot("material_drop_recovered")
	await t.key_up(KEY_ALT)
	for fi in fis:
		if is_instance_valid(fi):
			fi.queue_free()
	await t.close_all()
