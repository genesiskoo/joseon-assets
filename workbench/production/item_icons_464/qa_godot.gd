extends SceneTree
## #464 candidates through real UiSkin; transient texture identities; no runtime writes.
class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array = []
	var references: Array = []
	var mode := "after"
	func label(at:Vector2,text:String,size:int=15,strong:bool=false) -> void:
		draw_string(heading if strong else body,at,text,HORIZONTAL_ALIGNMENT_LEFT,-1,size,Color("e5d5bd") if strong else Color("a79b87"))
	func item(r:Rect2,row:Dictionary,black:bool=false) -> void:
		if black:
			draw_rect(r,Color.BLACK);draw_rect(r,skin.SLOT_RIM,false,1.0)
		else:skin.item_slot(self,r,true)
		assert(skin.item_icon(self,r,row.future,1.0,8.0))
	func _draw() -> void:
		draw_rect(Rect2(0,0,1280,760),Color("211d19"))
		label(Vector2(24,34),"#464 D1 T2 갑·포6 · " + ("실제 가방40px / 검정칸" if mode=="after" else "30·48·60px/칸"+ (" · 검정" if mode=="black_sizes" else " · 슬롯")),24,true)
		label(Vector2(24,64),"실제 공통 UiSkin · 전부2×3칸/쌓기1 · 후보는 검수 프로세스 메모리에서만 사용",15)
		for i in rows.size():
			var row:Dictionary=rows[i]
			var x:float=24+i*208
			label(Vector2(x,104),row.spec.display_name,20,true)
			if mode=="after":
				item(Rect2(x+52,155,80,120),row)
				item(Rect2(x+52,328,80,120),row,true)
			else:
				for j in 3:
					var side:int=[30,48,60][j]
					var y:int=[135,275,480][j]
					item(Rect2(x+32,y,side*2,side*3),row,mode=="black_sizes")
					label(Vector2(x+32,y+side*3+22),"%dpx/칸"%side,14)
		if mode=="after":
			label(Vector2(24,508),"화풍 기준 · 이미 채택한 D1 원본",18,true)
			for i in references.size():
				var row:Dictionary=references[i]
				var x:float=270+i*275
				item(Rect2(x,550,row.definition.size.x*40,row.definition.size.y*40),row)
				label(Vector2(x,715),row.definition.display_name,16)
		else:label(Vector2(24,738),"소재 구획/깃/테두리 검수 · 30px에서는 사슬 고리 하나/못 머리 하나의 세부 판독은 제한됨",15)
var pack_root := ""
var out_dir := ""
var mode := "after"
func _initialize() -> void:
	call_deferred("_launch")
func _launch() -> void:
	await process_frame
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="):pack_root=arg.trim_prefix("--root=")
		if arg.begins_with("--out="):out_dir=arg.trim_prefix("--out=")
		if arg.begins_with("--mode="):mode=arg.trim_prefix("--mode=")
	assert(not pack_root.is_empty() and not out_dir.is_empty())
	var config=JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(config.items.size()>0 and config.items.size()<=6)
	var p:=Plate.new();p.skin=load("res://ui/ui_skin.gd");p.body=ThemeDB.fallback_font
	p.heading=load("res://ui/ui_fonts.gd").heading();p.mode=mode
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_DISABLED;root.size=Vector2i(1280,760)
	root.title="#464 D1 갑·포 원화 검수"
	for spec in config.items:
		var definition=load("res://data/items/%s.tres"%spec.item_id)
		assert(definition!=null and definition.icon!=null)
		assert(definition.size==Vector2i(2,3) and definition.size==Vector2i(spec.grid_w,spec.grid_h))
		assert(definition.display_name==spec.display_name and definition.slot==1 and definition.tier==2)
		assert(definition.max_stack==1 and not definition.quest_item)
		var image:=Image.load_from_file(pack_root.path_join("game/items/%s.png"%spec.item_id))
		assert(image!=null and image.get_size()==Vector2i(160,240))
		var texture:=ImageTexture.create_from_image(image)
		texture.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png"%spec.item_id)
		p.rows.append({"definition":definition,"future":texture,"spec":spec})
	for id in ["cotton_dopo","saingeom","hwando"]:
		var def=load("res://data/items/%s.tres"%id)
		p.references.append({"definition":def,"future":def.icon})
	root.add_child(p);p.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.35).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png"%mode))==OK)
	print("GODOT_D1_464_PASS mode=",mode," items=",config.items.size(),"; footprint/name/tier/render validated; no runtime intake")
	quit(0)
