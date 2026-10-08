from pathlib import Path
import json,hashlib,sys,subprocess,concurrent.futures
root=Path('C:/workspace/joseon');p=root/'tmp/audio613';work=Path('C:/Users/FORYOUCOM/.codex/worktrees/613-final-cast/joseon')
sys.path.insert(0,str(root/'tools'));import audio_intake as ai
manifest=json.loads((p/'voice_manifest.json').read_text(encoding='utf-8'))
for name,sha in manifest['source_sha256'].items():assert hashlib.sha256((work/name).read_bytes()).hexdigest()==sha,name
def convert(r):
 src=p/'voice'/r['speaker']/(r['id']+'.mp3');dst=work/'assets/audio/voice'/(r['id']+'.wav');assert src.exists(),src
 original=root/'assets/audio/voice'/dst.name
 gain=-18-ai.out_loudness(str(src))[0];previous=hashlib.sha256(original.read_bytes()).hexdigest() if original.exists() else None
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-af',f'volume={gain}dB,alimiter=limit=0.749894:level=false:latency=true','-ar','44100','-ac','1','-c:a','pcm_s16le',str(dst)],check=True)
 loud=ai.out_loudness(str(dst));info=ai.ffprobe(str(dst));assert abs(loud[0]+18)<1.1,(r['id'],loud);assert loud[1]<=-1.5,(r['id'],loud);assert info['ch']==1 and info['rate']==44100 and info['codec']=='pcm_s16le'
 print('INTAKE_OK',r['id'],flush=True)
 return {'id':r['id'],'speaker':r['speaker'],'voice_id':r['voice_id'],'file':'assets/audio/voice/'+dst.name,'previous_sha256':previous,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'loudness':loud,'format':info}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(convert,manifest['lines']))
report={'card':613,'generated_by':'codex','files':files,'count':len(files)}
(p/'intake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');(work/'docs/design/audio_613_intake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('INTAKE_QA_PASS',len(files),flush=True)
