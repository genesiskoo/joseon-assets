extends SceneTree
## #550 파일 경계: byte 보존 이관·id 위조·새 슬롯/쓰기 실패·손상 fail-closed.
const PROFILES = preload("res://core/character_profiles.gd")
var checks := 0
var failures: Array[String] = []
var _files: Array[String] = []
var _directories: Array[String] = []


func _init() -> void:
	_run.call_deferred()


func _check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		push_error("FAIL: " + message)


func _write(path: String, value: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(value)
	file.close()
	_files.append(path)


func _run() -> void:
	var fixture := "user://profile_unit_550_" + str(Time.get_ticks_usec())
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(fixture))
	_directories.append(fixture)
	for value in ["떠돌이도호", "FirstDoho", "도호 123"]:
		_check(PROFILES.name_error(value).is_empty(), "완성형 한글/영문/숫자 이름: " + value)
	for value in ["", "도호", "도호/../비", "도호\n님", "도호-님", "abcdefghijklmn", "ㄷㅗㅎㅗ"]:
		_check(not PROFILES.name_error(value).is_empty(), "길이·경로 문자·제어 문자 거부")
	_check(PROFILES.path_for(fixture, "../../save_v2").is_empty() and not PROFILES.valid_id("doho_00/../legacy"), "id로 폴더를 벗어나지 않음")
	var saves: Node = root.get_node("SaveSystem")
	var state: Node = root.get_node("GameState")
	state.character.level = 5
	state.character.xp = 37
	state.inventory.gold = 4321
	state.flags["legacy_proof"] = "보존"
	state.first_kills["boss_heukrang"] = 1
	var source := fixture.path_join("old_save.json")
	var data: Dictionary = saves.call("_snapshot")
	data["unused_future_field"] = {"keep": true}
	_write(source, "\n  " + JSON.stringify(data, "\t") + "\n")
	var original_bytes := FileAccess.get_file_as_bytes(source)
	var directory := fixture.path_join("characters")
	var migrated: String = PROFILES.path_for(directory, PROFILES.LEGACY_ID)
	_files.append(migrated)
	_directories.append(directory)
	_check(PROFILES.migrate_legacy(source, directory).is_empty(), "기존 저장 이관 성공")
	_check(FileAccess.get_file_as_bytes(source) == original_bytes and FileAccess.get_file_as_bytes(migrated) == original_bytes, "이관 원본·복사본 byte 완전 동일")
	var loaded := PROFILES.read_checked(migrated, PROFILES.LEGACY_ID)
	_check(loaded.error == "" and loaded.data.inventory.gold == 4321 and loaded.data.character.level == 5 and loaded.data.flags.legacy_proof == "보존"
		and loaded.data.inventory.equipment.weapon.def == "iron_sword" and loaded.data.first_kills.boss_heukrang == 1, "옛 진행·장비·인벤·엽전·첫처치 보존")
	_write(source, "{broken")
	_check(PROFILES.migrate_legacy(source, directory).is_empty() and FileAccess.get_file_as_bytes(migrated) == original_bytes and FileAccess.get_file_as_string(source) == "{broken", "이관 재호출은 원본·이관본을 덮지 않음")
	var corrupt_source := fixture.path_join("corrupt_save.json")
	_write(corrupt_source, "{broken")
	var refused_directory := fixture.path_join("refused")
	_check(not PROFILES.migrate_legacy(corrupt_source, refused_directory).is_empty() and not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(refused_directory))
		and FileAccess.get_file_as_string(corrupt_source) == "{broken", "깨진 원본은 적용/복사 없이 보존")
	var a_id := "doho_111111111111111111111111"
	var b_id := "doho_222222222222222222222222"
	var a := data.duplicate(true)
	a.character.name = "첫도호님"
	a["profile"] = {"id": a_id, "name": a.character.name, "class_id": "doho", "model_id": "doho", "created_at": "2026-10-02T01:00:00"}
	var b := a.duplicate(true)
	b.character.name = "둘째도호"
	b.character.level = 1
	b.inventory.gold = 0
	b.profile = {"id": b_id, "name": b.character.name, "class_id": "doho", "model_id": "doho", "created_at": "2026-10-02T02:00:00"}
	var a_path := PROFILES.path_for(directory, a_id)
	var b_path := PROFILES.path_for(directory, b_id)
	_files.append_array([a_path, b_path])
	_check(PROFILES.write_json(a_path, a, false).is_empty() and PROFILES.write_json(b_path, b, false).is_empty(), "서로 다른 슬롯 두 개 생성")
	var a_bytes := FileAccess.get_file_as_bytes(a_path)
	_check(not PROFILES.write_json(a_path, b, false).is_empty() and FileAccess.get_file_as_bytes(a_path) == a_bytes, "신규 생성은 기존 슬롯을 덮지 않음")
	_check(PROFILES.duplicate_name(directory, " 첫도호님 ") and not PROFILES.duplicate_name(directory, "새도호님"), "정규화한 중복 이름 확인")
	_check(PROFILES.read_checked(a_path, b_id).data.is_empty(), "파일과 profile id가 다른 위조 거부")
	var invalid := a.duplicate(true)
	invalid.profile.class_id = "guisae"
	_check(not PROFILES.profile_error(invalid, a_id).is_empty(), "EA 도호 외 클래스 거부")
	invalid = a.duplicate(true)
	invalid.profile.name = "다른이름"
	_check(not PROFILES.profile_error(invalid, a_id).is_empty(), "프로필·상태 이름 불일치 거부")
	var absent_path := fixture.path_join("missing/save.json")
	_check(not PROFILES.write_json(absent_path, b).is_empty() and FileAccess.get_file_as_bytes(a_path) == a_bytes, "쓰지 못하는 폴더는 기존 저장을 건드리지 않음")
	_write(b_path, "{broken")
	var rows := PROFILES.list_profiles(directory)
	_check(rows.size() == 3 and rows.filter(func(info: Dictionary) -> bool: return info.valid).size() == 2, "손상 파일은 목록에 남고 선택 불가")
	var old_context: String = saves.save_path
	saves.call("use_save_context", fixture.path_join("session.json"))
	_check(saves.call("create_profile", "새도호님", false), "SaveSystem 새 캐릭터 생성")
	var created_id: String = saves.active_profile_id
	var created_path: String = saves.save_path
	var created_directory: String = saves.call("profile_directory")
	_files.append(created_path)
	_directories.append(created_directory)
	_check(state.character.name == "새도호님" and state.character.level == 1 and state.inventory.gold == 0 and state.flags.get("opening_pending") == false,
		"새 프로필 = 실제 시작 장비·Lv1·새 진행")
	state.inventory.gold = 550
	_check(saves.call("save_now", "unit550"), "현재 프로필 자동 저장")
	var good_bytes := FileAccess.get_file_as_bytes(created_path)
	saves.save_path = source
	_check(not saves.call("save_now", "redirect550") and FileAccess.get_file_as_bytes(created_path) == good_bytes and FileAccess.get_file_as_string(source) == "{broken", "활성 프로필의 외부 save_path 변경은 두 파일을 덮지 않고 거부")
	saves.save_path = created_path
	_check(not saves.call("create_profile", "새도호님", false) and saves.active_profile_id == created_id and state.inventory.gold == 550 and FileAccess.get_file_as_bytes(created_path) == good_bytes,
		"중복 생성 실패는 현재 선택·상태·파일 보존")
	state.character.name = "저장/불가"
	_check(not saves.call("save_now", "internal550") and FileAccess.get_file_as_bytes(created_path) == good_bytes, "현재 상태·profile 이름 불일치는 쓰기 전 거부")
	state.character.name = "새도호님"
	DirAccess.remove_absolute(ProjectSettings.globalize_path(created_path))
	_check(not saves.call("save_now", "missing550") and not FileAccess.file_exists(created_path) and state.inventory.gold == 550, "사라진 활성 파일을 자동 저장으로 재생성하지 않음")
	var restore_file := FileAccess.open(created_path, FileAccess.WRITE)
	restore_file.store_buffer(good_bytes)
	restore_file.close()
	_write(created_path, "{broken")
	_check(not saves.call("save_now", "damage550") and FileAccess.get_file_as_string(created_path) == "{broken", "손상된 활성 파일은 자동 저장으로 덮지 않음")
	_check(not saves.call("select_profile", created_id) and state.inventory.gold == 550, "손상 선택은 GameState 그대로")
	var blocker := fixture.path_join("occupied")
	_write(blocker, "regular file")
	saves.call("use_save_context", blocker.path_join("save.json"))
	_check(not saves.call("create_profile", "쓰지못함", false) and state.inventory.gold == 550 and state.character.name == "새도호님", "생성 폴더 실패도 지금 판 그대로")
	saves.call("use_save_context", "user://save_v2.json")
	var legacy_exists := FileAccess.file_exists("user://save_v2.json")
	var legacy_bytes := FileAccess.get_file_as_bytes("user://save_v2.json") if legacy_exists else PackedByteArray()
	_check(not saves.call("save_now", "legacy_guard550") and FileAccess.file_exists("user://save_v2.json") == legacy_exists
		and (not legacy_exists or FileAccess.get_file_as_bytes("user://save_v2.json") == legacy_bytes), "기본 원본 경로는 자동 저장 입구에서도 보존")
	saves.call("begin_fresh_session")
	_check(saves.save_path == "user://save_dev_new.json" and saves.active_profile_id == "", "명시적 기본 새 판은 옛 save_v2와 프로필을 피하는 개발 슬롯")
	saves.call("use_save_context", old_context)
	for path in _files:
		if FileAccess.file_exists(path):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
		if FileAccess.file_exists(path + ".tmp"):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(path + ".tmp"))
	_directories.reverse()
	for path in _directories:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	print("CHARACTER_PROFILES_TEST checks=%d fails=%d %s" % [checks, failures.size(), "PASS" if failures.is_empty() else "FAIL"])
	quit(0 if failures.is_empty() else 1)
