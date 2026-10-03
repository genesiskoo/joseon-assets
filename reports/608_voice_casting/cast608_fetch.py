from pathlib import Path
import json,urllib.request,urllib.parse,ssl,time
out=Path('C:/workspace/joseon/tmp/cast608');out.mkdir(exist_ok=True)
env=dict(l.split('=',1) for l in Path('C:/workspace/joseon/.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'))
key=env['ELEVENLABS_API_KEY'].strip().strip('\"').strip("'")
def get(path):
 req=urllib.request.Request('https://api.elevenlabs.io'+path,headers={'xi-api-key':key})
 for attempt in range(4):
  try:
   with urllib.request.urlopen(req,timeout=90,context=ssl.create_default_context()) as r:return json.load(r)
  except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode()) from e
  except urllib.error.URLError:
   if attempt==3:raise
   time.sleep(1)
for name,path in [('models','/v1/models'),('account','/v2/voices?page_size=100'),('korean','/v1/shared-voices?page_size=100&language=ko')]:
 data=get(path);(out/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(name,[(x.get('model_id'),x.get('name')) for x in data] if name=='models' else {'count':len(data.get('voices',[])),'has_more':data.get('has_more')},flush=True)
 if name=='korean':
  pages=[data];n=1
  while data.get('has_more') and n<10:
   data=get('/v1/shared-voices?page_size=100&language=ko&page='+str(n));pages.append(data);n+=1
  voices={v['voice_id']:v for p in pages for v in p.get('voices',[])}
  (out/'korean.json').write_text(json.dumps({'voices':list(voices.values()),'has_more':data.get('has_more'),'pages':n},ensure_ascii=False,indent=2),encoding='utf-8')
  print('KOREAN_TOTAL',len(voices),'remaining',data.get('has_more'))
