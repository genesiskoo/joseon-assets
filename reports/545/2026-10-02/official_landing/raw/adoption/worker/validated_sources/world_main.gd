extends Node3D
## Main — 영속 셸 (청사진 §5). Player·카메라·HUD는 여기 살고, 레벨(마을/던전 층)만 WorldRoot 아래서 교체된다.
## 왜 이 구조인가: 레벨을 갈아끼워도 인벤·스탯을 든 Player가 살아남아야 함(v1 D-062의 뼈대만 계승).
## 대안 = 레벨 씬 안에 Player를 두기 → 층 이동마다 상태 이사 코드가 필요해 기각.
## 지역·층 이동 규칙 = docs/design/areas_v2.md §3 (D-077: 층 번호 하나 → 지역 id + 층). 전투 HUD/사망 = design/combat_v2.md.

const STAIRS_LOCK_SEC := 0.7
const PORTAL_SCRIPT := preload("res://world/portal.gd")
const TALISMAN_TARGET := preload("res://ui/talisman_target.gd")   # 가방 부적 표적 선택 (#451)
const HOVER_TIP := preload("res://ui/hover_tip.gd")
const INACTIVE_GEAR := preload("res://ui/inactive_gear.gd")   # 꺼진 장비 알림 (#427, item_system_v2 §17.2)
const DEV_KEYS := preload("res://world/dev_keys.gd")   # dev 키 콘솔 (#417) — 키 표·동작·DevMode 게이트는 저 파일, 여기는 위임만
const SYSTEM_MENU := preload("res://ui/system_menu.gd")   # Esc 시스템 메뉴·설정 (#156, design/system_menu_156.md)
const STORY_CUTIN := preload("res://ui/story_cutin_ui.gd")   # 첫 여정 사설·보스 등장 (#96)
const QUEST_WATCH := preload("res://core/quest_watch.gd")   # 퀘스트 목표 ↔ 게임 사건 (#305 — 싹쓸이 셈·바크), 신호만 받는다

@onready var world_root: Node3D = $WorldRoot
@onready var player: CharacterBody3D = $Player
@onready var camera: Camera3D = $IsoCamera
@onready var hud_label: Label = $HUD/Label
@onready var title_ui: PanelUi = $HUD/Title

var _started: bool = false
var system_menu: PanelUi
var story_cutin: StoryCutinUi
var _skip_cinematics: bool = false

var current_level: Level
var _stairs_lock: float = 0.0
var _dev := DEV_KEYS.new(self)   # dev 키 콘솔 — 트리에 안 붙인다: 대화 띠가 셸 맨 끝 자식으로 남아 입력 선후가 그대로(AGENTS §8-16)
var _quests := QUEST_WATCH.new(self)   # 같은 까닭으로 트리 밖 — EventBus(층 들어섬·적 죽음)에만 붙는다


func _ready() -> void:
	print(BuildInfo.log_line())   # 부팅 로그 첫 줄 (D-092) — 버그 제보 로그가 커밋까지 따라간다. 파일 없으면(에디터·시험) dev
	# 커서 호버 표시 (보드 #81) — 씬 파일을 건드리지 않고 HUD에 얹는다(다른 세션의 UI 작업과 겹치지 않게).
	var tip := HOVER_TIP.new()
	tip.name = "HoverTip"
	$HUD.add_child(tip)
	$HUD.add_child(INACTIVE_GEAR.new())   # 꺼진 장비 알림 — 스탯 갱신을 듣고 꺼지는 순간 한 줄(ui_message). 새 판·불러오기보다 먼저 선다
	# Esc 시스템 메뉴 (#156) — 창이 하나도 없을 때의 Esc. 열린 동안 판을 멈춘다(pause_world). 대화 띠보다 앞 자식이라 대화 중 Esc는 띠 몫이다.
	var talisman_target := TALISMAN_TARGET.new()
	talisman_target.name = "TalismanTarget"
	$HUD.add_child(talisman_target)
	system_menu = SYSTEM_MENU.new()
	system_menu.name = "SystemMenu"
	system_menu.set("main", self)
	$HUD.add_child(system_menu)
	story_cutin = STORY_CUTIN.new()
	story_cutin.name = "StoryCutin"
	story_cutin.visible = false
	$HUD.add_child(story_cutin)
	story_cutin.finished.connect(_on_story_cutin_finished)
	add_child(DialogueBand.new())   # 대화 띠 (#238, D-082) — 셸 맨 끝 자식이라 대화 중 입력을 창들보다 먼저 받는다
	title_ui.create_requested.connect(_on_character_created)
	title_ui.profile_chosen.connect(_on_character_selected)
	title_ui.settings_requested.connect(system_menu.open_title_settings)
	system_menu.title_settings_closed.connect(title_ui.settings_closed)
	EventBus.stairs_used.connect(_on_stairs_used)
	EventBus.area_exit_used.connect(_on_area_exit_used)
	EventBus.player_died.connect(_on_player_died)
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.ui_message.connect(_on_ui_message)
	EventBus.town_portal_requested.connect(_on_town_portal_requested)
	EventBus.portal_used.connect(_on_portal_used)
	EventBus.waypoint_travel.connect(_on_waypoint_travel)
	EventBus.boss_died.connect(_on_boss_died)
	EventBus.boss_spotted.connect(_on_boss_spotted)
	EventBus.quest_changed.connect(func() -> void: SaveSystem.save_now("quest"))
	if DevMode.is_active:
		EventBus.player_move_target_set.connect(func(p: Vector3) -> void: print("[Click] world=%s cell=%s" % [p, Level.world_to_cell(p)]))
	# #111: 첫 실행도 H1 타이틀에서 시작한다. 명시적 --new와 E2E 대본은 종전처럼 바로 새 판.
	var args := OS.get_cmdline_user_args() + OS.get_cmdline_args()
	var bypass_title: bool = "--new" in args
	for arg in args:
		if arg.begins_with("--e2e=") or arg == "--e2e-selftest":
			bypass_title = true
			break
	_skip_cinematics = bypass_title
	if bypass_title:
		start_game(false)
	else:
		title_ui.set_open(true)
		player.menu_pause_started()
		pause_world(true)


## 판 멈춤의 단일 입구 (#156, design/system_menu_156.md) — 트리를 멈추면 물리·애니·적 AI·예약 타이머(process_always 끔)와
## 전투 시계(GameClock은 이 셸의 _physics_process가 흘린다, #234)가 같이 선다. 메뉴·타이틀·UI 소리만 PROCESS_MODE_ALWAYS.
func pause_world(paused: bool) -> void:
	get_tree().paused = paused


## 「저장 후 타이틀」(#156) — 저장은 부른 쪽(SystemMenu)이 이미 성공시켰다. 판은 멈춘 채 타이틀이 뜨고, 고르면 start_game.
func show_title() -> void:
	system_menu.set_open(false)
	story_cutin.set_open(false)
	_started = false
	title_ui.set_open(true)
	player.menu_pause_started()
	pause_world(true)


## #550: 새 파일이 완성된 뒤 기존 start_game의 세션 정리·복원 입구로 시작한다.
func _on_character_created(display_name: String) -> void:
	if not SaveSystem.create_profile(display_name, not _skip_cinematics):
		_stay_on_title(SaveSystem.last_error)
		return
	start_game(true)


func _on_character_selected(id: String) -> void:
	if not SaveSystem.select_profile(id):
		_stay_on_title(SaveSystem.last_error)
		return
	start_game(true)


## 게임 시작. continue_game = 저장 복원 후 **저장한 지역·층 입구에서**(v4, #156 — 옛 세이브는 못골).
## 불러오기에 실패하면(손상·깨진 파일) 타이틀에 남아 까닭을 보이고 파일은 그대로 둔다 — 새 판·자동 저장으로 덮지 않는다.
func start_game(continue_game: bool) -> void:
	# 이어하기는 판을 걷기 전에 파일부터 본다 — 못 읽으면 타이틀에 남는다(판·파일 그대로)
	if continue_game and SaveSystem.read_checked().is_empty():
		_stay_on_title(SaveSystem.last_error)
		return
	system_menu.set_open(false)
	story_cutin.set_open(false)
	title_ui.set_open(false)
	player.menu_pause_ended()
	pause_world(false)
	# 사망 연출 도중 새 게임/이어하기(e2e 리셋 포함)면 덮개·상태를 걷는다
	_dying = false
	_death_gen += 1
	if _fade_tw and _fade_tw.is_valid():
		_fade_tw.kill()
	if _fade:
		_fade.color.a = 0.0
	player.combat.reset_session()
	_dev.reset_session()   # dev 정예 차례(#290) — 새 판마다 처음부터(같은 판·같은 차례 = 같은 무리)
	var vitals: Dictionary = {}
	if continue_game:
		vitals = SaveSystem.load_into_state()
		if vitals.is_empty():   # 방금 본 파일이 그새 바뀌었다 — 적용 전에 멈췄으니 GameState는 그대로
			_stay_on_title(SaveSystem.last_error)
			return
		player.combat.bind_inventory()
		player.combat.recompute_stats()
		player.combat.hp = clampf(float(vitals.hp), 1.0, player.combat.max_hp)
		player.combat.mp = clampf(float(vitals.mp), 0.0, player.combat.max_mp)
		EventBus.game_loaded.emit()
	else:
		SaveSystem.begin_fresh_session()
		SaveSystem.delete_save()
		GameState.new_character()
		GameState.flags["opening_pending"] = not _skip_cinematics
		player.combat.bind_inventory()
		player.combat.recompute_stats()
		player.combat.revive_full()
		EventBus.game_loaded.emit()
	_started = true
	if continue_game:
		load_area(StringName(vitals.area_id), int(vitals.floor_no), Level.SpawnHint.DEFAULT)
	else:
		load_town(Level.SpawnHint.DEFAULT)
	if bool(GameState.flags.get("opening_pending", false)) and not _skip_cinematics:
		story_cutin.open_opening()
		player.menu_pause_started()
		pause_world(true)


func _on_boss_spotted(boss: Node) -> void:
	if _skip_cinematics or not _started or story_cutin.visible or title_ui.visible or _dying:
		return
	if not boss is Boss or not boss.is_in_group("boss") or boss.def == null:
		return
	if story_cutin.open_boss(boss.def.id):
		player.menu_pause_started()
		pause_world(true)


func _on_story_cutin_finished(kind: String) -> void:
	if not _started or title_ui.visible:
		return
	if kind == "opening":
		GameState.flags.erase("opening_pending")
		SaveSystem.save_now("opening")
	player.menu_pause_ended()
	pause_world(false)


## 이어하기 실패 — 타이틀을 띄운 채 까닭 한 줄, 판은 멈춘 채 (#156). 파일은 건드리지 않는다.
func _stay_on_title(why: String) -> void:
	title_ui.set_open(true)
	title_ui.show_msg(why)
	player.menu_pause_started()
	pause_world(true)


## 전투 시계 (#234, core/game_clock.gd) — 셸이 물리 틱마다 한 번 흘린다. 트리 순서상 Player·적(WorldRoot 아래)보다 먼저 돌아 같은 틱의 「언제까지」 비교가 새 시각을 본다.
## 멈춤(paused)이면 이 노드도 멈추니 시계도 선다 · time_scale·--fixed-fps는 delta가 이미 따른다.
func _physics_process(delta: float) -> void:
	GameClock.step(delta)


func _process(delta: float) -> void:
	if _stairs_lock > 0.0:
		_stairs_lock -= delta


func load_town(hint: Level.SpawnHint) -> void:
	load_area(AreaDb.TOWN, 0, hint)


## 지역 이동의 단일 입구 (D-077, design/areas_v2.md). 던전 층은 1..floors로 자르고, 마을·필드는 층 0.
## 왜 한 함수인가: 계단·귀환문·서낭단·사망·dev 키가 전부 "어느 지역 몇 층"으로 같은 길을 타야 세이브·강함·재고가 어긋나지 않는다.
func load_area(id: StringName, floor_no: int, hint: Level.SpawnHint, entry: StringName = &"") -> void:
	var def := AreaDb.get_def(id)
	if def == null:
		return
	floor_no = clampi(floor_no, 1, def.floors) if def.is_dungeon() else 0
	GameState.area_id = id
	GameState.floor_no = floor_no
	if def.is_town():
		GameState.town_visits += 1
		# 김 영감 재고는 마을 들어올 때마다 새로 (design/town_v2.md), ilvl = 가 본 가장 높은 지역 레벨 + 2회차 12 (item_system_v2 §3.1, #427)
		GameState.vendor_stock = Vendor.generate_stock(hash([GameState.run_seed, "vendor", GameState.town_visits]), Vendor.stock_ilvl(GameState.max_area_level, GameState.run), GameState.run)
	else:
		# 필드는 들어서면 무리 레벨 끝(들녘 3 · 정령재 7), 던전은 그 층 (AreaDef.reach_level, #427)
		GameState.max_area_level = maxi(GameState.max_area_level, def.reach_level(floor_no))
	var lvl := def.scene.instantiate() as Level
	if lvl.has_method("configure"):
		lvl.configure(def, floor_no)
	lvl.spawn_entry = entry
	_swap_level(lvl, hint)


## 귀환문이 지금 이 지역·층에 있나.
func _portal_is_here() -> bool:
	var pt: Variant = GameState.portal
	return pt != null and StringName(pt.area) == GameState.area_id and int(pt.floor) == GameState.floor_no


## 레벨이 서면 귀환문을 상태(GameState.portal)에 맞춰 세운다: 마을 = PortalSpot, 던전 = 문을 연 그 자리.
func _restore_portal() -> void:
	var pt: Variant = GameState.portal
	if pt == null or current_level == null:
		return
	if GameState.is_town():
		var spot := current_level.get_node_or_null("PortalSpot") as Marker3D
		current_level.spawn_portal(spot.global_position if spot else Vector3(2, 0, 6))
	elif _portal_is_here():
		pt.pos = current_level.walkable_point(pt.pos)   # 배치가 바뀐 옛 세이브(#165)면 벽 속 좌표를 바닥으로
		current_level.spawn_portal(pt.pos)


func _swap_level(lvl: Level, hint: Level.SpawnHint) -> void:
	EventBus.level_loading.emit(lvl.scene_file_path)
	if current_level:
		current_level.queue_free()
		current_level = null
	current_level = lvl
	world_root.add_child(lvl)  # _ready에서 생성까지 끝남
	player.teleport_to(lvl.get_spawn(hint))
	# 족자에 빨려 들어간 크기·위치를 되돌린다(#90). 어느 경로로 왔든 새 레벨에서는 제 크기로 선다.
	Portal.restore_actor(player)
	camera.snap_to_target()
	# 영속 플레이어의 보조광도 레벨별로 복원한다 — 마을 조정을 던전에 남기지 않음 (#94).
	var travel_light := player.get_node_or_null("LightRadius") as OmniLight3D
	if travel_light:
		travel_light.light_energy = lvl.player_light_energy
		travel_light.omni_range = lvl.player_light_range
	_stairs_lock = STAIRS_LOCK_SEC
	# #109: 지역명은 진입 배너, 조작법은 버튼 툴팁에. 개발 범례만 개발 모드에서 보인다.
	hud_label.visible = DevMode.is_active
	hud_label.text = DEV_KEYS.HUD_LEGEND if DevMode.is_active else ""
	_restore_portal()
	EventBus.level_loaded.emit(lvl)
	_dev.log_stairs_screen.call_deferred()
	if _started:
		SaveSystem.save_now("level %s" % lvl.display_name)


func _on_ui_message(text: String) -> void:
	DamagePopup.spawn(world_root, player.global_position, text, Color(1.0, 0.9, 0.6))


## 레벨업 뒤 도호 추임새까지 (초) — 머리 위 道를 다 쓸 무렵(쓰기 0.12 + 0.55초, vfx.md §8.9 「목소리 시작 = 글자를 다 쓸 무렵」).
const LEVELUP_VOICE_SEC := 0.6


func _on_enemy_died(_enemy: Node, xp: int) -> void:
	var xp_pct := float(player.combat.stats.get("xp_pct", 0.0))
	var gained := int(round(xp * (1.0 + xp_pct * 0.01)))
	var levels := Progression.add_xp(GameState.character, gained)
	if DevMode.is_active:
		print("[Kill] +%d xp (lv %d, %d/%d)" % [gained, GameState.character.level, GameState.character.xp, Progression.xp_to_next(int(GameState.character.level))])
	if levels > 0:
		var lv: int = GameState.character.level
		# 「레벨 업!」 글자 대신 이펙트 + 소리 (D-085, 보드 #280): 발밑 금니 먹 파문 · 옅은 금빛 · 머리 위 道 획 쓰기가 도호를 따라간다(숫자는 HUD Lv).
		# 소리 = 레벨업(가야금 + 종, Audio가 EventBus로) → 道를 다 쓸 무렵 도호 추임새 「어허!」(말 없는 소리, D-017 경계 안).
		Vfx.play("level_up", player.global_position, {"parent": player})
		EventBus.level_up.emit(lv)
		get_tree().create_timer(LEVELUP_VOICE_SEC, false).timeout.connect(Audio.play.bind("doho_levelup"))   # 멈춤을 따른다 (#156)
		player.combat.recompute_stats()
		if DevMode.is_active:
			print("[LevelUp] lv=%d stat_pts=%d skill_pts=%d" % [lv, GameState.character.stat_points, GameState.character.skill_points])
	EventBus.player_stats_changed.emit()


## 사망 연출 (design/combat_v2.md §8): 시체 1.2s(입력 무시·적 정지) → 검게 0.6s → 부활·마을 스폰 → 밝게 0.6s + 메시지. 대가 = 엽전 10%.
const DEATH_LINGER_SEC := 1.2
const DEATH_FADE_SEC := 0.6
const DEATH_GOLD_LOSS_PCT := 0.10
var _fade: ColorRect
var _fade_tw: Tween
var _dying: bool = false
## 사망 연출 세대 — start_game이 올린다. 연출은 기다릴 때마다 자기 세대가 아직 맞는지 보고, 새 판이 시작됐으면 거기서 멈춘다
## (안 멈추면 새 판 도중에 뒤늦게 "부활·마을 이동"이 끼어든다 — e2e 리셋·한 대본 안에서 판 다시 하기가 사망 직후에 걸린다, #97).
var _death_gen: int = 0


func _on_player_died() -> void:
	if _dying:
		return
	_dying = true
	var lost: int = GameState.inventory.take_gold(int(round(float(GameState.inventory.gold) * DEATH_GOLD_LOSS_PCT)))
	EventBus.ui_message.emit("쓰러졌다…")
	if DevMode.is_active:
		print("[Death] 도호 사망 → %.1fs 뒤 마을 복귀, 엽전 -%d" % [DEATH_LINGER_SEC, lost])
	# 물리 콜백 안일 수 있으니 다음 프레임부터
	_death_sequence.call_deferred(lost)


func _death_sequence(lost: int) -> void:
	var gen := _death_gen
	await get_tree().create_timer(DEATH_LINGER_SEC, false).timeout
	if gen != _death_gen:
		return
	await _fade_to(1.0, DEATH_FADE_SEC)
	if gen != _death_gen:
		return
	# 부활을 먼저 — 마을 진입 자동 저장이 생명 0을 남기지 않게
	player.combat.revive_full()
	load_town(Level.SpawnHint.DEFAULT)
	Audio.play("revive")
	Vfx.play("revive", player.global_position)
	await _fade_to(0.0, DEATH_FADE_SEC)
	if gen != _death_gen:
		return
	_dying = false
	EventBus.ui_message.emit("못골 마을에서 눈을 떴다" + (" — 엽전 %d 잃음" % lost if lost > 0 else ""))


## 컷씬 명령 Cut.fade (#240) — 사망 연출과 같은 덮개. sec 0 = 다음 프레임에 그 값.
func fade_to(a: float, sec: float) -> void:
	await _fade_to(a, sec)


## 덮개의 지금 알파 (없으면 0).
func fade_alpha() -> float:
	return _fade.color.a if _fade != null else 0.0


## 검은 덮개(지연 생성, 최상위 CanvasLayer, 마우스 통과). alpha를 sec 동안 a로. 진행 중인 트윈은 새 것이 덮는다.
func _fade_to(a: float, sec: float) -> void:
	if _fade == null:
		var layer := CanvasLayer.new()
		layer.name = "Fade"
		layer.layer = 100
		add_child(layer)
		_fade = ColorRect.new()
		_fade.name = "Rect"
		_fade.color = Color(0.0, 0.0, 0.0, 0.0)
		_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.add_child(_fade)
		_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)   # 앵커+오프셋 둘 다 — 앵커만 잡으면 0×0 상자
	if _fade_tw and _fade_tw.is_valid():
		_fade_tw.kill()
	_fade_tw = create_tween()
	_fade_tw.tween_property(_fade, "color:a", a, sec)
	await _fade_tw.finished


# ---------- 귀환부 / 서낭단 (design/town_v2.md) ----------

func _on_town_portal_requested() -> void:
	if GameState.is_town():
		EventBus.ui_message.emit("마을에서는 귀환부를 쓸 수 없다")
		return
	if _portal_is_here() and not GameState.portal.returned:
		EventBus.ui_message.emit("이미 문이 열려 있다")
		return
	if not GameState.inventory.consume_def("town_portal"):
		EventBus.ui_message.emit("귀환부가 없다")
		return
	var pos: Vector3 = player.global_position + player.facing() * 1.3
	var nw: Array = current_level.nearest_walkable(Level.world_to_cell(pos), 3)
	if nw[0]:
		pos = Level.cell_to_world(nw[1])
	# 기존 문(다른 층에 남은 것)은 새 문이 대체
	for old in current_level.find_children("*", "Area3D", true, false):
		if old.get_script() == PORTAL_SCRIPT:
			old.queue_free()
	GameState.portal = {"area": GameState.area_id, "floor": GameState.floor_no, "pos": pos, "returned": false}
	current_level.spawn_portal(pos)
	if DevMode.is_active:
		print("[Portal] opened %s %d층 pos=%s" % [GameState.area_id, GameState.floor_no, pos])


func _on_portal_used() -> void:
	var generation := _death_gen   # 판 세대 (#156) — 진입 연출을 기다리는 사이 「저장 후 타이틀 → 이어하기」로 새 판이 열리면 이 이동은 버린다
	Vfx.play("portal_use", player.global_position)
	# 족자 진입 연출(#84): 그림 면으로 빨려 들어간 뒤에 이동한다. 족자가 없으면(옛 저장·테스트) 곧장 이동.
	var portal := get_tree().get_first_node_in_group("portal")
	var wait := 0.0
	if portal and portal.has_method("play_enter"):
		wait = portal.play_enter(player)
	if wait > 0.0:
		await get_tree().create_timer(wait, false).timeout   # 멈춤을 따른다 (#156)
	if generation != _death_gen or not _started:
		return
	# 이동 전에 진입 트윈을 죽인다 — 크기 복구는 _swap_level이 한다(#90).
	if is_instance_valid(portal) and portal.has_method("end_enter"):
		portal.end_enter()
	_travel_portal.call_deferred(generation)


func _travel_portal(generation: int = -1) -> void:
	if generation >= 0 and (generation != _death_gen or not _started):
		return
	var pt: Variant = GameState.portal
	if pt == null:
		return
	if GameState.is_town():
		pt.returned = true
		load_area(StringName(pt.area), int(pt.floor), Level.SpawnHint.FROM_PORTAL)
	else:
		if pt.returned:
			GameState.portal = null   # 두 번째 귀환 → 문 닫힘 (디아2)
		load_town(Level.SpawnHint.FROM_PORTAL)
	if DevMode.is_active:
		print("[Portal] travel → %s %d층 portal=%s" % [GameState.area_id, GameState.floor_no, GameState.portal])


func _on_waypoint_travel(key: String) -> void:
	Vfx.play("waypoint_use", player.global_position)
	_travel_waypoint.call_deferred(key)


## 서낭단 키 "<지역>:<층>" → 그 지역·층의 서낭단 옆.
func _travel_waypoint(key: String) -> void:
	var at: Array = AreaDb.parse_waypoint_key(key)
	if not AreaDb.has(at[0]):
		push_error("Main: 서낭단 키가 이상하다 %s" % key)
		return
	load_area(at[0], at[1], Level.SpawnHint.FROM_WAYPOINT)
	if DevMode.is_active:
		print("[Waypoint] travel → %s" % key)


func _on_boss_died(_boss: Node) -> void:
	SaveSystem.save_now("boss")


func _on_stairs_used(direction: int, target_area: StringName) -> void:
	if _stairs_lock > 0.0:
		return
	_stairs_lock = STAIRS_LOCK_SEC  # 같은 프레임 중복 발동 차단
	# 물리 콜백(Area3D 겹침) 안에서 씬을 갈아치우면 안 되므로 다음 프레임으로 넘긴다.
	_change_level_by_stairs.call_deferred(direction, target_area)


## 걸어서 넘어가기 (마을 들머리 ↔ 들녘, field_v2.md §6) — 계단과 같은 잠금·다음 프레임 규칙.
func _on_area_exit_used(target_area: StringName, entry: StringName) -> void:
	if _stairs_lock > 0.0:
		return
	_stairs_lock = STAIRS_LOCK_SEC
	load_area.call_deferred(target_area, 0, Level.SpawnHint.FROM_ENTRY, entry)


## 계단 규칙 (areas_v2.md §3): 던전 안 = 위·아래 층(마지막 층 아래는 없음), 1층에서 오르면 그 던전의 exit_up(입구 마커로),
## 마을·필드의 입구 = target_area 던전 1층(비면 AreaDb.DEFAULT_DUNGEON).
func _change_level_by_stairs(direction: int, target_area: StringName = &"") -> void:
	var def := GameState.area_def()
	if direction > 0:
		if not def.is_dungeon():
			load_area(target_area if target_area != &"" else AreaDb.DEFAULT_DUNGEON, 1, Level.SpawnHint.FROM_ABOVE)
		elif GameState.floor_no < def.floors:
			load_area(def.id, GameState.floor_no + 1, Level.SpawnHint.FROM_ABOVE)
	elif def.is_dungeon():
		if GameState.floor_no > 1:
			load_area(def.id, GameState.floor_no - 1, Level.SpawnHint.FROM_BELOW)
		else:
			# 떠나온 던전 id를 입구 이름으로 — 던전 입구가 여럿인 필드(정령재 = 범굴·쇠부리 폐광)가 그 입구 앞에 세운다 (#167)
			load_area(def.exit_up if def.exit_up != &"" else AreaDb.TOWN, 0, Level.SpawnHint.FROM_BELOW, def.id)


func _unhandled_key_input(event: InputEvent) -> void:
	if event.is_action_pressed("town_portal") and not event.is_echo():
		_on_town_portal_requested()
		return
	_dev.handle(event)   # dev 키 콘솔 (#417) — DevMode 게이트·키 표는 world/dev_keys.gd. 같은 단계에서 위임하므로 대화 띠(KEY_L)와의 선후가 그대로
