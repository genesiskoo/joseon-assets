from pathlib import Path
from collections import defaultdict
import ast,json,subprocess,sys,time

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
out=base/'analysis'
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
tree=ast.parse((base/'worker/analyze_focused_pair558.py').read_text(encoding='utf-8'))
ns={}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'context','identity','differences'}],type_ignores=[]),'<pure-saved-analysis>','exec'),ns)
context,differences=ns['context'],ns['differences']
cmp={'__name__':'read_only_analysis'}
exec(compile((wt/'tools/combat_trace_compare.py').read_bytes(),str(wt/'tools/combat_trace_compare.py'),'exec'),cmp)
relative=cmp['relative_only']
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,data):
    assert not p.exists(),'preserve original evidence'
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pair=load(out/'focused_pair/comparison.json'); full=load(out/'focused_1_vs_full_1/comparison.json')
refs={'focused_1':pair['left_files'],'focused_2':pair['right_files'],'full_1':full['right_files']}
docs={mode:{(r['level'],r['attempt']):load(Path(r['file'])) for r in refs[mode]} for mode in refs}
roles={'doho0':{'role':1,'ordinal':0},'heukrang0':{'role':2,'ordinal':0},'guard_bat1':{'role':4,'ordinal':1},'guard_bat2':{'role':4,'ordinal':2},'summon_bat1':{'role':3,'ordinal':1},'summon_bat2':{'role':3,'ordinal':2}}
flag_fields=('stopped','clip_speed','stagger_future','stagger_remaining')
def first(events,predicate):return next(e for e in events if predicate(e))
def preceding(e,events,predicate=lambda r:r['body']=='doho0'):
    return next(r for r in reversed(events[:e['event_seq']-1]) if predicate(r))
def compact(e):
    fields=('position','velocity','clip','clip_position','clip_speed','stopped','stagger_remaining','stagger_future','busy_remaining','busy_future','committed','hp','mp','cooldowns','target','target_position','target_distance','swing','rng_state','slide_collisions')
    return {**context(e),'actor':roles.get(e['body']), 'fields':e['fields'],'state':{k:e['state'][k] for k in fields if k in e['state']}}
stages={};polls={};full_evidence={}
for mode,run in docs.items():
    stages[mode]={};polls[mode]={};full_evidence[mode]={}
    for key,doc in sorted(run.items()):
        events=doc['events']
        bound=first(events,lambda e:e['kind']=='body_bound' and e['body']=='doho0')
        poll=first(events,lambda e:e['kind']=='input_poll')
        cast=first(events,lambda e:e['kind']=='cast_success' and e['body']=='doho0')
        cast_attempt=preceding(cast,events,lambda e:e['kind']=='cast_attempt' and e['body']=='doho0')
        actual=first(events,lambda e:e['kind']=='receive_attack_before' and e['callsite']=='Enemy.receive_attack' and e['fields']['attack_rng_body']=='doho0')
        prior=preceding(actual,events)
        mark=preceding(actual,events,lambda e:e['kind']=='mark_fire' and e['body']=='doho0')
        incoming=first(events,lambda e:e['kind']=='receive_attack_before' and e['callsite']=='PlayerCombat.receive_attack')
        baseline={k:docs['focused_1'][key]['events'][1]['state'][k] for k in flag_fields}
        convergence=next((e for e in events if e['body']=='doho0' and e['event_seq']<=poll['event_seq'] and {k:e['state'].get(k) for k in flag_fields}==baseline),None)
        doho=[e for e in events if e['body']=='doho0' and e['event_seq']<=poll['event_seq']]
        # get_slide_collision* records the last move_and_slide; TRACE never initiates a collision query/move.
        initial_collision=relative(bound['state']['slide_collisions'])
        first_replaced=next((e for e in doho if relative(e['state']['slide_collisions'])!=initial_collision),None)
        stage={'binding':bound,'first_combat_input':poll,'first_accepted_cast_before':cast_attempt,'first_accepted_cast_after_resource':cast,
               'first_actual_impact_mark_before_fire':mark,'first_actual_impact_doho_before_receive':prior,'first_actual_impact_enemy_before_receive':actual,
               'first_incoming_receive':incoming,'first_baseline_flag_snapshot':convergence,'first_last_slide_cache_change':first_replaced}
        full_evidence[mode][str(key)]={'stages':stage,'all_doho_observations_to_first_input':doho,
                'first_actual_impact_window':events[max(0,actual['event_seq']-13):actual['event_seq']+3],
                'all_preparation_events':events[:poll['event_seq']],
                'scope':'first combat input is scenario input_poll; dev ]/V dispatch itself is evidenced by raw preparation logs/source, not an added input hook'}
        stages[mode][str(key)]={name:None if event is None else compact(event) for name,event in stage.items()}
        decisions=[]
        for e in events:
            if e['kind']!='input_poll':continue
            next_result=next(r for r in events[e['event_seq']:] if r['body']=='doho0' and r['kind'] in ('cast_rejected','cast_success'))
            next_attempt=next(r for r in events[e['event_seq']:] if r['body']=='doho0' and r['kind']=='cast_attempt')
            assert next_attempt['event_seq']<next_result['event_seq']
            decisions.append({'poll':e['fields']['poll'],'input':e,'attempt':next_attempt,'decision':next_result})
        polls[mode][key]=decisions

analysis={}
for name,modes in [('focused_pair',('focused_1','focused_2')),('focused_1_vs_full_1',('focused_1','full_1')),('focused_2_vs_full_1',('focused_2','full_1'))]:
    rows=[]
    for key in sorted(docs[modes[0]]):
        sk=str(key);sa,sz=stages[modes[0]][sk],stages[modes[1]][sk]
        diff={}
        for stage in ('first_combat_input','first_accepted_cast_before','first_accepted_cast_after_resource','first_actual_impact_doho_before_receive','first_actual_impact_enemy_before_receive'):
            diff[stage]={'left':{k:sa[stage][k] for k in ('event_seq','tick','kind','callsite','body','physics')},
                         'right':{k:sz[stage][k] for k in ('event_seq','tick','kind','callsite','body','physics')},
                         'state_changed_leaves':differences(relative(sa[stage]['state']),relative(sz[stage]['state'])),
                         'fields_changed_leaves':differences(relative(sa[stage]['fields']),relative(sz[stage]['fields']))}
        decision_diff=None
        for previous,(x,y) in enumerate(zip(polls[modes[0]][key],polls[modes[1]][key])):
            dx=(x['decision']['kind'],x['decision']['fields'].get('reason'))
            dy=(y['decision']['kind'],y['decision']['fields'].get('reason'))
            if dx!=dy:
                decision_diff={'poll':x['poll'],'left':x,'right':y,'prior_poll_decision_count_same':previous,
                               'attempt_state_changed_leaves':differences(relative(x['attempt']['state']),relative(y['attempt']['state'])),
                               'limit':'earlier decisions equal does not mean earlier process snapshots/every RNG timing were equal'}
                break
        series=[]
        selectors=[('accepted_cast',lambda e:e['body']=='doho0' and e['kind']=='cast_success'),
                   ('outgoing_impact',lambda e:e['kind']=='receive_attack_before' and e['callsite']=='Enemy.receive_attack' and e['fields']['attack_rng_body']=='doho0'),
                   ('incoming_receive',lambda e:e['kind']=='receive_attack_before' and e['callsite']=='PlayerCombat.receive_attack')]
        for label,pred in selectors:
            lists=[[e for e in docs[mode][key]['events'] if pred(e)] for mode in modes]
            first_time=None;first_receiver_source=None
            for i,(x,y) in enumerate(zip(*lists)):
                if first_time is None and x['tick']!=y['tick']:
                    first_time={'ordinal':i+1,'left':x,'right':y}
                sx=(x['body'],x['fields'].get('attack_rng_body'))
                sy=(y['body'],y['fields'].get('attack_rng_body'))
                if first_receiver_source is None and sx!=sy:
                    first_receiver_source={'ordinal':i+1,'left':x,'right':y}
            series.append({'kind':label,'left_count':len(lists[0]),'right_count':len(lists[1]),'first_tick_difference':first_time,
                           'first_receiver_source_order_difference':first_receiver_source,'all_left_events':lists[0],'all_right_events':lists[1]})
        rows.append({'level':key[0],'attempt':key[1],'left_mode':modes[0],'right_mode':modes[1],'stage_differences':diff,
                     'first_poll_decision_difference':decision_diff,'series':series,'causation':'earlier state differences must not be discarded; local gate explanation may be observed but no whole-battle root cause established'})
    analysis[name]=rows
write(out/'cohort_preparation_and_first_impact_01.json',{'candidate':'f1bf88f05a8eb48dd7d12510011245f3f6631e76','roles':roles,'stages':stages,'comparisons':analysis})
write(out/'cohort_preparation_original_evidence_01.json',full_evidence)
summary=[]
for mode,record in stages.items():
    for key,stage in record.items():
        def flag_record(name):
            e=stage[name]
            return None if e is None else {'seq':e['event_seq'],'tick':e['tick'],'kind':e['kind'],'flags':{k:e['state'].get(k) for k in flag_fields},'pos':e['state'].get('position'),'clip':e['state'].get('clip'),'clip_position':e['state'].get('clip_position')}
        summary.append({'run':mode,'battle':key,**{name:flag_record(name) for name in ('binding','first_baseline_flag_snapshot','first_combat_input','first_accepted_cast_before','first_actual_impact_doho_before_receive','first_last_slide_cache_change')}})
for name,rows in analysis.items():
    for row in rows:
        d=row['first_poll_decision_difference']
        summary.append({'comparison':name,'level':row['level'],'first_poll_decision_difference':None if d is None else {'poll':d['poll'],'left':compact(d['left']['decision']),'right':compact(d['right']['decision']),'before_state_delta':d['attempt_state_changed_leaves']},
                        'first_series_ticks':[(s['kind'],None if s['first_tick_difference'] is None else {'ordinal':s['first_tick_difference']['ordinal'],'left':context(s['first_tick_difference']['left']),'right':context(s['first_tick_difference']['right'])}) for s in row['series']]})
text=json.dumps(summary,ensure_ascii=False,indent=2)+'\n'
path=out/'cohort_first_impact_stdout_01.raw.log'
assert not path.exists();path.write_text(text,encoding='utf-8')
print(text)
