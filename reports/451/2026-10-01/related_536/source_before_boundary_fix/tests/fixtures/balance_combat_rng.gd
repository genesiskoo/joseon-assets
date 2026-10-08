extends Node
## #536 시험 전용 전투 스트림. balance_boss의 go_down 전에 Main 자식으로 붙인다.
## Enemy/PlayerCombat의 게임 randomize·명중·스탯·파수 AI를 바꾸지 않는다.
## 판/몸별 시드식은 최초 전투 실행 전에 docs/design/balance_rng_536.md에서 고정했다.

const PLAYER := 1
const BOSS := 2
const SUMMON_BAT := 3
const GUARD_BAT := 4
const ROLE_NAMES := {PLAYER: "doho", BOSS: "heukrang", SUMMON_BAT: "summon_bat", GUARD_BAT: "guard_bat"}

var _dungeon_script: Script
var _tree: SceneTree
var _event_bus: Node
var _target_level: WeakRef
var _boss: WeakRef
var _area_id: StringName
var _floor_no := 0
var _base := 0
var _level := 0
var _attempt := 0
var _guard_ordinal := 0
var _spawn_ordinal := 0
var _active := false
var _next_trace_time := 0.0
var _trace_samples := 0
var _note: Callable
var _records: Array[Dictionary] = []
var _pending: Array[Dictionary] = []
var _finished: Array[Dictionary] = []


static func seed_for(base: int, level: int, attempt: int, role: int, ordinal: int = 0) -> int:
	return base + level * 1000003 + attempt * 10007 + role * 1009 + ordinal * 101


## 층 입장 전. 영속 도호는 지금, 지정 보스 층의 적은 ready 직후 고정한다.
func begin(combat: Node, base: int, level: int, attempt: int, area_id: StringName, floor_no: int, note: Callable = Callable()) -> void:
	close()
	_dungeon_script = load("res://world/dungeon_level.gd")
	_tree = get_tree()
	_event_bus = _tree.root.get_node("EventBus")
	_target_level = null
	_boss = null
	_area_id = area_id
	_floor_no = floor_no
	_base = base
	_level = level
	_attempt = attempt
	_note = note
	_guard_ordinal = 0
	_spawn_ordinal = 0
	_next_trace_time = 0.0
	_trace_samples = 0
	_records.clear()
	_pending.clear()
	_finished.clear()
	_active = true
	_bind_actor(combat, PLAYER, 0)
	_tree.node_added.connect(_on_node_added)
	_event_bus.level_loaded.connect(_on_level_loaded)


func _has_actor(actor: Node) -> bool:
	for record in _records:
		if record.actor.get_ref() == actor:
			return true
	for pending in _pending:
		if pending.actor.get_ref() == actor:
			return true
	return false


func _matches_level(node: Node) -> bool:
	return node.get_script() == _dungeon_script and node.area != null and node.area.id == _area_id and node.floor_no == _floor_no


## preset 생성 루프가 map.guard_cells 순서대로 파수를 add_child한다. ready에는 아직 위치가 원점이다.
func _on_node_added(node: Node) -> void:
	if not _active:
		return
	if _matches_level(node):
		_target_level = weakref(node)
		node.tree_exiting.connect(_on_level_exiting)
		return
	if not node.has_method("seed_rng") or _has_actor(node):
		return
	var target: Node = _target_level.get_ref() if _target_level else null
	if not is_instance_valid(target) or node.get_parent() != target.get("_enemies"):
		return
	var def = node.get("def")
	if def == null:
		return
	if String(def.id) == "boss_heukrang":
		_boss = weakref(node)
		_bind_after_ready(node, BOSS, 0)
	elif String(def.id) == "bat":
		var boss: Node = _boss.get_ref() if _boss else null
		if is_instance_valid(boss) and bool(boss.get("_phase2")):
			_spawn_ordinal += 1
			_bind_after_ready(node, SUMMON_BAT, _spawn_ordinal)
		else:
			var map = target.get("map")
			if map == null or _guard_ordinal >= map.guard_cells.size():
				push_error("BalanceCombatRng: 파수 생성이 map.guard_cells 계약을 넘었다")
				return
			_guard_ordinal += 1
			_bind_after_ready(node, GUARD_BAT, _guard_ordinal)


func _bind_after_ready(actor: Node, role: int, ordinal: int) -> void:
	if actor.is_node_ready():
		_bind_actor(actor, role, ordinal)
	else:
		# Enemy._ready.randomize 뒤, 첫 physics의 겹침 분리·돌격·공격 소비 전 동기 ready 콜백.
		var apply := _bind_actor.bind(actor, role, ordinal)
		_pending.append({"actor": weakref(actor), "apply": apply})
		actor.ready.connect(apply, CONNECT_ONE_SHOT)


func _bind_actor(actor: Node, role: int, ordinal: int) -> void:
	for i in range(_pending.size() - 1, -1, -1):
		if _pending[i].actor.get_ref() == actor:
			_pending.remove_at(i)
	if not _active or not is_instance_valid(actor):
		return
	var rng := actor.get("_rng") as RandomNumberGenerator
	if rng == null:
		push_error("BalanceCombatRng: 실제 몸에 private _rng가 없다")
		return
	var previous_seed: int = rng.seed
	var previous_state: int = rng.state
	var seed := seed_for(_base, _level, _attempt, role, ordinal)
	if actor.has_method("seed_rng"):
		actor.call("seed_rng", seed)
	else:
		# PlayerCombat에는 공개 seed API가 없어서 시험 fixture에서만 private 스트림을 고정한다.
		rng.seed = seed
	var record := {"actor": weakref(actor), "rng": rng, "role": role, "ordinal": ordinal, "seed": seed,
		"initial": int(rng.state), "previous_seed": previous_seed, "previous_state": previous_state}
	_records.append(record)
	if _note.is_valid():
		_note.call(_line(record, false))


func _line(record: Dictionary, final: bool) -> String:
	var line := "흑랑 RNG Lv%d 판%d %s%d seed=%d initial=%d" % [_level, _attempt, ROLE_NAMES[record.role], record.ordinal, record.seed, record.initial]
	if final:
		line += " final=%d" % int((record.rng as RandomNumberGenerator).state)
	return line


func actor_count() -> int:
	return _records.size()


func guard_count() -> int:
	return _guard_ordinal


func spawn_count() -> int:
	return _spawn_ordinal


func is_active() -> bool:
	return _active


## 첫 상태로 돌려 실제 같은 전투 굴림을 검산한다. 게임 reset_session 대신 쓰지 않는다.
func rewind() -> void:
	if not _active:
		return
	for record in _records:
		var rng: RandomNumberGenerator = record.rng
		rng.seed = int(record.seed)
		rng.state = int(record.initial)


func snapshot() -> Array[Dictionary]:
	if not _active and not _finished.is_empty():
		return _finished.duplicate(true)
	var out: Array[Dictionary] = []
	for record in _records:
		out.append({"role": int(record.role), "ordinal": int(record.ordinal), "seed": int(record.seed),
			"initial": int(record.initial), "final": int((record.rng as RandomNumberGenerator).state)})
	return out


func finish() -> Array[Dictionary]:
	if _active:
		observe_guard("finish")
		_finished = snapshot()
		if _note.is_valid():
			for record in _records:
				_note.call(_line(record, true))
	close()
	return _finished.duplicate(true)


func _on_level_exiting() -> void:
	finish()


## 입장 도중 중단돼도 다음 대본의 마을 리셋/다른 지역 입장에서 고정 스트림을 남기지 않는다.
func _on_level_loaded(node: Node) -> void:
	if _matches_level(node):
		observe_guard("entered")
	elif node.get_script() != _dungeon_script or node.area == null or node.area.id != _area_id or node.floor_no > _floor_no:
		finish()


## 호출·층 종료 둘 다 같은 정리. 살아 있는 영속 도호를 포함해 원래 seed/state를 돌린다.
func close() -> void:
	if not _active:
		return
	if _finished.is_empty():
		_finished = snapshot()
	_active = false
	if is_instance_valid(_tree) and _tree.node_added.is_connected(_on_node_added):
		_tree.node_added.disconnect(_on_node_added)
	if is_instance_valid(_event_bus) and _event_bus.level_loaded.is_connected(_on_level_loaded):
		_event_bus.level_loaded.disconnect(_on_level_loaded)
	var target: Node = _target_level.get_ref() if _target_level else null
	if is_instance_valid(target) and target.tree_exiting.is_connected(_on_level_exiting):
		target.tree_exiting.disconnect(_on_level_exiting)
	for pending in _pending:
		var actor: Node = pending.actor.get_ref()
		if is_instance_valid(actor) and actor.ready.is_connected(pending.apply):
			actor.ready.disconnect(pending.apply)
	_pending.clear()
	for record in _records:
		var rng: RandomNumberGenerator = record.rng
		rng.seed = int(record.previous_seed)
		rng.state = int(record.previous_state)


func _exit_tree() -> void:
	finish()


## #536 진단: 읽기만 한다. 시드/상태/타깃/AI를 고치거나 난수를 뽑지 않는다.
func observe_guard(tag: String) -> bool:
	if not _active or not _note.is_valid():
		return false
	for record in _records:
		if int(record.role) != GUARD_BAT or int(record.ordinal) != 2:
			continue
		var actor: Node3D = record.actor.get_ref()
		if not is_instance_valid(actor):
			return false
		var target: Node3D = actor.call("target")
		var target_pos := "none"
		if is_instance_valid(target):
			target_pos = "(%.4f,%.4f)" % [target.global_position.x, target.global_position.z]
		var pos: Vector3 = actor.global_position
		var state: int = actor.get("state")
		var path: PackedVector3Array = actor.get("_path")
		var current: Node = _target_level.get_ref() if _target_level else null
		_note.call("흑랑 파수2 Lv%d 판%d %s tick=%d game=%.4f state=%d XZ=(%.4f,%.4f) pack=%d target=%s path=%d/%d level_current=%s rng=%d" % [
			_level, _attempt, tag, Engine.get_physics_frames(), GameClock.now, state, pos.x, pos.z, int(actor.get("pack_id")),
			target_pos, int(actor.get("_path_i")), path.size(), actor.get("_level") == current, int((record.rng as RandomNumberGenerator).state)])
		return true
	return false


func _process(_delta: float) -> void:
	# 최대 48게임초/96줄: 한 판45초+셋업 여유. 멈춘 GameClock에서는 같은 줄을 반복하지 않는다.
	if _active and _trace_samples < 96 and GameClock.now >= _next_trace_time and observe_guard("sample"):
		_trace_samples += 1
		_next_trace_time = GameClock.now + 0.5