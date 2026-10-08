extends SceneTree
## Actual UiSkin rendering only. Unique icon lookup is explicitly not installed.
class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array = []
	var mode := "forty"
	func label(pos: Vector2, value: String, size: int = 15, strong: bool = false) -> void:
		draw_string(heading if strong else body, pos, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color("e5d5bd") if strong else Color("a79b87"))
	func item(rect: Rect2, texture: Texture2D, black: bool = false) -> void:
		if black:
			draw_rect(rect, Color.BLACK)
			draw_rect(rect, skin.SLOT_RIM, false, 1.0)
		else:
			skin.item_slot(self, rect, true)
		assert(skin.item_icon(self, rect, texture, 1.0, 8.0))
	func _draw() -> void:
		draw_rect(Rect2(0,0,1280,760),Color("211d19"))
		label(Vector2(25,40),"#483 대표유니크 장신구3 · 실제 UiSkin · "+mode,24,true)
		label(Vector2(25,73),"모두1×1 · 메모리의 후보 PNG만 렌더 · 유니크 전용 그림 연결은 아직 없음",15)
		for i in rows.size():
			var row: Dictionary=rows[i]
			var x: float=25.0+i*418.0
			label(Vector2(x,115),row.spec.display_name,21,true)
			if mode=="forty":
				var sizes: Array=[40,40,48]
				var ys: Array=[177.0,340.0,520.0]
				var names: Array=["가방40px","검정40px","좌판48px"]
				for j in 3:
					label(Vector2(x,ys[j]-18.0),names[j],15)
					item(Rect2(x+155.0,ys[j],sizes[j],sizes[j]),row.future,j==1)
			elif mode=="base_compare":
				label(Vector2(x,157),row.spec.base_display_name+" 채택 베이스 / 유니크 후보",15)
				for j in 3:
					var side: int=[30,40,60][j]
					var y: float=[195.0,360.0,530.0][j]
					label(Vector2(x,y-18.0),"%dpx · 같은 UiSkin 패킹"%side,15)
					item(Rect2(x+95.0,y,side,side),row.reference,true)
					item(Rect2(x+230.0,y,side,side),row.future,true)
			else:
				for j in 3:
					var side: int=[30,48,60][j]
					var y: float=[177.0,340.0,520.0][j]
					label(Vector2(x,y-18.0),"%dpx · 1×1칸"%side,15)
					item(Rect2(x+155.0,y,side,side),row.future,mode=="black_sizes")
		label(Vector2(25,718),"송곳니 호신부 / 짐승 눈빛의 놋거울 / 붉은 속무늬 여우구슬",16)
		label(Vector2(25,744),"기존PNG42·아이템/유니크 정의·런타임 코드 보존 · 실제 게임 설치 검수와 구별",14)

var pack_root := ""
var out_dir := ""
var mode := "forty"
func _initialize() -> void:
	call_deferred("_launch")
func _launch() -> void:
	await process_frame
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="): pack_root=arg.trim_prefix("--root=")
		if arg.begins_with("--out="): out_dir=arg.trim_prefix("--out=")
		if arg.begins_with("--mode="): mode=arg.trim_prefix("--mode=")
	assert(not pack_root.is_empty() and not out_dir.is_empty())
	var manifest=JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.items.size()==3)
	var plate:=Plate.new()
	plate.skin=load("res://ui/ui_skin.gd")
	plate.body=ThemeDB.fallback_font
	plate.heading=load("res://ui/ui_fonts.gd").heading()
	plate.mode=mode
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_DISABLED
	root.size=Vector2i(1280,760)
	root.title="#483 D1 유니크 장신구 검수"
	for spec in manifest.items:
		var unique=load("res://data/uniques/%s.tres"%spec.item_id)
		var base=load("res://data/items/%s.tres"%spec.base_id)
		assert(unique!=null and unique.display_name==spec.display_name and unique.base_id==spec.base_id)
		assert(base!=null and base.size==Vector2i(1,1) and base.slot==spec.slot and base.tier==spec.tier)
		var raw:=Image.load_from_file(pack_root.path_join(spec.game_path))
		assert(raw!=null and raw.get_size()==Vector2i(80,80))
		var tex:=ImageTexture.create_from_image(raw)
		tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png"%spec.item_id)
		var ref_raw:=Image.load_from_file(spec.base_reference_path)
		assert(ref_raw!=null)
		var ref_tex:=ImageTexture.create_from_image(ref_raw)
		ref_tex.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png"%spec.base_id)
		plate.rows.append({"spec":spec,"future":tex,"reference":ref_tex})
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png"%mode))==OK)
	print("GODOT_D1_483_PASS mode=",mode," items=3 unique/base footprint/name/tier/slot/render validated; no unique icon binding installed")
	quit(0)
