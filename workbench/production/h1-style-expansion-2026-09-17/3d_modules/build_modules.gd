extends SceneTree

const SOURCE := "res://source/"
const OUTPUT := "res://models/"
var output_dir := OUTPUT
var mats: Dictionary = {}
var parts: Dictionary = {}
var records: Array[Dictionary] = []
var errors: Array[String] = []
var atlas_regions: Dictionary = {}
var atlas_texture: Texture2D
var atlas_configuration: Dictionary = {}

func _init() -> void:
	call_deferred("_build")

func _build() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT))
	mats.stone = _texture_mat("wall", SOURCE + "wall_wall_tex_raw.png")
	mats.floor = _texture_mat("floor", SOURCE + "floor_floor_tex_raw.png")
	mats.iron = _color_mat("matte_iron", Color(0.12, 0.11, 0.10), 0.90)
	mats.wood = _color_mat("matte_old_timber", Color(0.17, 0.115, 0.075), 1.0)
	mats.paper = _color_mat("aged_seal_paper", Color(0.57, 0.49, 0.34), 1.0)
	mats.ink = _color_mat("muted_red_seal", Color(0.29, 0.085, 0.065), 1.0)
	mats.roof = _color_mat("matte_charcoal_roof", Color(0.10, 0.115, 0.13), 1.0)
	mats.roof_rib = _color_mat("matte_roof_tile_ribs", Color(0.13, 0.145, 0.16), 1.0)
	mats.earthenware = _color_mat("matte_onggi", Color(0.15, 0.09, 0.055), 0.92)
	_source_candidate("floor", "floor", true, "1 x 1 tile; top Y=0; exact source normals/UV/albedo retained; winding corrected")
	_source_candidate("wall_straight", "wall", true, "1 x 2 x 1 solid cell wall; base pivot; exact source normals/UV/albedo retained; winding corrected")
	_source_candidate("stairs_up", "stairs_up", false, "Existing fitted Meshy stair; candidate-only decimation 502 to 488 tri; footprint 1 x 1; same albedo")
	_source_candidate("stairs_down", "stairs_down", false, "Existing fitted Meshy stair; candidate-only decimation 514 to 487 tri; footprint 1 x 1; same albedo")
	parts.clear()
	# Full-cell outer corner. Only the exposed +X/+Z corner is chamfered.
	var ring := PackedVector2Array([Vector2(-0.5,-0.5),Vector2(0.5,-0.5),Vector2(0.5,0.38),Vector2(0.38,0.5),Vector2(-0.5,0.5)])
	_prism(ring, 0.0, 2.0, "stone", "floor", true)
	_save_generated("wall_corner", "1 x 2 x 1 outer corner; solid interior cell; 0.12u chamfer only on exposed +X/+Z corner")
	parts.clear()
	_box(Vector3(-1.125,1.025,0), Vector3(0.75,2.05,1), "stone")
	_box(Vector3(1.125,1.025,0), Vector3(0.75,2.05,1), "stone")
	_box(Vector3(0,2.225,0), Vector3(3,0.35,1), "stone")
	_save_generated("door_frame", "3 x 2.4 x 1, 3-cell doorway; clear opening 1.5 wide x 2.05 high; base-center pivot; no collision")
	parts.clear()
	_box(Vector3(0,1.01,0),Vector3(1.48,2.02,.22),"stone")
	_disc(Vector3(0,1.10,.125),.29,.025,12,"iron")
	_disc(Vector3(0,1.10,.154),.245,.018,12,"paper")
	for offset in [-.095,.095]:
		_box(Vector3(offset,1.10+offset,.176),Vector3(.13,.025,.015),"ink")
		_box(Vector3(offset-.05,1.06+offset,.176),Vector3(.025,.10,.015),"ink")
	# Large, spare seal strips. The marks are abstract brush strokes, not legible writing.
	for x in [-0.52,0.52]:
		_box(Vector3(x,1.35,0.136), Vector3(0.13,0.72,0.016), "paper")
		for j in 3:
			_box(Vector3(x,1.53-j*0.14,0.148), Vector3(0.072,0.027,0.012), "ink")
	_save_generated("seal_door", "Separate 1.48 x 2.02 stone seal insert for door_frame; round plaque and sparse paper seals; +Z front; base-center pivot; no animation/collision; abstract seal marks")
	parts.clear()
	_box(Vector3(0,0.10,0), Vector3(0.8,0.2,0.8), "stone")
	var pillar_ring := PackedVector2Array([Vector2(-.3,-.38),Vector2(.3,-.38),Vector2(.38,-.3),Vector2(.38,.3),Vector2(.3,.38),Vector2(-.3,.38),Vector2(-.38,.3),Vector2(-.38,-.3)])
	_prism(pillar_ring,0.2,2.15,"stone","floor",true)
	_box(Vector3(0,2.225,0), Vector3(0.86,0.15,0.86), "stone")
	_save_generated("pillar", "0.86 x 2.3 x 0.86; 1-cell freestanding pillar; octagonal broad chamfers; no collision")
	parts.clear()
	for angle in [0.0,TAU/3,TAU*2/3]:
		var p := Vector3(cos(angle)*0.21,0.225,sin(angle)*0.21)
		_box(p,Vector3(0.07,0.45,0.07),"iron")
	_bowl(0.40,0.69,0.18,0.32,0.04,8,"iron")
	_save_generated("brazier", "0.64 x 0.69 x 0.64; empty open octagonal iron bowl/3 feet; effect socket at (0,0.64,0); fire/light only in review scene")
	# Town material pass only. Existing dungeon stone/paper candidates above stay unchanged.
	mats.plaster = _color_mat("matte_wall_infill",Color(.34,.30,.24),1.0)
	_configure_atlas(["wood","roof","roof_rib","paper","plaster"])
	parts.clear()
	# One market bay, not a complete building or a replacement town layout.
	_box(Vector3(0,0.08,0),Vector3(3,0.16,1),"stone")
	_box(Vector3(0,1.13,-0.3),Vector3(2.8,1.94,0.12),"plaster")
	for x in [-1.35,1.35]:
		_box(Vector3(x,1.2,0.3),Vector3(0.16,2.08,0.16),"wood")
	_box(Vector3(0,2.15,0.3),Vector3(2.9,0.18,0.20),"wood")
	_box(Vector3(0,0.84,0.27),Vector3(2.8,0.16,0.48),"wood")
	for x in [-0.98,0.98]:
		_box(Vector3(x,1.43,-0.218),Vector3(0.55,0.84,0.04),"paper")
		for offset in [-0.15,0.0,0.15]:
			_box(Vector3(x+offset,1.43,-0.187),Vector3(0.018,0.84,0.022),"wood")
		_box(Vector3(x,1.43,-0.18),Vector3(0.55,0.025,0.024),"wood")
	# Closed wedge roofs with broad planes and a shallow lifted eave at both ends.
	for i in 4:
		var x0 := -1.6+float(i)*0.8
		var x1 := x0+0.8
		var lift0 := absf(x0)/1.6*0.08
		var lift1 := absf(x1)/1.6*0.08
		for direction in [-1.0,1.0]:
			var top := [Vector3(x0,2.58,0),Vector3(x0,2.25+lift0,direction*0.7),Vector3(x1,2.25+lift1,direction*0.7),Vector3(x1,2.58,0)]
			_slab(top,0.065,"roof")
	_box(Vector3(0,2.62,0),Vector3(3.25,0.12,0.16),"roof")
	for i in 7:
		var x:float=-1.4+float(i)*2.8/6
		for direction in [-1.0,1.0]:
			_tri_bar(Vector3(x,2.60,direction*.06),Vector3(x,2.27+absf(x)/1.6*.08,direction*.71),.034,"roof_rib")
	_save_generated("market_bay", "3.25 x 2.68 x 1.451 including roof ribs; one open timber market facade bay; 3-cell pitch with eave overhang; modest lifted eave, paper windows and counter; no interior/collision")
	parts.clear()
	_box(Vector3(0,.9,0),Vector3(.90,1.70,.035),"paper")
	for x in [-.46,.46]:_box(Vector3(x,.9,0),Vector3(.08,1.8,.10),"wood")
	for y in [.04,1.76]:_box(Vector3(0,y,0),Vector3(1,.08,.1),"wood")
	for x in [-.25,0,.25]:_box(Vector3(x,.9,.035),Vector3(.025,1.68,.05),"wood")
	for y in [.42,.9,1.38]:_box(Vector3(0,y,.035),Vector3(.86,.025,.05),"wood")
	_box(Vector3(.35,.82,.07),Vector3(.035,.15,.04),"iron")
	_save_generated("paper_sliding_door", "1 x 1.8 x 0.14; +Z front; base center; paper-and-timber sliding panel; no rail/animation/collision")
	parts.clear()
	_box(Vector3(0,.35,0),Vector3(.70,.70,.70),"wood")
	for z in [-.365,.365]:
		for y in [.11,.59]:_box(Vector3(0,y,z),Vector3(.75,.07,.04),"wood")
	for x in [-.365,.365]:
		for y in [.11,.59]:_box(Vector3(x,y,0),Vector3(.04,.07,.75),"wood")
	_save_generated("wood_crate", "0.77 x 0.7 x 0.77; dark timber crate with broad battens; base center; no collision")
	parts.clear()
	_lathe([Vector2(.20,0),Vector2(.28,.09),Vector2(.34,.33),Vector2(.32,.53),Vector2(.235,.67),Vector2(.235,.72),Vector2(.21,.72),Vector2(.21,.67),Vector2(.295,.52),Vector2(.305,.33),Vector2(.245,.09),Vector2(.18,.04)],12,"earthenware")
	_save_generated("onggi_jar", "0.68 x 0.72 x 0.68; broad ceramic body and open rim; matte constant-color material; no liquid/collision")
	parts.clear()
	_box(Vector3(0,.28,0),Vector3(.29,.42,.29),"paper")
	for x in [-.17,.17]:
		for z in [-.17,.17]:_box(Vector3(x,.28,z),Vector3(.035,.52,.035),"wood")
	for y in [.02,.54]:_box(Vector3(0,y,0),Vector3(.38,.04,.38),"wood")
	_box(Vector3(0,.59,0),Vector3(.025,.08,.025),"iron")
	_save_generated("square_paper_lantern", "0.38 x 0.63 x 0.38; square timber-and-paper lantern; base center; light separate; no emissive baked albedo")
	var source_hashes: Array[Dictionary] = []
	for filename in ["floor.glb","wall.glb","stairs_up.glb","stairs_down.glb","floor_floor_tex_raw.png","wall_wall_tex_raw.png","stairs_up_0.png","stairs_down_0.png"]:
		source_hashes.append({"file":filename,"sha256":FileAccess.get_sha256(SOURCE+filename)})
	_write_json("res://module_report.json", {"generated_utc":Time.get_datetime_string_from_system(true),"engine":Engine.get_version_info(),"generator":"Godot GLTFDocument + procedural candidate geometry; Blender candidate-only stair simplification; no image generation","unit":"1 unit = 1 tile","is_game_intake":false,"sources":source_hashes,"modules":records,"errors":errors,"limitations":["Candidates only; collision, navigation, runtime batching/cutaway integration not implemented","Stone albedos inherited unchanged; stairs retain inherited 2K textures","Door_frame and market_bay span 3 cells and must be placed as separate prop assemblies","Blank brazier and lantern omit light; effect is separate in the review scene","Timber, paper, ceramic and iron use matte constant colors; no newly painted surface grain; H1 texture finish is incomplete"]})
	print("H1 module build: %d candidates, %d errors" % [records.size(),errors.size()])
	quit(0 if errors.is_empty() else 2)

func _texture_mat(id: String, path: String) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.resource_name = "source_" + id
	mat.roughness = 1.0
	mat.albedo_texture = ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path(path)))
	return mat

func _color_mat(id: String, color: Color, rough: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.resource_name = id
	mat.albedo_color = color
	mat.roughness = rough
	return mat

func _configure_atlas(keys: Array) -> void:
	var config_path:="res://textures/atlas_layout.json"
	if not FileAccess.file_exists(config_path):return
	atlas_configuration=JSON.parse_string(FileAccess.get_file_as_string(config_path))
	var texture_path:String=atlas_configuration.texture
	atlas_texture=ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path(texture_path)))
	for key in keys:
		if not atlas_configuration.materials.has(key):continue
		var spec:Dictionary=atlas_configuration.materials[key]
		var mat:=StandardMaterial3D.new()
		mat.resource_name="h1_atlas_"+str(key)
		mat.albedo_texture=atlas_texture
		mat.roughness=1.0
		mat.texture_repeat=false
		var tint:Array=spec.get("tint",[1,1,1])
		mat.albedo_color=Color(tint[0],tint[1],tint[2])
		mats[key]=mat
		atlas_regions[key]=spec

func _atlas_uv(uv: Vector2,material: String) -> Vector2:
	if not atlas_regions.has(material):return uv
	var spec:Dictionary=atlas_regions[material]
	var offset:Array=spec.offset
	var uv_scale:Array=spec.scale
	return Vector2(offset[0],offset[1])+uv*Vector2(uv_scale[0],uv_scale[1])

func _add_tri(a: Vector3,b: Vector3,c: Vector3,n: Vector3,uv_a: Vector2,uv_b: Vector2,uv_c: Vector2,material: String) -> void:
	if not parts.has(material):
		parts[material] = {"vertices":PackedVector3Array(),"normals":PackedVector3Array(),"uvs":PackedVector2Array(),"indices":PackedInt32Array()}
	var vertices := [a,b,c]
	var uvs := [uv_a,uv_b,uv_c]
	if (b-a).cross(c-a).dot(n)>0:
		vertices = [a,c,b]
		uvs = [uv_a,uv_c,uv_b]
	var part: Dictionary = parts[material]
	for i in 3:
		part.indices.append(part.vertices.size())
		part.vertices.append(vertices[i])
		part.normals.append(n.normalized())
		part.uvs.append(_atlas_uv(uvs[i],material))

func _quad(v: Array,n: Vector3,material: String) -> void:
	# Align timber's grain axis with each broad face's longer edge. UV transform
	# goes into actual vertices; no edited/cropped raster or texture-transform extension.
	if atlas_regions.has(material) and material in ["wood","dark_wood"] and v[0].distance_to(v[3])>v[0].distance_to(v[1]):
		_add_tri(v[0],v[1],v[2],n,Vector2(0,0),Vector2(1,0),Vector2(1,1),material)
		_add_tri(v[0],v[2],v[3],n,Vector2(0,0),Vector2(1,1),Vector2(0,1),material)
		return
	_add_tri(v[0],v[1],v[2],n,Vector2(0,0),Vector2(0,1),Vector2(1,1),material)
	_add_tri(v[0],v[2],v[3],n,Vector2(0,0),Vector2(1,1),Vector2(1,0),material)

func _box(center: Vector3,size: Vector3,material: String) -> void:
	var a := center-size/2
	var b := center+size/2
	_quad([Vector3(a.x,b.y,a.z),Vector3(a.x,b.y,b.z),Vector3(b.x,b.y,b.z),Vector3(b.x,b.y,a.z)],Vector3.UP,material)
	_quad([Vector3(a.x,a.y,a.z),Vector3(a.x,a.y,b.z),Vector3(b.x,a.y,b.z),Vector3(b.x,a.y,a.z)],Vector3.DOWN,material)
	# Split tall side faces into approximately unit-high UV spans.
	var count := maxi(1,int(ceil(size.y)))
	for i in count:
		var y0 := lerpf(a.y,b.y,float(i)/count)
		var y1 := lerpf(a.y,b.y,float(i+1)/count)
		_quad([Vector3(a.x,y1,b.z),Vector3(a.x,y0,b.z),Vector3(b.x,y0,b.z),Vector3(b.x,y1,b.z)],Vector3.BACK,material)
		_quad([Vector3(b.x,y1,a.z),Vector3(b.x,y0,a.z),Vector3(a.x,y0,a.z),Vector3(a.x,y1,a.z)],Vector3.FORWARD,material)
		_quad([Vector3(b.x,y1,b.z),Vector3(b.x,y0,b.z),Vector3(b.x,y0,a.z),Vector3(b.x,y1,a.z)],Vector3.RIGHT,material)
		_quad([Vector3(a.x,y1,a.z),Vector3(a.x,y0,a.z),Vector3(a.x,y0,b.z),Vector3(a.x,y1,b.z)],Vector3.LEFT,material)

func _prism(ring: PackedVector2Array,y0: float,y1: float,side_mat: String,cap_mat: String,split_height: bool) -> void:
	for i in ring.size():
		var p := ring[i]
		var q := ring[(i+1)%ring.size()]
		var outward := Vector3(q.y-p.y,0,p.x-q.x).normalized()
		var bands := maxi(1,int(ceil(y1-y0))) if split_height else 1
		for j in bands:
			var low := lerpf(y0,y1,float(j)/bands)
			var high := lerpf(y0,y1,float(j+1)/bands)
			_quad([Vector3(p.x,high,p.y),Vector3(p.x,low,p.y),Vector3(q.x,low,q.y),Vector3(q.x,high,q.y)],outward,side_mat)
	for i in range(1,ring.size()-1):
		for y in [y0,y1]:
			var n := Vector3.UP if y==y1 else Vector3.DOWN
			_add_tri(Vector3(ring[0].x,y,ring[0].y),Vector3(ring[i].x,y,ring[i].y),Vector3(ring[i+1].x,y,ring[i+1].y),n,ring[0]+Vector2(.5,.5),ring[i]+Vector2(.5,.5),ring[i+1]+Vector2(.5,.5),cap_mat)

func _bowl(y0: float,y1: float,r0: float,r1: float,thickness: float,sides: int,material: String) -> void:
	for i in sides:
		var a := float(i)/sides*TAU
		var b := float(i+1)/sides*TAU
		var ra := Vector3(cos(a),0,sin(a))
		var rb := Vector3(cos(b),0,sin(b))
		var p0 := ra*r0+Vector3.UP*y0
		var q0 := rb*r0+Vector3.UP*y0
		var p1 := ra*r1+Vector3.UP*y1
		var q1 := rb*r1+Vector3.UP*y1
		var normal := (ra+rb+Vector3.DOWN*((r1-r0)/(y1-y0))*2).normalized()
		_quad([p1,p0,q0,q1],normal,material)
		var ip0 := ra*(r0-thickness)+Vector3.UP*(y0+thickness)
		var iq0 := rb*(r0-thickness)+Vector3.UP*(y0+thickness)
		var ip1 := ra*(r1-thickness)+Vector3.UP*y1
		var iq1 := rb*(r1-thickness)+Vector3.UP*y1
		_quad([ip1,ip0,iq0,iq1],-normal,material)
		_quad([p1,ip1,iq1,q1],Vector3.UP,material)
		_add_tri(Vector3(0,y0+thickness,0),ip0,iq0,Vector3.UP,Vector2(.5,.5),Vector2(0,0),Vector2(1,0),material)
		_add_tri(Vector3(0,y0,0),p0,q0,Vector3.DOWN,Vector2(.5,.5),Vector2(0,0),Vector2(1,0),material)

func _slab(top: Array,thickness: float,material: String) -> void:
	var normal:Vector3=(top[1]-top[0]).cross(top[2]-top[0]).normalized()
	if normal.y<0:normal=-normal
	_quad(top,normal,material)
	var bottom:Array=[]
	for p in top:bottom.append(p-Vector3.UP*thickness)
	_quad(bottom,-normal,material)
	var center:Vector3=(top[0]+top[1]+top[2]+top[3])/4
	for i in 4:
		var j: int=(i+1)%4
		var outward:Vector3=((top[i]+top[j])/2-center).normalized()
		_quad([top[i],bottom[i],bottom[j],top[j]],outward,material)

func _lathe(profile: Array,sides: int,material: String) -> void:
	for row in profile.size()-1:
		var p:Vector2=profile[row]
		var q:Vector2=profile[row+1]
		for i in sides:
			var a:=TAU*float(i)/sides
			var b:=TAU*float(i+1)/sides
			var ra:=Vector3(cos(a),0,sin(a))
			var rb:=Vector3(cos(b),0,sin(b))
			var mid:Vector3=(ra+rb).normalized()
			var n:Vector3=(mid*(q.y-p.y)+Vector3.UP*(p.x-q.x)).normalized()
			_quad([ra*p.x+Vector3.UP*p.y,ra*q.x+Vector3.UP*q.y,rb*q.x+Vector3.UP*q.y,rb*p.x+Vector3.UP*p.y],n,material)
	for i in sides:
		var a:=TAU*float(i)/sides
		var b:=TAU*float(i+1)/sides
		var p:Vector2=profile[0]
		var q:Vector2=profile[-1]
		_add_tri(Vector3(0,p.y,0),Vector3(cos(a)*p.x,p.y,sin(a)*p.x),Vector3(cos(b)*p.x,p.y,sin(b)*p.x),Vector3.DOWN,Vector2(.5,.5),Vector2(0,0),Vector2(1,0),material)
		_add_tri(Vector3(0,q.y,0),Vector3(cos(a)*q.x,q.y,sin(a)*q.x),Vector3(cos(b)*q.x,q.y,sin(b)*q.x),Vector3.UP,Vector2(.5,.5),Vector2(0,0),Vector2(1,0),material)

func _disc(center: Vector3,radius: float,depth: float,sides: int,material: String) -> void:
	for i in sides:
		var a:=TAU*float(i)/sides
		var b:=TAU*float(i+1)/sides
		var p:=Vector3(cos(a)*radius,sin(a)*radius,0)
		var q:=Vector3(cos(b)*radius,sin(b)*radius,0)
		var front:=center+Vector3.BACK*depth/2
		var back:=center-Vector3.BACK*depth/2
		_add_tri(front,front+p,front+q,Vector3.BACK,Vector2(.5,.5),Vector2(0,0),Vector2(1,0),material)
		_add_tri(back,back+p,back+q,Vector3.FORWARD,Vector2(.5,.5),Vector2(0,0),Vector2(1,0),material)
		_quad([front+p,back+p,back+q,front+q],(p+q).normalized(),material)

func _tri_bar(start: Vector3,end: Vector3,radius: float,material: String) -> void:
	var axis:Vector3=(end-start).normalized()
	var side:=Vector3.RIGHT*radius
	var up:Vector3=axis.cross(Vector3.RIGHT).normalized()*radius
	if up.y<0:up=-up
	var offsets:Array=[-side,side,up]
	for i in 3:
		var j:int=(i+1)%3
		var outward:Vector3=((offsets[i]+offsets[j])/2-up/3).normalized()
		_quad([start+offsets[i],end+offsets[i],end+offsets[j],start+offsets[j]],outward,material)
	_add_tri(start+offsets[0],start+offsets[1],start+offsets[2],-axis,Vector2(0,0),Vector2(1,0),Vector2(.5,1),material)
	_add_tri(end+offsets[0],end+offsets[1],end+offsets[2],axis,Vector2(0,0),Vector2(1,0),Vector2(.5,1),material)

func _save_generated(id: String,contract: String) -> void:
	var mesh := ArrayMesh.new()
	for key in parts:
		var p: Dictionary = parts[key]
		var arrays: Array = []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX]=p.vertices
		arrays[Mesh.ARRAY_NORMAL]=p.normals
		arrays[Mesh.ARRAY_TEX_UV]=p.uvs
		arrays[Mesh.ARRAY_INDEX]=p.indices
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
		mesh.surface_set_material(mesh.get_surface_count()-1,mats[key])
	var root := Node3D.new()
	root.name=id
	var mi := MeshInstance3D.new()
	mi.name="CandidateMesh"
	mi.mesh=mesh
	root.add_child(mi)
	mi.owner=root
	_export(root,id)
	root.free()
	_analyze(id,contract,"procedural candidate with matte materials; existing stone textures only where present")

func _source_candidate(id: String,source_id: String,flip: bool,contract: String) -> void:
	if not flip:
		DirAccess.copy_absolute(ProjectSettings.globalize_path("res://prepared/"+source_id+".glb"),ProjectSettings.globalize_path(OUTPUT+id+".glb"))
	else:
		var root := _load(SOURCE+source_id+".glb")
		for node in root.find_children("*","MeshInstance3D",true,false):
			var instance := node as MeshInstance3D
			var mesh := ArrayMesh.new()
			for surface in instance.mesh.get_surface_count():
				var arrays := instance.mesh.surface_get_arrays(surface)
				var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
				if indices.is_empty():
					for i in arrays[Mesh.ARRAY_VERTEX].size(): indices.append(i)
				for i in range(0,indices.size(),3):
					var swap := indices[i+1]
					indices[i+1]=indices[i+2]
					indices[i+2]=swap
				arrays[Mesh.ARRAY_INDEX]=indices
				mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
				mesh.surface_set_material(surface,instance.get_active_material(surface))
			instance.mesh=mesh
		_export(root,id)
		root.free()
	_analyze(id,contract,"source winding corrected" if flip else "source candidate-only budget decimation; original preserved")

func _load(path: String) -> Node3D:
	var doc:=GLTFDocument.new()
	var state:=GLTFState.new()
	var err:=doc.append_from_file(ProjectSettings.globalize_path(path),state)
	if err!=OK:
		errors.append("GLTF load %d: %s" % [err,path])
		return null
	return doc.generate_scene(state) as Node3D

func _export(root: Node3D,id: String) -> void:
	var doc:=GLTFDocument.new()
	var state:=GLTFState.new()
	var err:=doc.append_from_scene(root,state)
	if err==OK: err=doc.write_to_filesystem(state,ProjectSettings.globalize_path(output_dir+id+".glb"))
	if err!=OK: errors.append("GLTF export %d: %s" % [err,id])

func _analyze(id: String,contract: String,derivation: String) -> void:
	var path:=output_dir+id+".glb"
	var root:=_load(path)
	var bounds:=AABB()
	var first:=true
	var triangles:=0
	var wrong:=0
	var degenerate:=0
	var mat_info: Array[Dictionary]=[]
	var vertex_min:=Vector3(INF,INF,INF)
	var vertex_max:=Vector3(-INF,-INF,-INF)
	for node in root.find_children("*","MeshInstance3D",true,false):
		var mi:=node as MeshInstance3D
		var transform:=_to_root(mi,root)
		var box:AABB=transform*mi.mesh.get_aabb()
		bounds=box if first else bounds.merge(box)
		first=false
		for s in mi.mesh.get_surface_count():
			var arrays:=mi.mesh.surface_get_arrays(s)
			var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
			for point in vertices:
				vertex_min=vertex_min.min(transform*point)
				vertex_max=vertex_max.max(transform*point)
			var normals:PackedVector3Array=arrays[Mesh.ARRAY_NORMAL]
			var idx:PackedInt32Array=arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
			if idx.is_empty():
				for i in vertices.size():idx.append(i)
			triangles+=int(idx.size()/3)
			for i in range(0,idx.size(),3):
				var geometric:Vector3=(vertices[idx[i+1]]-vertices[idx[i]]).cross(vertices[idx[i+2]]-vertices[idx[i]])
				if geometric.length_squared()<0.000000000001: degenerate+=1
				elif not normals.is_empty() and geometric.dot(normals[idx[i]]+normals[idx[i+1]]+normals[idx[i+2]])>0.00000001:wrong+=1
			var mat:=mi.get_active_material(s) as StandardMaterial3D
			var entry:Dictionary={"name":mat.resource_name if mat else "unknown"}
			if mat:
				entry.roughness=mat.roughness
				entry.cull_mode=mat.cull_mode
				entry.color=[mat.albedo_color.r,mat.albedo_color.g,mat.albedo_color.b,mat.albedo_color.a]
				entry.texture_size=[mat.albedo_texture.get_width(),mat.albedo_texture.get_height()] if mat.albedo_texture else []
			mat_info.append(entry)
	var record:Dictionary={"id":id,"file":output_dir.trim_prefix("res://")+id+".glb","sha256":FileAccess.get_sha256(path),"contract":contract,"derivation":derivation,"aabb_position":[bounds.position.x,bounds.position.y,bounds.position.z],"aabb_size":[bounds.size.x,bounds.size.y,bounds.size.z],"triangles":triangles,"under_500_triangles":triangles<=500,"cw_winding_normal_disagreements":wrong,"degenerate_triangles":degenerate,"materials":mat_info,"is_game_intake":false}
	records.append(record)
	record.vertex_aabb_position=[vertex_min.x,vertex_min.y,vertex_min.z]
	var vertex_size:=vertex_max-vertex_min
	record.vertex_aabb_size=[vertex_size.x,vertex_size.y,vertex_size.z]
	_write_json(output_dir+id+".json",record)
	if wrong>0: errors.append("Winding / normals disagree on %s: %d triangles" % [id,wrong])
	root.free()

func _to_root(node: Node3D,root: Node3D) -> Transform3D:
	var result:=Transform3D.IDENTITY
	var current:Node=node
	while current!=root and current is Node3D:
		result=(current as Node3D).transform*result
		current=current.get_parent()
	return result

func _write_json(path: String,value: Variant) -> void:
	var file:=FileAccess.open(path,FileAccess.WRITE)
	file.store_string(JSON.stringify(value,"\t")+"\n")
