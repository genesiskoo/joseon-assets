extends E2eScenario
## #721 capture-only registration: add _marketing_capture to E2eRunner.SCENARIOS.
const SLICE := "res://tests/e2e/scenarios/_slice_capture.gd"
const EFFECTS := "res://tests/e2e/scenarios/_marketing_effects.gd"
const EFFECT_CLIPS := {"effect_fire": "03_fire", "effect_cold": "04_cold", "effect_lightning": "08_lightning", "effect_flurry": "09_flurry", "effect_crit": "02_crit"}
var track := "cave"
var ui_on := true
var _hidden: Array[Node] = []
var _rng := RandomNumberGenerator.new()
const HIDE_CANVAS_BIT := 1 << 19
const HIDE_WORLD_BIT := 1 << 19

func timeout_sec() -> float:
	return 360.0

func area_title_on() -> bool:
	return true

func _arg(key: String, fallback: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with(key + "="):
			return a.substr(key.length() + 1)
	return fallback

func _mark(name: String, edge: String) -> void:
	print("CAPTURE %s %s %d" % [name, edge, Engine.get_process_frames()])

func _in_lab_hud(n: Node) -> bool:
	var parent := n.get_parent()
	while parent != null:
		if parent.name == "FeelLabHud":
			return true
		parent = parent.get_parent()
	return false

func _in_lab_station(n: Node) -> bool:
	var parent := n.get_parent()
	while parent != null:
		if parent.name == "FeelLabStations":
			return true
		parent = parent.get_parent()
	return false

func _is_world_label(n: Node) -> bool:
	# Includes Label3D children: floor-name plates and damage elemental/halo icons.
	var current := n
	while current != null:
		if current is Label3D:
			return true
		current = current.get_parent()
	return false

func _register_hidden(n: Node) -> void:
	if n is CanvasItem:
		_hidden.append(n)
		if not ui_on or _in_lab_hud(n):
			# Render-only exclusion: visible/input processing remains intact for hidden clicks.
			n.visibility_layer = HIDE_CANVAS_BIT
	elif n is GeometryInstance3D and (_in_lab_station(n) or (not ui_on and _is_world_label(n))):
		_hidden.append(n)
		# NPC and popup processing may rewrite visible/transparency each frame.
		# Layers exclude only rendering, retain nameplate input/colliders, and are stable.
		n.layers = HIDE_WORLD_BIT

func _visibility() -> void:
	t.main.hud_label.visible = false
	t.camera().cull_mask = t.camera().cull_mask & ~HIDE_WORLD_BIT
	for n in _hidden:
		if not is_instance_valid(n):
			continue
		if n is CanvasItem and (not ui_on or _in_lab_hud(n)):
			n.visibility_layer = HIDE_CANVAS_BIT
		elif n is GeometryInstance3D:
			n.layers = HIDE_WORLD_BIT

func _slice() -> Variant:
	var s = load(SLICE).new()
	s.setup(t)
	return s

func _npc(id: String) -> Node3D:
	for n in t.tree.get_nodes_in_group("npc"):
		if n.def.id == id:
			return n
	return null

func _stand(pos: Vector3) -> void:
	var near: Array = t.level().nearest_walkable(Level.world_to_cell(pos), 6)
	t.player().teleport_to(Level.cell_to_world(near[1]) if near[0] else pos)
	t.camera().snap_to_target()
	await t.seconds(0.5)

func _voice_line() -> bool:
	var b := t.band()
	var ok: bool = await t.wait_until(func() -> bool:
		return not b.is_open() or (not b.is_typing() and not Audio.voice_playing()), 75.0)
	t.check(ok, "Complete voice and text before dialogue advance")
	await t.seconds(0.4)
	return ok

func _voiced_choices() -> bool:
	var b := t.band()
	for i in 40:
		if not b.is_open():
			return false
		if not await _voice_line():
			return false
		if b.choices_shown():
			return true
		await t.key(KEY_SPACE)
		await t.frames(3)
	return false

func _pick(action: String) -> bool:
	var b := t.band()
	var index := b.choice_index(action)
	if not t.check(index >= 0, "Dialogue choice exists: " + action):
		return false
	await t.click(b.choice_rect(index).get_center())
	return true

func run() -> void:
	track = _arg("--marketing-track", "cave")
	ui_on = _arg("--marketing-ui", "on") == "on" and track != "screenshots"
	_rng.seed = 721
	seed(721)
	print("MARKETING INFO source=627061d8 track=%s ui=%s" % [track, "on" if ui_on else "off"])
	if track != "screenshots":
		# Movie Maker boot output is 1920x1080 (temporary override.cfg), while the
		# production UI/input contract remains its normal 1280x720 logical canvas.
		t.tree.root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
		t.tree.root.content_scale_size = Vector2i(1280, 720)
		t.tree.root.size = Vector2i(1920, 1080)
		await t.frames(4)
	t.tree.root.canvas_cull_mask = 0xFFFFF & ~HIDE_CANVAS_BIT
	Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)
	for n in t.tree.root.find_children("*", "CanvasItem", true, false):
		_register_hidden(n)
	for n in t.tree.root.find_children("*", "GeometryInstance3D", true, false):
		_register_hidden(n)
	t.tree.node_added.connect(_register_hidden)
	t.tree.process_frame.connect(_visibility)
	_visibility()
	await t.close_all()
	if track == "screenshots":
		await _photos()
	elif EFFECT_CLIPS.has(track):
		await _effect(EFFECT_CLIPS[track])
	elif track == "quest_accept":
		await _quest_accept()
	elif track == "quest_report":
		await _quest_report()
	elif track == "cave":
		await _cave()
	elif track == "boss":
		await _boss()
	elif track == "loot":
		await _loot()
	elif track == "attack":
		await _attack()
	elif track == "imugi":
		await _imugi()
	elif track == "check":
		t.check(ResourceLoader.exists(EFFECTS), "Capture helper present")
	else:
		t.check(false, "Unknown marketing track: " + track)
	t.tree.process_frame.disconnect(_visibility)
	t.tree.node_added.disconnect(_register_hidden)

func _quest_accept() -> void:
	var elder := _npc("elder")
	if not t.check(elder != null, "Town chief exists"):
		return
	await _stand(elder.global_position + Vector3(1.8, 0, 1.8))
	_mark("quest_accept", "BEGIN")
	t.check(await t.talk_to(elder), "Actual chief click opens voiced dialogue")
	if t.check(await _voiced_choices(), "Full voiced quest offer"):
		await _pick("accept")
		await _voiced_choices()
		t.check(Quest.state(GameState.flags, "heukrang_clear") == Quest.ACCEPTED, "Quest actually accepted")
	await t.seconds(1)
	await t.talk_close()
	await t.key(KEY_Q)
	await t.seconds(3)
	_mark("quest_accept", "END")
	await t.close_all()

func _quest_report() -> void:
	# Existing chief_quest fixture: prerequisites are prepared outside the recorded report.
	var elder := _npc("elder")
	if not t.check(elder != null, "Chief report fixture exists"):
		return
	t.check(await t.talk_to(elder), "Quest setup dialogue")
	t.check(await t.talk_until_choices(), "Setup choices")
	await t.talk_pick("accept")
	await t.talk_close()
	await t.go_down(1)
	await t.frames(5)
	var helper = load("res://tests/e2e/scenarios/chief_quest.gd").new()
	helper.setup(t)
	while EnemyKin.alive_count(t.tree) > 0:
		var alive: Array = helper._alive()
		if alive.is_empty():
			break
		await helper._kill(alive.back())
	t.check(Quest.state(GameState.flags, "heukrang_clear") == Quest.KILLED, "Report prerequisite completed through damage path")
	t.main.load_town(Level.SpawnHint.DEFAULT)
	await t.frames(8)
	elder = _npc("elder")
	await _stand(elder.global_position + Vector3(1.8, 0, 1.8))
	_mark("quest_report", "BEGIN")
	t.check(await t.talk_to(elder), "Chief report actual dialogue")
	if t.check(await _voiced_choices(), "Full voiced completion report"):
		await _pick("report")
		await _voiced_choices()
		t.check(Quest.state(GameState.flags, "heukrang_clear") == Quest.DONE, "Quest report actually completed")
	await t.seconds(1.5)
	await t.talk_close()
	await t.key(KEY_Q)
	await t.seconds(3)
	_mark("quest_report", "END")
	await t.close_all()

func _cave() -> void:
	var s = _slice()
	s._build()
	t.main.load_area(AreaDb.FIRST_FIELD, 0, Level.SpawnHint.FROM_ENTRY, &"west")
	await t.frames(8)
	await t.remove_enemies()
	await s._cave_entry(t.level())
	t.check(GameState.floor_no == 1, "Actual cave entry reaches floor one")
	t.player().combat.select_hotkey(0)
	await t.seconds(0.5)
	_mark("cave_floor1_combat", "BEGIN")
	await s._battle(14.0)
	await t.seconds(1.5)
	_mark("cave_floor1_combat", "END")

func _boss() -> void:
	var s = _slice()
	s._build()
	var def: AreaDef = AreaDb.get_def(AreaDb.DEFAULT_DUNGEON)
	t.main.load_area(AreaDb.DEFAULT_DUNGEON, def.boss_floor, Level.SpawnHint.FROM_ABOVE)
	await t.frames(12)
	var bosses: Array = t.tree.get_nodes_in_group("boss")
	if not t.check(bosses.size() == 1, "Actual floor boss present"):
		return
	var boss: Enemy = bosses[0]
	var banner := t.main.get_node_or_null("HUD/AreaTitle")
	if banner != null:
		var clear_title: bool = await t.wait_until(func() -> bool: return banner.current() == null, 6.0)
		t.check(clear_title, "Area title finished before boss telegraph capture")
	var pounce = load("res://tests/e2e/scenarios/heukrang_pounce.gd").new()
	pounce.setup(t)
	pounce._boss = boss
	pounce._vis = boss.get_node("Visual")
	pounce._ap = pounce._vis.find_child("AnimationPlayer", true, false)
	pounce._sk = pounce._vis.find_child("Skeleton3D", true, false)
	if pounce._sk != null:
		pounce._hips = pounce._sk.find_bone("Hips")
	_mark("boss_telegraph", "BEGIN")
	await pounce._charge(0, false)
	await t.seconds(1)
	_mark("boss_telegraph", "END")
	t.camera().snap_to_target()
	t.player().combat.heal_full()
	t.player().combat.mp = t.player().combat.max_mp
	_mark("boss_fight_highlight", "BEGIN")
	await s._battle(16.0, boss)
	await t.seconds(1.5)
	_mark("boss_fight_highlight", "END")

func _loot() -> void:
	t.main.load_area(AreaDb.DEFAULT_DUNGEON, 1, Level.SpawnHint.FROM_ABOVE)
	await t.frames(10)
	await t.remove_enemies()
	var p: Node3D = t.player()
	var inv: Inventory = GameState.inventory
	var unique := ItemGen.make_unique(_rng, ItemDb.unique("u_heukrang_fang"), 4)
	unique.identified = false
	var rare := ItemInstance.create(ItemDb.get_def("iron_sword"))
	rare.rarity = ItemInstance.Rarity.RARE
	var magic := ItemInstance.create(ItemDb.get_def("silver_ring"))
	magic.rarity = ItemInstance.Rarity.MAGIC
	_mark("loot_beams", "BEGIN")
	for pair in [[magic, -1.5], [rare, 0.0], [unique, 1.5]]:
		EventBus.loot_dropped.emit(pair[0], p.global_position + Vector3(float(pair[1]), 1.0, 1.8))
	await t.seconds(2)
	await t.key_down(KEY_ALT)
	await t.seconds(3)
	await t.key_up(KEY_ALT)
	_mark("loot_beams", "END")
	# Bring the same dropped unique into the bag using its actual floor pickup path.
	var floor_unique: FloorItem = null
	for n in t.tree.get_nodes_in_group("floor_item"):
		if n.item == unique:
			floor_unique = n
	if not t.check(floor_unique != null, "Dropped unique present"):
		return
	await t.click_world(floor_unique.global_position)
	if not t.check(await t.wait_until(func() -> bool: return inv.grid.has(unique), 7.0), "Actual ground unique pickup"):
		return
	var scroll: ItemInstance = null
	for it in inv.grid:
		if it.def.id == "ident_scroll":
			scroll = it
	if scroll == null:
		scroll = ItemInstance.create(ItemDb.get_def("ident_scroll"))
		inv.add_auto(scroll)
	await t.key(KEY_I)
	var bag: Node = t.hud_panel("Inventory")
	var center: Vector2 = bag._grid_rect().position + (Vector2(inv.grid[unique]) + Vector2(0.5, 0.5)) * bag.CELL
	_mark("identify_unidentified_unique", "BEGIN")
	await t.mouse_move(center)
	await t.seconds(2)
	await t.click(bag._grid_rect().position + (Vector2(inv.grid[scroll]) + Vector2(0.5, 0.5)) * bag.CELL)
	await t.click(center)
	t.check(unique.identified, "Actual identification scroll input identifies unique")
	await t.mouse_move(center)
	await t.seconds(4)
	_mark("identify_unidentified_unique", "END")
	await t.close_all()

func _attack() -> void:
	t.main.load_area(AreaDb.FIRST_FIELD, 0, Level.SpawnHint.FROM_ENTRY, &"west")
	await t.frames(10)
	await t.remove_enemies()
	var p: Node3D = t.player()
	var pos: Vector3 = t.level().walkable_point(p.global_position + Vector3(1.4, 0, 0))
	var e: Enemy = await t.spawn_enemy("bandit", pos, 1, {"hp": 100000.0, "frozen": true})
	e.gives_reward = false
	p.combat.recompute_stats()
	var count: int = p.visual().attack_swings
	_mark("attack_chain_current", "BEGIN")
	await t.click_world(e.global_position + Vector3(0, 0.8, 0))
	await t.seconds(7)
	p.combat.clear_target()
	t.check(p.visual().attack_swings >= count + 5, "Current production attack timing and chain")
	await t.seconds(1.5)
	_mark("attack_chain_current", "END")

func _effect(clip_name: String, photo: String = "") -> void:
	var helper = load(EFFECTS).new()
	helper.setup(t)
	helper.selected_clip = clip_name
	helper.photo_label = photo
	await helper.run()

func _imugi() -> void:
	var s = _slice()
	s._build()
	var named = load("res://tests/e2e/scenarios/named_imugi.gd").new()
	named.setup(t)
	t.main.load_area(&"jeongnyeongjae", 0, Level.SpawnHint.FROM_ENTRY, &"west")
	await t.frames(10)
	var e: Enemy = named._imugi()
	if not t.check(e != null, "Native optional imugi spawned"):
		return
	named._clear_others(e)
	var anchor: Vector3 = t.level().map.cell_to_world(t.level().map.anchor(&"pool"))
	await _stand(t.level().walkable_point(anchor))
	_mark("imugi_surface_dive_resurface", "BEGIN")
	t.check(await t.wait_until(func() -> bool: return not e.is_hidden() and not e.is_lurking(), 3.0), "Imugi naturally emerges")
	var y0 := e.global_position.y
	var start := t.game_time()
	while not e.is_hidden() and t.game_time() - start < 22.0:
		if t.player().combat.hp < t.player().combat.max_hp * 0.55:
			t.player().combat.use_belt(0)
		await t.frames(6)
	t.check(e.is_hidden(), "Native dive cooldown reaches actual submerge")
	t.check(await t.wait_until(func() -> bool: return not e.is_hidden(), 3.0), "Imugi resurfaces after dive")
	await t.seconds(0.3)
	t.check(e.is_on_floor() and absf(e.global_position.y - y0) <= 0.1, "Landed #710 fix: resurfaces above ground")
	await t.seconds(3)
	_mark("imugi_surface_dive_resurface", "END")

func _photo(label: String) -> void:
	_visibility()
	await RenderingServer.frame_post_draw
	var img := t.tree.root.get_viewport().get_texture().get_image()
	if t.check(img.get_size() == Vector2i(3840, 2160), "Native 3840x2160: " + label):
		await t.shot(label)

func _photos() -> void:
	var win := t.tree.root
	win.mode = Window.MODE_WINDOWED
	win.borderless = true
	# OS may clamp the physical window to the desktop. VIEWPORT renders a fixed
	# native 4K framebuffer and only scales its presentation into that window.
	win.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	win.content_scale_size = Vector2i(3840, 2160)
	win.size = Vector2i(3840, 2160)
	await t.frames(5)
	if not t.check(win.get_texture().get_image().get_size() == Vector2i(3840, 2160), "Actual native 4K framebuffer, no upscaling"):
		return
	for spot in [["01_town_plaza", Vector3(0, 0, 1)], ["02_town_shrine", Vector3(-4.6, 0, 0.8)], ["03_town_chief", Vector3(1.6, 0, -4.4)], ["04_town_pond", Vector3(8, 0, 4)]]:
		await _stand(spot[1])
		await _photo(spot[0])
	t.main.load_area(AreaDb.FIRST_FIELD, 0, Level.SpawnHint.FROM_ENTRY, &"west")
	await t.frames(10)
	await t.remove_enemies()
	for pair in [["05_field_cart", &"cart"], ["06_field_junction", &"junction"], ["07_field_cave_entrance", &"cave"]]:
		await _stand(t.level().map.cell_to_world(t.level().map.anchor(pair[1])) + Vector3(0, 0, 1.5))
		await _photo(pair[0])
	t.main.load_area(AreaDb.DEFAULT_DUNGEON, 1, Level.SpawnHint.FROM_ABOVE)
	await t.frames(10)
	for n in t.tree.get_nodes_in_group("enemy"):
		n.set_physics_process(false)
		n.set_process(false)
	await _stand(t.player().global_position)
	await _photo("08_cave_arrival")
	var rooms: Array = t.level().map.rooms
	if t.check(not rooms.is_empty(), "Cave generated room exists"):
		await _stand(t.level().map.cell_to_world(rooms[rooms.size() / 2].get_center()))
		await _photo("09_cave_room")
	t.main.load_area(AreaDb.DEFAULT_DUNGEON, AreaDb.get_def(AreaDb.DEFAULT_DUNGEON).boss_floor, Level.SpawnHint.FROM_ABOVE)
	await t.frames(10)
	var bosses: Array = t.tree.get_nodes_in_group("boss")
	if t.check(not bosses.is_empty(), "Boss screenshot body exists"):
		var b: Enemy = bosses[0]
		b.set_physics_process(false)
		b.set_process(false)
		await _stand(b.global_position + Vector3(3.5, 0, 3.5))
		await _photo("10_heukrang_boss")
	t.main.load_area(&"jeongnyeongjae", 0, Level.SpawnHint.FROM_ENTRY, &"west")
	await t.frames(10)
	var named = load("res://tests/e2e/scenarios/named_imugi.gd").new()
	named.setup(t)
	var e: Enemy = named._imugi()
	if t.check(e != null, "Imugi screenshot body exists"):
		named._clear_others(e)
		await _stand(t.level().walkable_point(t.level().map.cell_to_world(t.level().map.anchor(&"pool"))))
		await t.wait_until(func() -> bool: return not e.is_hidden(), 3.0)
		await _photo("11_imugi_surface")
	# One native 4K impact from each production showcase, all UI stays hidden.
	for pair in [["12_fire_action", "03_fire"], ["13_freeze_action", "04_cold"], ["14_lightning_action", "08_lightning"], ["15_flurry_action", "09_flurry"], ["16_critical_action", "02_crit"]]:
		await _effect(pair[1], pair[0])
