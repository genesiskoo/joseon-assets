from pathlib import Path
from collections import defaultdict
import ast, hashlib, json, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
out=base/'analysis'
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
source=ast.parse((base/'worker/analyze_focused_pair558.py').read_text(encoding='utf-8'))
defs=[node for node in source.body if isinstance(node,ast.FunctionDef) and node.name in {'context','identity','differences'}]
scope={}
exec(compile(ast.Module(body=defs,type_ignores=[]),'<saved-pure-analysis>','exec'),scope)
context,identity,differences=[scope[n] for n in ('context','identity','differences')]
normal_scope={'__name__':'read_only_analysis'}
exec(compile((wt/'tools/combat_trace_compare.py').read_bytes(),str(wt/'tools/combat_trace_compare.py'),'exec'),normal_scope)
relative=normal_scope['relative_only']

def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,data):
    assert not path.exists(),'preserve previous evidence'
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

pair_report=load(out/'focused_pair/comparison.json')
full_report=load(out/'focused_1_vs_full_1/comparison.json')
refs={'focused_1':pair_report['left_files'],'focused_2':pair_report['right_files'],'full_1':full_report['right_files']}
docs={mode:{(r['level'],r['attempt']):load(Path(r['file'])) for r in rows} for mode,rows in refs.items()}
result={}
for name,modes in [('focused_pair',('focused_1','focused_2')),('focused_1_vs_full_1',('focused_1','full_1')),('focused_2_vs_full_1',('focused_2','full_1'))]:
    comparisons=[]
    for key,a in sorted(docs[modes[0]].items()):
        b=docs[modes[1]][key]
        maps=[]
        for doc in (a,b):
            current=defaultdict(list)
            for event in doc['events']:
                current[(identity(event),event['tick'])].append(event)
            maps.append(current)
        first=None
        first_player=None
        matched_pairs=0
        for x in a['events']:
            k=(identity(x),x['tick'])
            index=next(i for i,e in enumerate(maps[0][k]) if e['event_seq']==x['event_seq'])
            if index>=len(maps[1].get(k,[])): continue
            matched_pairs+=1
            y=maps[1][k][index]
            if x['game_relative']!=y['game_relative']:
                row={'left':context(x),'right':context(y),'same_identity_tick_occurrence':True,'occurrence_index':index,
                     'state_and_payload_changed_leaves':differences(relative({'state':x['state'],'fields':x['fields']}),relative({'state':y['state'],'fields':y['fields']})),
                     'preceding_global_sequence_equal':False,'interpretation':'matching key is only diagnostic alignment after global order may already differ; exact clocks retained, no tolerance/root-cause claim'}
                if first is None: first=row
                if first_player is None and x['kind']=='player_physics': first_player=row
        comparisons.append({'level':key[0],'attempt':key[1],'left_mode':modes[0],'right_mode':modes[1],
                            'left_raw_epoch':a['raw_epoch'],'right_raw_epoch':b['raw_epoch'],
                            'first_same_identity_tick_occurrence_clock_difference':first,
                            'first_same_player_physics_tick_clock_difference':first_player,
                            'diagnostic_matched_pairs':matched_pairs,'left_events':len(a['events']),'right_events':len(b['events'])})
    result[name]=comparisons
save(out/'cohort_aligned_clock_01.json',{'candidate':'f1bf88f05a8eb48dd7d12510011245f3f6631e76','comparisons':result,'parent_536_complete':False})

windows={}
selected={'cast_attempt','cast_rejected','cast_success','input_event','mark_register','mark_fire','mark_cancel','hitstop_start','hitstop_restore','mixer_applied','receive_attack_before','receive_attack_after','attack_target','land_current_check'}
for mode,records in docs.items():
    doc=records[(5,1)]
    events=doc['events']
    windows[mode]={
        'battle':doc['battle'],'raw_epoch':doc['raw_epoch'],'first_40_events':events[:40],
        'cast_marker_receive_tick860_890':[e for e in events if 860<=e['tick']<=890 and e['kind'] in selected],
        'physics_tick860_890':[e for e in events if 860<=e['tick']<=890 and e['kind'] in ('player_physics','enemy_physics_before','enemy_physics_after_move') and e['body'] in ('doho0','guard_bat2')],
        'guard_boundary_tick1028_1040':[e for e in events if 1028<=e['tick']<=1040 and (e['body'] in ('doho0','guard_bat2') or e['fields'].get('attack_rng_body')=='guard_bat2')],
        'all_guard2_cast_marks_receive':[e for e in events if e['body']=='guard_bat2' and e['kind'] in selected or e['fields'].get('attack_rng_body')=='guard_bat2'],
    }
save(out/'cohort_Lv5_original_windows_01.json',windows)
summary=[]
for name,rows in result.items():
    for r in rows:
        first=r['first_same_player_physics_tick_clock_difference']
        summary.append({'comparison':name,'level':r['level'],'raw_epochs':[r['left_raw_epoch'],r['right_raw_epoch']],
                        'first_same_player_tick_clock':None if first is None else {'left':first['left'],'right':first['right'],'changed_leaf_count':len(first['state_and_payload_changed_leaves'])}})
text=json.dumps(summary,ensure_ascii=False,indent=2)+'\n'
path=out/'cohort_aligned_clock_stdout_01.raw.log'
assert not path.exists()
path.write_text(text,encoding='utf-8')
print(text)
