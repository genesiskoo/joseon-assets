extends SceneTree
## #274 read-only UiSkin fixture. No ItemDef/GemDef or installed textures are edited.

class Plate extends Node2D:
	var skin
	var heading: Font
	var body: Font
	var rows: Array[Dictionary] = []
	var mode := "actual"

	func label(at: Vector2, value: String, px: int = 15, strong: bool = false) -> void:
		draw_string(heading if strong else body, at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color("e5d5bd") if strong else Color("b9ad99"))

	func icon(rect: Rect2, row: Dictionary, variant: String = "actual", padding: float = 8.0) -> void:
		var tex: Texture2D = row.gray if variant == "grayscale" else row.texture
		assert(tex.resource_path.begins_with("res://assets/sprites/ui/icons_a/qa274/"))
		if variant == "black":
			draw_rect(rect, Color.BLACK)
			draw_rect(rect, skin.SLOT_RIM, false, 1.0)
		else:
			skin.item_slot(self, rect, true)
		assert(skin.item_icon(self, rect, tex, 1.0, padding))

	func native(rect: Rect2, tex: Texture2D, variant: String = "actual") -> void:
		draw_rect(rect, Color.BLACK if variant == "black" else skin.ITEM_OCCUPIED)
		draw_texture_rect(tex, rect, false)

	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1280, 960), Color("211d19"))
		if mode == "horibyeong":
			label(Vector2(24, 37), "#274 호리병 · 원본/알파 분리와 1×2 임시 아트 규격", 25, true)
			label(Vector2(24, 69), "Comfy 원본 RGB 보존 · 실제 ID/효능/최종 정의는 #265 의존 · 후보 미반입", 16)
			var row: Dictionary = rows.back()
			label(Vector2(39, 120), "생성 raw 1024×1536", 20, true)
			label(Vector2(388, 120), "BiRefNet clean · RGB 동일", 20, true)
			native(Rect2(40, 144, 300, 450), row.generated)
			native(Rect2(389, 144, 300, 450), row.source)
			label(Vector2(746, 120), "동일 UiSkin 함수·필터·콘텐츠 영역", 20, true)
			for i in 3:
				var variant: String = ["actual", "grayscale", "black"][i]
				var x: float = 758.0 + i * 169.0
				label(Vector2(x, 163), ["어두운 칸", "무채색", "검정 진단"][i], 18, true)
				icon(Rect2(x + 18, 194, 40, 80), row, variant, 8.0)
				label(Vector2(x - 4, 303), "가방40×80 · 여백8", 13)
				icon(Rect2(x + 15, 332, 48, 48), row, variant, 3.0)
				label(Vector2(x - 4, 409), "좌판48 · 여백3", 13)
				icon(Rect2(x, 441, 80, 160), row, variant, 6.0)
				label(Vector2(x - 4, 635), "임시 출력80×160", 13)
			label(Vector2(40, 665), "전체 박·마개·허리끈을 유지한 비율 보존 패킹 / 외곽 알파 여백 ≥6px / 수작업 알파·그림 수정 없음", 16)
			label(Vector2(40, 710), "1×2는 사양 기반 검수용이다. 실제 ItemDef·조합 UI·효능·세이브를 만들지 않았다.", 16)
			label(Vector2(40, 755), "오방옥20 + 호리병1 = 후보21 / #534 물약4 별도 / 승인 잔여25 유지", 16)
		else:
			label(Vector2(24, 37), "#274 오방옥 5색×4단 · " + {"actual": "어두운 칸", "grayscale": "무채색", "black": "검정 합성 진단"}[mode], 25, true)
			label(Vector2(24, 69), "원화 축소80 / 실제 가방40·여백8 / 좌판48·여백3 · 상위일수록 손상·세공·재질 개선 · 4단 이름 미확정", 15)
			for i in 20:
				var row: Dictionary = rows[i]
				var x: float = 16.0 + (i % 4) * 314.0
				var y: float = 99.0 + floori(i / 4.0) * 155.0
				draw_rect(Rect2(x, y, 303, 145), Color("29231e"))
				label(Vector2(x + 10, y + 23), String(row.spec.working_label), 18, true)
				var src: Texture2D = row.source80_gray if mode == "grayscale" else row.source80
				native(Rect2(x + 12, y + 36, 80, 80), src, mode)
				icon(Rect2(x + 123, y + 59, 40, 40), row, mode, 8.0)
				icon(Rect2(x + 214, y + 55, 48, 48), row, mode, 3.0)
				label(Vector2(x + 12, y + 133), "원화80", 13)
				label(Vector2(x + 113, y + 133), "가방40", 13)
				label(Vector2(x + 210, y + 133), "좌판48", 13)
		label(Vector2(24, 920), "UiSkin.item_slot/item_icon 실제 함수·선형 필터·비율 보존 / 제작 키는 게임 ID가 아님 / 후보21·PD 채택 대기", 15)
		label(Vector2(24, 946), "검수는 메모리의 독립 qa274 경로 사용. 기존 PNG·ItemDef·GemDef·홈·효능·세이브·UI 코드 변경0.", 14)


var pack_root := ""
var out_dir := ""
var mode := "actual"


func _initialize() -> void:
	_launch.call_deferred()


func _texture(path: String, resource_path: String) -> ImageTexture:
	var raw := Image.load_from_file(path)
	assert(raw != null)
	var tex := ImageTexture.create_from_image(raw)
	tex.take_over_path(resource_path)
	return tex


func _launch() -> void:
	await process_frame
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="): pack_root = arg.trim_prefix("--root=")
		if arg.begins_with("--out="): out_dir = arg.trim_prefix("--out=")
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
	assert(not pack_root.is_empty() and not out_dir.is_empty())
	assert(mode in ["actual", "grayscale", "black", "horibyeong"])
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	assert(manifest.card == 274 and manifest.items.size() == 21 and manifest.approved_remaining == 25)
	var plate := Plate.new()
	plate.skin = load("res://ui/ui_skin.gd")
	plate.body = load("res://ui/ui_fonts.gd").body()
	plate.heading = load("res://ui/ui_fonts.gd").heading()
	plate.mode = mode
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = Vector2i(1280, 960)
	root.title = "#274 read-only candidate UiSkin QA"
	var paths: Array[String] = []
	for spec in manifest.items:
		assert(spec.definition_state == "design_only" and spec.actual_item_id == null and spec.actual_gem_id == null)
		assert(spec.final_grade_name == null and spec.socket_count == null)
		var uid: String = spec.production_key
		var base: String = "res://assets/sprites/ui/icons_a/qa274/"
		var tex := _texture(pack_root.path_join(spec.game_path), base + "candidate_%s.png" % uid)
		assert(tex.get_size() == Vector2(int(spec.provisional_output_px[0]), int(spec.provisional_output_px[1])))
		var img: Image = tex.get_image()
		var used: Rect2i = img.get_used_rect()
		assert(used.position.x >= 6 and used.position.y >= 6)
		assert(used.end.x <= img.get_width() - 6 and used.end.y <= img.get_height() - 6)
		var source := _texture(pack_root.path_join(spec.source_path), base + "source_%s.png" % uid)
		var original := _texture(pack_root.path_join(spec.generated_path), base + "generated_%s.png" % uid)
		var gray := _texture(pack_root.path_join("qa/grayscale/%s.png" % uid), base + "gray_%s.png" % uid)
		var source80 := _texture(pack_root.path_join("qa/source80/%s.png" % uid), base + "source80_%s.png" % uid)
		var source80_gray := _texture(pack_root.path_join("qa/source80_gray/%s.png" % uid), base + "source80gray_%s.png" % uid)
		plate.rows.append({"spec": spec, "texture": tex, "source": source, "generated": original, "gray": gray, "source80": source80, "source80_gray": source80_gray})
		paths.append(tex.resource_path)
	root.add_child(plate)
	plate.queue_redraw()
	await process_frame
	await process_frame
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(out_dir.path_join("godot_%s.png" % mode)) == OK)
	var audit := {
		"card": 274, "mode": mode, "candidate_count": 21,
		"displayed_count": 1 if mode == "horibyeong" else 20,
		"runtime_itemdefs_modified": 0, "runtime_png_modified": 0,
		"memory_resource_paths": paths,
		"ui_functions": ["UiSkin.item_slot", "UiSkin.item_icon"],
		"ui_skin_source": "res://ui/ui_skin.gd",
		"bag_cell": [40, 80] if mode == "horibyeong" else [40, 40],
		"bag_padding": 8, "vendor_cell": [48, 48], "vendor_padding": 3,
		"canvas_size": [1280, 960], "filter": "linear",
		"definition_binding": "design_only; null IDs; no ItemDef/GemDef creation",
		"sprite_source": "Comfy clean; mechanical crop/premultiplied resize/pad only"
	}
	var output := FileAccess.open(out_dir.path_join("godot_%s.json" % mode), FileAccess.WRITE)
	assert(output != null)
	output.store_string(JSON.stringify(audit, "\t") + "\n")
	output.close()
	print("GODOT_274_PASS mode=", mode, " candidate21/UI-functions/render/null-definitions/alpha-margins/bag40p8/vendor48p3 validated; existing runtime unchanged")
	quit(0)
