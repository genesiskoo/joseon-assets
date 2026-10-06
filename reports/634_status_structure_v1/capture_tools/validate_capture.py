"""#634 before/after actual status capture gate and exact binary-state comparison."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
ap=argparse.ArgumentParser()
ap.add_argument('phase')
a=ap.parse_args()
raw_path=BASE/(a.phase+'.raw.log')
raw=raw_path.read_text(encoding='utf-8-sig',errors='replace')
pass_line=re.search(r'VIDEO634 phase='+a.phase+r' checks=(\d+) fails=0 PASS',raw)
assert pass_line,'no successful capture summary'
errors=[line for line in raw.splitlines() if re.search(r'SCRIPT ERROR|Parse Error|SHADER ERROR|^ERROR:',line) and not re.match(r'ERROR: \d+ resources still in use at exit',line)]
assert not errors,'\n'.join(errors)
fixture=json.loads(re.search(r'^FIXTURE634 (.+)$',raw,re.M)[1])
assert fixture['save_context']=='user://video634_capture.json' and fixture['active_profile']==''
records={r['segment']:r for r in [json.loads(line) for line in re.findall(r'^COMBAT634 (.+)$',raw,re.M)]}
assert list(records)==['burn','chill','frozen','sal']
bounds={}
for label,edge,frame in re.findall(r'^CAPTURE (\w+) (BEGIN|END) (\d+)$',raw,re.M):
    bounds.setdefault(label,{})[edge]=int(frame)
summary=[]
for label,r in records.items():
    assert bounds[label]['END']-bounds[label]['BEGIN']==r['frames']==360
    for key in ['actor_frames','camera_frames','target_frames','player_status_frames','enemy_status_frames','animation_frames','combat_frames','clock_frames','talisman_cd_frames','time_scale_frames','rng_frames']:
        assert len(r[key])==360,(label,key)
    assert all(v==1.0 for v in r['time_scale_frames'])
    assert r['mp_before']==r['mp_after']
    assert r['state_rng_before']==r['state_rng_after']
    states=r['player_status_frames'] if label=='sal' else r['enemy_status_frames']
    bit={'burn':4,'chill':1,'frozen':2,'sal':16}[label]
    active=[i for i,s in enumerate(states) if int(s['mask'])&bit]
    assert active and not(int(states[-1]['mask'])&bit)
    assert r['stack_before']==(0 if label=='chill' else 5) and r['stack_after']==(0 if label=='chill' else 4)
    if label=='chill':
        assert len(r['hit_events'])==1 and r['cancel_frame']>=0
        assert len(r['shots'])==0 and all(not(int(s['mask'])&2) for s in states)
        assert r['stats']['add_cold_min']==2 and r['stats']['add_cold_max']==3
        assert r['weapon']['affixes']==[{'id':'cold_1','v':3.0}]
        assert r['combat_frames'][-1]['target']==-1 and r['combat_frames'][-1]['pending']=={}
        assert len(r['input_edges'])==4 and all(e['kind']=='native_left' for e in r['input_edges'])
    else:
        assert len(r['shots'])==1
        shot=r['shots'][0]
        assert shot['seed']==632 and shot['born_frame']<shot['exit_frame'] and shot['initial_rng']!=shot['final_rng']
        if label!='sal':
            assert shot['hits']==1 and shot['mult']==2.5 and shot['radius']==1.5
        else:
            assert shot['kind']=='enemy' and shot['element']=='sal' and shot['share']==0.6
            assert int(states[-1]['mask'])&32 and r['stats_after']['res_sal']==50
            assert active[-1]==241 and r['input_edges'][-2]['frame']==240  # actual native input: first mask32 snapshot242
    if label=='burn':
        assert len(r['status_ticks'])==4 and all(e['element']=='fire' for e in r['status_ticks'])
    summary.append({'label':label,'bounds':bounds[label],'status_active_frames':[active[0],active[-1]],'status_seconds_observed':len(active)/60,'hp_before_after':[r['hp_before'],r['hp_after']],'enemy_hp_before_after':[r['enemy_hp_before'],r['enemy_hp_after']],'hits':r['hit_events'],'status_ticks':r['status_ticks'],'end_mechanism':r['end_mechanism']})
probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size','-of','json',str(BASE/(a.phase+'.avi'))],text=True))
stream=next(s for s in probe['streams'] if s['codec_name']=='mjpeg')
assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1280,720,'60/1')
source_files=subprocess.check_output(['git','-C',str(ROOT),'ls-files','core','actors','items','skills','data/items/talisman_fire.tres','data/items/talisman_ice.tres','data/items/talisman_thunder.tres','data/items/talisman_salpuri.tres','data/enemies/nachalnyeo.tres','data/affixes/affix_db.tres'],text=True).splitlines()
source_files+=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--others','--exclude-standard','core','actors','items','skills'],text=True).splitlines()
source_files=sorted(set(n for n in source_files if Path(n).suffix in ['.gd','.gdshader','.tres']))
source_hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in source_files}
head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
if a.phase=='before':
    reference=json.loads((ROOT/'._tmp/632_element_structure_v1/after04_metadata.json').read_text(encoding='utf-8'))
    for n,digest in reference['source_hashes'].items():
        assert source_hashes[n]==digest,'BEFORE634 differs from final632 raw source: '+n
    assert not (ROOT/'core/vfx_status.gd').exists(),'status runtime already present in baseline632tree'
meta={'card':634,'phase':a.phase,'checks':int(pass_line[1]),'fps':60,'speed':1.0,'source_head':head,'source_hashes':source_hashes,'source_reference':'#632 final AFTER04 raw-byte snapshot for BEFORE; exact hashes retained','capture_script_sha256':hashlib.sha256((BASE/'capture_status.gd').read_bytes()).hexdigest(),'raw_log_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),'fixture':fixture,'bounds':bounds,'combat':records,'avi_probe':probe}
if a.phase!='before':
    before=json.loads((BASE/'before_metadata.json').read_text(encoding='utf-8'))
    for field in ['fixture','bounds','combat','fps','speed','capture_script_sha256']:
        assert before[field]==meta[field],'actual status/combat differs: '+field
(BASE/(a.phase+'_metadata.json')).write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print(json.dumps({'phase':a.phase,'checks':meta['checks'],'source_files':len(source_hashes),'capture_sha':meta['capture_script_sha256'],'source_ref':'final632 AFTER04 rawSHA144','frames':stream['nb_frames'],'duration':probe['format']['duration'],'isolated_save':True,'invariant_equal':a.phase!='before','segments':summary},ensure_ascii=False),flush=True)
