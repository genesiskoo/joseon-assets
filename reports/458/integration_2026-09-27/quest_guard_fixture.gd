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
