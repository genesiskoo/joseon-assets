extends SceneTree
const PROFILES = preload("res://core/character_profiles.gd")
## #550: 별도 프로세스 두 번. 첫 프로세스가 만든 파일만 두 번째에서 실제 Main으로 이어한다.
var failures: Array[String] = []
var checks := 0


func _init() -> void:
	_run.call_deferred()


func _check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		push_error("FAIL: " + message)


func _run() -> void:
	var phase := ""
	var token := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--profile-phase="):
			phase = argument.trim_prefix("--profile-phase=")
		elif argument.begins_with("--profile-token="):
			token = argument.trim_prefix("--profile-token=")
	if phase.is_empty():
		token = str(Time.get_ticks_usec())
		for child_phase in ["write", "read"]:
			var output: Array = []
			var code := OS.execute(OS.get_executable_path(), ["--headless", "--path", ProjectSettings.globalize_path("res://"), "-s", "res://tests/test_profiles_restart.gd",
				"--", "--profile-phase=" + child_phase, "--profile-token=" + token], output, true)
			var raw := "".join(output)
			var child_errors := 0
			var error_pattern := RegEx.new()
			error_pattern.compile("(?m)^.*(?:SCRIPT ERROR|SHADER ERROR|Parse Error|Compile Error|Compilation failed).*$|^\\s*(?:USER )?ERROR:.*$")
			for hit in error_pattern.search_all(raw):
				if not hit.get_string().contains("resources still in use at exit"):
					child_errors += 1
			var ok := child_errors == 0 and code == 0 and raw.contains("PROFILE_RESTART_" + child_phase.to_upper() + " fails=0 PASS") and not raw.contains("SCRIPT ERROR") and not raw.contains("Parse Error")
			_check(ok, "독립 프로세스 " + child_phase + " 저장/복원")
			if not ok:
				print(raw)
		_finish("PROFILES_RESTART_TEST")
		return
	var pattern := RegEx.new()
	pattern.compile("^[0-9]+$")
	if pattern.search(token) == null or phase not in ["write", "read"]:
		_check(false, "fixture 토큰/단계 형식")
		_finish("PROFILE_RESTART_" + phase.to_upper())
		return
	var directory := "user://profiles_restart_550_" + token
	var context := directory.path_join("session.json")
	var ids_path := directory.path_join("fixture_ids.json")
	var saves: Node = root.get_node("SaveSystem")
	var state: Node = root.get_node("GameState")
	saves.call("use_save_context", context)
	var main: Node = (load("res://world/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	current_scene = main
	var ids := {}
	if phase == "write":
		for name in ["RestartDohoA", "RestartDohoB"]:
			_check(saves.call("create_profile", name, false), "독립 첫 프로세스 생성 " + name)
			main.start_game(true)
			main.pause_world(true)
			state.character.level = 5 if name.ends_with("A") else 2
			state.inventory.gold = 5510 if name.ends_with("A") else 5520
			state.flags["restart550"] = name
			if name.ends_with("A"):
				state.inventory.add_auto(ItemInstance.create(ItemDb.get_def("mp_potion"), 4))
				state.first_kills["boss_heukrang"] = 1
				main.call("load_area", &"deulnyeok", 0, 0)   # SpawnHint.DEFAULT, 런타임 로드 뒤 호출
			else:
				state.inventory.equip("weapon", ItemInstance.create(ItemDb.get_def("wooden_sword")))
			_check(saves.call("save_now", "restart550"), "독립 첫 프로세스 진행 저장 " + name)
			ids[name] = String(saves.active_profile_id)
			main.show_title()
		var file := FileAccess.open(ids_path, FileAccess.WRITE)
		file.store_string(JSON.stringify(ids))
		file.close()
	else:
		ids = JSON.parse_string(FileAccess.get_file_as_string(ids_path))
		var profiles: Array = saves.call("profiles")
		_check(profiles.size() == 2, "새 프로세스에서 캐릭터 파일 둘 발견")
		for name in ["RestartDohoA", "RestartDohoB"]:
			_check(saves.call("select_profile", String(ids[name])), "새 프로세스 파일 선택 " + name)
			main.start_game(true)
			main.pause_world(true)
			var is_a: bool = String(name).ends_with("A")
			_check(state.character.name == name and state.character.level == (5 if is_a else 2) and state.inventory.gold == (5510 if is_a else 5520)
				and state.flags.restart550 == name, "프로세스 재접속 이름·Lv·엽전·진행 격리 " + name)
			_check(state.inventory.count_of("mp_potion") == (4 if is_a else 0) and state.inventory.equipment.weapon.def.id == ("iron_sword" if is_a else "wooden_sword"),
				"프로세스 재접속 가방·장비 격리 " + name)
			_check(state.first_kills.has("boss_heukrang") == is_a and state.area_id == (&"deulnyeok" if is_a else AreaDb.TOWN), "프로세스 재접속 보스·지역 격리 " + name)
			main.show_title()
		var profile_directory: String = saves.call("profile_directory")
		for id in ids.values():
			DirAccess.remove_absolute(ProjectSettings.globalize_path(PROFILES.path_for(profile_directory, String(id))))
		DirAccess.remove_absolute(ProjectSettings.globalize_path(ids_path))
		DirAccess.remove_absolute(ProjectSettings.globalize_path(profile_directory))
		DirAccess.remove_absolute(ProjectSettings.globalize_path(directory))
	main.queue_free()
	await process_frame
	_finish("PROFILE_RESTART_" + phase.to_upper())


func _finish(label: String) -> void:
	print("%s%s fails=%d %s" % [label, " checks=" + str(checks) if label == "PROFILES_RESTART_TEST" else "", failures.size(), "PASS" if failures.is_empty() else "FAIL"])
	quit(0 if failures.is_empty() else 1)
