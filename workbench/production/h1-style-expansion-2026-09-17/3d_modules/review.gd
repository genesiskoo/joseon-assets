extends Node3D

const CAMERA_SCRIPT = preload("res://world/iso_camera.gd")
const TORCH_SCRIPT = preload("res://world/torch.gd")
const CUT_SHADER = preload("res://world/wall_cutaway.gdshader")
var geometry: Node3D
var camera: Camera3D
var hud: Label
var world: WorldEnvironment
var captures: Array[Dictionary] = []
var errors: Array[String] = []
var cache: Dictionary = {}
var mode: String = ""
var front_walls: Array[Node3D] = []
var proxy: MeshInstance3D
var actor_position := Vector3(2.3,0,2.3)
var actor_path := "res://reference_actor/H1_doho_preserved.glb"
var actor_source := "C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/fist/H1_doho_preserved.glb"
var dark_environment: Environment
var socket_report: Dictionary = {}
var candidate_actor: Node3D
var socket_sword: Node3D
var socket_attachment: BoneAttachment3D
var socket_skeleton: Skeleton3D
var socket_bone:= -1
var corrected_socket_samples: Array[Dictionary] = []

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://captures"))
	dark_environment=load("res://references/current_dungeon_environment.tres") as Environment
	world=WorldEnvironment.new()
	world.environment=dark_environment
	add_child(world)
	var focus:=Node3D.new()
	focus.name="Focus"
	add_child(focus)
	camera=Camera3D.new()
	camera.set_script(CAMERA_SCRIPT)
	camera.set("target_path",focus.get_path())
	camera.set("ortho_size",11.0)
	camera.set("pitch_deg",35.264)
	camera.set("yaw_deg",45.0)
	camera.set("distance",30.0)
	add_child(camera)
	camera.current=true
	var canvas:=CanvasLayer.new()
	add_child(canvas)
	hud=Label.new()
	hud.position=Vector2(20,16)
	hud.add_theme_font_size_override("font_size",18)
	hud.add_theme_color_override("font_outline_color",Color.BLACK)
	hud.add_theme_constant_override("outline_size",5)
	canvas.add_child(hud)
	call_deferred("_sequence")

func _load_model(id: String) -> Node3D:
	var path: String=("res://props/" if id in ["doho_sword","doho_scabbard","bandit_club","paper_talisman"] else "res://models/")+id+".glb"
	if not cache.has(id):
		var doc:=GLTFDocument.new()
		var state:=GLTFState.new()
		var err:=doc.append_from_file(ProjectSettings.globalize_path(path),state)
		if err!=OK:
			errors.append("GLB error %d: %s" % [err,id])
			return null
		var scene:=doc.generate_scene(state)
		# GLTFDocument runtime loads bypass editor texture import settings. Build
		# renderer mip levels for the atlas only; source PNG/base pixels stay intact.
		for mesh_node in scene.find_children("*","MeshInstance3D",true,false):
			var mesh_instance:=mesh_node as MeshInstance3D
			for surface in mesh_instance.mesh.get_surface_count():
				var material:=mesh_instance.get_active_material(surface) as StandardMaterial3D
				if material and material.resource_name.begins_with("h1_atlas_") and material.albedo_texture:
					var texture_image:=material.albedo_texture.get_image()
					if not texture_image.has_mipmaps():texture_image.generate_mipmaps()
					material.albedo_texture=ImageTexture.create_from_image(texture_image)
					material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
		var packed:=PackedScene.new()
		packed.pack(scene)
		scene.free()
		cache[id]=packed
	return (cache[id] as PackedScene).instantiate() as Node3D

func _reset() -> void:
	if geometry:geometry.free()
	geometry=Node3D.new()
	add_child(geometry)
	front_walls.clear()
	proxy=null
	candidate_actor=null
	world.environment=dark_environment

func _add(id: String,position: Vector3,rotation_y: float=0) -> Node3D:
	var model:=_load_model(id)
	if model:
		model.position=position
		model.rotation_degrees.y=rotation_y
		geometry.add_child(model)
	return model

func _label(text: String,position: Vector3) -> void:
	var label:=Label3D.new()
	label.text=text
	label.position=position
	label.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size=24
	label.pixel_size=.0025 if camera.size<5 else .004
	label.no_depth_test=true
	geometry.add_child(label)

func _floor(size: int=9) -> void:
	var half:=int(size/2)
	for x in range(-half,half+1):
		for z in range(-half,half+1):_add("floor",Vector3(x,0,z))

func _light(position: Vector3,color: Color,energy: float,range_value: float) -> void:
	var light:=OmniLight3D.new()
	light.position=position
	light.light_color=color
	light.light_energy=energy
	light.omni_range=range_value
	geometry.add_child(light)

func _neutral() -> void:
	var env:=Environment.new()
	env.background_mode=Environment.BG_COLOR
	env.background_color=Color(.035,.04,.045)
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color(.65,.66,.70)
	env.ambient_light_energy=.5
	env.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	world.environment=env
	var key:=DirectionalLight3D.new()
	key.rotation_degrees=Vector3(-60,-25,0)
	key.light_energy=1.1
	geometry.add_child(key)

func _build_dungeon_catalog() -> void:
	_reset()
	_neutral()
	var ids: Array[String]=["floor","wall_straight","wall_corner","stairs_up","door_frame","seal_door","stairs_down","pillar","brazier"]
	for i in ids.size():
		var x:=float(i%3-1)*3.7
		var z:=float(int(i/3)-1)*3.4
		_add(ids[i],Vector3(x,0,z))
		_label(ids[i].to_upper(),Vector3(x,-.25,z+.6))

func _build_town() -> void:
	_reset()
	_floor(7)
	_add("market_bay",Vector3(-1.5,0,-2.6))
	_add("market_bay",Vector3(1.5,0,-2.6))
	_add("paper_sliding_door",Vector3(-3,0,0),90)
	_add("wood_crate",Vector3(2.6,0,-1.25))
	_add("wood_crate",Vector3(2.6,.7,-1.25))
	_add("onggi_jar",Vector3(-2.7,0,-1.1))
	_add("onggi_jar",Vector3(-2.4,0,.9))
	_add("square_paper_lantern",Vector3(-1.5,1.45,-2.0))
	_add("square_paper_lantern",Vector3(1.5,1.45,-2.0))
	_light(Vector3(-1.5,1.75,-1.8),Color(1,.62,.30),3.2,7)
	_light(Vector3(1.5,1.75,-1.8),Color(1,.62,.30),3.2,7)
	_light(Vector3(0,2.2,1),Color(.98,.92,.82),2.2,9)
	_add_raw_actor(Vector3(0,0,.8))

func _build_town_catalog() -> void:
	_reset()
	_neutral()
	var items: Array=[
		["market_bay",Vector3(-1.6,0,-1.8)],
		["paper_sliding_door",Vector3(2.2,0,-1.8)],
		["wood_crate",Vector3(-2.2,0,2.0)],
		["onggi_jar",Vector3(0,0,2.0)],
		["square_paper_lantern",Vector3(2.2,0,2.0)]
	]
	for item in items:
		_add(item[0],item[1])
		_label(str(item[0]).to_upper(),item[1]+Vector3(0,-.25,.4))

func _build_room() -> void:
	_reset()
	_floor(7)
	for x in range(-3,4):
		if abs(x)>1:_add("wall_straight",Vector3(x,0,-4))
	for z in range(-3,4):_add("wall_straight",Vector3(-4,0,z))
	_add("wall_corner",Vector3(-4,0,-4),180)
	_add("door_frame",Vector3(0,0,-4))
	_add("seal_door",Vector3(0,0,-3.95))
	# The multi-cell doorway needs floor beneath its open middle cell.
	for x in [-1,0,1]:_add("floor",Vector3(x,0,-4))
	_add("pillar",Vector3(-3,0,-2.7))
	_add("pillar",Vector3(3,0,-2.7))
	_add("stairs_up",Vector3(-2.8,0,-1.5))
	_add("stairs_down",Vector3(2.8,0,-1.5))
	for x in [-2.0,2.0]:
		_add("brazier",Vector3(x,0,-3.3))
		var torch: Node3D=TORCH_SCRIPT.new()
		torch.position=Vector3(x,.57,-3.3)
		geometry.add_child(torch)
	_light(actor_position+Vector3(0,2.2,0),Color(.98,.92,.82),2.2,9)
	for i in range(-3,4):
		front_walls.append(_add("wall_straight",Vector3(i,0,4)))
		front_walls.append(_add("wall_straight",Vector3(4,0,i)))
	front_walls.append(_add("wall_corner",Vector3(4,0,4),0))
	front_walls.append(_add("wall_corner",Vector3(-4,0,4),90))
	front_walls.append(_add("wall_corner",Vector3(4,0,-4),-90))
	_add_raw_actor(Vector3(0,0,.2))

func _add_raw_actor(at: Vector3) -> void:
	if not FileAccess.file_exists(actor_path):return
	var doc:=GLTFDocument.new()
	var state:=GLTFState.new()
	if doc.append_from_file(actor_path,state)!=OK:return
	var root:=doc.generate_scene(state) as Node3D
	# Trial pipeline already baked this rig to 1.70u; do not use an unskinned AABB.
	root.position=at
	root.rotation_degrees.y=45
	geometry.add_child(root)
	candidate_actor=root
	for player_node in root.find_children("*","AnimationPlayer",true,false):
		var player:=player_node as AnimationPlayer
		for clip in player.get_animation_list():
			if str(clip).to_lower().contains("idle"):
				player.play(clip)
				player.seek(.5,true)
				player.pause()
				break
	_label("H1 FIST CANDIDATE / CONTACT REVIEW",at+Vector3(0,2.1,0))

func _build_props_catalog() -> void:
	_reset()
	_neutral()
	camera.size=2.2
	var right:=Vector3(.70710678,0,-.70710678)
	var ids:Array[String]=["doho_sword","doho_scabbard","bandit_club","paper_talisman"]
	for i in ids.size():
		var at:Vector3=right*(float(i)-1.5)*.65
		if ids[i]=="paper_talisman":at.y=.55
		_add(ids[i],at,45)
		_label(["SWORD","SCABBARD","CLUB","PAPER / BOTH SIDES"][i],right*(float(i)-1.5)*.65+Vector3(0,-.30,0))
	# Back of exactly the same zero-thickness sheet, visibly separated.
	_add("paper_talisman",right*1.30+Vector3(0,.55,0),225)

func _build_angle_probe() -> void:
	_reset()
	_neutral()
	camera.size=2.2
	var right:=Vector3(.70710678,0,-.70710678)
	for i in 3:
		var pivot:=Node3D.new()
		pivot.position=right*(float(i)-1)*.85
		pivot.rotation_degrees=Vector3(0,45,float(i-1)*45)
		geometry.add_child(pivot)
		pivot.add_child(_load_model("doho_sword"))
		var marker:=MeshInstance3D.new()
		var sphere:=SphereMesh.new()
		sphere.radius=.023
		sphere.height=.046
		marker.mesh=sphere
		var mat:=StandardMaterial3D.new()
		mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color=Color(0,.8,.9)
		marker.material_override=mat
		pivot.add_child(marker)
		_label("%d DEG" % [int(i-1)*45],pivot.position+Vector3(0,-.3,0))

func _build_socket_probe() -> void:
	_build_room()
	camera.size=11
	_set_front("removed")
	if candidate_actor==null:
		socket_report={"attached":false,"reason":"H1 candidate unavailable"}
		return
	var skeletons:=candidate_actor.find_children("*","Skeleton3D",true,false)
	if skeletons.is_empty():
		socket_report={"attached":false,"reason":"No skeleton"}
		return
	var skeleton:=skeletons[0] as Skeleton3D
	var bone:=skeleton.find_bone("RightHand")
	if bone<0:
		for i in skeleton.get_bone_count():
			var name_lower:=skeleton.get_bone_name(i).to_lower()
			if name_lower.contains("right") and name_lower.ends_with("hand"):bone=i
	if bone<0:
		socket_report={"attached":false,"reason":"No right hand bone"}
		return
	var attachment:=BoneAttachment3D.new()
	attachment.name="CandidateWeaponSocket"
	attachment.bone_name=skeleton.get_bone_name(bone)
	skeleton.add_child(attachment)
	var sword:=_load_model("doho_sword")
	attachment.add_child(sword)
	var chain_scale:=skeleton.global_transform.basis.get_scale().x
	sword.scale=Vector3.ONE/chain_scale
	sword.position=Vector3(.0093,.0832,.0361)/chain_scale
	sword.rotation_degrees=Vector3(-.96,179.24,90.07)
	socket_sword=sword
	socket_attachment=attachment
	socket_skeleton=skeleton
	socket_bone=bone
	socket_report={"attached":true,"bone":skeleton.get_bone_name(bone),"cumulative_scale":chain_scale,"copied_current_offset":[.0093,.0832,.0361],"copied_current_rotation_deg":[-.96,179.24,90.07],"is_final_grip_approval":false,"notes":"H1 fist candidate + actual prop under BoneAttachment3D; current main GT1 proxy offset reused as superseded control. H1-specific measured offset is in h1_socket_correction.json."}

func _set_front(mode_value: String) -> void:
	for wall in front_walls:
		wall.visible=mode_value!="removed"
		for item in wall.find_children("*","MeshInstance3D",true,false):
			var mi:=item as MeshInstance3D
			if mode_value=="cutaway":
				var base:=mi.get_active_material(0) as StandardMaterial3D
				var mat:=ShaderMaterial.new()
				mat.shader=CUT_SHADER
				mat.set_shader_parameter("albedo",Color(.42,.40,.44,1))
				mat.set_shader_parameter("use_tex",true)
				mat.set_shader_parameter("albedo_tex",base.albedo_texture)
				mat.set_shader_parameter("player_pos",actor_position)
				mat.set_shader_parameter("cam_forward",-camera.global_basis.z)
				mat.set_shader_parameter("cut_radius",2.4)
				mat.set_shader_parameter("cut_alpha",.3)
				mi.material_override=mat
			else:mi.material_override=null

func _flat_material_control() -> void:
	var flat_colors:Dictionary={"wood":Color(.17,.115,.075),"roof":Color(.10,.115,.13),"roof_rib":Color(.13,.145,.16),"plaster":Color(.17,.115,.075),"paper":Color(.57,.49,.34),"dark_wood":Color(.055,.061,.066)}
	for mesh_node in geometry.find_children("*","MeshInstance3D",true,false):
		var mi:=mesh_node as MeshInstance3D
		for surface in mi.mesh.get_surface_count():
			var material:=mi.get_active_material(surface) as StandardMaterial3D
			if not material or not material.resource_name.begins_with("h1_atlas_"):continue
			var key:String=material.resource_name.trim_prefix("h1_atlas_")
			var flat:=StandardMaterial3D.new()
			flat.albedo_color=flat_colors[key]
			# Club used a warmer flat timber in the original candidate pass.
			if key=="wood" and mi.get_parent().name=="bandit_club":flat.albedo_color=Color(.21,.13,.07)
			flat.roughness=1.0
			mi.set_surface_override_material(surface,flat)

func _add_proxy() -> void:
	proxy=MeshInstance3D.new()
	var mesh:=CapsuleMesh.new()
	mesh.radius=.23
	mesh.height=1.7
	proxy.mesh=mesh
	proxy.position=actor_position+Vector3(0,.85,0)
	var material:=StandardMaterial3D.new()
	material.albedo_color=Color(1,0,1)
	material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	material.disable_fog=true
	proxy.material_override=material
	geometry.add_child(proxy)

func _capture(id: String,title: String) -> void:
	hud.text=title+"\nORTHO %.1f | PITCH 35.264 | YAW 45 | 1280x720\nISOLATED CANDIDATES - NOT GAME INTAKE" % camera.size
	await get_tree().process_frame
	await get_tree().process_frame
	if id in ["09_sword_socket","10_sword_socket_closeup"] and socket_sword:
		var bone_world:Vector3=socket_skeleton.to_global(socket_skeleton.get_bone_global_pose(socket_bone).origin)
		var attachment_world:Vector3=socket_attachment.global_position
		var tip:Vector3=socket_sword.to_global(Vector3(0,.80,0))
		var grip:Vector3=socket_sword.global_position
		socket_report.bone_world=[bone_world.x,bone_world.y,bone_world.z]
		socket_report.attachment_world=[attachment_world.x,attachment_world.y,attachment_world.z]
		socket_report.bone_attachment_origin_error=bone_world.distance_to(attachment_world)
		socket_report.grip_world=[grip.x,grip.y,grip.z]
		socket_report.tip_world=[tip.x,tip.y,tip.z]
		socket_report.grip_to_tip_world_length=grip.distance_to(tip)
	await RenderingServer.frame_post_draw
	var image:=get_viewport().get_texture().get_image()
	var path:="res://captures/"+id+".png"
	var err:=image.save_png(path)
	if err!=OK:errors.append("PNG write %d: %s" % [err,id])
	var magenta:=0
	if proxy:
		for y in range(110,image.get_height()):
			for x in image.get_width():
				var color:=image.get_pixel(x,y)
				if color.r>.30 and color.b>.30 and color.g<.12:magenta+=1
	captures.append({"id":id,"file":"captures/"+id+".png","width":image.get_width(),"height":image.get_height(),"sha256":FileAccess.get_sha256(path),"ortho_size":camera.size,"scale_proxy_pixels":magenta,"lighting":"neutral catalog" if id.contains("catalog") or id.contains("angles") else "copied dungeon environment + production light values, trial layout"})

func _socket_contact_sample(action: String,phase: float,clip: String) -> Dictionary:
	var grip:Vector3=socket_sword.global_position
	var blade_start:Vector3=socket_sword.to_global(Vector3(0,.065,0))
	var tip:Vector3=socket_sword.to_global(Vector3(0,.8,0))
	var hips_id:=socket_skeleton.find_bone("Hips")
	var neck_id:=socket_skeleton.find_bone("neck")
	var hips:Vector3=socket_skeleton.to_global(socket_skeleton.get_bone_global_pose(hips_id).origin)
	var neck:Vector3=socket_skeleton.to_global(socket_skeleton.get_bone_global_pose(neck_id).origin)
	var axis:Vector3=neck-hips
	var minimum:=INF
	for i in 33:
		var p:Vector3=blade_start.lerp(tip,float(i)/32)
		var t:float=clampf((p-hips).dot(axis)/axis.length_squared(),0,1)
		minimum=minf(minimum,p.distance_to(hips+axis*t))
	var elbow_id:=socket_skeleton.find_bone("RightForeArm")
	var elbow:Vector3=socket_skeleton.to_global(socket_skeleton.get_bone_global_pose(elbow_id).origin)
	var wrist:Vector3=socket_skeleton.to_global(socket_skeleton.get_bone_global_pose(socket_bone).origin)
	return {"action":action,"phase":phase,"clip":clip,"grip":[grip.x,grip.y,grip.z],"tip":[tip.x,tip.y,tip.z],"grip_to_tip_length":grip.distance_to(tip),"forearm_blade_angle_deg":rad_to_deg((wrist-elbow).angle_to(tip-grip)),"torso_axis_min_distance":minimum,"torso_proxy_radius":.18,"torso_proxy_clear":minimum>.18,"blade_tip_above_ground":tip.y>0,"method":"33 blade samples against Hips-neck segment radius .18; conservative diagnostic capsule, not exact skinned mesh collision"}

func _corrected_socket_sequence() -> void:
	if not socket_sword:return
	var scale_value:=socket_skeleton.global_transform.basis.get_scale().x
	socket_sword.position=Vector3(.0053,.0703,.0260)/scale_value
	socket_sword.rotation_degrees=Vector3(1.80,-174.82,97.77)
	var players:=candidate_actor.find_children("*","AnimationPlayer",true,false)
	if players.is_empty():return
	var player:=players[0] as AnimationPlayer
	for action in ["idle","walk","attack"]:
		var selected:=""
		for clip in player.get_animation_list():
			if str(clip).to_lower().contains(action):
				selected=clip
				break
		if selected=="":
			errors.append("Missing socket inspection clip: "+action)
			continue
		for i in 3:
			var phase:float=[.12,.45,.78][i]
			player.play(selected)
			player.seek(player.get_animation(selected).length*phase,true)
			player.pause()
			await _capture("11_h1_socket_%s_%02d" % [action,i],"H1 FIST + MEASURED SOCKET / %s %d OF 3 - CONTACT REVIEW CANDIDATE" % [action.to_upper(),i+1])
			corrected_socket_samples.append(_socket_contact_sample(action,phase,selected))
	var correction:Dictionary={"model":actor_path,"source":actor_source,"sha256":FileAccess.get_sha256(actor_path),"bone":"RightHand","position":[.0053,.0703,.0260],"rotation_degrees":[1.80,-174.82,97.77],"measurement":"reference_actor/H1_doho_fist_fist.json; h1_active_guides rig_fix.py --fist=both --palm=down candidate; unmodified tools/weapon_socket.gd exact transform inversion","measurement_sha256":FileAccess.get_sha256("res://reference_actor/H1_doho_fist_fist.json"),"weapon_socket_roundtrip_position_m":0.0,"weapon_socket_roundtrip_angle_deg":0.0,"samples":corrected_socket_samples,"fist_geometry_applied":true,"hand_contact_visual_approved":false,"main_modeldef_modified":false,"caveat":"Right thumb selection=0 in helper report; fist geometry and selected frames remain visual candidates. Capsule clearance is not exact skinned mesh collision or full body/sleeve contact approval."}
	var file:=FileAccess.open("res://h1_socket_correction.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(correction,"\t")+"\n")

func _sequence() -> void:
	await get_tree().process_frame
	_build_dungeon_catalog()
	await _capture("01_dungeon_catalog","9 DUNGEON MODULES - NEUTRAL MATERIAL INSPECTION")
	_build_town_catalog()
	await _capture("01b_town_catalog","5 TOWN MODULES - NEUTRAL MATERIAL INSPECTION")
	_build_town()
	await _capture("02_town_assembly","5 TOWN MODULES - REPEATED MARKET BAYS / ACTUAL DARK LIGHTING")
	_build_room()
	_set_front("removed")
	await _capture("03_dungeon_assembly","DUNGEON MODULE ASSEMBLY - FOREGROUND REMOVED FOR REVIEW")
	_add_proxy()
	await _capture("04_occlusion_baseline","OCCLUSION BASELINE - 1.7u MAGENTA SCALE PROXY / NO FRONT WALL")
	_set_front("opaque")
	await _capture("05_occlusion_opaque","OCCLUSION TEST - SAME 1.7u PROXY / OPAQUE FRONT WALL")
	_set_front("cutaway")
	await _capture("06_occlusion_cutaway","OCCLUSION TEST - COPIED PRODUCTION CUTAWAY SHADER / SAME PROXY")
	var baseline:int=captures[4].scale_proxy_pixels
	var opaque:int=captures[5].scale_proxy_pixels
	var cutaway:int=captures[6].scale_proxy_pixels
	_build_props_catalog()
	await _capture("07_props_catalog","4 SEPARATE PROPS - AUXILIARY CLOSEUP / SAME PAPER FRONT AND BACK")
	_build_angle_probe()
	await _capture("08_sword_angles","SWORD AXIS PROBE - ROTATION ABOUT THE CYAN GRIP ORIGIN")
	_build_socket_probe()
	await _capture("09_sword_socket","H1 FIST CANDIDATE + SWORD - GT1 COPIED OFFSET CONTROL / SUPERSEDED")
	camera.size=3.5
	(get_node("Focus") as Node3D).position=Vector3(0,.85,.2)
	camera.call("snap_to_target")
	await _capture("10_sword_socket_closeup","H1 SWORD ATTACHMENT CLOSEUP - COPIED OFFSET / GRIP REQUIRES REVIEW")
	await _corrected_socket_sequence()
	# Same final geometry/actor/camera/light, original solid-color material control.
	_build_town_catalog()
	_flat_material_control()
	await _capture("12_town_catalog_flat_control","FLAT MATERIAL CONTROL - SAME FINAL GEOMETRY / NEUTRAL LIGHT")
	_build_town()
	_flat_material_control()
	await _capture("13_town_assembly_flat_control","FLAT MATERIAL CONTROL - SAME FINAL H1 / CAMERA / DARK LIGHT")
	_build_props_catalog()
	_flat_material_control()
	await _capture("14_props_catalog_flat_control","FLAT MATERIAL CONTROL - SAME PROPS / SAME AUXILIARY CAMERA")
	var report:Dictionary={"utc":Time.get_datetime_string_from_system(true),"engine":Engine.get_version_info(),"camera":{"ortho_size":11.0,"pitch":35.264,"yaw":45.0,"viewport":[1280,720],"auxiliary_props_closeup_ortho":2.2},"is_game_intake":false,"h1_actor":{"source":actor_path,"sha256":FileAccess.get_sha256(actor_path),"state":"rigged H1 candidate, idle sample .5s; hand grip not approved"},"captures":captures,"socket_probe":socket_report,"occlusion":{"diagnostic_only":true,"proxy_height":1.7,"position":[actor_position.x,actor_position.y,actor_position.z],"baseline_pixels":baseline,"opaque_pixels":opaque,"cutaway_pixels":cutaway,"opaque_visible_ratio":float(opaque)/maxi(baseline,1),"cutaway_visible_ratio":float(cutaway)/maxi(baseline,1),"shader":"Exact copied world/shaders/wall_cutaway.gdshader; uniforms radius=2.4 alpha=0.3; isolated MeshInstance test, not live DungeonBuilder"},"tile_seams":{"floor_contact_gap_units":0.0,"wall_contact_gap_units":0.0,"basis":"GLB AABB exact 1x1 floor/1x2x1 wall; positions at 1u spacing; integer corner cells; doorway floor included","texture_seam_review":"See repeated actual-render floor/wall; source image periodic patterns retained"},"errors":errors,"limitations":["All screenshots are real Godot-rendered candidate GLBs; no AI scene image used as render","H1 rig is a candidate, not final hand/cloth approval","Magenta capsule is only a scale/occlusion diagnostic","Collision/navigation/gameplay not tested","Town constant-color timber and ceramics need later H1 surface finish","Stairs_down is inherited wedge, not a real opening through the floor","Socket probe verifies attachment path, not H1 grip/contact/attack validation"]}
	report.h1_actor={"source":actor_source,"local_copy":actor_path,"sha256":FileAccess.get_sha256(actor_path),"state":"H1 fist candidate; final finger/sleeve contact approval pending"}
	report.camera.auxiliary_socket_closeup_ortho=3.5
	report.material_atlas={"source":"../23_material_atlas.png","local":"textures/H1_matte_atlas.png","actual_size":[1254,1254],"sha256":FileAccess.get_sha256("res://textures/H1_matte_atlas.png"),"source_png_pixels_modified":false,"uv_mapping":"UV0 quadrant transforms baked into candidate vertices","renderer_filter":"Runtime GLTFDocument atlas textures receive standard mipmaps and anisotropic sampling; PNG base pixels unchanged","not_1k_budget_pass":true,"not_guaranteed_seamless_or_unlit":true,"onggi":"unchanged matte solid color"}
	report.material_comparison=[{"before":"captures/12_town_catalog_flat_control.png","after":"captures/01b_town_catalog.png"},{"before":"captures/13_town_assembly_flat_control.png","after":"captures/02_town_assembly.png"},{"before":"captures/14_props_catalog_flat_control.png","after":"captures/07_props_catalog.png"}]
	report.limitations=["All captures are actual GLBs rendered in Godot, not concept art","1254x1254 shared atlas exceeds nominal 1K budget and is not guaranteed seamless or fully unlit","Onggi and talisman remain simple matte colors; H1 illustration-level finish unapproved","H1 preserved fist rig is a candidate; thumb/finger/sleeve contact requires further visual approval","Collision/navigation/gameplay not tested","Stairs_down is an inherited wedge, not a real floor opening","9 pose capsule checks do not establish full animation collision clearance"]
	var file:=FileAccess.open("res://render_report.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")+"\n")
	print("H1 module review captures=%d errors=%d" % [captures.size(),errors.size()])
	get_tree().quit(0 if errors.is_empty() else 2)
