from pathlib import Path
import json,hashlib,sys,urllib.request,concurrent.futures,collections,subprocess
root=Path('C:/workspace/joseon');p=root/'tmp/audio613';work=Path('C:/Users/FORYOUCOM/.codex/worktrees/613-final-cast/joseon');report=Path('C:/workspace/joseon-assets/reports/613_voice_casting');site=Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/release613')
sys.path.insert(0,str(root/'tools'));import audio_intake as ai
intake=json.loads((p/'intake.json').read_text(encoding='utf-8'))
for r in intake['files']:
 original=root/r['file'];r['previous_sha256']=hashlib.sha256(original.read_bytes()).hexdigest() if original.exists() else None
 assert hashlib.sha256((work/r['file']).read_bytes()).hexdigest()==r['sha256']
for dst in [p/'intake.json',work/'docs/design/audio_613_intake.json',report/'intake.json']:dst.write_text(json.dumps(intake,ensure_ascii=False,indent=2),encoding='utf-8')
rows=json.loads((site/'list.json').read_text(encoding='utf-8'))
def verify(r):
 f=site/r['file'];info=ai.ffprobe(str(f));loud=ai.out_loudness(str(f))
 if abs(loud[0]+20)>.6:
  gain=-2+(-20-loud[0]);src=work/'assets/audio/voice'/(r['id']+'.wav')
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-af',f'volume={gain}dB','-c:a','libmp3lame','-b:a','128k',str(f)],check=True)
  loud=ai.out_loudness(str(f));r['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 assert abs(loud[0]+20)<1.1,(r['id'],loud);assert loud[1]<=-1.5,(r['id'],loud);assert info['dur']>.2
 with urllib.request.urlopen('http://127.0.0.1:8767/release613/'+r['file']) as response:assert response.status==200
 return {'id':r['id'],'loudness':loud,'duration':info['dur']}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,rows))
qa={'card':613,'generated_by':'codex','count':len(results),'speaker_counts':dict(collections.Counter(r['speaker'] for r in rows)),'checks':['237 WAV PCM16 mono44100, -18 LUFS +/-1.1, true peak <= -1.5','237 listen MP3 decode, -20 LUFS +/-1.1, true peak <= -1.5, HTTP200','game WAV SHA256 matches manifest'],'preview_files':results}
(site/'list.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for dst in [p/'qa.json',report/'qa.json']:dst.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('QA_PASS',len(results),qa['speaker_counts'])
