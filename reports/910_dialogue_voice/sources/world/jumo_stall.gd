@tool
extends Node3D
## JumoStall — 주모의 목로 (보드 #306 · D-094, design/npcs_v2.md §3.5). 저자 어귀 = 김 영감 좌판 앞(남쪽)·못 사이, 주모가 서는 자리의 북동에
## 평상(목로) + 술독 둘 — 아이소 화면에서 목로·술독이 주모 오른쪽에 그려져 몸과 겹치지 않는다. 주모의 자리 단계에 따라 바뀌는 것도 이 노드 하나가 쥔다:
##   here = 살림만 · out(그날 자리를 비움) = 「잠시 비움」 팻말 + 곁을 지나면 마을 사람 바크 한 줄 · gone(마을에서 빠짐) = 식은 술잔·여우털 한 올
##   + 쪽지 한 장(곁에 들면 글) + 곁을 지나면 도호 한마디 한 번(구미호 전 S12-2 · 뒤 S14-1, #541).
## 주모(Npc 몸)가 서 있을지는 NpcDef.here_on_visit — 같은 판·같은 걸음이면 몸과 목로가 따로 물어도 같은 답이다(둘을 잇는 신호·경로가 없다).
##
## 왜 TownDressing 자리표가 아니라 노드 하나인가: 목로는 주모의 상태를 따라 모양이 바뀐다 — 정적 장식표에 진행 상태를 넣으면 장식 전부가
## 플래그를 알게 된다. 대안 = Npc 가 목로를 자식으로 든다(몸이 자리를 비우면 목로·흔적도 같이 사라진다 — 기각).
## 살림은 걷는 땅 밖이라 길찾기를 막지 않는다(obstacle 아님 — town_v2 §2.1 규약). 팻말·술잔은 GLB(#557)가 있으면 그것, 없으면 코드 메시 자리표시 — 여우털은 늘 코드.
## @tool = 편집기에서도 살림(평상·술독)만 선다(TownDressing 처럼) — 진행 상태(GameState)는 게임에서만 읽는다.

const FLAT := preload("res://core/flat.gd")
const PLATFORM_GLB := "res://assets/models/props/wooden_platform.glb"
const JAR_GLB := "res://assets/models/props/onggi_jar.glb"
const SIGN_GLB := "res://assets/models/props/away_sign.glb"
const CUP_GLB := "res://assets/models/props/cold_cup.glb"
## 모델 상자 재기·크기 맞추기 (#855 — @tool이라 preload 별칭)
const ModelFit := preload("res://world/model_fit.gd")
## 평상(목로) 긴 쪽 길이 — 모델(1.33 × 0.40 × 0.85)을 이만큼으로(긴 쪽 = 동서 x). 뒤(북)의 좌판과 0.28, 동쪽 못가 젖은 둑과 0.3쯤 띈다.
const PLATFORM_LEN := 1.3
## 술독 [x, z, 배율] — 목로 동쪽(못 쪽, 이 노드 기준). 모델 키 0.72.
const JARS := [[0.95, 0.1, 0.85], [0.85, 0.75, 0.7]]
## 「잠시 비움」 팻말 자리 = 주모가 서는 자리(town.tscn Jumo (7.1, −1.4) — 이 노드 (7.6, −2.6) 기준). 앞면(+Z)을 45° 돌려 카메라(+x+z)를
## 보게 해야 아이소 화면에서 글이 읽힌다.
## 주모 몸(town.tscn Jumo)도 #275 「시작점을 본다」의 예외로 카메라(45°)를 본다 — D-094 — 얼굴·금빛 눈이 인물의 핵심(PD 2026-10-01 「추천대로」).
const SIGN_AT := Vector3(-0.5, 0.0, 1.2)
const SIGN_TEXT := "잠시\n비움"
## 팻말 GLB 키(말뚝 발 → 판 위). GLB 판은 키의 60~95%(≈ 0.33)로 낮고 어두워 두 줄 먹 글씨(≈ 0.37)가 판을 넘고 안 읽힌다(#557 창 모드 실측) —
## 그래서 판 앞(+Z 끝)에 한지 한 장을 꽂고 글씨는 그 위에 쓴다. 종이 윗변 = 키의 PAPER_TOP 몫(판 위쪽), 아래는 판 밑으로 조금 늘어진다.
const SIGN_H := 0.95
const PAPER_SIZE := Vector2(0.42, 0.44)
const PAPER_TOP := 0.93
const PAPER_TILT := -2.5
## 흔적 자리 (평상 윗면 위, 광장 쪽) — 식은 술잔 · 여우털 한 올. 사발 GLB 는 지름 CUP_D 로.
const CUP_AT := Vector2(-0.3, 0.15)
const CUP_D := 0.15
const HAIR_AT := Vector2(0.1, -0.05)
## 바크 — 도호가 목로에서 이만큼 안에 들면 한 번. 말하는 몸 = 그 두 배 안의 가장 가까운 NPC(마을 사람 §6이 오기 전엔 김 영감), 없으면 목로 위.
const BARK_RADIUS := 4.5
## 빈 목로 (D-096 · #541, quest_rework_dialogue_2026-10-01 §4 — S12 · S14). gone 흔적에 쪽지 한 장(S12-1 — 갚으러 오라는 초대) ·
## 곁(BARK_RADIUS)에 들면 도호 한마디 한 번: 구미호를 벤 뒤 = S14-1, 그 전 = S12-2 — 한 번씩(flags.story 키). 「벤 뒤」 = 주모 영구 퇴장 표시(keeper.gone_flag —
## 구미호 처치가 세운다, #540)로 가른다: 처치 표시 boss_killed_bongmil_gul 은 회차 칸이라 2회차 전환이 지우면 S12-2 「여우라도 다녀갔나」가 엔딩 뒤에 나온다(교차 검수 ④).
## 쪽지 글은 도호가 곁에 있을 때만 뜬다: 이 화면(아이소 세로 11유닛)에선 종이 크기 글자가 안 읽혀 바크 크기 글을 종이 위에 띄운다(멀어지면 진다).
const NOTE_TEXT := "외상 장부는 여기 두고 가우.\n갚을 날 오시구려."
const NOTE_AT := Vector2(0.35, 0.2)
const GONE_BARK := "여우라도 다녀갔나?"
const ENDING_BARK := "술은 마을에서 마시자 했는데, 따라 줄 사람이 없구먼."
const GONE_SEEN_KEY := "jumo_gone_seen"
const ENDING_KEY := "jumo_empty_ending"
## 도호 머리 높이 (바크 — core/quest_watch.gd 와 같은 값).
const DOHO_HEIGHT := 1.7

const STATE_HERE := "here"
const STATE_OUT := "out"
const STATE_GONE := "gone"

## 목로 주인 (data/npcs/jumo.tres). 비면 살림만 선다.
@export var keeper: NpcDef

## 이번 걸음의 목로 — here · out · gone (시험이 읽는다).
var state: String = STATE_HERE
## 평상 윗면 높이 — 흔적을 얹는다(평상 GLB 가 없으면 자리표시 높이).
var top_y: float = 0.45
var _bark_armed := false
## 빈 목로를 지켜본다(gone — 쪽지 글 · 도호 한마디). 한마디는 이번 걸음에 한 번만 물어본다(한 번만 = story 키).
var _gone_watch := false
var _gone_asked := false
var _story: Node3D


## 이번 걸음의 목로 상태 — 몸(Npc)과 같은 NpcDef 셈(here_on_visit · stage)을 쓴다. 순수 — 시험이 값만 넣어 부른다.
static func state_for(def: NpcDef, flags: Dictionary, run: int, run_seed: int, visits: int) -> String:
	if def == null or def.here_on_visit(flags, run, run_seed, visits):
		return STATE_HERE
	return STATE_GONE if def.stage(flags, run) == NpcDef.STAGE_GONE else STATE_OUT


func _ready() -> void:
	for c in get_children():
		c.free()
	_build_furniture()
	_story = Node3D.new()
	_story.name = "Story"
	add_child(_story)
	set_physics_process(false)
	if Engine.is_editor_hint() or keeper == null:
		return
	apply_state(state_for(keeper, GameState.flags, GameState.run, GameState.run_seed, GameState.town_visits))


## 상태에 맞춰 팻말·흔적을 세우고 바크를 건다 (here = 아무것도 없음). 다시 불러도 앞 것을 지우고 새로.
func apply_state(s: String) -> void:
	state = s
	for c in _story.get_children():
		c.free()
	match s:
		STATE_OUT:
			_story.add_child(_away_sign())
		STATE_GONE:
			_story.add_child(_traces())
	_bark_armed = s == STATE_OUT and keeper != null and keeper.away_bark != ""
	_gone_watch = s == STATE_GONE and not Engine.is_editor_hint()
	_gone_asked = false
	set_physics_process(_bark_armed or _gone_watch)


func _physics_process(_delta: float) -> void:
	if not _bark_armed and not _gone_watch:
		return
	var p := get_tree().get_first_node_in_group("player") as Node3D
	if p == null:
		return
	var d := FLAT.dist(p.global_position, global_position)
	var near := d <= BARK_RADIUS
	if _bark_armed and near:
		bark()
	if _gone_watch:
		show_note(near)
		if near and not _gone_asked:
			gone_bark(p)


## 쪽지 글을 띄운다/거둔다 (gone 흔적이 있을 때만). 돌려줌 = 지금 보이는가.
func show_note(on: bool) -> bool:
	var text := _story.get_node_or_null("Traces/Note/Text") as Label3D
	if text == null:
		return false
	text.visible = on
	return on


## 빈 목로 곁 도호 한마디 (S12-2 · S14-1 — 한 번씩). 이번 걸음엔 다시 안 묻는다. 돌려줌 = 라벨(할 말이 없으면 null).
func gone_bark(p: Node3D) -> Label3D:
	_gone_asked = true
	var line := gone_line(GameState.flags, keeper.gone_flag if keeper != null else "")
	return Bark.say(p, line, DOHO_HEIGHT) if line != "" else null


## 빈 목로에서 도호가 할 말 — 영구 퇴장 표시(gone_key = keeper.gone_flag, 구미호 처치)가 섰으면 S14-1(한 번) · 아니면 S12-2(한 번) · 이미 했으면 "".
## 한 번만 = story 키를 여기서 켠다. 엔딩 뒤엔 회차가 바뀌어도 S12-2 로 돌아가지 않는다. 순수에 가깝다(flags 만 받는다) — 시험이 값만 넣어 부른다.
static func gone_line(flags: Dictionary, gone_key: String) -> String:
	var story := DialogueStory.new(flags)
	if Quest.is_gone(flags, gone_key):
		return ENDING_BARK if story.first(ENDING_KEY) else ""
	return GONE_BARK if story.first(GONE_SEEN_KEY) else ""


## 마을 사람 바크 한 줄 (자리를 비운 날 한 번) — 말하는 몸 = 목로 곁 가장 가까운 NPC. 돌려줌 = 라벨(시험이 읽는다).
func bark() -> Label3D:
	_bark_armed = false
	set_physics_process(false)
	if keeper == null or keeper.away_bark == "":
		return null
	var who := speaker()
	if who == null:
		return Bark.say(self, keeper.away_bark, top_y + 0.8)
	var h: float = who.def.height if "def" in who and who.def != null else 1.5
	return Bark.say(who, keeper.away_bark, h)


## 바크를 말할 몸 — 목로에서 BARK_RADIUS × 2 안의 가장 가까운 NPC(주모 자신은 빼고). 없으면 null.
func speaker() -> Node3D:
	var best: Node3D = null
	var best_d := BARK_RADIUS * 2.0
	for n in get_tree().get_nodes_in_group("npc"):
		var npc := n as Node3D
		if npc == null or npc.is_queued_for_deletion() or ("def" in npc and npc.def == keeper):
			continue
		var d := npc.global_position.distance_to(global_position)
		if d < best_d:
			best_d = d
			best = npc
	return best


# ---------- 살림 ----------

func _build_furniture() -> void:
	var table := Node3D.new()
	table.name = "Moknro"
	add_child(table)
	var h := _place(PLATFORM_GLB, table, PLATFORM_LEN)
	if h > 0.0:
		top_y = h
	for j in JARS:
		var holder := Node3D.new()
		holder.name = "Jar%d" % (get_child_count())
		holder.position = Vector3(float(j[0]), 0.0, float(j[1]))
		holder.rotation_degrees.y = float(j[0]) * 97.0
		holder.scale = Vector3.ONE * float(j[2])
		add_child(holder)
		_place(JAR_GLB, holder, 0.0)


## GLB 하나를 holder 아래 세운다 — length > 0 이면 긴 가로를, height > 0 이면 키를 그 길이에 맞추고 발 = y 0 · 가운데 = 0. 돌려줌 = 선 높이(없으면 0).
func _place(path: String, holder: Node3D, length: float, height: float = 0.0) -> float:
	if not ResourceLoader.exists(path):
		return 0.0
	var ps := load(path) as PackedScene
	if ps == null:
		return 0.0
	var n := ps.instantiate() as Node3D
	holder.add_child(n)
	var box := _box(n)
	if box.size == Vector3.ZERO:
		return 0.0
	var s := ModelFit.fit_box(n, box, "w" if length > 0.0 else ("h" if height > 0.0 else ""), length if length > 0.0 else height)
	return box.size.y * s


## n 아래 메시 상자 (n 좌표 · 메시 자원 상자) — 부모 사슬을 직접 곱한다(트리 밖이어도 된다). 셈 = ModelFit(#855).
static func _box(n: Node3D) -> AABB:
	return ModelFit.mesh_aabb(n, true)


# ---------- 팻말·흔적 (GLB, 없으면 자리표시) ----------

## 「잠시 비움」 — 말뚝 하나에 판 하나, 판 앞면에 먹 글씨. GLB 는 키 SIGN_H 로 세우고 판 앞에 꽂은 한지(Paper)에 글씨, 없으면 Box 자리표시.
func _away_sign() -> Node3D:
	var holder := Node3D.new()
	holder.name = "AwaySign"
	holder.position = SIGN_AT
	holder.rotation_degrees.y = 45.0
	var text := Label3D.new()
	text.name = "Text"
	text.text = SIGN_TEXT
	text.font_size = 44
	text.pixel_size = 0.0045
	text.modulate = Color(0.07, 0.055, 0.045)
	text.outline_size = 0
	text.line_spacing = -6.0
	if _place(SIGN_GLB, holder, 0.0, SIGN_H) > 0.0:
		var box := _box(holder)
		var paper := MeshInstance3D.new()
		paper.name = "Paper"
		var q := QuadMesh.new()
		q.size = PAPER_SIZE
		paper.mesh = q
		paper.material_override = _mat(Color(0.80, 0.74, 0.60), 1.0)
		paper.position = Vector3(0.0, box.position.y + box.size.y * PAPER_TOP - PAPER_SIZE.y * 0.5, box.end.z + 0.004)
		paper.rotation_degrees.z = PAPER_TILT
		holder.add_child(paper)
		text.position = paper.position + Vector3(0.0, 0.0, 0.003)
		text.rotation_degrees.z = PAPER_TILT
	else:
		var wood := _mat(Color(0.46, 0.36, 0.24), 0.95)
		holder.add_child(_box_mesh("Post", Vector3(0.05, 0.62, 0.05), Vector3(0.0, 0.31, -0.03), wood))
		holder.add_child(_box_mesh("Board", Vector3(0.5, 0.46, 0.03), Vector3(0.0, 0.76, 0.0), _mat(Color(0.62, 0.50, 0.34), 0.9)))
		text.position = Vector3(0.0, 0.76, 0.017)
	holder.add_child(text)
	return holder


## 식은 술잔(사발 하나 — GLB 는 지름 CUP_D, 없으면 원기둥 자리표시) · 여우털 한 올(금빛 가는 털 한 가닥 — 아주 옅게 스스로 빛나 어둔 목로에서 눈에 걸린다).
func _traces() -> Node3D:
	var holder := Node3D.new()
	holder.name = "Traces"
	var cup := Node3D.new()
	if _place(CUP_GLB, cup, CUP_D) > 0.0:
		cup.position = Vector3(CUP_AT.x, top_y + 0.002, CUP_AT.y)
	else:
		cup.free()
		var mi := MeshInstance3D.new()
		var cm := CylinderMesh.new()
		cm.top_radius = 0.075
		cm.bottom_radius = 0.045
		cm.height = 0.07
		cm.radial_segments = 16
		mi.mesh = cm
		mi.material_override = _mat(Color(0.78, 0.76, 0.69), 0.55)
		mi.position = Vector3(CUP_AT.x, top_y + cm.height * 0.5, CUP_AT.y)
		cup = mi
	cup.name = "ColdCup"
	holder.add_child(cup)
	var hair := Node3D.new()
	hair.name = "FoxHair"
	hair.position = Vector3(HAIR_AT.x, top_y + 0.004, HAIR_AT.y)
	var fur := _mat(Color(0.93, 0.74, 0.42), 0.6)
	fur.emission_enabled = true
	fur.emission = Color(0.95, 0.70, 0.35)
	fur.emission_energy_multiplier = 0.6
	var at := Vector3.ZERO
	var yaw := 20.0
	for i in 3:
		var seg := _box_mesh("Strand%d" % i, Vector3(0.012, 0.004, 0.1), Vector3.ZERO, fur)
		var dir := Vector3(sin(deg_to_rad(yaw)), 0.0, cos(deg_to_rad(yaw)))
		seg.position = at + dir * 0.05
		seg.rotation_degrees.y = yaw
		hair.add_child(seg)
		at += dir * 0.1
		yaw += 28.0
	holder.add_child(hair)
	holder.add_child(_note())
	return holder


## S12-1 쪽지 한 장 (D-096 · #541) — 평상 위 접힌 종이(자리표시 판) + 글(Label3D, 처음엔 숨김 — show_note 가 도호가 곁에 있을 때만 띄운다).
## 글은 바크와 같은 크기·같은 결(빌보드 · 먹빛 테두리)이라 이 화면에서 읽힌다. 종이는 카메라 쪽으로 45° 돌려 놓는다.
func _note() -> Node3D:
	var note := Node3D.new()
	note.name = "Note"
	note.position = Vector3(NOTE_AT.x, top_y, NOTE_AT.y)
	note.rotation_degrees.y = 45.0
	note.add_child(_box_mesh("Paper", Vector3(0.24, 0.006, 0.17), Vector3(0.0, 0.003, 0.0), _mat(Color(0.86, 0.82, 0.70), 0.95)))
	var text := Label3D.new()
	text.name = "Text"
	text.text = NOTE_TEXT
	text.font_size = Bark.FONT
	text.pixel_size = Bark.PIXEL
	text.outline_size = Bark.OUTLINE
	text.modulate = Bark.COLOR
	text.outline_modulate = Bark.OUTLINE_COLOR
	text.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	text.no_depth_test = true
	text.render_priority = 6
	text.outline_render_priority = 5
	text.position = Vector3(0.0, 0.55, 0.0)
	text.visible = false
	note.add_child(text)
	return note


func _box_mesh(n: String, size: Vector3, pos: Vector3, mat: Material) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = n
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	return mi


func _mat(c: Color, rough: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = rough
	return m
