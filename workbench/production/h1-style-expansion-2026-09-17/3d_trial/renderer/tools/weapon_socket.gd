extends SceneTree
## weapon_socket — 손아귀(주먹 원호 중심) 세계 좌표 → ModelDef.weapon_offset_pos / weapon_offset_rot_deg 계산.
##   godot --headless -s tools/weapon_socket.gd -- --model=<glb|res://…|id> [--report=<*_fist.json>] [--bone=RightHand] [--side=Right]
##   godot --headless -s tools/weapon_socket.gd -- --model=doho --grip=x,y,z --blade=x,y,z --width=x,y,z   (Godot 모델 공간, m)
## 입력: `tools/blender/rig_fix.py --fist`가 쓴 `<out>_fist.json`(Blender 좌표: z 위·-y 정면 → Godot (x, z, -y)로 바꿈).
##   grip = 검 원점(손아귀), blade = 칼끝 방향(+Y), width = 칼날 넓은 면의 가로축(+X). 임시 검·진짜 검 모두 이 축(§2.6).
## 왜 계산인가: 뷰어에서 눈대중으로 회전을 맞추면 칼이 손등·팔뚝 연장선에 붙기 쉽다(PD 지적). 주먹을 만든 스크립트가 손아귀 축을 알고 있으니
##   그 값을 손 본 rest 기준 로컬로 옮기면 어느 리그든 한 번에 맞는다. ActorVisual은 position = offset/chain_scale, rotation_degrees(YXZ), scale = 1/chain_scale.
const MC := preload("res://tools/model_check.gd")

func _init() -> void:
	var model := ""; var report := ""; var bone := "RightHand"; var side := "Right"
	var grip := Vector3.INF; var blade := Vector3.ZERO; var width := Vector3.ZERO
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--model="): model = a.get_slice("=", 1)
		elif a.begins_with("--report="): report = a.get_slice("=", 1)
		elif a.begins_with("--bone="): bone = a.get_slice("=", 1)
		elif a.begins_with("--side="): side = a.get_slice("=", 1)
		elif a.begins_with("--grip="): grip = _vec3(a.get_slice("=", 1))
		elif a.begins_with("--blade="): blade = _vec3(a.get_slice("=", 1))
		elif a.begins_with("--width="): width = _vec3(a.get_slice("=", 1))
	if model == "":
		printerr("--model= 필요"); quit(1); return
	if report != "":
		var f := FileAccess.open(report, FileAccess.READ)
		if f == null:
			printerr("보고 파일 없음: ", report); quit(1); return
		var j: Dictionary = JSON.parse_string(f.get_as_text())
		if not j.has(side):
			printerr("보고에 %s 없음" % side); quit(1); return
		var r: Dictionary = j[side]
		grip = _from_blender(_arr(r["grip"])); blade = _from_blender(_arr(r["blade_dir"])); width = _from_blender(_arr(r["width_dir"]))
	if grip == Vector3.INF or blade == Vector3.ZERO or width == Vector3.ZERO:
		printerr("--report= 또는 --grip/--blade/--width 필요"); quit(1); return
	var root: Node = MC.load_model(MC.resolve_path(model))
	if root == null:
		printerr("모델 로드 실패: ", model); quit(1); return
	var sks := root.find_children("*", "Skeleton3D", true, false)
	if sks.is_empty():
		printerr("Skeleton3D 없음"); quit(1); return
	var sk: Skeleton3D = sks[0]
	var bi := sk.find_bone(bone)
	if bi < 0:
		printerr("본 없음: ", bone); quit(1); return
	var t_sk: Transform3D = MC._transform_to(sk, root)
	var chain: float = t_sk.basis.get_scale().x                     # ActorVisual chain_scale (Meshy 0.01)
	var T: Transform3D = t_sk * sk.get_bone_global_rest(bi)          # 손 본 rest, 모델 공간(m)
	var local_cm: Vector3 = T.affine_inverse() * grip                # 본 공간(cm)
	var offset_pos: Vector3 = local_cm * chain
	var bw := Basis(width.normalized(), blade.normalized(), width.normalized().cross(blade.normalized())).orthonormalized()
	var bl := (T.basis.inverse() * bw).orthonormalized()
	var rot: Vector3 = bl.get_euler(EULER_ORDER_YXZ) * (180.0 / PI)
	# 검산: ActorVisual이 만들 노드 변환으로 세계 원점·칼끝 방향 복원
	var node := Transform3D(Basis.from_euler(rot * (PI / 180.0), EULER_ORDER_YXZ).scaled(Vector3.ONE / chain), offset_pos / chain)
	var world := T * node
	var err_pos := (world.origin - grip).length()
	var err_dir := rad_to_deg((world.basis.y.normalized()).angle_to(blade.normalized()))
	print("모델 %s  본 %s(#%d)  chain_scale %.4f" % [model, bone, bi, chain])
	print("손 본 rest 원점 = %s   손아귀 = %s   칼끝 방향 = %s" % [_fmt(T.origin), _fmt(grip), _fmt(blade.normalized())])
	print("weapon_offset_pos = Vector3(%.4f, %.4f, %.4f)" % [offset_pos.x, offset_pos.y, offset_pos.z])
	print("weapon_offset_rot_deg = Vector3(%.2f, %.2f, %.2f)" % [rot.x, rot.y, rot.z])
	print("검산: 원점 오차 %.4fm, 칼끝 각 오차 %.2f°" % [err_pos, err_dir])
	root.free()
	quit(0)

static func _vec3(s: String) -> Vector3:
	var p := s.split(",")
	return Vector3(float(p[0]), float(p[1]), float(p[2])) if p.size() == 3 else Vector3.ZERO

static func _arr(a) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))

## Blender(z 위, -y 정면) → Godot(y 위, +z 정면): (x, y, z) → (x, z, -y)
static func _from_blender(v: Vector3) -> Vector3:
	return Vector3(v.x, v.z, -v.y)

static func _fmt(v: Vector3) -> String:
	return "(%.3f, %.3f, %.3f)" % [v.x, v.y, v.z]
