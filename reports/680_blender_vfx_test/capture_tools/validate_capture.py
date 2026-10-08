from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
base=Path(__file__).resolve().parent; root=base.parent.parent.parent
phase=sys.argv[1]; rawpath=base/(phase+'.raw.log'); raw=rawpath.read_text(encoding='utf-8-sig',errors='replace')
success=re.search(r'VIDEO680 phase='+phase+r' checks=(\d+) fails=0 PASS',raw); assert success,'Capture did not pass; preserve complete raw before changing fixture.'
errors=[s for s in raw.splitlines() if re.search(r'SCRIPT ERROR|Parse Error|SHADER ERROR|^ERROR:',s) and not re.match(r'ERROR: \d+ resources still in use at exit',s)]; assert not errors,'\n'.join(errors)
fixture=json.loads(re.search(r'^FIXTURE680 (.+)$',raw,re.M)[1]); assert fixture['distance']==5 and fixture['save_context']=='user://video680_capture.json' and fixture['active_profile']==''
records={r['segment']:r for r in map(json.loads,re.findall(r'^COMBAT680 (.+)$',raw,re.M))}; assert list(records)==['fire_weak','fire_strong','sal_weak','sal_strong']
bounds={}
for label,edge,frame in re.findall(r'^CAPTURE (\w+) (BEGIN|END) (\d+)$',raw,re.M): bounds.setdefault(label,{})[edge]=int(frame)
summary=[]
for label,r in records.items():
    is_sal=r['element']=='sal'; strong=r['strong']
    assert bounds[label]['END']-bounds[label]['BEGIN']==r['frames']==360
    for key in ['actor_frames','camera_frames','target_frames','player_status_frames','enemy_status_frames','animation_frames','combat_frames','clock_frames','talisman_cd_frames','time_scale_frames','rng_frames']: assert len(r[key])==360,(label,key)
    assert r['actor_frames']==[r['actor_origin']]*360 and r['target_frames']==[r['target_origin']]*360
    assert r['time_scale_frames']==[1.0]*360 and r['mp_before']==r['mp_after'] and r['stats']==r['stats_after']
    assert len(r['shots'])==1 and r['stack_before']==(0 if is_sal else 5) and r['stack_after']==(0 if is_sal else 4)
    shot=r['shots'][0]; assert shot['seed']==632 and shot['born_frame']<r['hit_events'][0]['frame'] and shot['final_rng']!=shot['initial_rng']
    assert r['state_rng_before']==r['state_rng_after']
    if not is_sal:
        assert shot['hits']==1 and shot['mult']==(2.5 if strong else 1.2) and shot['radius']==1.5
        assert shot['base_range']==8 and r['input_edges']==[{'frame':30,'kind':'native_key','key':50,'down':True},{'frame':32,'kind':'native_key','key':50,'down':False}]
        assert len(r['status_ticks'])==4
    else:
        assert shot['kind']=='enemy' and shot['element']=='sal' and shot['share']==0.6 and r['hp_after']>0
        assert r['input_edges'][0]=={'frame':30,'kind':'fixture_release_native_enemy_ai'} and r['input_edges'][1]['kind']=='fixture_stop_repeat_after_actual_one_shot'
        assert len(r['hit_events'])==(7 if strong else 4) and len(r['status_ticks'])==(6 if strong else 3)
    states=r['player_status_frames' if is_sal else 'enemy_status_frames']; bit=16 if is_sal else 4
    active=[i for i,s in enumerate(states) if int(s['mask'])&bit]
    assert active and not(int(states[-1]['mask'])&bit)
    assert shot['visual']['element_spec']['grade']==(2 if strong else 0),(label,'actual native grade',shot['visual'])
    summary.append({'label':label,'bounds':bounds[label],'born_frame':shot['born_frame'],'initial_speed':shot['initial_speed'],'first_hit':r['hit_events'][0],'all_damage':r['hit_events'],'status_tick_count':len(r['status_ticks']),'native_grade':shot['visual']['element_spec']['grade'],'natural_active_frames':[active[0],active[-1]]})
probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size','-of','json',str(base/(phase+'.avi'))],text=True))
stream=next(s for s in probe['streams'] if s['codec_name']=='mjpeg'); assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1280,720,'60/1')
snapshot=json.loads((base/(phase+'_source_snapshot.json')).read_text(encoding='utf-8'))
assert hashlib.sha256((base/'capture_blender.gd').read_bytes()).hexdigest()==snapshot['capture_script_sha256'],'capture helper mutated after recording'
meta={'card':680,'phase':phase,'checks':int(success[1]),'fps':60,'speed':1.0,'source_head':snapshot['head'],'source_hashes':snapshot['source_hashes'],'capture_script_sha256':snapshot['capture_script_sha256'],'raw_log_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'fixture':fixture,'bounds':bounds,'combat':records,'avi_probe':probe,'summary':summary,'runtime_errors':errors}
if phase=='before':
    verified=0; newline_only=[]
    names=list(snapshot['source_hashes'])
    data=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(snapshot['head']+':'+name for name in names)+'\n').encode(),cwd=root)
    cursor=0
    for name in names:
        end=data.index(b'\n',cursor); header=data[cursor:end].split(); assert len(header)==3,('missing baseline tracked file',name)
        size=int(header[2]); blob=data[end+1:end+1+size]; cursor=end+size+2
        digest=snapshot['source_hashes'][name]
        if hashlib.sha256(blob).hexdigest()!=digest:
            current=(root/name).read_bytes()
            assert current.replace(b'\r\n',b'\n')==blob,('baseline commit mismatch beyond newlines',name)
            newline_only.append({'path':name,'raw_sha256':digest,'git_blob_sha256':hashlib.sha256(blob).hexdigest(),'difference':'CRLF checkout; exact LF-normalized bytes match baseline commit'})
        else: verified+=1
    meta['source_commit_verification']={'commit':snapshot['head'],'files':len(names),'raw_byte_exact_files':verified,'newline_only_files':newline_only,'all_semantic_source_bytes_match':True}
else:
    before=json.loads((base/'before_metadata.json').read_text(encoding='utf-8'))
    for field in ['fixture','bounds','fps','speed','capture_script_sha256']: assert before[field]==meta[field],field
    comparisons=[]
    for label,r in records.items():
        old=json.loads(json.dumps(before['combat'][label])); new=json.loads(json.dumps(r))
        old_visual=old['shots'][0].pop('visual'); new_visual=new['shots'][0].pop('visual')
        if old!=new:
            differences=[]
            def visit(a,b,path):
                if a==b or len(differences)>=30: return
                if isinstance(a,dict) and isinstance(b,dict):
                    for k in a.keys()|b.keys(): visit(a.get(k),b.get(k),path+'.'+str(k))
                elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
                    for i,(x,y) in enumerate(zip(a,b)): visit(x,y,path+'['+str(i)+']')
                else: differences.append({'path':path,'before':a,'after':b})
            visit(old,new,label)
            (base/(phase+'_exact_combat_difference.json')).write_text(json.dumps(differences,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            raise AssertionError(('absolute combat/flight/RNG/status/camera/animation difference',differences))
        assert new_visual['hybrid_spec'],('hybrid effect not actually attached',label)
        comparisons.append({'label':label,'every_absolute_combat_field_exact':True,'before_visual':old_visual,'after_visual':new_visual})
    meta['absolute_combat_invariant_equal']=True; meta['visual_comparisons']=comparisons
(base/(phase+'_metadata.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'phase':phase,'checks':meta['checks'],'source_files':len(meta['source_hashes']),'segments':summary,'absolute_equal':meta.get('absolute_combat_invariant_equal')},ensure_ascii=False))
