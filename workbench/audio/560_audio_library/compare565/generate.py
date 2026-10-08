import pathlib,json,urllib.request,urllib.error,sys,shutil,subprocess
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path('C:/workspace/joseon'); p=root/'tmp/audio565'; out=p/'compare_context';out.mkdir(exist_ok=True)
env=dict(l.split('=',1) for l in (root/'.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'))
keys={n:env[n].strip().strip('\"').strip("'") for n in ['TYPECAST_API_KEY','ELEVENLABS_API_KEY']}
lines=json.loads((root/'tmp/audio559/typecast/manifest.json').read_text(encoding='utf-8'))['lines']
selected=['NPC_ELDER_CLEAR_DONE_2','NPC_SHAMAN_AFTER_LORE_4','NPC_SHAMAN_OFFER_3','NPC_ELDER_OFFER_1','NPC_MERCHANT_FIRST_3','NPC_JUMO_FIRST_3']
voices={'doho':'Ir7oQcBXWiq4oFGROCfj','elder':'AgA5UKT9OrVg7jxVBZd4','merchant':'AgA5UKT9OrVg7jxVBZd4','shaman':'UvkXHIJzOBYWOI51BDKp','jumo':'xi3rF0t7dg7uN2M0WUhr'}
tags=['[casual]','[sarcastic]','[serious]','[serious]','[chuckles]','[playful]']
records=[]
for ident,tag in zip(selected,tags):
 i=next(j for j,x in enumerate(lines) if x['id']==ident);x=lines[i];prev=lines[i-1]['text'] if i and lines[i-1]['source']==x['source'] else '';nxt=lines[i+1]['text'] if i+1<len(lines) and lines[i+1]['source']==x['source'] else ''
 prefix=ident.rsplit('_',1)[0]; prev=prev if i and lines[i-1]['id'].rsplit('_',1)[0]==prefix else ''; nxt=nxt if i+1<len(lines) and lines[i+1]['id'].rsplit('_',1)[0]==prefix else ''
 row=dict(x,previous_text=prev,next_text=nxt,tag=tag,eleven_voice_id=voices[x['speaker']],variants=[])
 for variant in ['old','smart','v4_plain','v4_tagged']:
  ext='wav' if variant in ['old','smart'] else 'mp3';dst=out/(ident+'_'+variant+'.'+ext)
  body=None
  if variant=='old':shutil.copyfile(root/'tmp/audio559/typecast'/x['speaker']/(ident+'.wav'),dst)
  elif not dst.exists():
   if variant=='smart':
    body={'voice_id':x['voice_id'],'text':x['text'],'model':'ssfm-v30','language':'kor','prompt':{'emotion_type':'smart','previous_text':prev,'next_text':nxt},'output':{'audio_format':'wav','audio_tempo':1,'audio_pitch':0}}
    url='https://api.typecast.ai/v1/text-to-speech';headers={'X-API-KEY':keys['TYPECAST_API_KEY']}
   else:
    body={'text':(tag+' ' if variant=='v4_tagged' else '')+x['text'],'model_id':'eleven_v4','language_code':'ko','voice_settings':{'stability':0.5,'similarity_boost':0.75},'previous_text':prev,'next_text':nxt}
    url='https://api.elevenlabs.io/v1/text-to-speech/'+voices[x['speaker']]+'?output_format=mp3_44100_128';headers={'xi-api-key':keys['ELEVENLABS_API_KEY']}
   headers['Content-Type']='application/json';req=urllib.request.Request(url,data=json.dumps(body,ensure_ascii=False).encode(),headers=headers)
   try:
    with urllib.request.urlopen(req,timeout=120) as r:audio=r.read()
   except urllib.error.HTTPError as e:
    print('HTTP',e.code,e.read().decode(),flush=True);sys.exit(1)
   dst.write_bytes(audio)
  if body:(out/(ident+'_'+variant+'.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
  duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(dst)],text=True).strip())
  row['variants'].append({'name':variant,'file':dst.name,'duration':duration});print('OK',ident,variant,round(duration,2),flush=True)
 records.append(row);(out/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',len(records),'lines',sum(len(x['variants']) for x in records),'clips')

