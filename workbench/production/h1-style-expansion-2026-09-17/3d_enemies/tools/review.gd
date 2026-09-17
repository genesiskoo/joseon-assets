extends Node3D
## Independent, read-only input review. Missing models never become placeholders.

var model_path := ""
var output_dir := ""
var enemy_id := ""
var target_height := 1.5
var mode := "neutral"
var is_reference := false
var actor: Node3D
var camera: Camera3D
var report: Dictionary = {}

func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--model="): model_path = arg.trim_prefix("--model=")
		elif arg.begins_with("--output="): output_dir = arg.trim_prefix("--output=")
		elif arg.begins_with("--id="): enemy_id = arg.trim_prefix("--id=")
		elif arg.begins_with("--height="): target_height = float(arg.trim_prefix("--height="))
		elif arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
		elif arg == "--reference": is_reference = true
	if not FileAccess.file_exists(model_path) or output_dir == "" or enemy_id == "":
		push_error("Existing --model, explicit --id and --output are required.")
		get_tree().quit(2)
		return
	if mode not in ["neutral", "actual"]:
		push_error("Mode must be neutral or actual.")
		get_tree().quit(2)
		return
	DirAccess.make_dir_recursive_absolute(output_dir)
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var error := doc.append_from_file(model_path, state)
	if error != OK:
		push_error("GLTF load error %d: %s" % [error, model_path])
		get_tree().quit(2)
		return
	actor = doc.generate_scene(state) as Node3D
	add_child(actor)
	var bounds := model_bounds(actor)
	report = inspect_model(actor, bounds)
	# No normalization, culling repair, material override, or actor fill is hidden here.
	# A delivered candidate must already satisfy its requested geometry/material contract.
	_build_lighting()
	_build_camera(bounds)
	var hud := Label.new()
	hud.position = Vector2(20, 16)
	hud.add_theme_font_size_override("font_size", 18)
	hud.add_theme_constant_override("outline_size", 5)
	hud.text = ("HARNESS REFERENCE / NOT AN ENEMY RESULT" if is_reference else "H1 ENEMY CANDIDATE / NOT GAME INTAKE") + "\n" + enemy_id.to_upper() + " / " + mode.to_upper()
	hud.text += "\nSTATIC FORM AND MATERIAL CHECK; ANIMATION APPROVAL SEPARATE"
	hud.text += "\nORTHO %.3f / PITCH %.3f / YAW %.1f / 1280x720" % [camera.size, -camera.rotation_degrees.x, camera.rotation_degrees.y]
	var canvas := CanvasLayer.new()
	add_child(canvas)
	canvas.add_child(hud)
	call_deferred("capture")

func _build_lighting() -> void:
	var world := WorldEnvironment.new()
	if mode == "actual":
		world.environment = load("res://references/current_dungeon_environment.tres") as Environment
		var player_light := load("res://references/current_player_light.tscn") as PackedScene
		if player_light:
			var light := player_light.instantiate() as Node3D
			light.position += Vector3(1.0, 0.0, 1.0)
			add_child(light)
	else:
		var env := Environment.new()
		env.background_mode = Environment.BG_COLOR
		env.background_color = Color(0.14, 0.14, 0.14)
		env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
		env.ambient_light_color = Color.WHITE
		env.ambient_light_energy = 0.6
		world.environment = env
		var light := DirectionalLight3D.new()
		light.rotation_degrees = Vector3(-35.0, -30.0, 0.0)
		light.light_energy = 1.0
		add_child(light)
	add_child(world)
	# Geometry is a plain diagnostic ground, explicitly not an environment-kit result.
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(12.0, 12.0)
	ground.mesh = plane
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.11, 0.115, 0.13)
	material.metallic = 0.0
	material.roughness = 1.0
	ground.material_override = material
	ground.position.y = -0.01
	add_child(ground)

func _build_camera(bounds: AABB) -> void:
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 11.0 if mode == "actual" else maxf(bounds.size.y * 1.4, bounds.size.x * 0.85)
	camera.rotation_degrees = Vector3(-35.264, 45.0, 0.0) if mode == "actual" else Vector3(-8.0, 0.0, 0.0)
	add_child(camera)
	var focus := Vector3.ZERO if mode == "actual" else bounds.get_center()
	camera.position = focus + camera.global_transform.basis.z * 30.0
	camera.current = true

func model_bounds(root: Node3D) -> AABB:
	var bounds := AABB()
	var first := true
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		if mesh.mesh == null: continue
		var box: AABB = skinned_transform(mesh, root) * mesh.mesh.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
	return bounds

func transform_to(node: Node3D, top: Node) -> Transform3D:
	var result := Transform3D.IDENTITY
	var current: Node = node
	while current != null and current != top:
		if current is Node3D: result = (current as Node3D).transform * result
		current = current.get_parent()
	return (top as Node3D).transform * result if top is Node3D else result

func skinned_transform(mesh: MeshInstance3D, top: Node) -> Transform3D:
	if mesh.skin == null or mesh.skin.get_bind_count() == 0: return transform_to(mesh, top)
	var skeleton := mesh.get_parent() as Skeleton3D
	if skeleton == null:
		var found := top.find_children("*", "Skeleton3D", true, false)
		if found.is_empty(): return transform_to(mesh, top)
		skeleton = found[0] as Skeleton3D
	var bone := mesh.skin.get_bind_bone(0)
	if bone < 0: bone = skeleton.find_bone(mesh.skin.get_bind_name(0))
	if bone < 0 or bone >= skeleton.get_bone_count(): return transform_to(mesh, top)
	return transform_to(skeleton, top) * skeleton.get_bone_global_rest(bone) * mesh.skin.get_bind_pose(0)

func inspect_model(root: Node3D, bounds: AABB) -> Dictionary:
	var triangles := 0
	var materials: Array[Dictionary] = []
	var texture_ok := true
	var matte_ok := true
	var has_albedo := false
	var uv_ok := true
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var instance := node as MeshInstance3D
		if instance.mesh == null: continue
		for surface in instance.mesh.get_surface_count():
			var arrays := instance.mesh.surface_get_arrays(surface)
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			triangles += int((indices.size() if not indices.is_empty() else vertices.size()) / 3)
			var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV] if arrays[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
			uv_ok = uv_ok and uv.size() == vertices.size()
			var mat := instance.get_active_material(surface) as StandardMaterial3D
			if mat:
				var texture := mat.albedo_texture
				has_albedo = has_albedo or texture != null
				var dimensions := [texture.get_width(), texture.get_height()] if texture else []
				texture_ok = texture_ok and (texture == null or (texture.get_width() <= 1024 and texture.get_height() <= 1024))
				matte_ok = matte_ok and mat.metallic <= 0.01 and mat.roughness >= 0.8
				materials.append({"name": mat.resource_name, "albedo_size": dimensions, "metallic": mat.metallic, "roughness": mat.roughness, "emission_enabled": mat.emission_enabled, "cull_mode": mat.cull_mode})
	var bones := 0
	for skeleton in root.find_children("*", "Skeleton3D", true, false): bones += (skeleton as Skeleton3D).get_bone_count()
	var clips: Array[Dictionary] = []
	for animation_player in root.find_children("*", "AnimationPlayer", true, false):
		var player := animation_player as AnimationPlayer
		for clip in player.get_animation_list(): clips.append({"name": clip, "seconds": player.get_animation(clip).length})
	var geometry_checks := {"triangle_budget": triangles <= 8000, "height": absf(bounds.size.y - target_height) <= target_height * 0.02, "bottom_y_zero": absf(bounds.position.y) <= 0.01, "horizontal_center": Vector2(bounds.get_center().x, bounds.get_center().z).length() <= 0.05, "albedo_1k": texture_ok and has_albedo, "matte_material": matte_ok, "uv_present": uv_ok}
	if enemy_id == "bat": geometry_checks["wingspan_1_2m"] = absf(bounds.size.x - 1.2) <= 0.06
	geometry_checks["images_embedded_in_glb"] = embedded_images_check()
	return {"id": enemy_id, "source": model_path, "sha256": FileAccess.get_sha256(model_path), "is_reference": is_reference, "is_game_intake": false, "is_game_ready": false, "triangles": triangles, "target_height": target_height, "bounds": {"size": [bounds.size.x,bounds.size.y,bounds.size.z], "position": [bounds.position.x,bounds.position.y,bounds.position.z]}, "bones": bones, "clips": clips, "materials": materials, "contract_checks": geometry_checks, "front_axis": "unverified visually; required +Z", "animation_gate": "not evaluated by static renderer", "visual_qa": "pending direct image inspection"}

func embedded_images_check() -> bool:
	var file := FileAccess.open(model_path, FileAccess.READ)
	if file == null or file.get_length() < 20: return false
	if file.get_32() != 0x46546C67 or file.get_32() != 2: return false
	file.get_32()
	var chunk_length := file.get_32()
	if file.get_32() != 0x4E4F534A or chunk_length > file.get_length() - 20: return false
	var data = JSON.parse_string(file.get_buffer(chunk_length).get_string_from_utf8())
	file.close()
	if not data is Dictionary or not data.has("images") or data.images.is_empty(): return false
	for entry in data.images:
		if not entry.has("bufferView") or entry.has("uri"): return false
	return true

func capture() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var picture := get_viewport().get_texture().get_image()
	var image_path := output_dir.path_join(mode + ".png")
	var error := picture.save_png(image_path)
	if error != OK:
		push_error("PNG write error %d: %s" % [error,image_path])
		get_tree().quit(2)
		return
	report["captured_at_utc"] = Time.get_datetime_string_from_system(true)
	report["camera"] = {"mode": mode,"ortho": camera.size,"pitch": -camera.rotation_degrees.x,"yaw": camera.rotation_degrees.y,"viewport": [1280,720]}
	report["lighting"] = "Exact saved dungeon environment and player light, player offset (1,0,1); plain diagnostic floor, no torch" if mode == "actual" else "Neutral white ambient 0.6 and directional 1.0; plain diagnostic floor"
	report["render"] = {"path": image_path,"sha256": FileAccess.get_sha256(image_path)}
	var file := FileAccess.open(output_dir.path_join(mode + "_contract.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t") + "\n")
	file.close()
	print("[Enemy review] %s %s | triangles=%d | bones=%d | %s" % [enemy_id,mode,report.triangles,report.bones,image_path])
	get_tree().quit(0)
