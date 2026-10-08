extends E2eScenario
## #439: 채택 11종·9칸 장비·세 스킬 트리를 같은 자리에서 촬영한다.
## --icon-intake-before는 반입 전 동일 표본 촬영용이다.

const ITEMS := {
	"hwando": Vector2i(0, 0), "cotton_dopo": Vector2i(1, 0),
	"leather_shoes": Vector2i(3, 0), "paeraengi": Vector2i(5, 0),
	"mukham": Vector2i(7, 0), "cotton_belt": Vector2i(8, 0),
	"silver_ring": Vector2i(8, 1), "jade_charm": Vector2i(9, 1),
	"hp_potion": Vector2i(3, 2), "mp_potion": Vector2i(4, 2),
	"talisman_fire": Vector2i(5, 2),
}
const WORN := {
	"weapon": "hwando", "armor": "cotton_dopo", "boots": "leather_shoes",
	"head": "paeraengi", "offhand": "mukham", "belt": "cotton_belt",
	"ring1": "silver_ring", "ring2": "silver_ring", "amulet": "jade_charm",
}


func run() -> void:
	if "--icon-intake-466-only" in OS.get_cmdline_user_args():
		var review := preload("res://tests/e2e/helpers/approved_icons_466.gd").new()
		review.setup(t)
		await review.run()
		return

	if "--icon-intake-sword-only" in OS.get_cmdline_user_args():
		var was_dev: bool = DevMode.is_active
		var help_text: String = t.main.hud_label.text
		DevMode.is_active = false
		t.main.hud_label.text = ""
		await _sword_review()
		DevMode.is_active = was_dev
		t.main.hud_label.text = help_text
		await t.close_all()
		return

	if "--icon-intake-seal-only" in OS.get_cmdline_user_args():
		var was_dev: bool = DevMode.is_active
		var help_text: String = t.main.hud_label.text
		DevMode.is_active = false
		t.main.hud_label.text = ""
		await _seal_review()
		DevMode.is_active = was_dev
		t.main.hud_label.text = help_text
		await t.close_all()
		return

	if "--icon-intake-material-only" in OS.get_cmdline_user_args():
		var was_dev: bool = DevMode.is_active
		var help_text: String = t.main.hud_label.text
		DevMode.is_active = false
		t.main.hud_label.text = ""
		await _material_review()
		DevMode.is_active = was_dev
		t.main.hud_label.text = help_text
		await t.close_all()
		return

	if "--icon-intake-t2-only" in OS.get_cmdline_user_args():
		var was_dev: bool = DevMode.is_active
		var help_text: String = t.main.hud_label.text
		DevMode.is_active = false
		t.main.hud_label.text = ""
		await _t2_review()
		DevMode.is_active = was_dev
		t.main.hud_label.text = help_text
		await t.close_all()
		return
	await t.close_all()
	var bag: Node = t.hud_panel("Inventory")
	var tree_ui: Node = t.hud_panel("SkillTree")
	var inv: Inventory = GameState.inventory
	var p: Node = t.player()
	inv.clear_all()
	GameState.character.level = 10
	GameState.character.str = 45
	GameState.character.dex = 40
	GameState.character.spi = 40
	GameState.character.skill_points = 2
	p.combat.recompute_stats()
	var specimens: Dictionary = {}
	for id in ITEMS:
		var it := ItemInstance.create(ItemDb.get_def(id))
		specimens[id] = it
		t.check(inv.place(it, ITEMS[id]), "%s 다칸 물체 표본 배치" % id)
	for key in WORN:
		var it := ItemInstance.create(ItemDb.get_def(WORN[key]))
		var result: Dictionary = inv.equip(key, it)
		t.check(result.ok, "%s 실제 장비 칸 표본" % key)
	inv.belt_put(0, ItemInstance.create(ItemDb.get_def("hp_potion"), 3))
	inv.belt_put(1, ItemInstance.create(ItemDb.get_def("mp_potion"), 3))
	inv.belt_put(2, ItemInstance.create(ItemDb.get_def("talisman_fire"), 2))
	inv.gold = 1250
	inv.notify_changed()
	var old_dev: bool = DevMode.is_active
	var old_help: String = t.main.hud_label.text
	DevMode.is_active = false
	t.main.hud_label.text = ""
	await t.key(KEY_I)
	await t.mouse_move(Vector2(620, 550))
	await t.frames(2)
	await t.shot("inventory")
	# 실제 입력으로 긴 환도를 집어 든다. 빈 한 칸·잡기 그림에서도 물체의 비율을 확인한다.
	var sword: ItemInstance = specimens.hwando
	var source_cell: Vector2 = bag._grid_rect().position + Vector2(0.5, 0.5) * bag.CELL
	await t.click(source_cell)
	t.check(bag.held == sword and not inv.grid.has(sword), "환도 좌클릭 → 커서 물체·가방에서 빠짐")
	await t.mouse_move(bag._grid_rect().position + Vector2(8.5, 3.5) * bag.CELL)
	await t.frames(2)
	await t.shot("held_swap")
	await t.click(source_cell)
	t.check(bag.held == null and inv.grid.get(sword) == ITEMS.hwando, "환도 되놓기 → 원래 1×3 자리·물체 보존")
	await t.key(KEY_I)
	await t.key(KEY_K)
	for tab_id in ["sword", "body", "talisman"]:
		await t.click(tree_ui.tab_rect(tab_id).get_center())
		t.check(tree_ui.tab == tab_id, "%s 실제 탭 입력" % tab_id)
		await t.mouse_move(Vector2(620, 550))
		await t.frames(2)
		await t.shot("skills_" + tab_id)
	# 새 그림은 준비 중 기능을 켜지 않는다. 클릭 후 포인트/실제 선택이 그대로여야 한다.
	var old_points: int = GameState.character.skill_points
	var old_skill: int = p.combat.active_skill
	# 부적술 탭의 준비 중 칸 = 벽력부 익히기 (화염부·빙결부 익히기는 #477에서 켜져 누르면 찍힌다)
	for tab_id in ["body", "talisman"]:
		await t.click(tree_ui.tab_rect(tab_id).get_center())
		var id: String = "mana_shield" if tab_id == "body" else "thunder_lore"
		await t.click(tree_ui.btn_rect_for(id).get_center())
	t.check(GameState.character.skill_points == old_points and p.combat.active_skill == old_skill,
		"도력 방패·벽력부 익히기(준비 중)를 눌러도 준비 중 상태·포인트·선택 유지")
	await _t1_review()
	await _t2_review()
	await _material_review()
	await _seal_review()
	await _sword_review()
	DevMode.is_active = old_dev
	t.main.hud_label.text = old_help
	await t.close_all()


## 15종 각각 실제 입력·거래·바닥 습득을 도는 전용 판만 180초. 기존 대본은 60초 그대로.
func timeout_sec() -> float:
	return 180.0 if "--icon-intake-466-only" in OS.get_cmdline_user_args() else 60.0


## #447: 같은 T1 표본으로 가방·장비·커서·좌판을 반입 전후 비교한다.
## before 플래그는 옛 glyph/공용 PNG도 촬영하게 한다. 게임 ItemDef 자체는 바꾸지 않는다.
func _t1_review() -> void:
	await t.close_all()
	var bag: Node = t.hud_panel("Inventory")
	var tip: Node = t.main.get_node("HUD/Tooltip")
	var inv: Inventory = GameState.inventory
	inv.clear_all()
	var positions := {
		"satgat": Vector2i(0, 0), "piju": Vector2i(2, 0), "injang": Vector2i(4, 0),
		"yedo": Vector2i(5, 0), "mituri": Vector2i(6, 0), "jeondae": Vector2i(8, 0),
		"paeraengi": Vector2i(0, 2), "leather_shoes": Vector2i(2, 2), "cotton_belt": Vector2i(8, 1),
	}
	var specimens: Dictionary = {}
	var before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()
	for id in positions:
		var it := ItemInstance.create(ItemDb.get_def(id))
		specimens[id] = it
		t.check(inv.place(it, positions[id]), "%s T1/승인 기준물체 실제점유 배치" % id)
		if positions.keys().find(id) < 6 and not before:
			t.check(it.def.icon != null and it.def.icon.resource_path == "res://assets/sprites/ui/icons_a/items/%s.png" % id,
				"%s 실제 ItemDb → 승인 아이콘 로드" % id)
	# 미식별/매직 덮개는 ItemInstance만 고정한다. 공유 ItemDef의 수치/아이콘은 그대로다.
	specimens.piju.rarity = ItemInstance.Rarity.MAGIC
	specimens.piju.affixes.assign([{"id": "sturdy", "v": 2.0}])
	specimens.injang.rarity = ItemInstance.Rarity.RARE
	specimens.injang.identified = false
	specimens.injang.rare_name = "보이지 않는 인장"
	var worn := {
		"weapon": "yedo", "armor": "cotton_dopo", "boots": "mituri", "head": "satgat",
		"offhand": "injang", "belt": "jeondae", "ring1": "silver_ring", "ring2": "silver_ring", "amulet": "jade_charm",
	}
	for key in worn:
		var result: Dictionary = inv.equip(key, ItemInstance.create(ItemDb.get_def(worn[key])))
		t.check(result.ok, "%s T1 실제 장비 칸" % key)
	inv.gold = 1250
	inv.notify_changed()
	await t.key(KEY_I)
	await t.mouse_move(Vector2(620, 550))
	await t.frames(2)
	await t.shot("t1_inventory")
	# 1×3 예도의 마지막 점유 칸에서도 동일한 물건을 집고 원래 자리로 되놓는다.
	var grid: Rect2 = bag._grid_rect()
	await t.click(grid.position + Vector2(5.5, 2.5) * bag.CELL)
	t.check(bag.held == specimens.yedo and not inv.grid.has(specimens.yedo), "예도 마지막 칸 클릭 → 같은 물체 held")
	t.check(not tip.current_rect.has_area(), "held 예도는 이전 툴팁을 지움")
	await t.mouse_move(grid.position + Vector2(9.5, 3.5) * bag.CELL)
	await t.frames(2)
	await t.shot("t1_held")
	await t.click(grid.position + Vector2(5.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(specimens.yedo) == positions.yedo, "예도 되놓기 → 원래 1×3 점유 보존")
	# 피주 우클릭은 실제 머리 장착이다. 기존 삿갓은 피주의 원래 2×2 자리로 돌아온다.
	var old_head: ItemInstance = inv.equipment.head
	await t.click(grid.position + Vector2(2.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.head == specimens.piju and inv.grid.get(old_head) == positions.piju,
		"피주 우클릭 장착 → 삿갓 원자리 교체, 비율/입력 동일")
	await t.click(grid.position + Vector2(2.5, 0.5) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(inv.equipment.head == old_head and inv.grid.get(specimens.piju) == positions.piju, "삿갓 재장착 → 피주 원자리 복원")
	await t.close_all()
	var merchant: Node3D = null
	for npc in t.tree.get_nodes_in_group("npc"):
		if "def" in npc and npc.def and npc.def.id == "merchant":
			merchant = npc
			break
	if not t.check(merchant != null, "T1 좌판 검수 김 영감 있음"):
		return
	if not t.check(await t.talk_to(merchant), "김 영감 실제 클릭 → 대화"):
		return
	if not t.check(await t.talk_pick("shop"), "거래한다 실제 클릭 → 좌판"):
		return
	var vendor: Node = t.hud_panel("Vendor")
	t.check(await t.wait_until(func() -> bool: return vendor.visible and bag.visible, 2.0), "좌판과 가방 실제 열림")
	var stock: Array[ItemInstance] = []
	for id in ["satgat", "piju", "injang", "yedo", "mituri", "jeondae"]:
		stock.append(ItemInstance.create(ItemDb.get_def(id)))
	GameState.vendor_stock = stock
	inv.notify_changed()
	await t.mouse_move(vendor._row_rect(2).get_center())
	t.check(await t.wait_until(func() -> bool: return tip.current_rect.has_area() and _t1_tip_name(tip).contains("인장"), 1.0),
		"48px 좌판 인장 호버 → 현재 물건 툴팁")
	t.check(tip.source_rect.is_equal_approx(vendor._row_rect(2)), "좌판 툴팁 source는 인장 전체 행")
	t.check(not tip.current_rect.intersects(tip.source_rect), "좌판 툴팁이 인장 그림/행을 가리지 않음")
	await t.frames(2)
	await t.shot("t1_vendor_tooltip")
	var bought: ItemInstance = stock[1]
	var gold_before: int = inv.gold
	var price: int = Vendor.buy_price(bought)
	await t.click(vendor._row_rect(1).get_center())
	t.check(inv.grid.has(bought) and inv.gold == gold_before - price and not stock.has(bought), "피주 행 실제 구매 → 같은 물건/가격/재고 이동")
	var sale: int = Vendor.sell_price(bought)
	await t.click(bag._grid_rect().position + (Vector2(inv.grid[bought]) + Vector2(0.5, 0.5)) * bag.CELL, MOUSE_BUTTON_RIGHT)
	t.check(not inv.grid.has(bought) and inv.gold == gold_before - price + sale, "새 피주 그림 실제 우클릭 판매 → 같은 물건/가격")
	await t.close_all()


func _t1_tip_name(tip: Node) -> String:
	for row in tip.current_rows:
		if String(row.role) == "name":
			return String(row.text)
	return ""


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
		"벽력부 가방 우클릭은 마을 진입 거절·수량 보존 (#451)")
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
	var safety_before: bool = "--quest-safety-before" in OS.get_cmdline_user_args()
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
	_quest_tooltip_rules(tip, safety_before, false)
	await t.shot("seal_inventory")
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == specimens[0] and not inv.grid.has(specimens[0]), "봉인패 클릭 → 같은 물건 커서")
	await t.click(grid.position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == null and inv.grid.get(specimens[0]) == Vector2i.ZERO, "봉인패 되놓기 → 원래 칸")
	await _quest_cursor_guards(specimens, safety_before)
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
	_quest_tooltip_rules(tip, safety_before, true)
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
	_quest_tooltip_rules(tip, safety_before, false)
	await t.shot("seal_drop_recovered")
	await t.close_all()
	await _quest_safety_fallbacks(specimens)


## #458: before는 옛 결함을 재현·복구하는 검수 모드. 실제 게임 입력 규칙은 바꾸지 않는다.
func _quest_tooltip_rules(tip: Node, baseline: bool, selling: bool) -> void:
	var hints := ""
	var price := ""
	for row in tip.current_rows:
		if row.role == "hint":
			hints += String(row.text) + "\n"
		elif row.role == "price":
			price += String(row.text)
	if baseline:
		t.check(hints.contains("들고 창 밖 클릭: 버림"), "before: 퀘스트 물건에도 버림 안내가 있는 결함 재현")
		t.check(price.contains("판매가") if selling else price.is_empty(), "before: 좌판 열린 가방의 불가능한 판매가 재현")
	else:
		t.check(hints.contains("좌클릭: 들기") and hints.contains("퀘스트 물건 · 팔기·버리기 불가"), "퀘스트 들기·팔기/버리기 불가 안내")
		t.check(not hints.contains("클릭: 버림") and not hints.contains("클릭: 판매") and not hints.contains("모두 판매"), "불가능한 버림·판매 동작 안내 없음")
		t.check(price.is_empty(), "좌판 유무와 관계없이 퀘스트 판매가 없음")


func _quest_cursor_guards(specimens: Array[ItemInstance], baseline: bool) -> void:
	var bag: Node = t.hud_panel("Inventory")
	var inv: Inventory = GameState.inventory
	var grid: Rect2 = bag._grid_rect()
	var start: Vector3 = t.player().global_position
	var gold: int = inv.gold
	var floors: int = t.tree.get_nodes_in_group("floor_item").size()
	for i in specimens.size():
		var at: Vector2 = grid.position + Vector2(i + 0.5, 0.5) * bag.CELL
		await t.click(at)
		t.check(bag.held == specimens[i], "퀘스트 창 밖 검수: 같은 물건을 들기")
		await t.click(Vector2(700, 480))
		var fallen := _quest_floor(specimens[i])
		if baseline:
			t.check(bag.held == null and fallen != null and not inv.grid.has(specimens[i]), "before: 실제 창 밖 클릭으로 퀘스트 물건이 버려지는 결함 재현")
			if fallen != null:
				fallen.queue_free()
				await t.frames(2)
			t.check(inv.place(specimens[i], Vector2i(i, 0)), "before 표본만 복구: 버려진 같은 물건을 원래 칸에")
			inv.notify_changed()
		else:
			t.check(bag.held == specimens[i] and fallen == null and not inv.grid.has(specimens[i]), "창 밖 버림 거부: 같은 물건 커서 유지·바닥 생성 없음")
			t.check(bag._msg == "퀘스트 물건은 버릴 수 없다", "창 밖 버림 거부 문구")
			await t.click(at)
			t.check(bag.held == null and inv.grid.get(specimens[i]) == Vector2i(i, 0), "거부 뒤 실제 되놓기: 같은 물건·원래 칸")
		t.check(t.player().global_position.distance_to(start) < 0.02 and inv.gold == gold, "창 밖 클릭을 월드 이동/거래로 넘기지 않음")
	t.check(t.tree.get_nodes_in_group("floor_item").size() == floors, "퀘스트 창 밖 검수 뒤 바닥 물건 수 보존")


func _quest_floor(item: ItemInstance) -> FloorItem:
	for node in t.tree.get_nodes_in_group("floor_item"):
		if node is FloorItem and node.item == item:
			return node
	return null


func _quest_safety_fallbacks(specimens: Array[ItemInstance]) -> void:
	var bag: Node = t.hud_panel("Inventory")
	var inv: Inventory = GameState.inventory
	await t.key(KEY_I)
	# 일반 물건은 기존처럼 직접 버릴 수 있다. 준비만 데이터로, 조작은 실제 입력으로.
	var normal := ItemInstance.create(ItemDb.get_def("hp_potion"), 3)
	t.check(inv.place(normal, Vector2i(3, 0)), "일반 물약3 검수 표본 배치")
	inv.notify_changed()
	await t.click(bag._grid_rect().position + Vector2(3.5, 0.5) * bag.CELL)
	await t.click(Vector2(700, 480))
	var normal_floor := _quest_floor(normal)
	t.check(bag.held == null and normal_floor != null and normal.stack == 3, "일반 물건 창 밖 버림은 유지·수량3 보존")
	if normal_floor != null:
		normal_floor.queue_free()
		await t.frames(2)
	# 창을 닫는 안전망은 직접 버리기와 별도다. 회수 불가를 만들지 않는다.
	await t.click(bag._grid_rect().position + Vector2(0.5, 0.5) * bag.CELL)
	t.check(bag.held == specimens[0], "꽉 찬 가방 안전망: 퀘스트 물건 들기")
	for y in Inventory.ROWS:
		for x in Inventory.COLS:
			if inv.item_at(Vector2i(x, y)) == null:
				inv.place(ItemInstance.create(ItemDb.get_def("hp_potion"), 10), Vector2i(x, y))
	inv.notify_changed()
	await t.key(KEY_I)
	var quest_floor := _quest_floor(specimens[0])
	t.check(not bag.visible and bag.held == null and quest_floor != null and not inv.grid.has(specimens[0]), "창 닫기·가방 가득 참: 같은 퀘스트 물건을 발밑에 보존")
	if quest_floor == null:
		return
	var filler: ItemInstance = inv.item_at(Vector2i.ZERO)
	inv.remove(filler)
	inv.notify_changed()
	t.check(await t.wait_until(func() -> bool: return quest_floor.is_settled and t.camera().call("ui_framing_settled"), 3.0), "안전망 물건 정착·카메라 완료")
	await t.key_down(KEY_ALT)
	await t.frames(5)
	var label: Label3D = quest_floor.get_node("Label")
	var at: Vector2 = t.screen_of(label.global_position)
	await t.mouse_move(at)
	t.check(await t.wait_until(func() -> bool: return GameState.hover == quest_floor, 1.0), "안전망 물건 실제 이름표 호버")
	var floor_id: int = quest_floor.get_instance_id()
	await t.click(at)
	t.check(await t.wait_until(func() -> bool:
		var node := instance_from_id(floor_id) as Node
		return node == null or node.is_queued_for_deletion(), 5.0), "안전망 물건 이름표 클릭 → 회수")
	t.check(inv.grid.has(specimens[0]) and specimens[0].stack == 1, "회수 뒤 같은 퀘스트 물건·쌓기1·소실 없음")
	await t.key_up(KEY_ALT)


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
