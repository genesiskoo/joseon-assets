extends SceneTree
## #243 read-only-process art preview. No game asset/resource is saved.
var runner_api: Script
var band_api: Script
const PROD := "C:/workspace/joseon/._tmp/assets_87/workbench/production/dialogue-portraits-235"
const REPORT := "C:/workspace/joseon/._tmp/assets_87/reports/243/2026-09-28"
var snapshots: Array = []

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	await process_frame
	runner_api = load("res://core/dialogue_runner.gd")
	band_api = load("res://ui/dialogue_band.gd")
	root.get_node("SaveSystem").set("save_path", REPORT + "/preview_save.json")
	var saved: Dictionary = runner_api._portraits.duplicate()
	for actor in ["doho", "merchant"]:
		var def = runner_api.portrait_for(actor).duplicate(true)
		def.expressions.clear()
		var expressions: Array = ["neutral", "smug", "serious"] if actor == "doho" else ["neutral", "smile"]
		for tag in expressions:
			var img := Image.load_from_file(PROD + "/game/" + actor + "/" + tag + ".png")
			assert(img != null and not img.is_empty())
			def.expressions[tag] = ImageTexture.create_from_image(img)
		runner_api._portraits[actor] = def
	var main = load("res://world/main.tscn").instantiate()
	root.add_child(main)
	current_scene = main
	await create_timer(1.0).timeout
	var band = band_api.find(self)
	assert(band != null)
	var text := "~ start\ndoho: [#neutral] 영감, 오늘은 제값을 쳐 주시오. [ID:ART243_DN]\nmerchant: [#neutral] 물건부터 봅시다, 도사 양반. [ID:ART243_MN]\ndoho: [#smug] 내 칼솜씨만큼 값도 후하게 쳐 주면 좋겠는데. [ID:ART243_DS]\nmerchant: [#smile] 허허, 그 솜씨로 좋은 물건부터 가져오시구려. [ID:ART243_MS]\ndoho: [#serious] 굴 안쪽이 심상치 않소. 오늘은 오래 머물지 마시오. [ID:ART243_DR]\n=> END\n"
	var compiled: Dictionary = runner_api.compile(text, "res://data/dialogue/dev/art243_transient_preview.dialogue")
	assert(compiled.errors.is_empty(), str(compiled.errors))
	assert(band.start(compiled.resource, "", {}, ["doho", "merchant"]))
	await create_timer(0.15).timeout
	for side in ["L", "R"]:
		var p = band.portrait(side)
		assert(p != null)
		# Existing full-body foot anchor is unsuitable for mid-thigh static crops.
		# Virtual foot anchor + old sheet shadow hidden only in this QA process.
		p._sheet = p._sheet.duplicate()
		var cell: Vector2 = p._sheet.cell
		var unit: float = p.base_scale * cell.x / 1024.0
		var ax: float = 35.0 + (p.slot.x - 20.0) / unit if side == "L" else 990.0 - (1260.0 - p.slot.x) / unit
		var ay: float = 123.0 + (p.slot.y - 95.0) / unit
		p._sheet.anchor = Vector2(ax / 1024.0 * cell.x, ay / 1536.0 * cell.y)
		if p._body is Sprite2D:
			p._body.offset = -(p._sheet.anchor / cell) * Vector2(p._body.texture.get_size())
		if p._shadow != null:
			p._shadow.visible = false
	var ids := ["doho_neutral", "merchant_neutral", "doho_smug", "merchant_smile", "doho_serious"]
	for index in ids.size():
		await create_timer(0.6).timeout
		if band.is_typing():
			band.advance()
		await create_timer(0.2).timeout
		var line = band.current_line()
		assert(line != null)
		var who: String = line.speaker
		var portrait = band.portrait("L" if who == "doho" else "R")
		assert(portrait.body_kind() == "still")
		await RenderingServer.frame_post_draw
		var path: String = REPORT + "/preview_" + ids[index] + ".png"
		assert(root.get_texture().get_image().save_png(path) == OK)
		snapshots.append({"id": ids[index], "speaker": who, "expression": String(line.expression), "size": [root.size.x, root.size.y], "path": path, "preview_only": true, "static_anchor_adapted_in_memory": true, "legacy_idle_shadow_hidden": true})
		print("ART243_CAPTURE ", ids[index], " ", who, " ", line.expression)
		if index + 1 < ids.size():
			band.advance()
	var f := FileAccess.open(REPORT + "/preview_capture.json", FileAccess.WRITE)
	f.store_string(JSON.stringify({"card":243, "runtime_files_changed":false, "snapshots": snapshots}, "\t"))
	f.close()
	band.hide_now()
	runner_api._portraits = saved
	print("ART243_PREVIEW_PASS captures=5; transient anchors only; no runtime intake")
	quit(0)
