from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent; ROOT=BASE.parent.parent
ap=argparse.ArgumentParser(); ap.add_argument('phase'); a=ap.parse_args()
rawpath=BASE/(a.phase+'.raw.log'); raw=rawpath.read_text(encoding='utf-8-sig',errors='replace')
success=re.search(r'VIDEO672 phase='+a.phase+r' checks=(\d+) fails=0 PASS',raw); assert success,'capture did not pass'
errors=[s for s in raw.splitlines() if re.search(r'SCRIPT ERROR|Parse Error|SHADER ERROR|^ERROR:',s) and not re.match(r'ERROR: \d+ resources still in use at exit',s)]; assert not errors,'\n'.join(errors)
fixture=json.loads(re.search(r'^FIXTURE672 (.+)$',raw,re.M)[1]); assert fixture['distance']==5 and fixture['save_context']=='user://video672_capture.json' and fixture['active_profile']==''
records={r['segment']:r for r in map(json.loads,re.findall(r'^COMBAT672 (.+)$',raw,re.M))}; assert list(records)==['fire','cold','lightning','sal']
bounds={}
for label,edge,frame in re.findall(r'^CAPTURE (\w+) (BEGIN|END) (\d+)$',raw,re.M): bounds.setdefault(label,{})[edge]=int(frame)
summary=[]
for label,r in records.items():
    assert bounds[label]['END']-bounds[label]['BEGIN']==r['frames']==360
    for key in ['actor_frames','camera_frames','target_frames','player_status_frames','enemy_status_frames','animation_frames','combat_frames','clock_frames','talisman_cd_frames','time_scale_frames','rng_frames']: assert len(r[key])==360,(label,key)
    assert r['actor_frames']==[r['actor_origin']]*360 and r['target_frames']==[r['target_origin']]*360
    assert r['time_scale_frames']==[1.0]*360 and r['mp_before']==r['mp_after'] and r['stats']==r['stats_after']
    assert len(r['shots'])==1 and r['stack_before']==(0 if label=='sal' else 5) and r['stack_after']==(0 if label=='sal' else 4)
    shot=r['shots'][0]; assert shot['seed']==632 and shot['born_frame']<r['hit_events'][0]['frame'] and shot['final_rng']!=shot['initial_rng']
    assert r['state_rng_before']==r['state_rng_after']
    if label!='sal':
        assert shot['hits']==1 and shot['mult']==2.5 and shot['radius']==(0 if label=='lightning' else 1.5)
        assert shot['base_range']==8 and r['input_edges']==[{'frame':30,'kind':'native_key','key':50,'down':True},{'frame':32,'kind':'native_key','key':50,'down':False}]
    else:
        assert shot['kind']=='enemy' and shot['element']=='sal' and shot['share']==0.6 and r['hp_after']>0
        assert r['input_edges'][0]=={'frame':30,'kind':'fixture_release_native_enemy_ai'} and r['input_edges'][1]['kind']=='fixture_stop_repeat_after_actual_one_shot'
        assert len(r['hit_events'])==7 and len(r['status_ticks'])==6
    states=r['player_status_frames' if label=='sal' else 'enemy_status_frames']
    bit={'fire':4,'cold':2,'lightning':0,'sal':16}[label]
    active=[i for i,s in enumerate(states) if int(s['mask'])&bit]
    if bit: assert active and not(int(states[-1]['mask'])&bit)
    if label=='fire': assert len(r['status_ticks'])==4
    if label in ['cold','lightning']: assert len(r['hit_events'])==1 and not r['status_ticks']
    initial_event=next((v for v in r['status_events'] if v['mask']&bit),None) if bit else None
    summary.append({'label':label,'bounds':bounds[label],'born_frame':shot['born_frame'],'initial_speed':shot['initial_speed'],'first_hit':r['hit_events'][0],'all_damage':[(v['actor'],v['damage']) for v in r['hit_events']],'natural_active_frames':active and [active[0],active[-1]],'initial_state_at_native_event':initial_event and initial_event['state_at_event'],'status_tick_count':len(r['status_ticks']),'seed_before_collision':True})
probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size','-of','json',str(BASE/(a.phase+'.avi'))],text=True)); stream=next(s for s in probe['streams'] if s['codec_name']=='mjpeg'); assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1280,720,'60/1')
files=subprocess.check_output(['git','ls-files','core','actors','items','skills','data/items/talisman_fire.tres','data/items/talisman_ice.tres','data/items/talisman_thunder.tres','data/items/talisman_salpuri.tres','data/enemies/nachalnyeo.tres','data/affixes/affix_db.tres'],cwd=ROOT,text=True).splitlines()
files+=subprocess.check_output(['git','ls-files','--others','--exclude-standard','core','actors','items','skills'],cwd=ROOT,text=True).splitlines()
files=sorted(set(n for n in files if Path(n).suffix in ['.gd','.gdshader','.tres'])); hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files}
meta={'card':672,'phase':a.phase,'checks':int(success[1]),'fps':60,'speed':1.0,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_hashes':hashes,'capture_script_sha256':hashlib.sha256((BASE/'capture_flight.gd').read_bytes()).hexdigest(),'raw_log_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'fixture':fixture,'bounds':bounds,'combat':records,'avi_probe':probe}
if a.phase=='before':
    ref=json.loads((ROOT/'._tmp/634_status_structure_v1/after02_metadata.json').read_text(encoding='utf-8'))
    assert hashes==ref['source_hashes'],'BEFORE source differs from frozen147-source634'
else:
    before=json.loads((BASE/'before_metadata.json').read_text(encoding='utf-8'))
    for field in ['fixture','bounds','fps','speed','capture_script_sha256']: assert before[field]==meta[field],field
    equality=['trigger','end_mechanism','stats','weapon','item','stack_before','stack_after','mp_before','mp_after','hp_before','hp_after','enemy_hp_before','enemy_hp_after','enemy_def','area_level','enemy_damage','enemy_damage_mult','enemy_projectile_base_speed','attack_screen','actor_origin','target_origin','player_rng_before','player_rng_after','enemy_rng_before','enemy_rng_after','state_rng_before','state_rng_after','stats_after','input_edges','actor_frames','camera_frames','target_frames','talisman_cd_frames','time_scale_frames','clock_frames']
    temporal=[]
    for label,r in records.items():
        old=before['combat'][label]
        for field in equality: assert old[field]==r[field],(label,field)
        for field in ['ordinal','kind','seed','initial_rng','final_rng','born_frame','born_engine_frame']:
            assert old['shots'][0][field]==r['shots'][0][field],(label,'shot '+field)
        if label!='sal':
            for field in ['item','element','mult','look_scale','radius','mods','base_range','base_dot_sec','base_status_sec','hits','ended']: assert old['shots'][0][field]==r['shots'][0][field],(label,'shot '+field)
        else:
            for field in ['element','look','dmg_min','dmg_max','share','accuracy']: assert old['shots'][0][field]==r['shots'][0][field],(label,'shot '+field)
        assert [(v['actor'],v['damage']) for v in old['hit_events']]==[(v['actor'],v['damage']) for v in r['hit_events']],(label,'actual damage order/totals')
        assert [{k:v for k,v in e.items() if k!='frame'} for e in old['damage_events']]==[{k:v for k,v in e.items() if k!='frame'} for e in r['damage_events']],(label,'native damage events')
        assert [(v['actor'],v['amount'],v['element']) for v in old['status_ticks']]==[(v['actor'],v['amount'],v['element']) for v in r['status_ticks']],(label,'DOT full tick amounts/order')
        positive_old=[v for v in old['status_events'] if v['mask']]; positive_new=[v for v in r['status_events'] if v['mask']]
        assert len(positive_old)==len(positive_new)
        for x,y in zip(positive_old,positive_new): assert (x['actor'],x['mask'],x['state_at_event'])==(y['actor'],y['mask'],y['state_at_event']),(label,'native status initialization/transition')
        first_old=old['hit_events'][0]['frame']; first_new=r['hit_events'][0]['frame']
        offsets_old=[v['frame']-first_old for v in old['status_ticks']]; offsets_new=[v['frame']-first_new for v in r['status_ticks']]
        assert offsets_old==offsets_new,(label,'native hit-relative DOT tick frames',offsets_old,offsets_new)
        temporal.append({'label':label,'first_hit_before':first_old,'first_hit_after':first_new,'flight_frames_before':first_old-old['shots'][0]['born_frame'],'flight_frames_after':first_new-r['shots'][0]['born_frame'],'initial_speed_before':old['shots'][0]['initial_speed'],'initial_speed_after':r['shots'][0]['initial_speed'],'hit_relative_dot_tick_frames':offsets_new,'intentional_changed_fields':'trajectory/speed, absolute hit time, frame snapshots shifted by native hit; no fullcombat-exact claim'})
    meta['semantic_combat_invariant_equal']=True; meta['timing_comparison']=temporal
(BASE/(a.phase+'_metadata.json')).write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'phase':a.phase,'checks':meta['checks'],'source_files':len(hashes),'capture_sha':meta['capture_script_sha256'],'frames':stream['nb_frames'],'duration':probe['format']['duration'],'semantic_combat_equal':a.phase!='before','segments':summary},ensure_ascii=False),flush=True)