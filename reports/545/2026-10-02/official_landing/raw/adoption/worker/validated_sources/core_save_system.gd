extends Node
## #550: 캐릭터별 저장. 기존 SaveCodec 상태와 단일 save_path 시험 입구는 유지한다.
const PROFILES = preload("res://core/character_profiles.gd")
const DEFAULT_SAVE := "user://save_v2.json"
var save_path: String = DEFAULT_SAVE
var last_error: String = ""
var active_profile_id: String = ""
var _profile: Dictionary = {}
var _context_path: String = DEFAULT_SAVE


## 명시적 외부 저장 문맥. E2E/개발 리셋은 이 API로 원래 단일 파일에 돌아간다.
func use_save_context(path: String) -> void:
	save_path = path
	_context_path = path
	active_profile_id = ""
	_profile = {}
	last_error = ""


func profile_directory() -> String:
	if active_profile_id.is_empty():
		_context_path = save_path
	elif save_path != PROFILES.path_for(_directory_for_context(), active_profile_id):
		# 기존 공개 save_path 오버라이드도 허용한다. 파일을 삭제하거나 자동으로 읽지 않는다.
		use_save_context(save_path)
	return _directory_for_context()


func _directory_for_context() -> String:
	return "user://characters" if _context_path == DEFAULT_SAVE else _context_path + ".characters"


func profiles() -> Array[Dictionary]:
	var directory := profile_directory()
	last_error = PROFILES.migrate_legacy(_context_path, directory)
	return PROFILES.list_profiles(directory)


func select_profile(id: String) -> bool:
	var directory := profile_directory()
	var selected: Dictionary = PROFILES.read_checked(PROFILES.path_for(directory, id), id)
	if not String(selected.error).is_empty():
		return _failed(String(selected.error))
	save_path = PROFILES.path_for(directory, id)
	active_profile_id = id
	_profile = PROFILES.metadata(selected.data, id)
	last_error = ""
	return true


func create_profile(value: String, opening_pending: bool = true) -> bool:
	var display_name := value.strip_edges()
	var problem: String = PROFILES.name_error(display_name)
	if not problem.is_empty():
		return _failed(problem)
	var directory := profile_directory()
	if PROFILES.duplicate_name(directory, display_name):
		return _failed("같은 이름의 캐릭터가 있습니다")
	var directory_error: String = PROFILES.ensure_directory(directory)
	if not directory_error.is_empty():
		return _failed(directory_error)
	var id := ""
	for _try in 8:
		id = "doho_" + Crypto.new().generate_random_bytes(12).hex_encode()
		if not FileAccess.file_exists(PROFILES.path_for(directory, id)):
			break
	var target: String = PROFILES.path_for(directory, id)
	if target.is_empty() or FileAccess.file_exists(target):
		return _failed("새 캐릭터 저장을 만들지 못했습니다")
	# 새 상태는 기존 시작 장비 규칙 하나(GameState.new_character)에서 만든다. 쓰기 실패 때는 현재 판도 되돌린다.
	var previous := _snapshot()
	var rng_state := GameState.rng.state
	GameState.new_character()
	GameState.character.name = display_name
	GameState.area_id = AreaDb.TOWN
	GameState.floor_no = 0
	GameState.run_seed = int(Time.get_unix_time_from_system()) ^ int(Time.get_ticks_usec())
	GameState.rng.seed = GameState.run_seed
	GameState.flags["opening_pending"] = opening_pending
	var fresh := _snapshot()
	var stats := StatsCalc.compute(GameState.character, GameState.inventory.equipped_items())
	fresh.hp = stats.max_hp
	fresh.mp = stats.max_mp
	var info := {"id": id, "name": display_name, "class_id": PROFILES.CLASS_ID, "model_id": PROFILES.CLASS_ID,
		"created_at": Time.get_datetime_string_from_system()}
	fresh["profile"] = info
	problem = PROFILES.write_json(target, fresh, false)
	if not problem.is_empty():
		_apply_checked(previous)
		GameState.rng.state = rng_state
		var player := get_tree().get_first_node_in_group("player")
		if player and "combat" in player:
			player.combat.recompute_stats()
			player.combat.hp = float(previous.hp)
			player.combat.mp = float(previous.mp)
		return _failed(problem)
	save_path = target
	active_profile_id = id
	_profile = info
	last_error = ""
	return true


## --new/시험 새 판. 원래 사용자 파일·캐릭터는 삭제하지 않는다.
func begin_fresh_session() -> void:
	if active_profile_id.is_empty():
		_context_path = save_path
	var path := "user://save_dev_new.json" if _context_path == DEFAULT_SAVE else _context_path
	use_save_context(path)


func has_save() -> bool:
	return FileAccess.file_exists(save_path)


func _snapshot() -> Dictionary:
	var player := get_tree().get_first_node_in_group("player")
	var hp := 0.0
	var mp := 0.0
	if player and "combat" in player:
		hp = player.combat.hp
		mp = player.combat.mp
	return SaveCodec.serialize(GameState.character, GameState.inventory, GameState.flags, GameState.portal, GameState.waypoints_active,
		GameState.run_seed, GameState.max_area_level, GameState.town_visits, GameState.run, hp, mp, GameState.first_magic_run, GameState.first_kills,
		GameState.area_id, GameState.floor_no)


func save_now(reason: String = "") -> bool:
	last_error = ""
	if save_path == DEFAULT_SAVE:
		return _failed("캐릭터를 선택한 뒤 저장해 주세요. 기존 저장 원본은 보존됩니다")
	if not active_profile_id.is_empty() and save_path != PROFILES.path_for(_directory_for_context(), active_profile_id):
		return _failed("저장 위치가 바뀌었습니다. 캐릭터를 다시 선택해 주세요")
	# 선택한 파일이 밖에서 사라졌다면 다른 파일을 만들며 저장을 계속하지 않는다.
	if not active_profile_id.is_empty() and save_path == PROFILES.path_for(_directory_for_context(), active_profile_id) and not has_save():
		return _failed("선택한 캐릭터 저장 파일을 찾지 못했습니다")
	# 외부 손상/바뀐 id 파일을 현재 판의 자동 저장으로 덮지 않는다.
	if has_save() and read_checked().is_empty():
		return false
	var data := _snapshot()
	if not active_profile_id.is_empty() and save_path == PROFILES.path_for(_directory_for_context(), active_profile_id):
		data["profile"] = _profile.duplicate()
	var problem: String = SaveCodec.validation_error(data)
	if problem.is_empty() and data.has("profile"):
		problem = PROFILES.profile_error(data, active_profile_id)
	if not problem.is_empty():
		return _failed("현재 상태를 저장할 수 없습니다: " + problem)
	problem = PROFILES.write_json(save_path, data)
	if not problem.is_empty():
		return _failed(problem)
	if DevMode.is_active:
		print("[Save] %s → %s (%s)" % [reason, save_path, ProjectSettings.globalize_path(save_path)])
	return true


func read_checked() -> Dictionary:
	last_error = ""
	var id := active_profile_id if save_path == PROFILES.path_for(_directory_for_context(), active_profile_id) else ""
	var read: Dictionary = PROFILES.read_checked(save_path, id)
	if not String(read.error).is_empty():
		_failed(String(read.error))
		return {}
	return read.data


func load_into_state() -> Dictionary:
	var parsed := read_checked()
	if parsed.is_empty():
		return {}
	return _apply_checked(parsed)


func _apply_checked(parsed: Dictionary) -> Dictionary:
	var n := SaveCodec.normalize(parsed)
	var dropped := SaveCodec.sanitize(n)   # 지금 지도와 안 맞는 서낭단 키·귀환문 (#165 배치 변경)
	if not dropped.is_empty():
		print("[Load] 지금 지도와 안 맞아 걷어냄: %s" % ", ".join(dropped))
	GameState.area_id = n.area_id
	GameState.floor_no = n.floor_no
	GameState.run_seed = n.run_seed
	GameState.rng.seed = GameState.run_seed
	GameState.character = n.character
	GameState.ensure_skill_state()   # 옛 세이브의 빠진 칸·단축키를 지금 스킬 트리로 (D-083)
	GameState.inventory.apply_dict(n.inventory)
	GameState.flags = n.flags
	GameState.portal = n.portal
	GameState.waypoints_active = n.waypoints_active
	GameState.max_area_level = n.max_area_level
	GameState.town_visits = n.town_visits
	GameState.run = n.run
	GameState.first_magic_run = n.first_magic_run
	GameState.first_kills = n.first_kills
	if DevMode.is_active:
		print("[Load] lv=%d gold=%d flags=%s portal=%s wps=%s" % [GameState.character.level, GameState.inventory.gold, GameState.flags, GameState.portal, GameState.waypoints_active])
	return {"hp": n.hp, "mp": n.mp, "area_id": n.area_id, "floor_no": n.floor_no}


func delete_save() -> void:
	if has_save():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(save_path))


func _failed(message: String) -> bool:
	last_error = message
	push_warning("SaveSystem: " + message)
	return false
