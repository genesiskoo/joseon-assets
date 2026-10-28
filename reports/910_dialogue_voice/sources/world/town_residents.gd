extends Node3D
## #777 · 승인 #772: 기존 영감/촌장 몸 두 종을 색으로 나눠 주거 거리에 세운다. 6명, 엔딩 완료 뒤 2명 추가.
## 주민은 서비스·클릭·충돌·내비 장애물 없이 기존 모델과 Bark만 쓴다. 가까운 한 사람이 한 걸음에 단계별 한 번만 말한다.
## 전용 주민 모델을 새로 생성하는 대안은 아트 선행을 늘리므로 기각. 실제 NPC 정의와 분리해 좌판·대화 호출에 섞이지 않는다.

const FLAT := preload("res://core/flat.gd")
const ENDING := preload("res://core/ending.gd")
const AV := preload("res://actors/actor_visual.gd")
const MODELS := [preload("res://data/models/merchant_v2.tres"), preload("res://data/models/elder_v2.tres")]
const TINTS := [Color(0.74, 0.83, 0.80), Color(0.83, 0.73, 0.69), Color(0.70, 0.75, 0.86)]
const SPOTS := [Vector3(-10.4, 0, -4.4), Vector3(-14.2, 0, -7.2), Vector3(-14.2, 0, -0.7), Vector3(-11.3, 0, 4.4),
	Vector3(-14.2, 0, 8.4), Vector3(-8.5, 0, 11.6), Vector3(-11.1, 0, -8.6), Vector3(-10.9, 0, 8.5)]
const BEFORE := ["어이쿠, 도사 양반이 오셨네.", "옆 마을도 문 닫은 지 오래라던디…", "밤엔 문 꼭 걸어요. 바람 소리도 수상하니.", "장터 열리면 두부부터 사야지."]
const AFTER_HEUKRANG := ["굴 쪽이 잠잠해졌다더니, 장터에 장돌뱅이 하나 들어왔더군. 보따리에 별게 다 들었다던데.", "이제 좀 살겠구먼."]
const AFTER_ENDING := ["하늘이 좀 맑아진 것 같우.", "도사 양반, 고맙수. 술 한잔은 나중에라도 꼭 내리다."]
const RADIUS := 3.0
const INTERVAL := 10.0

static var armed: bool = true

var _main: Node
var _people: Array[Node3D] = []
var _said: Dictionary = {}
var _next_at := 0.0


func configure(main: Node) -> void:
	_main = main


func _ready() -> void:
	add_to_group("town_residents")
	_refresh_people()
	_next_at = GameClock.now + 4.0


func _physics_process(_delta: float) -> void:
	if not armed:
		return
	_refresh_people()
	if GameClock.now < _next_at or not can_speak(_main):
		return
	var player := get_tree().get_first_node_in_group("player") as Node3D
	if player == null or Bark.current(player) != null:
		return
	var index := nearest_index(player.global_position)
	if index < 0:
		return
	var stage := _stage()
	var key := "%s/%d" % [stage, index]
	if _said.has(key):
		return
	var line := line_for(stage, index)
	var read_sec := maxf(Bark.SEC, float(line.length()) * 0.06 + 1.2)
	if Bark.say(_people[index], line, MODELS[index % 2].target_height, read_sec) == null:
		return
	_said[key] = true
	_next_at = GameClock.now + INTERVAL


static func can_speak(main: Node) -> bool:
	if main == null or not is_instance_valid(main) or not main.is_inside_tree():
		return false
	var tree := main.get_tree()
	if tree.paused or not main._started or main._dying or main._traveling or main._travel_held or main.fade_alpha() > 0.02:
		return false
	var band := DialogueBand.find(tree)
	if band != null and band.is_open():
		return false
	for panel in tree.get_nodes_in_group("panel_ui"):
		# HUD도 PanelUi지만 항상 표시되는 하단 판이다. 실제로 여닫는 창만 한마디를 기다리게 한다.
		if panel is PanelUi and panel.closable_by_esc and panel.is_visible_in_tree():
			return false
	return true


func _stage() -> String:
	if ENDING.finished(GameState.flags):
		return "ending"
	return "heukrang" if Quest.den_cleared(GameState.flags, "heukrang_gul") else "before"


static func line_for(stage: String, index: int) -> String:
	var pool: Array = AFTER_ENDING if stage == "ending" else (AFTER_HEUKRANG if stage == "heukrang" else BEFORE)
	return String(pool[index % pool.size()])


func nearest_index(at: Vector3) -> int:
	var best := -1
	var distance := RADIUS
	for i in _people.size():
		var d := FLAT.dist(at, _people[i].global_position)
		if d < distance:
			distance = d
			best = i
	return best


func people() -> Array[Node3D]:
	return _people.duplicate()


func _refresh_people() -> void:
	var wanted := 8 if ENDING.finished(GameState.flags) else 6
	while _people.size() < wanted:
		_add_person(_people.size())


func _add_person(index: int) -> void:
	var person := Node3D.new()
	person.name = "Resident%d" % (index + 1)
	add_child(person)
	var level := get_parent() as Level
	person.global_position = level.walkable_point(SPOTS[index]) if level != null else SPOTS[index]
	person.rotation.y = deg_to_rad(45.0 + float(index % 3) * 75.0)
	var visual := AV.new()
	visual.name = "Visual"
	visual.albedo_tint = TINTS[floori(index / 2.0) % TINTS.size()]
	visual.model = MODELS[index % 2]
	person.add_child(visual)
	visual.freeze_idle(0.35 + float(index % 3) * 0.4)
	_people.append(person)
