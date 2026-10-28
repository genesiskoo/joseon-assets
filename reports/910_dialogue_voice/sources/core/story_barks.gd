extends RefCounted
## #777 · 승인 #770: 도착/봉밀굴 한마디를 기존 Bark로 잇는다. flags.story에 실제로 뜬 줄만 1회 기록한다.
## QuestWatch가 쥐는 작은 신호 수신자라 Main의 이동/입력 구조는 늘리지 않는다. 층 이동으로 지난 장소의 말은 버린다.
## 컷·대화·메뉴·먹 이동·다른 머리 위 글이 끝난 뒤 말한다. 음성은 Bark의 공통 경로가 맡는다.

const RESIDENTS := preload("res://world/town_residents.gd")
const ENDING := preload("res://core/ending.gd")
const ARRIVAL := "거, 술 한잔할 데가 없구먼."
const BONGMIL_ENTRY := "발소리도 아껴야겠군."
const BONGMIL_LAST := "이 안이 끝이겠군."
const ARRIVAL_KEY := "bark/doho_arrival"
const ENTRY_KEY := "bark/bongmil_entry"
const LAST_KEY := "bark/bongmil_last"
const DOHO_HEIGHT := 1.7
const AFTER_ENTRY := 0.8

static var armed: bool = true

var _main: Node
var _level: WeakRef
var _key := ""
var _line := ""
var _ready_at := 0.0
var _connected := false


func _init(main: Node) -> void:
	_main = main
	EventBus.level_loaded.connect(_on_level_loaded)


## e2e 러너만 기본으로 재운다. 정상 실행은 처음부터 true, dialogue_audit는 정상 오프닝 닫힘까지 같은 경로로 잰다.
static func set_armed(on: bool) -> void:
	armed = on
	RESIDENTS.armed = on


func _on_level_loaded(level: Node3D) -> void:
	_level = weakref(level)
	_key = ""
	_line = ""
	_ready_at = GameClock.now + AFTER_ENTRY
	if not _connected:
		_main.get_tree().physics_frame.connect(_tick)
		_connected = true
	if GameState.is_town():
		if armed:
			var residents := RESIDENTS.new()
			residents.name = "TownResidents"
			residents.configure(_main)
			level.add_child(residents)
		var story := DialogueStory.new(GameState.flags)
		if GameState.town_visits <= 1 and not ENDING.begun(GameState.flags) and not story.flag("jumo_met") and not story.flag("event/shaman_quest"):
			_queue(ARRIVAL_KEY, ARRIVAL)
	elif GameState.area_id == &"bongmil_gul" and not ENDING.begun(GameState.flags):
		if GameState.floor_no == 1:
			_queue(ENTRY_KEY, BONGMIL_ENTRY)
		elif GameState.floor_no == AreaDb.get_def(&"bongmil_gul").boss_floor:
			_queue(LAST_KEY, BONGMIL_LAST)


func _queue(key: String, text: String) -> void:
	if not DialogueStory.new(GameState.flags).flag(key):
		_key = key
		_line = text


func _tick() -> void:
	if not armed or _key == "" or GameClock.now < _ready_at or not RESIDENTS.can_speak(_main):
		return
	var level: Node = _level.get_ref() if _level != null else null
	if level == null or not level.is_inside_tree() or level != _main.current_level:
		_key = ""
		return
	var story := DialogueStory.new(GameState.flags)
	if ENDING.begun(GameState.flags) or (_key == ARRIVAL_KEY and (story.flag("jumo_met") or story.flag("event/shaman_quest"))):
		_key = ""   # 기다리는 사이 이야기 단계가 바뀌면 지난 말은 꺼내지 않는다.
		_line = ""
		return
	var player := _main.get_tree().get_first_node_in_group("player") as Node3D
	if player == null or Bark.current(player) != null:
		return
	if Bark.say(player, _line, DOHO_HEIGHT) == null:
		return
	story.put(_key)
	SaveSystem.save_now("story bark")
	_key = ""
	_line = ""
