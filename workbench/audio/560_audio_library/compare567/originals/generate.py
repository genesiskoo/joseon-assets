import pathlib,json,urllib.request,urllib.error,sys
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path('C:/workspace/joseon');out=root/'tmp/audio567';out.mkdir(exist_ok=True)
env=dict(l.split('=',1) for l in (root/'.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'));key=env['ELEVENLABS_API_KEY'].strip().strip('"').strip("'")
def call(route,body,dst):
 if dst.exists():return {}
 req=urllib.request.Request('https://api.elevenlabs.io/v1/'+route,data=json.dumps(body,ensure_ascii=False).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=480) as r:
   data=r.read();h={k:v for k,v in r.headers.items() if k.lower() in ['song-id','character-cost','request-id','content-type']}
 except urllib.error.HTTPError as e:print('HTTP',e.code,e.read().decode(),flush=True);raise
 dst.write_bytes(data);return h
records=[]
if sys.argv[1]=='music':
 src=json.loads((root/'tmp/audio566/suno.json').read_text(encoding='utf-8'))
 for b in src['batches'][::3]:
  for n in range(1,3):
   ident=b['title'].split()[1];dst=out/f'music_{ident}_{n}.mp3';body={'prompt':b['prompt']+' No vocals, choir, pop beat, heroic brass or triumphant finale.','music_length_ms':60000,'model_id':'music_v2_5','force_instrumental':True}
   h=call('music?output_format=mp3_44100_128',body,dst);records.append({'category':'BGM','title':b['title'].replace('JH566 ','').replace(' W45','')+' · Eleven '+str(n),'file':dst.name,'request':body,'headers':h});(out/'music.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print('MUSIC',dst.name,flush=True)
else:
 src=json.loads((root/'tmp/audio565/compare_context/manifest.json').read_text(encoding='utf-8'))
 for x in src[1:]:
  for stability in [.5,.35]:
   dst=out/(x['id']+'_'+str(stability)+'.mp3');body={'text':x['tag']+' '+x['text'],'model_id':'eleven_v4','language_code':'ko','voice_settings':{'stability':stability,'similarity_boost':.75},'previous_text':x['previous_text'],'next_text':x['next_text']}
   h=call('text-to-speech/'+x['eleven_voice_id']+'?output_format=mp3_44100_128',body,dst);records.append({'category':'대사','title':x['speaker']+' · 안정도 '+str(stability),'text':x['text'],'file':dst.name,'request':body,'headers':h});(out/'voices.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print('VOICE',dst.name,flush=True)
