extends "res://build_modules.gd"

func _build() -> void:
	output_dir="res://props/"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output_dir))
	mats.steel=_color_mat("matte_blade",Color(.58,.61,.64),.67)
	mats.brass=_color_mat("aged_brass",Color(.33,.27,.16),.85)
	mats.grip=_color_mat("dark_wrap",Color(.065,.052,.043),1.0)
	mats.wood=_color_mat("worn_timber",Color(.21,.13,.07),1.0)
	mats.dark_wood=_color_mat("dark_scabbard",Color(.055,.061,.066),1.0)
	mats.paper=_color_mat("talisman_paper",Color(.58,.52,.39),1.0)
	mats.ink=_color_mat("talisman_ink",Color(.07,.065,.055),1.0)
	mats.stamp=_color_mat("talisman_stamp",Color(.31,.09,.06),1.0)
	_configure_atlas(["wood","dark_wood"])
	for name in ["paper","ink","stamp"]:(mats[name] as StandardMaterial3D).cull_mode=BaseMaterial3D.CULL_DISABLED
	parts.clear()
	_blade()
	_lathe([Vector2(.017,-.115),Vector2(.015,.045)],8,"grip")
	_lathe([Vector2(.022,-.135),Vector2(.022,-.115)],8,"brass")
	var guard_ring:=PackedVector2Array()
	for i in 12:guard_ring.append(Vector2(cos(TAU*float(i)/12)*.06,sin(TAU*float(i)/12)*.018))
	_prism(guard_ring,.045,.065,"brass","brass",false)
	for y in [-.09,-.055,-.02,.015]:_lathe([Vector2(.017,y),Vector2(.017,y+.008)],8,"dark_wood")
	_save_generated("doho_sword","Grip origin (0,0,0); +Y blade tip; XY broad face; blade Y=.06..80 (0.74u); hilt .16u; no skeleton; matches current ActorVisual proxy scale")
	parts.clear()
	# Hollow mouth and shell sized around blade width .035 / thickness .008.
	_box(Vector3(-.0255,.375,0),Vector3(.007,.75,.034),"dark_wood")
	_box(Vector3(.0255,.375,0),Vector3(.007,.75,.034),"dark_wood")
	_box(Vector3(0,.375,-.0125),Vector3(.044,.75,.009),"dark_wood")
	_box(Vector3(0,.375,.0125),Vector3(.044,.75,.009),"dark_wood")
	_box(Vector3(0,.756,0),Vector3(.060,.012,.036),"brass")
	for y in [.02,.52,.72]:
		_box(Vector3(-.031,y,0),Vector3(.008,.025,.038),"brass")
		_box(Vector3(.031,y,0),Vector3(.008,.025,.038),"brass")
		_box(Vector3(0,y,-.018),Vector3(.064,.025,.006),"brass")
		_box(Vector3(0,y,.018),Vector3(.064,.025,.006),"brass")
	_save_generated("doho_scabbard","Mouth origin (0,0,0); +Y sheath tip; internal opening .044 x .016; usable depth .75; place at sword local Y=.06 for fit diagnostic; no attachment approved")
	parts.clear()
	_lathe([Vector2(.020,-.12),Vector2(.024,-.09),Vector2(.021,.06),Vector2(.026,.12),Vector2(.055,.28),Vector2(.075,.62),Vector2(.067,.68)],8,"wood")
	for y in [-.085,-.045,-.005,.035]:_lathe([Vector2(.024,y),Vector2(.024,y+.025)],8,"grip")
	_save_generated("bandit_club","Grip origin (0,0,0); +Y striking end; .80u overall Y length; grip around origin; wooden club only, no skeleton/attack integration")
	parts.clear()
	# A genuinely zero-thickness XY sheet. Adjacent color cells share the same plane;
	# there are no offset decal faces or solid box thickness.
	for row in 20:
		for col in 6:
			var material: String="paper"
			if row>=2 and row<=16 and col>=2 and col<=3 and row%3!=0:material="ink"
			if row in [5,8,11] and col in [1,4]:material="ink"
			if row>=14 and row<=16 and col>=1 and col<=4:material="stamp"
			var x0:float=-.04+float(col)*.08/6
			var x1:float=-.04+float(col+1)*.08/6
			var y0:float=-float(row)*.32/20
			var y1:float=-float(row+1)*.32/20
			_quad([Vector3(x0,y0,0),Vector3(x0,y1,0),Vector3(x1,y1,0),Vector3(x1,y0,0)],Vector3.BACK,material)
	_save_generated("paper_talisman","Zero-thickness double-sided XY sheet .08 x .32; top-edge pinch origin; extends -Y; +Z front; matte vertex-region colors, abstract marks; no paper simulation")
	_write_json("res://props_report.json",{"generated_utc":Time.get_datetime_string_from_system(true),"props":records,"engine":Engine.get_version_info(),"errors":errors,"is_game_intake":false,"sword_contract_source":"actors/actor_visual.gd::make_placeholder_sword, copied numeric dimensions only","sheath_fit":{"blade_width":.035,"blade_thickness":.008,"blade_length":.74,"cavity_width":.044,"cavity_thickness":.016,"cavity_depth":.75,"clearance_width_total":.009,"clearance_thickness_total":.008,"tip_clearance":.01,"sheath_origin_in_sword_local":[0,.06,0]},"limitations":["Matte geometry candidates, not illustration-level finish","H1 hand is open; attachability does not certify grip or animation contact","No main weapon_scene, socket offset or runtime asset changed"]})
	print("H1 props build: %d candidates, %d errors" % [records.size(),errors.size()])
	quit(0 if errors.is_empty() else 2)

func _blade() -> void:
	var lower:Array=[Vector3(-.0175,.06,0),Vector3(0,.06,.004),Vector3(.0175,.06,0),Vector3(0,.06,-.004)]
	var upper:Array=[Vector3(-.014,.72,0),Vector3(0,.72,.004),Vector3(.014,.72,0),Vector3(0,.72,-.004)]
	var tip:=Vector3(0,.80,0)
	for i in 4:
		var j:int=(i+1)%4
		var n:Vector3=(lower[i]+lower[j])/2-Vector3(0,.06,0)
		_quad([lower[i],upper[i],upper[j],lower[j]],n.normalized(),"steel")
		_add_tri(upper[i],tip,upper[j],n.normalized(),Vector2(0,0),Vector2(.5,1),Vector2(1,0),"steel")
	_add_tri(lower[0],lower[1],lower[2],Vector3.DOWN,Vector2(0,0),Vector2(.5,1),Vector2(1,0),"steel")
	_add_tri(lower[0],lower[2],lower[3],Vector3.DOWN,Vector2(0,0),Vector2(1,0),Vector2(.5,1),"steel")
