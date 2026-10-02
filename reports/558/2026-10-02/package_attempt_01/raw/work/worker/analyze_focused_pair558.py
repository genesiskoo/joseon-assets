from pathlib import Path
from collections import defaultdict
import hashlib, json, re, sys

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
out=base/'analysis/focused_pair'
report=json.loads((out/'comparison.json').read_text(encoding='utf-8'))
scope={'__name__':'read_only_analysis'}
exec(compile((wt/'tools/combat_trace_compare.py').read_bytes(),str(wt/'tools/combat_trace_compare.py'),'exec'),scope)
relative=scope['relative_only']

def write(name,data):
    path=out/name
    assert not path.exists(), 'keep prior analysis'
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def context(e):
    return {k:e[k] for k in ('event_seq','kind','callsite','body','tick','process_frame','physics','game_relative')}
def identity(e): return (e['kind'],e['callsite'],e['body'],e['physics'])
def differences(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        rows=[]
        for key in sorted(set(a)|set(b)):
            p=path+'.'+key if path else key
            if key not in a or key not in b: rows.append({'field':p,'left':a.get(key,{'missing':True}),'right':b.get(key,{'missing':True})})
            else: rows+=differences(a[key],b[key],p)
        return rows
    if isinstance(a,list) and isinstance(b,list):
        rows=[]
        for i in range(max(len(a),len(b))):
            if i>=len(a) or i>=len(b): rows.append({'field':path+f'[{i}]','left':a[i] if i<len(a) else {'missing':True},'right':b[i] if i<len(b) else {'missing':True}})
            else: rows+=differences(a[i],b[i],path+f'[{i}]')
        return rows
    return [] if a==b else [{'field':path,'left':a,'right':b}]
def first_delta(left,right):
    for i in range(max(len(left),len(right))):
        a=left[i] if i<len(left) else None
        b=right[i] if i<len(right) else None
        if a!=b: return {'index':i,'left':a,'right':b}
    return None
def transitions(doc):
    latest={s['body']:s['initial'] for s in doc['streams']}
    histories={key:[] for key in latest}
    for e in doc['events']:
        observations=[]
        if 'rng_state' in e['state']: observations.append((e['body'],e['state']['rng_state'],'state.rng_state'))
        fields=e['fields']
        if fields.get('attack_rng_body') in latest: observations.append((fields['attack_rng_body'],fields['attack_rng_state'],'fields.attack_rng_state'))
        for body,state,location in observations:
            if body in latest and state!=latest[body]:
                histories[body].append({'rng_body':body,'old':latest[body],'new':state,'observed_at':location,**context(e)})
                latest[body]=state
    for s in doc['streams']: assert latest[s['body']]==s['final'], ('unobserved final RNG difference',s['body'])
    return histories

docs={}
for side in ('left','right'):
    docs[side]={}
    for record in report[side+'_files']:
        doc=json.loads(Path(record['file']).read_text(encoding='utf-8'))
        docs[side][(record['level'],record['attempt'])]=doc

audits=[]
roles={'doho':1,'heukrang':2,'summon_bat':3,'guard_bat':4}
for i,side in enumerate(('left','right'),1):
    run_dir=base/'cohort'/f'focused_{i}'
    run=json.loads((run_dir/'RUN.json').read_text(encoding='utf-8-sig'))
    launch=json.loads((run_dir/'LAUNCH.json').read_text(encoding='utf-8-sig'))
    assert run['candidate_commit']==launch['candidate_commit']=='f1bf88f05a8eb48dd7d12510011245f3f6631e76'
    proof=report[side+'_provenance'][0]
    raw=Path(proof['phase']).parent/'godot.raw.log'
    text=raw.read_text(encoding='utf-8-sig')
    rng_rows=[]
    for m in re.finditer(r'흑랑 RNG Lv(\d+) 판(\d+) ([a-z_]+)(\d+) seed=(-?\d+) initial=(-?\d+)(?: final=(-?\d+))?',text):
        level,attempt,role,ordinal,seed,initial,final=m.groups()
        doc=docs[side][(int(level),int(attempt))]
        body=role+ordinal
        stream=next(s for s in doc['streams'] if s['body']==body)
        expected=int(doc['battle']['base_seed'])+int(level)*1000003+int(attempt)*10007+roles[role]*1009+int(ordinal)*101
        assert seed==stream['seed']==str(expected) and initial==stream['initial']
        if final is not None: assert final==stream['final']
        rng_rows.append({'level':int(level),'attempt':int(attempt),'body':body,'seed':seed,'initial':initial,'final':final})
    dt=[]; clocks=[]
    for line in text.splitlines():
        for tag,arr in [('BALANCE_REPLAY_DT',dt),('BALANCE_REPLAY_CLOCK',clocks)]:
            if tag+' ' in line: arr.append(json.loads(line.split(tag+' ',1)[1]))
    finals=[r for r in rng_rows if r['final'] is not None]
    attempts=proof['raw_rows']['BALANCE_REPLAY_ATTEMPT']
    audits.append({'run':run,'launch':launch,'run_sha256':hashlib.sha256((run_dir/'RUN.json').read_bytes()).hexdigest(),
                   'env':proof['raw_rows']['BALANCE_REPLAY_ENV'],'raw_rng_rows':rng_rows,'raw_dt_rows':dt,'raw_clock_rows':clocks,
                   'attempt_keys':[list(k) for k in sorted(docs[side])],'total_actual_traces':len(docs[side]),
                   'rng_initial_rows':len(rng_rows)-len(finals),'rng_final_rows':len(finals),'attempt_rows':len(attempts),
                   'legacy_summary_rows_observed':len(finals)+len(attempts),
                   'legacy_summary_scope':'this run has 12 final stream summaries + 2 attempts = 14; excludes initial rows/DT/events and is not a fixed completeness requirement',
                   'same_seed_formula_verified':True,'exit_code':proof['exit_code'],'timed_out':proof['timed_out']})
    dest=out/'phase_evidence'/f'focused_{i}'
    for name in ('RUN.json','LAUNCH.json','stdout.raw.log','stderr.raw.log'):
        path=dest/('cohort_'+name)
        assert not path.exists()
        path.write_bytes((run_dir/name).read_bytes())

analysis=[]
all_histories={}
for key in sorted(docs['left']):
    a,b=docs['left'][key],docs['right'][key]
    ca=next(row for row in report['battles'] if (row['level'],row['attempt'])==key)
    ea,eb=a['events'],b['events']
    prefix=0
    for x,y in zip(ea,eb):
        if identity(x)!=identity(y) or x['tick']!=y['tick']: break
        prefix+=1
    float_only_prefix=[{'left':context(x),'right':context(y),'left_float':x['game_relative'],'right_float':y['game_relative']}
                       for x,y in zip(ea[:prefix],eb[:prefix]) if x['game_relative']!=y['game_relative']]
    sd=ca['state_or_payload']
    state_index=sd['index']
    i_float=ca['relative_game_float17']['index']
    ha,hb=transitions(a),transitions(b)
    all_histories[str(key)]={'left':ha,'right':hb}
    rng=[]
    for body in ha:
        xa,xb=ha[body],hb[body]
        values_a=[r['new'] for r in xa];values_b=[r['new'] for r in xb]
        d=first_delta(values_a,values_b)
        td=first_delta([r['tick'] for r in xa],[r['tick'] for r in xb])
        ic=None
        for n,(x,y) in enumerate(zip(xa,xb)):
            if (x['kind'],x['callsite'],x['body'])!=(y['kind'],y['callsite'],y['body']):
                ic={'index':n,'left':x,'right':y};break
        rng.append({'body':body,'left_observed_transitions':len(xa),'right_observed_transitions':len(xb),
                    'first_state_sequence_difference':None if d is None else {'index':d['index'],'left':xa[d['index']] if d['index']<len(xa) else {'missing':True},'right':xb[d['index']] if d['index']<len(xb) else {'missing':True}},
                    'first_transition_tick_difference':None if td is None else {'index':td['index'],'left':xa[td['index']] if td['index']<len(xa) else {'missing':True},'right':xb[td['index']] if td['index']<len(xb) else {'missing':True}},
                    'first_transition_callsite_difference':ic,'left_initial':next(s['initial'] for s in a['streams'] if s['body']==body),
                    'right_initial':next(s['initial'] for s in b['streams'] if s['body']==body),'left_final':next(s['final'] for s in a['streams'] if s['body']==body),
                    'right_final':next(s['final'] for s in b['streams'] if s['body']==body),
                    'interpretation':'observed state transitions, not exact RNG draw count; equal value prefixes do not prove identical timing'})
    # Exact same-role physics-tick observations. Show every changed leaf at the first spatial boundary.
    physics=[]
    for body in ('doho0','heukrang0','guard_bat1','guard_bat2'):
        maps=[]
        for evs in (ea,eb):
            maps.append({(e['tick'],e['kind']):e for e in evs if e['body']==body and e['kind'] in ('player_physics','enemy_physics_before','enemy_physics_after_move')})
        first=None
        for ident in sorted(set(maps[0])&set(maps[1])):
            x,y=maps[0][ident],maps[1][ident]
            fields=('position','velocity','target','target_position','target_distance','slide_collisions')
            sa=relative({k:x['state'][k] for k in fields if k in x['state']})
            sb=relative({k:y['state'][k] for k in fields if k in y['state']})
            diff=differences(sa,sb)
            if diff:
                first={'left':context(x),'right':context(y),'differences':diff,
                       'full_state_differences':differences(relative(x['state']),relative(y['state']))}
                break
        physics.append({'body':body,'first_same_role_tick_spatial_difference':first,
                        'left_physics_observations':len(maps[0]),'right_physics_observations':len(maps[1])})
    window={}
    for side,evs,hs in [('left',ea,ha),('right',eb,hb)]:
        guard=hs['guard_bat2']
        first_guard=guard[0] if guard else None
        anchor=first_guard['event_seq']-1 if first_guard else None
        window[side]={'first_guard_bat2_transition':first_guard,
                      'around_first_guard_transition':evs[max(0,anchor-12):anchor+4] if anchor is not None else [],
                      'first_40_events':evs[:40]}
    row={'level':key[0],'attempt':key[1],'common_identity_tick_prefix_events':prefix,
         'first_exact_state_payload_difference':{'left':context(ea[state_index]),'right':context(eb[state_index]),'changed_leaves':differences(sd['left'],sd['right'])},
         'first_comparer_clock_difference':{'left':context(ea[i_float]),'right':context(eb[i_float]),
              'same_identity':identity(ea[i_float])==identity(eb[i_float]),'same_tick':ea[i_float]['tick']==eb[i_float]['tick']},
         'float_only_in_common_identity_tick_prefix':float_only_prefix,
         'rng_observations':rng,'physics_spatial_boundaries':physics,'evidence_windows':window,
         'causation':'not established; earliest observed deltas/clip/order are retained, but Lv3 outcomes and final RNG are identical despite those differences'}
    analysis.append(row)

write('coverage_and_rng.json',{'candidate':'f1bf88f05a8eb48dd7d12510011245f3f6631e76','audits':audits,'analysis':analysis,
      'raw_files_remain_unchanged':True,'draw_count_limit':'RNG state changes are observed only at existing hooks; individual internal draws are not instrumented',
      'parent_536_complete':False})
write('all_observed_rng_transitions.json',all_histories)
write('analysis_operations.json',{'scope':'read existing completed focused archives and frozen source only; no game/test launches; no candidate writes',
      'comparison_sha256':hashlib.sha256((out/'comparison.json').read_bytes()).hexdigest(),
      'analysis_sha256':hashlib.sha256((out/'coverage_and_rng.json').read_bytes()).hexdigest()})
for row in analysis:
    print('Lv',row['level'],'prefix',row['common_identity_tick_prefix_events'],'state',row['first_exact_state_payload_difference']['changed_leaves'])
    for r in row['rng_observations']:
        print(r['body'],r['left_observed_transitions'],r['right_observed_transitions'],'firstvalue',r['first_state_sequence_difference'],'firsttick',r['first_transition_tick_difference'])
    for r in row['physics_spatial_boundaries']:
        print('spatial',r['body'],r['first_same_role_tick_spatial_difference'])
