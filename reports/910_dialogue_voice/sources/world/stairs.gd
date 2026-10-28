extends Area3D
## Stairs — 층 이동 트리거. 디아1처럼 "계단을 클릭해서 도착"했을 때만 발동한다.
## 지나가다 밟는 것만으로는 안 바뀜: 플레이어의 최종 목적지가 이 계단 셀 안이어야 함(경로가 계단을 통과해도 무시).
## 마을 입구(DungeonEntrance)와 던전 계단이 같은 씬을 쓴다. 색으로 방향 구분(플레이스홀더).

enum Direction { UP = -1, DOWN = 1 }

const TRIGGER_RADIUS := 0.9

@export var direction: Direction = Direction.DOWN
## 마을·필드의 입구가 내려갈 던전 (D-077, design/areas_v2.md §3). 던전 안 계단은 비움 = 같은 던전의 위·아래 층.
@export var target_area: StringName = &""
## 타일 킷 계단 GLB(design/art_3d_pipeline.md §2.5). 파일이 있으면 박스 대신 이 모델(피벗 바닥 중앙). DungeonBuilder가 킷에서 넘긴다.
@export var model_scene_path: String = ""
## 봉인 — 비어 있지 않으면 도착해도 층을 바꾸지 않고 이 말만 한 번 띄운다(못골 북쪽 봉밀굴 문턱, field_v2.md §6).
@export_multiline var sealed_message: String = ""
## 이 플래그(GameState.flags)가 서야 열린다 (#167 — 범굴 어귀 = boss_killed_heukrang_gul). 안 섰으면 `locked_message`만. 쓰는 순간에 본다.
@export var requires_flag: String = ""
@export_multiline var locked_message: String = ""
## 봉인 조각 문 (#169 — 못골 북쪽 봉밀굴 문, design/dungeon.md §10): 이 수의 봉인 조각(Quest.seals — 세 굴 주인의 처치 표시)이 모여야 열린다. 0 = 아님.
## 모자라면 봉인 말(sealed_message) 자리에 「몇 개 모자란지」 한 줄(refresh_seal_gate — 자동 지도 「봉인된 문」도 이 칸을 읽는다) ·
## 다 모인 뒤 처음 닿으면 컷 네 줄(event/seal_gate, #549) 다음 여는 순간(open_seal_gate — 조각을 대고 · 흰 먹 파문 · 석문이 가라앉는다) — 그 닿음엔 안 내려가고, 다시 누르면 내려간다
## (들어갈지는 도호가 정한다 — 열어 두고 마을로 돌아가 채비해도 된다). 연 회차 = Quest.gate_open(flags[Quest.GATE_FLAG]) — 2회차엔 다시 닫힌다(npcs_v2 §5.4).
@export var seal_pieces: int = 0
## 겉모습을 안 그린다 (#533) — 이 문의 모양은 다른 노드가 그린다(못골 봉밀굴 문턱 = TownDressing의 #131 문턱 GLB). 박스·계단 모델만 끄고
## 클릭 자리(TRIGGER_RADIUS) · 봉인 말 · 잠금 · 문틈 빛 · 안개 · 어귀 호버는 그대로.
@export var hide_visual: bool = false

## 문틈 빛 (dungeon.md §6) — 내려가는 쪽 1.8 · 올라가는 쪽 1.2 · 반경 4.
const GLOW_RANGE := 4.0
## 잠긴 봉인 조각 문의 문틈 빛 (#533) — 못골 문턱(#131 GLB)은 빈 봉인 홈 셋·종이 부적이 문짝 앞에 있어 1.8·반경 4면 문짝 가운데가 하얗게 떴다(#131 검수).
## 닫힌 동안만 1.0·반경 3 — 가운데 빈 홈(빛에서 1.56)에 닿는 빛 0.96 → 0.48, 도호 발밑(0.9)은 2.05 → 1.13으로 여전히 푸르다(OmniLight 감쇠 1.3 셈 · test_town_gate ⑥).
## 열리면 반경 GLOW_RANGE + 여는 빛 OPEN_GLOW — 문이 가라앉고 빛이 쏟아진다. 여는 순간(open_seal_gate)과 이미 연 문으로 다시 선 마을
## (_ready — 던전 왕복·불러오기 뒤)이 같은 빛이다(_set_seal_glow 한 곳, 교차 검수 #533 — 전엔 다시 서면 계단 기본 1.8로 돌아갔다).
const SEALED_GLOW := 1.0
const SEALED_GLOW_RANGE := 3.0
const OPEN_GLOW := 2.8

## 여는 순간의 길이(초, 물리 틱) — 그동안은 다시 눌러도 안 내려간다(연출이 끊기지 않게).
const GATE_OPEN_HOLD := 1.8
## 석문(마을 장식 seal_door GLB — 무리 「seal_door」, town_dressing)이 땅으로 가라앉는 깊이 · 시간.
const DOOR_SINK := 2.6
const DOOR_SINK_SEC := 1.4
const AREA_EXIT := preload("res://world/area_exit.gd")
const RENDER_INTERP := preload("res://world/render_interp.gd")   # 물리 보간 (#700)
const COUNT_WORDS := ["", "하나", "둘", "셋", "넷", "다섯", "여섯"]
## 북쪽 돌문 첫 접근 혼잣말 (#547 · D-097 ⑦ — DIALOGUE_CRITICAL_PATH CP-04 #0 · STORY_MUDANG 장면 B0): 봉인 조각 문(seal_pieces > 0)에
## 처음 FIRST_LOOK_RADIUS(평면 유닛) 안으로 들면 도호 머리 위 한 줄(Bark) — 판에 한 번(story 플래그 = NPC 대본의 `Story.first`와 같은 칸).
## 이 줄이 떠 있는 동안 문에 닿으면 문 글(봉인 말 · 여는 순간)은 줄이 걷힌 뒤로 미룬다 — 알림 팝업도 도호 머리 위라 포개진다(「문 글보다 먼저」,
## 불가살이 「도호 머리 위 글은 한 줄씩」과 같은 규칙).
const FIRST_LOOK_LINE := "이 빛, 어디서 본 것 같은데."
const FIRST_LOOK_KEY := "gate_first_look"
## 산길 마지막 꺾임(MotgolLayout.APPROACH (1, −24) — 문까지 7.1) 뒤 곧은 길 — 문틈 빛이 화면에 든 자리.
const FIRST_LOOK_RADIUS := 6.0
## 줄이 떠 있는 시간(Bark.SEC) + 줄 사이(불가살이 LINE_GAP과 같다) — 이만큼 지나야 미룬 문 글을 낸다.
const FIRST_LOOK_HOLD := Bark.SEC + 0.1
## 도호 머리 높이 (Bark 자리 — QuestWatch.DOHO_HEIGHT와 같다).
const DOHO_HEIGHT := 1.7

var _said := false
var _gate_hold: float = 0.0
var _looked := false           # 이 판에 첫 접근 혼잣말을 이미 했다(story) — 더 안 본다
var _look_left: float = 0.0    # 혼잣말이 아직 떠 있는 시간(초)
var _touch_waiting := false    # 혼잣말 동안 문에 닿았다 — 걷히면 문 글

@onready var _mesh: MeshInstance3D = $Mesh
## 계단 빛 (dungeon.md §6): 문틈으로 새는 푸른 빛. 내려가는 쪽이 더 세다.
var _glow: OmniLight3D
var _glow_base: float = 1.2
var _t: float = 0.0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2  # player
	# 다른 지역으로 가는 어귀(같은 던전 안 위·아래 층 계단은 target_area가 빈다) — 호버가 화면 좌표로 따로 찾는다(#474, 클릭·충돌 레이어는 안 건드린다).
	if target_area != &"":
		add_to_group(&"area_gate")
	_glow = OmniLight3D.new()
	_glow.name = "Glow"
	_glow.light_color = Color(0.35, 0.6, 1.0)
	_glow_base = 1.8 if direction == Direction.DOWN else 1.2
	_glow.light_energy = _glow_base
	_glow.omni_range = GLOW_RANGE
	_glow.omni_attenuation = 1.3
	_glow.shadow_enabled = false
	_glow.position = Vector3(0, 0.9, 0)
	add_child(_glow)
	Vfx.attach("stairs_mist", self, Vector3(0, 0.3, 0))
	if hide_visual:
		_mesh.visible = false
	elif model_scene_path != "" and ResourceLoader.exists(model_scene_path):
		var ps := load(model_scene_path) as PackedScene
		if ps:
			var model := ps.instantiate()
			model.name = "Model"
			add_child(model)
			_mesh.visible = false
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.85, 0.65, 0.2) if direction == Direction.DOWN else Color(0.3, 0.7, 0.9)
	m.emission_enabled = true
	m.emission = m.albedo_color
	m.emission_energy_multiplier = 0.6
	_mesh.material_override = m
	if seal_pieces > 0:
		refresh_seal_gate()
		var open := Quest.gate_open(GameState.flags, GameState.run)
		if open:
			_sink_doors.call_deferred(false)   # 이미 연 문 — 석문은 가라앉은 채로(장식은 제 _ready에서 선다)
		_set_seal_glow(open)   # 잠김 = 낮은 문틈 빛 · 연 문 = 여는 순간 뒤와 같은 빛 (#533)


func _process(delta: float) -> void:
	_t += delta
	_glow.light_energy = _glow_base * (0.9 + 0.1 * sin(_t * 2.0))


func _physics_process(delta: float) -> void:
	_gate_hold = maxf(0.0, _gate_hold - delta)
	if seal_pieces > 0:
		_tick_first_look(delta)
	if AREA_EXIT.player_arrived(self, TRIGGER_RADIUS):
		# 잠금(이야기 조건 — 흑랑 처치)을 봉인·막힘보다 먼저 — 들어갈 곳이 아직 없어도(#354 전 범굴) 「흑랑부터」가 먼저 들린다
		if not is_open():
			if locked_message != "" and not _said:
				_said = true
				EventBus.ui_message.emit(locked_message)
			return
		# 봉인 조각 문 (#169): 이번 회차에 아직 안 열렸다 — 모자라면 한 줄, 다 모였으면 여는 순간(이번 닿음엔 안 내려간다)
		if seal_pieces > 0 and not Quest.gate_open(GameState.flags, GameState.run):
			if not _said:
				_said = true
				if _look_left > 0.0:
					_touch_waiting = true   # 첫 접근 혼잣말이 먼저 — 걷히면 문 글 (#547)
				else:
					_touch_seal_gate()
			return
		if _gate_hold > 0.0:
			return   # 여는 순간 — 끝난 뒤 다시 누르면 내려간다
		if sealed_message != "":
			if not _said:
				_said = true
				EventBus.ui_message.emit(sealed_message)
			return
		# 시그널 안에서 레벨을 갈아치우면 물리 플러시 중 노드 생성 → Main이 deferred로 처리한다.
		EventBus.stairs_used.emit(direction, target_area)
		return
	_said = false


## 요구 플래그가 섰나 (없으면 늘 열림)
func is_open() -> bool:
	return AREA_EXIT.flag_open(requires_flag)


# ---------- 봉인 조각 문 (#169, design/dungeon.md §10) ----------

## 봉인 조각 문의 문틈 빛 (#533) — 잠김 = SEALED_GLOW · 반경 SEALED_GLOW_RANGE / 열림 = OPEN_GLOW · 반경 GLOW_RANGE.
## 여는 순간(open_seal_gate)과 이미 연 문으로 다시 선 마을(_ready)이 이 한 곳을 지난다 — 같은 회차의 「열림」 빛은 언제 봐도 같다.
func _set_seal_glow(open: bool) -> void:
	_glow_base = OPEN_GLOW if open else SEALED_GLOW
	_glow.light_energy = _glow_base
	_glow.omni_range = GLOW_RANGE if open else SEALED_GLOW_RANGE


## 봉인 말 다시 쓰기 — 이번 회차에 연 문 = 빈칸(내려간다) · 아직 = 몇 개 모자란지 한 줄 · 다 모였다 = 문에 대 보자는 한 줄(닿으면 연다).
func refresh_seal_gate() -> void:
	if seal_pieces <= 0:
		return
	if Quest.gate_open(GameState.flags, GameState.run):
		sealed_message = ""
	else:
		sealed_message = seal_gate_text(_gate_name(), Quest.seals(GameState.flags), seal_pieces)


## 봉인 말 — have/need = 모인 조각 · 필요한 조각. 순수(시험이 부른다).
## 「굴 주인들이 쥔」 = 조각을 어디서 얻는지 (#546 대본 점검 A B1 — 북쪽 문에 처음 닿은 사람은 봉인 조각이 뭔지 몰랐다).
static func seal_gate_text(gate_name: String, have: int, need: int) -> String:
	if have >= need:
		return "%s 문 — 봉인 조각이 다 모였다. 문에 대 보자" % gate_name
	var miss := need - have
	var word: String = COUNT_WORDS[miss] if miss < COUNT_WORDS.size() else str(miss)
	return "%s 문이 봉인에 막혀 있다 — 굴 주인들이 쥔 봉인 조각이 %s 모자란다 (%d/%d)" % [gate_name, word, have, need]


## 여는 순간 — 조각을 문에 댄다(가방의 봉인 조각 소모, Quest.take_seal_items) · 연 회차를 적는다 · 흰 먹 파문 · 문틈 빛 · 석문이 가라앉는다 ·
## 카메라 흔들림. 시스템 알림 한 줄은 컷(event/seal_gate)이 대신한다(#549). 이 닿음엔 안 내려간다 — 다시 누르면(GATE_OPEN_HOLD초 뒤) 내려간다.
## 조각 셋이 모였는지는 부르는 쪽이 본다(dev·시험은 바로 부른다).
func open_seal_gate() -> void:
	Quest.open_gate(GameState.flags, GameState.run)
	var used := Quest.take_seal_items(GameState.inventory)
	sealed_message = ""
	_gate_hold = GATE_OPEN_HOLD
	_set_seal_glow(true)   # 여는 빛 · 잠긴 동안 줄였던 반경을 돌린다 (#533)
	Vfx.play("seal_ripple", global_position + Vector3(0, 0.05, 0), {"scale": 1.6})
	Vfx.play("ink_ripple", global_position + Vector3(0, 0.05, -0.8), {"scale": 2.4})
	Vfx.play("portal_open", global_position + Vector3(0, 1.0, -1.2))
	Audio.play("stone_door_sink", global_position, "portal_open")   # 석문이 가라앉는 소리(#514) — 파일이 없으면 옛 대역(문 열림)
	Audio.play_gugak(&"seal_gate")   # 징 세 타 (#881, gugak_sfx_plan §3 B2)
	var cam := get_viewport().get_camera_3d()
	if cam and cam.has_method("kick"):
		cam.kick(0.15)
	_sink_doors(true)
	if DevMode.is_active:
		print("[SealGate] %s 열림 — 회차 %d · 댄 조각 %s" % [target_area, GameState.run, used])


## 석문 (마을 장식 — 무리 「seal_door」)을 땅으로 가라앉힌다 · animated = 여는 순간(먼지 · DOOR_SINK_SEC) / 아니면 곧바로(이미 연 문 — 마을에 들어올 때).
func _sink_doors(animated: bool) -> void:
	if not is_inside_tree():
		return
	for d in get_tree().get_nodes_in_group(&"seal_door"):
		var n := d as Node3D
		if n == null or not n.visible:
			continue
		var down := n.position + Vector3(0.0, -DOOR_SINK, 0.0)
		if animated:
			RENDER_INTERP.per_frame(n)   # 가라앉는 트윈은 그림 틱마다 — 물리 보간(#700)이 한 틱 늦게 덜컥 그리지 않게
			var tw := n.create_tween()
			tw.tween_property(n, "position", down, DOOR_SINK_SEC).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
			tw.tween_callback(n.hide)
			Vfx.play("dash_dust", n.global_position + Vector3(0.0, 0.2, 0.6), {"scale": 1.8})
		else:
			n.position = down
			n.hide()


## 이 문이 여는 지역 이름 (봉밀굴) — 모르면 「굴」.
func _gate_name() -> String:
	var d := AreaDb.get_def(target_area) if AreaDb.has(target_area) else null
	return d.display_name if d != null else "굴"


## 아직 안 연 봉인 조각 문에 닿음 — 조각이 다 모였으면 컷 네 줄 다음 여는 순간(#549), 모자라면 봉인 말 한 줄.
## 띠를 못 열면(대화 중 · 띠 없음) 컷 없이 바로 연다 — 문이 조각만 삼키고 안 열리는 일이 없게.
func _touch_seal_gate() -> void:
	if Quest.seals(GameState.flags) >= seal_pieces:
		if not _play_seal_cut():
			open_seal_gate()
	else:
		refresh_seal_gate()
		EventBus.ui_message.emit(sealed_message)


## 봉밀굴 문 컷 (#549, dialogue_v2.md §6.2) — 대본이 $> Seal.open_from_cut() 으로 이 문을 연다.
const SEAL_CUT := "res://data/dialogue/event/seal_gate.dialogue"
const SEAL_BEHIND := "seal_behind"
var _shaman_away: Node3D
var _shaman_home: Transform3D
var _shaman_vis_rot: Vector3


class SealHook extends RefCounted:
	var gate: Node

	func _init(p_gate: Node) -> void:
		gate = p_gate

	func open_from_cut() -> void:
		if is_instance_valid(gate) and gate.has_method("open_seal_gate"):
			gate.open_seal_gate()


## 컷을 연다. 할매는 줄이 있는 동안만 문 한 걸음 뒤. 열렸으면 true (못 열면 부르는 쪽이 바로 연다).
func _play_seal_cut() -> bool:
	var band := DialogueBand.find(get_tree())
	if band == null or band.is_open():
		return false
	_seat_shaman(true)
	if not band.start_once(SEAL_CUT, "", {"Cut": Cut.new(get_tree()), "Seal": SealHook.new(self)}, ["doho", "shaman"], _on_seal_cut_closed):
		_seat_shaman(false)
		return false
	return true


func _on_seal_cut_closed(_script_id: String, _cue: String) -> void:
	_seat_shaman(false)


## 할매를 문 뒤에 세운다 / 정자 자리·고개로 되돌린다. 마커가 없으면 문에서 마을 쪽으로 1.6.
func _seat_shaman(at_gate: bool) -> void:
	if at_gate:
		if _shaman_away != null:
			return
		var shaman := _shaman_node()
		if shaman == null:
			return
		var vis := shaman.get_node_or_null("Visual") as Node3D
		_shaman_home = shaman.global_transform
		_shaman_vis_rot = vis.rotation if vis != null else Vector3.ZERO
		_shaman_away = shaman
		shaman.global_position = _behind_spot()
		shaman.reset_physics_interpolation()   # 물리 보간(#700) — 정자 자리에서 문 뒤로 미끄러지지 않게
	elif _shaman_away != null and is_instance_valid(_shaman_away):
		var vis := _shaman_away.get_node_or_null("Visual") as Node3D
		_shaman_away.global_transform = _shaman_home
		if vis != null:
			vis.rotation = _shaman_vis_rot
		_shaman_away.reset_physics_interpolation()   # 제자리로 돌아올 때도 (#700)
		_shaman_away = null
	else:
		_shaman_away = null


func _shaman_node() -> Node3D:
	return NpcDef.actor_in(get_tree(), "shaman") as Node3D


func _behind_spot() -> Vector3:
	for n in get_tree().get_nodes_in_group("cut_marker"):
		if n is Node3D and n.name == SEAL_BEHIND:
			return (n as Node3D).global_position
	return global_position + Vector3(0.0, 0.0, 1.6)


# ---------- 첫 접근 혼잣말 (#547, D-097 ⑦ — CP-04 #0) ----------

## 혼잣말이 떠 있는 동안 = 시간만 센다(다 걷히면 미뤄 둔 문 글) · 이 판에 아직 안 했으면 = 도호가 반경 안에 든 첫 틱에 한 번.
func _tick_first_look(delta: float) -> void:
	if _look_left > 0.0:
		_look_left = maxf(0.0, _look_left - delta)
		if _look_left == 0.0 and _touch_waiting:
			_touch_waiting = false
			if not Quest.gate_open(GameState.flags, GameState.run):
				_touch_seal_gate()
		return
	if _looked:
		return
	var p := get_tree().get_first_node_in_group("player") as Node3D
	if p == null or Vector2(p.global_position.x - global_position.x, p.global_position.z - global_position.z).length() > FIRST_LOOK_RADIUS:
		return
	var story := DialogueStory.new(GameState.flags)
	if story.flag(FIRST_LOOK_KEY):
		_looked = true   # 이 판에 이미 했다 (다른 날 · 2회차)
		return
	if Bark.say(p, FIRST_LOOK_LINE, DOHO_HEIGHT) == null:
		return   # 도호가 아직 트리 밖 — 다음 틱에
	story.put(FIRST_LOOK_KEY)
	_looked = true
	_look_left = FIRST_LOOK_HOLD
	if DevMode.is_active:
		print("[SealGate] 첫 접근 혼잣말 — %s" % FIRST_LOOK_LINE)
