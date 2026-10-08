class_name ActorVisual
extends Node3D
## ActorVisual — 배우의 `Visual` 노드. ModelDef가 가리키는 GLB가 있으면 인스턴스해 플레이스홀더(캡슐)를 숨기고,
## 없으면 플레이스홀더를 그대로 둔다. 애니 상태기(idle/walk 루프 + attack/hit 단발 + die)도 여기.
## 왜 이 구조인가(D-067 "코드는 아트를 기다리지 않는다"): 배우 스크립트(player/enemy/npc)는 "움직인다·때린다·맞았다·죽었다"만 알리고
## 클립 이름·스케일·정면 보정은 데이터(ModelDef)와 이 노드가 흡수한다. 대안 = 각 배우가 AnimationPlayer를 직접 다루기 →
## 모델마다 클립 이름이 달라(Meshy "Sword Slash", Tripo "preset:slash") 배우 코드가 아트에 끌려간다 → 기각.
## 사양 design/art_3d_pipeline.md §2.

## 동의어 — 생성 서비스마다 다른 프리셋 이름을 흡수 (§2.3). 순서 = 우선순위.
const SYNONYMS := {
	"idle": ["idle", "stand", "breath", "wait"],
	"walk": ["walk", "move", "locomot"],
	"run": ["run", "sprint", "jog"],
	"attack": ["attack", "slash", "punch", "kick", "bite", "cast", "shoot", "throw", "strike"],
	"hit": ["hit", "hurt", "damage", "impact", "react", "flinch"],
	"die": ["die", "death", "dying", "dead", "fall", "down", "defeat"],
}
## 걷기 판정 속도(유닛/초).
const MOVE_EPS := 0.2
## 클립 사이 블렌드(초).
const BLEND := 0.1

signal model_changed(loaded: bool)

@export var model: ModelDef

var moving: bool = false

var _model_root: Node3D
var _anim: AnimationPlayer
var _weapon: Node3D
## 공격 클립 목록(attack, attack2, …) — play_attack / play_once("attack")이 무작위로 고른다(같은 클립 연속 금지, combat_v2 §6).
var _attack_clips: PackedStringArray = []
var _last_attack: String = ""
var _hitstop_token: int = 0
var _flash_token: int = 0
## 피격 플래시 오버레이(공유). unshaded 흰색 반투명 — 플레이스홀더 캡슐에도 그대로 먹는다.
static var _flash_mat: StandardMaterial3D
## 동작 키 → 실제 클립 이름 (없으면 "").
var _clips: Dictionary = {}
var _placeholders: Array[Node] = []
## 단발 동작(attack/hit/die)이 끝나는 시각. 그 전엔 idle/walk로 덮어쓰지 않는다.
var _busy_until: float = 0.0
var _dead: bool = false
var _current: String = ""


func _ready() -> void:
	if _model_root == null:
		apply_model(model)


## 모델 교체. 성공(파일 있고 로드됨) 여부 반환. 실패 시 플레이스홀더가 보인다.
func apply_model(def: ModelDef) -> bool:
	var node: Node3D = null
	if def != null and def.exists():
		var ps := load(def.scene_path) as PackedScene
		if ps:
			node = ps.instantiate() as Node3D
	return apply_node(node, def)


## 이미 인스턴스된 노드를 모델로 (뷰어가 GLTFDocument로 직접 읽은 GLB를 넘길 때). node=null이면 플레이스홀더.
func apply_node(node: Node3D, def: ModelDef) -> bool:
	model = def
	# 플레이스홀더 = 처음 호출 시점의 기존 자식들 (트리 밖에서 불려도 동작하도록 _ready에 의존하지 않는다)
	if _placeholders.is_empty():
		for c in get_children():
			if c != _model_root:
				_placeholders.append(c)
	if _model_root:
		_model_root.queue_free()
		_model_root = null
	_anim = null
	_clips.clear()
	_attack_clips.clear()
	_last_attack = ""
	var loaded := false
	_model_root = node
	if _model_root and def:
		_model_root.name = "Model"
		add_child(_model_root)
		_model_root.scale = Vector3.ONE * def.scale
		_model_root.position.y = def.y_offset
		_model_root.rotation.y = deg_to_rad(def.yaw_offset_deg)
		_anim = _model_root.find_child("AnimationPlayer", true, false) as AnimationPlayer
		if _anim:
			for kind in SYNONYMS:
				_clips[kind] = resolve_anim(_anim.get_animation_list(), def.anim_name(kind), kind)
			for kind in ["idle", "walk", "run"]:
				var n: String = _clips.get(kind, "")
				if n != "":
					_anim.get_animation(n).loop_mode = Animation.LOOP_LINEAR
			# 공격 다양화: 해석된 attack + 이름이 "attack"으로 시작하는 나머지 클립(attack2, attack_thrust…)
			var primary: String = _clips.get("attack", "")
			if primary != "":
				_attack_clips.append(primary)
			for n in _anim.get_animation_list():
				if n != primary and n.to_lower().begins_with("attack"):
					_attack_clips.append(n)
		if def.pixel_filter:
			_apply_pixel_filter(_model_root)
		_attach_weapon(def)
		_attach_springs(def)
		loaded = true
	for p in _placeholders:
		if p is Node3D:
			(p as Node3D).visible = not loaded
	_dead = false
	_busy_until = 0.0
	_current = ""
	_play("idle")
	model_changed.emit(loaded)
	return loaded


func is_model_loaded() -> bool:
	return _model_root != null


## 손에 붙은 무기 노드 (없으면 null). 뷰어·테스트용.
func weapon_node() -> Node3D:
	return _weapon


# ---------- 무기 소켓 (§2.6) ----------

## 무기 = 별도 프롭. 스켈레톤의 손 본에 BoneAttachment3D를 만들고 그 아래 무기 씬(없으면 임시 검)을 붙인다.
## 왜 캐릭터 메시에 안 굽나: 생성기가 검을 손에 쥔 채 뽑으면 T-pose·리깅이 깨지고(§7), 장비 교체(D-023 무기 드랍)도 불가능하다.
## Armature가 0.01 배율(Meshy)이어도 무기가 1유닛 크기로 보이도록 스켈레톤까지의 누적 배율을 나눈다.
func _attach_weapon(def: ModelDef) -> void:
	_weapon = null
	if _model_root == null or def == null:
		return
	if def.weapon_scene == "" and not def.weapon_placeholder:
		return
	var skeletons := _model_root.find_children("*", "Skeleton3D", true, false)
	if skeletons.is_empty():
		return
	var sk := skeletons[0] as Skeleton3D
	var bone := find_hand_bone(sk, def.weapon_bone)
	if bone < 0:
		push_warning("ActorVisual: 무기 본을 못 찾음 (%s) — 본: %s" % [def.weapon_bone, _bone_names(sk)])
		return
	var w: Node3D = null
	if def.weapon_scene != "" and ResourceLoader.exists(def.weapon_scene):
		var ps := load(def.weapon_scene) as PackedScene
		if ps:
			w = ps.instantiate() as Node3D
	if w == null and def.weapon_placeholder:
		w = make_placeholder_sword()
	if w == null:
		return
	var att := BoneAttachment3D.new()
	att.name = "WeaponSocket"
	sk.add_child(att)
	att.bone_name = sk.get_bone_name(bone)
	# 모델 루트 → 스켈레톤 누적 배율 (Meshy Armature 0.01 등) 보정
	var chain_scale := 1.0
	var n: Node = sk
	while n != null and n != _model_root:
		if n is Node3D:
			chain_scale *= (n as Node3D).scale.x
		n = n.get_parent()
	if chain_scale <= 0.0:
		chain_scale = 1.0
	w.name = "Weapon"
	att.add_child(w)
	w.position = def.weapon_offset_pos / chain_scale
	w.rotation_degrees = def.weapon_offset_rot_deg
	w.scale = Vector3.ONE * (def.weapon_scale / chain_scale)
	_weapon = w


## 스프링본 (art_3d_pipeline §12): ModelDef.spring_roots/ends 쌍마다 SpringBoneSimulator3D 설정 1개. 리그에 없는 본은 건너뛴다.
## 왜 데이터 주도인가: 어떤 뼈를 흔들지는 캐릭터·리그마다 다르고(허리끈·술·꼬리), 코드는 "쌍 목록"만 알면 된다.
func _attach_springs(def: ModelDef) -> void:
	if def == null or def.spring_roots.is_empty() or _model_root == null:
		return
	var skeletons := _model_root.find_children("*", "Skeleton3D", true, false)
	if skeletons.is_empty():
		return
	var sk := skeletons[0] as Skeleton3D
	var sim := SpringBoneSimulator3D.new()
	sim.name = "SpringBones"
	var n := 0
	for i in def.spring_roots.size():
		var root_name := def.spring_roots[i]
		var end_name: String = def.spring_ends[i] if i < def.spring_ends.size() else root_name
		if sk.find_bone(root_name) < 0 or sk.find_bone(end_name) < 0:
			push_warning("ActorVisual: 스프링본 본 없음 %s→%s" % [root_name, end_name])
			continue
		sim.set_setting_count(n + 1)
		sim.set_root_bone_name(n, root_name)
		sim.set_end_bone_name(n, end_name)
		sim.set_extend_end_bone(n, true)
		sim.set_stiffness(n, def.spring_stiffness)
		sim.set_drag(n, def.spring_drag)
		sim.set_gravity(n, def.spring_gravity)
		sim.set_gravity_direction(n, Vector3.DOWN)
		n += 1
	if n == 0:
		sim.free()
		return
	sk.add_child(sim)


## 손 본 찾기: 정확 → "hand" 포함 + 오른쪽 표식(right / r_ / _r / .r / mixamorig:Right) + 손가락 본 제외. static = 테스트·검수 공용.
static func find_hand_bone(sk: Skeleton3D, wanted: String) -> int:
	var i := sk.find_bone(wanted)
	if i >= 0:
		return i
	var best := -1
	for b in sk.get_bone_count():
		var n := sk.get_bone_name(b).to_lower()
		if not n.contains("hand"):
			continue
		if n.contains("thumb") or n.contains("index") or n.contains("middle") or n.contains("ring") or n.contains("pinky") or n.contains("finger"):
			continue
		var right := n.contains("right") or n.begins_with("r_") or n.ends_with("_r") or n.ends_with(".r") or n.contains(":r_")
		if not right:
			continue
		if best < 0 or sk.get_bone_name(b).length() < sk.get_bone_name(best).length():
			best = b
	return best


## 임시 검(회색 칼날 + 검은 손잡이). 원점 = 손아귀, +Y = 칼끝. 진짜 검 GLB도 이 축으로 만든다(§2.6).
static func make_placeholder_sword() -> Node3D:
	var root := Node3D.new()
	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.78, 0.8, 0.85)
	steel.metallic = 0.8
	steel.roughness = 0.35
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.12, 0.1, 0.09)
	var blade := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.035, 0.74, 0.008)
	blade.mesh = bm
	blade.material_override = steel
	blade.position = Vector3(0, 0.06 + 0.37, 0)
	root.add_child(blade)
	var guard := MeshInstance3D.new()
	var gm := BoxMesh.new()
	gm.size = Vector3(0.12, 0.02, 0.03)
	guard.mesh = gm
	guard.material_override = dark
	guard.position = Vector3(0, 0.055, 0)
	root.add_child(guard)
	var grip := MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.015
	cm.bottom_radius = 0.017
	cm.height = 0.16
	grip.mesh = cm
	grip.material_override = dark
	grip.position = Vector3(0, -0.035, 0)
	root.add_child(grip)
	return root


static func _bone_names(sk: Skeleton3D) -> String:
	var names: Array = []
	for b in sk.get_bone_count():
		names.append(sk.get_bone_name(b))
	return ", ".join(names)


func has_clip(kind: String) -> bool:
	return _clips.get(kind, "") != ""


## 동작 키 → 실제 클립 이름 ("" = 없음).
func clip_for(kind: String) -> String:
	return _clips.get(kind, "")


## 모델의 클립 이름 전부 (뷰어·검수용).
func clip_names() -> PackedStringArray:
	return _anim.get_animation_list() if _anim else PackedStringArray()


## 지금 재생 중인 클립 이름 ("" = 없음/모델 없음).
func current_clip() -> String:
	return _anim.current_animation if _anim else ""


## 뷰어용: 동작 키를 강제 재생(단발 잠금 무시).
func play_kind(kind: String) -> void:
	_busy_until = 0.0
	_dead = false
	_play(kind, true)


## 뷰어용: 클립 이름 직접 재생.
func play_clip(name: String) -> void:
	if _anim and _anim.has_animation(name):
		_busy_until = _now() + 3600.0
		_current = name
		_anim.play(name, BLEND)
		_anim.seek(0.0, true)


## 동작 키의 클립 길이(초). 없으면 0.
func clip_length(kind: String) -> float:
	var n: String = _clips.get(kind, "")
	return _anim.get_animation(n).length if (_anim and n != "") else 0.0


## 매 물리 틱: 배우가 자기 속도(유닛/초)로 알려준다. idle/walk/run 전환과 **발 미끄럼 방지**(재생 배율 = 실제 속도 ÷ 클립 지면 속도)는 여기서만.
## 왜 speed_scale인가: 이동 클립은 매 틱 속도가 바뀌므로 play()를 다시 부르지 않고 플레이어 배율만 바꾼다(단발 동작·히트스톱은 1.0으로 되돌린다).
func set_moving(m: bool, speed: float = 0.0) -> void:
	moving = m
	if _dead or _now() < _busy_until:
		return
	if not moving:
		_play("idle")
		if _anim:
			_anim.speed_scale = 1.0
		return
	var kind := "walk"
	var natural := model.walk_speed if model else 1.0
	if model and speed >= model.run_threshold and has_clip("run"):
		kind = "run"
		natural = model.run_speed
	_play(kind)
	if _anim and speed > 0.0 and natural > 0.0:
		var lo: float = model.loco_scale_min if model else 0.75
		var hi: float = model.loco_scale_max if model else 1.8
		_anim.speed_scale = clampf(speed / natural, lo, hi)


## 단발 동작(attack/hit). 클립이 없으면 fallback_sec만 idle/walk 전환을 막는다(타이밍은 배우 로직이 잡음).
func play_once(kind: String, fallback_sec: float = 0.3) -> void:
	if _dead:
		return
	var n: String = _pick_attack() if kind == "attack" else String(_clips.get(kind, ""))
	var dur := _len_of(n)
	_busy_until = _now() + (dur if dur > 0.0 else fallback_sec)
	if dur > 0.0:
		_play_name(n, 1.0)


## 공격 휘두르기 (combat_v2 §6): 클립을 interval(=1/공속) 초 안에 끝나게 재생해 공속이 곧 휘두르는 속도가 된다(디아2 IAS 감각).
## 반환 = 칼이 닿는 시각(초, 지금부터). 클립이 없으면 0 → 호출자가 즉시 타격. 속도 배율은 0.5~3배로 묶는다(너무 느리거나 우스꽝스럽지 않게).
func play_attack(interval: float) -> float:
	if _dead:
		return 0.0
	var n := _pick_attack()
	var clip_len := _len_of(n)
	if clip_len <= 0.0 or interval <= 0.0:
		_busy_until = _now() + maxf(interval * 0.5, 0.2)
		return 0.0
	var speed := clampf(clip_len / interval, 0.5, 3.0)
	var duration := clip_len / speed
	_busy_until = _now() + duration
	_play_name(n, speed)
	return impact_frac(n) * duration


## 클립의 타격 시각 비율(0~1). ModelDef.attack_impact[clip] → 없으면 기본값.
func impact_frac(clip: String) -> float:
	if model == null:
		return 0.45
	return float(model.attack_impact.get(clip, model.attack_impact_default))


## 히트스톱: 애니를 sec 초 멈춘다(공격자·피격자 양쪽에 걸면 "닿았다"가 몸으로 느껴진다). 겹치면 마지막 것만 유효.
func hit_stop(sec: float) -> void:
	if _anim == null or not is_inside_tree():
		return
	_anim.speed_scale = 0.0
	_hitstop_token += 1
	var tok := _hitstop_token
	get_tree().create_timer(sec).timeout.connect(func() -> void:
		if tok == _hitstop_token and _anim:
			_anim.speed_scale = 1.0)


## 피격 플래시: 보이는 메시 전부에 흰 오버레이를 sec 초 씌운다.
func flash(sec: float = 0.08) -> void:
	if not is_inside_tree():
		return
	if _flash_mat == null:
		_flash_mat = StandardMaterial3D.new()
		_flash_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		_flash_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_flash_mat.albedo_color = Color(1.0, 0.97, 0.9, 0.7)
	_flash_token += 1
	var tok := _flash_token
	var targets: Array[Node] = []
	for mi in find_children("*", "MeshInstance3D", true, false):
		if (mi as MeshInstance3D).visible:
			(mi as MeshInstance3D).material_overlay = _flash_mat
			targets.append(mi)
	get_tree().create_timer(sec).timeout.connect(func() -> void:
		if tok != _flash_token:
			return
		for mi in targets:
			if is_instance_valid(mi):
				(mi as MeshInstance3D).material_overlay = null)


## 공격 클립 고르기: 2개 이상이면 무작위, 직전 것과 다른 클립.
func _pick_attack() -> String:
	if _attack_clips.is_empty():
		return ""
	var n := _attack_clips[0]
	if _attack_clips.size() > 1:
		n = _attack_clips[randi() % _attack_clips.size()]
		if n == _last_attack:
			n = _attack_clips[(_attack_clips.find(n) + 1) % _attack_clips.size()]
	_last_attack = n
	return n


func _len_of(n: String) -> float:
	return _anim.get_animation(n).length if (_anim and n != "" and _anim.has_animation(n)) else 0.0


func _play_name(n: String, speed: float) -> void:
	_current = n
	_anim.speed_scale = 1.0   # 이동 배율은 단발 동작에 섞이지 않게
	_anim.play(n, BLEND, speed)
	_anim.seek(0.0, true)


## 사망. 반환 = 클립 길이(초, 없으면 0) — 배우가 그만큼 기다렸다가 사라진다.
func play_die() -> float:
	_dead = true
	var dur := clip_length("die")
	if dur > 0.0:
		_play("die", true)
	return dur


func revive() -> void:
	_dead = false
	_busy_until = 0.0
	_current = ""
	_play("idle")


# ---------- 내부 ----------

func _play(kind: String, restart: bool = false) -> void:
	if _anim == null:
		return
	var n: String = _clips.get(kind, "")
	if n == "":
		return
	if _current == n and not restart:
		return
	_current = n
	_anim.play(n, BLEND)
	if restart:
		_anim.seek(0.0, true)


func _now() -> float:
	return float(Time.get_ticks_msec()) / 1000.0


## GLB 안의 모든 머티리얼을 nearest 필터로 (픽셀 느낌).
static func _apply_pixel_filter(root: Node) -> void:
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m := (mi as MeshInstance3D).mesh
		if m == null:
			continue
		for i in m.get_surface_count():
			var mat := m.surface_get_material(i) as BaseMaterial3D
			if mat:
				mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST


## 클립 목록에서 동작 키에 맞는 이름을 찾는다 (§2.3: 정확 → 부분 → 동의어). 없으면 "".
## static인 이유: model_check·단위 테스트가 트리 없이 같은 규칙으로 검사한다.
static func resolve_anim(names: PackedStringArray, wanted: String, kind: String) -> String:
	if wanted != "" and names.has(wanted):
		return wanted
	var w := wanted.to_lower()
	if w != "":
		for n in names:
			if n.to_lower().contains(w):
				return n
	for syn in SYNONYMS.get(kind, []):
		for n in names:
			if n.to_lower().contains(syn):
				return n
	return ""
