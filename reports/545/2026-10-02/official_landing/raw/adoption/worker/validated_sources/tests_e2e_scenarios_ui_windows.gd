extends E2eScenario
## UI 창 한 바퀴 (보드 #7·#8·#9, ui_v2.md): 캐릭터·가방·스킬·대화(NPC 3 — 대화 띠, #239)·좌판·서낭단·시작 화면을 열어 열림·화면 안 좌표를 검사하고
## 창 모드면 창마다 스크린샷(user://e2e/ui_windows_*.png) — 겹침·잘림 같은 미관은 그 그림으로 PD 눈 검수.

const VIEW := Rect2(0, 0, 1280, 720)


func _npc(id: String) -> Node:
	for n in t.tree.get_nodes_in_group("interactable"):
		if "def" in n and n.def is NpcDef and n.def.id == id:
			return n
	return null


## 대화 띠가 그 NPC 와 열렸나 — 첫 줄 = 그 사람 · 초상 = 왼쪽 도호 · 오른쪽 그 사람 (#239).
func _band_check(band: DialogueBand, id: String) -> void:
	var l = band.current_line()
	t.check(band.is_open() and l != null and l.speaker == id, "대화 띠(%s) 첫 줄 = %s (%s)" % [id, id, l.speaker if l != null else "-"])
	var pl := band.portrait("L")
	var pr := band.portrait("R")
	t.check(pl != null and pl.def.id == "doho" and pr != null and pr.def.id == id, "대화 띠(%s) 초상 = 도호 · %s" % [id, id])


func _open_check(panel: Node, label: String) -> bool:
	var ok := t.check(panel.visible, "%s 열림" % label)
	if ok:
		var pr: Rect2 = panel.panel_rect()
		t.check(VIEW.encloses(pr), "%s 창이 화면 안 (%s)" % [label, pr])
	return ok


## #111 수용: 검은 여백·잘림을 720p 숫자 검사만으로 놓치지 않도록 실제 창에서 세 해상도를 찍는다.
func _capture_three_sizes(panel: Node, label: String, is_title: bool) -> void:
	if not t.shots or DisplayServer.get_name() == "headless":
		return
	var window := t.tree.root
	var original := window.size
	for resolution in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080)]:
		window.size = resolution
		await t.frames(8)
		await RenderingServer.frame_post_draw
		t.check_eq(window.get_texture().get_image().get_size(), resolution, "%s 실제 렌더 치수" % label)
		var bounds := Rect2(Vector2.ZERO, panel.get_viewport_rect().size)
		if is_title:
			t.check(bounds.encloses(panel._btn_rect(0)) and bounds.encloses(panel._btn_rect(1)), "%s 메뉴 두 칸 화면 안" % label)
		else:
			t.check(bounds.encloses(panel.panel_rect()) and panel.panel_rect().encloses(panel._row_rect(panel._display_entries().size() - 1)), "%s 목적지 마지막 행 창 안" % label)
		await t.shot("%s_%dx%d" % [label, resolution.x, resolution.y])
	window.size = original
	await t.frames(5)


func run() -> void:
	var character: Node = t.hud_panel("Character")
	var inv_ui: Node = t.hud_panel("Inventory")
	var skills: Node = t.hud_panel("SkillTree")
	var band := t.band()
	var vendor: Node = t.hud_panel("Vendor")
	var wp_ui: Node = t.hud_panel("Waypoint")
	var title: Node = t.hud_panel("Title")
	var bar: Node = t.hud_panel("Bar")
	await t.shot("hud")
	# E2E는 --dev라 상단 개발 범례가 보인다. 출시 화면은 범례만 잠시 감추어 같은 구도를 따로 찍는다.
	var dev_legend_visible: bool = t.main.hud_label.visible
	t.main.hud_label.visible = false
	await t.shot("hud_clean")
	t.main.hud_label.visible = dev_legend_visible
	# #109: 조작 문구 없이 10%H 판, 창 그림 버튼, 필요할 때만 뜨는 점수 알림.
	t.check(bar.panel_rect().position.y == 648.0 and bar.panel_rect().size.y == 72.0, "HUD 가운데 판 72px(10%H)")
	t.check(not t.main.hud_label.text.contains("좌클릭") and not t.main.hud_label.text.contains("우클릭"), "상단 일반 조작 문장 0줄")
	# 그림 밖 빈 틈은 UI 캡처를 해제하며, 구슬과 판 위 경험치 선은 같은 hit_test를 쓴다.
	await t.mouse_move(Vector2(bar.panel_rect().position.x - 4, 680))
	await t.frames(2)
	t.check(not GameState.is_ui_captured(), "구슬과 중앙 판 사이 빈 틈 → 월드 입력 허용")
	await t.mouse_move(Vector2(72, 618))
	await t.frames(2)
	t.check(GameState.is_ui_captured(), "판 위로 솟은 생명 구슬 → UI 입력 포획")
	await t.mouse_move(Vector2(900, 647))
	await t.frames(2)
	var tooltip: Node = t.hud_panel("Tooltip")
	t.check(tooltip != null and tooltip.source_rect == bar.XP_RECT, "판 위 경험치 선 → 실제 호버 툴팁")
	await t.mouse_move(Vector2(600, 500))
	var start_pos: Vector3 = t.player().global_position
	await t.click(bar._button_rect(0).get_center())
	t.check(character.visible, "HUD 능력 그림 버튼 클릭 → 캐릭터 창")
	await t.click(bar._button_rect(1).get_center())
	t.check(inv_ui.visible, "HUD 가방 그림 버튼 클릭 → 가방")
	await t.click(bar._button_rect(2).get_center())
	t.check(skills.visible and not character.visible, "HUD 술법 그림 버튼 클릭 → 술법 창(왼쪽 배타)")
	await t.close_all()
	var menu: Node = t.hud_panel("SystemMenu")
	await t.click(bar._button_rect(3).get_center())
	t.check(menu.visible and t.tree.paused, "HUD 메뉴 그림 버튼 클릭 → 시스템 메뉴·일시정지")
	await t.key(KEY_ESCAPE)
	t.check(not menu.visible and not t.tree.paused, "메뉴 Esc → 게임 복귀")
	var old_points: int = int(GameState.character.get("stat_points", 0))
	GameState.character.stat_points = 1
	await t.frames(2)
	t.check(bar._point_available(0), "남은 능력 점수 → 구슬 곁 알림")
	await t.mouse_move(Vector2(600, 500))
	await t.frames(2)
	t.main.hud_label.visible = false
	await t.shot("point_notice")
	t.main.hud_label.visible = dev_legend_visible
	await t.click(bar._point_rect(0).get_center())
	t.check(character.visible and not bar._point_available(0), "점수 알림 클릭 → 능력 창, 열린 동안 알림 숨김")
	await t.key(KEY_C)
	GameState.character.stat_points = old_points
	t.check(t.player().global_position.distance_to(start_pos) < 0.05, "HUD 버튼·알림 클릭은 월드 이동으로 새지 않음")
	# 커서 호버 표시 (보드 #81): NPC 위 → 이름 + 동사, 바닥 아이템 위 → 등급색 이름 + 아이콘
	var tip: Node = t.tree.root.find_child("HoverTip", true, false)
	t.check(tip != null, "HoverTip 노드")
	var merchant: Node3D = _npc("merchant")
	if tip != null and merchant != null:
		# 창을 닫은 뒤 카메라 보간이 끝나야 같은 NPC 투영점을 실제로 겨냥한다.
		t.check(await t.wait_until(func() -> bool: return t.camera().ui_framing_settled(), 1.0), "창 닫힘 뒤 호버 투영 카메라 수렴")
		await t.mouse_move(t.screen_of(merchant.global_position + Vector3(0, 0.9, 0)))
		# 창 모드에서는 진짜 커서가 창 위에 있으면 주입 좌표를 덮어쓴다 — 한 프레임 단정 대신 잠깐 기다린다(실측 흔들림)
		await t.wait_until(func() -> bool: return GameState.hover == merchant, 1.0)
		t.check(GameState.hover == merchant, "NPC 위 → hover = 김 영감 (실제 %s)" % (GameState.hover.name if GameState.hover else "없음"))
		var merchant_label := merchant.get_node_or_null("Label") as Label3D
		# CursorPick과 NPC 이름표는 서로 다른 _process에서 갱신하므로 최종 표시를 기다린다.
		var name_hidden: bool = await t.wait_until(func() -> bool: return merchant_label != null and GameState.hover == merchant and not GameState.is_ui_captured() and not merchant_label.visible, 1.0)
		t.check(name_hidden, "NPC 호버 띠가 이름·동사를 맡으면 상시 이름표는 숨음")
		await t.shot("hover_npc")
		var p0: Node3D = t.player()
		EventBus.item_dropped.emit(ItemInstance.create(ItemDb.get_def("hwando")), p0.global_position + Vector3(1.3, 0, 1.3))
		await t.frames(3)
		var fi: Node3D = null
		for n in t.level().find_children("*", "Area3D", true, false):
			if n is FloorItem:
				fi = n
		if t.check(fi != null, "바닥 아이템 생성"):
			await t.mouse_move(t.screen_of(fi.global_position + Vector3(0, 0.3, 0)))
			await t.wait_until(func() -> bool: return GameState.hover == fi, 1.0)
			await t.shot("hover_item")
			fi.queue_free()
			await t.frames(2)
		await t.mouse_move(Vector2(40, 400))
		await t.wait_until(func() -> bool: return GameState.hover == null, 1.0)
		t.check(GameState.hover == null, "빈 바닥 위 → hover 없음")
		await t.frames(2)
		t.check(merchant_label != null and merchant_label.visible, "NPC 호버를 떠나면 상시 이름표 복귀")
	# 캐릭터 · 가방 · 스킬 (C·I·K)
	await t.key(KEY_C)
	_open_check(character, "캐릭터 창")
	await t.shot("character")
	await t.click(character.tab_rect(1).get_center())
	t.check(character._page == 1, "막이 보기로 전환")
	var resist_tip: Dictionary = character.tooltip_at(character.panel_rect().position + Vector2(90, 245))
	t.check(resist_tip.get("title", "") == "불막이" and (resist_tip.get("body", []) as Array).size() == 3, "막이 툴팁은 원래 값·벌점·상한")
	await t.shot("character_resistances")
	await t.click(character.tab_rect(0).get_center())
	t.check(character._page == 0, "능력 보기로 복귀")
	await t.click(character.close_rect().get_center())
	t.check(not character.visible, "캐릭터 창 주홍 X → 닫힘")
	await t.key(KEY_C)
	t.check(character.visible, "캐릭터 창 X 뒤 단축키로 다시 열림")
	await t.key(KEY_I)
	_open_check(inv_ui, "가방")
	await t.mouse_move(Vector2(620, 550))
	await t.frames(2)
	await t.shot("inventory")
	await t.key(KEY_K)
	_open_check(skills, "스킬 창")
	t.check(not character.visible, "스킬 창이 캐릭터 창을 닫음 (왼쪽 창 배타)")
	await t.mouse_move(Vector2(620, 550))
	await t.frames(2)
	await t.shot("skills")
	await t.close_all()
	t.check(not inv_ui.visible and not skills.visible, "Esc → 전부 닫힘")
	# NPC 대화 3 + 좌판 — 대화 = 대화 띠(#239). 컷 이름 dialog_<id> 와 자리는 옛 대화창 그대로(같은 NPC 앞) — 전/후 사진이 같은 구도가 되게
	# 띠가 뜨고 첫 줄이 다 찍히고 초상 등장(0.25초)이 끝난 뒤 찍는다.
	if not t.check(band != null, "대화 띠 노드"):
		return
	for id in ["merchant", "shaman", "elder"]:
		var npc := _npc(id)
		if not t.check(npc != null, "NPC %s" % id):
			continue
		var opened := await t.talk_to(npc)
		if not t.check(opened, "%s 클릭 → 대화 띠" % id):
			continue
		_band_check(band, id)
		await t.wait_until(func() -> bool: return not band.is_typing(), 5.0)
		await t.seconds(0.35)
		t.check(GameState.hover == null, "모달 대화 중 월드 호버 해제 (%s)" % id)
		await t.shot("dialog_" + id)
		if id == "merchant":
			# 좌판이 열린 그 순간의 띠 — 걷히는 초상·글자가 좌판·가방 위에 겹치면 안 된다(§3.6 hide_now, 창 모드 실측 겹침)
			var at_open := [-1.0, -1]
			var on_vis := func() -> void:
				if vendor.visible and at_open[1] < 0:
					at_open[0] = band.shown_alpha()
					at_open[1] = t.band_portraits()
			vendor.visibility_changed.connect(on_vis)
			t.check(await t.talk_pick("shop"), "「거래한다」 클릭")
			await t.wait_until(func() -> bool: return vendor.visible, 2.0)
			vendor.visibility_changed.disconnect(on_vis)
			t.check(not band.is_open(), "거래한다 → 띠 걷힘")
			t.check(at_open[0] == 0.0 and at_open[1] == 0, "좌판이 열린 그 순간 띠(초상·글자) 알파 0 (알파 %.2f · 초상 %d)" % [at_open[0], at_open[1]])
			_open_check(vendor, "좌판")
			await t.shot("vendor")
		await t.talk_close()
		await t.close_all()
	# 서낭단 (마을)
	var wp: Node = t.level().get_node_or_null("Waypoint")
	if t.check(wp != null, "마을 서낭단"):
		await t.click_world(wp.global_position + Vector3(0, 0.8, 0))
		var opened := await t.wait_until(func() -> bool: return wp_ui.visible, 8.0)
		if t.check(opened, "서낭단 클릭 → 창"):
			_open_check(wp_ui, "서낭단 창")
			t.check(wp_ui._display_entries() == ["motgol:0", "deulnyeok:0", "jeongnyeongjae:0", "bongmil_gul:2"] and wp_ui._entries().size() == 1, "서낭단 4곳 표시(봉밀굴 2층 포함), 새 판은 못골만 깨어남")
			await t.shot("waypoint")
			await _capture_three_sizes(wp_ui, "waypoint", false)
			await t.click(wp_ui._row_rect(1).get_center())
			t.check(wp_ui.visible and GameState.is_town() and wp_ui._msg.contains("아직"), "잠긴 들녘 행은 이동하지 않고 안내")
		await t.close_all()
	# 저장 있음/없음: 같은 자리에 두 메뉴, 없는 저장의 이어하기만 비활성.
	title.set_open(true)
	await t.frames(2)
	t.check(title.visible and title._has_save(), "저장 있는 시작 화면 열림")
	await t.shot("title")
	await _capture_three_sizes(title, "title", true)
	title.set_open(false)
	await t.frames(2)
	t.check(not title.visible, "시작 화면 닫힘")
	# 렌더 텍스처는 창 모드 촬영 때만 존재한다 (automap/skill_picker와 같은 문턱).
	if t.shots and DisplayServer.get_name() != "headless":
		await t.key(KEY_C)
		await t.key(KEY_I)
		var window := t.tree.root
		var before_size := window.size
		for resolution in [Vector2i(1280, 720), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
			window.size = resolution
			await t.frames(8)
			await RenderingServer.frame_post_draw
			var view := Rect2(Vector2.ZERO, Vector2(resolution))
			t.check_eq(window.get_texture().get_image().get_size(), resolution, "목조 UI 실제 렌더 해상도")
			t.check(view.encloses(character.panel_rect()) and view.encloses(inv_ui.panel_rect()), "목조 UI 양쪽 창 화면 안 (%s)" % resolution)
			t.check(character.panel_rect().encloses(character.close_rect()) and inv_ui.panel_rect().encloses(inv_ui.close_rect()), "주홍 X 클릭 영역 창 안 (%s)" % resolution)
			await t.shot("wood_skin_%dx%d" % [resolution.x, resolution.y])
		window.size = before_size
		await t.frames(5)
		await t.close_all()
	var old_title_context := SaveSystem.save_path
	SaveSystem.use_save_context("user://ui_windows_550_" + str(Time.get_ticks_usec()) + ".json")
	t.main.show_title()
	await t.frames(2)
	t.check(title.visible and not title._has_save(), "저장 없는 타이틀: 저장된 캐릭터 없음")
	await t.shot("title_no_save")
	await t.click(title._btn_rect(1).get_center())
	t.check(title.visible and title.screen == title.Screen.CREATE and not SaveSystem.has_save(), "저장 없는 선택은 생성 안내, 파일은 아직 없음")
	title.name_input.text = "UIWindowDoho"
	await t.click(title.confirm_rect().get_center())
	t.check(not title.visible and t.main._started and SaveSystem.has_save(), "생성 확인 클릭 → 별도 첫 판·저장")
	var created_profile_directory := SaveSystem.profile_directory()
	SaveSystem.delete_save()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(created_profile_directory))
	SaveSystem.use_save_context(old_title_context)
