class_name E2e
extends RefCounted
## E2e — 시나리오가 쓰는 도구 상자: 진짜 입력 이벤트 주입, 기다리기, 좌표 변환, 검사 기록, 스크린샷. 사양 design/testing.md.
## 왜 진짜 이벤트인가: 플레이어·창은 Input 상태와 InputEvent로만 세상을 본다. 함수를 직접 부르면 "클릭 경로"가 검증되지 않는다.

## 던전·스폰 배치 시드. 싸움 자체(명중·치명·적 AI)는 매번 굴린다 — 같은 시드여도 결과는 판마다 다르다.
const SEED := 20260916

## 주입 표식 (#369) — 대본이 넣는 마우스 이벤트의 `device`. 창 모드에서 러너(`E2eRunner.InputGate`)가 이 표식이 **없는**
## 포인터 이벤트(진짜 OS 커서)를 게임보다 먼저 막는다. 4.7 엔진 번호와 안 겹치는 값: 흉내 −1 · 엔진 내부 −2 · 패드 0~15 ·
## 키보드 16 · 마우스 32(OS 마우스도, `InputEventMouseMotion.new()` 기본값도 32 — 옛 주입은 진짜와 구별이 안 됐다).
const INJECT_DEVICE := 0xE2E

var tree: SceneTree
var main: Node
var scenario_name: String = ""
var checks: int = 0
var fails: Array[String] = []
var shots: bool = false
var _shot_i: int = 0


func _init(p_tree: SceneTree, p_main: Node, p_name: String, p_shots: bool) -> void:
	tree = p_tree
	main = p_main
	scenario_name = p_name
	shots = p_shots


# ---------- 검사 ----------

func check(cond: bool, msg: String) -> bool:
	checks += 1
	if not cond:
		fails.append(msg)
		print("  ✗ %s" % msg)
	return cond


func check_eq(a: Variant, b: Variant, msg: String) -> bool:
	return check(a == b, "%s (기대 %s, 실제 %s)" % [msg, b, a])


func note(msg: String) -> void:
	print("  · %s" % msg)


# ---------- 기다리기 ----------

func frames(n: int) -> void:
	for i in n:
		await tree.process_frame


func seconds(s: float) -> void:
	await tree.create_timer(s).timeout


## 게임 시간(초) = 전투 시계 GameClock.now(물리 델타의 합, #234 — 경직·넉백·busy와 같은 시계). 시간 판정은 이것의 차이로: 프레임 수로 세면 헤드리스(~128fps)에서
## "프레임 6 = 0.1초"가 실제로는 0.047초라 2배 넘게 부풀고, 기계 부하에 따라 fps가 바뀌면 같이 흔들린다(#97 실측).
## 옛 셈(Engine.get_physics_frames() ÷ 틱수)과 time_scale 1에선 같은 값 — 틱 수는 슬로모·멈춤을 모르니 시계 하나로 모았다.
func game_time() -> float:
	return GameClock.now


## pred가 참이 될 때까지 (최대 timeout초). 참이면 true.
func wait_until(pred: Callable, timeout: float = 5.0) -> bool:
	var t := 0.0
	while t < timeout:
		if pred.call():
			return true
		await tree.process_frame
		t += tree.root.get_process_delta_time()
	return pred.call()


## 적어도 min_s초(진짜 idle _process 델타의 합)를 기다리고 그 합을 돌려준다 — 타자기 찍기처럼 `_process(delta)`로 도는 것의
## 속도를 잴 때 쓴다(카드 #436). game_time()(GameClock — 물리 델타)은 `_physics_process` 쪽 시계라 쓰면 안 된다: CPU를 나눠 쓰면
## idle 프레임과 물리 틱이 서로 다르게 밀려 rate = Δ찍힌글자 ÷ Δgame_time이 흔들린다(#436 dialogue_band 실측, 초당 18자로 떨어짐).
## 잰 구간과 똑같은 델타(get_process_delta_time, wait_until과 같은 값)로 나누면 어긋날 클럭이 없다.
func idle_seconds(min_s: float) -> float:
	var sum := 0.0
	while sum < min_s:
		await tree.process_frame
		sum += tree.root.get_process_delta_time()
	return sum


# ---------- 노드 ----------

func player() -> Node:
	return tree.get_first_node_in_group("player")


func level() -> Node:
	return tree.get_first_node_in_group("level")


func camera() -> Camera3D:
	return main.camera


func hud_panel(name: String) -> Node:
	return main.get_node("HUD/" + name)


func screen_of(world: Vector3) -> Vector2:
	return camera().unproject_position(world)


# ---------- 입력 주입 ----------

## 헤드리스 창은 64×64인데 stretch(canvas_items, 비율 유지)가 1280×720 캔버스를 축소·중앙 배치한다.
## 주입 좌표는 "창 좌표"라야 하므로 뷰포트의 최종 변환(캔버스→창)을 그대로 적용한다 (실측: 축만 나눠 넣으면 Y가 틀어짐).
func _to_window(pos: Vector2) -> Vector2:
	return tree.root.get_final_transform() * pos


## 주입할 마우스 이벤트 하나를 채운다 — 좌표(캔버스 → 창)와 표식(#369). **마우스 이벤트를 만드는 곳은 전부 이것을 지난다**
## (움직임·클릭·누름/뗌 — 휠·끌기 도우미를 새로 만들 때도). 대본은 보통 mouse_move·click을 쓰고, 같은 프레임에 여럿을 넣어야 할 때만 직접 부른다.
## window_id = INVALID(−1)인 이유: 엔진 입력 누적(`Input.use_accumulated_input`, 기본 켬)이 같은 프레임에 쌓인 마우스 움직임을
## **device를 안 보고** 합친다(#369 탐침 — 주입 뒤에 진짜가 오면 표식을 단 채 진짜 위치로 새고, 진짜 뒤에 주입이 오면 표식 없이 먹힌다).
## 누적은 window_id가 다르면 안 합친다(진짜 = 0). −1 = 「창 지정 없음」이라 DisplayServer가 모든 창(이 게임은 하나)으로 보낸다 — 헤드리스는 창 번호를 안 본다.
func mouse_event(ev: InputEventMouse, pos: Vector2) -> InputEventMouse:
	var wpos := _to_window(pos)
	ev.position = wpos
	ev.global_position = wpos
	ev.device = INJECT_DEVICE
	ev.window_id = DisplayServer.INVALID_WINDOW_ID
	return ev


func mouse_move(pos: Vector2) -> void:
	Input.parse_input_event(mouse_event(InputEventMouseMotion.new(), pos))
	await frames(2)


func click(pos: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT, shift: bool = false, ctrl: bool = false) -> void:
	await mouse_move(pos)
	if shift:
		_key_state(KEY_SHIFT, true)
	if ctrl:
		_key_state(KEY_CTRL, true)
	await frames(1)
	var down := mouse_event(InputEventMouseButton.new(), pos) as InputEventMouseButton
	down.button_index = button
	down.pressed = true
	down.shift_pressed = shift
	down.ctrl_pressed = ctrl
	Input.parse_input_event(down)
	await frames(3)
	var up := mouse_event(InputEventMouseButton.new(), pos) as InputEventMouseButton
	up.button_index = button
	up.pressed = false
	up.shift_pressed = shift
	up.ctrl_pressed = ctrl
	Input.parse_input_event(up)
	await frames(2)
	if shift:
		_key_state(KEY_SHIFT, false)
	if ctrl:
		_key_state(KEY_CTRL, false)
	await frames(1)


func click_world(world: Vector3, button: MouseButton = MOUSE_BUTTON_LEFT, shift: bool = false) -> void:
	# 창 전환 카메라가 멈춘 뒤 투영한다. 이동 중 계산한 좌표는 몇 프레임 뒤 NPC를 벗어난다.
	await wait_until(func(): return camera().call("ui_framing_settled"), 1.0)
	await click(screen_of(world), button, shift)


## 버튼 누름/뗌만 (홀드 이동 재현). click()과 같은 창 좌표 변환.
func mouse_button(pos: Vector2, pressed: bool, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	await mouse_move(pos)
	var ev := mouse_event(InputEventMouseButton.new(), pos) as InputEventMouseButton
	ev.button_index = button
	ev.pressed = pressed
	Input.parse_input_event(ev)
	await frames(2)


## 키는 표식을 안 단다(#369, design/testing.md) — 창을 가로지르는 진짜 키 이벤트는 없고(PD가 게임 창에 치지 않는 한),
## 내장 `ui_cancel` 등은 키보드 장치(16)에만 걸려 있어 device를 바꾸면 Esc가 액션에 안 걸린다.
func _key_state(keycode: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = keycode
	ev.physical_keycode = keycode
	ev.pressed = pressed
	Input.parse_input_event(ev)


func key(keycode: Key) -> void:
	_key_state(keycode, true)
	await frames(2)
	_key_state(keycode, false)
	await frames(3)


## 키를 sec 초 누르고 있다가 뗀다 (이벤트 건너뛰기 = Esc 0.8초, #240).
func hold_key(keycode: Key, sec: float) -> void:
	_key_state(keycode, true)
	await seconds(sec)
	_key_state(keycode, false)
	await frames(3)


## 키를 누른 채 둔다 / 뗀다 (Ctrl 빨리 넘기기처럼 누르는 동안을 재는 대본).
func key_down(keycode: Key) -> void:
	_key_state(keycode, true)
	await frames(1)


func key_up(keycode: Key) -> void:
	_key_state(keycode, false)
	await frames(1)


# ---------- 게임 흐름 헬퍼 (dev 키 = 셋업 도구) ----------

func go_down(floors: int = 1) -> void:
	for i in floors:
		await key(KEY_BRACKETRIGHT)
		await frames(3)


func remove_enemies() -> void:
	await key(KEY_N)


# ---------- 적 소환 (#416) — 대본 24편이 손으로 되풀이하던 여섯 줄을 한 곳에 ----------

## 적 몸 씬. 잡몹·부적술사·박쥐 = enemy.tscn · 흑랑 = boss.tscn(Boss — 돌격·2페이즈·보스 바). 대본이 opts.scene 으로 고른다 —
## 안 고르면 enemy.tscn(보스 정의를 잡몹 몸에 세워 넉백만 재는 대본도 있다, hit_stagger).
const ENEMY_SCENE := "res://actors/enemy.tscn"
const BOSS_SCENE := "res://actors/boss.tscn"
## 장산범 몸 (#494 — 은신·덮치기·허상, EnemyDef.boss_scene과 같은 값).
const JSB_SCENE := "res://actors/boss_jangsanbeom.tscn"

## 적 정의 id → 데이터 파일. 대본은 경로 대신 id 를 쓴다(enemy_def · spawn_enemy).
const ENEMY_DEFS := {
	"bandit": "res://data/enemies/bandit.tres",
	"bat": "res://data/enemies/bat.tres",
	"beacon_keeper": "res://data/enemies/beacon_keeper.tres",
	"cart_puller": "res://data/enemies/cart_puller.tres",
	"centipede": "res://data/enemies/centipede.tres",
	"guard_master": "res://data/enemies/guard_master.tres",
	"honbul": "res://data/enemies/honbul.tres",
	"imugi": "res://data/enemies/imugi.tres",
	"locust": "res://data/enemies/locust.tres",
	"plague_dog": "res://data/enemies/plague_dog.tres",
	"talisman_master": "res://data/enemies/talisman_master.tres",
	"boss_heukrang": "res://data/enemies/boss_heukrang.tres",
	"boss_jangsanbeom": "res://data/enemies/boss_jangsanbeom.tres",
	# 여성형 F1 (#355)
	"hollin_yeogung_bow": "res://data/enemies/hollin_yeogung_bow.tres",
	"hollin_yeogung_spear": "res://data/enemies/hollin_yeogung_spear.tres",
	"nachalnyeo": "res://data/enemies/nachalnyeo.tres",
	"tteodoneun_neok": "res://data/enemies/tteodoneun_neok.tres",
	"gaekgwi": "res://data/enemies/gaekgwi.tres",
	"mulgwishin": "res://data/enemies/mulgwishin.tres",
}
static var _defs: Dictionary = {}


## 적 정의 하나 — id("bandit") 또는 res:// 경로. 한 번 읽어 두고 같은 자원을 돌려준다(공유 — 수치를 바꿔 쓸 땐 duplicate()).
static func enemy_def(id: String) -> EnemyDef:
	var path: String = ENEMY_DEFS.get(id, id)
	if not _defs.has(path):
		_defs[path] = load(path) as EnemyDef
	return _defs[path]


## 적 하나를 세운다 — 대본들이 손으로 하던 순서 그대로: 씬 → def·area_level → (트리 밖 설정) → 층의 Enemies 에 붙임(없으면 층에, 마을) →
## 자리 → (붙은 뒤 설정) → frames 만큼 기다림. def_or_id = EnemyDef(사본도) · id · 경로. area_level < 0 = 지금 층의 지역 레벨(마을이면 1).
## opts(전부 선택): scene(몸 씬, BOSS_SCENE) · pack(무리 id) · rank + mods(set_rank — 트리에 넣기 전, _ready 가 한 번에 입힌다) ·
## hp(max_hp·hp 둘 다 — _ready 가 def × 레벨로 채운 값을 덮는다) · state(출발 상태) · frozen(물리·처리 끔 = 허수아비) ·
## no_physics(물리만 끔 — 화상·빙결 시간은 흐른다) · disabled(process_mode DISABLED) · frames(끝에 기다릴 프레임, 기본 2).
func spawn_enemy(def_or_id: Variant, pos: Vector3, area_level: int = -1, opts: Dictionary = {}) -> Enemy:
	var def: EnemyDef
	if def_or_id is EnemyDef:
		def = def_or_id
	else:
		def = enemy_def(String(def_or_id))
	var e: Enemy = (load(opts.get("scene", ENEMY_SCENE)) as PackedScene).instantiate()
	e.def = def
	e.area_level = area_level if area_level >= 0 else maxi(GameState.area_level(), 1)
	if opts.has("pack"):
		e.pack_id = int(opts.pack)
	if opts.has("rank"):
		e.set_rank(int(opts.rank), opts.get("mods", []))
	var parent: Node = level().get_node_or_null("Enemies")
	if parent == null:
		parent = level()
	parent.add_child(e)
	e.global_position = pos
	if opts.has("hp"):
		e.max_hp = float(opts.hp)
		e.hp = float(opts.hp)
	if opts.has("state"):
		e.state = opts.state
	if opts.get("frozen", false):
		e.set_physics_process(false)
		e.set_process(false)
	if opts.get("no_physics", false):
		e.set_physics_process(false)
	if opts.get("disabled", false):
		e.process_mode = Node.PROCESS_MODE_DISABLED
	await frames(int(opts.get("frames", 2)))
	return e


## 러너가 시나리오마다 세우는 출발점(새 캐릭터·고정 시드·마을·창 닫힘)으로 되돌린다 — 한 대본 안에서 판을 다시 할 때(#97).
func restart() -> void:
	reset_game(tree, main)
	await frames(1)


## 시나리오마다 같은 출발점: 새 캐릭터(조작 상태 포함, PlayerCombat.reset_session), 고정 시드, 마을, 창 전부 닫힘.
## 러너와 restart()가 이 한 곳을 같이 쓴다.
static func reset_game(p_tree: SceneTree, p_main: Node) -> void:
	for n in p_tree.get_nodes_in_group("panel_ui"):
		if n.visible and n.closable_by_esc:
			n.set_open(false)
	# 이벤트 트리거(#240)는 재운다 — 대본들이 마을을 지나다니며 무당 할매 앞을 밟는다. 이벤트를 재는 대본(dialogue_event)만 깨운다.
	EventTrigger.armed = false
	# 죽음 고르기의 기억(#472 — 같은 모습을 연달아 피함)도 비운다: 앞 대본이 무엇을 죽였는지가 이 대본의 죽음 모습을 흔들지 않게
	EnemyDeath.reset_memory()
	GameState.run_seed = SEED
	GameState.rng.seed = SEED
	SaveSystem.use_save_context("user://save_e2e.json")
	p_main.start_game(false)
	GameState.run_seed = SEED
	GameState.rng.seed = SEED


## 창이 모두 닫힌 상태로 (대화 띠도).
func close_all() -> void:
	var b := band()
	if b != null and b.is_open():
		b.close()
	for n in tree.get_nodes_in_group("panel_ui"):
		if n.visible and n.closable_by_esc:
			n.set_open(false)
	await frames(2)
	await wait_until(func(): return camera().call("ui_framing_settled"), 1.0)


# ---------- 대화 띠 (D-082, design/dialogue_v2.md §3.6 · #239) ----------

## 셸에 붙은 대화 띠 (없으면 null).
func band() -> DialogueBand:
	return DialogueBand.find(tree)


## 띠 무대에 남은(지워지는 중이 아닌) 초상 수 — 좌판이 열린 순간 0 이어야 한다(§3.6 hide_now).
func band_portraits() -> int:
	var b := band()
	var n := 0
	if b != null and b.stage() != null:
		for c in b.stage().get_children():
			if c is DialoguePortrait and not c.is_queued_for_deletion():
				n += 1
	return n


## NPC 에게 말을 건다 — 진짜 클릭으로 다가가 띠가 열릴 때까지. 열렸으면 true.
func talk_to(npc: Node3D, timeout: float = 8.0) -> bool:
	await click_world(npc.global_position + Vector3(0, 0.9, 0))
	return await wait_until(func() -> bool: return band() != null and band().is_open(), timeout)


## 선택지가 보일 때까지 Space 로 넘긴다 — 글자가 찍히는 중이면 이 줄 끝까지, 다 찍혔으면 다음 줄(띠의 진짜 키 입력 길).
## 선택지가 보이면 true, 대화가 끝나거나 max_steps 번 안에 안 오면 false.
func talk_until_choices(max_steps: int = 60) -> bool:
	var b := band()
	for i in max_steps:
		if b == null or not b.is_open():
			return false
		if b.choices_shown():
			return true
		var l: Variant = b.current_line()
		if l != null and (b.is_typing() or b.next_visible() or not l.choices.is_empty()):
			await key(KEY_SPACE)
		else:
			await frames(2)   # 애드온이 다음 줄을 꺼내는 중($> 명령 기다림)
	return b != null and b.choices_shown()


## 일 선택지를 진짜 클릭으로 고른다 — 대본 태그 [#act=…] 의 일 이름(§3.6). 선택지까지 넘기고 그 칸 가운데를 클릭. 없으면 false.
func talk_pick(action: String) -> bool:
	if not await talk_until_choices():
		return false
	var b := band()
	var i := b.choice_index(action)
	if i < 0:
		note("일 선택지 %s 없음 (있는 것 %s)" % [action, str(b.choice_actions())])
		return false
	await click(b.choice_rect(i).get_center())
	return true


## 대화를 닫는다 (Esc — 진짜 키). 닫혀 있으면 그대로.
func talk_close() -> void:
	var b := band()
	if b != null and b.is_open():
		await key(KEY_ESCAPE)
	await wait_until(func() -> bool: return b == null or not b.is_open(), 2.0)


# ---------- 스크린샷 (창 모드에서만) ----------

func shot(label: String) -> void:
	if not shots or DisplayServer.get_name() == "headless":
		return
	await wait_until(func(): return camera().call("ui_framing_settled"), 1.0)
	await RenderingServer.frame_post_draw
	var img := tree.root.get_viewport().get_texture().get_image()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("user://e2e"))
	_shot_i += 1
	var path := "user://e2e/%s_%02d_%s.png" % [scenario_name, _shot_i, label]
	img.save_png(path)
	note("스크린샷 %s" % ProjectSettings.globalize_path(path))
