extends SceneTree
## retarget_mixamo — Mixamo 클립(스킨 없는 FBX, 기본 캐릭터)을 다른 리그(Tripo/Meshy GLB)에 리타겟해 한 GLB로 합친다.
##   godot --headless -s tools/retarget_mixamo.gd -- --base=<rigged.glb> --out=<out.glb> [--fps=30] idle=<fbx> walk=<fbx> attack=<fbx>[@속도] hit=<fbx> die=<fbx>
##   클립 뒤 `@1.6`처럼 붙이면 재생 속도 배율(길이 1/1.6). Mixamo 클립은 준비·회수가 길어 공격은 1.5~2배가 게임 템포에 맞는다.
##   --upright=idle:9,walk:12  → 그 클립의 Spine을 전역 X축으로 -도만큼 젖혀 상체를 세운다(Mixamo 전투 자세 클립이 10~19° 앞으로 숙여 있음, 실측).
##   --yaw=idle:35  → 그 클립 전체를 Y축으로 +도 돌린다(몸통이 정면 +Z에서 틀어진 클립 교정. Mixamo 전투 자세 클립은 몸이 35~50° 돌아가 있어 게걸음처럼 보임, 실측).
##   --inplace=walk,run  → 힙의 XZ 직선 이동(루트 모션)을 빼서 제자리 클립으로 만든다. 기본값 idle,walk,run (Mixamo "In Place"가 아닌 클립은 1사이클에 1.4u 전진 → 게임에서 매 사이클 앞으로 튀었다 되돌아옴, 실측).
## 왜 이 구조인가: Mixamo 자동 리거는 Tripo/Meshy처럼 수백 조각으로 된 AI 메시를 거부한다(실측 2회 실패). 그래서 메시+리그는
##   생성기 것을 그대로 쓰고, 애니만 Mixamo에서 받아 **글로벌 회전 델타**로 옮긴다: 소스 본의 (포즈 × 레스트⁻¹)를 타깃 본의
##   "실루엣 정렬된 레스트"에 곱한다. 실루엣 정렬 = 타깃 레스트를 소스 레스트와 같은 방향(팔 T포즈 등)으로 돌린 것(Godot 임포터의
##   fix_silhouette와 같은 발상). Blender 없이 godot 하나로 끝나고, 리그 종류별 본 이름표만 추가하면 재사용된다.
## 한계: 손가락·트위스트 본은 리타겟하지 않는다(레스트 유지). 루트 이동은 힙 위치만 키 높이 비율로 옮긴다(걷기는 Mixamo "In Place"로 받을 것).

const PROFILE_CHILD := {
	"Hips": "Spine", "Spine": "Chest", "Chest": "Neck", "Neck": "Head",
	"LeftShoulder": "LeftUpperArm", "LeftUpperArm": "LeftLowerArm", "LeftLowerArm": "LeftHand",
	"RightShoulder": "RightUpperArm", "RightUpperArm": "RightLowerArm", "RightLowerArm": "RightHand",
	"LeftUpperLeg": "LeftLowerLeg", "LeftLowerLeg": "LeftFoot", "LeftFoot": "LeftToes",
	"RightUpperLeg": "RightLowerLeg", "RightLowerLeg": "RightFoot", "RightFoot": "RightToes",
}

# 프로필 본 → 리그별 실제 본 이름. 순서 = Mixamo(접두 유무 둘 다) / Meshy / Tripo
const BONE_MAPS := {
	"mixamo": {
		"Hips": "Hips", "Spine": "Spine", "Chest": "Spine1", "UpperChest": "Spine2", "Neck": "Neck", "Head": "Head",
		"LeftShoulder": "LeftShoulder", "LeftUpperArm": "LeftArm", "LeftLowerArm": "LeftForeArm", "LeftHand": "LeftHand",
		"RightShoulder": "RightShoulder", "RightUpperArm": "RightArm", "RightLowerArm": "RightForeArm", "RightHand": "RightHand",
		"LeftUpperLeg": "LeftUpLeg", "LeftLowerLeg": "LeftLeg", "LeftFoot": "LeftFoot", "LeftToes": "LeftToeBase",
		"RightUpperLeg": "RightUpLeg", "RightLowerLeg": "RightLeg", "RightFoot": "RightFoot", "RightToes": "RightToeBase",
	},
	"meshy": {
		# Meshy 리그의 척추 이름은 계층과 거꾸로다: Hips→Spine02→Spine01→Spine→neck (2026-09-17 실측). 이름이 아니라 위치로 맞춘다.
		"Hips": "Hips", "Spine": "Spine02", "Chest": "Spine01", "UpperChest": "Spine", "Neck": "neck", "Head": "Head",
		"LeftShoulder": "LeftShoulder", "LeftUpperArm": "LeftArm", "LeftLowerArm": "LeftForeArm", "LeftHand": "LeftHand",
		"RightShoulder": "RightShoulder", "RightUpperArm": "RightArm", "RightLowerArm": "RightForeArm", "RightHand": "RightHand",
		"LeftUpperLeg": "LeftUpLeg", "LeftLowerLeg": "LeftLeg", "LeftFoot": "LeftFoot", "LeftToes": "LeftToeBase",
		"RightUpperLeg": "RightUpLeg", "RightLowerLeg": "RightLeg", "RightFoot": "RightFoot", "RightToes": "RightToeBase",
	},
	"tripo": {
		"Hips": "Hip", "Spine": "Spine01", "Chest": "Spine02", "Neck": "NeckTwist01", "Head": "Head",
		"LeftShoulder": "L_Clavicle", "LeftUpperArm": "L_Upperarm", "LeftLowerArm": "L_Forearm", "LeftHand": "L_Hand",
		"RightShoulder": "R_Clavicle", "RightUpperArm": "R_Upperarm", "RightLowerArm": "R_Forearm", "RightHand": "R_Hand",
		"LeftUpperLeg": "L_Thigh", "LeftLowerLeg": "L_Calf", "LeftFoot": "L_Foot", "LeftToes": "L_ToeBase",
		"RightUpperLeg": "R_Thigh", "RightLowerLeg": "R_Calf", "RightFoot": "R_Foot", "RightToes": "R_ToeBase",
	},
}

var _fps := 30.0
## 클립 키 → 상체 세우기 각도(도). --upright= 로 지정.
var _upright: Dictionary = {}
## 클립 키 → 전체 Y 회전(도). --yaw= 로 지정.
var _yaw: Dictionary = {}
## 루트 모션(힙 XZ 직선 이동)을 제거할 클립 키. 기본 = 루프 클립.
var _inplace: PackedStringArray = PackedStringArray(["idle", "walk", "run"])


func _init() -> void:
	var base := ""
	var out := ""
	var clips: Array = []
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--base="):
			base = a.get_slice("=", 1)
		elif a.begins_with("--out="):
			out = a.get_slice("=", 1)
		elif a.begins_with("--fps="):
			_fps = float(a.get_slice("=", 1))
		elif a.begins_with("--yaw="):
			for pair in a.get_slice("=", 1).split(",", false):
				if pair.contains(":"):
					_yaw[pair.get_slice(":", 0)] = float(pair.get_slice(":", 1))
		elif a.begins_with("--inplace="):
			_inplace = a.get_slice("=", 1).split(",", false)
		elif a.begins_with("--upright="):
			for pair in a.get_slice("=", 1).split(",", false):
				if pair.contains(":"):
					_upright[pair.get_slice(":", 0)] = float(pair.get_slice(":", 1))
		elif a.contains("=") and not a.begins_with("--"):
			var spec := a.substr(a.find("=") + 1)
			var speed := 1.0
			if spec.contains("@"):
				speed = float(spec.get_slice("@", 1))
				spec = spec.get_slice("@", 0)
			# Trial-only: select a named clip from the frozen current-game GLB.
			var source_clip := ""
			if spec.contains("#"):
				source_clip = spec.get_slice("#", 1)
				spec = spec.get_slice("#", 0)
			clips.append([a.get_slice("=", 0), spec, maxf(speed, 0.01), source_clip])
	if base == "" or out == "" or clips.is_empty():
		print("usage: godot --headless -s tools/retarget_mixamo.gd -- --base=<rigged.glb> --out=<out.glb> idle=<fbx> walk=<fbx> …")
		quit(1)
		return

	var scene := _load_any(base)
	if scene == null:
		quit(1)
		return
	var tsk := _find_skeleton(scene)
	if tsk == null:
		print("base에 Skeleton3D 없음")
		quit(1)
		return
	var tmap := _detect_map(tsk)
	if tmap.is_empty():
		print("base 리그 종류를 모름 (본: %s)" % _bone_names(tsk))
		quit(1)
		return
	var ap := _find_player(scene)
	var sk_path := ""
	if ap != null and ap.get_animation_list().size() > 0:
		var a0: Animation = ap.get_animation(ap.get_animation_list()[0])
		if a0.get_track_count() > 0:
			sk_path = a0.track_get_path(0).get_concatenated_names()
	if ap == null:
		ap = AnimationPlayer.new()
		ap.name = "AnimationPlayer"
		scene.add_child(ap)
		ap.owner = scene
	if sk_path == "":
		sk_path = str(scene.get_path_to(tsk))
	var lib: AnimationLibrary = ap.get_animation_library(ap.get_animation_library_list()[0]) if ap.get_animation_library_list().size() > 0 else null
	if lib == null:
		lib = AnimationLibrary.new()
		ap.add_animation_library("", lib)
	for n in lib.get_animation_list():
		lib.remove_animation(n)
	print("base %s: 리그=%s 본 %d, 트랙 경로 '%s'" % [base.get_file(), _map_name(tmap), tsk.get_bone_count(), sk_path])

	var ok := true
	for c in clips:
		var key: String = c[0]
		var src := _load_any(c[1])
		if src == null:
			ok = false
			continue
		var ssk := _find_skeleton(src)
		var sap := _find_player(src)
		if ssk == null or sap == null or sap.get_animation_list().is_empty():
			print("  ✗ %s: Skeleton3D/AnimationPlayer 없음 (%s)" % [key, c[1]])
			ok = false
			src.free()
			continue
		var smap := _detect_map(ssk)
		if smap.is_empty():
			print("  ✗ %s: 소스 리그 종류를 모름 (본: %s)" % [key, _bone_names(ssk)])
			ok = false
			src.free()
			continue
		var first: String = c[3] if c[3] != "" else sap.get_animation_list()[0]
		if not sap.has_animation(first):
			print("  ✗ %s: 지정 클립 없음 (%s)" % [key, first])
			ok = false
			src.free()
			continue
		var sanim: Animation = sap.get_animation(first)
		var speed: float = c[2]
		var anim := _retarget(sanim, ssk, smap, tsk, tmap, sk_path, speed, float(_upright.get(key, 0.0)), key in _inplace, float(_yaw.get(key, 0.0)))
		anim.loop_mode = Animation.LOOP_LINEAR if key in ["idle", "walk", "run"] else Animation.LOOP_NONE
		lib.add_animation(key, anim)
		print("  ✓ %-7s ← %s (%.2fs%s%s%s%s, 소스=%s, 트랙 %d)" % [key, first, anim.length, (" = %.2fs×%.1f" % [sanim.length, speed]) if speed != 1.0 else "", (" 상체 -%.0f°" % _upright[key]) if _upright.has(key) else "", (" 요 %+.0f°" % _yaw[key]) if _yaw.has(key) else "", " 제자리" if key in _inplace else "", _map_name(smap), anim.get_track_count()])
		src.free()

	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_scene(scene, state)
	if err != OK:
		print("append_from_scene 실패 %d" % err)
		quit(1)
		return
	var abs := ProjectSettings.globalize_path(out) if out.begins_with("res://") else out
	DirAccess.make_dir_recursive_absolute(abs.get_base_dir())
	err = doc.write_to_filesystem(state, abs)
	print("retargeted GLB → %s (%s) 클립: %s" % [abs, "OK" if err == OK else "ERR %d" % err, ", ".join(lib.get_animation_list())])
	scene.free()
	quit(0 if (err == OK and ok) else 1)


# ---------------------------------------------------------------- 리타겟 본체

func _retarget(sanim: Animation, ssk: Skeleton3D, smap: Dictionary, tsk: Skeleton3D, tmap: Dictionary, sk_path: String, speed: float = 1.0, upright_deg: float = 0.0, inplace: bool = false, yaw_deg: float = 0.0) -> Animation:
	# 1) 소스 트랙 → 본 인덱스
	var s_rot_track := {}   # bone idx -> track idx
	var s_pos_track := {}
	for t in sanim.get_track_count():
		var p := sanim.track_get_path(t)
		if p.get_subname_count() == 0:
			continue
		var bi := ssk.find_bone(p.get_subname(0))
		if bi < 0:
			continue
		match sanim.track_get_type(t):
			Animation.TYPE_ROTATION_3D: s_rot_track[bi] = t
			Animation.TYPE_POSITION_3D: s_pos_track[bi] = t

	# 2) 레스트 글로벌 (스켈레톤 공간)
	var s_rest := _global_rests(ssk)
	var t_rest := _global_rests(tsk)

	# 3) 프로필 본 → 인덱스
	var s_idx := {}
	var t_idx := {}
	for prof in smap:
		var i := _find_bone_any(ssk, smap[prof])
		if i >= 0:
			s_idx[prof] = i
	for prof in tmap:
		var i := _find_bone_any(tsk, tmap[prof])
		if i >= 0:
			t_idx[prof] = i
	var t_prof := {}  # target bone idx -> profile
	for prof in t_idx:
		if s_idx.has(prof):
			t_prof[t_idx[prof]] = prof

	# 4) 타깃 레스트를 소스 실루엣에 정렬 (top-down)
	var order := _topo_order(tsk)
	var aligned := {}  # bone idx -> Basis (global)
	for i in order:
		var par := tsk.get_bone_parent(i)
		var b: Basis = (aligned[par] * tsk.get_bone_rest(i).basis) if par >= 0 else tsk.get_bone_rest(i).basis
		if t_prof.has(i):
			var prof: String = t_prof[i]
			var cprof: String = PROFILE_CHILD.get(prof, "")
			if cprof != "" and t_idx.has(cprof) and s_idx.has(cprof):
				var ct: int = t_idx[cprof]
				var cs: int = s_idx[cprof]
				var d_t: Vector3 = (b * _rel_offset(tsk, i, ct)).normalized()
				var d_s: Vector3 = (s_rest[s_idx[prof]].basis * _rel_offset(ssk, s_idx[prof], cs)).normalized()
				if d_t.length() > 0.5 and d_s.length() > 0.5:
					b = Basis(Quaternion(d_t, d_s)) * b
		aligned[i] = b.orthonormalized()

	# 5) 힙 높이 비율 (스켈레톤 공간)
	var s_hip: int = s_idx.get("Hips", -1)
	var t_hip: int = t_idx.get("Hips", -1)
	# 상체 세우기: 첫 척추 본의 전역 회전에 X축(좌우축) 회전을 앞에 곱한다 → 자식(가슴·팔·머리)이 함께 젖혀지고 다리는 그대로
	# 상체 보정 기준 = 골반 바로 위의 척추 뼈(이름이 아니라 계층으로 찾는다 — Meshy 리그는 Spine02가 맨 아래, Spine이 맨 위로 이름이 거꾸로다, 실측)
	var t_spine: int = -1
	if t_hip >= 0:
		for i in tsk.get_bone_count():
			if tsk.get_bone_parent(i) == t_hip and tsk.get_bone_name(i).to_lower().contains("spine"):
				t_spine = i
				break
	if t_spine < 0:
		t_spine = t_idx.get("Spine", -1)
	var upright := Basis(Vector3.RIGHT, deg_to_rad(-upright_deg)) if (upright_deg != 0.0 and t_spine >= 0) else Basis.IDENTITY
	# 전체 Y 회전(몸통 정면 교정): 모든 본의 전역 회전과 힙 오프셋에 같은 회전을 곱한다 → 포즈가 통째로 돈다
	var yawB := Basis(Vector3.UP, deg_to_rad(yaw_deg)) if yaw_deg != 0.0 else Basis.IDENTITY
	# 척추와 그 자손(가슴·팔·머리) 전부의 전역 회전에 같은 보정을 곱해야 상체가 한 덩어리로 젖혀진다 — 본마다 소스 델타로 전역 회전을 따로 만들기 때문
	var upper := {}
	if upright_deg != 0.0 and t_spine >= 0:
		for i in order:
			var j: int = i
			while j >= 0:
				if j == t_spine:
					upper[i] = true
					break
				j = tsk.get_bone_parent(j)
	var k := 1.0
	if s_hip >= 0 and t_hip >= 0 and absf(s_rest[s_hip].origin.y) > 1e-4:
		k = t_rest[t_hip].origin.y / s_rest[s_hip].origin.y

	# 6) 프레임 샘플링
	var anim := Animation.new()
	anim.length = sanim.length / speed
	var tracks := {}  # target bone -> rot track
	for i in order:
		var tr := anim.add_track(Animation.TYPE_ROTATION_3D)
		anim.track_set_path(tr, NodePath("%s:%s" % [sk_path, tsk.get_bone_name(i)]))
		tracks[i] = tr
	var hip_track := -1
	if t_hip >= 0:
		hip_track = anim.add_track(Animation.TYPE_POSITION_3D)
		anim.track_set_path(hip_track, NodePath("%s:%s" % [sk_path, tsk.get_bone_name(t_hip)]))

	# 루트 모션 제거: 소스 힙의 처음→끝 XZ 이동을 시간 비례로 뺀다(상하 흔들림·좌우 흔들림은 남긴다)
	var drift := Vector3.ZERO
	if inplace and s_hip >= 0:
		var p0: Vector3 = _sample_globals(sanim, ssk, s_rot_track, s_pos_track, 0.0)[s_hip].origin
		var p1: Vector3 = _sample_globals(sanim, ssk, s_rot_track, s_pos_track, sanim.length)[s_hip].origin
		drift = Vector3(p1.x - p0.x, 0.0, p1.z - p0.z)
	var frames := int(ceil(sanim.length * _fps)) + 1
	for f in frames:
		var time := minf(f / _fps, sanim.length)  # 소스 시간
		var out_t := time / speed                  # 출력 시간(속도 배율)
		# 소스 포즈 글로벌
		var s_pose := _sample_globals(sanim, ssk, s_rot_track, s_pos_track, time)
		# 타깃 포즈 글로벌
		var t_pose := {}
		for i in order:
			var par := tsk.get_bone_parent(i)
			var par_xf: Transform3D = t_pose[par] if par >= 0 else Transform3D.IDENTITY
			var xf: Transform3D
			if t_prof.has(i):
				var si: int = s_idx[t_prof[i]]
				var delta: Basis = s_pose[si].basis * s_rest[si].basis.inverse()
				var gb: Basis = (yawB * delta * aligned[i]).orthonormalized()
				var origin: Vector3 = par_xf * tsk.get_bone_rest(i).origin
				if i == t_hip:
					var s_off: Vector3 = s_pose[si].origin - s_rest[si].origin - drift * (time / maxf(sanim.length, 1e-4))
					origin = t_rest[t_hip].origin + yawB * (s_off * k)
				xf = Transform3D(gb, origin)
			else:
				xf = par_xf * tsk.get_bone_rest(i)
			if upper.has(i):
				xf.basis = (upright * xf.basis).orthonormalized()
			t_pose[i] = xf
			var local_b: Basis = (par_xf.basis.inverse() * xf.basis).orthonormalized()
			anim.rotation_track_insert_key(tracks[i], out_t, local_b.get_rotation_quaternion())
			if i == t_hip and hip_track >= 0:
				anim.position_track_insert_key(hip_track, out_t, par_xf.affine_inverse() * xf.origin)
	return anim


func _sample_globals(anim: Animation, sk: Skeleton3D, rot_tracks: Dictionary, pos_tracks: Dictionary, time: float) -> Dictionary:
	var out := {}
	for i in _topo_order(sk):
		var rest := sk.get_bone_rest(i)
		var q: Quaternion = anim.rotation_track_interpolate(rot_tracks[i], time) if rot_tracks.has(i) else rest.basis.get_rotation_quaternion()
		var p: Vector3 = anim.position_track_interpolate(pos_tracks[i], time) if pos_tracks.has(i) else rest.origin
		var local := Transform3D(Basis(q), p)
		var par := sk.get_bone_parent(i)
		out[i] = (out[par] * local) if par >= 0 else local
	return out


func _global_rests(sk: Skeleton3D) -> Dictionary:
	var out := {}
	for i in _topo_order(sk):
		var par := sk.get_bone_parent(i)
		out[i] = (out[par] * sk.get_bone_rest(i)) if par >= 0 else sk.get_bone_rest(i)
	return out


## 자식 본이 직계가 아닐 수도 있어(트위스트 본 사이) 레스트 체인을 곱해 i 기준 오프셋을 구한다
func _rel_offset(sk: Skeleton3D, i: int, child: int) -> Vector3:
	var chain: Array = []
	var c := child
	while c >= 0 and c != i:
		chain.push_front(c)
		c = sk.get_bone_parent(c)
	if c != i:
		return Vector3.ZERO
	var xf := Transform3D.IDENTITY
	for b in chain:
		xf = xf * sk.get_bone_rest(b)
	return xf.origin


func _topo_order(sk: Skeleton3D) -> Array:
	var order: Array = []
	var stack: Array = sk.get_parentless_bones()
	stack.reverse()
	while not stack.is_empty():
		var i: int = stack.pop_back()
		order.append(i)
		var kids := sk.get_bone_children(i)
		kids.reverse()
		for kd in kids:
			stack.append(kd)
	return order


# ---------------------------------------------------------------- 리그 판별·로드

func _find_bone_any(sk: Skeleton3D, name: String) -> int:
	var i := sk.find_bone(name)
	if i >= 0:
		return i
	i = sk.find_bone("mixamorig:" + name)
	if i >= 0:
		return i
	i = sk.find_bone("mixamorig_" + name)
	return i


func _detect_map(sk: Skeleton3D) -> Dictionary:
	var best := {}
	var best_n := 0
	for fam in BONE_MAPS:
		var n := 0
		for prof in BONE_MAPS[fam]:
			if _find_bone_any(sk, BONE_MAPS[fam][prof]) >= 0:
				n += 1
		if n > best_n:
			best_n = n
			best = BONE_MAPS[fam]
	return best if best_n >= 12 else {}


func _map_name(m: Dictionary) -> String:
	for fam in BONE_MAPS:
		if BONE_MAPS[fam] == m:
			return fam
	return "?"


func _bone_names(sk: Skeleton3D) -> String:
	var names: Array = []
	for i in mini(sk.get_bone_count(), 12):
		names.append(sk.get_bone_name(i))
	return ", ".join(names)


func _load_any(path: String) -> Node:
	var abs := ProjectSettings.globalize_path(path) if path.begins_with("res://") else path
	if abs.get_extension().to_lower() == "fbx":
		var fdoc := FBXDocument.new()
		var fstate := FBXState.new()
		var ferr := fdoc.append_from_file(abs, fstate)
		if ferr != OK:
			print("FBX 읽기 실패 %d: %s" % [ferr, path])
			return null
		return fdoc.generate_scene(fstate)
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(abs, state)
	if err != OK:
		print("GLB 읽기 실패 %d: %s" % [err, path])
		return null
	return doc.generate_scene(state)


func _find_skeleton(n: Node) -> Skeleton3D:
	if n is Skeleton3D:
		return n
	for c in n.get_children():
		var r := _find_skeleton(c)
		if r:
			return r
	return null


func _find_player(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n
	for c in n.get_children():
		var r := _find_player(c)
		if r:
			return r
	return null
