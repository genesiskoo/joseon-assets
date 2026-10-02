from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])

if '"detached"' not in (WT/'core/combat_trace.gd').read_text(encoding='utf-8'):
    edit('core/combat_trace.gd',lambda s: replace(s, '\tout["position"] = vector(body.global_position)', '\tif not body.is_inside_tree():\n\t\tout["detached"] = true\n\t\treturn out\n\tout["position"] = vector(body.global_position)').replace('"name": String(collider.name)', '"raw_name": String(collider.name)'))
def cleanup_reason(s):
    s=replace(s, 'func _dispose_replay() -> void:', 'func _dispose_replay(reason: String = "disposed") -> void:')
    s=s.replace('\t\t_replay.finish()', '\t\t_replay.finish({}, reason)', 1)
    return replace(s, '\t\t_replay.finish()','\t\t_replay.finish({}, "predelete")')
edit('tests/e2e/scenarios/balance_boss.gd',cleanup_reason)
edit('tests/e2e/e2e_runner.gd',lambda s: replace(s, 'sc.call("_dispose_replay")', 'sc.call("_dispose_replay", "runner_cleanup" if _finished else "runner_timeout")'))
edit('tests/fixtures/balance_combat_rng.gd',lambda s: replace(replace(replace(s, 'func _on_level_exiting() -> void:\n\tfinish()', 'func _on_level_exiting() -> void:\n\tfinish({}, "level_exiting")'), '\t\tfinish()\n\n\n## 호출·층 종료', '\t\tfinish({}, "level_changed")\n\n\n## 호출·층 종료'), 'func _exit_tree() -> void:\n\tfinish()', 'func _exit_tree() -> void:\n\tfinish({}, "fixture_exit")'))

write('tests/test_combat_trace.gd', '''extends SceneTree
## #558 signed64·기본off·관측 전후 RNG/위치·상대 식별자·수명 정리. 실제 balance cohort는 돌리지 않는다.
const TRACE := preload("res://core/combat_trace.gd")
const FIXTURE := preload("res://tests/fixtures/balance_combat_rng.gd")
const SCENARIO := preload("res://tests/e2e/scenarios/balance_boss.gd")
var _checks := 0
var _fails: Array[String] = []
var _directory := ""

class FakeCombat extends Node:
\tvar _rng := RandomNumberGenerator.new()
\tvar target: Node3D
\tvar hp := 130.0
\tvar max_hp := 130.0
\tvar mp := 60.0
\tvar max_mp := 60.0
\tvar cooldowns: Array[float] = [0.0]
\tvar active_skill := 0

class FakeEnemy extends CharacterBody3D:
\tvar _rng := RandomNumberGenerator.new()
\tvar _target: Node3D
\tvar hp := 195.0
\tvar max_hp := 195.0
\tvar state := 0

class FakeVisual extends Node:
\tvar _swing_no := 101
\tvar _hitstop_token := 91
\tvar _busy_until := 0.0
\tvar _committed := false
\tvar _stopped := false
\tvar _anim: AnimationPlayer


func _check(condition: bool, message: String) -> void:
\t_checks += 1
\tif not condition:
\t\t_fails.append(message)
\t\tpush_error("FAIL: " + message)


func _init() -> void:
\tawait process_frame
\t_directory = "user://trace_unit_%d_%d" % [OS.get_process_id(), Time.get_ticks_usec()]
\t_check(not TRACE.enabled(), "기본 off")
\tvar values: Array[int] = [9007199254740993, -9007199254740995, 9223372036854775807, -9223372036854775807 - 1, 0]
\tfor value in values:
\t\tvar payload := JSON.stringify({"state": TRACE.decimal(value)})
\t\tvar parsed: Dictionary = JSON.parse_string(payload)
\t\t_check(parsed.state is String and parsed.state == str(value) and int(parsed.state) == value, "signed64 JSON 문자열 보존 " + str(value))
\tvar body := CharacterBody3D.new()
\troot.add_child(body)
\tvar combat := FakeCombat.new()
\tbody.add_child(combat)
\tvar visual := FakeVisual.new()
\tvisual.name = "Visual"
\tbody.add_child(visual)
\tvisual._anim = AnimationPlayer.new()
\tvisual.add_child(visual._anim)
\tcombat._rng.seed = 20260916
\tvar state0 := combat._rng.state
\tvar position0 := body.global_position
\tTRACE.event("disabled", "unit", combat)
\t_check(combat._rng.state == state0 and body.global_position == position0, "off 관측은 실제 상태 불변")
\tTRACE.begin(self, {"scenario": "balance_boss", "base_seed": "20260916", "level":3, "attempt":1}, _directory.path_join("simple"))
\tTRACE.bind_actor(combat,"doho",0,combat._rng,combat._rng.seed,combat._rng.state)
\tTRACE.event("probe", "unit.actual_callsite", visual, {"state": TRACE.decimal(combat._rng.state)})
\t_check(combat._rng.state == state0 and body.global_position == position0, "on 관측도 RNG/위치 불변")
\tvar snap := TRACE.snapshot()
\t_check(snap.streams.size() == 1 and snap.not_spawned.size() == 5, "미생성 몸은 가짜 스트림 없이 표시")
\t_check(snap.events.back().body == "doho0" and snap.events.back().callsite == "unit.actual_callsite", "Visual 별칭도 실제 도호 역할/호출위치")
\tvisual._swing_no += 2
\tvisual._hitstop_token += 3
\tTRACE.event("after_swing", "unit", visual)
\t_check(TRACE.snapshot().events.back().state.swing == 2 and TRACE.relative_hitstop(visual,94) == 3 and visual._swing_no == 103, "상대 swing/hitstop만 계산 · 원 카운터 유지")
\t_check(TRACE.snapshot().events.back().state.raw_swing == "103", "절대 swing 원문 보존")
\tvar ended := TRACE.finish("unit")
\t_check(not TRACE.enabled() and ended.events.back().kind == "battle_end" and FileAccess.file_exists(TRACE.last_summary().path), "finish 저장과 disable")
\t_check(TRACE.finish("again").is_empty(), "finish idempotent")
\tfor mode in ["close", "finish", "level_exiting", "level_changed", "exit_tree", "dispose", "timeout", "predelete"]:
\t\tawait _lifecycle(combat, mode)
\t# Detached but valid body must never read global_position outside the tree.
\tTRACE.begin(self,{"scenario":"balance_boss","base_seed":"20260916","level":3,"attempt":1},_directory.path_join("detached"))
\tTRACE.bind_actor(combat,"doho",0,combat._rng,combat._rng.seed,combat._rng.state)
\troot.remove_child(body)
\tTRACE.event("detached", "unit", combat)
\t_check(TRACE.snapshot().events.back().state.get("detached",false), "tree_exiting 경계 detached 위치를 읽지 않음")
\tTRACE.finish("detached")
\tbody.free()
\t_check(not TRACE.enabled(), "모든 수명 뒤 off")
\tprint("COMBAT_TRACE_TEST checks=%d fails=%d %s" % [_checks,_fails.size(),"PASS" if _fails.is_empty() else "FAIL"])
\tquit(1 if not _fails.is_empty() else 0)


func _lifecycle(combat: Node, mode: String) -> void:
\tvar fixture := FIXTURE.new()
\troot.add_child(fixture)
\tvar seed0: int = combat._rng.seed
\tvar state0: int = combat._rng.state
\tvar adds0 := node_added.get_connections().size()
\tfixture.begin(combat,20260916,3,1,AreaDb.DEFAULT_DUNGEON,2,Callable(),true,_directory.path_join(mode))
\t_check(TRACE.enabled(), mode + " 시작에서 켜짐")
\tmatch mode:
\t\t"close": fixture.close()
\t\t"finish": fixture.finish()
\t\t"level_exiting": fixture._on_level_exiting()
\t\t"level_changed":
\t\t\tvar town := Node.new()
\t\t\tfixture._on_level_loaded(town)
\t\t\ttown.free()
\t\t"exit_tree": fixture._exit_tree()
\t\t"dispose", "timeout", "predelete":
\t\t\tvar scenario := SCENARIO.new()
\t\t\tscenario.set("_replay",fixture)
\t\t\tif mode == "predelete":
\t\t\t\tscenario = null
\t\t\telse:
\t\t\t\tscenario._dispose_replay("runner_timeout" if mode == "timeout" else "unit_dispose")
\t\t\t\tscenario = null
\t_check(not TRACE.enabled() and combat._rng.seed == seed0 and combat._rng.state == state0 and node_added.get_connections().size() == adds0,
\t\tmode + " flush/disable・원 RNG/연결 복원")
\t_check(TRACE.finish("duplicate").is_empty(), mode + " 중복 flush 없음")
\tif is_instance_valid(fixture) and not fixture.is_queued_for_deletion():
\t\tfixture.free()
\tawait process_frame
''')

# 기존 실전 피해 단위 대조 두 번째 판에서만 trace를 켜서 결과와 종료 RNG까지 off 판과 비교한다.
def actual_unit(s):
    s=replace(s,'const BASE := 20260916','const BASE := 20260916\nconst TRACE := preload("res://core/combat_trace.gd")')
    s=replace(s, '\tvar second := _combat_trace(combat, _boss, all_bats)', '''\tvar trace_dir := "user://balance_trace_unit_%d_%d" % [OS.get_process_id(), Time.get_ticks_usec()]
\tTRACE.begin(self, {"scenario":"balance_boss","base_seed":str(BASE),"level":3,"attempt":1}, trace_dir)
\tfor record in replay.get("_records"):
\t\tTRACE.bind_actor(record.actor.get_ref(), String(FIXTURE.ROLE_NAMES[record.role]), int(record.ordinal), record.rng, int(record.seed), int(record.initial))
\tvar second := _combat_trace(combat, _boss, all_bats)
\tvar observed := TRACE.finish("actual_attack_unit")
\t_check(observed.streams.size() == 6 and observed.events.any(func(row: Dictionary) -> bool: return row.kind == "receive_attack_before")
\t\tand observed.events.any(func(row: Dictionary) -> bool: return row.kind == "receive_attack_after"), "실제 받기 전후와 여섯 몸 읽기 전용 계측")''')
    return s
edit('tests/test_balance_rng.gd',actual_unit)
print('UNIT558 source and cleanup tests written')
