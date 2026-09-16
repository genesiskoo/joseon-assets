extends SceneTree

const SOURCE := "C:/workspace/joseon/assets/models/doho/doho.glb"
const OUT_DIR := "C:/workspace/joseon/tmp/artwork_compare/"

func _initialize() -> void:
	call_deferred("_capture")

func _label(text: String, x: int, y: int, size: int, color := Color(0.87, 0.88, 0.9)) -> Label:
	var label := Label.new()
	label.text = text
	label.position = Vector2(x, y)
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	root.add_child(label)
	return label

func _viewport(rect: Rect2i, yaw: float, pitch: float, ortho: float, target: Vector3, floor_grid := false) -> SubViewport:
	var holder := SubViewportContainer.new()
	holder.position = rect.position
	holder.size = rect.size
	root.add_child(holder)
	var vp := SubViewport.new()
	vp.size = rect.size
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.msaa_3d = Viewport.MSAA_4X
	holder.add_child(vp)
	var env := WorldEnvironment.new()
	var settings := Environment.new()
	settings.background_mode = Environment.BG_COLOR
	settings.background_color = Color(0.09, 0.08, 0.1)
	settings.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	settings.ambient_light_color = Color(0.55, 0.55, 0.62)
	settings.ambient_light_energy = 0.6
	env.environment = settings
	vp.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45, 35, 0)
	sun.light_energy = 1.1
	sun.shadow_enabled = true
	vp.add_child(sun)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-15, -150, 0)
	fill.light_energy = 0.22
	vp.add_child(fill)
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var result := doc.append_from_file(SOURCE, state)
	if result != OK:
		push_error("GLB read failed: %s" % result)
		quit(1)
		return vp
	var model := doc.generate_scene(state)
	vp.add_child(model)
	var ap := model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if ap:
		print("model clips: ", ap.get_animation_list())
		for clip in ap.get_animation_list():
			if String(clip).to_lower().contains("idle"):
				ap.play(clip)
				ap.advance(0.0)
				ap.pause()
				break
	if floor_grid:
		for x in range(-9, 10):
			for z in range(-9, 10):
				var tile := MeshInstance3D.new()
				var mesh := PlaneMesh.new()
				mesh.size = Vector2(0.98, 0.98)
				tile.mesh = mesh
				tile.position = Vector3(x, -0.01, z)
				var mat := StandardMaterial3D.new()
				mat.albedo_color = Color(0.15, 0.145, 0.16) if (x+z)%2==0 else Color(0.17, 0.165, 0.18)
				tile.material_override = mat
				vp.add_child(tile)
	var camera := Camera3D.new()
	vp.add_child(camera)
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = ortho
	camera.rotation_degrees = Vector3(-pitch, yaw, 0)
	camera.position = target + camera.transform.basis.z * 30.0
	camera.current = true
	return vp

func _capture() -> void:
	root.size = Vector2i(1536, 960)
	RenderingServer.set_default_clear_color(Color(0.045, 0.047, 0.055))
	_label("CURRENT IMPORTED DOHO / v2 / 2026-09-17", 30, 20, 30)
	_label("Source: assets/models/doho/doho.glb   |   idle frame 0   |   scale 1.0   |   no model edits", 30, 64, 18)
	_label("FRONT", 30, 112, 24)
	_label("ISOMETRIC / pitch 35.264 / yaw 45", 534, 112, 21)
	_label("BACK", 1038, 112, 24)
	_viewport(Rect2i(18, 154, 492, 710), 0.0, 0.0, 2.35, Vector3(0, 0.85, 0))
	_viewport(Rect2i(522, 154, 492, 710), 45.0, 35.264, 2.35, Vector3(0, 0.85, 0))
	_viewport(Rect2i(1026, 154, 492, 710), 180.0, 0.0, 2.35, Vector3(0, 0.85, 0))
	_label("Audit render with model-viewer lighting + weak fill. This is not a gameplay screenshot.", 30, 893, 20)
	for i in range(8):
		await process_frame
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	var err := img.save_png(OUT_DIR + "doho_v2_model_audit.png")
	print("AUDIT saved ", err)
	for child in root.get_children():
		child.queue_free()
	await process_frame
	root.size = Vector2i(1280, 720)
	_viewport(Rect2i(0, 0, 1280, 720), 45.0, 35.264, 14.0, Vector3.ZERO, true)
	_label("NATIVE SCALE CHECK / 1280 x 720 / orthographic size 14", 28, 22, 22)
	_label("Current GLB, isolated 1-unit grid; game camera angles; synthetic stage, not gameplay.", 28, 56, 18)
	for i in range(8):
		await process_frame
	await RenderingServer.frame_post_draw
	img = root.get_texture().get_image()
	err = img.save_png(OUT_DIR + "doho_v2_native_scale.png")
	print("NATIVE saved ", err)
	quit()
