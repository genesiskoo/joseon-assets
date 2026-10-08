from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])

def deadlines(s):
    s=replace(s, ', "_charge_cd", "_stagger_until"]:', ', "_charge_cd"]:')
    s=replace(s, '\tif "state" in actor:\n', '''\t# 절대 deadline/sentinel을 raw로 두고 실제 남은 시간만 비교한다. runtime 값은 건드리지 않는다.
\tvar stagger_owner: Node = body if "_stagger_until" in body else actor
\tif "_stagger_until" in stagger_owner:
\t\tvar deadline := float(stagger_owner.get("_stagger_until"))
\t\tout["raw_stagger_until"] = exact(deadline)
\t\tout["stagger_remaining"] = exact(maxf(0.0, deadline - GameClock.now))
\t\tout["stagger_future"] = deadline > GameClock.now
\tif "state" in actor:
''')
    s=replace(s, '\t\tout["busy_until"] = exact(float(visual.get("_busy_until")))\n\t\tout["busy_remaining"] = exact(float(visual.get("_busy_until")) - GameClock.now)', '''\t\tvar deadline := float(visual.get("_busy_until"))
\t\tout["raw_busy_until"] = exact(deadline)
\t\tout["busy_remaining"] = exact(maxf(0.0, deadline - GameClock.now))
\t\tout["busy_future"] = deadline > GameClock.now''')
    return s
edit('core/combat_trace.gd',deadlines)
edit('tests/test_combat_trace.gd',lambda s: replace(replace(s, '\tvar active_skill := 0\n', '\tvar active_skill := 0\n\tvar _stagger_until := 0.0\n'), '\tfor mode in ["close",', '''\tvar epoch0 := GameClock.now
\tvar idle_states: Array[Dictionary] = []
\tfor epoch in [10.0, 20000.0]:
\t\tGameClock.now = epoch   # 단위에서만. 원 epoch를 동기 검사 끝에 돌린다.
\t\tTRACE.begin(self,{"scenario":"balance_boss","base_seed":"20260916","level":3,"attempt":1},_directory.path_join("epoch_%d" % int(epoch)))
\t\tTRACE.bind_actor(combat,"doho",0,combat._rng,combat._rng.seed,combat._rng.state)
\t\tTRACE.event("idle_epoch", "unit", combat)
\t\tidle_states.append(TRACE.snapshot().events.back().state)
\t\tTRACE.finish("epoch_unit")
\tGameClock.now = epoch0
\t_check(idle_states[0].busy_remaining == idle_states[1].busy_remaining and idle_states[0].busy_remaining == TRACE.exact(0.0)
\t\tand idle_states[0].stagger_remaining == idle_states[1].stagger_remaining and not idle_states[0].busy_future and not idle_states[1].stagger_future,
\t\t"다른 누적 epoch의 inactive sentinel은 가짜 상대시간 차이를 만들지 않음")
\t_check(idle_states[0].raw_busy_until == TRACE.exact(0.0) and idle_states[1].raw_stagger_until == TRACE.exact(0.0) and GameClock.now == epoch0,
\t\t"절대 deadline 원문과 원 GameClock 유지")
\tfor mode in ["close",'''))
edit('docs/design/combat_trace_558.md',lambda s: replace(replace(s, '원 swing/hitstop/session 카운터는', 'busy/stagger의 절대 deadline과 inactive sentinel은 raw로 보존하고 남은 시간(max(0, deadline-now))·deadline_future와 분리한다. 원 swing/hitstop/session 카운터는'), '러너는 timeout에서 PREDELETE를 기다리지 않고 fixture를 명시적으로 정리한다.', '러너는 scenario timeout에서 PREDELETE를 기다리지 않고 fixture를 명시적으로 정리한다. 외부 강제 프로세스 종료는 메모리 버퍼의 끝 JSON을 저장할 수 없으며 phase raw·timeout 메타만 보존된다.'))
print('FIX558 absolute deadline raw / inactive remaining contract')
