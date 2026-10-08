extends E2eScenario
const PROFILES = preload("res://core/character_profiles.gd")
## #550: 실제 버튼·LineEdit 키 입력 → 두 캐릭터 생성·복귀·선택·재접속 문맥·설정/크레딧.


func timeout_sec() -> float:
	return 100.0


func _type_name(title: Node, value: String) -> void:
	await t.click(title.name_rect().get_center())
	for letter in value:
		var key := InputEventKey.new()
		key.unicode = letter.unicode_at(0)
		key.pressed = true
		Input.parse_input_event(key)
		await t.frames(1)
		key.pressed = false
		Input.parse_input_event(key)
	await t.frames(2)


func _clear_name(title: Node) -> void:
	await t.click(title.name_rect().get_center())
	var select_all := InputEventKey.new()
	select_all.keycode = KEY_A
	select_all.physical_keycode = KEY_A
	select_all.ctrl_pressed = true
	select_all.pressed = true
	Input.parse_input_event(select_all)
	await t.frames(1)
	select_all.pressed = false
	Input.parse_input_event(select_all)
	await t.key(KEY_BACKSPACE)


func _save_and_title(menu: Node) -> void:
	await t.key(KEY_ESCAPE)
	await t.click(menu.button_rect(2).get_center())
	await t.frames(2)


func _select(title: Node, id: String) -> void:
	await t.click(title._btn_rect(1).get_center())
	var index := -1
	for i in title._profiles.size():
		if title._profiles[i].id == id:
			index = i
			break
	t.check(index >= 0, "선택 목록에 실제 프로필 존재")
	if index < 0:
		return
	await t.click(title.selection_row_rect(index).get_center())
	await t.click(title.confirm_rect().get_center())
	await t.frames(3)


func run() -> void:
	var title: Node = t.main.title_ui
	var menu: Node = t.main.system_menu
	var original_context: String = SaveSystem.save_path
	var context := "user://profiles_e2e_550_" + str(Time.get_ticks_usec()) + ".json"
	SaveSystem.use_save_context(context)
	t.main.show_title()
	await t.frames(2)
	t.check(title.visible and t.tree.paused and not t.main._started, "타이틀에서 세계 정지")
	t.check(title.MENU_LABELS == ["캐릭터 생성", "기존 캐릭터로 플레이", "설정", "크레딧"], "타이틀 네 메뉴")
	await t.shot("menu")
	await t.click(title._btn_rect(1).get_center())
	t.check(title.screen == title.Screen.CREATE and not SaveSystem.has_save(), "저장 없는 선택 → 생성 안내, 파일은 아직 없음")
	await _type_name(title, "FirstDoho")
	t.check(title.name_input.text == "FirstDoho", "LineEdit 실제 글자 키 입력")
	await t.shot("creation")
	await t.click(title.confirm_rect().get_center())
	await t.frames(3)
	var a_id := SaveSystem.active_profile_id
	var a_path := SaveSystem.save_path
	var directory := SaveSystem.profile_directory()
	t.check(not title.visible and t.main._started and not t.tree.paused and a_id.begins_with("doho_"), "생성 버튼 → 별도 파일·실제 게임")
	t.check(GameState.character.name == "FirstDoho" and GameState.character.level == 1 and GameState.inventory.gold == 0, "첫 캐릭터 새 이름·초기 상태")
	GameState.character.level = 4
	GameState.inventory.gold = 7777
	GameState.first_kills["boss_heukrang"] = 1
	GameState.flags["profile550"] = "A"
	GameState.inventory.add_auto(ItemInstance.create(ItemDb.get_def("mp_potion"), 4))
	t.main.load_area(&"deulnyeok", 0, Level.SpawnHint.DEFAULT)
	await t.frames(3)
	await _save_and_title(menu)
	var a_bytes := FileAccess.get_file_as_bytes(a_path)
	await t.click(title._btn_rect(0).get_center())
	await _type_name(title, "FirstDoho")
	await t.click(title.confirm_rect().get_center())
	t.check(title.visible and t.tree.paused and not title._error.is_empty() and SaveSystem.active_profile_id == a_id and GameState.inventory.gold == 7777,
		"같은 이름 생성 거부, 선택·현재 판 유지")
	t.check(FileAccess.get_file_as_bytes(a_path) == a_bytes, "중복 이름 생성은 기존 파일 byte 그대로")
	await _clear_name(title)
	await _type_name(title, "SecondDoho")
	await t.key(KEY_ENTER)
	await t.frames(3)
	var b_id := SaveSystem.active_profile_id
	var b_path := SaveSystem.save_path
	t.check(b_id != a_id and b_path != a_path and not title.visible and t.main._started, "Enter 생성 → 다른 id·다른 저장·게임")
	t.check(GameState.character.name == "SecondDoho" and GameState.character.level == 1 and GameState.inventory.gold == 0
		and not GameState.flags.has("profile550") and GameState.first_kills.is_empty(), "두 번째 캐릭터에 첫 진행·엽전·첫처치가 섞이지 않음")
	GameState.character.level = 2
	GameState.inventory.gold = 2200
	GameState.flags["profile550"] = "B"
	await _save_and_title(menu)
	await t.click(title._btn_rect(1).get_center())
	t.check(title._profiles.size() == 2 and title.screen == title.Screen.SELECT, "별도 선택창 두 캐릭터")
	for info in title._profiles:
		t.check(info.valid and info.model_id == "doho" and info.level in [2, 4] and not String(info.location).is_empty(), "저장된 이름·Lv·지역·도호 외형 메타데이터")
	await t.shot("selection")
	await t.click(title.back_rect().get_center())
	await _select(title, a_id)
	t.check(GameState.character.name == "FirstDoho" and GameState.character.level == 4 and GameState.inventory.gold == 7777
		and GameState.flags.profile550 == "A" and GameState.first_kills.boss_heukrang == 1, "A 실제 선택 → 이름·레벨·엽전·플래그·첫처치 복원")
	t.check(GameState.inventory.count_of("mp_potion") == 4, "A의 가방 물약 스택 4 복원")
	t.check(GameState.area_id == &"deulnyeok" and GameState.floor_no == 0, "선택한 A의 지역 입구로 복원")
	await _save_and_title(menu)
	await _select(title, b_id)
	t.check(GameState.character.name == "SecondDoho" and GameState.character.level == 2 and GameState.inventory.gold == 2200
		and GameState.flags.profile550 == "B" and GameState.first_kills.is_empty(), "B 실제 전환 → 별도 상태 복원")
	t.check(GameState.inventory.count_of("mp_potion") == 0, "B 가방에 A 물약이 섞이지 않음")
	t.check(GameState.area_id == AreaDb.TOWN and GameState.floor_no == 0, "B의 못골 위치 복원")
	await _save_and_title(menu)
	# 프로필 선택 기억을 버리고 파일만 남긴 새 접속 문맥에서 다시 찾고 선택한다.
	SaveSystem.use_save_context(context)
	title._menu()
	await _select(title, a_id)
	t.check(SaveSystem.active_profile_id == a_id and GameState.character.level == 4 and GameState.inventory.gold == 7777
		and GameState.flags.profile550 == "A", "새 접속 문맥에서 파일 목록·A 진행 다시 복원")
	await _save_and_title(menu)
	var clock := GameClock.now
	await t.click(title._btn_rect(2).get_center())
	t.check(menu.visible and menu.settings_open and menu._from_title and t.tree.paused, "타이틀 설정은 기존 설정 창")
	var volume := GameSettings.volume("Master")
	var slider: Rect2 = menu.volume_rect(0)
	await t.click(Vector2(slider.position.x + slider.size.x * 0.41, slider.get_center().y))
	t.check(absf(GameSettings.volume("Master") - 0.41) < 0.011, "타이틀 설정 실제 슬라이더")
	await t.shot("settings")
	await t.key(KEY_ESCAPE)
	t.check(not menu.visible and title.visible and t.tree.paused and GameClock.now == clock, "설정 Esc → 타이틀, 세계/전투 시계 계속 정지")
	GameSettings.set_volume("Master", volume)
	await t.click(title._btn_rect(3).get_center())
	t.check(title.screen == title.Screen.CREDITS and title.visible and t.tree.paused, "크레딧 실제 메뉴")
	await t.shot("credits")
	await t.click(title.license_button_rect().get_center())
	t.check(title.license_view.visible and title.license_view.text.contains("SIL OPEN FONT LICENSE")
		and title.license_view.text.contains("Nathan Hoad") and title.license_view.text.contains("Godot"), "폰트·대화 시스템·엔진 라이선스 원문")
	await t.key(KEY_ESCAPE)
	t.check(title.screen == title.Screen.MENU and not title.license_view.visible and t.tree.paused, "크레딧 Esc → 타이틀")
	# 7개 유효 파일 fixture로 실제 페이지 버튼/행 입력을 본다. 이 fixture는 이 격리 폴더에만 산다.
	var extra_ids: Array[String] = []
	var original_data: Dictionary = PROFILES.read_checked(a_path, a_id).data
	for index in 5:
		var id := "doho_" + str(index + 550).sha256_text().substr(0, 24)
		var data := original_data.duplicate(true)
		data.character.name = "ExtraDoho" + str(index)
		data.profile.id = id
		data.profile.name = data.character.name
		data.profile.created_at = "2026-01-01T00:00:00"
		t.check(PROFILES.write_json(PROFILES.path_for(directory, id), data, false).is_empty(), "목록 페이지 격리 fixture")
		extra_ids.append(id)
	await t.click(title._btn_rect(1).get_center())
	t.check(title._profiles.size() == 7 and title._page == 0, "6행을 넘으면 페이지 제공")
	await t.click(title.page_rect(1).get_center())
	t.check(title._page == 1 and title.dialog_rect().encloses(title.selection_row_rect(0)), "다음 페이지의 보이는 행/입력 영역 일치")
	await t.click(title.selection_row_rect(0).get_center())
	t.check(title._selected_id == title._profiles[6].id, "둘째 페이지 행 클릭 → 그 파일 선택")
	await t.click(title.page_rect(0).get_center())
	t.check(title._page == 0, "이전 페이지 실제 클릭")
	await t.click(title.back_rect().get_center())
	for id in extra_ids:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(PROFILES.path_for(directory, id)))
	for path in [a_path, b_path]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(directory))
	SaveSystem.use_save_context(original_context)
	t.main.start_game(false)
