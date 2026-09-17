extends Camera3D
## IsoCamera — 직교(orthographic) 아이소메트릭 카메라. 대상(Player)을 고정 각도에서 따라간다.
## 왜 3D+직교 카메라인가(D-067): 캐릭터가 Tripo/Meshy 3D 모델이라 8방향 스프라이트 사전 렌더가 불필요.
## 회전이 공짜, 플레이어 조명 = 디아1 시야 반경이 그대로. 대안 = 2D 아이소 타일맵+사전렌더 → 파이프라인 2배라 기각.

@export var target_path: NodePath
## 카메라 내려다보는 각도(도). 35.264 = 정통 아이소, 디아2 감성은 30~40 사이.
@export_range(20.0, 60.0) var pitch_deg: float = 35.264
## 좌우 회전(도). 45 = 격자 대각.
@export var yaw_deg: float = 45.0
@export var distance: float = 30.0
## 직교 크기 = 화면 세로에 들어오는 월드 유닛 수. 1유닛 = 타일 1칸.
## 14 → 11 (2026-09-17 PD, art_3d_pipeline §11): 도호 87px → 110px. 디아2 캐릭 ≈ 화면 세로 15%에 맞춤. 시야 반경(OmniLight r=9)은 그대로.
@export var ortho_size: float = 11.0
@export var follow_speed: float = 10.0

var _target: Node3D
## 따라가기 기준 위치(킥 제외). 킥 오프셋은 여기에 더해서만 표시한다 — 보간 상태를 더럽히지 않게.
var _base: Vector3
var _kick: Vector3 = Vector3.ZERO
var _kick_t: float = 0.0
const KICK_SEC := 0.12


func _ready() -> void:
	projection = PROJECTION_ORTHOGONAL
	size = ortho_size
	_target = get_node_or_null(target_path)
	rotation_degrees = Vector3(-pitch_deg, yaw_deg, 0.0)
	snap_to_target()


func _process(delta: float) -> void:
	if _target == null:
		return
	var desired := _desired_position()
	_base = _base.lerp(desired, clampf(follow_speed * delta, 0.0, 1.0))
	var off := Vector3.ZERO
	if _kick_t > 0.0:
		_kick_t = maxf(_kick_t - delta, 0.0)
		off = _kick * (_kick_t / KICK_SEC)
	global_position = _base + off


## 타격 킥(combat_v2 §6): 화면 아래로 amount 유닛 튕겼다가 KICK_SEC에 걸쳐 복귀. 직교 카메라라 시선 방향 이동은 안 보이므로 화면 축으로 민다.
func kick(amount: float) -> void:
	_kick = -global_transform.basis.y * amount
	_kick_t = KICK_SEC


func snap_to_target() -> void:
	if _target:
		_base = _desired_position()
		global_position = _base


func _desired_position() -> Vector3:
	# 카메라가 바라보는 방향(-Z 로컬)의 반대로 distance만큼 물러선 위치.
	var back := -global_transform.basis.z  # 카메라 forward
	return _target.global_position - back * distance
