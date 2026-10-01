extends E2eScenario
## 흑랑 밸런스 (combat_v2 §7·§7.1 보드 #1·#97 · monsters_v2 §9.7 보드 #292) — 도호 두 벌로 흑랑을 잡는다. 흑랑 숫자는 그대로.
## ① **Lv3**(+5체+5힘) · 참격 2 · 탕약 3 = 「최소 레벨로도 잡힌다」 — 들녘이 붙기 전 기준이던 판. §7 목표 ②(3번 안에)를 그대로 잰다.
## ② **Lv5**(+10체+10힘) · 참격 3 · 탕약 3 = 지금 길로 오는 도착 레벨(들녘 뒤 길만 5.3 — §9.7). 목표(15~30초 · 탕약 1 안팎 ·
##    최저 생명 35~60%)는 한 판으로 판정하지 않는다 — 굴림마다 갈리니 25판의 평균·범위로 재서 §9.7 표에 적고(#292),
##    대본은 한 판의 굴림에 안 흔들리는 선(관측 범위 밖)만 건다(#97). 한 판 값은 note 한 줄로 남긴다.
## 조작 모델 = 시뮬과 같게: 보스 타깃 유지(자동공격) + 참격 쿨마다 보스 방향(2페이즈 박쥐는 부채꼴에 걸림) + 생명 35% 아래서 탕약.
## 한 판의 승패는 명중·치명·돌격 굴림에 갈린다 → 진 판은 새 판(러너와 같은 리셋)부터 다시, 벌마다 최대 3판.
## #536: 굴림의 역할별 시드식은 실행 전에 고정한다. 도호·흑랑·기존 파수·P2 박쥐 seed/초기·종료 state를 기록해 같은 판을 재생한다.

const COMBAT_RNG := preload("res://tests/fixtures/balance_combat_rng.gd")
var _replay: Node

const ATTEMPTS := 3
const POTIONS := 3
const PREP_DESCEND_TICKS := 6
const PREP_BOSS_TICKS := 5
const MAX_SEC := 45.0      # 한 판 게임 초 — #97 실측 16~24초의 두 배
const MIN_SEC := 8.0       # 보스전이 순간이 아님

## 도호 두 벌 — 마을에서 만든다. 레벨마다 능력 5 · 스킬 1, 참격은 시작 1점(Progression).
## Lv3: XP 180 = 20+57 → Lv3, 이월 103(<104). 능력 10 = 체력 5·힘 5, 스킬 포인트 2 중 1 = 참격 2.
## Lv5: XP 341 = 20+57+104+160 → Lv5, 이월 0(싸움 중 박쥐 경험치로 레벨이 안 오른다). 능력 20 = 체력 10·힘 10, 스킬 포인트 4 중 2 = 참격 3.
const LV3 := {"name": "Lv3", "xp": 180, "vit": 5, "str": 5, "slash": 2, "level": 3, "max_hp": 130.0}
const LV5 := {"name": "Lv5", "xp": 341, "vit": 10, "str": 10, "slash": 3, "level": 5, "max_hp": 150.0}


## 벌마다 3판 × 판당 게임 45초 + 오가는 시간.
func timeout_sec() -> float:
	return 60.0 * ATTEMPTS * 2.0


## 명중률까지 실전 그대로 잰다 — 러너의 명중 확정(#342)을 끈다. 판을 다시 해도(`t.restart()`) 대본 동안 꺼진 채다.
func sure_hit() -> bool:
	return false


## 탕약은 딱 POTIONS개 — 시작 탕약 2개 위에 얹으면(띠가 쌓는다) 5개가 된다(#97 전까지 그랬다).
func _prepare(c: Node, b: Dictionary) -> void:
	var ch: Dictionary = GameState.character
	Progression.add_xp(ch, int(b.xp))
	for i in int(b.vit):
		Progression.spend_stat(ch, "vit")
	for i in int(b.str):
		Progression.spend_stat(ch, "str")
	var slash := load("res://data/skills/slash.tres") as SkillDef
	while Progression.skill_level(ch, "slash") < int(b.slash) and Progression.learn_skill(ch, slash):
		pass
	c.recompute_stats()
	c.hp = c.max_hp
	c.mp = c.max_mp
	GameState.inventory.belt_take(0)
	GameState.inventory.belt_put(0, ItemInstance.create(ItemDb.get_def("hp_potion"), POTIONS))


## 한 판: 보스 층(흑랑 굴 2층)으로 내려가 흑랑 옆에서 싸운다. 준비 검사는 벌마다 첫 판에서만 센다.
func _attempt(b: Dictionary, first: bool, attempt: int) -> Dictionary:
	var p: Node = t.player()
	var c: Node = p.combat
	_prepare(c, b)
	var ch: Dictionary = GameState.character
	if first:
		t.check_eq(int(ch.level), int(b.level), b.name)
		t.check_eq(Progression.skill_level(ch, "slash"), int(b.slash), "%s 참격 %d" % [b.name, b.slash])
		t.check(c.max_hp >= float(b.max_hp), "%s 생명 %d+ (%d)" % [b.name, int(b.max_hp), int(c.max_hp)])
		t.check_eq(GameState.inventory.count_of("hp_potion"), POTIONS, "%s 탕약 %d" % [b.name, POTIONS])
	var boss_floor: int = AreaDb.get_def(AreaDb.DEFAULT_DUNGEON).boss_floor
	# #536: 입장 전에 도호를 고정하고 기존 파수·흑랑의 첫 ready부터 관찰한다.
	_replay = COMBAT_RNG.new()
	t.main.add_child(_replay)
	_replay.begin(c, E2e.SEED, int(b.level), attempt, AreaDb.DEFAULT_DUNGEON, boss_floor, Callable(t, "note"))
	for floor_step in boss_floor:
		await _prepare_key(KEY_BRACKETRIGHT, PREP_DESCEND_TICKS)
	var bosses := t.tree.get_nodes_in_group("boss")
	if first:
		t.check_eq(GameState.floor_no, boss_floor, "%s 보스 층" % b.name)
		t.check(bosses.size() == 1, "%s 흑랑 1" % b.name)
	if GameState.floor_no != boss_floor or bosses.size() != 1:
		_dispose_replay()
		return {}
	var boss: Node3D = bosses[0]
	if first:
		t.check(absf(boss.max_hp - 150.0 * 1.3) < 0.5, "흑랑 생명 195 (%d)" % int(boss.max_hp))
	t.check(_replay.actor_count() == 4 and _replay.guard_count() == 2 and not DamageCalc.sure_hit,
		"%s 판%d 도호·흑랑·파수 둘 RNG 고정 · 실제 명중 굴림" % [b.name, attempt])
	_replay.observe_guard("before_V")
	await _prepare_key(KEY_V, PREP_BOSS_TICKS)   # 같은 dev 키: 보스 옆
	_replay.observe_guard("after_V")
	var pots0: int = GameState.inventory.count_of("hp_potion")
	var hp0: float = c.hp
	var t0: float = t.game_time()
	var atk0: int = c.attacks_received
	var hit0: int = c.hits_received
	var elapsed := 0.0
	var hp_min: float = c.hp
	var phase2_at := -1.0
	var input_waits := 0
	var input_ticks_ok := true
	while elapsed < MAX_SEC and c.hp > 0.0 and boss.state != Enemy.State.DEAD:
		if c.target != boss:
			c.set_target(boss)
		c.cast_active(boss.global_position)          # 쿨다운·도력은 cast_active가 거른다
		if c.hp < c.max_hp * 0.35:
			c.use_belt(0)
		var tick0 := Engine.get_physics_frames()
		await _combat_ticks()
		input_waits += 1
		input_ticks_ok = input_ticks_ok and Engine.get_physics_frames() - tick0 == 6
		elapsed = t.game_time() - t0
		hp_min = minf(hp_min, c.hp)
		if phase2_at < 0.0 and boss.hp <= boss.max_hp * 0.5:
			phase2_at = elapsed
	t.note("흑랑 입력 %s 판%d polls=%d physics_interval=6 valid=%s" % [b.name, attempt, input_waits, input_ticks_ok])
	t.check(input_ticks_ok and input_waits > 0, "%s 판%d 전투 입력은6물리틱 간격 (%d회)" % [b.name, attempt, input_waits])
	var win: bool = boss.state == Enemy.State.DEAD and c.hp > 0.0
	var r := {"win": win, "sec": elapsed, "phase2": phase2_at, "hp0": hp0, "hp": c.hp, "hp_min": hp_min, "max_hp": c.max_hp,
		"used": pots0 - GameState.inventory.count_of("hp_potion"), "boss_hp": boss.hp}
	# 한 줄 = 25판 표의 한 칸(§9.7) — 모양을 바꾸면 모으는 쪽도 같이.
	t.note("흑랑 %s %s · %.1f초 · 2페이즈 %.1f초 · 생명 %.0f→%.0f (최저 %.0f = %.0f%%) · 탕약 %d/%d · 적 공격 %d (명중 %d)" % [
		b.name, "처치" if win else ("도호 쓰러짐" if c.hp <= 0.0 else "시간 초과") + "(흑랑 %d)" % int(boss.hp),
		elapsed, phase2_at, hp0, c.hp, hp_min, 100.0 * hp_min / c.max_hp, r.used, POTIONS,
		c.attacks_received - atk0, c.hits_received - hit0])
	c.clear_target()
	p.stop_moving()
	r.attacks = c.attacks_received - atk0
	r.hits = c.hits_received - hit0
	r.guards = _replay.guard_count()
	r.summoned = _replay.spawn_count()
	r.rng = _replay.finish()
	t.note("흑랑 재생 %s 판%d win=%s attacks=%d hits=%d guards=%d summoned=%d" % [b.name, attempt, win, r.attacks, r.hits, r.guards, r.summoned])
	_dispose_replay()
	return r


## 한 벌을 최대 ATTEMPTS판 — 이긴 판(win = true)이나 진 기록(win = false)을 돌려준다. stop = 준비가 깨져 더 볼 게 없음(검사는 이미 빨갛다).
func _fight(b: Dictionary) -> Dictionary:
	var tries: Array[String] = []
	for i in ATTEMPTS:
		if i > 0:
			await t.restart()
		var r: Dictionary = await _attempt(b, i == 0, i + 1)
		if r.is_empty():
			return {"stop": true}
		tries.append("처치" if r.win else "패")
		if r.win:
			r.tries = tries
			return r
	return {"win": false, "tries": tries}


func run() -> void:
	# ① Lv3 — 최소 레벨로도 잡힌다 (§7 ② · #97 판정선 그대로)
	var w3 := await _fight(LV3)
	if w3.has("stop"):
		return
	t.check(w3.win, "Lv3 흑랑 처치 — 최소 레벨로도 %d번 안에 (%s)" % [ATTEMPTS, " → ".join(w3.tries)])
	if w3.win:
		t.check(w3.sec >= MIN_SEC, "Lv3 보스전이 순간이 아님 (%.1f초)" % w3.sec)
		# 대가 (§7 ③ "보스에 생명 절반 · 탕약 1개"): 탕약을 썼거나 생명이 30% 넘게 깎였다
		t.check(w3.used >= 1 or w3.hp_min <= w3.hp0 * 0.7, "Lv3 대가가 있다 — 탕약 %d · 최저 생명 %.0f / %.0f" % [w3.used, w3.hp_min, w3.hp0])
	# ② Lv5 — 지금 길 도착 레벨 (§9.7). 새 판에서 새 도호로.
	await t.restart()
	var w5 := await _fight(LV5)
	if w5.has("stop"):
		return
	t.check(w5.win, "Lv5 흑랑 처치 — %d번 안에 (%s)" % [ATTEMPTS, " → ".join(w5.tries)])
	if not w5.win:
		return
	t.check(w5.sec >= MIN_SEC, "Lv5 보스전이 순간이 아님 (%.1f초)" % w5.sec)
	t.check(w5.used >= 1 or w5.hp_min <= w5.hp0 * 0.7, "Lv5 대가가 있다 — 탕약 %d · 최저 생명 %.0f / %.0f" % [w5.used, w5.hp_min, w5.hp0])
	t.note("Lv5 목표 대조(이 판 — 판정은 25판 표 §9.7): %.1f초 (15~30) · 탕약 %d (1 안팎) · 최저 생명 %.0f%% (35~60)" % [w5.sec, w5.used, 100.0 * w5.hp_min / w5.max_hp])


func _dispose_replay() -> void:
	if is_instance_valid(_replay):
		_replay.finish()
		_replay.queue_free()
	_replay = null


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and is_instance_valid(_replay):
		# RefCounted 소멸 통지에서는 self 메서드를 호출할 수 없으므로 몸만 직접 정리한다.
		_replay.finish()
		_replay.queue_free()
		_replay = null


## #536 준비 키는 물리 경계에 맞춘다. 공통 입력/frames 구현은 그대로.
func _prepare_key(keycode: Key, ticks: int) -> void:
	await t.tree.physics_frame
	var tick0 := Engine.get_physics_frames()
	t._key_state(keycode, true)
	Input.flush_buffered_events()
	await t.tree.physics_frame
	t._key_state(keycode, false)
	Input.flush_buffered_events()
	for i in ticks - 1:
		await t.tree.physics_frame
	var elapsed_ticks := Engine.get_physics_frames() - tick0
	t.note("흑랑 준비 key=%d physics=%d expected=%d" % [keycode, elapsed_ticks, ticks])
	t.check(elapsed_ticks == ticks, "흑랑 준비 키 %d 물리 %d틱" % [keycode, ticks])


## #536 전투 입력 주기만 로컬6물리틱. 기존 process6회는 기계 부하에 따라 다른 물리 틱 사이에 끝난다.
func _combat_ticks() -> void:
	for i in 6:
		await t.tree.physics_frame
