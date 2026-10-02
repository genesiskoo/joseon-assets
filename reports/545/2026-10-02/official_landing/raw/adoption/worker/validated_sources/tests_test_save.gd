extends SceneTree
## 헤드리스: godot --headless -s tests/test_save.gd — 직렬화 JSON 왕복(캐릭터·인벤·플래그·문·서낭단), in-place 복원 후 스탯 동일 (design/boss_save_v2.md §2).


func _check(cond: bool, msg: String, fails: Array) -> void:
	if not cond:
		push_error("FAIL: " + msg)
		fails.append(msg)


func _init() -> void:
	_run.call_deferred()


func _run() -> void:
	var fails := []
	var ch := {"name": "도호", "level": 4, "xp": 33, "str": 18, "dex": 15, "vit": 22, "spi": 20, "stat_points": 3, "skill_points": 1, "skills": {"slash": 2, "dash_strike": 1, "whirl": 0}}
	var inv := Inventory.new()
	var sword := ItemInstance.create(ItemDb.get_def("hwando"))
	sword.rarity = ItemInstance.Rarity.MAGIC
	sword.affixes = [{"id": "sharp", "v": 2.0}, {"id": "of_tiger", "v": 3.0}]
	inv.equip("weapon", sword)
	inv.add_auto(ItemInstance.create(ItemDb.get_def("hp_potion"), 4))
	var unid := ItemInstance.create(ItemDb.get_def("straw_shoes"))
	unid.rarity = ItemInstance.Rarity.RARE
	unid.affixes = [{"id": "sturdy", "v": 3.0}, {"id": "of_ox", "v": 4.0}, {"id": "of_wind", "v": 7.0}]
	unid.identified = false
	unid.rare_name = "달빛 발톱"
	inv.add_auto(unid)
	inv.belt_put(2, ItemInstance.create(ItemDb.get_def("mp_potion"), 3))
	# 상품 신 (#258 — 세이브 v3 덧칸 superior·superior_pct): 짚신 방어 1 → 2
	var shoes := ItemInstance.create(ItemDb.get_def("straw_shoes"))
	shoes.superior = true
	shoes.superior_pct = 20
	inv.equip("boots", shoes)
	# 유니크 호신부 (#263 — 세이브 v3 덧칸 unique_id·mods, 유니크일 때만): 흑랑 송곳니 식별됨
	var urng := RandomNumberGenerator.new()
	urng.seed = 263
	var fang := ItemGen.make_unique(urng, ItemDb.unique("u_heukrang_fang"), 6)
	fang.identified = true
	inv.equip("amulet", fang)
	inv.gold = 777
	var flags := {"boss_quest": "killed", "boss_killed_heukrang_gul": true}
	var portal := {"area": &"heukrang_gul", "floor": 2, "pos": Vector3(12.5, 0.0, 7.5), "returned": true}
	var wps: Array[String] = ["heukrang_gul:2"]
	var before := StatsCalc.compute(ch, inv.equipped_items())

	var d := SaveCodec.serialize(ch, inv, flags, portal, wps, 123456, 3, 5, 1, 88.5, 31.0)
	_check(d.version == SaveCodec.VERSION and SaveCodec.VERSION == 4 and d.run_seed == 123456, "버전(v4)·시드", fails)
	# 지금 지역·층 (v4, #156 — design/system_menu_156.md): 메뉴의 「저장 후 타이틀 → 이어하기」가 같은 지역·층 입구에서 연다. JSON 왕복 뒤에도 필드 0 · 던전 2층
	for location in [[&"deulnyeok", 0], [&"heukrang_gul", 2]]:
		var current := SaveCodec.serialize(ch, inv, flags, portal, wps, 123456, 3, 5, 1, 88.5, 31.0, 0, {}, location[0], location[1])
		var read: Dictionary = JSON.parse_string(JSON.stringify(current))
		_check(SaveCodec.validation_error(read) == "", "v4 파일 검증 (%s)" % SaveCodec.validation_error(read), fails)
		var restored := SaveCodec.normalize(read)
		SaveCodec.sanitize(restored)
		_check(restored.area_id == location[0] and restored.floor_no == location[1], "v4 현재 지역/층 왕복", fails)
	_check(d.area_id == "motgol" and d.floor_no == 0, "지역·층을 안 넘기면 못골 0 (옛 부르는 곳 그대로)", fails)
	for version in [1, 2, 3]:
		var old := d.duplicate(true)
		old.version = version
		old.area_id = "heukrang_gul"
		old.floor_no = 2
		var restored := SaveCodec.normalize(old)
		_check(restored.area_id == AreaDb.TOWN and restored.floor_no == 0, "v%d는 마을 기본값" % version, fails)
	for location in [[&"gone", 1], [&"heukrang_gul", 99], [&"deulnyeok", 1]]:
		var missing := {"area_id": location[0], "floor_no": location[1], "waypoints_active": [], "portal": null}
		_check(SaveCodec.sanitize(missing).size() == 1 and missing.area_id == AreaDb.TOWN and missing.floor_no == 0, "사라진 현재 위치는 마을로", fails)
	# 적용 전 검사 (#156): 옛 판의 파일은 전부 통과한다 — v3(회차 run, #258 뒤) · v3(옛 rare_unlocked, #258 전) · v1(층 번호 depth·max_depth)
	var old_run: Dictionary = JSON.parse_string(JSON.stringify(d))
	old_run.version = 3
	old_run.erase("area_id")
	old_run.erase("floor_no")
	var old_unlock := old_run.duplicate(true)
	for k in ["run", "first_magic_run", "first_kills"]:
		old_unlock.erase(k)
	old_unlock["rare_unlocked"] = false
	var old_v1 := old_unlock.duplicate(true)
	old_v1.version = 1
	old_v1.erase("max_area_level")
	old_v1["max_depth"] = 3
	old_v1.portal = {"depth": 2, "pos": [1.0, 0.0, 2.0], "returned": false}
	old_v1.waypoints_active = [2]
	_check(SaveCodec.validation_error(old_run) == "" and SaveCodec.validation_error(old_unlock) == "" and SaveCodec.validation_error(old_v1) == "",
		"옛 판 파일도 검사 통과 (v3 run %s · v3 rare_unlocked %s · v1 %s)" % [SaveCodec.validation_error(old_run), SaveCodec.validation_error(old_unlock), SaveCodec.validation_error(old_v1)], fails)
	_check(SaveCodec.validation_error({}) != "", "빈 저장은 적용하지 않는다", fails)
	# 퀘스트 칸 (#305 — v4 안의 덧칸, 판 올림 없음): 퀘스트 칸 없는 v4 파일(#305 전 #156 판) = 검사 통과 · 포인트 기록 빈 사전 ·
	# 퀘스트는 전부 none — 옛 flags.boss_quest 는 퀘스트 1로 읽힌다
	var v4_noquest: Dictionary = JSON.parse_string(JSON.stringify(d))
	(v4_noquest["character"] as Dictionary).erase("skill_grants")
	(v4_noquest["flags"] as Dictionary).erase(Quest.ROOT)
	var nq := SaveCodec.normalize(v4_noquest)
	_check(int(v4_noquest["version"]) == 4 and SaveCodec.validation_error(v4_noquest) == "" and (nq.character.skill_grants as Dictionary).is_empty()
		and not (nq.flags as Dictionary).has(Quest.ROOT) and Quest.state(nq.flags) == Quest.KILLED and Quest.state(nq.flags, "heukrang_clear") == Quest.NONE,
		"퀘스트 칸 없는 v4 파일 = 검사 통과 · 포인트 기록 빈 사전 · 옛 boss_quest → 퀘스트 1 killed · 소탕 none (%s)" % SaveCodec.validation_error(v4_noquest), fails)
	# 퀘스트 칸 있는 v4 = 왕복(형 되돌림: left 정수 · barked · 포인트 점수 정수) · 형이 틀린 칸은 적용 전에 거부
	var fq := flags.duplicate(true)
	Quest.accept(fq, "heukrang_clear")
	Quest.floor_entered(fq, "heukrang_clear", 5)
	Quest.tally(fq, "heukrang_clear", 3)
	var chq := ch.duplicate(true)
	Progression.grant_skill_points(chq, 1, "quest/heukrang_clear", 1)
	var v4q: Dictionary = JSON.parse_string(JSON.stringify(SaveCodec.serialize(chq, inv, fq, portal, wps, 1, 3, 5, 1, 1.0, 1.0)))
	var nq2 := SaveCodec.normalize(v4q.duplicate(true))
	var cq: Dictionary = (nq2.flags[Quest.ROOT] as Dictionary).get("heukrang_clear", {})
	_check(SaveCodec.validation_error(v4q) == "" and Quest.state(nq2.flags, "heukrang_clear") == Quest.ACCEPTED and typeof(cq.get("left")) == TYPE_INT and int(cq.get("left")) == 3
		and cq.get("barked") == true and typeof((nq2.character.skill_grants as Dictionary).get("quest/heukrang_clear@1")) == TYPE_INT,
		"v4 퀘스트 칸 왕복 (state · left 정수 · barked · 포인트 기록 정수, %s)" % str(cq), fails)
	for damage in ["quest_not_dict", "quest_state", "quest_left", "grant_value"]:
		var bq: Dictionary = v4q.duplicate(true)
		match damage:
			"quest_not_dict": bq["flags"][Quest.ROOT] = "accepted"
			"quest_state": bq["flags"][Quest.ROOT]["heukrang_clear"]["state"] = 3
			"quest_left": bq["flags"][Quest.ROOT]["heukrang_clear"]["left"] = "3"
			"grant_value": bq["character"]["skill_grants"]["quest/heukrang_clear@1"] = "1"
		_check(SaveCodec.validation_error(bq) != "", "퀘스트 칸 손상 적용 거부: " + damage, fails)
	var malformed: Dictionary = JSON.parse_string(JSON.stringify(d))
	malformed.inventory.grid = [{"def": "iron_sword", "pos": [1]}]
	_check(SaveCodec.validation_error(malformed) != "", "깨진 가방 좌표를 적용 전에 거부", fails)
	malformed = JSON.parse_string(JSON.stringify(d))
	malformed.portal.pos = [1, 2]
	_check(SaveCodec.validation_error(malformed) != "", "깨진 귀환문 좌표를 적용 전에 거부", fails)
	for damage in ["empty_inventory", "missing_name", "invalid_rarity", "bad_run", "bad_superior", "newer_version"]:
		var broken: Dictionary = JSON.parse_string(JSON.stringify(d))
		match damage:
			"empty_inventory": broken.inventory = {}
			"missing_name": broken.character.erase("name")
			"invalid_rarity": broken.inventory.equipment.weapon.rarity = 99
			"bad_run": broken.run = "2"
			"bad_superior": broken.inventory.equipment.boots.superior = "yes"
			"newer_version": broken.version = SaveCodec.VERSION + 1
		_check(SaveCodec.validation_error(broken) != "", "손상 적용 거부: " + damage, fails)
	var json := JSON.stringify(d)
	var parsed: Variant = JSON.parse_string(json)
	_check(parsed is Dictionary, "JSON 파싱", fails)
	var n := SaveCodec.normalize(parsed)
	_check(n.character.level == 4 and n.character.skills.slash == 2 and typeof(n.character.level) == TYPE_INT, "캐릭터 int 복원", fails)
	_check(n.portal != null and n.portal.pos == Vector3(12.5, 0.0, 7.5) and n.portal.area == &"heukrang_gul" and typeof(n.portal.area) == TYPE_STRING_NAME and n.portal.floor == 2 and n.portal.returned == true, "문 지역·층·Vector3 왕복 (%s)" % [n.portal], fails)
	_check(n.waypoints_active == ["heukrang_gul:2"] and n.max_area_level == 3 and n.town_visits == 5 and n.run == 1 and typeof(n.run) == TYPE_INT, "서낭단·지역 레벨·방문·회차", fails)
	# 회차 (#258 — 옛 rare_unlocked bool을 갈음, 판 올림 없음): 2회차 왕복 · 옛 세이브의 rare_unlocked true → 2 · 둘 다 없으면 1
	var n_run2 := SaveCodec.normalize(JSON.parse_string(JSON.stringify(SaveCodec.serialize(ch, inv, flags, portal, wps, 1, 3, 5, 2, 1.0, 1.0))))
	_check(n_run2.run == 2 and not SaveCodec.serialize(ch, inv, flags, portal, wps, 1, 3, 5, 2, 1.0, 1.0).has("rare_unlocked"), "2회차 왕복 · rare_unlocked 칸은 더 안 적는다", fails)
	var old_unlocked := {"version": 3, "run_seed": 9, "character": ch, "inventory": inv.to_dict(), "flags": {}, "portal": null, "waypoints_active": [], "rare_unlocked": true}
	var old_locked := {"version": 3, "run_seed": 9, "character": ch, "inventory": inv.to_dict(), "flags": {}, "portal": null, "waypoints_active": []}
	_check(SaveCodec.normalize(JSON.parse_string(JSON.stringify(old_unlocked))).run == 2 and SaveCodec.normalize(JSON.parse_string(JSON.stringify(old_locked))).run == 1, "옛 세이브 rare_unlocked true → 2회차 · 칸 없음 → 1회차", fails)
	# 첫 매직 보장 (#374, item_system_v2 §15.6 — v3 덧칸, 판 올림 없음): 적은 회차 왕복(int) · 칸 없는 옛 세이브 = 0(아직 — 보장이 남음) · 안 넘기면 0
	var n_fm := SaveCodec.normalize(JSON.parse_string(JSON.stringify(SaveCodec.serialize(ch, inv, flags, portal, wps, 1, 3, 5, 2, 1.0, 1.0, 1))))
	_check(n_fm.first_magic_run == 1 and typeof(n_fm.first_magic_run) == TYPE_INT and Loot.first_magic_pending(n_fm.first_magic_run, n_fm.run),
		"첫 매직 회차 왕복 (1회차에 씀 · 지금 2회차 → 다시 남음, %s)" % [n_fm.first_magic_run], fails)
	_check(n.first_magic_run == 0 and SaveCodec.normalize(JSON.parse_string(JSON.stringify(old_locked))).first_magic_run == 0 and d.has("first_magic_run"),
		"첫 매직 칸 — 안 넘기면 0 · 칸 없는 옛 세이브 0(보장 남음) · 늘 적는다", fails)
	# 보스 첫 처치 (#263, item_system_v2 §8.3 — v3 덧칸, 판 올림 없음): {적 id: 처음 잡은 회차} 왕복(int) · 안 넘기면 빈 사전 · 늘 적는다 ·
	# 칸 없는 옛 세이브 = 빈 사전(아무 보스도 안 잡음 = 다음 흑랑이 첫 처치 보장) · 사전이 아니면 빈 사전
	var n_fk := SaveCodec.normalize(JSON.parse_string(JSON.stringify(SaveCodec.serialize(ch, inv, flags, portal, wps, 1, 3, 5, 2, 1.0, 1.0, 1, {"boss_heukrang": 1}))))
	_check(n_fk.first_kills == {"boss_heukrang": 1} and typeof(n_fk.first_kills.boss_heukrang) == TYPE_INT, "첫 처치 왕복 {boss_heukrang: 1} (int, %s)" % [n_fk.first_kills], fails)
	var bad_fk := old_locked.duplicate(true)
	bad_fk["first_kills"] = "boss_heukrang"
	_check(n.first_kills.is_empty() and d.has("first_kills") and SaveCodec.normalize(JSON.parse_string(JSON.stringify(old_locked))).first_kills.is_empty()
		and SaveCodec.normalize(JSON.parse_string(JSON.stringify(bad_fk))).first_kills.is_empty(), "첫 처치 칸 — 안 넘기면 빈 사전 · 늘 적는다 · 옛 세이브·깨진 칸 = 빈 사전", fails)
	_check(absf(n.hp - 88.5) < 0.01 and absf(n.mp - 31.0) < 0.01, "생명·도력", fails)
	_check(n.flags.boss_quest == "killed" and n.flags.boss_killed_heukrang_gul == true, "플래그", fails)
	# 스킬 단축키·데이터 버전 (v3, D-083 skills_v2 §8): 단축키는 문자열 8칸 그대로, 데이터 버전은 int. v2 이하 = 0(트리가 바뀐 뒤 첫 불러오기)
	var ch3 := ch.duplicate(true)
	ch3.hotkeys = ["slash", "dash_strike", "whirl", "", "", "", "", ""]
	ch3.skill_data_ver = 1
	var n3 := SaveCodec.normalize(JSON.parse_string(JSON.stringify(SaveCodec.serialize(ch3, inv, flags, portal, wps, 1, 3, 5, 1, 1.0, 1.0))))
	_check(n3.character.hotkeys == ["slash", "dash_strike", "whirl", "", "", "", "", ""] and typeof(n3.character.skill_data_ver) == TYPE_INT and n3.character.skill_data_ver == 1, "v3 단축키·스킬 데이터 버전 왕복 (%s, %s)" % [n3.character.hotkeys, n3.character.skill_data_ver], fails)
	# 수동 F8 배정도 기존 문자열 8칸 형식으로 저장한다 (#245) — F2만 비고 미학습 F3 예약은 남는다.
	var custom := ch3.duplicate(true)
	var skill_tree := load("res://data/skill_trees/doho.tres") as SkillTreeDef
	_check(Progression.assign_hotkey(custom, skill_tree, 7, "dash_strike"), "저장 전 돌진베기 F8 수동 배정", fails)
	var n_custom := SaveCodec.normalize(JSON.parse_string(JSON.stringify(SaveCodec.serialize(custom, inv, flags, portal, wps, 1, 3, 5, 1, 1.0, 1.0))))
	_check(n_custom.character.hotkeys == ["slash", "", "whirl", "", "", "", "", "dash_strike"]
		and n_custom.character.hotkeys.all(func(id: Variant) -> bool: return id is String)
		and n_custom.character.skill_data_ver == ch3.skill_data_ver, "사용자 F8 배정 왕복 = 문자열 8칸 · 데이터 버전 그대로", fails)
	var save_v2 := {"version": 2, "run_seed": 9, "character": ch3, "inventory": inv.to_dict(), "flags": {}, "portal": null, "waypoints_active": []}
	var n_v2 := SaveCodec.normalize(JSON.parse_string(JSON.stringify(save_v2)))
	_check(n_v2.character.skill_data_ver == 0 and n_v2.character.skills.slash == 2, "v2 세이브 = 스킬 데이터 버전 0(굿 1번 공짜 표시) · 칸 점수는 그대로", fails)

	# v1(층 번호) 세이브 옮기기 (areas_v2.md §4): 문 depth 2 → 흑랑 굴 2층, 서낭단 [2] → "heukrang_gul:2", max_depth → max_area_level
	var v1 := {"version": 1, "run_seed": 9, "character": ch, "inventory": inv.to_dict(), "flags": {},
		"portal": {"depth": 2, "pos": [1.0, 0.0, 2.0], "returned": false}, "waypoints_active": [2], "max_depth": 3, "town_visits": 2}
	var m := SaveCodec.normalize(JSON.parse_string(JSON.stringify(v1)))
	_check(m.portal != null and m.portal.area == &"heukrang_gul" and m.portal.floor == 2 and m.portal.pos == Vector3(1, 0, 2) and m.portal.returned == false, "v1 문 → 흑랑 굴 2층 (%s)" % [m.portal], fails)
	_check(m.waypoints_active == ["heukrang_gul:2"] and m.max_area_level == 3, "v1 서낭단·최대 층 → 키·지역 레벨 (%s, %d)" % [m.waypoints_active, m.max_area_level], fails)
	# 서낭단 키 왕복 (AreaDb)
	var pk: Array = AreaDb.parse_waypoint_key(AreaDb.waypoint_key(&"heukrang_gul", 2))
	_check(pk[0] == &"heukrang_gul" and pk[1] == 2 and AreaDb.label(&"heukrang_gul", 2) == "흑랑 굴 2층" and AreaDb.label(AreaDb.TOWN, 0) == "못골 마을", "서낭단 키·지역 이름", fails)
	_check(AreaDb.level_at(&"heukrang_gul", 1) == 2 and AreaDb.level_at(&"heukrang_gul", 2) == 3 and AreaDb.level_at(AreaDb.TOWN, 0) == 1 		and AreaDb.level_at(AreaDb.FIRST_FIELD, 0) == 1, "지역 레벨 = 들녘 1·흑랑 굴 1층 2·보스 층 3 (field_v2.md §7)", fails)
	# 지금 지도와 안 맞는 것 걷어내기 (#165, dungeon.md §7.4): 지금 서낭단 층이 아닌 키·없는 지역은 버리고, 층 수를 넘는 귀환문은 닫는다
	# #166: 흑랑 굴 1층 서낭단은 들녘 갈림길로 옮겼다 (field_v2.md §7) → "heukrang_gul:1"도 버린다
	var sn := {"waypoints_active": ["heukrang_gul:2", "heukrang_gul:1", "motgol:0", "deulnyeok:0", "nowhere:3"], "portal": {"area": &"heukrang_gul", "floor": 3, "pos": Vector3.ZERO, "returned": false}}
	var dropped := SaveCodec.sanitize(sn)
	_check(sn.waypoints_active == ["motgol:0", "deulnyeok:0"] and sn.portal == null and dropped.size() == 4, "sanitize: 옛 서낭단 키·없는 지역 버림, 3층 귀환문 닫음 (%s / %s)" % [sn.waypoints_active, dropped], fails)
	var sn2 := {"waypoints_active": [], "portal": {"area": &"heukrang_gul", "floor": 2, "pos": Vector3.ZERO, "returned": true}}
	_check(SaveCodec.sanitize(sn2).is_empty() and sn2.portal != null, "sanitize: 있는 층의 귀환문은 둔다", fails)

	# in-place 인벤 복원
	var inv2 := Inventory.new()
	inv2.add_auto(ItemInstance.create(ItemDb.get_def("wooden_sword")))  # 덮어써져야 함
	inv2.apply_dict(n.inventory)
	_check(inv2.gold == 777 and inv2.grid.size() == 2 and inv2.equipment.weapon != null and inv2.equipment.weapon.def.id == "hwando", "인벤 복원 (gold %d grid %d)" % [inv2.gold, inv2.grid.size()], fails)
	_check(inv2.belt[2] != null and inv2.belt[2].stack == 3 and inv2.belt[0] == null, "벨트 복원", fails)
	var found_rare := false
	for it in inv2.grid:
		if it.def.id == "straw_shoes":
			found_rare = it.rarity == ItemInstance.Rarity.RARE and not it.identified and it.rare_name == "달빛 발톱" and it.affixes.size() == 3
	_check(found_rare, "희귀 미식별 복원", fails)
	var after := StatsCalc.compute(n.character, inv2.equipped_items())
	_check(absf(after.dmg_min - before.dmg_min) < 0.001 and absf(after.dmg_max - before.dmg_max) < 0.001 and absf(after.str - before.str) < 0.001, "복원 후 스탯 동일", fails)
	var shoes2: ItemInstance = inv2.equipment.boots
	_check(shoes2 != null and shoes2.superior and shoes2.superior_pct == 20 and shoes2.display_name() == "상품 짚신" and absf(after.defense - before.defense) < 0.001, "상품 짚신 왕복 (방어 %s → %s)" % [before.defense, after.defense], fails)
	var fang2: ItemInstance = inv2.equipment.amulet
	_check(fang2 != null and fang2.rarity == ItemInstance.Rarity.UNIQUE and fang2.unique_id == "u_heukrang_fang" and fang2.mods == fang.mods and fang2.identified and fang2.display_name() == "흑랑 송곳니"
		and absf(after.move_speed - before.move_speed) < 0.001 and absf(before.move_speed - StatsCalc.BASE_MOVE_SPEED * 1.1) < 0.001,
		"유니크 흑랑 송곳니 왕복 (id · 줄 · 식별 · 이름 · 이동 %s → %s)" % [before.move_speed, after.move_speed], fails)
	# 못 낌은 불러오기에서 벗기지 않는다 (#375, item_system_v2 §5): 요구치가 모자란 채 낀 세이브(Lv3 · 힘 20 환도)를 몸(Lv1 · 힘 15) 있는 가방에
	# 불러오면 칸 그대로 · 꺼짐(맨손) — 새로 끼기만 거절된다. 몸 = GameState.wearer_stats와 같은 모양
	var weak := {"level": 1, "xp": 0, "str": 15, "dex": 15, "vit": 20, "spi": 20}
	var inv4 := Inventory.new()
	inv4.wearer = func() -> Dictionary: return {"character": weak, "extra": {}}
	inv4.apply_dict(n.inventory)
	var w4: ItemInstance = inv4.equipment.weapon
	_check(w4 != null and w4.def.id == "hwando" and inv4.equipment.boots != null and inv4.grid.size() == 2 and inv4.wearer.is_valid(), "몸 있는 가방에 불러오기 = 모자란 환도도 칸 그대로 · 신·가방·몸 그대로", fails)
	var s4 := StatsCalc.compute(weak, inv4.equipped_items())
	_check(s4.inactive.has(w4) and absf(s4.dmg_max - 4.0) < 0.001, "불러온 환도 = 꺼짐 → 맨손 최대 4 (got %s)" % s4.dmg_max, fails)
	_check(inv4.equip_check("weapon", ItemInstance.create(ItemDb.get_def("hwando"))) == Inventory.EquipReason.REQ_LEVEL, "새로 끼는 환도 = REQ_LEVEL (못 낌)", fails)
	# 장비 칸 9 (D-091 · #388 — v3 덧칸, 판 올림 없음): 세이브는 9키를 적는다 · 옛 7키 세이브 = 머리·보조 빈 칸, 나머지 그대로
	_check(d.inventory.equipment.size() == 9 and d.inventory.equipment.has("head") and d.inventory.equipment.has("offhand") and d.inventory.equipment.head == null,
		"세이브 장비 = 9키 (빈 머리 = null)", fails)
	var old7: Dictionary = (n.inventory as Dictionary).duplicate(true)
	(old7.equipment as Dictionary).erase("head")
	(old7.equipment as Dictionary).erase("offhand")
	var inv7 := Inventory.new()
	inv7.apply_dict(JSON.parse_string(JSON.stringify(old7)))
	_check(old7.equipment.size() == 7 and inv7.equipment.size() == 9 and inv7.equipment.head == null and inv7.equipment.offhand == null
		and inv7.equipment.weapon != null and inv7.equipment.weapon.def.id == "hwando" and inv7.equipment.amulet != null and inv7.equipment.boots != null and inv7.gold == 777,
		"옛 7키 세이브 → 머리·보조 빈 칸 · 칼·호신부·신·엽전 그대로", fails)
	_check(SaveCodec.normalize(JSON.parse_string(JSON.stringify({"version": 3, "run_seed": 9, "character": ch, "inventory": old7, "flags": {}, "portal": null, "waypoints_active": []}))).inventory.equipment.size() == 7
		and SaveCodec.VERSION == 4, "옛 세이브를 고치지 않는다 — 장비 9칸은 판 올림 없음(v3 덧칸 · v4는 #156 지역·층) · 빈 칸은 가방이 채운다", fails)
	# 머리·보조 왕복 — 실제 베이스 패랭이 · 묵함 (S2 #389) · 묵함 = 도호 결 보조 줄(tal_t1_doho) + 공용 줄 매직
	var hat_d := ItemDb.get_def("paeraengi")
	var tool_d := ItemDb.get_def("mukham")
	var inv9 := Inventory.new()
	var hat := ItemInstance.create(hat_d)
	var tool := ItemInstance.create(tool_d)
	tool.rarity = ItemInstance.Rarity.MAGIC
	tool.affixes = [{"id": "tal_t1_doho", "v": 8.0}, {"id": "of_crane", "v": 3.0}]
	_check(hat_d != null and tool_d != null and inv9.equip("head", hat).ok and inv9.equip("offhand", tool).ok, "패랭이·묵함 끼기", fails)
	var back9 := Inventory.from_dict(JSON.parse_string(JSON.stringify(inv9.to_dict())))
	var hat2: ItemInstance = back9.equipment.head
	var tool2: ItemInstance = back9.equipment.offhand
	var s9 := StatsCalc.compute(ch, back9.equipped_items())
	_check(hat2 != null and hat2.def == hat_d and tool2 != null and tool2.def == tool_d and tool2.affixes == tool.affixes and tool2.rarity == ItemInstance.Rarity.MAGIC
		and absf(s9.defense - 1.0) < 0.001 and absf(float(s9.talisman_pct) - 13.0) < 0.001 and tool2.display_name() == "학의 주사 먹인 묵함",
		"머리·보조 JSON 왕복 (정의 · 등급 · 옵션 · 방어 1 · 부적 피해 암묵 5 + 옵션 8 · 이름)", fails)
	# 문 없음
	var d2 := SaveCodec.serialize(ch, inv, {}, null, [] as Array[String], 1, 0, 0, 1, 1.0, 1.0)
	var n2 := SaveCodec.normalize(JSON.parse_string(JSON.stringify(d2)))
	_check(n2.portal == null and n2.waypoints_active.is_empty(), "문 없음 왕복", fails)

	print("SAVE_TEST fails=%d %s" % [fails.size(), "PASS" if fails.is_empty() else "FAIL"])
	quit(1 if fails.size() > 0 else 0)
