extends SceneTree
## model_check — GLB 반입 검수 (design/art_3d_pipeline.md §5.3).
##   godot --headless -s tools/model_check.gd -- <경로|id> [--height=1.7] [--kind=actor|tile]
## 경로: res://… (임포트된 것) 또는 파일시스템 경로(GLTFDocument로 직접 읽음 — 복사 전 검사 가능). id는 assets/models/<id>/<id>.glb.
## 출력: 노드·본·클립(이름·길이)·동작 매핑·AABB(키·발 높이)·삼각형·텍스처. 마지막 줄 RESULT PASS|WARN|FAIL. FAIL = 종료 코드 1.
## 왜 별도 스크립트인가: 뷰어(눈)와 달리 숫자로 판정해 intake_model.ps1·CI가 같은 규칙을 쓴다. 매핑 규칙은 ActorVisual.resolve_anim 그대로.

const TRI_WARN := 12000
const HEIGHT_TOL := 0.15


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	var target := ""
	var height := 0.0
	var kind := "actor"
	for a in args:
		if a.begins_with("--height="):
			height = float(a.get_slice("=", 1))
		elif a.begins_with("--kind="):
			kind = a.get_slice("=", 1)
		elif not a.begins_with("--"):
			target = a
	if target == "":
		print("usage: godot --headless -s tools/model_check.gd -- <res://path|id|C:/path.glb> [--height=1.7] [--kind=actor|tile]")
		quit(1)
		return
	var path := resolve_path(target)
	print("== model_check %s" % path)
	var warns: PackedStringArray = []
	var node := load_model(path)
	if node == null:
		print("FAIL: 파일을 열 수 없음 (%s). res:// 경로면 `godot --headless --import` 먼저." % path)
		print("RESULT FAIL")
		quit(1)
		return
	# (_init 시점엔 트리가 아직 없어 global_transform을 못 쓴다 → 부모 체인을 직접 곱한다)
	# 노드
	var meshes := node.find_children("*", "MeshInstance3D", true, false)
	var skels := node.find_children("*", "Skeleton3D", true, false)
	var anims := node.find_children("*", "AnimationPlayer", true, false)
	print("노드: MeshInstance3D %d · Skeleton3D %d · AnimationPlayer %d" % [meshes.size(), skels.size(), anims.size()])
	# 본
	for sk in skels:
		var names: PackedStringArray = []
		for i in mini((sk as Skeleton3D).get_bone_count(), 6):
			names.append((sk as Skeleton3D).get_bone_name(i))
		print("본 %d: %s%s" % [(sk as Skeleton3D).get_bone_count(), ", ".join(names), "…" if (sk as Skeleton3D).get_bone_count() > 6 else ""])
	# 메시·AABB·텍스처
	var tris := 0
	var aabb := AABB()
	var first := true
	var tex_lines: PackedStringArray = []
	for m in meshes:
		var mi := m as MeshInstance3D
		if mi.mesh == null:
			continue
		var box: AABB = _skinned_transform(mi, node) * mi.mesh.get_aabb()
		aabb = box if first else aabb.merge(box)
		first = false
		for s in mi.mesh.get_surface_count():
			var arrays := mi.mesh.surface_get_arrays(s)
			var idx: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX] if arrays[Mesh.ARRAY_VERTEX] != null else PackedVector3Array()
			tris += (idx.size() if idx.size() > 0 else verts.size()) / 3
			var mat := mi.mesh.surface_get_material(s) as BaseMaterial3D
			if mat and mat.albedo_texture:
				tex_lines.append("%s %dx%d" % [mat.albedo_texture.resource_name if mat.albedo_texture.resource_name != "" else "albedo", mat.albedo_texture.get_width(), mat.albedo_texture.get_height()])
	print("삼각형 %d%s" % [tris, "  ⚠ %d 초과 → remesh 권장" % TRI_WARN if tris > TRI_WARN else ""])
	if tris > TRI_WARN:
		warns.append("폴리 과다")
	if first:
		print("⚠ 메시 없음")
		warns.append("메시 없음")
	else:
		print("AABB: 키 %.2f · 너비 %.2f · 깊이 %.2f · 발 y=%.2f · 중심 x=%.2f z=%.2f" % [aabb.size.y, aabb.size.x, aabb.size.z, aabb.position.y, aabb.get_center().x, aabb.get_center().z])
		if height > 0.0 and absf(aabb.size.y - height) > height * HEIGHT_TOL:
			print("⚠ 키 %.2f ≠ 목표 %.2f (±%d%%) → ModelDef.scale = %.3f 권장" % [aabb.size.y, height, int(HEIGHT_TOL * 100), height / maxf(aabb.size.y, 0.001)])
			warns.append("키 불일치")
		var floor_tile := kind == "tile" and absf(aabb.end.y) < 0.01   # 바닥 타일 = 윗면 y=0, 두께는 아래로(§2.5)
		if absf(aabb.position.y) > 0.1 and not floor_tile:
			print("⚠ 발이 y=0에서 %.2f 떨어짐 → ModelDef.y_offset = %.2f 권장" % [aabb.position.y, -aabb.position.y])
			warns.append("발 높이")
		if Vector2(aabb.get_center().x, aabb.get_center().z).length() > 0.3:
			print("⚠ 원점이 중앙에서 벗어남 (x=%.2f z=%.2f)" % [aabb.get_center().x, aabb.get_center().z])
			warns.append("원점 치우침")
	print("텍스처: %s" % (", ".join(tex_lines) if not tex_lines.is_empty() else "없음(단색)"))
	# 애니
	if kind == "actor":
		if anims.is_empty():
			print("⚠ AnimationPlayer 없음 — 정적 모델로 표시됨")
			warns.append("애니 없음")
		else:
			var ap := anims[0] as AnimationPlayer
			var names := ap.get_animation_list()
			var lines: PackedStringArray = []
			for n in names:
				lines.append("%s(%.2fs)" % [n, ap.get_animation(n).length])
			print("클립 %d: %s" % [names.size(), ", ".join(lines)])
			for k in ["idle", "walk", "attack", "hit", "die"]:
				var r := ActorVisual.resolve_anim(names, k, k)
				print("  %-6s → %s" % [k, r if r != "" else "(없음)"])
				if r == "" and (k == "idle" or k == "walk"):
					warns.append("%s 클립 없음" % k)
			# 타격 프레임 (combat_v2 §6): 공격 클립마다 오른손 속도 피크 시각 → ModelDef.attack_impact에 적을 값
			var sk_for_impact := (skels[0] as Skeleton3D) if not skels.is_empty() else null
			if sk_for_impact and sk_for_impact.find_bone("RightHand") >= 0:
				var added := false
				if not node.is_inside_tree():
					get_root().add_child(node)
					added = true
				var impacts: PackedStringArray = []
				for n in names:
					if n.to_lower().begins_with("attack"):
						impacts.append('"%s": %.2f' % [n, impact_frac(ap, sk_for_impact, n)])
				if not impacts.is_empty():
					print("  타격 프레임(오른손 속도 피크) → attack_impact = {%s}" % ", ".join(impacts))
				if added:
					get_root().remove_child(node)
	node.free()
	if warns.is_empty():
		print("RESULT PASS")
	else:
		print("RESULT WARN: %s" % ", ".join(warns))
	quit(0)


## 스킨 메시의 렌더 변환. 스킨이 있으면 메시 노드의 transform은 무시되고(glTF 규격)
## 정점 = 스켈레톤 전역 × 본 전역 rest × 바인드 역행렬 × v 이므로, 첫 바인드로 그 곱을 만든다.
## (Meshy 리그 = Armature scale 0.01 + 본 cm 단위 → 메시 transform만 곱하면 키가 0.02로 나온다, 실측.)
static func _skinned_transform(mi: MeshInstance3D, top: Node) -> Transform3D:
	if mi.skin == null or mi.skin.get_bind_count() == 0:
		return _transform_to(mi, top)
	var sk: Skeleton3D = mi.get_parent() as Skeleton3D
	if sk == null:
		var found := top.find_children("*", "Skeleton3D", true, false)
		if found.is_empty():
			return _transform_to(mi, top)
		sk = found[0] as Skeleton3D
	var bi := mi.skin.get_bind_bone(0)
	if bi < 0:
		bi = sk.find_bone(mi.skin.get_bind_name(0))
	if bi < 0 or bi >= sk.get_bone_count():
		return _transform_to(mi, top)
	return _transform_to(sk, top) * sk.get_bone_global_rest(bi) * mi.skin.get_bind_pose(0)


## n의 변환을 top(모델 루트)까지 누적 — 트리 밖에서도 되는 global_transform.
static func _transform_to(n: Node3D, top: Node) -> Transform3D:
	var t := Transform3D.IDENTITY
	var cur: Node = n
	while cur != null and cur != top:
		if cur is Node3D:
			t = (cur as Node3D).transform * t
		cur = cur.get_parent()
	if top is Node3D:
		t = (top as Node3D).transform * t
	return t


static func resolve_path(target: String) -> String:
	if target.begins_with("res://") or target.begins_with("user://"):
		return target
	if target.contains(":/") or target.contains(":\\") or target.begins_with("/") or target.ends_with(".glb") or target.ends_with(".gltf"):
		return target.replace("\\", "/")
	# id: "doho" → assets/models/doho/doho.glb, "tilekit_stone/floor" → assets/models/tilekit_stone/floor.glb
	if target.contains("/"):
		return "res://assets/models/%s.glb" % target
	return "res://assets/models/%s/%s.glb" % [target, target]


## res:// = 임포트된 PackedScene. 그 외 = GLTFDocument로 파일 직접 읽기(임포트 불필요).
static func load_model(path: String) -> Node:
	if path.begins_with("res://"):
		if not ResourceLoader.exists(path):
			return null
		var ps := load(path) as PackedScene
		return ps.instantiate() if ps else null
	if not FileAccess.file_exists(path):
		return null
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(path, state)
	if err != OK:
		return null
	return doc.generate_scene(state)


## 공격 클립의 타격 시각 비율: RightHand 본의 스켈레톤 공간 속도가 최대인 시각(클립 15~85% 구간). 헤드리스에선 global pose가 지연 갱신되므로
## seek(update=true)가 바로 쓰는 로컬 포즈를 부모 체인으로 직접 곱한다. 찌르기처럼 피크가 둘이면(당김·찌름) 값을 눈으로 보정한다.
static func impact_frac(ap: AnimationPlayer, sk: Skeleton3D, clip: String) -> float:
	var hb := sk.find_bone("RightHand")
	var L := ap.get_animation(clip).length
	if hb < 0 or L <= 0.0:
		return 0.45
	var dt := 1.0 / 60.0
	var prev := Vector3.ZERO
	var best_t := L * 0.45
	var best_v := 0.0
	ap.play(clip)
	var t := 0.0
	while t <= L + 0.0001:
		ap.seek(t, true)
		var xf := Transform3D()
		var i := hb
		while i >= 0:
			xf = Transform3D(Basis(sk.get_bone_pose_rotation(i)).scaled(sk.get_bone_pose_scale(i)), sk.get_bone_pose_position(i)) * xf
			i = sk.get_bone_parent(i)
		if t > 0.0:
			var v := (xf.origin - prev).length() / dt
			var frac := t / L
			if frac > 0.15 and frac < 0.85 and v > best_v:
				best_v = v
				best_t = t
		prev = xf.origin
		t += dt
	ap.stop()
	return best_t / L
