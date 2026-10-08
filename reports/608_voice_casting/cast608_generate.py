from pathlib import Path
import json,urllib.request,urllib.error,ssl,time,concurrent.futures,sys
sys.stdout.reconfigure(encoding='utf-8')
p=Path('C:/workspace/joseon/tmp/cast608');plan=json.loads((p/'plan.json').read_text(encoding='utf-8'))
env=dict(l.split('=',1) for l in Path('C:/workspace/joseon/.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'))
key=env['ELEVENLABS_API_KEY'].strip().strip('\"').strip("'")
def gen(j):
 dst=p/'raw'/j['file'];dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():return
 req=urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/'+j['voice_id']+'?output_format=mp3_44100_128',data=json.dumps(j['request'],ensure_ascii=False).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
 for attempt in range(4):
  try:
   with urllib.request.urlopen(req,timeout=120,context=ssl.create_default_context()) as r:data=r.read();headers={k:r.headers.get(k) for k in ['request-id','history-item-id','character-cost']}
   break
  except urllib.error.HTTPError as e:
   if e.code in [409,429,500,502,503] and attempt<3:time.sleep(2+attempt*2);continue
   message=e.read().decode();(p/(j['role']+'_error.log')).write_text(message,encoding='utf-8');raise RuntimeError(message)
  except urllib.error.URLError:
   if attempt==3:raise
   time.sleep(1)
 dst.write_bytes(data);dst.with_suffix('.json').write_text(json.dumps({'request':j,'response':headers},ensure_ascii=False,indent=2),encoding='utf-8')
 print('AUDITION_OK',j['file'],flush=True)
jobs=plan['jobs'][:1] if '--probe' in sys.argv else plan['jobs']
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(gen,jobs))
print('DONE',len(jobs),flush=True)
