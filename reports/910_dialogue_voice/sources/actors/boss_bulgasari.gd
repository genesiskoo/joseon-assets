extends Boss
## 불가살이 — 쇠부리 폐광 3층 보스 (bosses_v2 §3 · §3.8, 보드 #507 — #69에서 쪼갬). 흑랑 틀(Boss: 페이즈 문턱 · 보장 드랍 · 봉인 조각 · 먹 스러짐 + 封 ·
## 처치 표시 · 스킬 포인트)을 그대로 쓰고 기제를 덧붙인다 — 기술 하나 = 함수 하나(bosses_v2 §6, 장산범 #494와 같은 이음매):
##   ① 쇠 무효 (§3.3): 물리 막이 = 데이터 resist_phys 85(칼이 15%만 든다 — 숫자 회색 · 「칼이 안 든다」 · 불똥) — hit_target · receive_attack
##   ② 달아오름 (§3.3): 화로 원(Brazier.FIRE_RADIUS + 몸)에 닿거나 불이 붙으면(화상 — 화염부 · 부적 진 · 불씨) 물리 막이 −50 · 이동 × 0.8 · 맞으면 휘청 ·
##      주황 빛 + 불씨 · 숫자 주황 · P1이면 1.5초 몸을 흔들며 물러난다 · 쇠 먹는 이빨에 맞으면 1초(#529 — 피해 창·빛만: 물러남·느려짐·휘청 없음
##      = is_fire_heated) — heat · _tick_braziers · apply_burn · _backoff · receive_attack
##   ③ 쇠 먹기 (§3.4): 물기가 닿으면 도호 엽전 3%(P3 5%, 최소 10)를 삼킨다 → 처치 때 × 1.2로 쏟아 돌려줌 · 방에 떨어진 무기·갑옷이 있으면 먼저 가서 먹는다
##      (6초 · 생명 +5%) — _land_on_player · _eat_gold · _try_eat · _drop_loot
##   ④ 페이즈 (§3.4 — 100 → 50 → 20): P1 물기 + 코 후려치기(셋째 공격) / P2 쇠사슬을 삼킨다(2초 무적 · 몸집 × 1.2 · 화로 하나 먹음) · 포효 · 코 둘째마다 ·
##      빨라짐 · 달아오름 5초 / P3 붉은 눈 · 돌진(흑랑 틀 DASH) · 엽전 5% · 불 달아오름 3초 — _tick_phase · _enter_p2 · _begin_roar · _enter_p3
##   ⑤ 글 (§3.8 「글 차례」): 도호 머리 위 알림 · 엽전 줄 · 도호 바크는 셸 한 차례(앞 줄이 진 뒤) · 처치 줄은 드랍·封 뒤 — _queue_line · _hush_lines (#511)
## 왜 이 구조인가: 장산범처럼 보스 하나 = 스크립트 하나(§6 대안 ①). 셋째 보스에서 공통을 페이즈 표(BossDef)로 뺄지 보자던 것(#494)은 — 셋이 겹치는 칸이
## 문턱 비율·알림 두 줄뿐이라(장산범 은신·목소리 / 불가살이 달아오름·쇠 먹기는 서로 안 겹친다) 아직 이르다, 구미호 때 다시 본다.
## 대안 = 달아오름을 오라(Enemy.set_buff — 막이 더하기)로 → 막이는 되지만 이동·휘청·빛·물러남·페이즈별 시간이 따로 돌아 결국 여기 상태가 필요하다, 기각 ·
## 화로 원을 Area3D로 → 헤드리스 시험의 손 틱에서 신호 순서가 흔들리고 화로 넷 × 몸 하나라 거리 넷이면 된다, 기각.
## 수치 = 데이터(data/enemies/boss_bulgasari.tres — 지역 레벨 9 곡선이 곱한다) · 기제의 시간·배수 = 아래 상수(bosses_v2 §3.8 표와 한 값).
## 페이즈별 값은 Vector3(P1, P2, P3) — test_balance가 이 줄을 글자로 읽는다(_script_consts).

const BRAZIER := preload("res://world/brazier.gd")
const Flat := preload("res://core/flat.gd")

## 페이즈 문턱 (§3.4 — 생명 100 → 50 → 20).
const P2_RATIO := 0.5
const P3_RATIO := 0.2
## 쇠 무효 · 달아오름 (§3.3 · elements_v2 §4.3): 물리 막이 = 데이터 resist_phys(85) → 달아오르면 이 값(−50).
const HEATED_PHYS := -50.0
## 달아오름 시간 (P1, P2, P3) — 화로 · 불(화상이 붙을 때 — 화염부 · 부적 진 · 불씨) (§3.7 「6 / 5 / 5초 (화염부 4/4/3)」).
const HEAT_BRAZIER := Vector3(6.0, 5.0, 5.0)
const HEAT_FIRE := Vector3(4.0, 4.0, 3.0)
## 달아오른 몸 — 이동 × · 맞으면 휘청(초, 데이터 stagger_sec 0 = 철갑은 안 휘청) (§3.3).
const HEATED_MOVE := 0.8
const HEATED_STAGGER := 0.25
## P1 달아오르면 공격 없이 몸을 흔들며 물러난다 — 시간 · 도호 반대쪽 거리 (§3.4 「화로에 들어간 직후가 안전한 딜 창」).
const BACKOFF_SEC := 1.5
const BACKOFF_DIST := 3.0
## 쇠 튕김 표시 (§3.3 팝업 회색 — 글은 「칼이 안 든다」, #546 대본 점검: 옛 「쇠가 먹힌다」는 「칼이 먹힌다(통한다)」로도 읽혔다): 달아오르지 않은 몸에 칼이 들면 숫자가 회색 · 글 한 줄은 이 초마다 한 번 · 불똥.
const IRON_LINE_EVERY := 2.0
const IRON_COLOR := Color(0.63, 0.65, 0.68)
const HEAT_COLOR := Color(1.0, 0.55, 0.2)
const SPARK_COLOR := Color(1.0, 0.86, 0.55)
## 달아오른 몸의 겉 — 주황 겉칠(상태 틴트 길) · 몸 빛(주황 · 세기 · 반경) (§3.1 「등줄기와 입에서 주황 발광 + 김」).
const HEAT_TINT := Color(1.0, 0.42, 0.1, 0.34)
const HEAT_LIGHT := Color(1.0, 0.5, 0.18)
const HEAT_LIGHT_ENERGY := 2.6
const HEAT_LIGHT_RANGE := 4.5
## 이동 (§3.7 — 3.2 / 3.6 / 3.6) = 데이터 move_speed × 이 배수(P2부터).
const P2_SPEED := 1.125
## 코 후려치기 (§3.4): 이만큼째 공격마다(P1 셋째 · P2부터 둘째 — #254 시뮬 읽기) · 선딜 0.7(코 치켜듦) · 앞 120° · 반경 2.5 · 물기 × 1.2 · 밀침 2.
const NOSE_EVERY := Vector3(3.0, 2.0, 2.0)
const NOSE_WINDUP := 0.7
const NOSE_FAN := 120.0
const NOSE_RANGE := 2.5
const NOSE_MULT := 1.2
const NOSE_KNOCK := 2.0
## P2 쇠사슬 삼키기 (§3.4): 무적 연출 초 · 몸집 × · 끝나면 가장 가까운 화로 하나를 먹는다(4 → 3).
const SWALLOW_SEC := 2.0
const P2_GROW := 1.2
## 포효 (§3.4 P2+): 쿨 · 첫 번(삼킨 뒤) · 선딜(몸 부풂) · 반경 · 밀침 · 경직 · 피해 0 — 도호가 반경 안일 때만 건다(화로 원 밖으로 밀어내기).
const ROAR_CD := 12.0
const ROAR_FIRST := 3.0
const ROAR_WINDUP := 1.0
const ROAR_RADIUS := 4.0
const ROAR_KNOCK := 3.0
const ROAR_STUN := 0.4
const ROAR_SWELL := 1.12
## P3 광란 (§3.4): 돌진(흑랑 틀 DASH — 데이터 dash_speed 12 · dash_length 8 · 거리 keep_distance 3~9) 쿨 · 첫 번 · 한 대 배수.
const DASH_CD := 8.0
const DASH_FIRST := 2.0
const DASH_MULT := 1.5
## 엽전 뜯기 (§3.4): 물기가 닿으면 도호 엽전의 % (P1, P2, P3) · 최소 · 처치 때 돌려주는 배수(§3.5 「삼킨 엽전 ×1.2」) · 쏟는 더미 수 상한.
const GOLD_BITE_PCT := Vector3(3.0, 3.0, 5.0)
const GOLD_BITE_MIN := 10
const GOLD_RETURN := 1.2
const GOLD_PILES_MAX := 4
## 바닥 쇠 먹기 (§3.4): 이 거리 안(같은 방) 바닥의 무기·갑옷 → 그리로(최대 EAT_SEC초) → 먹으면 생명 + EAT_HEAL · 둘러보는 간격 · 한 번 뒤 쉼 · 닿음.
const EAT_RANGE := 10.0
const EAT_SEC := 6.0
const EAT_HEAL := 0.05
const EAT_SCAN := 0.5
const EAT_COOLDOWN := 3.0
const EAT_ARRIVE := 1.3
## 붉은 눈 (§3.4 P3 「붉은 눈 발광」) — 몸 그림(Visual)의 자식 · 자리 = 흑랑 GLB × 1.3 머리 추정(장산범 눈 자리 × 1.083 — 진짜 모델이 오면 머리 뼈로).
const EYE_COLOR := Color(1.0, 0.16, 0.08)
const EYE_Y := 1.61
const EYE_FWD := 1.14
const EYE_GAP := 0.14
const EYE_R := 0.07

## 알림 (§3.2 방 진입 · §3.3 첫 달아오름 · §3.4 P2 · P3 · §3.5 처치) · 도호 바크 (§3.1 톤 — 능청은 도호 몫, D-086).
const INTRO_LINE := "쇠 냄새와 열기. 무언가 씹는 소리."
const HEAT_LINE := "쇠가 달아오른다 — 지금이다!"
const SWALLOW_LINE := "쇠사슬을 삼켰다 — 더 커진다."
const FRENZY_LINE := "불가살이가 미쳐 날뛴다."
const DEATH_LINE := "쇠 씹는 소리가 그쳤다."
const IRON_LINE := "칼이 안 든다"
const BARK_IRON := "쇠 좋아하나? 내 검은 안 돼."
const BARK_GOLD := "야! 그거 내 돈이야!"
const BARK_DEATH := "미안하다. 배고팠지."
## 엽전 바크는 이만큼 사이를 둔다(물릴 때마다 말하지 않게) · 도호 머리 높이.
const BARK_GOLD_EVERY := 12.0
const DOHO_BARK_HEIGHT := 1.7
## 도호 머리 위 글은 셸 한 차례 (#511, OverheadQueue). 알림(LINE_SEC) · 엽전 줄(GOLD_LINE_SEC) · 도호 바크(Bark.SEC)가 한 줄을 쓰고, 앞 줄이 진 뒤(+ LINE_GAP)에 다음 줄.
## 쇠 먹힘 · 무적 글(불가살이 머리 위)은 차례를 안 쓰고, 도호 줄이 떠 있으면 건너뛴다(한 줄만 — 회색 숫자·불똥이 그대로 알린다).
const LINE_SEC := DEATH_LINE_SEC
const GOLD_LINE_SEC := 1.0
const LINE_GAP := OverheadQueue.GAP
## 도호 머리 위 줄은 바닥 이름표(글자 3)·바크(6) 위에 그린다 — 처치 줄이 드랍 이름표 밑에 깔렸다(창 사진).
const LINE_PRIORITY := OverheadQueue.LINE_PRIORITY
## 처치 줄은 드랍이 다 앉고 바닥 封이 다 스러진 뒤(셸 홀드 1.8초). 흑랑·장산범도 같은 차례.
const DEATH_LINE_AFTER := OverheadQueue.SEAL_AFTER
## 불가살이 머리 위 글(쇠 먹힘 · 무적)의 높이 — 피해 숫자(키 + 0.2에서 떠오름) 위 한 뼘(DamagePopup.spawn이 1.9를 더 얹는다).
const HEAD_LINE_Y := 1.55
## 쇠사슬을 삼키는 동안 = 무적 — 칼이 튕기면 「무적」(이 초에 한 번) · 몸에 쇳빛 겉칠.
const INVULN_LINE := "무적"
const INVULN_LINE_EVERY := 0.8
const SWALLOW_TINT := Color(0.74, 0.78, 0.86, 0.32)

## 지금 페이즈(1~3) — e2e·단위 시험이 읽는다.
var phase: int = 1
## 달아오름 남은 초(피해 창 · 겉 · 빛 — 출처 모두) · 그중 불로 달아오른 몫(화로 · 화염부·부적 진·불씨 — 몸이 반응한다: P1 물러남 · 느려짐 · 맞으면 휘청 ·
## 화로를 더 안 먹음. 쇠 먹는 이빨 달아오름(&"weapon")은 이 칸을 안 채운다 — #529 지휘 판정) · 달아오른 횟수 · 마지막 출처(&"brazier" · &"fire" · &"weapon") · 먹은(끈) 화로 수.
var heat_left: float = 0.0
var fire_heat_left: float = 0.0
var heats: int = 0
var heat_source: StringName = &""
var braziers_used: int = 0
## 센 것 (e2e·단위 시험): 칼이 쇠에 먹힌 수 · 물러남 · 코 후려치기 · 포효(건 · 닿은) · 돌진 · 엽전 뜯기 · 삼킨 엽전 · 바닥 쇠 먹기(간 · 먹은) · 뜯은 쇠사슬.
var iron_hits: int = 0
var backoffs: int = 0
var noses: int = 0
var roars: int = 0
var roar_hits: int = 0
var dashes: int = 0
var gold_bites: int = 0
var eaten_gold: int = 0
var eat_tries: int = 0
var items_eaten: int = 0
var chains_ripped: int = 0
## 뜯은 벽 쇠사슬의 차례(뜯은 순서 — 층 그림 Geometry/Props/Chain의 인스턴스 번호) — 판정은 이 표와 _chain_xforms로 한다(#561).
var chains_torn: Array[int] = []
## 쇠사슬을 삼키는 중(무적) — P2 들머리.
var swallowing: bool = false

var _woke := false
var _attack_n := 0
var _roar_cd := 0.0
var _eat_scan := 0.0
var _eat_cd := 0.0
var _eat_target: Node3D = null
var _iron_line_t := 0.0
var _iron_barked := false
var _heat_said := false
var _gold_bark_t := -INF
## line_log = 선 줄 전부 {kind · text · at · end}(걷힌 바크는 걷힌 때까지) — 시험이 「한 순간에 두 줄 없음」을 잰다. 차례 자체는 OverheadQueue.
var line_log: Array = []
var _showing_kind: StringName = &""
var _showing_end := -INF
var _invuln_line_t := -INF
var _base_scale := 1.0
var _heat_light: OmniLight3D
var _heat_fx: Node3D
var _eyes: Node3D
var _grow_tw: Tween
## 벽 쇠사슬 그림 · 생성기가 심은 자리(그림 안 변환 — FieldBuilder.XFORMS_META). 몸이 설 때 _gather_chains가 채운다.
var _chain_mmi: MultiMeshInstance3D
var _chain_xforms: Array = []


func _ready() -> void:
	super._ready()   # Boss — 등급 BOSS · 무리 「boss」
	_gather_chains()
	_base_scale = _visual.scale.x
	_heat_light = OmniLight3D.new()
	_heat_light.name = "HeatLight"
	_heat_light.light_color = HEAT_LIGHT
	_heat_light.light_energy = HEAT_LIGHT_ENERGY
	_heat_light.omni_range = HEAT_LIGHT_RANGE
	_heat_light.shadow_enabled = false
	_heat_light.position = Vector3(0.0, def.height * 0.6, 0.0)
	_heat_light.visible = false
	add_child(_heat_light)
	_eyes = Node3D.new()
	_eyes.name = "Eyes"
	DARK_STEALTH.eye_dots(_eyes, EYE_Y, EYE_FWD, EYE_GAP, EYE_R, EYE_COLOR)   # 붉은 눈 두 점 (P3) — 장산범 눈과 한 벌(#865), 색만 붉게
	_eyes.visible = false
	_visual.add_child(_eyes)


func _physics_process(delta: float) -> void:
	OverheadQueue.tick()   # 기제보다 먼저 — 이 틱에 설 줄이 선 뒤에 쇠 먹힘 글이 건너뛴다
	if state != State.DEAD:
		_tick_bul(delta)
	super._physics_process(delta)   # Boss — 차례를 한 번 더(같은 시각이라 겹치지 않는다) · 쿨 · 페이즈 · Enemy


## 기제 틱 (물리 틱마다 — 상태기보다 먼저): 달아오름 시계 · 화로 원 · 포효·먹기 쉼 · 삼키기 끝(끊겼으면).
func _tick_bul(delta: float) -> void:
	fire_heat_left = maxf(0.0, fire_heat_left - delta)
	if heat_left > 0.0:
		heat_left = maxf(0.0, heat_left - delta)
		if heat_left <= 0.0:
			_cool()
	_tick_braziers()
	_roar_cd = maxf(0.0, _roar_cd - delta)
	_eat_cd = maxf(0.0, _eat_cd - delta)
	_iron_line_t = maxf(0.0, _iron_line_t - delta)
	if swallowing and busy_kind() != &"swallow":
		_end_swallow()   # 붙듦이 끊겼다(있을 수 없는 길이지만) — 삼키기를 끝맺는다


# ---------- ① 쇠 무효 · ② 달아오름 (§3.3) ----------

## 달아올랐나 — 피해 창(물리 막이 −50) · 주황 숫자 · 겉·빛. 출처 모두(쇠 먹는 이빨 포함).
func is_heated() -> bool:
	return heat_left > 0.0 and state != State.DEAD


## 불로 달아올랐나 — 화로·화염부(화상) 달아오름만. 몸이 반응한다: P1 물러남(달아오름 중 공격 멈춤) · 이동 × 0.8 · 맞으면 휘청 · 화로를 더 안 먹음.
## 쇠 먹는 이빨 달아오름(&"weapon")만이면 거짓 — 칼을 1초 안쪽으로 이어 치는 동안 놈이 내내 물러나 무력해지지 않게(#529 지휘 판정: 무기 = 피해 창·빛만).
func is_fire_heated() -> bool:
	return fire_heat_left > 0.0 and state != State.DEAD


## 달군다 — sec초(남은 것보다 길면 늘림). source = &"brazier" · &"fire" · &"weapon"(쇠 먹는 이빨 1초 — 피해 창·빛만, #529). 새로 달아오르면 겉·알림 ·
## 불로 달아오르기 시작하면(무기로 이미 빛나고 있었어도) P1 물러남. 반환 = 달궜나.
func heat(sec: float, source: StringName = &"fire") -> bool:
	if state == State.DEAD or sec <= 0.0:
		return false
	var was := is_heated()
	var was_fire := is_fire_heated()
	heat_left = maxf(heat_left, sec)
	heat_source = source
	if source != &"weapon":
		fire_heat_left = maxf(fire_heat_left, sec)
	if not was:
		heats += 1
		_on_heat()
	if phase == 1 and not was_fire and is_fire_heated():
		_backoff()
	return true


## 새로 달아오른 순간 — 불똥 · 주황 빛·겉칠 · 불씨 · 첫 번 알림. (P1 물러남은 불 달아오름만 — heat가 건다)
func _on_heat() -> void:
	_apply_heat_look()
	Vfx.play("burn_flash", global_position + Vector3(0.0, def.height * 0.6, 0.0), {"scale": 1.6})
	Audio.play("burn", global_position)
	if not _heat_said:
		_heat_said = true
		_queue_line(&"note", HEAT_LINE)


## 식었다 — 김이 빠지고 다시 철갑.
func _cool() -> void:
	_apply_heat_look()
	Vfx.play("ink_smoke", global_position + Vector3(0.0, def.height * 0.8, 0.0), {"color": Color(0.82, 0.82, 0.8), "scale": 1.4})


## 겉 = 쇠사슬을 삼키는 중이면 쇳빛 겉칠(무적) · 달아오름이면 주황 겉칠 · 몸 빛 · 등의 불씨 / 아니면 상태 틴트(한기·화상)로 되돌림.
func _apply_heat_look() -> void:
	var on := is_heated()
	_visual.set_tint(_body_tint())
	if _heat_light:
		_heat_light.visible = on
	if on and (_heat_fx == null or not is_instance_valid(_heat_fx)):
		_heat_fx = Vfx.attach("torch_embers", self, Vector3(0.0, def.height * 0.9, 0.0), {"scale": 2.4, "color": HEAT_LIGHT})
	elif not on and _heat_fx != null and is_instance_valid(_heat_fx):
		_heat_fx.queue_free()
		_heat_fx = null


## 상태 틴트(한기·화상)가 바뀌어도 무적 · 달아오른 겉칠이 이긴다.
func _status_look() -> void:
	super._status_look()
	if swallowing or is_heated():
		_visual.set_tint(_body_tint())


## 몸 겉칠 한 색 — 무적(쇠사슬 삼키기) > 달아오름 > 상태(한기·화상) > 없음.
func _body_tint() -> Color:
	if swallowing and state != State.DEAD:
		return SWALLOW_TINT
	if is_heated():
		return HEAT_TINT
	return _status.tint() if _status != null else Color(0, 0, 0, 0)


## 화로 원 — 불로 달아오르지 않은 몸이 붙은 화로의 불 원(FIRE_RADIUS + 제 몸 반지름) 안이면 그 화로를 먹고(꺼짐) 달아오른다.
## 불로 달아오른 몸은 불을 더 먹지 않는다(화로를 헛되이 끄지 않게 — 도호가 다음 화로를 고른다). 삼키는 중엔 안 본다.
## 쇠 먹는 이빨로만 달아 있는 몸은 화로를 먹는다(#529 — 무기 달아오름은 피해 창·빛만: 화로 유인·P3 제 발로 뛰어들기는 그대로).
func _tick_braziers() -> void:
	if is_fire_heated() or swallowing or not is_inside_tree():
		return
	var reach := BRAZIER.FIRE_RADIUS + def.radius * body_scale()
	for n in get_tree().get_nodes_in_group(&"brazier"):
		var b := n as Node3D
		if b == null or not b.has_method("can_heat") or not b.can_heat():
			continue
		if _flat(b.global_position) <= reach:
			b.douse()
			braziers_used += 1
			heat(HEAT_BRAZIER[phase - 1], &"brazier")
			return


## 불이 붙었다(화염부·부적 진의 화상 · 불씨) → 화상은 그대로 걸고 달아오른다(elements_v2 §3.3 「달아오름 = 화상이 붙을 때」). 무기 불 옵션은 화상이 없어 안 달군다.
func apply_burn(dps: float, sec: float) -> bool:
	var took := super.apply_burn(dps, sec)
	if state != State.DEAD:
		heat(HEAT_FIRE[phase - 1], &"fire")
	return took


## 맞는 쪽의 표 — 달아오르면 물리 막이 85 → −50(데이터 값과의 차를 더한다 — 오라·옵션 더하기는 그대로).
func hit_target() -> Dictionary:
	var t := super.hit_target()
	if is_heated():
		var res: Dictionary = t.res
		res[DamageCalc.RES_PHYS] = float(res.get(DamageCalc.RES_PHYS, 0.0)) + (HEATED_PHYS - def.resist_phys)
	return t


## 칼을 받는다 — 삼키는 중이면 무적(불똥 + 「무적」) · 달아오르면 주황 숫자(불로 달았으면 + 휘청) · 철갑이면 회색 숫자 + 「칼이 안 든다」(IRON_LINE_EVERY초마다) + 불똥 ·
## 첫 번 도호 바크 · 맞힌 칼이 쇠 먹는 이빨이면(mods.heat_sec, #529) 그 뒤에 달군다(피해 창·빛만).
func receive_attack(rng: RandomNumberGenerator, dmg_min: float, dmg_max: float, mult: float, accuracy: float, str_pct: float = 0.0, crit_chance: float = 0.0, blow: Dictionary = {}, adds: Dictionary = {}, mods: Dictionary = {}) -> int:
	if swallowing and state != State.DEAD and not _hidden:
		_blocked_hit()
		return 0
	var hot := is_heated()
	var fire := is_fire_heated()
	var n := super.receive_attack(rng, dmg_min, dmg_max, mult, accuracy, str_pct, crit_chance, blow, adds, mods)
	if n <= 0 or state == State.DEAD:
		return n
	_tint_number(HEAT_COLOR if hot else IRON_COLOR)
	if hot:
		# 휘청 0.25 = 불 달아오름만 (#529 — 쇠 먹는 이빨로 이어 치는 동안 맞을 때마다 휘청이면 놈이 무력해진다)
		if fire and state != State.WINDUP and state != State.DASH:
			var away := global_position - (_player.global_position if _player else global_position)
			away.y = 0.0
			_stagger_until = maxf(_stagger_until, GameClock.now + HEATED_STAGGER)
			_visual.play_hit(HEATED_STAGGER, away)
	elif String(last_hit_element) == "":
		iron_hits += 1
		Vfx.play("hit", global_position + Vector3(0.0, def.height * 0.55, 0.0), {"color": SPARK_COLOR, "scale": 1.3})
		if _iron_line_t <= 0.0 and not line_busy():
			_iron_line_t = IRON_LINE_EVERY
			_head_line(IRON_LINE, IRON_COLOR)
		if not _iron_barked:
			_iron_barked = true
			_queue_line(&"bark", BARK_IRON, 0.5)
	# 쇠 먹는 이빨 (elements_v2 §5.4, #529 — StatsCalc.hit_mods heat_sec): 이 칼에 맞으면 달아오름 그 초 — 피해 창(물리 막이 −50)·겉·빛은 화로·화염부와 같은 상태
	# (heat: 더 길게 달아 있으면 그대로), 몸의 반응(P1 물러남·느려짐·휘청·화로 안 먹음)은 없다(is_fire_heated — 지휘 판정).
	# 맞은 뒤에 건다 — 이 한 대는 맞을 때의 철갑/달아오름 그대로(숫자 색 · 「칼이 안 든다」). 빗나감·무적(삼키기)·처치 한 대는 위에서 돌아가 안 달군다
	var hs := float(mods.get("heat_sec", 0.0))
	if hs > 0.0:
		heat(hs, &"weapon")
	return n


## 부적을 받는다 — 삼키는 중이면 무적. 불 부적의 달아오름은 화상(apply_burn)이 건다.
func receive_spell(rng: RandomNumberGenerator, element: StringName, lo: float, hi: float, effects: Dictionary = {}, mods: Dictionary = {}) -> int:
	if swallowing and state != State.DEAD and not _hidden:
		_blocked_hit()
		return 0
	return super.receive_spell(rng, element, lo, hi, effects, mods)


## 삼키는 동안 칼·부적이 튕긴다 — 불똥 + 머리 위 「무적」(INVULN_LINE_EVERY초에 한 번 · 도호 줄이 떠 있으면 불똥만).
func _blocked_hit() -> void:
	Vfx.play("hit", global_position + Vector3(0.0, def.height * 0.55, 0.0), {"color": SPARK_COLOR, "scale": 1.3})
	if GameClock.now - _invuln_line_t >= INVULN_LINE_EVERY and not line_busy():
		_invuln_line_t = GameClock.now
		_head_line(INVULN_LINE, IRON_COLOR)


## 불가살이 머리 위 짧은 글(쇠 먹힘 · 무적) — 피해 숫자 위 한 뼘(P2 몸집을 따라 올라간다), 떠올랐다 사라진다(DamagePopup 알림 한 개).
func _head_line(text: String, c: Color) -> void:
	if is_inside_tree():
		DamagePopup.spawn(get_parent(), global_position + Vector3(0.0, HEAD_LINE_Y * maxf(body_scale(), _visual.scale.x), 0.0), text, c)


## 시간 피해(화상) — 삼키는 중이면 안 든다(무적 2초).
func _take_dot(amount: int, element: StringName) -> void:
	if swallowing:
		return
	super._take_dot(amount, element)


## 방금 이 몸 위에 뜬 피해 숫자(보통·큰 타격만 — 치명·처치는 제 색)를 물들인다 — 철갑 회색 · 달아오름 주황 (§3.3 팝업 색).
func _tint_number(c: Color) -> void:
	var l := DamagePopup.last()
	if l == null or int(l.get_meta("key", 0)) != get_instance_id():
		return
	if DamagePopup.is_v2():
		# 판 d (#716 PD ⑥): 철갑 = 회색 채움 그대로 · 달아오름 = 주황 후광(채움이면 불 피해로 읽힌다) — 물리 보통·큰만
		DamagePopup.tint_phys(l, c, c == HEAT_COLOR)
		return
	var kind := int(l.get_meta("kind", DamagePopup.Kind.NORMAL))
	if kind != DamagePopup.Kind.NORMAL and kind != DamagePopup.Kind.BIG:
		return
	l.modulate = Color(c.r, c.g, c.b, l.modulate.a)


## P1 달아오름 — 공격을 끊고 도호 반대쪽으로 BACKOFF_DIST 물러난다(BACKOFF_SEC 붙듦 · 걷는 칸으로) · 피격 동작으로 몸을 흔든다.
func _backoff() -> void:
	if state == State.DEAD or swallowing:
		return
	var p := _attacker()
	var away := global_position - (p.global_position if p != null else global_position)
	away.y = 0.0
	if away.length_squared() < 0.01:
		away = -Vector3(sin(_visual.rotation.y), 0.0, cos(_visual.rotation.y))
	var to := global_position + away.normalized() * BACKOFF_DIST
	if _level != null:
		var nw: Array = _level.nearest_walkable(Level.world_to_cell(to), 3)
		if nw[0]:
			var w := Level.cell_to_world(nw[1])
			to = Vector3(w.x, global_position.y, w.z)
	_cancel_attack()
	if hold(BACKOFF_SEC, {"kind": &"heat_backoff", "to": to, "arrive": 0.3}):
		backoffs += 1
		_visual.play_hit(BACKOFF_SEC, away)


## 불로 달아오른 몸은 느리다(× HEATED_MOVE) — 한기·페이즈·등급 곱(Enemy._move_dir) 위에. 쇠 먹는 이빨 달아오름만이면 제 빠르기(#529).
func _move_dir(dir: Vector3, delta: float) -> void:
	super._move_dir(dir, delta)
	if is_fire_heated():
		velocity.x *= HEATED_MOVE
		velocity.z *= HEATED_MOVE


# ---------- 깸 · 쫓기 (포효 · 바닥 쇠 먹기가 먼저) ----------

## 첫 만남 이름 카드(#843 · #871, boss_intro_843 §2.1) — 쇳소리가 먼저: 카드가 뜨는 순간 붙듦(바닥 쇠 먹기는 걷힌 뒤) + 쇠 긁는 소리 →
## 0.2초(intro_roar) 등의 쇠가시가 곤두서며 「쩡」(boss_intro_iron — 강철 별 + 쇠 불티) · 怒 없음. 소리 둘 = 전용(#880 — 옛 대역 soemeogi_wake · leader_wake).
const INTRO_SCRAPE_CUE := "boss_bulgasari_intro_scrape"
const INTRO_CLANG_CUE := "boss_bulgasari_intro_clang"
## 쇠가시 별 자리 = 몸 꼭대기의 이만큼(등 높이) · 몸을 못 재면 이 높이
const INTRO_SPIKE_AT := 0.62
const INTRO_SPIKE_FALLBACK := 1.1


func intro_hold(sec: float) -> void:
	super.intro_hold(sec)
	Audio.play(INTRO_SCRAPE_CUE, global_position)


func intro_roar() -> void:
	Audio.play(INTRO_CLANG_CUE, global_position)
	var top := _body_top()
	var y := top * INTRO_SPIKE_AT if top > 0.0 else INTRO_SPIKE_FALLBACK
	Vfx.play("boss_intro_iron", global_position + Vector3(0.0, y, 0.0))
	_intro_swell(1.06, 0.08, 0.32)
	_intro_kick(0.2)
	_intro_light_to(INTRO_LIGHT_ENERGY, 0.1)


## 깬다 — 처음 한 번 방 알림 「쇠 냄새와 열기. 무언가 씹는 소리.」(§3.2).
func wake(by_pack: bool = false, seen: Vector3 = Vector3.INF) -> bool:
	var now := super.wake(by_pack, seen)
	if now and not _woke:
		_woke = true
		_queue_line(&"note", INTRO_LINE)
	return now


func _tick_chase(delta: float, dist: float, to_player: Vector3) -> void:
	if phase >= 2 and _roar_cd <= 0.0 and _target != null and dist <= ROAR_RADIUS and _begin_roar():
		return
	if _try_eat(delta):
		return
	super._tick_chase(delta, dist, to_player)   # Boss — P3 돌진(_wants_charge) · Enemy 근접(물기 · 코)


# ---------- ④ P1 코 후려치기 (§3.4) ----------

## 근접 선딜 — 이만큼째 공격이면 코 후려치기(선딜 0.7 · 앞 120° 부채 예고 · 반경 2.5 · × 1.2 · 밀침 2). Enemy가 strike_mod를 읽는다(몸통 훑기 #326과 같은 길).
func _begin_windup() -> void:
	_attack_n += 1
	if _attack_n % int(NOSE_EVERY[phase - 1]) == 0:
		strike_mod = {"windup": NOSE_WINDUP * _atk_mult(), "fan_deg": NOSE_FAN, "range": NOSE_RANGE, "mult": NOSE_MULT, "nose": true}
		noses += 1
	super._begin_windup()


## 한 대를 낸다 — 코 후려치기면 맞은 몸을 몸 반대쪽으로 밀친다(Player.shove — 피해 뒤).
func _deal_melee(kind: StringName = &"melee", victim: Node = null) -> void:
	var nose := bool(strike_mod.get("nose", false))
	super._deal_melee(kind, victim)
	if not nose:
		return
	var v: Node = victim if victim != null else _target
	if is_instance_valid(v) and v.has_method("shove"):
		var d: Vector3 = (v as Node3D).global_position - global_position
		d.y = 0.0
		v.shove(d, NOSE_KNOCK)


## 한 대의 배수 — P3 돌진 × 1.5 (코 × 1.2는 strike_mod가 이미 곱한다).
func _strike_atk(kind: StringName) -> Dictionary:
	var atk := super._strike_atk(kind)
	if kind == &"dash":
		atk.dmg_min = float(atk.dmg_min) * DASH_MULT
		atk.dmg_max = float(atk.dmg_max) * DASH_MULT
	return atk


## 도호에게 한 대 — 물기(코 · 돌진 아님)가 닿으면 엽전을 뜯는다(분신이면 안 뜯는다).
func _land_on_player(atk: Dictionary, victim: Node = null) -> int:
	var dealt := super._land_on_player(atk, victim)
	var v: Node = atk.get("target")
	if dealt > 0 and StringName(atk.get("kind", &"")) == &"melee" and not bool(strike_mod.get("nose", false)) and v != null and v.is_in_group("player"):
		_eat_gold(v)
	return dealt


# ---------- ③ 쇠 먹기 (§3.4) ----------

## 엽전 뜯기 — 도호 엽전의 GOLD_BITE_PCT%(최소 GOLD_BITE_MIN, 가진 만큼) → 삼킨 엽전에 쌓인다(처치 때 × 1.2로 돌려줌) · 엽전 소리·불똥 ·
## 도호 머리 위 「−N냥(먹힘)」 → 그 줄이 진 뒤 도호 바크(BARK_GOLD_EVERY초에 한 번). 도호 줄이 이미 떠 있으면 글은 건너뛴다(한 줄만 — 소리·불똥은 그대로).
func _eat_gold(_victim: Node) -> void:
	var inv = GameState.inventory
	if inv == null or int(inv.gold) <= 0:
		return
	var want := maxi(GOLD_BITE_MIN, int(floor(float(inv.gold) * GOLD_BITE_PCT[phase - 1] * 0.01)))
	var took := int(inv.take_gold(want))
	if took <= 0:
		return
	gold_bites += 1
	eaten_gold += took
	Audio.play("pickup_coin", global_position)
	Vfx.play("pickup_coin", global_position + Vector3(0.0, def.height * 0.6, 0.0))
	if line_busy():
		return
	_queue_line(&"gold", "−%d냥(먹힘)" % took)
	if GameClock.now - _gold_bark_t >= BARK_GOLD_EVERY:
		_gold_bark_t = GameClock.now
		_queue_line(&"bark", BARK_GOLD)


## 바닥 쇠 먹기 — EAT_SCAN초마다 방 안 바닥의 무기·갑옷을 찾아 그리로 붙든다(최대 EAT_SEC초, 닿으면 _eat_done). 쫓기 중 · 쉼이 끝났을 때만.
func _try_eat(delta: float) -> bool:
	_eat_scan -= delta
	if _eat_scan > 0.0 or _eat_cd > 0.0:
		return false
	_eat_scan = EAT_SCAN
	var fi := _find_iron()
	if fi == null:
		return false
	var to := Vector3(fi.global_position.x, global_position.y, fi.global_position.z)
	_eat_target = fi
	if not hold(EAT_SEC, {"kind": &"eat_item", "to": to, "arrive": EAT_ARRIVE, "done": _eat_done}):
		_eat_target = null
		return false
	eat_tries += 1
	return true


## 먹을 쇠 — 바닥에 앉은 무기·갑옷(보통·매직·희귀 — 세트·유니크는 안 먹는다) · 이 몸에서 EAT_RANGE 안 · 층이 있으면 같은 방. 가장 가까운 것(없으면 null).
func _find_iron() -> Node3D:
	if not is_inside_tree():
		return null
	var room := _room_of(global_position)
	var best: Node3D = null
	var best_d := EAT_RANGE
	for n in get_tree().get_nodes_in_group("floor_item"):
		var fi := n as Node3D
		if fi == null or fi.is_queued_for_deletion() or not bool(fi.get("is_settled")):
			continue
		var it = fi.get("item")
		if not edible(it):
			continue
		var d := _flat(fi.global_position)
		if d > best_d:
			continue
		if room.size != Vector2i.ZERO and not room.has_point(Level.world_to_cell(fi.global_position)):
			continue
		best = fi
		best_d = d
	return best


## 불가살이가 먹는 물건인가 (§3.4 「떨어진 장비(무기·갑옷)」 — 세트·유니크는 벌점이 커서 뺀다, 퀘스트 물건 아님).
static func edible(it) -> bool:
	if it == null or not (it is ItemInstance):
		return false
	var item := it as ItemInstance
	if item.def == null or item.def.quest_item:
		return false
	if item.def.slot != ItemDef.Slot.WEAPON and item.def.slot != ItemDef.Slot.ARMOR:
		return false
	return item.rarity < ItemInstance.Rarity.SET


## 붙듦 끝 — 먹을 쇠에 닿았으면 먹는다(불똥 · 생명 + EAT_HEAL · 물건 사라짐), 6초 안에 못 닿았거나 도호가 먼저 주웠으면 그만. 다음 둘러보기는 EAT_COOLDOWN 뒤.
func _eat_done() -> void:
	var fi := _eat_target
	_eat_target = null
	_eat_cd = EAT_COOLDOWN
	if fi == null or not is_instance_valid(fi) or fi.is_queued_for_deletion():
		return
	if _flat(fi.global_position) > EAT_ARRIVE + 0.6:
		return
	items_eaten += 1
	Vfx.play("hit", fi.global_position + Vector3(0.0, 0.3, 0.0), {"color": SPARK_COLOR, "scale": 1.4})
	Audio.play("pickup", global_position)
	fi.queue_free()
	heal(max_hp * EAT_HEAL)


## 이 자리가 든 방 네모 (층이 없거나 방 밖 = 빈 네모 — 거리만 본다).
func _room_of(p: Vector3) -> Rect2i:
	if _level == null or not ("map" in _level) or _level.map == null:
		return Rect2i()
	var c := Level.world_to_cell(p)
	for r in _level.map.rooms:
		var rr: Rect2i = r
		if rr.has_point(c):
			return rr
	return Rect2i()


## 처치 — 삼킨 엽전 × 1.2를 더미 몇으로 쏟는다(§3.5 「와르르」) — 흑랑 틀 보장 드랍(매직 둘 · 유니크 · 사슬 조각 · 엽전 200 + 50 × 지역) 뒤에.
func _drop_loot() -> void:
	super._drop_loot()
	var total := int(round(float(eaten_gold) * GOLD_RETURN))
	if total <= 0:
		return
	var piles := clampi(int(ceil(float(total) / 60.0)), 1, GOLD_PILES_MAX)
	var chest := global_position + Vector3(0.0, def.height * 0.55, 0.0)
	var left := total
	for i in piles:
		var amt := left if i == piles - 1 else int(float(total) / float(piles))
		left -= amt
		EventBus.loot_dropped.emit(ItemInstance.create(ItemDb.get_def("coin"), amt), chest)


# ---------- ④ 페이즈 (§3.4) ----------

func _tick_phase() -> void:
	if phase == 1 and hp <= max_hp * P2_RATIO:
		_enter_p2()
	if phase == 2 and not swallowing and hp <= max_hp * P3_RATIO:
		_enter_p3()


## P2 쇠사슬 — 하던 짓을 끊고 SWALLOW_SEC 붙듦(무적) · 벽 쇠사슬 하나를 뜯어 삼킨다 · 몸집 × 1.2 · 알림 · 소리·링·카메라. 끝나면 _end_swallow.
func _enter_p2() -> void:
	phase = 2
	_phase2 = true
	speed_mult = P2_SPEED
	swallowing = true
	_cancel_attack()
	hold(SWALLOW_SEC, {"kind": &"swallow", "done": _end_swallow})
	_apply_heat_look()   # 쇳빛 겉칠 = 무적 (알림 줄은 삼킨 뒤 _end_swallow — 삼키는 동안 도호 줄 차례를 비워 둬야 튕긴 칼의 「무적」이 뜬다)
	Audio.play("boss_roar", global_position)
	Audio.play_gugak(&"boss_phase2")   # 꽹과리 휘몰이 (#881, gugak_sfx_plan §3 A2)
	roar_fx()   # 발 위 먹 파문 + 머리 위 怒 (#282 — Boss.roar_fx)
	_kick(0.2)
	_rip_chain()
	_visual.play_once("attack", SWALLOW_SEC)
	if _grow_tw and _grow_tw.is_valid():
		_grow_tw.kill()
	_grow_tw = create_tween()
	_grow_tw.tween_property(_visual, "scale", Vector3.ONE * _base_scale * P2_GROW, SWALLOW_SEC).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


## 삼키기 끝 — 무적이 풀리고 알림 「쇠사슬을 삼켰다 — 더 커진다.」 · 가장 가까운 화로를 화로째 먹는다(4 → 3, §3.4 「화로도 쇠다」) · 포효 첫 쿨.
func _end_swallow() -> void:
	if not swallowing:
		return
	swallowing = false
	_apply_heat_look()   # 쇳빛 겉칠을 걷는다(달아올라 있으면 주황)
	if state != State.DEAD:
		_queue_line(&"note", SWALLOW_LINE)
	_roar_cd = ROAR_FIRST
	var best: Node3D = null
	var best_d := INF
	if is_inside_tree():
		for n in get_tree().get_nodes_in_group(&"brazier"):
			var b := n as Node3D
			if b == null or not b.has_method("devour") or bool(b.get("eaten")):
				continue
			var d := _flat(b.global_position)
			if d < best_d:
				best_d = d
				best = b
	if best != null:
		best.devour()
		Vfx.play("hit", best.global_position + Vector3(0.0, 0.8, 0.0), {"color": SPARK_COLOR, "scale": 1.6})


## 벽 쇠사슬 자리를 받아 든다 (몸이 설 때 — 층이 지은 뒤에 보스를 세운다). 층 = 조상 Level(Enemy._level은 첫 틱에야 잡힌다).
## 자리 = 생성기가 심은 목록 — 헤드리스(더미 렌더러)는 MultiMesh 인스턴스 값을 단위 행렬로 돌려줘 그림에서 읽으면 늘 0번을 고르고 뜯은 것을 못 알아봤다(#561).
func _gather_chains() -> void:
	var n := get_parent()
	while n != null and not (n is Level):
		n = n.get_parent()
	var mmi := n.get_node_or_null("Geometry/Props/Chain") as MultiMeshInstance3D if n else null
	if mmi == null or mmi.multimesh == null:
		return
	_chain_mmi = mmi
	_chain_xforms = mmi.get_meta(FieldBuilder.XFORMS_META, [])


## 벽의 끊어진 쇠사슬 하나를 뜯는다 (§3.4 「벽의 끊어진 쇠사슬을 뜯어 삼킨다」) — 아직 안 뜯은 벽 사슬 중 이 몸에 가장 가까운 하나를 고르고(받아 든 목록 · chains_torn)
## 층의 쇠사슬 무리 그림(Geometry/Props/Chain — 멀티메시)에서 그것을 지운다.
func _rip_chain() -> void:
	if not is_instance_valid(_chain_mmi):
		return
	var best := -1
	var best_d := INF
	for i in _chain_xforms.size():
		if chains_torn.has(i):
			continue   # 이미 뜯었다
		var d := _flat(_chain_mmi.global_transform * (_chain_xforms[i] as Transform3D).origin)
		if d < best_d:
			best_d = d
			best = i
	if best < 0:
		return
	var spot: Vector3 = (_chain_xforms[best] as Transform3D).origin
	var at := _chain_mmi.global_transform * spot
	_chain_mmi.multimesh.set_instance_transform(best, Transform3D(Basis.from_scale(Vector3.ONE * 0.001), spot))
	chains_torn.append(best)
	chains_ripped += 1
	Vfx.play("hit", at + Vector3(0.0, 1.0, 0.0), {"color": SPARK_COLOR, "scale": 1.5})
	Vfx.play("dash_dust", at, {"scale": 1.2})


## 포효 (P2+) — 쿨이 돌았고 도호가 반경 안이면: ROAR_WINDUP 붙듦(몸 부풂 · 둥근 바닥 예고) → _roar_fire. 반환 = 걸었나.
func _begin_roar() -> bool:
	var w := ROAR_WINDUP * _atk_mult()
	_cancel_attack()
	if not hold(w, {"kind": &"roar", "done": _roar_fire}):
		return false
	_roar_cd = ROAR_CD
	roars += 1
	FanTelegraph.spawn(self, ROAR_RADIUS, 360.0, w)
	Audio.play("%s_attack" % def.id, global_position, "enemy_attack")
	_play_windup_clip(w)
	var tw := create_tween()
	var s := _visual.scale
	tw.tween_property(_visual, "scale", s * ROAR_SWELL, w * 0.8).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_property(_visual, "scale", s, w * 0.2)
	return true


## 포효가 터진다 — 반경 안 도호를 밀치고(3) 경직(0.4) · 피해 0 · 소리 · 링(반경) · 카메라.
func _roar_fire() -> void:
	Audio.play("boss_roar", global_position)
	roar_fx({"radius": ROAR_RADIUS, "no_glyph": true})   # 먹 파문만 — 12초마다 오는 공격에 怒를 쓰면 지친다(#282, vfx.md §8.1 ③ · 怒는 페이즈 포효에만)
	_kick(0.16)
	var p := target()
	if p == null or _flat(p.global_position) > ROAR_RADIUS + 0.3:
		return
	roar_hits += 1
	var d := p.global_position - global_position
	d.y = 0.0
	if d.length_squared() < 0.0001:
		d = Vector3(sin(_visual.rotation.y), 0.0, cos(_visual.rotation.y))
	if p.has_method("shove"):
		p.shove(d, ROAR_KNOCK)
	if p.has_method("stagger"):
		p.stagger(ROAR_STUN)


## P3 광란 — 알림 · 붉은 눈 · 돌진 첫 쿨 · 소리·링·카메라.
func _enter_p3() -> void:
	phase = 3
	_charge_cd = DASH_FIRST
	if _eyes:
		_eyes.visible = true
	_queue_line(&"note", FRENZY_LINE)
	Audio.play("boss_roar", global_position)
	Audio.play_gugak(&"boss_phase2")   # 꽹과리 휘몰이 (#881)
	roar_fx()   # 발 위 먹 파문 + 머리 위 怒 (#282 — Boss.roar_fx)
	_kick(0.2)


## 돌진은 P3에서만 — 쿨이 돌았고 거리 3~9 (흑랑 틀 돌격 = 선딜 0.5 「!!」 → DASH).
func _wants_charge(dist: float) -> bool:
	return phase >= 3 and _charge_cd <= 0.0 and dist >= def.keep_distance_min and dist <= def.keep_distance_max


## 돌진을 걸었으면 쿨 = DASH_CD (흑랑 틀은 6초).
func _do_attack(to_player: Vector3) -> void:
	var charged := _charging
	super._do_attack(to_player)
	if charged:
		_charge_cd = DASH_CD * _atk_mult()
		dashes += 1


# ---------- 처치 (§3.5 — Boss 틀 그대로) ----------

func _die() -> void:
	swallowing = false
	heat_left = 0.0
	fire_heat_left = 0.0
	if _heat_light:
		_heat_light.visible = false
	if _heat_fx != null and is_instance_valid(_heat_fx):
		_heat_fx.queue_free()
		_heat_fx = null
	if _eyes:
		_eyes.visible = false
	_hush_lines()   # 처치 순간 = 막타 숫자만 (#494)
	var was_boss := is_in_group("boss")
	super._die()   # Boss — 처치 줄 · 스킬 포인트 줄 = _queue_overhead → 이 몸의 줄 기록
	if was_boss:
		# 도호 바크 「…미안하다. 배고팠지.」 = 처치 줄 · 스킬 포인트 줄이 다 진 뒤
		_queue_line(&"bark", BARK_DEATH, 0.0, true)


## 처치 줄 · 스킬 포인트는 셸 차례(封 홀드는 Boss._die가 이미 걸었다). 선 줄은 line_log에 남긴다.
func _queue_overhead(kind: StringName, text: String, min_delay: float) -> void:
	_queue_line(kind, text, min_delay, true)


func _death_line() -> String:
	return DEATH_LINE


## 보장 엽전 (bosses_v2 §3.5 「엽전 200 + 50 × 층」 — 층을 지역 레벨로, 장산범과 같은 읽기 · 폐광 3층 = 650).
func _boss_coins() -> int:
	return 200 + 50 * area_level


# ---------- 그림 · 소리 · 말 ----------

## 선딜 동작 한 번(포효) — 몸 그림이 선딜 맞춤(#503 ActorVisual.play_windup — 클립 타격이 선딜 끝)을 알면 그것으로, 모르면 옛 길(공격 클립 1배속).
func _play_windup_clip(sec: float) -> void:
	if _visual.has_method("play_windup"):
		_visual.call("play_windup", sec)
	else:
		_visual.play_once("attack", sec + 0.25)


func _kick(amount: float) -> void:
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	if cam and cam.has_method("kick"):
		cam.kick(amount)


# ---------- 도호 머리 위 줄 (창 사진 — 알림 · 엽전 · 바크가 한 자리·한 때에 겹쳤다) ----------
## 차례는 셸(OverheadQueue, #511). 이 몸은 무엇을 언제 말할지만 넣고, 선 시각은 line_log에 남긴다.

## 지금 도호 줄이 떠 있거나 기다리는 줄이 있나 — 한 줄만 쓰는 글(쇠 먹힘 · 무적 · 엽전)은 이때 건너뛴다.
func line_busy() -> bool:
	return OverheadQueue.busy()


## 이 몸이 넣어 두고 아직 안 선 줄 수 · 그 마지막의 예정 시각 (시험).
func pending_count() -> int:
	return OverheadQueue.count_owner(self)


func pending_back() -> Dictionary:
	return OverheadQueue.peek_last(self)


## 도호 머리 위 한 줄을 셸 차례에 넣는다 — kind: &"note" · &"death" · &"skill"(LINE_SEC) · &"gold"(GOLD_LINE_SEC) · &"bark"(Bark.SEC).
## after_death = 쓰러진 뒤에도 선다(처치 줄 · 스킬 포인트 · 마지막 바크 — 그 밖은 쓰러지면 버린다).
## 반환 = 선 때까지 남은 초(바로 섰으면 0).
func _queue_line(kind: StringName, text: String, min_delay: float = 0.0, after_death: bool = false) -> float:
	if text == "":
		return -1.0
	var now := GameClock.now
	OverheadQueue.push(self, kind, text, min_delay, _line_sec(kind), after_death, _show_line.bind(kind, text))
	var peek := pending_back()
	if float(peek.at) < 0.0:
		return 0.0
	return maxf(0.0, float(peek.at) - now)


func _line_sec(kind: StringName) -> float:
	match kind:
		&"bark":
			return Bark.SEC
		&"gold":
			return GOLD_LINE_SEC
	return LINE_SEC


## 한 줄을 세운다 — 알림 = Boss._announce(도호 머리 위 · LINE_SEC 머묾 · 바닥 이름표 위에 그림) · 엽전 = 도호 머리 위 엽전 색 · 바크 = Bark(도호).
func _show_line(kind: StringName, text: String) -> Dictionary:
	if not is_inside_tree():
		return {}
	_showing_kind = kind
	_showing_end = GameClock.now + _line_sec(kind)
	var shown: Label3D = null
	match kind:
		&"note", &"death", &"skill":
			_announce(text)
			var label := DamagePopup.last()
			if _raise(label, text):
				shown = label
		&"gold":
			var p := _attacker()
			if p != null:
				DamagePopup.spawn(p.get_parent(), p.global_position, text, UiSkin.PRICE)
				var l := DamagePopup.last()
				if _raise(l, text):
					DamagePopup.linger(l, GOLD_LINE_SEC)
					shown = l
		&"bark":
			var pb := _attacker()
			if pb != null:
				shown = Bark.say(pb, text, DOHO_BARK_HEIGHT)
			_showing_end = GameClock.now + Bark.display_sec(shown, _line_sec(kind))
	line_log.append({"kind": kind, "text": text, "at": GameClock.now, "end": _showing_end})
	return {"nodes": [shown], "cut": _cut_shown_line}


func _cut_shown_line() -> void:
	if _showing_end > GameClock.now and not line_log.is_empty():
		_showing_end = GameClock.now
		var entry: Dictionary = line_log.back()
		entry.end = GameClock.now


## 방금 뜬 줄(글자가 맞으면)을 바닥 이름표·바크 위에 그린다. 반환 = 그 줄이었나 (셸이 없는 단위 시험이면 알림 팝업이 없다).
func _raise(l: Label3D, text: String) -> bool:
	if l == null or not is_instance_valid(l) or l.text != text:
		return false
	l.render_priority = LINE_PRIORITY
	l.outline_render_priority = LINE_PRIORITY - 1
	return true


## 처치 순간: 이 몸의 바크를 걷고 전투 중 대기를 버린다. 이미 선 알림·엽전은 Boss의 seal_hold가 걷는다 (#511).
func _hush_lines() -> void:
	var now := GameClock.now
	var p := _attacker() if is_inside_tree() else _player
	var cut := false
	var theirs: Label3D = Bark.current(p) if (p != null and is_instance_valid(p)) else null
	if theirs != null and theirs.text in [BARK_IRON, BARK_GOLD]:
		theirs.queue_free()
		cut = true
		if _showing_kind == &"bark" and _showing_end > now and not line_log.is_empty():
			_showing_end = now
			var entry: Dictionary = line_log.back()
			entry.end = now   # 걷힌 줄 — 기록도 지금 끝난 것으로
	OverheadQueue.hush(self, cut)


func _flat(p: Vector3) -> float:
	return Flat.dist(p, global_position)
