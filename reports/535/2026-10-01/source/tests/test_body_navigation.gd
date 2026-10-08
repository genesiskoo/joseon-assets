extends SceneTree
## #535 큰 몸 경로 회귀. 헤드리스: godot --headless -s tests/test_body_navigation.gd
## 실제 Level 공개 nav/find_path 계약을 합성 1×1 막는 셀로 검사한다.
## 안전 검산은 Level의 거리/격자 도우미를 부르지 않고, 경로 전체를 0.025u 이하 간격으로
## 표본화해 셀 상자까지 최근점을 직접 잰다(큰 몸 .9 + 선회 여유 .35의 경로와 별개 계산).
## 이 시험은 길찾기이고 실제 충돌·먹기·회복은 e2e bulgasari_path가 검사한다.

const RADIUS := 0.9
const SAMPLE_STEP := 0.025
const EPS := 0.001

var _level_script: Script
var _n := 0
var _fails: Array[String] = []


func _check(cond: bool, msg: String) -> void:
	_n += 1
	if not cond:
		push_error("FAIL: " + msg)
		_fails.append(msg)


func _init() -> void:
	# Level이 끌어오는 씬의 오토로드 이름은 첫 프레임 뒤 로드한다.
	await process_frame
	_level_script = load("res://world/level.gd") as Script
	_straight_and_small()
	_brazier_and_corners()
	_corridors()
	_start_and_end()
	_cache_changes()
	print("BODY_NAVIGATION_TEST checks=%d fails=%d %s" % [_n, _fails.size(), "PASS" if _fails.is_empty() else "FAIL"])
	quit(1 if not _fails.is_empty() else 0)


func _center(cell: Vector2i) -> Vector3:
	return Vector3(cell.x + 0.5, 0.0, cell.y + 0.5)


func _world_cell(p: Vector3) -> Vector2i:
	return Vector2i(floori(p.x), floori(p.z))


func _outline(size: Vector2i) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for z in size.y:
		for x in size.x:
			if x == 0 or z == 0 or x == size.x - 1 or z == size.y - 1:
				out.append(Vector2i(x, z))
	return out


func _carve(size: Vector2i, floors: Array[Rect2i]) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for z in size.y:
		for x in size.x:
			var cell := Vector2i(x, z)
			var walk := false
			for rect in floors:
				walk = walk or rect.has_point(cell)
			if not walk:
				out.append(cell)
	return out


func _level(size: Vector2i, solids: Array[Vector2i]) -> Node3D:
	var lvl: Node3D = _level_script.new()
	lvl.call("nav_init", Rect2i(Vector2i.ZERO, size))
	for cell in solids:
		lvl.call("nav_set_solid", cell, true)
	lvl.call("nav_finish")
	return lvl


func _path(lvl: Node3D, from: Vector3, to: Vector3, radius: float = RADIUS) -> PackedVector3Array:
	return lvl.call("find_path", from, to, radius)


## 독립 계산: 점마다 막는 1×1 상자에 가장 가까운 좌표로 clamp한 실제 거리.
func _point_clearance(p: Vector3, solids: Array[Vector2i]) -> float:
	var distance := INF
	for cell in solids:
		var near := Vector2(clampf(p.x, float(cell.x), float(cell.x + 1)), clampf(p.z, float(cell.y), float(cell.y + 1)))
		distance = minf(distance, Vector2(p.x, p.z).distance_to(near))
	return distance


## 출발 실좌표→첫 보정점과 마지막 실좌표까지 포함한다. 빈 경로는 안전한 경로가 아니다.
func _sweep_clearance(from: Vector3, path: PackedVector3Array, solids: Array[Vector2i]) -> float:
	if path.is_empty():
		return -INF
	var distance := _point_clearance(from, solids)
	var a := from
	for b in path:
		var steps := maxi(1, ceili(a.distance_to(b) / SAMPLE_STEP))
		for i in range(steps + 1):
			distance = minf(distance, _point_clearance(a.lerp(b, float(i) / float(steps)), solids))
		a = b
	return distance


func _safe(from: Vector3, path: PackedVector3Array, solids: Array[Vector2i], label: String, radius: float = RADIUS) -> void:
	var distance := _sweep_clearance(from, path, solids)
	_check(not path.is_empty() and distance + EPS >= radius, "%s: 실제 반경 %.2f · 모든 이동 선분 최소 여유 %.3f · 길 %s" % [label, radius, distance, path])


func _straight_and_small() -> void:
	var no_nav: Node3D = _level_script.new()
	var from := Vector3(2.1, 4.0, 2.2)
	var to := Vector3(7.8, 6.0, 7.7)
	var flat_to := Vector3(to.x, 0.0, to.z)
	_check(_path(no_nav, from, to) == PackedVector3Array([flat_to]), "격자 없는 레벨은 큰 몸도 기존 직선·바닥 y=0")
	no_nav.free()
	var size := Vector2i(14, 14)
	var solids := _outline(size)
	var lvl := _level(size, solids)
	var golden := PackedVector3Array([Vector3(3.5, 0.0, 3.5), Vector3(4.5, 0.0, 4.5), Vector3(5.5, 0.0, 5.5), Vector3(6.5, 0.0, 6.5), flat_to])
	var legacy: PackedVector3Array = lvl.call("find_path", from, to)
	_check(legacy == golden, "기존 두 인자 길 = 대각 셀 중심 · 마지막 실제 클릭 좌표")
	for radius in [0.0, 0.35, 0.5]:
		_check(_path(lvl, from, to, float(radius)) == legacy, "작은 몸 %.2f 길 = 기존 두 인자와 동일" % float(radius))
	var large := _path(lvl, from, to)
	_safe(from, large, solids, "트인 바닥 큰 몸")
	_check((lvl.call("find_path", from, to) as PackedVector3Array) == legacy and _path(lvl, from, to, 0.35) == legacy,
		"큰 몸 경로를 만든 뒤에도 원본 작은 몸 격자·대각 길 동일")
	lvl.free()


func _brazier_and_corners() -> void:
	var size := Vector2i(14, 14)
	var solids := _outline(size)
	solids.append(Vector2i(6, 6))
	var lvl := _level(size, solids)
	var from := _center(Vector2i(3, 6))
	var to := _center(Vector2i(10, 6))
	var old: PackedVector3Array = lvl.call("find_path", from, to)
	_check(_sweep_clearance(from, old, solids) < RADIUS, "1×1 화로 픽스처는 원본 셀 경로의 큰 몸 끼임을 드러냄")
	var path := _path(lvl, from, to)
	_safe(from, path, solids, "1×1 화로 우회")
	var cardinal := true
	var a := from
	for b in path:
		cardinal = cardinal and (is_equal_approx(a.x, b.x) or is_equal_approx(a.z, b.z))
		a = b
	_check(cardinal, "셀 중심 사이 큰 몸 길은 직교 — 대각 모서리 절단 없음")
	lvl.free()
	# 대각선으로 붙은 두 상자 사이 1칸 모서리는 반지름 .9가 지나갈 수 없다.
	solids = _outline(size)
	solids.append(Vector2i(6, 6))
	solids.append(Vector2i(8, 8))
	lvl = _level(size, solids)
	from = _center(Vector2i(4, 9))
	to = _center(Vector2i(10, 4))
	path = _path(lvl, from, to)
	_safe(from, path, solids, "대각선 상자 두 모서리 여유")
	var passed_pinch := false
	for p in path:
		passed_pinch = passed_pinch or _world_cell(p) == Vector2i(7, 7)
	_check(not path.is_empty() and not passed_pinch, "두 상자 대각 모서리 틈 (7,7)은 큰 몸 길에 없음")
	lvl.free()


func _corridors() -> void:
	var size := Vector2i(17, 15)
	var rooms: Array[Rect2i] = [Rect2i(2, 2, 5, 11), Rect2i(10, 2, 5, 11)]
	var three: Array[Rect2i] = rooms.duplicate()
	three.append(Rect2i(7, 6, 3, 3))
	var solids := _carve(size, three)
	var lvl := _level(size, solids)
	var from := _center(Vector2i(4, 7))
	var to := _center(Vector2i(12, 7))
	var path := _path(lvl, from, to)
	_safe(from, path, solids, "3칸 복도의 반지름 .9 중앙길")
	var central := true
	for p in path:
		central = central and is_equal_approx(p.z, 7.5)
	_check(not path.is_empty() and central, "3칸 복도에서 중앙 직선길이 살아 있음")
	_check(_path(lvl, from, to, 1.2).is_empty() and not _path(lvl, from, to, RADIUS).is_empty(),
		"반경별 경로 격자 독립: .9는 3칸 통과 · 1.2+선회 여유는 못 통과 · .9 다시 통과")
	lvl.free()
	var one: Array[Rect2i] = rooms.duplicate()
	one.append(Rect2i(7, 7, 3, 1))
	solids = _carve(size, one)
	lvl = _level(size, solids)
	_check(not _path(lvl, from, to, 0.35).is_empty(), "1칸 복도는 원래 작은 몸에게 열려 있음")
	_check(_path(lvl, from, to).is_empty(), "방 둘 사이 1칸 복도는 반지름 .9 몸이 통과하지 못함")
	lvl.free()


func _start_and_end() -> void:
	var size := Vector2i(16, 20)
	var solids := _outline(size)
	for z in range(1, size.y - 1):
		solids.append(Vector2i(1, z))
	solids.append(Vector2i(4, 14))
	var lvl := _level(size, solids)
	var from := Vector3(3.99967, 0.0, 13.09992)
	var to := Vector3(6.826933, 0.0, 11.78921)
	var path := _path(lvl, from, to)
	_safe(from, path, solids, "화로 북면 실좌표에서 첫 보정점까지")
	_check(not path.is_empty() and path[0].is_equal_approx(Vector3(3.5, 0.0, 12.5)),
		"큰 몸이 막힌 출발 셀에서 빠져나올 첫 보정 중심 (3.5,12.5)을 보존")
	_check(not path.is_empty() and path[path.size() - 1].is_equal_approx(to), "끝 실좌표와 그 앞 이동 선분에 여유가 있으면 실제 칼 좌표까지 감")
	lvl.free()
	# 걷는 셀 안이지만 몸 .9가 막는 상자에 겹치는 끝 좌표는 그대로 반환하지 않는다.
	size = Vector2i(14, 14)
	solids = _outline(size)
	solids.append(Vector2i(6, 6))
	lvl = _level(size, solids)
	from = Vector3(9.5, 0.0, 3.5)
	to = Vector3(6.85, 0.0, 5.7)
	path = _path(lvl, from, to)
	_check(_point_clearance(to, solids) < RADIUS and bool(lvl.call("is_cell_walkable", _world_cell(to))), "끝 보정 픽스처: 걷는 셀의 클릭이 큰 몸에겐 위험")
	_safe(from, path, solids, "큰 몸 끝 좌표 보정")
	_check(not path.is_empty() and not path[path.size() - 1].is_equal_approx(to), "걷는 셀이어도 큰 몸 여유 없는 끝 좌표는 안전한 중심으로 보정")
	lvl.free()
	# 끝점 자체는 .9가 서지만, 큰 몸 격자 밖 2칸 굽은 복도로 곧장 잇는 선분은 벽을 가른다.
	size = Vector2i(16, 16)
	var floors: Array[Rect2i] = [Rect2i(2, 2, 7, 6), Rect2i(9, 4, 4, 2), Rect2i(11, 6, 2, 6)]
	solids = _carve(size, floors)
	lvl = _level(size, solids)
	from = Vector3(4.5, 0.0, 4.5)
	to = Vector3(12.0, 0.0, 10.0)
	path = _path(lvl, from, to)
	_check(_point_clearance(to, solids) + EPS >= RADIUS, "끝 이동 선분 픽스처: 끝점 자체의 몸 여유는 안전")
	_safe(from, path, solids, "끝점까지 지름길이 벽을 가르면 보정 중심에 멈춤")
	_check(not path.is_empty() and not path[path.size() - 1].is_equal_approx(to), "끝점뿐 아니라 마지막 이동 선분 전체를 검사")
	lvl.free()


func _cache_changes() -> void:
	var size := Vector2i(14, 14)
	var solids := _outline(size)
	var lvl := _level(size, solids)
	var from := _center(Vector2i(3, 6))
	var to := _center(Vector2i(10, 6))
	var path := _path(lvl, from, to)
	_safe(from, path, solids, "장애물 갱신 전 경로")
	_path(lvl, from, to, 1.1)   # 다른 큰 몸 반경의 캐시도 먼저 만든다.
	var added := Vector2i(6, 6)
	lvl.call("nav_set_solid", added, true)
	solids.append(added)
	_safe(from, _path(lvl, from, to), solids, "nav_set_solid 뒤 .9 경로 즉시 갱신")
	_safe(from, _path(lvl, from, to, 1.1), solids, "nav_set_solid 뒤 다른 반경 캐시도 갱신", 1.1)
	lvl.call("nav_set_solid", added, false)
	solids.erase(added)
	path = _path(lvl, from, to)
	var reopened := not path.is_empty()
	for p in path:
		reopened = reopened and is_equal_approx(p.z, from.z)
	_check(reopened, "막는 칸을 열면 큰 몸 중앙 직선길이 다시 열림")
	# 같은 Level을 전혀 다른 1칸 복도 지도로 다시 만든다 — 예전 큰몸 캐시를 쓰면 거짓 통과한다.
	var floors: Array[Rect2i] = [Rect2i(2, 2, 4, 10), Rect2i(9, 2, 3, 10), Rect2i(6, 6, 3, 1)]
	solids = _carve(size, floors)
	lvl.call("nav_init", Rect2i(Vector2i.ZERO, size))
	for cell in solids:
		lvl.call("nav_set_solid", cell, true)
	lvl.call("nav_finish")
	_check(_path(lvl, from, to).is_empty(), "nav_init·nav_finish로 다시 만든 층에 이전 큰 몸 경로가 남지 않음")
	lvl.free()
