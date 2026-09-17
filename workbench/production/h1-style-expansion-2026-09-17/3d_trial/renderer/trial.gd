extends Node3D
## Isolated art trial: copied production renderer helpers + external GLB candidates.
## No gameplay autoloads, save files, editor integration, or main-project mutation.

const CAMERA_SCRIPT = preload("res://world/iso_camera.gd")
const TORCH_SCRIPT = preload("res://world/torch.gd")
const VISUAL_SCRIPT = preload("res://actors/actor_visual.gd")
const MODEL_SCRIPT = preload("res://actors/model_def.gd")
const CHECK_SCRIPT = preload("res://tools/model_check.gd")
const TILE_ROOT := "res://assets/models/tilekit_stone/"
const DEFAULT_MODELS := "C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/"
const SCREEN_RIGHT := Vector3(0.70710678, 0.0, -0.70710678)

var mode := "assembly_reference"
var doho_path := DEFAULT_MODELS + "H1_doho.glb"
var merchant_path := DEFAULT_MODELS + "H1_merchant.glb"
var shots_dir := ""
var sword_proxy := false
var socket_file := ""
var socket_data: Dictionary = {}
var grip_closeup := false
var tiles_two_sided := false
var tiles_flip_winding := false
var diagnostic := ""
var camera_size := 11.0
var camera_pitch := 35.264
var camera_yaw := 45.0
var pc_matte := false
var pc_fill := false
var camera: Camera3D
var hud: Label
var slots: Array[Dictionary] = []
var captures: Array[Dictionary] = []
var tile_records: Array[Dictionary] = []
var load_failures: PackedStringArray = []


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mode="):
			mode = arg.trim_prefix("--mode=")
		elif arg.begins_with("--doho="):
			doho_path = arg.trim_prefix("--doho=").replace("\\", "/")
		elif arg.begins_with("--merchant="):
			merchant_path = arg.trim_prefix("--merchant=").replace("\\", "/")
		elif arg.begins_with("--shots="):
			shots_dir = arg.trim_prefix("--shots=").replace("\\", "/")
		elif arg == "--sword-proxy":
			sword_proxy = true
		elif arg.begins_with("--socket="):
			socket_file = arg.trim_prefix("--socket=").replace("\\", "/")
		elif arg == "--grip-closeup":
			grip_closeup = true
		elif arg == "--tiles-two-sided":
			tiles_two_sided = true
		elif arg == "--tiles-flip-winding":
			tiles_flip_winding = true
		elif arg.begins_with("--diagnostic="):
			diagnostic = arg.trim_prefix("--diagnostic=")
		elif arg == "--pc-matte":
			pc_matte = true
		elif arg == "--pc-fill":
			pc_fill = true
	if socket_file == "" and mode == "h1_trial" and sword_proxy and doho_path == DEFAULT_MODELS + "H1_doho.glb":
		socket_file = DEFAULT_MODELS + "fist/H1_doho_socket.json"
	if socket_file != "":
		var socket_json = JSON.parse_string(FileAccess.get_file_as_string(socket_file))
		if socket_json is Dictionary:
			socket_data = socket_json
		else:
			load_failures.append("Invalid socket JSON: " + socket_file)
	if grip_closeup:
		diagnostic = "neutral"
	if shots_dir == "":
		shots_dir = ProjectSettings.globalize_path("res://captures/" + mode)
	DirAccess.make_dir_recursive_absolute(shots_dir)
	_build_environment()
	if diagnostic == "":
		_build_tiles()
	_build_camera()
	_build_hud()
	if mode == "assembly_reference":
		doho_path = ProjectSettings.globalize_path("res://references/CURRENT_REFERENCE_NOT_H1.glb")
		merchant_path = ""
	_add_actor("doho", doho_path, 1.7, -1.3)
	_add_actor("merchant", merchant_path, 1.6, 1.3)
	var actual_light := load("res://references/current_player_light.tscn") as PackedScene
	if diagnostic == "" and actual_light and not slots.is_empty():
		(slots[0].visual as Node3D).add_child(actual_light.instantiate())
	if pc_fill and not slots.is_empty():
		var fill := OmniLight3D.new()
		fill.name = "PCOnlyFillCandidate"
		fill.position = (slots[0].visual as Node3D).position + Vector3(0.75, 1.8, 0.75)
		fill.light_color = Color(0.88, 0.93, 1.0)
		fill.light_energy = 0.65
		fill.omni_range = 3.0
		fill.light_cull_mask = 2
		add_child(fill)
	call_deferred("_capture_sequence")


func _build_environment() -> void:
	var world := WorldEnvironment.new()
	if diagnostic != "":
		var env := Environment.new()
		env.background_mode = Environment.BG_COLOR
		env.background_color = Color(0.12, 0.12, 0.12)
		env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
		env.ambient_light_color = Color.WHITE
		env.ambient_light_energy = 0.6
		world.environment = env
		add_child(world)
		var key := DirectionalLight3D.new()
		key.rotation_degrees = Vector3(-30.0, -35.0, 0.0)
		key.light_energy = 1.0
		add_child(key)
		return
	world.environment = load("res://references/current_dungeon_environment.tres") as Environment
	add_child(world)
	# Production torch node/material/light, arranged in this isolated room.
	for x in [-2.5, 2.5]:
		var torch: Node3D = TORCH_SCRIPT.new()
		torch.position = Vector3(x, 1.35, -3.92)
		torch.set("seed_offset", x * 4.0)
		add_child(torch)


func load_GLTF(file_path: String) -> Node3D:
	if file_path == "" or not FileAccess.file_exists(file_path):
		return null
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var err := document.append_from_file(file_path, state)
	if err != OK:
		load_failures.append("GLTF error %d: %s" % [err, file_path])
		return null
	return document.generate_scene(state) as Node3D


func _tile_scene(kind: String) -> PackedScene:
	var source := TILE_ROOT + kind + ".glb"
	var packed := load(source) as PackedScene
	if packed == null:
		load_failures.append("Tile unavailable: " + source)
	else:
		tile_records.append({"id": kind, "source": source, "sha256": FileAccess.get_sha256(source)})
	return packed


func _build_tiles() -> void:
	var floor_scene := _tile_scene("floor")
	var wall_scene := _tile_scene("wall")
	var up_scene := _tile_scene("stairs_up")
	var down_scene := _tile_scene("stairs_down")
	var geometry := Node3D.new()
	geometry.name = "ReusedProductionStoneKit"
	add_child(geometry)
	if floor_scene:
		var floor_positions: Array[Vector3] = []
		for z in range(-4, 5):
			for x in range(-4, 5):
				floor_positions.append(Vector3(x, 0.0, z))
		geometry.add_child(_tile_batch(floor_scene, floor_positions))
	if wall_scene:
		var wall_positions: Array[Vector3] = []
		for i in range(-4, 5):
			for pos in [Vector3(i, 0.0, -4.5), Vector3(-4.5, 0.0, i)]:
				wall_positions.append(pos)
		geometry.add_child(_tile_batch(wall_scene, wall_positions))
	if up_scene:
		var up := up_scene.instantiate() as Node3D
		up.position = Vector3(-2.5, 0.0, -3.0)
		geometry.add_child(up)
	if down_scene:
		var down := down_scene.instantiate() as Node3D
		down.position = Vector3(2.5, 0.0, -3.0)
		geometry.add_child(down)


func _tile_batch(scene: PackedScene, positions: Array[Vector3]) -> MultiMeshInstance3D:
	# Production DungeonBuilder uses MultiMesh and the first imported mesh.
	var source := scene.instantiate() as Node3D
	var found := source.find_children("*", "MeshInstance3D", true, false)
	var mesh := (found[0] as MeshInstance3D).mesh
	if tiles_flip_winding:
		mesh = _flipped_winding_mesh(mesh)
	var batch := MultiMesh.new()
	batch.transform_format = MultiMesh.TRANSFORM_3D
	batch.use_colors = true
	batch.mesh = mesh
	batch.instance_count = positions.size()
	for i in positions.size():
		batch.set_instance_transform(i, Transform3D(Basis.IDENTITY, positions[i]))
		batch.set_instance_color(i, Color(0.94, 0.94, 0.94))
	var instance := MultiMeshInstance3D.new()
	instance.multimesh = batch
	var material := mesh.surface_get_material(0) as StandardMaterial3D
	if material:
		var copied := material.duplicate() as StandardMaterial3D
		copied.vertex_color_use_as_albedo = true
		if tiles_two_sided:
			copied.cull_mode = BaseMaterial3D.CULL_DISABLED
		instance.material_override = copied
	source.free()
	return instance


func _flipped_winding_mesh(source: Mesh) -> ArrayMesh:
	var result := ArrayMesh.new()
	for surface in source.get_surface_count():
		var arrays := source.surface_get_arrays(surface)
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
		if indices.is_empty():
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			for index in vertices.size():
				indices.append(index)
		for index in range(0, indices.size(), 3):
			var swap := indices[index + 1]
			indices[index + 1] = indices[index + 2]
			indices[index + 2] = swap
		arrays[Mesh.ARRAY_INDEX] = indices
		result.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		result.surface_set_material(surface, source.surface_get_material(surface))
	return result


func _build_camera() -> void:
	var focus := Node3D.new()
	focus.name = "Focus"
	if diagnostic != "":
		focus.position.y = 0.85
		camera_size = 3.3
		camera_pitch = 10.0
	if grip_closeup:
		camera_size = 0.5
		camera_pitch = rad_to_deg(atan2(0.9, sqrt(1.6 * 1.6 * 2.0)))
	add_child(focus)
	camera = Camera3D.new()
	camera.name = "ActualGameCamera"
	camera.set_script(CAMERA_SCRIPT)
	camera.set("target_path", focus.get_path())
	camera.set("ortho_size", camera_size)
	camera.set("pitch_deg", camera_pitch)
	camera.set("yaw_deg", camera_yaw)
	camera.set("distance", 30.0)
	add_child(camera)
	camera.current = true


func _build_hud() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	hud = Label.new()
	hud.position = Vector2(20, 16)
	hud.add_theme_font_size_override("font_size", 17)
	hud.add_theme_color_override("font_color", Color(0.95, 0.9, 0.8))
	hud.add_theme_color_override("font_outline_color", Color(0.02, 0.02, 0.025))
	hud.add_theme_constant_override("outline_size", 5)
	canvas.add_child(hud)


func _add_actor(id: String, source: String, target_height: float, offset: float) -> void:
	var visual: Node3D = VISUAL_SCRIPT.new()
	visual.name = id
	visual.position = SCREEN_RIGHT * offset
	visual.rotation_degrees.y = 45.0
	add_child(visual)
	var def: Resource = MODEL_SCRIPT.new()
	if id == "doho" and mode == "assembly_reference":
		def = (load("res://references/current_doho.tres") as Resource).duplicate(true)
	def.set("id", id)
	def.set("scene_path", source)
	def.set("target_height", target_height)
	def.set("weapon_placeholder", sword_proxy and id == "doho")
	if sword_proxy and mode != "assembly_reference" and id == "doho":
		if socket_data.has("weapon_offset_pos") and socket_data.has("weapon_offset_rot_deg"):
			var pos: Array = socket_data.weapon_offset_pos
			var rot: Array = socket_data.weapon_offset_rot_deg
			def.set("weapon_offset_pos", Vector3(pos[0], pos[1], pos[2]))
			def.set("weapon_offset_rot_deg", Vector3(rot[0], rot[1], rot[2]))
		else:
			# Historical pre-fist baseline only; new H1 fist runs pass measured --socket.
			def.set("weapon_offset_pos", Vector3(0.0093, 0.0832, 0.0361))
			def.set("weapon_offset_rot_deg", Vector3(-0.96, 179.24, 90.07))
	var root := load_GLTF(source)
	var entry: Dictionary = {"id": id, "source": source, "target_height": target_height, "visual": visual, "base_position": visual.position, "loaded": root != null, "placeholder": root == null, "clips": [], "source_sha256": "", "raw_height": 0.0, "scale": 1.0}
	if root:
		entry.source_sha256 = FileAccess.get_sha256(source)
		if id == "doho" and (pc_matte or pc_fill):
			for mesh in root.find_children("*", "MeshInstance3D", true, false):
				var instance := mesh as MeshInstance3D
				if pc_fill:
					instance.layers = 3
				if pc_matte:
					for surface in instance.mesh.get_surface_count():
						var material := instance.mesh.surface_get_material(surface) as StandardMaterial3D
						if material:
							var copied := material.duplicate() as StandardMaterial3D
							copied.metallic = 0.0
							copied.roughness = 0.8
							instance.set_surface_override_material(surface, copied)
		if diagnostic in ["unshaded", "solid", "nearest"]:
			for mesh in root.find_children("*", "MeshInstance3D", true, false):
				var instance := mesh as MeshInstance3D
				for surface in instance.mesh.get_surface_count():
					var material := instance.mesh.surface_get_material(surface) as StandardMaterial3D
					if material:
						var copied := material.duplicate() as StandardMaterial3D
						if diagnostic in ["unshaded", "nearest"]:
							copied.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
						if diagnostic == "solid":
							copied.albedo_texture = null
							copied.albedo_color = Color(0.7, 0.7, 0.7)
						if diagnostic == "nearest":
							copied.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
						instance.set_surface_override_material(surface, copied)
		var bounds := _model_bounds(root)
		entry.raw_height = bounds.size.y
		if bounds.size.y > 0.001:
			var normalize_scale := target_height / bounds.size.y
			def.set("scale", normalize_scale)
			def.set("y_offset", -bounds.position.y * normalize_scale)
			entry.scale = normalize_scale
		entry.triangles = _triangles(root)
		visual.call("apply_node", root, def)
		entry.clips = Array(visual.call("clip_names"))
		entry.runtime_total_triangles = _triangles(root)
		entry.bones = 0
		for skeleton in root.find_children("*", "Skeleton3D", true, false):
			entry.bones += (skeleton as Skeleton3D).get_bone_count()
	else:
		var dummy := MeshInstance3D.new()
		var cap := CapsuleMesh.new()
		cap.radius = 0.23
		cap.height = target_height
		dummy.mesh = cap
		dummy.position.y = target_height * 0.5
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.34, 0.35, 0.37)
		mat.roughness = 1.0
		dummy.material_override = mat
		visual.add_child(dummy)
		if mode == "h1_trial":
			load_failures.append("Missing H1 model: " + id)
	var label := Label3D.new()
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 28
	label.pixel_size = 0.003
	label.outline_size = 7
	label.position = visual.position + Vector3(0, target_height + 0.25, 0)
	label.text = ("CURRENT REFERENCE / NOT H1" if mode == "assembly_reference" and id == "doho" else id.to_upper()) + (" / MISSING" if root == null else "")
	add_child(label)
	entry.label_node = label
	slots.append(entry)


func _model_bounds(root: Node3D) -> AABB:
	var bounds := AABB()
	var first := true
	var meshes: Array[Node] = root.find_children("*", "MeshInstance3D", true, false)
	if root is MeshInstance3D:
		meshes.append(root)
	for node in meshes:
		var mesh := node as MeshInstance3D
		if mesh.mesh == null:
			continue
		var box: AABB = CHECK_SCRIPT._skinned_transform(mesh, root) * mesh.mesh.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
	return bounds


func _triangles(root: Node3D) -> int:
	var count := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var instance := node as MeshInstance3D
		if instance.mesh == null:
			continue
		for surface in instance.mesh.get_surface_count():
			var arrays := instance.mesh.surface_get_arrays(surface)
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX] if arrays[Mesh.ARRAY_VERTEX] != null else PackedVector3Array()
			count += int((indices.size() if indices.size() > 0 else vertices.size()) / 3)
	return count


func _pose(slot: Dictionary, action: String, phase: float) -> Dictionary:
	var visual := slot.visual as Node3D
	var players := visual.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		return {"requested": action, "clip": "", "available": false}
	var player := players[0] as AnimationPlayer
	var clip: String = visual.call("clip_for", action)
	if clip == "" or not player.has_animation(clip):
		player.pause()
		return {"requested": action, "clip": "", "available": false}
	var anim := player.get_animation(clip)
	var position_sec := minf(anim.length * phase, maxf(anim.length - 0.001, 0.0))
	player.play(clip, 0.0)
	player.seek(position_sec, true)
	player.pause()
	return {"requested": action, "clip": clip, "available": true, "duration_sec": anim.length, "sample_sec": position_sec}


func _capture_sequence() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	for action in ["idle", "walk", "attack"]:
		for frame_index in 3:
			var phase := [0.12, 0.45, 0.78][frame_index] as float
			var samples: Array[Dictionary] = []
			for slot in slots:
				var visual := slot.visual as Node3D
				visual.position = slot.base_position
				if slot.id == "doho" and action == "walk":
					visual.position += SCREEN_RIGHT * (phase - 0.45) * 1.0
				var sample := _pose(slot, action if slot.id == "doho" else "idle", phase)
				sample.id = slot.id
				var foot := camera.unproject_position(visual.global_position)
				var head := camera.unproject_position(visual.global_position + Vector3.UP * float(slot.target_height))
				sample.projected_vertical_height_px = absf(foot.y - head.y)
				sample.foot_px = [foot.x, foot.y]
				samples.append(sample)
			var title := "ASSEMBLY REFERENCE — NOT H1" if mode == "assembly_reference" else "H1 CANDIDATE — ISOLATED 3D TRIAL"
			hud.text = "%s\nORTHO %.3f / PITCH %.3f / YAW %.1f / 1280×720\nDOHO 1.70m  •  MERCHANT 1.60m  •  %s %d/3%s" % [title, camera_size, camera_pitch, camera_yaw, action.to_upper(), frame_index + 1, "  •  SWORD PROXY" if sword_proxy else ""]
			if diagnostic != "":
				hud.text += "\nDIAGNOSTIC CLOSE VIEW: " + diagnostic.to_upper() + " / NOT GAME LIGHTING"
			if not socket_data.is_empty():
				hud.text += "\nH1 FIST + MEASURED SOCKET / NO FINGER BONES REQUIRED"
			if pc_matte or pc_fill:
				hud.text += "\nPC-ONLY CANDIDATE: " + ("MATTE METAL0 ROUGH0.8 " if pc_matte else "") + ("LOCAL FILL0.65" if pc_fill else "")
			if tiles_flip_winding or tiles_two_sided:
				hud.text += "\nTILE DIAGNOSTIC: " + ("RUNTIME WINDING FLIP" if tiles_flip_winding else "TWO SIDED")
			if mode == "h1_trial" and samples.any(func(sample: Dictionary) -> bool: return not sample.available):
				hud.text += "\nMISSING ANIMATION CLIP — STATIC FORM / MATERIAL CHECK ONLY"
			await get_tree().process_frame
			if grip_closeup:
				camera.set_process(false)
				var hands := (slots[0].visual as Node3D).find_children("*", "Skeleton3D", true, false)
				if not hands.is_empty():
					var sk := hands[0] as Skeleton3D
					var hand := sk.find_bone("RightHand")
					var wrist: Transform3D = sk.global_transform * sk.get_bone_global_pose(hand)
					var offset: Array = socket_data.get("weapon_offset_pos", [0.0053, 0.0703, 0.0260])
					var hand_center := wrist.origin + wrist.basis.orthonormalized() * Vector3(offset[0], offset[1], offset[2])
					camera.size = 0.50
					camera.position = hand_center + Vector3(1.6, 0.9, 1.6)
					camera.look_at(hand_center)
					hud.text = "%s / %d — H1 FIST + MEASURED SOCKET\nGRIP CLOSEUP ORTHO 0.5 / NEUTRAL / SWORD PROXY" % [action.to_upper(), frame_index + 1]
			await RenderingServer.frame_post_draw
			var image := get_viewport().get_texture().get_image()
			var filename := "%s_%s_%02d.png" % [mode, action, frame_index]
			var image_path := shots_dir.path_join(filename)
			var save_error := image.save_png(image_path)
			if save_error != OK:
				load_failures.append("PNG write error %d: %s" % [save_error, image_path])
			captures.append({"path": image_path, "action": action, "phase": phase, "width": image.get_width(), "height": image.get_height(), "samples": samples, "sha256": FileAccess.get_sha256(image_path)})
	_write_report()
	get_tree().quit(0 if load_failures.is_empty() else 2)


func _write_report() -> void:
	var actor_data: Array[Dictionary] = []
	var animation_gate := mode == "h1_trial" and load_failures.is_empty()
	for capture in captures:
		for sample in capture.samples:
			animation_gate = animation_gate and bool(sample.available)
	for slot in slots:
		var entry: Dictionary = slot.duplicate()
		entry.erase("visual")
		entry.erase("label_node")
		entry.erase("base_position")
		actor_data.append(entry)
	var report := {
		"captured_at_utc": Time.get_datetime_string_from_system(true),
		"mode": mode,
		"is_h1_result": mode == "h1_trial" and load_failures.is_empty(),
		"clip_sampling_gate_passed": animation_gate,
		"animation_visual_qa_status": "not_approved; inspect deformation, hands, and socket",
		"is_game_intake": false,
		"diagnostic": diagnostic,
		"pc_material_candidate": {"matte": pc_matte, "metallic_override": 0.0 if pc_matte else null, "roughness_override": 0.8 if pc_matte else null, "emission": "preserved from source"},
		"pc_local_fill_candidate": {"enabled": pc_fill, "energy": 0.65 if pc_fill else 0.0, "range": 3.0, "cull_mask": 2, "affects_floor_or_npc": false},
		"engine": Engine.get_version_info(),
		"camera": {"ortho_size": camera_size, "pitch_deg": camera_pitch, "yaw_deg": camera_yaw, "distance": Vector3(1.6, 0.9, 1.6).length() if grip_closeup else 30.0, "viewport": [1280, 720]},
		"environment": "Exact Environment property snapshot from current world/dungeon_level.tscn" if diagnostic == "" else "Diagnostic neutral environment; not the game lighting",
		"lighting": "Exact current player light plus reused production torch script; isolated room layout" if diagnostic == "" else "Neutral white ambient 0.6 + directional 1.0; no game light/torch",
		"weapon_is_proxy": sword_proxy,
		"weapon_socket": {"source": socket_file, "data": socket_data},
		"grip_closeup": grip_closeup,
		"tile_two_sided_diagnostic": tiles_two_sided,
		"tile_flipped_winding_diagnostic": tiles_flip_winding,
		"tiles": tile_records,
		"actors": actor_data,
		"captures": captures,
		"errors": Array(load_failures),
		"limitations": ["Isolated review room, not gameplay integration", "Merchant uses idle while Doho is sampled in idle/walk/attack", "Projected vertical height excludes hat width and pose-dependent silhouette", "Assembly-reference captures are never H1 results"]
	}
	var output := shots_dir.path_join("report.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(report, "\t") + "\n")
		file.close()
	print("[H1 trial] %s | captures=%d | errors=%d | report=%s" % [mode, captures.size(), load_failures.size(), output])
