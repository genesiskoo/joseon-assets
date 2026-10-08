from pathlib import Path
import subprocess

WT = Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
OLD = 'C:/Users/FORYOUCOM/.codex/worktrees/536-balance-rng-replay/joseon'

def write(name, text, bom=False):
    p = WT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8-sig' if bom else 'utf-8', newline='\n')

def edit(name, fn):
    p = WT / name
    original = p.read_text(encoding='utf-8-sig')
    revised = fn(original)
    assert revised != original, name
    write(name, revised, name.endswith('.ps1'))

def replace(text, old, new):
    assert text.count(old) == 1, (old[:150], text.count(old))
    return text.replace(old, new, 1)

def old_file(name):
    return subprocess.check_output(['git', '-c', 'safe.directory='+OLD, '-C', OLD, 'show', 'e57f7666:'+name]).decode('utf-8')

write('core/combat_trace.gd', '''extends RefCounted
## #558 읽기 전용 전투 계측. 기본 꺼짐, 호출 위치에서 동기로 읽고 판 끝에만 저장한다.
## 역할/생성순서와 상대 tick/swing이 비교 키다. instance/frame/epoch는 raw 증거로만 남긴다.
## 왜 이 구조인가: 별도 스케줄러/신호 연결 없이 실제 경계를 읽어 선공권·RNG 소비 순서를 유지한다.
## 수동 애니 구동이나 전역 FPS 강제는 실전 경로를 바꾸므로 쓰지 않는다.

static var _enabled := false
static var _tree: SceneTree
static var _meta: Dictionary = {}
static var _events: Array[Dictionary] = []
static var _bodies: Dictionary = {}
static var _aliases: Dictionary = {}
static var _tick0 := 0
static var _frame0 := 0
static var _epoch := 0.0
static var _wall0 := 0
static var _observe_usec := 0
static var _directory := ""
static var _last_summary: Dictionary = {}


static func enabled() -> bool:
\treturn _enabled


static func requested() -> bool:
\treturn OS.get_cmdline_user_args().has("--combat-trace")


static func requested_directory() -> String:
\tfor arg in OS.get_cmdline_user_args():
\t\tif arg.begins_with("--combat-trace-dir="):
\t\t\treturn arg.trim_prefix("--combat-trace-dir=")
\treturn "user://combat_trace"


static func decimal(value: int) -> String:
\treturn str(value)   # signed64 → 문자열 직행. JSON 숫자/float를 경유하지 않는다.


static func exact(value: float) -> String:
\treturn "%.17f" % value


static func vector(value: Vector3) -> Array[String]:
\treturn [exact(value.x), exact(value.y), exact(value.z)]


static func begin(tree: SceneTree, meta: Dictionary, directory: String) -> void:
\tif _enabled:
\t\tfinish("replaced")
\t_tree = tree
\t_meta = meta.duplicate(true)
\t_events = []
\t_bodies = {}
\t_aliases = {}
\t_tick0 = Engine.get_physics_frames()
\t_frame0 = Engine.get_process_frames()
\t_epoch = GameClock.now
\t_wall0 = Time.get_ticks_usec()
\t_observe_usec = 0
\t_directory = directory
\t_enabled = true
\tevent("battle_begin", "BalanceCombatRng.begin", null)


## 바인딩은 기존 fixture가 정한 role/ordinal만 받는다. RNG·swing 상태를 바꾸지 않는다.
static func bind_actor(actor: Node, role: String, ordinal: int, rng: RandomNumberGenerator, seed: int, initial: int) -> void:
\tif not _enabled or not is_instance_valid(actor):
\t\treturn
\tvar started := Time.get_ticks_usec()
\tvar body := actor.get_parent() if role == "doho" else actor
\tvar visual := body.get_node_or_null("Visual")
\tvar swing0 := int(visual.get("_swing_no")) if visual != null else 0
\tvar key := role + str(ordinal)
\t_bodies[key] = {"actor": weakref(actor), "body": weakref(body), "visual": weakref(visual) if visual != null else null,
\t\t"rng": rng, "seed": decimal(seed), "initial": decimal(initial), "swing0": swing0,
\t\t"raw_actor_id": decimal(actor.get_instance_id()), "raw_body_id": decimal(body.get_instance_id())}
\t_aliases[actor.get_instance_id()] = key
\t_aliases[body.get_instance_id()] = key
\t_observe_usec += Time.get_ticks_usec() - started
\tevent("body_bound", "BalanceCombatRng._bind_actor", actor, {"role": role, "ordinal": ordinal, "seed": decimal(seed), "initial": decimal(initial)})


static func body_key(source: Node) -> String:
\tvar node := source
\twhile is_instance_valid(node):
\t\tif _aliases.has(node.get_instance_id()):
\t\t\treturn String(_aliases[node.get_instance_id()])
\t\tnode = node.get_parent()
\treturn "unbound" if source != null else "fixture"


static func rng_key(rng: RandomNumberGenerator) -> String:
\tfor key in _bodies:
\t\tif _bodies[key].rng == rng:
\t\t\treturn String(key)
\treturn "unbound"


static func _body_state(key: String) -> Dictionary:
\tif not _bodies.has(key):
\t\treturn {}
\tvar rec: Dictionary = _bodies[key]
\tvar out := {"rng_state": decimal((rec.rng as RandomNumberGenerator).state)}
\tvar actor: Node = rec.actor.get_ref()
\tvar body: Node3D = rec.body.get_ref()
\tif not is_instance_valid(actor) or not is_instance_valid(body):
\t\tout["freed"] = true
\t\treturn out
\tout["position"] = vector(body.global_position)
\tout["node_process_priority"] = actor.process_priority
\tout["node_physics_priority"] = actor.process_physics_priority
\tif body is CharacterBody3D:
\t\tout["velocity"] = vector(body.velocity)
\t\tout["collision_layer"] = body.collision_layer
\t\tout["collision_mask"] = body.collision_mask
\t\tout["on_floor"] = body.is_on_floor()
\t\tvar hits: Array[Dictionary] = []
\t\tfor i in body.get_slide_collision_count():
\t\t\tvar hit := body.get_slide_collision(i)
\t\t\tvar collider := hit.get_collider() as Node
\t\t\thits.append({"body": body_key(collider), "name": String(collider.name) if is_instance_valid(collider) else "freed",
\t\t\t\t"normal": vector(hit.get_normal()), "position": vector(hit.get_position()), "depth": exact(hit.get_depth())})
\t\tout["slide_collisions"] = hits
\tvar target: Node3D = actor.get("target") if key.begins_with("doho") else actor.get("_target")
\tif is_instance_valid(target):
\t\tout["target"] = body_key(target)
\t\tout["target_position"] = vector(target.global_position)
\t\tvar flat := target.global_position - body.global_position
\t\tflat.y = 0.0
\t\tout["target_distance"] = exact(flat.length())
\telse:
\t\tout["target"] = "none"
\tfor field in ["hp", "max_hp", "mp", "max_mp", "_attack_timer", "_cooldown", "_state_timer", "_charge_cd", "_stagger_until"]:
\t\tif field in actor:
\t\t\tout[field] = exact(float(actor.get(field)))
\tif "state" in actor:
\t\tout["state"] = int(actor.get("state"))
\tif "cooldowns" in actor:
\t\tvar cds: Array[String] = []
\t\tfor cd in actor.get("cooldowns"):
\t\t\tcds.append(exact(float(cd)))
\t\tout["cooldowns"] = cds
\t\tout["active_skill"] = int(actor.get("active_skill"))
\tvar visual: Node = rec.visual.get_ref() if rec.visual != null else null
\tif is_instance_valid(visual):
\t\tvar no := int(visual.get("_swing_no"))
\t\tout["swing"] = no - int(rec.swing0)
\t\tout["raw_swing"] = decimal(no)
\t\tout["busy_until"] = exact(float(visual.get("_busy_until")))
\t\tout["busy_remaining"] = exact(float(visual.get("_busy_until")) - GameClock.now)
\t\tout["committed"] = bool(visual.get("_committed"))
\t\tout["stopped"] = bool(visual.get("_stopped"))
\t\tvar mixer := visual.get("_anim") as AnimationPlayer
\t\tif mixer != null:
\t\t\tout["clip"] = String(mixer.current_animation)
\t\t\tout["clip_position"] = exact(mixer.current_animation_position)
\t\t\tout["clip_speed"] = exact(mixer.speed_scale)
\t\t\tout["mixer_callback_mode"] = int(mixer.callback_mode_process)
\t\t\tout["mixer_process_priority"] = mixer.process_priority
\t\t\tout["mixer_physics_priority"] = mixer.process_physics_priority
\treturn out


## phase는 호출자가 적은 경로와 실제 physics 여부 둘 다 보존한다. callback mode로 추정하지 않는다.
static func event(kind: String, callsite: String, source: Node, fields: Dictionary = {}) -> void:
\tif not _enabled:
\t\treturn
\tvar started := Time.get_ticks_usec()
\tvar key := body_key(source)
\tif source != null and key == "unbound":
\t\treturn   # 지정 보스 층의 실제 4~6몸만. 다른 층/FX의 가짜 스트림은 만들지 않는다.
\t_events.append({"event_seq": _events.size() + 1, "kind": kind, "callsite": callsite, "body": key,
\t\t"tick": Engine.get_physics_frames() - _tick0, "process_frame": Engine.get_process_frames() - _frame0,
\t\t"physics": Engine.is_in_physics_frame(), "game_relative": exact(GameClock.now - _epoch),
\t\t"raw_physics_frame": decimal(Engine.get_physics_frames()), "raw_process_frame": decimal(Engine.get_process_frames()),
\t\t"raw_game_time": exact(GameClock.now), "state": _body_state(key), "fields": fields.duplicate(true)})
\t_observe_usec += Time.get_ticks_usec() - started


static func snapshot() -> Dictionary:
\tvar streams: Array[Dictionary] = []
\tvar missing: Array[String] = []
\tfor key in ["doho0", "heukrang0", "guard_bat1", "guard_bat2", "summon_bat1", "summon_bat2"]:
\t\tif not _bodies.has(key):
\t\t\tmissing.append(key)
\t\t\tcontinue
\t\tvar rec: Dictionary = _bodies[key]
\t\tstreams.append({"body": key, "seed": rec.seed, "initial": rec.initial,
\t\t\t"final": decimal((rec.rng as RandomNumberGenerator).state), "raw_actor_id": rec.raw_actor_id,
\t\t\t"raw_body_id": rec.raw_body_id, "raw_swing_origin": decimal(int(rec.swing0))})
\treturn {"schema": 1, "battle": _meta.duplicate(true), "raw_epoch": exact(_epoch),
\t\t"raw_tick_origin": decimal(_tick0), "raw_process_origin": decimal(_frame0), "physics_hz": Engine.physics_ticks_per_second,
\t\t"time_scale": exact(Engine.time_scale), "streams": streams, "not_spawned": missing, "events": _events.duplicate(true)}


## 終了・timeout・途中中断・tree_exitingのどれでも1回だけ。出力より前にdisabledにする。
static func finish(reason: String, outcome: Dictionary = {}) -> Dictionary:
\tif not _enabled:
\t\treturn {}
\tevent("battle_end", "BalanceCombatRng.finish", null, {"reason": reason})
\tvar document := snapshot()
\tdocument["reason"] = reason
\tdocument["outcome"] = outcome.duplicate(true)
\tdocument["overhead"] = {"observe_usec": decimal(_observe_usec), "wall_usec": decimal(Time.get_ticks_usec() - _wall0),
\t\t"event_count": _events.size(), "scope": "bind/event collection only; serialization measured separately; no zero-impact claim"}
\t_enabled = false
\tvar serialize0 := Time.get_ticks_usec()
\tvar content := JSON.stringify(document)
\tvar serialization_usec := Time.get_ticks_usec() - serialize0
\tvar dir := ProjectSettings.globalize_path(_directory)
\tvar path := dir.path_join("trace_%d_Lv%d_attempt%d.json" % [OS.get_process_id(), int(_meta.get("level", 0)), int(_meta.get("attempt", 0))])
\tvar saved := false
\tif DirAccess.make_dir_recursive_absolute(dir) == OK and not FileAccess.file_exists(path):
\t\tvar file := FileAccess.open(path, FileAccess.WRITE)
\t\tif file != null:
\t\t\tfile.store_string(content)
\t\t\tfile.close()
\t\t\tsaved = true
\t_last_summary = {"path": path, "saved": saved, "reason": reason, "events": _events.size(), "pid": OS.get_process_id(),
\t\t"level": int(_meta.get("level", 0)), "attempt": int(_meta.get("attempt", 0)), "observe_usec": decimal(_observe_usec),
\t\t"serialization_usec": decimal(serialization_usec)}
\tprint("BALANCE_TRACE_FILE " + JSON.stringify(_last_summary))
\tif not saved:
\t\tpush_error("CombatTrace: trace output failed or would overwrite an existing file: " + path)
\t_tree = null
\t_bodies = {}
\t_aliases = {}
\t_events = []
\treturn document


static func last_summary() -> Dictionary:
\treturn _last_summary.duplicate(true)
''')

# #536候補のfixtureはmainの同ファイルと同じbaseからの追加分のみ。スケジュールを変更しない。
fixture = old_file('tests/fixtures/balance_combat_rng.gd')
fixture = replace(fixture, 'const PLAYER := 1', 'const TRACE := preload("res://core/combat_trace.gd")\n\nconst PLAYER := 1')
fixture = replace(fixture, 'var _physics_dt_max := 0.0', 'var _physics_dt_max := 0.0\nvar _dt_rows: Array[Dictionary] = []')
fixture = replace(fixture, '\t_active = true\n\t_bind_actor(combat, PLAYER, 0)', '''\t_dt_rows.clear()
\t_active = true
\tif TRACE.requested():
\t\tTRACE.begin(_tree, {"scenario": "balance_boss", "base_seed": TRACE.decimal(base), "level": level, "attempt": attempt}, TRACE.requested_directory())
\t_bind_actor(combat, PLAYER, 0)''')
fixture = replace(fixture, '\t_records.append(record)\n\tif _note.is_valid():', '''\t_records.append(record)
\tif TRACE.enabled():
\t\tTRACE.bind_actor(actor, String(ROLE_NAMES[role]), ordinal, rng, seed, int(rng.state))
\tif _note.is_valid():''')
fixture = replace(fixture, 'func finish() -> Array[Dictionary]:', 'func finish(outcome: Dictionary = {}, reason: String = "finished") -> Array[Dictionary]:')
fixture = replace(fixture, '\t\t\t_note.call("BALANCE_REPLAY_CLOCK " + JSON.stringify(clock_snapshot()))', '''\t\t\t_note.call("BALANCE_REPLAY_CLOCK " + JSON.stringify(clock_snapshot()))
\t\t\tfor row in _dt_rows:
\t\t\t\t_note.call("BALANCE_REPLAY_DT " + JSON.stringify(row))''')
fixture = replace(fixture, '\tclose()\n\treturn _finished.duplicate(true)', '\tTRACE.finish(reason, outcome)\n\tclose()\n\treturn _finished.duplicate(true)')
fixture = replace(fixture, '\t_active = false\n\t_boundary_samples = 0', '\tTRACE.finish("closed")\n\t_active = false\n\t_boundary_samples = 0')
fixture = replace(fixture, '\t\t_note.call("BALANCE_REPLAY_DT " + JSON.stringify({', '\t\t_dt_rows.append({')
fixture = replace(fixture, '"time_scale": "%.17f" % Engine.time_scale}))\n\t\t_next_trace_time', '"time_scale": "%.17f" % Engine.time_scale})\n\t\t_next_trace_time')
write('tests/fixtures/balance_combat_rng.gd', fixture)

scenario = old_file('tests/e2e/scenarios/balance_boss.gd')
scenario = replace(scenario, 'var _replay: Node', 'var _replay: Node\nconst TRACE := preload("res://core/combat_trace.gd")')
scenario = replace(scenario, '\t\tc.cast_active(boss.global_position)', '''\t\tif TRACE.enabled():
\t\t\tTRACE.event("input_poll", "balance_boss._attempt", c, {"poll": input_waits + 1, "point": TRACE.vector(boss.global_position)})
\t\tc.cast_active(boss.global_position)''')
scenario = replace(scenario, '\tr.rng = _replay.finish()', '''\tvar outcome := {"win": win, "attacks": r.attacks, "hits": r.hits, "guards": r.guards, "summoned": r.summoned,
\t\t"used": r.used, "input_polls": input_waits, "input_ticks_ok": input_ticks_ok}
\tfor field in ["sec", "phase2", "hp0", "hp", "hp_min", "max_hp", "boss_hp"]:
\t\toutcome[field] = "%.17f" % float(r[field])
\tr.rng = _replay.finish(outcome)''')
write('tests/e2e/scenarios/balance_boss.gd', scenario)

test = old_file('tests/test_balance_rng.gd')
write('tests/test_balance_rng.gd', test)
write('tools/balance_replay.py', old_file('tools/balance_replay.py'))

for name in ['actors/actor_visual.gd', 'actors/player_combat.gd', 'actors/player.gd', 'actors/enemy.gd']:
    edit(name, lambda s: replace(s, 'extends '+{'actors/actor_visual.gd':'Node3D','actors/player_combat.gd':'Node','actors/player.gd':'CharacterBody3D','actors/enemy.gd':'CharacterBody3D'}[name]+'\n', 'extends '+{'actors/actor_visual.gd':'Node3D','actors/player_combat.gd':'Node','actors/player.gd':'CharacterBody3D','actors/enemy.gd':'CharacterBody3D'}[name]+'\n\nconst TRACE := preload("res://core/combat_trace.gd")\n'))

def visual_hooks(s):
    s = replace(s, '\t_committed = true\n\n\n## 휘두르는 중인가', '\t_committed = true\n\tif TRACE.enabled():\n\t\tTRACE.event("swing_begin", "ActorVisual._begin_swing", self, {"clip": clip, "hit_ratio": TRACE.exact(hit_ratio), "speed": TRACE.exact(speed)})\n\n\n## 휘두르는 중인가')
    s = replace(s, '\t_marks.append(mk)\n\tget_tree().create_timer(due, false)', '\t_marks.append(mk)\n\tif TRACE.enabled():\n\t\tTRACE.event("mark_register", "ActorVisual._add_mark", self, {"raw_mark_swing": TRACE.decimal(int(mk.no)), "at": TRACE.exact(at), "due": TRACE.exact(due), "pending": _marks.size(), "timer_process_in_physics": false})\n\tget_tree().create_timer(due, false)')
    for func, kind in [('_on_mixer_marks', 'mixer_applied'), ('_mark_due', 'mark_timer_due'), ('_fire_mark', 'mark_fire'), ('_cancel_mark', 'mark_cancel')]:
        signature = 'func '+func+'('+('' if func=='_on_mixer_marks' else 'mk: Dictionary')+') -> void:\n'
        fields = '{"pending": _marks.size()}' if func=='_on_mixer_marks' else '{"raw_mark_swing": TRACE.decimal(int(mk.no)), "at": TRACE.exact(float(mk.at)), "late": bool(mk.late), "already_done": bool(mk.done)}'
        s = replace(s, signature, signature+'\tif TRACE.enabled():\n\t\tTRACE.event("'+kind+'", "ActorVisual.'+func+'", self, '+fields+')\n')
    s = replace(s, '\tvar tok := _hitstop_token\n\tget_tree().create_timer(sec, false)', '\tvar tok := _hitstop_token\n\tif TRACE.enabled():\n\t\tTRACE.event("hitstop_start", "ActorVisual.hit_stop", self, {"seconds": TRACE.exact(sec), "token": tok, "timer_process_in_physics": false})\n\tget_tree().create_timer(sec, false)')
    s = replace(s, '\t\tif tok == _hitstop_token:\n\t\t\t_stopped = false', '\t\tif TRACE.enabled():\n\t\t\tTRACE.event("hitstop_restore", "ActorVisual.hit_stop.timeout", self, {"token": tok, "current_token": _hitstop_token, "applies": tok == _hitstop_token})\n\t\tif tok == _hitstop_token:\n\t\t\t_stopped = false')
    for func in ['on_impact', 'on_swing_ratio']:
        sig_start = s.index('func '+func+'(')
        end = s.index('\n\n\n', sig_start)
        block = s[sig_start:end]
        block = replace(block, '\tif delay <= 0.0:\n\t\tcb.call()', '\tif delay <= 0.0:\n\t\tif TRACE.enabled():\n\t\t\tTRACE.event("mark_immediate", "ActorVisual.'+func+'", self, {"delay": TRACE.exact(delay)})\n\t\tcb.call()')
        s = s[:sig_start] + block + s[end:]
    return s
edit('actors/actor_visual.gd', visual_hooks)

def combat_hooks(s):
    s = replace(s, 'func _process(delta: float) -> void:\n', 'func _process(delta: float) -> void:\n\tif TRACE.enabled():\n\t\tTRACE.event("resource_process_before", "PlayerCombat._process", self, {"delta": TRACE.exact(delta)})\n')
    s = replace(s, '\t# 엣지 폴링 (player.gd와 같은 이유:', '\tif TRACE.enabled():\n\t\tTRACE.event("resource_process_after", "PlayerCombat._process", self, {"delta": TRACE.exact(delta)})\n\t# 엣지 폴링 (player.gd와 같은 이유:')
    s = replace(s, 'func _physics_process(delta: float) -> void:\n', 'func _physics_process(delta: float) -> void:\n\tif TRACE.enabled():\n\t\tTRACE.event("combat_physics", "PlayerCombat._physics_process", self, {"delta": TRACE.exact(delta)})\n')
    s = replace(s, 'func cast_active(cursor_world: Vector3) -> void:\n', 'func cast_active(cursor_world: Vector3) -> void:\n\tif TRACE.enabled():\n\t\tTRACE.event("cast_attempt", "PlayerCombat.cast_active", self, {"point": TRACE.vector(cursor_world)})\n')
    start = s.index('func cast_active(')
    end = s.index('\n\n\nfunc ', start)
    # comments can separate next func; all return reasons are attached only to known guards
    block = s[start:end]
    cases = [
        ('if _dead or active_skill >= skills.size():\n\t\treturn', 'dead_or_missing_skill'),
        ('_player.queue_command({"kind": "cast_point", "point": cursor_world})\n\t\treturn', 'queued_motion_locked'),
        ('if lv <= 0:\n\t\treturn', 'unlearned'),
        ('if cooldowns[active_skill] > 0.0 or mp < cost:\n\t\treturn', 'cooldown_or_mp'),
        ('if seal_i < 0:\n\t\t\treturn', 'missing_talisman'),
    ]
    for old, reason in cases:
        indent = '\t\t\t' if reason=='missing_talisman' else '\t\t'
        block = replace(block, old, old.rsplit(indent+'return',1)[0]+indent+'if TRACE.enabled():\n'+indent+'\tTRACE.event("cast_rejected", "PlayerCombat.cast_active", self, {"reason": "'+reason+'"})\n'+indent+'return')
    block = replace(block, '\tmp -= cost\n\tcooldowns[active_skill] = s.cooldown', '\tmp -= cost\n\tcooldowns[active_skill] = s.cooldown\n\tif TRACE.enabled():\n\t\tTRACE.event("cast_success", "PlayerCombat.cast_active", self, {"skill": String(s.id), "cost": TRACE.exact(cost), "mult": TRACE.exact(mult)})')
    block = replace(block, '\t\t_start_storm(active_skill, s, lv, mult, tier_lv, cursor_world)\n\t\treturn', '\t\t_start_storm(active_skill, s, lv, mult, tier_lv, cursor_world)\n\t\tif TRACE.enabled():\n\t\t\tTRACE.event("cast_success", "PlayerCombat.cast_active", self, {"skill": String(s.id), "kind": "storm"})\n\t\treturn')
    s = s[:start]+block+s[end:]
    s = replace(s, 'func _land(e, mult: float, check_range: bool, blow: Dictionary = {}) -> int:\n', 'func _land(e, mult: float, check_range: bool, blow: Dictionary = {}) -> int:\n\tif TRACE.enabled():\n\t\tTRACE.event("impact_range_check", "PlayerCombat._land", self, {"target": TRACE.body_key(e if is_instance_valid(e) else null), "check_range": check_range, "range": TRACE.exact(float(stats.attack_range) + LAND_RANGE_SLACK), "mult": TRACE.exact(mult)})\n')
    s = replace(s, '\tif generation == _session_generation:\n\t\t_land(e, mult, check_range, blow)', '\tif TRACE.enabled():\n\t\tTRACE.event("impact_generation_check", "PlayerCombat._land_if_current", self, {"generation": generation, "current_generation": _session_generation, "applies": generation == _session_generation})\n\tif generation == _session_generation:\n\t\t_land(e, mult, check_range, blow)')
    s = replace(s, 'func use_belt(i: int) -> void:\n', 'func use_belt(i: int) -> void:\n\tif TRACE.enabled():\n\t\tTRACE.event("belt_attempt", "PlayerCombat.use_belt", self, {"slot": i})\n')
    return s
edit('actors/player_combat.gd', combat_hooks)

# receive_attackは元処理を一度だけ同期呼び出し、入力RNGの前後を読んで戻り値を返す。
def receive_wrapper(s, owner):
    start = s.index('func receive_attack(')
    lineend = s.index('\n', start)
    signature = s[start:lineend]
    arguments = 'rng, dmg_min, dmg_max, attacker_acc, mult, element, share' if owner=='PlayerCombat' else 'rng, dmg_min, dmg_max, mult, accuracy, str_pct, crit_chance, blow, adds, mods'
    acc = 'attacker_acc' if owner=='PlayerCombat' else 'accuracy'
    wrapper = signature+'''\n\tif TRACE.enabled():
\t\tTRACE.event("receive_attack_before", "OWNER.receive_attack", self, {"attack_rng_body": TRACE.rng_key(rng), "attack_rng_state": TRACE.decimal(rng.state), "dmg_min": TRACE.exact(dmg_min), "dmg_max": TRACE.exact(dmg_max), "accuracy": TRACE.exact(ACC), "mult": TRACE.exact(mult)})
\tvar dealt := _receive_attack_untraced(ARGS)
\tif TRACE.enabled():
\t\tTRACE.event("receive_attack_after", "OWNER.receive_attack", self, {"attack_rng_body": TRACE.rng_key(rng), "attack_rng_state": TRACE.decimal(rng.state), "dealt": dealt})
\treturn dealt


'''.replace('OWNER', owner).replace('ARGS', arguments).replace('ACC', acc)
    return s[:start]+wrapper+signature.replace('func receive_attack(', 'func _receive_attack_untraced(')+s[lineend:]
edit('actors/player_combat.gd', lambda s: receive_wrapper(s,'PlayerCombat'))
edit('actors/enemy.gd', lambda s: receive_wrapper(s,'Enemy'))

def player_hooks(s):
    s = replace(s, 'func _physics_process(delta: float) -> void:\n', 'func _physics_process(delta: float) -> void:\n\tif TRACE.enabled():\n\t\tTRACE.event("player_physics", "Player._physics_process", self, {"delta": TRACE.exact(delta)})\n')
    s = replace(s, '\tif _holding_sec and not GameState.is_ui_captured():\n', '\tif _holding_sec and not GameState.is_ui_captured():\n\t\tif TRACE.enabled():\n\t\t\tTRACE.event("input_secondary_hold", "Player._process", self)\n')
    return s
edit('actors/player.gd', player_hooks)

def enemy_hooks(s):
    s = replace(s, 'func _physics_process(delta: float) -> void:\n', 'func _physics_process(delta: float) -> void:\n\tif TRACE.enabled():\n\t\tTRACE.event("enemy_physics_before", "Enemy._physics_process", self, {"delta": TRACE.exact(delta)})\n')
    # 全early-returnへの補助呼び出しは不要。開始stateと実移動直後stateで消費/衝突境界を観測。
    s = replace(s, '\tvar _hspeed := Vector2(velocity.x, velocity.z).length()\n\tif state == State.DASH', '\tif TRACE.enabled():\n\t\tTRACE.event("enemy_physics_after_move", "Enemy._physics_process", self)\n\tvar _hspeed := Vector2(velocity.x, velocity.z).length()\n\tif state == State.DASH')
    return s
edit('actors/enemy.gd', enemy_hooks)
edit('actors/boss.gd', lambda s: replace(s, 'func _physics_process(delta: float) -> void:\n', 'func _physics_process(delta: float) -> void:\n\tif TRACE.enabled():\n\t\tTRACE.event("boss_physics", "Boss._physics_process", self, {"delta": TRACE.exact(delta)})\n'))
edit('tests/e2e/e2e_runner.gd', lambda s: replace(s, '\tDamageCalc.sure_hit = false\n\tEnemy.knockdown_on = false\n\t# 창 모드 거름', '\t# #558 timeout/끊긴 await도 PREDELETE를 기다리지 않고 실제 fixture를 정리한다.\n\tif name == "balance_boss" and sc.has_method("_dispose_replay"):\n\t\tsc.call("_dispose_replay")\n\tDamageCalc.sure_hit = false\n\tEnemy.knockdown_on = false\n\t# 창 모드 거름'))

print('IMPLEMENT558 initial core/hooks/fixture integration complete')
