import pathlib,json,urllib.request,urllib.error,sys
sys.stdout.reconfigure(encoding='utf-8');root=pathlib.Path('C:/workspace/joseon');p=root/'tmp/audio566';out=p/'voices';out.mkdir(exist_ok=True)
env=dict(l.split('=',1) for l in (root/'.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'));key=env['ELEVENLABS_API_KEY'].strip().strip('\"').strip("'")
allv=json.loads((root/'tmp/audio565/voices.json').read_text(encoding='utf-8'))['voices'];names={v['voice_id']:v['name'] for v in allv}
groups=[('doho','[sarcastic] 남의 자물쇠로 제 집 문을 잠갔구먼. 뻔뻔하기는.',['Ir7oQcBXWiq4oFGROCfj','YcKXQhCnoNmbyAdL8Shk','6Ezg9LQ453osVlR62RFI']),('elder','[serious] 부탁이 하나 있소. 흑랑 굴 말이오.',['AgA5UKT9OrVg7jxVBZd4','ibCGc01503OQd2R6i1n1','KFTSy1J20kTAnUHnQjVx']),('jumo','[playful] 외상은 살아서 돌아오는 사람한테만 놓수.',['xi3rF0t7dg7uN2M0WUhr','UvkXHIJzOBYWOI51BDKp','zgDzx5jLLCqEp6Fl7Kl7'])]
r=[]
for role,text,ids in groups:
 for n,vid in enumerate(ids,1):
  dst=out/(role+'_'+str(n)+'.mp3');body={'text':text,'model_id':'eleven_v4','language_code':'ko','voice_settings':{'stability':.5,'similarity_boost':.75}}
  if not dst.exists():
   req=urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/'+vid+'?output_format=mp3_44100_128',data=json.dumps(body,ensure_ascii=False).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
   try:
    with urllib.request.urlopen(req,timeout=120) as q:dst.write_bytes(q.read())
   except urllib.error.HTTPError as e:print('HTTP',e.code,e.read().decode());raise
  r.append({'role':role,'voice_id':vid,'name':names[vid],'file':dst.name,'request':body});(out/'manifest.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print('VOICE',role,n,names[vid],flush=True)
