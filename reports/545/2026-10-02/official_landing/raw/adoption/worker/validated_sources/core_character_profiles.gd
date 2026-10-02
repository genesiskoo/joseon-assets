class_name CharacterProfiles
extends RefCounted
## #550: 상태는 SaveCodec 그대로, 프로필은 한 파일 안. UI·GameState 없는 파일 IO.
const CODEC = preload("res://core/save_codec.gd")
const CLASS_ID := "doho"
const LEGACY_ID := "legacy"


static func valid_id(id: String) -> bool:
	var pattern := RegEx.new()
	pattern.compile("^(legacy|doho_[0-9a-f]{24})$")
	return pattern.search(id) != null


static func name_error(value: String) -> String:
	var cleaned := value.strip_edges()
	if cleaned.length() < 3 or cleaned.length() > 12:
		return "이름은 3~12자로 지어 주세요"
	var pattern := RegEx.new()
	pattern.compile("^[가-힣A-Za-z0-9][가-힣A-Za-z0-9 ]*[가-힣A-Za-z0-9]$")
	if pattern.search(cleaned) == null:
		return "이름에는 한글·영문·숫자만 쓸 수 있습니다"
	return ""


static func path_for(directory: String, id: String) -> String:
	return directory.path_join(id + ".json") if valid_id(id) else ""


static func read_checked(path: String, id: String = "") -> Dictionary:
	if path.is_empty() or (not id.is_empty() and not valid_id(id)):
		return {"data": {}, "error": "캐릭터 정보가 올바르지 않습니다"}
	if not FileAccess.file_exists(path):
		return {"data": {}, "error": "저장 파일을 찾지 못했습니다"}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {"data": {}, "error": "저장 파일을 읽지 못했습니다"}
	var parser := JSON.new()
	var result := parser.parse(file.get_as_text())
	file.close()
	if result != OK or not parser.data is Dictionary:
		return {"data": {}, "error": "저장 파일이 손상되었습니다"}
	var data: Dictionary = parser.data
	var problem: String = CODEC.validation_error(data)
	if problem.is_empty() and not id.is_empty():
		problem = profile_error(data, id)
	if not problem.is_empty():
		return {"data": {}, "error": "저장 파일을 불러올 수 없습니다: " + problem}
	return {"data": data, "error": ""}


static func profile_error(data: Dictionary, id: String) -> String:
	if id == LEGACY_ID and not data.has("profile"):
		return ""
	var raw: Variant = data.get("profile")
	if not raw is Dictionary:
		return "캐릭터 식별 정보 없음"
	var profile: Dictionary = raw
	if profile.get("id") != id or not valid_id(id):
		return "캐릭터 식별 정보 불일치"
	if profile.get("class_id") != CLASS_ID or profile.get("model_id") != CLASS_ID:
		return "지원하지 않는 캐릭터"
	if not profile.get("name") is String or not profile.get("created_at") is String:
		return "캐릭터 표시 정보 형식"
	if (id != LEGACY_ID and not name_error(String(profile.name)).is_empty()) or String(profile.name).is_empty():
		return "캐릭터 이름 형식"
	if profile.name != data.character.name:
		return "캐릭터 이름 불일치"
	return ""


static func metadata(data: Dictionary, id: String) -> Dictionary:
	if data.get("profile") is Dictionary:
		return (data.profile as Dictionary).duplicate()
	return {"id": id, "name": String(data.character.name), "class_id": CLASS_ID, "model_id": CLASS_ID,
		"created_at": String(data.get("saved_at", ""))}


static func list_profiles(directory: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(directory)):
		return result
	var folder := DirAccess.open(directory)
	if folder == null:
		return result
	for filename in folder.get_files():
		if not filename.ends_with(".json") or not valid_id(filename.get_basename()):
			continue
		var id := filename.get_basename()
		var read := read_checked(path_for(directory, id), id)
		if not String(read.error).is_empty():
			result.append({"id": id, "name": "기존 캐릭터" if id == LEGACY_ID else "불러올 수 없는 캐릭터",
				"valid": false, "error": read.error, "level": 0, "location": "저장 확인 필요", "model_id": CLASS_ID, "created_at": ""})
			continue
		var data: Dictionary = read.data
		var normalized: Dictionary = CODEC.normalize(data)
		CODEC.sanitize(normalized)
		var info := metadata(data, id)
		result.append({"id": id, "name": info.name, "valid": true, "error": "", "level": int(normalized.character.level),
			"location": AreaDb.label(normalized.area_id, normalized.floor_no), "model_id": info.model_id,
			"created_at": info.created_at, "gold": int(normalized.inventory.gold)})
	result.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if a.created_at == b.created_at:
			return String(a.id) < String(b.id)
		return String(a.created_at) > String(b.created_at))
	return result


static func duplicate_name(directory: String, value: String) -> bool:
	for info in list_profiles(directory):
		if info.valid and String(info.name).to_lower() == value.strip_edges().to_lower():
			return true
	return false


static func ensure_directory(directory: String) -> String:
	var absolute := ProjectSettings.globalize_path(directory)
	var ancestor := absolute
	while not DirAccess.dir_exists_absolute(ancestor):
		if FileAccess.file_exists(ancestor):
			return "저장 폴더를 만들지 못했습니다. 같은 자리에 파일이 있습니다"
		var parent := ancestor.get_base_dir()
		if parent == ancestor or parent.is_empty():
			return "저장 폴더 경로가 올바르지 않습니다"
		ancestor = parent
	var result := DirAccess.make_dir_recursive_absolute(absolute)
	return "" if result == OK else "저장 폴더를 만들지 못했습니다 (오류 %d)" % result


static func write_json(path: String, data: Dictionary, replace: bool = true) -> String:
	if path.is_empty() or (not replace and FileAccess.file_exists(path)):
		return "기존 캐릭터를 덮어쓸 수 없습니다"
	var temporary := path + ".tmp"
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null:
		return "저장하지 못했습니다 (오류 %d)" % FileAccess.get_open_error()
	file.store_string(JSON.stringify(data, "\t"))
	file.flush()
	var result := file.get_error()
	file.close()
	if result == OK and not replace and FileAccess.file_exists(path):
		return "기존 캐릭터를 덮어쓸 수 없습니다"
	if result == OK:
		result = DirAccess.rename_absolute(ProjectSettings.globalize_path(temporary), ProjectSettings.globalize_path(path))
	return "" if result == OK else "저장하지 못했습니다 (오류 %d)" % result


static func migrate_legacy(source: String, directory: String) -> String:
	var target := path_for(directory, LEGACY_ID)
	# 이관본이 있으면 손상됐어도 재복사하지 않는다. 원본·이관본 둘 다 그대로 두고 UI가 알린다.
	if FileAccess.file_exists(target) or not FileAccess.file_exists(source):
		return ""
	var read := read_checked(source)
	if not String(read.error).is_empty():
		return "기존 저장을 보존했습니다. " + String(read.error)
	var directory_error := ensure_directory(directory)
	if not directory_error.is_empty():
		return "기존 저장을 보존했습니다. " + directory_error
	var bytes := FileAccess.get_file_as_bytes(source)
	var temporary := target + ".tmp"
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null:
		return "기존 저장 이관본을 쓰지 못했습니다"
	file.store_buffer(bytes)
	file.flush()
	var result := file.get_error()
	file.close()
	if FileAccess.file_exists(target):
		return ""
	if result == OK:
		result = DirAccess.rename_absolute(ProjectSettings.globalize_path(temporary), ProjectSettings.globalize_path(target))
	return "" if result == OK else "기존 저장을 이관하지 못했습니다 (오류 %d)" % result
