import pathlib,json,sys,re
root=pathlib.Path('C:/workspace/joseon');sys.path.insert(0,str(root/'tmp/audio568_sdk'));sys.stdout.reconfigure(encoding='utf-8')
from typecast import Typecast
from typecast.models import TTSRequest,SmartPrompt,Output
# Persistent onboarding attribution requested by PD (API page, not docs default).
ATTRIBUTION={'source':'api-page','generated_by':'codex'}
env=dict(l.split('=',1) for l in (root/'.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'));key=env['TYPECAST_API_KEY'].strip().strip('"').strip("'")
client=Typecast(api_key=key,**ATTRIBUTION)
rows=json.loads((root/'tmp/audio565/compare_context/manifest.json').read_text(encoding='utf-8'));out=root/'tmp/audio568';out.mkdir(exist_ok=True);records=[]
for row in rows:
 for variant in ['smart','pause']:
  text=row['text']
  if variant=='pause':text=re.sub(r'([.!?])\s+',r'\1 <|0.25s|> ',text,count=1)
  req=TTSRequest(text=text,model='ssfm-v30',voice_id=row['voice_id'],language='kor',prompt=SmartPrompt(emotion_type='smart',previous_text=row['previous_text'],next_text=row['next_text']),output=Output(audio_format='wav',audio_pitch=0,audio_tempo=1))
  dst=out/(row['id']+'_'+variant+'.wav')
  if not dst.exists():dst.write_bytes(client.text_to_speech(req).audio_data)
  records.append({'id':row['id'],'speaker':row['speaker'],'text':row['text'],'variant':variant,'file':dst.name,'request':req.model_dump(mode='json',exclude_none=True),'attribution':ATTRIBUTION})
  (out/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print('OK',row['id'],variant,flush=True)
