from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])

def trace(text):
    text = replace(text, 'static var _enabled := false\n', 'static var _enabled := false\nstatic var _generation := 0   # 진단 수명만. 게임/애니 카운터와 무관하다.\n')
    text = replace(text, 'static func begin(tree: SceneTree, meta: Dictionary, directory: String) -> void:', 'static func begin(tree: SceneTree, meta: Dictionary, directory: String) -> int:')
    text = replace(text, '\t_tree = tree\n\t_meta = meta.duplicate(true)', '\t_generation += 1\n\t_tree = tree\n\t_meta = meta.duplicate(true)')
    text = replace(text, '\tevent("battle_begin", "BalanceCombatRng.begin", null)\n', '\tevent("battle_begin", "BalanceCombatRng.begin", null)\n\treturn _generation\n\n\nstatic func owns(generation: int) -> bool:\n\treturn _enabled and generation > 0 and generation == _generation\n\n\nstatic func finish_owned(generation: int, reason: String, outcome: Dictionary = {}) -> Dictionary:\n\treturn finish(reason, outcome) if owns(generation) else {}\n')
    text = replace(text, '\tif not is_instance_valid(target) or not target.is_inside_tree():\n\t\treturn out', '\tif not is_instance_valid(target):\n\t\treturn out\n\tout["detached"] = not target.is_inside_tree()\n\tif not target.is_inside_tree():\n\t\treturn out')
    text = replace(text, '\t\tout["target_position"] = vector(target.global_position)\n\t\tvar flat := target.global_position - body.global_position\n\t\tflat.y = 0.0\n\t\tout["target_distance"] = exact(flat.length())', '\t\tout["target_detached"] = not target.is_inside_tree()\n\t\tif target.is_inside_tree():\n\t\t\tout["target_position"] = vector(target.global_position)\n\t\t\tvar flat := target.global_position - body.global_position\n\t\t\tflat.y = 0.0\n\t\t\tout["target_distance"] = exact(flat.length())')
    text = replace(text, 'return {"schema": 1, "engine_pid": OS.get_process_id(),', 'return {"schema": 1, "engine_pid": OS.get_process_id(), "raw_trace_generation": decimal(_generation),')
    return text
edit('core/combat_trace.gd', trace)

def fixture(text):
    text = replace(text, 'var _active := false\n', 'var _active := false\nvar _trace_owner := 0\n')
    text = replace(text, '\t_active = true\n\tif trace_enabled', '\t_active = true\n\t_trace_owner = 0\n\tif trace_enabled')
    text = replace(text, '\t\tTRACE.begin(_tree,', '\t\t_trace_owner = TRACE.begin(_tree,')
    text = replace(text, '\tif TRACE.enabled():\n\t\tTRACE.bind_actor', '\tif TRACE.owns(_trace_owner):\n\t\tTRACE.bind_actor')
    text = replace(text, '\tTRACE.finish(reason, outcome)\n\tclose()', '\t\tTRACE.finish_owned(_trace_owner, reason, outcome)\n\tclose()')
    text = replace(text, '\tTRACE.finish("closed")\n\t_active = false', '\tTRACE.finish_owned(_trace_owner, "closed")\n\t_trace_owner = 0\n\t_active = false')
    # Existing observer must also remain safe if cleanup sees an already-detached actor/target.
    text = replace(text, '\t\tif not is_instance_valid(actor):\n\t\t\treturn false\n\t\tvar target:', '\t\tif not is_instance_valid(actor) or not actor.is_inside_tree():\n\t\t\treturn false\n\t\tvar target:')
    text = replace(text, '\t\tif is_instance_valid(target):\n\t\t\ttarget_pos =', '\t\tif is_instance_valid(target) and target.is_inside_tree():\n\t\t\ttarget_pos =')
    return text
edit('tests/fixtures/balance_combat_rng.gd', fixture)

def unit(text):
    text = replace(text, '\t# Detached but valid body must never read global_position outside the tree.\n', '''\tawait _cross_generation(combat)
\t# Body remains in tree, but its still-valid target has already left it.
\tvar target := FakeEnemy.new()
\troot.add_child(target)
\tcombat.target = target
\tTRACE.begin(self,{"scenario":"balance_boss","base_seed":"20260916","level":3,"attempt":1},_directory.path_join("detached_target"))
\tTRACE.bind_actor(combat,"doho",0,combat._rng,combat._rng.seed,combat._rng.state)
\troot.remove_child(target)
\tTRACE.event("detached_target", "unit", combat)
\tvar target_state: Dictionary = TRACE.snapshot().events.back().state
\t_check(body.is_inside_tree() and target_state.target_detached and not target_state.has("target_position") and not target_state.has("target_distance"),
\t\t"몸만 tree에 있는 detached target의 전역 위치를 읽지 않음")
\t_check(TRACE.attack_target(combat,target).get("detached",false), "실제 공격 target도 detached로 보존")
\tTRACE.finish("detached_target")
\tcombat.target = null
\ttarget.free()
\t# Detached but valid body must never read global_position outside the tree.
''')
    return text + '''

func _cross_generation(combat: Node) -> void:
\tvar seed0: int = combat._rng.seed
\tvar state0: int = combat._rng.state
\tvar a := FIXTURE.new()
\troot.add_child(a)
\ta.begin(combat,20260916,3,1,AreaDb.DEFAULT_DUNGEON,2,Callable(),true,_directory.path_join("generation_a"))
\tvar token_a: int = a.get("_trace_owner")
\ta.finish()
\ta.queue_free()   # 실제 exit_tree는 B 시작 뒤 process 경계에서 도착한다.
\tvar b := FIXTURE.new()
\troot.add_child(b)
\tb.begin(combat,20260916,5,2,AreaDb.DEFAULT_DUNGEON,2,Callable(),true,_directory.path_join("generation_b"))
\tvar token_b: int = b.get("_trace_owner")
\tvar b_state: int = combat._rng.state
\t_check(token_b > token_a and TRACE.owns(token_b) and not TRACE.owns(token_a), "진단 수명 소유권은 새 판만 가짐")
\ta.finish({}, "late_finished")
\ta._exit_tree()
\t_check(TRACE.enabled() and TRACE.snapshot().battle.level == 5 and TRACE.finish_owned(token_a,"late_owned").is_empty()
\t\tand combat._rng.state == b_state, "A 중복 종료/구소유권은 B trace·RNG를 닫거나 바꾸지 않음")
\tawait process_frame
\t_check(TRACE.owns(token_b) and TRACE.snapshot().battle.attempt == 2 and combat._rng.state == b_state,
\t\t"A의 늦은 실제 exit_tree 이후에도 B가 계속 기록됨")
\tb.finish({"win":false})
\tb.free()
\t_check(not TRACE.enabled() and combat._rng.seed == seed0 and combat._rng.state == state0, "B 판만 한 번 종료·원 스트림 복원")
'''
edit('tests/test_combat_trace.gd', unit)

def doc(text):
    text = replace(text, '유효하지만 트리에서 빠진 몸은 detached로 표시한다.', '유효하지만 트리에서 빠진 몸/타깃은 detached로 표시하며 전역 위치를 읽지 않는다.')
    text = replace(text, '저장 전에 disabled로 바꾸며 원 fixture의 seed/state 복원·관찰 신호 정리를 유지한다.', '저장 전에 disabled로 바꾸며 원 fixture의 seed/state 복원·관찰 신호 정리를 유지한다. 진단 세대 소유권을 확인해 끝난 A fixture의 늦은 exit_tree/중복 finish가 새 B 판을 닫지 못하게 한다. 게임의 RNG/애니/세션 카운터는 재설정하지 않는다.')
    text = replace(text, '모든 cleanup 경로 idempotence,', '모든 cleanup 경로 idempotence·A 종료/B 시작/A 지연 종료,')
    return text
edit('docs/design/combat_trace_558.md', doc)
print('558 ownership and detached-target refinements applied')
