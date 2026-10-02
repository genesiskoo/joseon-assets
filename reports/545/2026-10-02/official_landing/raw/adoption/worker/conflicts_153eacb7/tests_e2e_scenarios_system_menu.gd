extends E2eScenario
## 실제 입력으로 정지/설정/타이틀 이어하기와 실패 보호를 확인한다 (#156, design/system_menu_156.md · testing.md §2).
## 예약 타격은 실제 `_strike` 경로에 닿은 횟수만 세는 적(HitProbe)으로 잰다 — 명중 난수·피해와 무관. 서명은 Enemy.receive_attack 그대로(덮어쓰기 규칙).
class HitProbe extends Enemy:
	var land_calls := 0
	func receive_attack(_rng: RandomNumberGenerator, _dmg_min: float, _dmg_max: float, _mult: float, _accuracy: float, _str_pct: float = 0.0, _crit_chance: float = 0.0, _blow: Dictionary = {}, _adds: Dictionary = {}, _mods: Dictionary = {}) -> int:
		land_calls += 1
		return 0


## #550: 네 메뉴의 「기존 캐릭터」 → 실제 선택 행 → 이어가기.
func _continue(title: Node) -> void:
	if title.screen != title.Screen.MENU:
		await t.click(title.back_rect().get_center())
	await t.click(title._btn_rect(1).get_center())
	await t.click(title.selection_row_rect(0).get_center())
	await t.click(title.confirm_rect().get_center())


func run() -> void:
	var menu: Node = t.hud_panel("SystemMenu")
	var title: Node = t.hud_panel("Title")
	var bag: Node = t.hud_panel("Inventory")
	var p: Node = t.player()
	var original_save_context := SaveSystem.save_path
	var menu_save_context := "user://system_menu_550_" + str(Time.get_ticks_usec()) + ".json"
	SaveSystem.use_save_context(menu_save_context)
	t.check(GameSettings.settings_path == "user://settings_e2e.cfg", "테스트 설정 격리")
	var original_volumes: Dictionary = GameSettings.volumes.duplicate()
	var original_screen: bool = GameSettings.fullscreen
	var original_blood: bool = GameSettings.blood_fx
	await t.key(KEY_I)
	t.check(bag.visible, "가방 키로 열림")
	await t.key(KEY_ESCAPE)
	t.check(not bag.visible and not menu.visible and not t.tree.paused, "첫 Esc는 열린 창만 닫음")
	await t.key(KEY_ESCAPE)
	t.check(menu.visible and t.tree.paused, "다음 Esc는 메뉴와 일시정지")
	await _check_build_labels(menu, title)
	var menu_version: Label = menu.get_node("BuildVersion")
	await t.click(menu_version.get_global_rect().get_center())
	t.check(menu.visible and not menu.settings_open and t.tree.paused, "버전 글씨 클릭은 메뉴 동작을 선택하지 않음")
	var position: Vector3 = p.global_position
	var clock := GameClock.now   # 전투 시계(#234) = 물리 델타의 합 — 트리가 멈추면 셸 _physics_process가 안 돌아 저절로 선다
	await t.seconds(0.12)
	t.check(p.global_position.distance_to(position) < 0.001, "메뉴에서 월드 이동 정지")
	t.check(GameClock.now == clock, "전투 경직/연속타 시계도 정지")
	await t.shot("menu")
	await t.click(menu.button_rect(1).get_center())
	t.check(menu.settings_open, "설정 버튼 실제 클릭")
	t.check(menu.menu_rect().encloses(menu_version.get_global_rect()) and menu_version.position.y > menu.menu_rect().end.y - 36, "설정에서도 버전은 안내 아래·패널 안")
	var values := [0.37, 0.45, 0.63, 0.0]
	for i in values.size():
		var r: Rect2 = menu.volume_rect(i)
		await t.click(Vector2(r.position.x + r.size.x * values[i], r.get_center().y))
		t.check(absf(GameSettings.volume(GameSettings.BUSES[i]) - values[i]) < 0.011, "실제 음량 슬라이더 %d" % i)
	t.check(AudioServer.is_bus_mute(AudioServer.get_bus_index("UI")), "UI 0퍼센트는 음소거")
	var cfg := ConfigFile.new()
	t.check(cfg.load(GameSettings.settings_path) == OK and is_equal_approx(float(cfg.get_value("audio", "Master")), 0.37), "설정 별도 파일 저장")
	await t.shot("settings")
	await t.click(menu.blood_rect().get_center())
	t.check(GameSettings.blood_fx != original_blood and GameState.blood_fx == GameSettings.blood_fx, "피 표현 버튼은 즉시 게임에 적용")
	var blood_saved := ConfigFile.new()
	t.check(blood_saved.load(GameSettings.settings_path) == OK and blood_saved.get_value("visual", "blood_fx", null) == GameSettings.blood_fx, "피 표현은 사용자 설정 파일에 저장")
	await t.shot("settings_blood")
	await t.click(menu.display_rect().get_center())
	t.check(GameSettings.fullscreen != original_screen, "화면 버튼 선택 변경")
	if DisplayServer.get_name() != "headless":
		t.check((DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN) == GameSettings.fullscreen, "실제 창 모드 변경")
	await t.click(menu.display_rect().get_center())
	t.check(GameSettings.fullscreen == original_screen, "화면 버튼 되돌리기")
	await t.key(KEY_ESCAPE)
	t.check(menu.visible and not menu.settings_open and t.tree.paused, "설정 Esc는 메뉴로")
	await t.key(KEY_ESCAPE)
	t.check(not menu.visible and not t.tree.paused, "메뉴 Esc는 게임으로")

	# RNG와 피해량에 의존하지 않고 실제 _strike 예약의 호출 횟수를 잰다.
	var enemy: Enemy = load("res://actors/enemy.tscn").instantiate()
	enemy.set_script(HitProbe)
	enemy.def = t.enemy_def("bandit")
	enemy.area_level = 1
	t.level().add_child(enemy)
	enemy.global_position = p.global_position + Vector3(2, 0, 0)
	enemy.set_physics_process(false)
	p.combat.cooldowns[0] = 1.0
	p.stagger(0.8)
	p.combat._strike(enemy, 1.0, 0.5, false)
	await t.key(KEY_ESCAPE)
	var cooldown: float = p.combat.cooldowns[0]
	var stagger_left: float = p._stagger_until - GameClock.now
	await t.seconds(0.7)
	t.check(enemy.get("land_calls") == 0, "0.5초 뒤 예약 타격은 메뉴 0.7초 동안 미실행")
	t.check(is_equal_approx(p.combat.cooldowns[0], cooldown), "쿨다운 정지")
	t.check(is_equal_approx(p._stagger_until - GameClock.now, stagger_left), "남은 경직 시간 보존")
	var selected: int = p.combat.active_skill
	var belt_count: int = GameState.inventory.belt[0].stack
	t._key_state(KEY_F2, true)
	t._key_state(KEY_1, true)
	await t.frames(2)
	await t.key(KEY_ESCAPE)
	t._key_state(KEY_F2, false)
	t._key_state(KEY_1, false)
	await t.frames(2)
	t.check(p.combat.active_skill == selected and GameState.inventory.belt[0].stack == belt_count, "메뉴에서 누른 키는 복귀 후 새 스킬/소비 입력이 아님")
	t.check(not p._holding and p.combat.target == null, "복귀 후 홀드/추적 입력 없음")
	await t.wait_until(func() -> bool: return enemy.get("land_calls") == 1, 2.0)
	t.check(enemy.get("land_calls") == 1, "복귀 후 남은 예약 타격 한 번 실행")
	# 새 판으로 넘어가는 reset_session은 옛 예약을 취소한다.
	p.combat._strike(enemy, 1.0, 0.15, false)
	p.combat.reset_session()
	await t.seconds(0.25)
	t.check(enemy.get("land_calls") == 1, "새 판은 이전 예약 타격을 버림")
	var freed_target: WeakRef = weakref(enemy)
	p.combat._strike(enemy, 1.0, 0.15, false)
	enemy.queue_free()
	await t.seconds(0.25)
	t.check(freed_target.get_ref() == null, "예약 타격 대상이 먼저 지워져도 오류 없이 취소")

	# 귀환문 진입 연출 중 타이틀로 나가면 이전 이동 예약은 새 판에서 취소된다.
	t.main.load_area(&"heukrang_gul", 1, Level.SpawnHint.DEFAULT)
	await t.frames(3)
	GameState.inventory.add_auto(ItemInstance.create(ItemDb.get_def("town_portal")))
	t.main._on_town_portal_requested()
	t.main._on_portal_used()
	await t.key(KEY_ESCAPE)
	t.check(menu.visible and t.tree.paused, "귀환문 예약 도중 메뉴")
	await t.click(menu.button_rect(2).get_center())
	await _continue(title)
	await t.seconds(0.85)
	t.check(GameState.area_id == &"heukrang_gul" and GameState.floor_no == 1, "새 판에서 옛 귀환문 예약이 마을로 보내지 않음")

	# 같은 프로세스이지만 실제 메뉴/타이틀 버튼 → 파일 load 경로를 검증한다.
	for location in [[&"deulnyeok", 0], [&"heukrang_gul", 2]]:
		t.main.load_area(location[0], location[1], Level.SpawnHint.DEFAULT)
		await t.frames(3)
		GameState.inventory.gold = 15600 + location[1]
		await t.key(KEY_ESCAPE)
		await t.click(menu.button_rect(2).get_center())
		t.check(title.visible and not menu.visible and t.tree.paused, "저장 후 타이틀 실제 클릭")
		var title_version: Label = title.get_node("BuildVersion")
		t.check(title_version.is_visible_in_tree() and not menu_version.is_visible_in_tree(), "타이틀 복귀는 타이틀 버전만 표시")
		await t.click(title_version.get_global_rect().get_center())
		t.check(title.visible and t.tree.paused and GameState.area_id == location[0], "타이틀 버전 클릭은 여정을 시작하지 않음")
		await t.shot("title_" + String(location[0]))
		GameState.inventory.gold = 0
		await _continue(title)
		t.check(not title.visible and not t.tree.paused, "이어하기 실제 클릭 → 게임")
		t.check(GameState.area_id == location[0] and GameState.floor_no == location[1], "같은 지역과 층 복원")
		t.check(GameState.inventory.gold == 15600 + location[1], "같은 엽전 복원")
	await t.key(KEY_ESCAPE)
	var save_path: String = SaveSystem.save_path
	var good_text := FileAccess.get_file_as_string(save_path)
	SaveSystem.save_path = "user://menu156_missing_directory/save.json"
	await t.click(menu.button_rect(2).get_center())
	t.check(menu.visible and t.tree.paused and not title.visible and menu.get("_error") != "", "저장 실패는 메뉴에 머묾")
	t.check(FileAccess.get_file_as_string(save_path) == good_text, "저장 실패가 기존 저장을 덮지 않음")
	SaveSystem.save_path = save_path
	await t.click(menu.button_rect(2).get_center())
	t.check(title.visible, "다시 저장 성공하면 타이틀")
	good_text = FileAccess.get_file_as_string(save_path)
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	file.store_string("{broken"); file.close()
	await _continue(title)
	t.check(title.visible and t.tree.paused and title._error != "", "손상된 이어하기는 타이틀에 오류 표시")
	t.check(FileAccess.get_file_as_string(save_path) == "{broken", "손상 파일을 자동 저장으로 덮지 않음")
	file = FileAccess.open(save_path, FileAccess.WRITE)
	file.store_string(good_text); file.close()
	await _continue(title)
	t.check(not title.visible and not t.tree.paused, "정상 저장으로 복구 후 이어하기")
	for bus in original_volumes:
		GameSettings.set_volume(bus, original_volumes[bus])
	GameSettings.set_fullscreen(original_screen)
	GameSettings.set_blood_fx(original_blood)
<<<<<<< HEAD


func _check_build_labels(menu: Node, title: Node) -> void:
	var menu_version: Label = menu.get_node("BuildVersion")
	var title_version: Label = title.get_node("BuildVersion")
	var original: String = BuildInfo.label()
	t.check(menu_version.text == original and title_version.text == original, "두 화면은 실제 빌드 정보와 같은 버전 표시")
	t.check(menu_version.mouse_filter == Control.MOUSE_FILTER_IGNORE and title_version.mouse_filter == Control.MOUSE_FILTER_IGNORE, "버전 글씨는 별도 마우스 캡처 없음")
	t.check(menu_version.is_visible_in_tree() and not title_version.is_visible_in_tree(), "Esc 메뉴만 열면 메뉴 버전만 표시")
	# 정식 포맷의 긴 번호·커밋으로 최소 폭이 바뀌어도 우측 끝과 안내 행을 유지한다.
	menu_version.text = "v0.123.456789 · 0123456789abcdef · 10-01"
	title_version.text = menu_version.text
	await t.frames(3)
	_check_build_bounds(menu, title)
	if DisplayServer.get_name() != "headless":
		var win := t.tree.root
		var original_size := win.size
		for resolution in [Vector2i(1280, 720), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
			win.size = resolution
			await t.frames(8)
			_check_build_bounds(menu, title)
		win.size = original_size
		await t.frames(8)
	menu_version.text = original
	title_version.text = original
	await t.frames(3)


func _check_build_bounds(menu: Node, title: Node) -> void:
	var menu_version: Label = menu.get_node("BuildVersion")
	var title_version: Label = title.get_node("BuildVersion")
	var mr: Rect2 = menu_version.get_global_rect()
	var tr: Rect2 = title_version.get_global_rect()
	var viewport: Rect2 = title.get_viewport_rect()
	t.check(menu.menu_rect().encloses(mr) and is_equal_approx(mr.end.x, menu.menu_rect().end.x - 24), "긴 메뉴 버전은 잘림 없이 우측 여백 유지")
	t.check(viewport.encloses(tr) and is_equal_approx(tr.end.x, viewport.end.x - 24), "긴 타이틀 버전은 잘림 없이 우측 여백 유지")
	t.check(title.footer_rect().end.y < tr.position.y, "타이틀 오류 안내 행은 버전 행과 분리")
	var clear: bool = mr.position.y > menu.menu_rect().end.y - 36
	for i in 4:
		clear = clear and not mr.intersects(menu.button_rect(i))
	t.check(clear, "메뉴 버전은 안내와 버튼 영역 밖")
=======
	# 이 시험이 만든 단일 파일·이관본만 정리하고 다음 대본의 save_e2e 문맥으로 돌아간다.
	var profile_directory := SaveSystem.profile_directory()
	if SaveSystem.active_profile_id != "":
		SaveSystem.delete_save()
	if FileAccess.file_exists(menu_save_context):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(menu_save_context))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(profile_directory))
	SaveSystem.use_save_context(original_save_context)
>>>>>>> 153eacb7 (feat(#550): add safe character profiles and title menus)
