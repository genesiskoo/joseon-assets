from pathlib import Path
from collections import Counter, defaultdict
import ast, hashlib, json, re, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
wt = Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
base = Path('C:/workspace/joseon/._tmp/trace_558_20261002')
out = base/'analysis'
candidate = 'f1bf88f05a8eb48dd7d12510011245f3f6631e76'
scope = {'__name__':'read_only_analysis'}
exec(compile((wt/'tools/combat_trace_compare.py').read_bytes(), str(wt/'tools/combat_trace_compare.py'), 'exec'), scope)
relative = scope['relative_only']
# Reuse only pure read-only functions from the earlier saved analysis, not its main block.
original = ast.parse((base/'worker/analyze_focused_pair558.py').read_text(encoding='utf-8'))
selected = [node for node in original.body if isinstance(node, ast.FunctionDef) and node.name in {'context','identity','differences','first_delta','transitions'}]
helper_scope = {'relative':relative}
exec(compile(ast.Module(body=selected,type_ignores=[]), '<saved-pure-analysis-functions>', 'exec'), helper_scope)
context, identity, differences, first_delta, transitions = [helper_scope[name] for name in ('context','identity','differences','first_delta','transitions')]

def write(path, data):
    assert not path.exists(), 'preserve prior analysis: '+str(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def delta_events(events_left, events_right, diff):
    if diff is None:
        return None
    i = diff['index']
    return {'index':i,'left':context(events_left[i]),'right':context(events_right[i]),'changed_leaves':differences(diff['left'],diff['right'])}

reports = {name:load(out/name/'comparison.json') for name in ('focused_pair','focused_1_vs_full_1','focused_2_vs_full_1')}
run_proofs = {
    'focused_1':(reports['focused_pair']['left_provenance'], reports['focused_pair']['left_files']),
    'focused_2':(reports['focused_pair']['right_provenance'], reports['focused_pair']['right_files']),
    'full_1':(reports['focused_1_vs_full_1']['right_provenance'],reports['focused_1_vs_full_1']['right_files']),
}
docs, histories, audits = {}, {}, {}
role_ids = {'doho':1,'heukrang':2,'summon_bat':3,'guard_bat':4}
for mode, (proofs, files) in run_proofs.items():
    docs[mode] = {(row['level'],row['attempt']):load(Path(row['file'])) for row in files}
    histories[mode] = {key:transitions(doc) for key,doc in docs[mode].items()}
    run_dir = base/'cohort'/mode
    run, launch = load(run_dir/'RUN.json'), load(run_dir/'LAUNCH.json')
    assert run['candidate_commit'] == launch['candidate_commit'] == candidate and run['fixed_fps'] == 0
    rng_rows, dt_rows, clock_rows, env_rows, file_rows, phases = [],[],[],[],[],[]
    for proof in proofs:
        raw = Path(proof['phase']).parent/'godot.raw.log'
        text = raw.read_text(encoding='utf-8-sig')
        for match in re.finditer(r'흑랑 RNG Lv(\d+) 판(\d+) ([a-z_]+)(\d+) seed=(-?\d+) initial=(-?\d+)(?: final=(-?\d+))?', text):
            level, attempt, role, ordinal, seed, initial, final = match.groups()
            doc = docs[mode][(int(level),int(attempt))]
            stream = next(s for s in doc['streams'] if s['body']==role+ordinal)
            expected = int(doc['battle']['base_seed'])+int(level)*1000003+int(attempt)*10007+role_ids[role]*1009+int(ordinal)*101
            assert seed == stream['seed'] == str(expected) and initial == stream['initial']
            assert final is None or final == stream['final']
            rng_rows.append({'level':int(level),'attempt':int(attempt),'body':role+ordinal,'seed':seed,'initial':initial,'final':final})
        for line in text.splitlines():
            for tag, rows in [('BALANCE_REPLAY_DT',dt_rows),('BALANCE_REPLAY_CLOCK',clock_rows)]:
                if tag+' ' in line:
                    rows.append(json.loads(line.split(tag+' ',1)[1]))
        env_rows += proof['raw_rows']['BALANCE_REPLAY_ENV']
        file_rows += proof['raw_rows']['BALANCE_TRACE_FILE']
        phases.append({'phase':proof['phase'],'actual_argv':proof['launch']['argv'],'runtime_pid':proof['runtime_pid'],
                       'raw_sha256':proof['godot_sha256'],'exit_code':proof['exit_code'],'timed_out':proof['timed_out'],
                       'attempt_rows':proof['raw_rows']['BALANCE_REPLAY_ATTEMPT'],'tries_rows':proof['raw_rows']['BALANCE_REPLAY_TRIES']})
    finals = [r for r in rng_rows if r['final'] is not None]
    audit_rows = []
    for key,doc in sorted(docs[mode].items()):
        calls = defaultdict(lambda:{'before':0,'after':0,'positive_damage':0,'damage_sum':0,'before_events':[],'after_events':[]})
        for e in doc['events']:
            if e['callsite'] != 'PlayerCombat.receive_attack' or e['kind'] not in ('receive_attack_before','receive_attack_after'):
                continue
            source = e['fields']['attack_rng_body']
            row = calls[source]
            which = 'before' if e['kind']=='receive_attack_before' else 'after'
            row[which] += 1
            row[which+'_events'].append(e)
            if which == 'after':
                dealt = e['fields']['dealt']
                row['positive_damage'] += int(dealt > 0)
                row['damage_sum'] += dealt
        call_counts = {body:{k:v for k,v in row.items() if not k.endswith('_events')} for body,row in calls.items()}
        assert sum(v['before'] for v in calls.values()) == doc['outcome']['attacks']
        assert sum(v['after'] for v in calls.values()) == doc['outcome']['attacks']
        assert sum(v['positive_damage'] for v in calls.values()) == doc['outcome']['hits']
        receive_evidence = out/(mode+'_incoming_Lv'+str(key[0])+'_attempt'+str(key[1])+'.json')
        write(receive_evidence, {'level':key[0],'attempt':key[1],'all_incoming_calls_by_source':dict(calls)})
        clock = next(r for r in clock_rows if (r['level'],r['attempt'])==key)
        ds = [r for r in dt_rows if (r['level'],r['attempt'])==key]
        assert len(ds) == clock['dt_sample_count']
        assert clock['physics_hz']==60 and clock['time_scale']=='1.00000000000000000'
        assert clock['physics_dt_min']==clock['physics_dt_max']=='0.01666666666666667'
        observe, wall = int(doc['overhead']['observe_usec']), int(doc['overhead']['wall_usec'])
        audit_rows.append({'level':key[0],'attempt':key[1],'base_seed':doc['battle']['base_seed'], 'streams':doc['streams'],'not_spawned':doc['not_spawned'],
                           'outcome':doc['outcome'],'event_count':len(doc['events']),'incoming_counts':call_counts,'incoming_evidence':str(receive_evidence),
                           'clock':clock,'dt_sample_count':len(ds),'overhead':doc['overhead'],'observe_over_wall_percent':observe/wall*100,
                           'overhead_limit':'descriptive observer time only; no uninstrumented baseline/no zero-impact inference'})
    audits[mode] = {'run':run,'launch':launch,'phases':phases,'env':env_rows,'file_rows':file_rows,'raw_rng_rows':rng_rows,'raw_dt_rows':dt_rows,'raw_clock_rows':clock_rows,
                    'actual_attempt_keys':[list(key) for key in sorted(docs[mode])],'actual_attempt_count':len(docs[mode]),'battles':audit_rows,
                    'rng_initial_rows':len(rng_rows)-len(finals),'rng_final_rows':len(finals),'legacy_summary_rows':len(finals)+len(docs[mode]),
                    'legacy_scope':'12 final RNG stream summaries + 2 actual attempt summaries observed here; not a fixed14 completeness condition; initial/DT/event rows excluded',
                    'seed_formula_verified':True,'complete_saved_attempts_verified':True}

comparisons = {}
for name, modes in [('focused_pair',('focused_1','focused_2')),('focused_1_vs_full_1',('focused_1','full_1')),('focused_2_vs_full_1',('focused_2','full_1'))]:
    left_mode, right_mode = modes
    rows = []
    for b in reports[name]['battles']:
        key = b['level'],b['attempt']
        a,z = docs[left_mode][key],docs[right_mode][key]
        ea,ez = a['events'],z['events']
        ha,hz = histories[left_mode][key],histories[right_mode][key]
        prefix = 0
        for x,y in zip(ea,ez):
            if identity(x)!=identity(y) or x['tick']!=y['tick']:
                break
            prefix += 1
        pure_float_prefix = [{'left':context(x),'right':context(y)} for x,y in zip(ea[:prefix],ez[:prefix]) if x['game_relative']!=y['game_relative']]
        rng = []
        for body in ha:
            x,y = ha[body],hz[body]
            vd = first_delta([r['new'] for r in x],[r['new'] for r in y])
            td = first_delta([r['tick'] for r in x],[r['tick'] for r in y])
            def located(d):
                if d is None: return None
                i=d['index']
                return {'index':i,'left':x[i] if i<len(x) else {'missing':True},'right':y[i] if i<len(y) else {'missing':True}}
            rng.append({'body':body,'left_observed_transitions':len(x),'right_observed_transitions':len(y),
                        'first_value_sequence_difference':located(vd),'first_relative_tick_difference':located(td)})
        gx = sorted([r for body in ha for r in ha[body]],key=lambda r:r['event_seq'])
        gy = sorted([r for body in hz for r in hz[body]],key=lambda r:r['event_seq'])
        first_global = first_delta([(r['rng_body'],r['old'],r['new']) for r in gx],[(r['rng_body'],r['old'],r['new']) for r in gy])
        if first_global is not None:
            i=first_global['index']
            first_global={'index':i,'left':gx[i] if i<len(gx) else {'missing':True},'right':gy[i] if i<len(gy) else {'missing':True}}
        physics=[]
        for body in ('doho0','heukrang0','guard_bat1','guard_bat2'):
            maps=[{(e['tick'],e['kind']):e for e in evs if e['body']==body and e['kind'] in ('player_physics','enemy_physics_before','enemy_physics_after_move')} for evs in (ea,ez)]
            found={}
            for label, fields in [('own_motion',('position','velocity')),('target',('target','target_position','target_distance')),('collision',('slide_collisions',))]:
                for ident in sorted(set(maps[0])&set(maps[1])):
                    x,y=maps[0][ident],maps[1][ident]
                    delta=differences(relative({k:x['state'][k] for k in fields if k in x['state']}),relative({k:y['state'][k] for k in fields if k in y['state']}))
                    if delta:
                        found[label]={'left':context(x),'right':context(y),'changed_leaves':delta,'full_state_changed_leaves':differences(relative(x['state']),relative(y['state']))}
                        break
            physics.append({'body':body,'first_same_role_tick_difference':found})
        clock_idx=b['relative_game_float17']['index']
        row={'level':key[0],'attempt':key[1],'left_mode':left_mode,'right_mode':right_mode,'common_identity_tick_prefix_events':prefix,
             'first_event_order_difference':delta_events(ea,ez,b['event_order']),
             'first_tick_difference':delta_events(ea,ez,b['relative_physics_ticks']),
             'first_state_payload_difference':delta_events(ea,ez,b['state_or_payload']),
             'first_clock_difference':{'left':context(ea[clock_idx]),'right':context(ez[clock_idx]),'same_identity':identity(ea[clock_idx])==identity(ez[clock_idx]),'same_tick':ea[clock_idx]['tick']==ez[clock_idx]['tick']},
             'clock_float_differences_inside_common_identity_tick_prefix':pure_float_prefix,
             'rng':rng,'first_global_observed_rng_order_value_difference':first_global,'same_role_physics':physics,
             'outcome_changed_leaves':differences(a['outcome'],z['outcome']),
             'causation':'not established; process/clip/order differences and same-tick float-only observations are not automatically causes; RNG state transitions are observations, not internal draw counts'}
        rows.append(row)
    comparisons[name]=rows

write(out/'cohort_audit_01.json', {'candidate':candidate,'runs':audits,'total_actual_attempts':sum(len(d) for d in docs.values()),'parent_536_complete':False})
write(out/'cohort_observed_rng_01.json', {mode:{str(key):rows for key,rows in h.items()} for mode,h in histories.items()})
write(out/'cohort_first_divergence_01.json', {'candidate':candidate,'comparisons':comparisons,'parent_536_complete':False})
write(out/'cohort_analysis_operations_01.json',{'candidate':candidate,'scope':'read only all declared focused/full completed attempts; no game or test launches, candidate files untouched',
     'comparer_sha256':hashlib.sha256((wt/'tools/combat_trace_compare.py').read_bytes()).hexdigest(),
     'audit_sha256':hashlib.sha256((out/'cohort_audit_01.json').read_bytes()).hexdigest(),
     'divergence_sha256':hashlib.sha256((out/'cohort_first_divergence_01.json').read_bytes()).hexdigest()})
summary=[]
for name, rows in comparisons.items():
    for row in rows:
        summary.append({'comparison':name,'level':row['level'],'prefix':row['common_identity_tick_prefix_events'],
                        'first_state':row['first_state_payload_difference'],'first_order':row['first_event_order_difference'],
                        'first_clock':row['first_clock_difference'],'pure_clock_prefix_count':len(row['clock_float_differences_inside_common_identity_tick_prefix']),
                        'rng_counts':[(r['body'],r['left_observed_transitions'],r['right_observed_transitions']) for r in row['rng']],
                        'outcome_differences':row['outcome_changed_leaves']})
summary_path=out/'cohort_analysis_stdout_01.raw.log'
text=json.dumps(summary,ensure_ascii=False,indent=2)+'\n'
assert not summary_path.exists()
summary_path.write_text(text,encoding='utf-8')
print(text)
