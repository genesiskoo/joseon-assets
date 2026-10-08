"""#680 native Godot frames and native PCM; captions only, no added effects."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
base=Path(__file__).resolve().parent; out=base/'deliverables'; out.mkdir(exist_ok=True)
ffmpeg,ffprobe=shutil.which('ffmpeg'),shutil.which('ffprobe'); font='C:/Windows/Fonts/malgun.ttf'
labels=['fire_weak','fire_strong','sal_weak','sal_strong']
ap=argparse.ArgumentParser(); ap.add_argument('--phase',default='after01'); ap.add_argument('--before-only',action='store_true'); ap.add_argument('--reels-only',action='store_true'); args=ap.parse_args()
previous=json.loads((out/'video_manifest.json').read_text(encoding='utf-8')) if args.reels_only else None
if previous: assert previous['phase_after']==args.phase
before=json.loads((base/'before_metadata.json').read_text(encoding='utf-8'))
after=None if args.before_only else json.loads((base/(args.phase+'_metadata.json')).read_text(encoding='utf-8'))
windows=[{'label':label,'start_frame_zero_based':before['bounds'][label]['BEGIN'],'end_frame_exclusive':before['bounds'][label]['END'],'frames':360,'start_sample':before['bounds'][label]['BEGIN']*800,'end_sample_exclusive':before['bounds'][label]['END']*800} for label in labels]
def run(command,log):
    r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    (base/log).write_bytes(r.stdout); assert r.returncode==0,(log,r.stdout.decode(errors='replace'))
    return r.stdout.decode('utf-8',errors='replace')
def check(path,frames,width,height):
    run([ffmpeg,'-v','error','-i',str(path),'-f','null','-'],path.stem+'_decode.raw.log')
    probe=json.loads(run([ffprobe,'-v','error','-show_entries','stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames:format=duration,size','-of','json',str(path)],path.stem+'_probe.json'))
    v=next(s for s in probe['streams'] if s['codec_name']=='h264')
    assert (v['r_frame_rate'],int(v['nb_frames']),v['width'],v['height'])==('60/1',frames,width,height)
    assert path.stat().st_size<10_000_000
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'probe':probe,'whole_decode_exit':0}
def master(phase,meta):
    source='before' if phase=='before' else args.phase; path=out/f'680_blender_vfx_{phase}_engine_capture_60fps.mp4'
    if args.reels_only:
        row=next(f for f in previous['files'] if f['file']==path.name); assert path.stat().st_size==row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        return row
    if phase!='before' or not path.exists():
        run([ffmpeg,'-hide_banner','-y','-i',str(base/(source+'.avi')),'-c:v','libx264','-threads','2','-preset','fast','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(path)],source+'_master_encode.raw.log')
    frames=int(next(s for s in meta['avi_probe']['streams'] if s['codec_name']=='mjpeg')['nb_frames'])
    return check(path,frames,1280,720)
before_master=master('before',before)
if args.before_only:
    (out/'before_master_manifest.json').write_text(json.dumps(before_master,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(before_master,ensure_ascii=False)); raise SystemExit()
assert after['absolute_combat_invariant_equal'] and before['bounds']==after['bounds'] and before['capture_script_sha256']==after['capture_script_sha256']
def sound(phase):
    r=subprocess.run([ffmpeg,'-v','error','-i',str(base/(phase+'.avi')),'-map','0:a:0','-f','s16le','-acodec','pcm_s16le','-ac','2','-ar','48000','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW); assert r.returncode==0
    result={}
    for w in windows:
        block=r.stdout[w['start_sample']*4:w['end_sample_exclusive']*4]; assert len(block)==360*800*4
        result[w['label']]=hashlib.sha256(block).hexdigest()
    return result
audio={'format':'native s16le stereo48000Hz, exactly800samples/frame','before_segment_sha256':sound('before'),'after_segment_sha256':sound(args.phase),'comparison':'AFTER AUDIO labelled; no retiming; each full engine movie retains own native sound','variation_reason':'Existing core/audio.gd independently randomizes variant and pitch; native combat RNG/impact frame remains exact.'}
def caption(label,compare):
    height=590 if compare else 720; image=Image.new('RGBA',(1280,height)); d=ImageDraw.Draw(image)
    d.rectangle((0,0,1279,71 if compare else 47),fill=(13,15,18,255)); d.rectangle((0,height-37,1279,height-1),fill=(13,15,18,255))
    element='화염부' if label.startswith('fire') else '나찰녀 살 구슬'
    level=('정기150' if label.endswith('strong') else '정기20') if label.startswith('fire') else ('지역Lv16' if label.endswith('strong') else '지역Lv1')
    grade=('강 · grade2' if label.endswith('strong') else '약 · grade0')+' · '+level
    d.text((18,7),f'#680 Blender + Godot | {element} · {grade}',font=ImageFont.truetype(font,23),fill='white')
    if compare:
        d.text((18,40),'변경 전 · 코드 메시 / 붓결 · 2× 확대',font=ImageFont.truetype(font,20),fill=(218,201,178))
        particles='GPU 불티' if label.startswith('fire') else 'GPU 살 방울'
        d.text((660,40),'변경 후 · 볼륨 시트 / '+particles+' · AFTER AUDIO',font=ImageFont.truetype(font,18),fill=(246,225,188))
    footer='동일 실제 프레임 2× 확대 / 입력·명중·피해·DOT·RNG 동일 · 정상 1× · A/B AFTER 원음' if compare else '실제 게임 카메라 / 원음 · 정상 1× · MovieMaker 60fps · 실시간 성능 측정 아님'
    d.text((18,height-30),footer,font=ImageFont.truetype(font,18),fill=(205,205,205))
    path=base/(label+('_pair' if compare else '_actual')+'_caption.png'); image.save(path); return path
def reel(compare):
    path=out/('680_blender_vfx_'+('before_after' if compare else 'actual')+'_60fps.mp4')
    inputs=['-i',str(base/'before.avi'),'-i',str(base/(args.phase+'.avi'))] if compare else ['-i',str(base/(args.phase+'.avi'))]
    ai=1 if compare else 0; first=2 if compare else 1
    for label in labels: inputs+=['-loop','1','-framerate','60','-i',str(caption(label,compare))]
    graph=[]
    if compare: graph.append('[0:v]split=4'+''.join(f'[b{i}]' for i in range(4)))
    graph.append(f'[{ai}:v]split=4'+''.join(f'[a{i}]' for i in range(4))); graph.append(f'[{ai}:a]asplit=4'+''.join(f'[s{i}]' for i in range(4)))
    for i,w in enumerate(windows):
        trim=f'trim=start_frame={w["start_frame_zero_based"]}:end_frame={w["end_frame_exclusive"]},setpts=PTS-STARTPTS'
        if compare:
            graph.append(f'[b{i}]{trim},crop=320:240:510:210,scale=640:480[l{i}]'); graph.append(f'[a{i}]{trim},crop=320:240:510:210,scale=640:480[r{i}]'); graph.append(f'[l{i}][r{i}]hstack=inputs=2,pad=1280:590:0:72:black[base{i}]')
        else: graph.append(f'[a{i}]{trim}[base{i}]')
        graph.append(f'[base{i}][{first+i}:v]overlay=shortest=1[v{i}]'); graph.append(f'[s{i}]atrim=start_sample={w["start_sample"]}:end_sample={w["end_sample_exclusive"]},asetpts=PTS-STARTPTS[sound{i}]')
    graph.append(''.join(f'[v{i}][sound{i}]' for i in range(4))+'concat=n=4:v=1:a=1[out][audio]')
    script=base/(path.stem+'_filter.txt'); script.write_text(';\n'.join(graph)+'\n',encoding='utf-8')
    run([ffmpeg,'-hide_banner','-y','-filter_complex_threads','2']+inputs+['-filter_complex_script',str(script),'-map','[out]','-map','[audio]','-c:v','libx264','-threads','2','-preset','fast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-r','60','-t','24','-movflags','+faststart',str(path)],path.stem+'_encode.raw.log')
    return check(path,1440,1280,590 if compare else 720)
files=[reel(True),reel(False),before_master,master('after',after)]
manifest={'card':680,'phase_after':args.phase,'fps':60,'speed':1.0,'before_checks':before['checks'],'after_checks':after['checks'],'every_absolute_combat_field_exact':True,'fixture':before['fixture'],'windows':windows,'capture_script_sha256':before['capture_script_sha256'],'source_hashes_before':before['source_hashes'],'source_hashes_after':after['source_hashes'],'baseline_commit':before['source_head'],'baseline_commit_verification':before['source_commit_verification'],'source_after_commit':'pending root final commit','audio':audio,'capture_mode':'Actual Godot MovieMaker, natural belt throw/enemy orb/DOT, not realtime performance evidence','frame_mapping':'Engine process counter N = AVI zero-based frame N, exact [BEGIN,END),800audio samples/frame','comparison_crop_xywh':[510,210,320,240],'comparison_magnification':2.0,'actual_crop':'none; original1280x720','files':files,'visual_comparisons':after['visual_comparisons']}
(out/'video_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'videos':[{'file':f['file'],'bytes':f['bytes']} for f in files],'absolute_combat_exact':True},ensure_ascii=False))
