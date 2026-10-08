## #450: 승인 T2 4·소모품 2를 실제 가방/장비/좌판/커서에서 전후 비교한다.
func _t2_review() -> void:
	await t.close_all()
	var bag: Node = t.hud_panel("Inventory")
	var tip: Node = t.main.get_node("HUD/Tooltip")
	var inv: Inventory = GameState.inventory
	var p: Node = t.player()
	var pc: Node = p.combat
	inv.clear_all()
	GameState.character.level = 10
	GameState.character.str = 45
	GameState.character.dex = 40
	GameState.character.spi = 40
	pc.recompute_stats()
	var positions := {
		"jeongjagwan": Vector2i(0, 0), "cheomju": Vector2i(2, 0), "yundo": Vector2i(4, 0),
		"bujeok_mokpan": Vector2i(6, 0), "rejuv": Vector2i(8, 0), "talisman_thunder": Vector2i(9, 0),
		"satgat": Vector2i(0, 2), "piju": Vector2i(2, 2), "injang": Vector2i(4, 2),
	}
	var specimens: Dictionary = {}
	var before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()
	for id in positions:
		var it := ItemInstance.create(ItemDb.get_def(id), 2 if id in ["rejuv", "talisman_thunder"] else 1)
		specimens[id] = it
		t.check(inv.place(it, positions[id]), "%s T2/승인 기준물체 점유 배치" % id)
		if positions.keys().find(id) < 6 and not before:
			t.check(it.def.icon != null and it.def.icon.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % id,
				"%s 실제 ItemDb → 승인 #448 아이콘 로드" % id)
	specimens.cheomju.rarity = ItemInstance.Rarity.MAGIC
	specimens.cheomju.affixes.assign([{"id": "sturdy", "v": 2.0}])
	specimens.bujeok_mokpan.rarity = ItemInstance.Rarity.RARE
	specimens.bujeok_mokpan.identified = false
	specimens.bujeok_mokpan.rare_name = "보이지 않는 목판"
	var worn := {
		"weapon": "yedo", "armor": "cotton_dopo", "boots": "mituri", "head": "jeongjagwan",
		"offhand": "yundo", "belt": "jeondae", "ring1": "silver_ring", "ring2": "silver_ring", "amulet": "jade_charm",
	}
	for key in worn:
		var result: Dictionary = inv.equip(key, ItemInstance.create(ItemDb.get_def(worn[key])))
		t.check(result.ok, "%s T2 실제 장비 칸" % key)
	inv.gold = 3750
	inv.notify_changed()
	await t.key(KEY_I)
	await t.mouse_move(Vector2(620, 550))
	await t.frames(2)
	await t.shot("t2_inventory")
	var grid: Rect2 = bag._grid_rect()
	await t.click(grid.position + Vector2(5.5, 1.5) * bag.CELL)
	t.check(bag.held == specimens.yundo and not inv.grid.has(specimens.yundo), "윤도 마지막 점유 칸 → 같은 2×2 물체 held")
	t.check(not tip.current_rect.has_area(), "held 윤도는 이전 툴팁을 지움")
	await t.mouse_move(grid.position + Vector2(9.5, 3.5) * bag.CELL)
	await t.frames(2)
	await t.shot("t2_held")
	await t.click(grid.position + Vector2(4.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(specimens.yundo) == positions.yundo, "윤도 되놓기 → 원래 2×2 점유 보존")
	var old_head: ItemInstance = inv.equipment.head
	await t.click(grid.position + Vector2(2.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.head == specimens.cheomju and inv.grid.get(old_head) == positions.cheomju,
		"첨주 우클릭 장착 → 정자관 원자리 교체")
	await t.click(grid.position + Vector2(2.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.head == old_head and inv.grid.get(specimens.cheomju) == positions.cheomju, "정자관 재장착 → 첨주 원자리 복원")
	await t.close_all()
	var merchant: Node3D = null
	for npc in t.tree.get_nodes_in_group("npc"):
		if "def" in npc and npc.def and npc.def.id == "merchant":
			merchant = npc
			break
	if not t.check(merchant != null, "T2 좌판 검수 김 영감 있음"):
		return
	if not t.check(await t.talk_to(merchant), "김 영감 실제 클릭 → 대화"):
		return
	if not t.check(await t.talk_pick("shop"), "거래한다 실제 클릭 → 좌판"):
		return
	var vendor: Node = t.hud_panel("Vendor")
	t.check(await t.wait_until(func() -> bool: return vendor.visible and bag.visible, 2.0), "T2 좌판과 가방 실제 열림")
	var stock: Array[ItemInstance] = []
	for id in ["jeongjagwan", "cheomju", "yundo", "bujeok_mokpan", "rejuv", "talisman_thunder"]:
		stock.append(ItemInstance.create(ItemDb.get_def(id)))
	GameState.vendor_stock = stock
	inv.notify_changed()
	await t.mouse_move(vendor._row_rect(2).get_center())
	t.check(await t.wait_until(func() -> bool: return tip.current_rect.has_area() and _t1_tip_name(tip).contains("윤도"), 1.0),
		"48px 좌판 윤도 호버 → 현재 물건 툴팁")
	t.check(tip.source_rect.is_equal_approx(vendor._row_rect(2)), "좌판 툴팁 source는 윤도 전체 행")
	t.check(not tip.current_rect.intersects(tip.source_rect), "좌판 툴팁이 윤도 그림/행을 가리지 않음")
	await t.frames(2)
	await t.shot("t2_vendor_tooltip")
	var bought: ItemInstance = stock[1]
	var gold_before: int = inv.gold
	var price: int = Vendor.buy_price(bought)
	await t.click(vendor._row_rect(1).get_center())
	t.check(inv.grid.has(bought) and inv.gold == gold_before - price and not stock.has(bought), "첨주 행 실제 구매 → 같은 물건/가격/재고 이동")
	var sale: int = Vendor.sell_price(bought)
	await t.click(bag._grid_rect().position + (Vector2(inv.grid[bought]) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(not inv.grid.has(bought) and inv.gold == gold_before - price + sale, "첨주 그림 실제 우클릭 판매 → 같은 물건/가격")
	await t.close_all()
	await _t2_consumables(specimens, positions)


func _t2_consumables(specimens: Dictionary, positions: Dictionary) -> void:
	var bag: Node = t.hud_panel("Inventory")
	var bar: Node = t.hud_panel("Bar")
	var inv: Inventory = GameState.inventory
	var p: Node = t.player()
	var pc: Node = p.combat
	await t.key(KEY_I)
	var grid: Rect2 = bag._grid_rect()
	# 실제 우클릭은 유지하고, 이 짧은 측정에서 자연 재생만 멈춘다.
	var was_processing: bool = pc.is_processing()
	pc.set_process(false)
	pc.hp = pc.max_hp * 0.2
	pc.mp = pc.max_mp * 0.2
	await t.click(grid.position + Vector2(8.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(is_equal_approx(pc.hp, pc.max_hp * 0.55) and is_equal_approx(pc.mp, pc.max_mp * 0.55),
		"청심환 실제 가방 우클릭 → HP/MP 각각 최대치 35% 즉시 회복")
	t.check(specimens.rejuv.stack == 1 and inv.grid.has(specimens.rejuv), "청심환 스택 2→1, 동일 물체 유지")
	pc.set_process(was_processing)
	await t.click(grid.position + Vector2(8.5, 0.5) * bag.CELL)
	await t.click(bar._belt_rect(0).get_center())
	t.check(bag.held == specimens.rejuv and inv.belt[0] == null, "청심환 실제 HUD 벨트 놓기 거절 → held/물체 보존")
	await t.click(grid.position + Vector2(8.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(specimens.rejuv) == positions.rejuv, "청심환 가방 원자리 복원")
	await t.click(grid.position + Vector2(9.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(specimens.talisman_thunder.stack == 2 and inv.grid.get(specimens.talisman_thunder) == positions.talisman_thunder and bag.held == null,
		"벽력부 가방 우클릭은 기존 무동작 유지")
	await t.click(grid.position + Vector2(9.5, 0.5) * bag.CELL)
	await t.click(bar._belt_rect(1).get_center())
	t.check(bag.held == null and inv.belt[1] == specimens.talisman_thunder and not inv.grid.has(specimens.talisman_thunder),
		"벽력부 실제 가방→HUD 벨트 이동, 동일 1×1 물체 보존")
	t.check(GameState.is_town(), "벽력부 제한 검사 출발 = 마을")
	await t.key(KEY_2)
	await t.click(bar._belt_rect(1).get_center(), MOUSE_BUTTON_RIGHT)
	t.check(specimens.talisman_thunder.stack == 2 and pc.talisman_cd == 0.0, "마을 벽력부 숫자키/벨트 우클릭 → 소비·쿨 없음")
	await t.close_all()
	var was_dev: bool = DevMode.is_active
	DevMode.is_active = true
	await t.go_down(1)
	await t.remove_enemies()
	DevMode.is_active = was_dev
	if not t.check(not GameState.is_town(), "벽력부 시전 검수 실제 던전 입장"):
		return
	p = t.player()
	pc = p.combat
	pc.stats["talisman_save"] = 0.0
	pc.mp = pc.max_mp
	t.check(not pc.is_dead() and not p.motion_locked() and pc.talisman_cd == 0.0, "벽력부 시전 가능 상태")
	await t.mouse_move(t.screen_of(p.global_position + Vector3(3, 0, 0)))
	await t.key(KEY_2)
	t.check(specimens.talisman_thunder.stack == 1 and pc.talisman_cd > 0.0 and is_equal_approx(pc.mp, pc.max_mp),
		"벽력부 실제 숫자키 시전 → 2→1·공용 쿨·MP 소비 없음")
	await t.key(KEY_2)
	t.check(specimens.talisman_thunder.stack == 1, "벽력부 쿨 중 재입력은 추가 소비 없음")
	t.check(await t.wait_until(func() -> bool: return is_instance_valid(pc.last_talisman), 2.0)
		and pc.last_talisman.def.id == "talisman_thunder", "벽력부 실제 lightning 부적 투사체 연결")
	await t.wait_until(func() -> bool: return not p.motion_locked(), 2.0)
	await t.close_all()
