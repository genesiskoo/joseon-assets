import pathlib,re,json,sys,urllib.request,urllib.error,hashlib,concurrent.futures,ssl,time
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path('C:/workspace/joseon')
OUT=ROOT/'tmp/audio572'; OUT.mkdir(exist_ok=True)
voices={'doho':'Ir7oQcBXWiq4oFGROCfj','elder':'AgA5UKT9OrVg7jxVBZd4','merchant':'AgA5UKT9OrVg7jxVBZd4','shaman':'UvkXHIJzOBYWOI51BDKp','jumo':'xi3rF0t7dg7uN2M0WUhr'}
rows=[]; hashes={}
for src in sorted((ROOT/'data/dialogue').rglob('*.dialogue')):
 if 'dev' in src.parts: continue
 text=src.read_text(encoding='utf-8-sig'); hashes[str(src.relative_to(ROOT))]=hashlib.sha256(src.read_bytes()).hexdigest()
 stack=[]; title=''; segment=0
 for n,line in enumerate(text.splitlines(),1):
  s=line.strip(); indent=len(line)-len(line.lstrip('\t'))
  if not s or s.startswith('#'): continue
  if s.startswith('~ '):title=s;stack=[];segment+=1;continue
  while stack and stack[-1][0]>=indent:stack.pop()
  if re.match(r'^(if |elif |else\b|match |when |otherwise\b|- )',s):stack.append((indent,s));continue
  if s.startswith('=>'):segment+=1;continue
  m=re.match(r'(doho|elder|merchant|shaman|jumo):\s*(.*?)\s*\[ID:([^\]]+)\]',s)
  if not m:continue
  who,spoken,ident=m.groups();spoken=re.sub(r'\[[^\]]*\]','',spoken).strip()
  rows.append(dict(id=ident,speaker=who,text=spoken,source=str(src.relative_to(ROOT)),line=n,branch=[title]+[x[1] for x in stack],segment=segment))
assert len({r['id'] for r in rows})==len(rows)
for i,r in enumerate(rows):
 signature=lambda x:(x['source'],x['branch'],x['segment'])
 r['previous_text']=rows[i-1]['text'] if i and signature(rows[i-1])==signature(r) else ''
 r['next_text']=rows[i+1]['text'] if i+1<len(rows) and signature(rows[i+1])==signature(r) else ''
 r['voice_id']=voices[r['speaker']]
 r['request']={'text':r['text'],'model_id':'eleven_v4','language_code':'ko','previous_text':r['previous_text'],'next_text':r['next_text'],'voice_settings':{'stability':0.5,'similarity_boost':0.75}}
manifest=dict(card=572,generated_by='codex',model='eleven_v4',source_sha256=hashes,voices=voices,lines=rows)
(OUT/'voice_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('PLAN',len(rows),'lines',sum(len(r['text']) for r in rows),'chars',flush=True)
if '--plan' in sys.argv:sys.exit()
env=dict(l.split('=',1) for l in (ROOT/'.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'))
key=env['ELEVENLABS_API_KEY'].strip().strip('"').strip("'")
def generate(r):
 dst=OUT/'voice'/r['speaker']/(r['id']+'.mp3');dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():
  req=urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/'+r['voice_id']+'?output_format=mp3_44100_128',data=json.dumps(r['request'],ensure_ascii=False).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
  for attempt in range(4):
   try:
    with urllib.request.urlopen(req,timeout=120,context=ssl.create_default_context()) as response:data=response.read()
    break
   except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode()) from e
   except urllib.error.URLError:
    if attempt==3:raise
    time.sleep(1)
  dst.write_bytes(data)
 print('VOICE_OK',r['id'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(generate,rows))
print('VOICE_DONE',len(rows),flush=True)
