class_name Level
extends Node3D
## Level — 마을·던전 층의 공통 베이스. 셸(Main)이 아는 계약은 이것뿐:
##   get_spawn(hint) → 스폰 위치, find_path(from, to) → 웨이포인트, display_name.
## 길찾기 = AStarGrid2D(셀 1유닛). 기본 구현은 `Floor`(grid_floor) 크기로 격자를 만들고
## 그룹 "obstacle" 노드들의 메시 AABB(플레이어 반경만큼 팽창)를 막는다. 던전은 맵 셀로 override.
## 왜 베이스에 두나: 플레이어는 "지금 레벨에게 길을 묻는다"만 알면 되고, 마을·던전이 같은 계약을 지킨다.

## 스폰 힌트. FROM_ABOVE = 위층/마을에서 내려옴(올라가는 계단 옆) / FROM_BELOW = 아래층에서 올라옴(내려가는 계단 옆) /
## FROM_ENTRY = 걸어서 넘어옴(AreaExit) — `spawn_entry` 이름의 입구(`Entry_<이름>` 마커) 옆 (field_v2.md §6).
enum SpawnHint { DEFAULT, FROM_ABOVE, FROM_BELOW, FROM_PORTAL, FROM_WAYPOINT, FROM_ENTRY }

const OBSTACLE_PAD := 0.35  # 플레이어 캡슐 반경
const FLOOR_ITEM_SCENE := preload("res://world/floor_item.tscn")
const PORTAL_SCENE := preload("res://world/portal.tscn")
## 손으로 떨군 물건(item_dropped)의 짧은 낙하 (§4.1): 제자리 0.5 위에서, 정점 +0.35, 0.28초.
const HOP_FROM := 0.5
const HOP_APEX := 0.35
const HOP_SEC := 0.28
## 벽 칸 보정이 몰릴 때 최소 간격 — §4.1 규약 0.3보다 여유를 둬 부동소수 오차에도 항상 넘는다(#176).
const WALL_PILE_GAP := 0.35

@export var display_name: String = "레벨"
## 오디오 (design/audio.md §2): 층 진입 때 Audio가 level_loaded로 읽는다. 기본값 = 마을. 던전은 _ready에서 덮는다.
@export var music_id: String = "town"
@export var ambient_id: String = "amb_town"
@export var footstep_cue: String = "step_dirt"
## #94: 영속 플레이어 광원을 층 교체 때 복원한다. 기본값은 현행 던전 조명 그대로.
@export var player_light_energy: float = 2.2
@export var player_light_range: float = 9.0

## FROM_ENTRY로 들어올 때 설 입구 이름 — 셸이 세우기 전에 채운다.
var spawn_entry: StringName = &""

## 캐릭터 전용 조명 (보드 #191, docs/design/dungeon.md §6.7, 디아2R §4.2): 배우(렌더 레이어 ActorVisual.CHAR_LIGHT_LAYER)만 비추는
## 방향광 2개. 배경은 그 비트가 없어 밝기가 그대로다. 방향 = IsoCamera와 같은 각 규약, 빛이 **오는** 쪽(yaw 45 = 카메라 자리).
## 기본값 = 던전. 레벨 씬이 덮어쓴다(마을 = 해가 이미 인물을 비추니 키를 낮게). 세기 0이면 그 빛을 끈다.
@export_group("캐릭터 조명")
## 따뜻한 키광 색 (디아2R (1.00, 0.94, 0.88)).
@export var char_key_color: Color = Color(1.0, 0.94, 0.88)
## 키광 세기 — D-070 다크 판타지에 맞게 낮게 시작(던전 0.35 ≈ 횃불 4칸 거리의 빛). 과하면 이것만 내린다.
@export_range(0.0, 2.0, 0.01) var char_key_energy: float = 0.35
## 키광이 오는 쪽: 5 = 카메라(45)에서 화면 왼쪽으로 40°. 높이 40° = 카메라(35°)보다 조금 위.
@export var char_key_yaw_deg: float = 5.0
@export_range(5.0, 85.0, 1.0) var char_key_elevation_deg: float = 40.0
## 차가운 보조광 색 (디아2R (0.90, 0.92, 1.00)).
@export var char_fill_color: Color = Color(0.90, 0.92, 1.0)
## 키 : 보조 세기 비 (디아2R 30 : 4 ≈ 7.5). 보조 세기 = 키 ÷ 이 값.
@export_range(1.0, 30.0, 0.1) var char_light_ratio: float = 7.5
## 보조광이 오는 쪽: 키의 반대편(뒤·오른쪽), 낮게 — 윤곽 가장자리에만 닿는다.
@export var char_fill_yaw_deg: float = 185.0
@export_range(5.0, 85.0, 1.0) var char_fill_elevation_deg: float = 25.0

var _astar := AStarGrid2D.new()
var _nav_ready: bool = false
## #535 큰 몸만 별도 격자. 길 점 0.35 도착 여유 동안 선회해도 캡슐이 장애물에 닿지 않게 한다.
const BODY_PATH_TURN_PAD := 0.35
var _body_nav: Dictionary[float, AStarGrid2D] = {}
var _items: Node3D
## 전리품 부채꼴 (§4.1): 같은 자리·같은 프레임에 나온 것끼리 한 무리.
var _burst_key := Vector3i(1 << 20, 0, 0)
var _burst_frame: int = -1
var _burst_n: int = 0
var _burst_base: float = 0.0
## 이번 무리가 잡아 둔 착지 자리 — 날아가는 중엔 현재 위치로 겹침을 못 보므로 계획을 들고 있는다.
var _burst_spots: Array[Vector3] = []
## 벽에 막혀 같은 걷는 셀로 스냅된 것이 몇 번째인지(#176) — 층이 사는 동안 유지(리셋 안 함).
## 다른 무리(다른 시체)가 나중에 같은 궁지 칸을 또 쓰더라도 이미 놓인 것과 겹치지 않는다.
var _wall_cell_pile: Dictionary = {}  # Vector2i(cell) -> 다음에 쓸 순번


func _ready() -> void:
	add_to_group("level")
	_items = Node3D.new()
	_items.name = "Items"
	add_child(_items)
	EventBus.item_dropped.connect(_on_item_dropped)
	EventBus.loot_dropped.connect(_on_loot_dropped)
	_setup_char_lights()
	_setup_nav()


# ---------- 캐릭터 전용 조명 (보드 #191, dungeon.md §6.7) ----------
## 반사광 = Godot 기본값 0.5 — 횃불·플레이어 빛과 같은 반사 규칙. 1차에 무광 톤(D-070)을 노려 0.25로 낮췄더니, metallic 1.0으로 들어온
## Meshy 인물 5종(난반사 0, #119 ①)은 반사가 유일한 반응이라 캐릭터 빛이 거의 안 보였다(창 모드 실측 +2~5/255, dungeon.md §6.7). 무광은 재질의 거칠기가 맡는다.
const CHAR_LIGHT_SPECULAR := 0.5


## 키·보조 방향광을 만든다. cull mask = 캐릭터 비트뿐 · 그림자 끔(배경에 그림자를 떨어뜨리지 않는다) · 굽기·안개·하늘 영향 없음.
## 왜 레벨이 갖나: 빛의 세기·방향은 장소의 분위기(마을엔 해가 있다)라 레벨 씬이 덮어쓰고, 배우는 "나는 캐릭터다" 비트만 안다.
## 대안 = 배우마다 따라다니는 빛 → 배우 수만큼 빛이 늘고 서로의 빛이 겹쳐 밝기가 무리마다 달라진다 → 기각(디아2R도 레벨 설정 한 벌).
func _setup_char_lights() -> void:
	_add_char_light("CharKeyLight", char_key_color, char_key_energy, char_key_yaw_deg, char_key_elevation_deg)
	_add_char_light("CharFillLight", char_fill_color, char_key_energy / maxf(char_light_ratio, 1.0), char_fill_yaw_deg, char_fill_elevation_deg)


func _add_char_light(node_name: String, color: Color, energy: float, yaw_deg: float, elevation_deg: float) -> DirectionalLight3D:
	var l := DirectionalLight3D.new()
	l.name = node_name
	l.light_color = color
	l.light_energy = energy
	l.light_specular = CHAR_LIGHT_SPECULAR
	l.light_cull_mask = ActorVisual.CHAR_LIGHT_LAYER
	l.shadow_enabled = false
	l.light_bake_mode = Light3D.BAKE_DISABLED
	l.light_volumetric_fog_energy = 0.0
	l.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
	# 방향광은 -Z로 비춘다 → 카메라와 같은 각(x = -높이, y = yaw)이면 +Z(빛이 오는 쪽)가 그 yaw·높이를 가리킨다
	l.rotation_degrees = Vector3(-elevation_deg, yaw_deg, 0.0)
	l.visible = energy > 0.0
	add_child(l)
	return l


## 드랍 → 바닥 아이템. 레벨이 소유하므로 층을 떠나면 함께 사라진다(디아1). 목표 셀이 벽이면 가장 가까운 걷는 셀로.
## item_dropped = "여기 떨궈라"(가방에서 버림·보상·테스트) → 제자리 위에서 짧게 떨어진다(§4.1 — 손으로 버린 것도 바닥에 닿는 소리가 난다).
func _on_item_dropped(item: RefCounted, world_pos: Vector3) -> void:
	if is_queued_for_deletion() or not is_inside_tree():
		return
	var pos := _landing_cell(Vector3(world_pos.x, 0.0, world_pos.z))
	if pos.y < -0.5:
		return
	var fi := _spawn_floor_item(item, pos)
	fi.launch(pos + Vector3(0, HOP_FROM, 0), pos, HOP_APEX, HOP_SEC)


## 전리품이 **튀어나온다** (game_feel_v2 §4.1, 보드 #105). origin = 시체 가슴.
## 같은 자리·같은 프레임에 여럿이 나오면 **황금각(137.5°)으로 부채꼴**을 나눈다 — 개수를 미리 몰라도 고르게 퍼진다
## (사양의 "360°/n"과 같은 목표, n을 모르는 신호 구조에 맞춘 방법).
func _on_loot_dropped(item: RefCounted, origin: Vector3) -> void:
	if is_queued_for_deletion() or not is_inside_tree():
		return
	var key := Vector3i(roundi(origin.x * 4.0), 0, roundi(origin.z * 4.0))
	var frame := Engine.get_process_frames()
	if key != _burst_key or frame != _burst_frame:
		_burst_key = key
		_burst_frame = frame
		_burst_n = 0
		_burst_base = randf() * TAU
		_burst_spots.clear()
	var prof: Dictionary = FloorItem.launch_profile(item as ItemInstance)
	var ang := _burst_base + float(_burst_n) * deg_to_rad(137.508) + deg_to_rad(randf_range(-12.0, 12.0))
	_burst_n += 1
	var dist := randf_range(float(prof.dist_min), float(prof.dist_max))
	var ground := Vector3(origin.x, 0.0, origin.z)
	var dir := Vector3(sin(ang), 0.0, cos(ang))
	# 이미 떨어져 있는 물건 위로 겹치면 그 방향으로 조금 더 밀어낸다 — 좁은 방에서는 셀 스냅이 여럿을 한 점에 모은다(실측)
	var to := ground
	for tries in 6:
		# 다시 고를 땐 각도도 함께 튼다 — 좁은 방에서 같은 방향으로만 밀면 계속 같은 벽·같은 셀로 스냅된다(실측 0.28유닛)
		var d2 := dir.rotated(Vector3.UP, deg_to_rad(37.0 * float(tries)))
		to = _landing_cell(ground + d2 * (dist + 0.26 * float(tries)))
		if to.y < -0.5:
			continue
		if not _item_near(to, 0.36):
			break
	if to.y < -0.5:
		to = _landing_cell(ground)
		if to.y < -0.5:
			return
	_burst_spots.append(to)
	var fi := _spawn_floor_item(item, ground)
	fi.launch(origin, to, float(prof.apex), float(prof.sec))


## 착지 자리: 걷는 셀이면 그대로, 아니면 가장 가까운 걷는 셀 **중심에서 순번대로 흩어서**.
## 중심 그대로 쓰면 벽에 막힌 여러 개가 정확히 같은 점에 쌓인다(실측). 못 찾으면 y = -1 (호출자가 버린다).
## #176: 예전엔 여기서 매번 독립된 무작위 지터(±0.3)를 뽑았다 — 궁지(걷는 칸이 하나뿐인 자리)에서 둘이 같은 셀로
## 스냅되면 두 무작위 지터가 우연히 가까이 찍힐 수 있었다(실측 0.06유닛, 바깥 재시도 6번도 못 피함).
## 지금은 "이 칸에 몇 번째로 몰렸나"(_wall_cell_pile)를 세어 해바라기씨 나선(황금각 137.508° + 반지름 0.35·√순번)으로
## 편다 — 이 배치는 순번이 몇이든 이웃 간 최소 거리가 항상 WALL_PILE_GAP(0.35 > 사양 0.3)이 되는 성질이 있어(실측 스크립트로 n=50까지 확인)
## 무작위 없이 결정적으로 간격을 보장한다.
func _landing_cell(pos: Vector3) -> Vector3:
	if _nav_ready and not is_cell_walkable(world_to_cell(pos)):
		var nw := nearest_walkable(world_to_cell(pos), 4)
		if not nw[0]:
			return Vector3(0, -1, 0)
		var cell: Vector2i = nw[1]
		var k: int = _wall_cell_pile.get(cell, 0)
		_wall_cell_pile[cell] = k + 1
		if k == 0:
			return cell_to_world(cell)
		var ang := deg_to_rad(137.508) * float(k)
		var r := WALL_PILE_GAP * sqrt(float(k))
		return cell_to_world(cell) + Vector3(cos(ang), 0.0, sin(ang)) * r
	return pos


## 그 자리 근처(XZ)에 이미 바닥 아이템이 있나 — **이번 무리가 찍어 둔 착지 자리**도 같이 본다.
## (같은 프레임에 나온 것들은 아직 전부 시체 위에 있어서 현재 위치로는 겹침을 알 수 없다 — 실측)
func _item_near(pos: Vector3, r: float) -> bool:
	for spot in _burst_spots:
		if Vector2(spot.x - pos.x, spot.z - pos.z).length() < r:
			return true
	if _items == null:
		return false
	for n in _items.get_children():
		var fi := n as Node3D
		if fi == null:
			continue
		if Vector2(fi.global_position.x - pos.x, fi.global_position.z - pos.z).length() < r:
			return true
	return false


func _spawn_floor_item(item: RefCounted, pos: Vector3) -> FloorItem:
	var fi := FLOOR_ITEM_SCENE.instantiate() as FloorItem
	fi.item = item as ItemInstance
	_items.add_child(fi)
	fi.global_position = pos
	if DevMode.is_active:
		var cam := get_viewport().get_camera_3d()
		print("[Dev] item %s world=%s screen=%s" % [(item as ItemInstance).display_name(), pos, cam.unproject_position(pos + Vector3(0, 0.3, 0)) if cam else Vector2.ZERO])
	return fi


## 기본: Floor 크기·선택 원점/보행 마스크 + obstacle 그룹 AABB. 던전은 override.
func _setup_nav() -> void:
	var floor_node := get_node_or_null("Floor")
	if floor_node == null or not ("size_x" in floor_node):
		return
	var sx: int = floor_node.size_x
	var sz: int = floor_node.size_z
	var origin := Vector2i(int(-sx * 0.5), int(-sz * 0.5))
	if "nav_origin" in floor_node:
		origin = floor_node.nav_origin
	var bounds := Rect2i(origin, Vector2i(sx, sz))
	nav_init(bounds)
	if floor_node.has_method("is_nav_walkable"):
		for z in range(bounds.position.y, bounds.end.y):
			for x in range(bounds.position.x, bounds.end.x):
				var cell := Vector2i(x, z)
				nav_set_solid(cell, not floor_node.is_nav_walkable(cell))
	for node in get_tree().get_nodes_in_group("obstacle"):
		if not is_ancestor_of(node):
			continue
		for mi in node.find_children("*", "MeshInstance3D", true, false):
			var aabb: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
			_mark_aabb_solid(aabb.grow(OBSTACLE_PAD))
	_nav_ready = true


func nav_init(rect: Rect2i) -> void:
	_body_nav.clear()
	_astar.region = rect
	_astar.cell_size = Vector2(1, 1)
	_astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	_astar.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	_astar.default_estimate_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	_astar.update()
	_nav_ready = false


## 서브클래스가 격자를 다 채운 뒤 호출 — 이때부터 find_path가 A*를 쓴다.
func nav_finish() -> void:
	_body_nav.clear()
	_nav_ready = true


func nav_set_solid(c: Vector2i, solid: bool) -> void:
	if _astar.region.has_point(c):
		_astar.set_point_solid(c, solid)
		_body_nav.clear()


## 셀 중심이 (팽창한) AABB 안에 있을 때만 막는다. 양끝을 floor로 넓히면 서낭단 같은 작은 물체가 4×4칸을 먹어 상호작용 사거리 밖으로 밀려남(실측).
func _mark_aabb_solid(aabb: AABB) -> void:
	var x0 := int(floor(aabb.position.x))
	var x1 := int(floor(aabb.end.x))
	var z0 := int(floor(aabb.position.z))
	var z1 := int(floor(aabb.end.z))
	for z in range(z0, z1 + 1):
		for x in range(x0, x1 + 1):
			var cx := x + 0.5
			var cz := z + 0.5
			if cx >= aabb.position.x and cx <= aabb.end.x and cz >= aabb.position.z and cz <= aabb.end.z:
				nav_set_solid(Vector2i(x, z), true)


## 자동 지도 등 읽기 전용 소비자는 생성기 크기 대신 최종 내비 범위를 쓴다. 미완성 격자는 노출하지 않는다.
func navigation_bounds() -> Rect2i:
	return _astar.region if _nav_ready else Rect2i()


func is_cell_walkable(c: Vector2i) -> bool:
	return _astar.region.has_point(c) and not _astar.is_point_solid(c)


static func world_to_cell(v: Vector3) -> Vector2i:
	return Vector2i(int(floor(v.x)), int(floor(v.z)))


static func cell_to_world(c: Vector2i) -> Vector3:
	return Vector3(c.x + 0.5, 0.0, c.y + 0.5)


## 목표가 막힌 셀이면 가장 가까운 걷는 셀 (반경 확장 탐색). 없으면 (-1,-1)... 단 음수 좌표가 유효하므로 found 플래그를 씀.
func nearest_walkable(p: Vector2i, max_radius: int = 10) -> Array:  # [found: bool, cell: Vector2i]
	if is_cell_walkable(p):
		return [true, p]
	for r in range(1, max_radius + 1):
		var best := Vector2i.ZERO
		var best_d := 1e9
		var found := false
		for dy in range(-r, r + 1):
			for dx in range(-r, r + 1):
				if absi(dx) != r and absi(dy) != r:
					continue
				var q := p + Vector2i(dx, dy)
				if is_cell_walkable(q):
					var d := float(dx * dx + dy * dy)
					if d < best_d:
						best_d = d
						best = q
						found = true
		if found:
			return [true, best]
	return [false, p]


## 귀환문 생성 (Main이 GameState.portal에 맞춰 부른다).
## 이 자리가 걷는 칸이면 그대로, 막혔으면 가장 가까운 걷는 칸 중심 (넓게 찾는다). 못 찾으면 그대로.
## 옛 세이브의 귀환문처럼 배치가 바뀐 뒤에 남은 좌표를 바닥에 내려놓는 데 쓴다(#165).
func walkable_point(pos: Vector3, radius: int = 64) -> Vector3:
	var nw := nearest_walkable(world_to_cell(pos), radius)
	if not nw[0] or nw[1] == world_to_cell(pos):
		return pos
	return cell_to_world(nw[1])


func spawn_portal(pos: Vector3) -> void:
	var p := PORTAL_SCENE.instantiate()
	_items.add_child(p)
	p.global_position = Vector3(pos.x, 0.0, pos.z)
	Audio.play("portal_open", p.global_position)
	Vfx.play("portal_open", p.global_position + Vector3(0, 0.6, 0))
	if DevMode.is_active:
		var cam := get_viewport().get_camera_3d()
		if cam:
			print("[Dev] interact Portal world=%s screen=%s" % [p.global_position, cam.unproject_position(p.global_position + Vector3(0, 0.9, 0))])


## 마을 서낭단 위치 (없으면 null).
func waypoint_position() -> Variant:
	for n in get_tree().get_nodes_in_group("interactable"):
		if is_ancestor_of(n) and "area_id" in n and n.has_method("is_active"):
			return n.global_position
	return null


## 힌트별 마커: FROM_BELOW → `SpawnFromBelow`, FROM_PORTAL → `PortalSpot`, FROM_WAYPOINT → 서낭단 옆,
## FROM_ENTRY → `Entry_<spawn_entry>`, 그 외 `PlayerSpawn`.
func get_spawn(hint: SpawnHint = SpawnHint.DEFAULT) -> Vector3:
	if hint == SpawnHint.FROM_ENTRY and spawn_entry != &"":
		var e := get_node_or_null("Entry_%s" % spawn_entry) as Marker3D
		if e:
			return e.global_position
	if hint == SpawnHint.FROM_BELOW:
		var b := get_node_or_null("SpawnFromBelow") as Marker3D
		if b:
			return b.global_position
	if hint == SpawnHint.FROM_PORTAL:
		var ps := get_node_or_null("PortalSpot") as Marker3D
		if ps:
			return ps.global_position + Vector3(1.3, 0, 0)
	if hint == SpawnHint.FROM_WAYPOINT:
		var wp: Variant = waypoint_position()
		if wp != null:
			return (wp as Vector3) + Vector3(1.6, 0, 0.6)
	var m := get_node_or_null("PlayerSpawn") as Marker3D
	return m.global_position if m else Vector3.ZERO


## 웨이포인트 목록. 비어 있으면 갈 수 없음(호출자는 무시). 격자가 없으면 직선.
func find_path(from: Vector3, to: Vector3, body_radius: float = 0.0) -> PackedVector3Array:
	if not _nav_ready:
		return PackedVector3Array([Vector3(to.x, 0.0, to.z)])
	if body_radius > 0.5:
		return _large_body_path(from, to, body_radius)
	var a := nearest_walkable(world_to_cell(from))
	var b := nearest_walkable(world_to_cell(to))
	if not a[0] or not b[0]:
		return PackedVector3Array()
	var out := PackedVector3Array()
	var target_cell_ok := is_cell_walkable(world_to_cell(to))
	var target_position := Vector3(to.x, 0.0, to.z)
	var floor_node := get_node_or_null("Floor")
	if target_cell_ok and floor_node != null and floor_node.has_method("nav_target_position"):
		# 못골 경계의 임의 클릭만 캡슐 여유가 있는 지점으로 보정한다. 기존 Floor/던전은 그대로.
		target_position = floor_node.nav_target_position(target_position)
	if a[1] == b[1]:
		out.append(target_position if target_cell_ok else cell_to_world(b[1]))
		return out
	var ids := _astar.get_id_path(a[1], b[1])
	# 첫 셀(현재 위치)은 건너뛰고, 마지막은 클릭 지점 그대로(셀 중심이 아니라)로 마무리
	for i in range(1, ids.size()):
		out.append(cell_to_world(ids[i]))
	if out.size() > 0 and target_cell_ok:
		out[out.size() - 1] = target_position
	return out


## 큰 몸의 경로만 셀 상자와 실제 캡슐 여유를 함께 본다. 작은 몸/플레이어의 원본 A*는 그대로.
func _large_body_path(from: Vector3, to: Vector3, body_radius: float) -> PackedVector3Array:
	var grid := _body_grid(body_radius)
	var a := _nearest_body_cell(from, grid, body_radius, true)
	var b := _nearest_body_cell(to, grid, body_radius, false)
	var out := PackedVector3Array()
	if not a[0] or not b[0]:
		return out
	var ids := grid.get_id_path(a[1], b[1])
	if ids.is_empty():
		return out
	var next_point := cell_to_world(ids[1] if ids.size() > 1 else ids[0])
	# 막힌 큰몸 셀에서 빠져나가는 첫 점, 또는 현재 위치에서 다음 점으로 곧장 갈 수 없는 첫 점을 보존한다.
	if a[1] != world_to_cell(from) or not _body_segment_clear(from, next_point, body_radius):
		out.append(cell_to_world(a[1]))
	for i in range(1, ids.size()):
		out.append(cell_to_world(ids[i]))
	var end := Vector3(to.x, 0.0, to.z)
	var last := out[out.size() - 1] if not out.is_empty() else Vector3(from.x, 0.0, from.z)
	if _body_segment_clear(last, end, body_radius):
		if out.is_empty() or last.distance_squared_to(end) > 0.000001:
			out.append(end)
	elif out.is_empty():
		out.append(cell_to_world(b[1]))
	return out


func _body_grid(body_radius: float) -> AStarGrid2D:
	var key := ceilf(body_radius * 100.0) / 100.0
	if _body_nav.has(key):
		return _body_nav[key]
	var grid := AStarGrid2D.new()
	grid.region = _astar.region
	grid.cell_size = _astar.cell_size
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	grid.default_compute_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
	grid.default_estimate_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
	grid.update()
	for z in range(grid.region.position.y, grid.region.end.y):
		for x in range(grid.region.position.x, grid.region.end.x):
			var cell := Vector2i(x, z)
			var center := cell_to_world(cell)
			grid.set_point_solid(cell, not _body_segment_clear(center, center, key + BODY_PATH_TURN_PAD))
	_body_nav[key] = grid
	return grid


func _nearest_body_cell(pos: Vector3, grid: AStarGrid2D, radius: float, approach: bool) -> Array:
	var origin := world_to_cell(pos)
	for ring in range(0, 11):
		var best := origin
		var best_d := INF
		var found := false
		for dz in range(-ring, ring + 1):
			for dx in range(-ring, ring + 1):
				if absi(dx) != ring and absi(dz) != ring:
					continue
				var cell := origin + Vector2i(dx, dz)
				if not grid.region.has_point(cell) or grid.is_point_solid(cell):
					continue
				var center := cell_to_world(cell)
				if approach and not _body_segment_clear(pos, center, radius):
					continue
				var d := Vector2(center.x - pos.x, center.z - pos.z).length_squared()
				if d < best_d:
					best_d = d
					best = cell
					found = true
		if found:
			return [true, best]
	return [false, origin]


## 이동 구간 전체와 1×1 셀 상자의 최단 거리. 원의 모서리 여유도 보므로 가는 LOS로 대신하지 않는다.
func _body_segment_clear(from: Vector3, to: Vector3, radius: float) -> bool:
	var a := Vector2(from.x, from.z)
	var b := Vector2(to.x, to.z)
	var r2 := radius * radius
	var x0 := int(floor(minf(a.x, b.x) - radius))
	var x1 := int(floor(maxf(a.x, b.x) + radius))
	var z0 := int(floor(minf(a.y, b.y) - radius))
	var z1 := int(floor(maxf(a.y, b.y) + radius))
	for z in range(z0, z1 + 1):
		for x in range(x0, x1 + 1):
			if not is_cell_walkable(Vector2i(x, z)):
				var rect := Rect2(float(x), float(z), 1.0, 1.0)
				if _segment_rect_distance_squared(a, b, rect) + 0.000001 < r2:
					return false
	return true


static func _segment_rect_distance_squared(a: Vector2, b: Vector2, rect: Rect2) -> float:
	var near_a := Vector2(clampf(a.x, rect.position.x, rect.end.x), clampf(a.y, rect.position.y, rect.end.y))
	var near_b := Vector2(clampf(b.x, rect.position.x, rect.end.x), clampf(b.y, rect.position.y, rect.end.y))
	var distance := minf(a.distance_squared_to(near_a), b.distance_squared_to(near_b))
	if distance <= 0.0 or a.is_equal_approx(b):
		return distance
	var corners := PackedVector2Array([rect.position, Vector2(rect.end.x, rect.position.y), rect.end, Vector2(rect.position.x, rect.end.y)])
	for i in 4:
		if Geometry2D.segment_intersects_segment(a, b, corners[i], corners[(i + 1) % 4]) != null:
			return 0.0
		distance = minf(distance, corners[i].distance_squared_to(Geometry2D.get_closest_point_to_segment(corners[i], a, b)))
	return distance
