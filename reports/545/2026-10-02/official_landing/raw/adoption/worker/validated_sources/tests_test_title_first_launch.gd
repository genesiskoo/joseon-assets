extends SceneTree
## #550: 실제 첫 부팅·생성 안내·오프닝. 프로필은 별도 fixture 문맥에만 쓴다.


func _init() -> void:
	_run.call_deferred()


func _run() -> void:
	var fails: Array[String] = []
	var saves: Node = root.get_node("/root/SaveSystem")
	var old_path: String = String(saves.get("save_path"))
	var context := "user://title_first_launch_550_" + str(Time.get_ticks_usec()) + ".json"
	saves.call("use_save_context", context)
	var main: Node = (load("res://world/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	current_scene = main
	_check(main.title_ui.visible and paused and not main._started, "저장 없는 첫 진입 = 타이틀·세계 정지", fails)
	_check(not main.title_ui._has_save(), "첫 진입에 저장된 캐릭터 없음", fails)
	main.title_ui._on_click(main.title_ui._btn_rect(1).get_center(), MOUSE_BUTTON_LEFT)
	_check(main.title_ui.screen == main.title_ui.Screen.CREATE and paused and not main._started and not bool(saves.call("has_save")), "저장 없는 선택 메뉴 → 생성 안내, 아직 판/파일 없음", fails)
	main.title_ui.name_input.text = "첫여정도호"
	main.title_ui._on_click(main.title_ui.confirm_rect().get_center(), MOUSE_BUTTON_LEFT)
	_check(not main.title_ui.visible and main._started and bool(saves.call("has_save")) and main.story_cutin.visible and paused,
		"생성 확인 → 별도 캐릭터 파일·첫 판·오프닝", fails)
	_check(root.get_node("GameState").character.name == "첫여정도호" and not FileAccess.file_exists(context), "새 이름 적용, 기존 단일 문맥 파일을 덮지 않음", fails)
	var directory: String = saves.call("profile_directory")
	main.story_cutin.dismiss()
	_check(not paused and not main.story_cutin.visible, "오프닝 뒤 못골에서 조작 재개", fails)
	main.queue_free()
	await process_frame
	saves.call("delete_save")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(directory))
	saves.call("use_save_context", old_path)
	print("TITLE_FIRST_LAUNCH_TEST fails=%d %s" % [fails.size(), "PASS" if fails.is_empty() else "FAIL"])
	quit(1 if not fails.is_empty() else 0)


func _check(ok: bool, message: String, fails: Array[String]) -> void:
	if not ok:
		push_error("FAIL: " + message)
		fails.append(message)
