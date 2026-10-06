"""#672 actual engine film: four exact 360-frame status takes, native 1x."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
OUT=BASE/'deliverables'
FFMPEG,FFPROBE=shutil.which('ffmpeg'),shutil.which('ffprobe')
FONT='C:/Windows/Fonts/malgun.ttf'
LABELS=['fire','cold','lightning','sal']
ap=argparse.ArgumentParser()
ap.add_argument('--phase',default='after01')
ap.add_argument('--smoke',action='store_true',help='only a provisional normal-camera actual reel in local scratch')
ap.add_argument('--dry-run',action='store_true')
ap.add_argument('--plan-only',action='store_true',help='validate only the immutable BEFORE edit plan; no AFTER proof claim')
args=ap.parse_args()
before=json.loads((BASE/'before_metadata.json').read_text(encoding='utf-8'))
after=before if args.plan_only else json.loads((BASE/(args.phase+'_metadata.json')).read_text(encoding='utf-8'))
for field in ['fixture','bounds','capture_script_sha256','fps','speed']:
    assert before[field]==after[field],'immutable capture/combat differs: '+field
assert before['checks']==after['checks']==47
assert hashlib.sha256((BASE/'capture_flight.gd').read_bytes()).hexdigest()==before['capture_script_sha256']
for name,digest in after['source_hashes'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'capture source changed: '+name
if not args.plan_only:
    assert 'core/vfx_status.gd' in after['source_hashes'] and len(after['source_hashes'])>=148
    assert after['semantic_combat_invariant_equal']
windows=[]
for label in LABELS:
    bounds=before['bounds'][label]
    start,end=bounds['BEGIN'],bounds['END']
    assert end-start==360
    windows.append({'label':label,'start_frame_zero_based':start,'end_frame_exclusive':end,'frames':360,'start_sample':start*800,'end_sample_exclusive':end*800})
if args.dry_run or args.plan_only:
    print(json.dumps({'phase':None if args.plan_only else args.phase,'proof':'BEFORE plan only; AFTER exact proof pending' if args.plan_only else 'launch/setup/RNG-final/damage/MP/belt/radius/native-status exact; flight/hit time intentionally different','frames':1440,'seconds':24,'fps':60,'speed':1.0,'windows':windows,'source_files':len(after['source_hashes'])},ensure_ascii=False))
    raise SystemExit(0)
OUT.mkdir(exist_ok=True)

def run(command,log):
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
    (BASE/log).write_text(result.stdout,encoding='utf-8')
    assert result.returncode==0,f'{log}: exit {result.returncode}\n{result.stdout}'
    return result.stdout

def sound_hashes(phase):
    result=subprocess.run([FFMPEG,'-v','error','-i',str(BASE/(phase+'.avi')),'-map','0:a:0','-f','s16le','-acodec','pcm_s16le','-ac','2','-ar','48000','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode==0,result.stderr.decode('utf-8',errors='replace')
    hashes={}
    for window in windows:
        block=result.stdout[window['start_sample']*4:window['end_sample_exclusive']*4]
        assert len(block)==360*800*4
        hashes[window['label']]=hashlib.sha256(block).hexdigest()
    return hashes
sound_before,sound_after=sound_hashes('before'),sound_hashes(args.phase)
audio={'format':'source PCM s16le stereo 48000Hz; exactly 800 samples per 60fps frame','before_segment_sha256':sound_before,'after_segment_sha256':sound_after,'identical':sound_before==sound_after}
(BASE/(args.phase+'_audio_comparison.json')).write_text(json.dumps(audio,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audio['difference_reason']='Existing core/audio.gd independently randomizes sound variant/pitch RNG, and native impact cue times intentionally follow the changed flight speeds; semantic combat RNG remains exact. Comparison and actual reel share the same AFTER native audio; each full-engine movie retains its original native audio.'

def caption(label,compare):
    height=590 if compare else 720
    picture=Image.new('RGBA',(1280,height))
    draw=ImageDraw.Draw(picture)
    draw.rectangle((0,0,1279,71 if compare else 49),fill=(16,17,18,255))
    draw.rectangle((0,height-38,1279,height-1),fill=(16,17,18,255))
    name={'fire':'불 부적','cold':'한기 부적','lightning':'벽력 부적','sal':'실제 적 살 구슬'}[label]
    old=before['combat'][label]['shots'][0]['initial_speed']; new=after['combat'][label]['shots'][0]['initial_speed']
    draw.text((20,7),f'#672 원소 비행 | {name} · 최초 관측 속도 {old:g} → {new:g} u/s',font=ImageFont.truetype(FONT,23),fill='white')
    if compare:
        draw.text((20,40),'변경 전',font=ImageFont.truetype(FONT,21),fill=(235,215,190))
        draw.text((660,40),'변경 후 · 속성별 움직임 / 탄두 / 후류',font=ImageFont.truetype(FONT,21),fill=(245,232,199))
    draw.text((20,height-31),'고정5u / 실제 첫발 격리 · 피해/RNG/소모 동일 · 속도/명중시각 변경 · 정상1× · A/B AFTER 원음',font=ImageFont.truetype(FONT,18),fill=(205,205,205))
    target=BASE/(label+('_pair' if compare else '_actual')+'_caption.png')
    picture.save(target)
    return target

def reel(compare):
    target=(BASE/(args.phase+'_actual_smoke_60fps.mp4')) if args.smoke else OUT/('672_element_flight_'+('before_after' if compare else 'actual')+'_60fps.mp4')
    inputs=['-i',str(BASE/'before.avi'),'-i',str(BASE/(args.phase+'.avi'))] if compare else ['-i',str(BASE/(args.phase+'.avi'))]
    after_index=1 if compare else 0
    first_caption=2 if compare else 1
    for label in LABELS:
        inputs+=['-loop','1','-framerate','60','-i',str(caption(label,compare))]
    n=len(LABELS)
    graph=[]
    if compare:
        graph.append('[0:v]split='+str(n)+''.join(f'[b{i}]' for i in range(n)))
    graph.append(f'[{after_index}:v]split='+str(n)+''.join(f'[a{i}]' for i in range(n)))
    graph.append(f'[{after_index}:a]asplit='+str(n)+''.join(f'[s{i}]' for i in range(n)))
    for i,window in enumerate(windows):
        start,end=window['start_frame_zero_based'],window['end_frame_exclusive']
        trim=f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS'
        if compare:
            graph.append(f'[b{i}]{trim},crop=720:540:280:80,scale=640:480[l{i}]')
            graph.append(f'[a{i}]{trim},crop=720:540:280:80,scale=640:480[r{i}]')
            graph.append(f'[l{i}][r{i}]hstack=inputs=2,pad=1280:590:0:72:black[base{i}]')
        else:
            graph.append(f'[a{i}]{trim}[base{i}]')
        graph.append(f'[base{i}][{first_caption+i}:v]overlay=shortest=1[v{i}]')
        graph.append(f'[s{i}]atrim=start_sample={window["start_sample"]}:end_sample={window["end_sample_exclusive"]},asetpts=PTS-STARTPTS[sound{i}]')
    graph.append(''.join(f'[v{i}][sound{i}]' for i in range(n))+f'concat=n={n}:v=1:a=1[out][audio]')
    script=BASE/(target.stem+'_filter.txt')
    script.write_text(';\n'.join(graph)+'\n',encoding='utf-8')
    command=[FFMPEG,'-hide_banner','-y','-filter_complex_threads','2']+inputs+['-filter_complex_script',str(script),'-map','[out]','-map','[audio]','-c:v','libx264','-threads','2','-preset','fast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-r','60','-t','24','-movflags','+faststart',str(target)]
    run(command,target.stem+'_encode.raw.log')
    if target.stat().st_size>=10_000_000:
        command[command.index('-crf')+1]='26'
        run(command,target.stem+'_size_retry.raw.log')
    return target

def master(phase):
    target=OUT/f'672_element_flight_{phase}_engine_capture_60fps.mp4'
    source='before' if phase=='before' else args.phase
    if phase=='after' or not target.exists():
        run([FFMPEG,'-hide_banner','-y','-i',str(BASE/(source+'.avi')),'-c:v','libx264','-threads','2','-preset','fast','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(target)],source+'_master_encode.raw.log')
    if target.stat().st_size>=10_000_000:
        run([FFMPEG,'-hide_banner','-y','-i',str(BASE/(source+'.avi')),'-c:v','libx264','-threads','2','-preset','fast','-crf','28','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(target)],source+'_master_size_retry.raw.log')
    return target

def check_video(path,frames,width,height):
    run([FFMPEG,'-v','error','-i',str(path),'-f','null','-'],path.stem+'_decode.raw.log')
    probe=json.loads(run([FFPROBE,'-v','error','-show_entries','stream=codec_name,width,height,pix_fmt,color_range,r_frame_rate,nb_frames:format=duration,size','-of','json',str(path)],path.stem+'_probe.json'))
    video=next(s for s in probe['streams'] if s['codec_name']=='h264')
    assert (video['r_frame_rate'],int(video['nb_frames']),video['width'],video['height'])==('60/1',frames,width,height)
    assert path.stat().st_size<10_000_000,f'{path.name} exceeds10MB'
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'probe':probe,'whole_decode_exit':0}

if args.smoke:
    target=reel(False)
    file=check_video(target,1440,1280,720)
    (BASE/(args.phase+'_smoke_manifest.json')).write_text(json.dumps({'card':672,'phase':args.phase,'provisional':True,'fps':60,'speed':1.0,'windows':windows,'audio':audio,'file':file},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'smoke':str(target),'bytes':file['bytes'],'frames':1440,'original_audio_identical':audio['identical']},ensure_ascii=False))
    raise SystemExit(0)
paths=[(reel(True),1440,1280,590),(reel(False),1440,1280,720),(master('before'),int(before['avi_probe']['streams'][0]['nb_frames']),1280,720),(master('after'),int(after['avi_probe']['streams'][0]['nb_frames']),1280,720)]
files=[check_video(path,frames,width,height) for path,frames,width,height in paths]
manifest={'card':672,'phase_after':args.phase,'fps':60,'speed':1.0,'capture_checks':{'before':before['checks'],'after':after['checks'],'failed':0},'source_before':before['source_head'],'source_hashes_before':before['source_hashes'],'source_hashes_after':after['source_hashes'],'capture_script_sha256':before['capture_script_sha256'],'capture_mode':'Godot MovieMaker actual belt/weapon/enemy projectile/status ticks and expiry; recorded60fps is not realtime performance evidence','comparison_crop_xywh':[280,80,720,540],'actual_crop':'none,1280x720 original camera','frame_mapping':'Engine.get_process_frames counter N corresponds to AVI zero-based N; exact takes use [BEGIN,END)' ,'windows':windows,'fixture':before['fixture'],'audio':audio,'comparison_audio':'one shared native AFTER track, trimmed at exactly800 samples/frame; original per-take sound variants differ','combat_fields_exact':False,'semantic_combat_invariant_equal':True,'intentional_timing_changes':after['timing_comparison'],'before_original_combat_sha256':hashlib.sha256(json.dumps(before['combat'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest(),'after_original_combat_sha256':hashlib.sha256(json.dumps(after['combat'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest(),'combat_records':'before_metadata.json and '+args.phase+'_metadata.json preserve every original field/frame','status_end':'fire/cold/sal all expire naturally inside each six-second clip; lightning adds no native status; full ticks/initial duration and hit-relative ticks verified', 'save_isolation':'video672_capture.json selected BEFORE Main instantiate; never reset_game; active_profile empty; all writes independently scoped', 'raw_avi':'local ignored intermediates, full engine before/after MP4 preserved','files':files}
(OUT/'video_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'videos':[{'file':f['file'],'bytes':f['bytes']} for f in files],'invariant_equal':True,'original_audio_identical':audio['identical']},ensure_ascii=False),flush=True)
