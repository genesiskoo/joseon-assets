from pathlib import Path
import json,urllib.request,urllib.error,ssl,time,base64,concurrent.futures,sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path('C:/workspace/joseon/tmp/cast608/round2');root.mkdir(exist_ok=True)
old=json.loads(Path('C:/workspace/joseon/tmp/cast608/plan.json').read_text(encoding='utf-8'))
env=dict(l.split('=',1) for l in Path('C:/workspace/joseon/.env').read_text(encoding='utf-8-sig').splitlines() if '=' in l and not l.startswith('#'))
key=env['ELEVENLABS_API_KEY'].strip().strip('\"').strip("'")
def api(path,body=None):
 req=urllib.request.Request('https://api.elevenlabs.io'+path,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
 for attempt in range(4):
  try:
   with urllib.request.urlopen(req,timeout=180,context=ssl.create_default_context()) as r:return r.read()
  except urllib.error.HTTPError as e:
   msg=e.read().decode();(root/'last_error.log').write_text(msg,encoding='utf-8')
   if e.code in [409,429,500,502,503] and attempt<3:time.sleep(2+attempt*2);continue
   raise RuntimeError(msg)
def store(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
prompts={
 'merchant':('김 영감 · 구수한 노장','An unmistakably elderly Korean man in his late seventies, a weathered village shopkeeper in a Korean historical fantasy drama. Native Korean pronunciation. A grainy, cracked, pleasantly raspy old throat, rounded chest resonance, audible age in every vowel. Lively knowing smile and sly warm humour, grounded earthy speech, confident bargaining. Expressive speech with short chuckles in the voice, not a smooth middle-aged announcer. Clearly old but spirited and sturdy, never feeble. Clean dry studio recording, natural acted dialogue.'),
 'elder':('촌장 · 늙은 어른의 무게','An unmistakably elderly Korean man around eighty, a stern village elder in a Korean historical fantasy drama. Native Korean pronunciation. Deep worn bass-baritone with coarse cracked edges and dry gravel, years of hardship audible in the throat. A thick grounded chest voice, deliberate compact speech, weighty authority and contained grief. He has lost villagers but remains firm and responsible. Clearly aged and powerful, not a youthful smooth narrator or a fragile whisper. Natural dialogue, clean dry close studio sound.'),
 'shaman':('무당 할매 · 거친 노파','An unmistakably elderly Korean woman around eighty, a village wise woman in a Korean historical fantasy drama. Native Korean pronunciation. A low dry croaky and grainy old female voice, rough worn throat and cracked vowels, strong age texture, clear words. Stern earthy presence, a penetrating grounded warning, controlled urgency and seasoned authority. Not sweet, young, soft counselling or cute cartoon grandmother. Firm breath support and strength, never a weak inaudible whisper. Natural acted dialogue in a clean dry studio recording.'),
 'jumo':('주모 · 농밀한 구미호','A mature adult Korean woman in her late thirties to forties, secretly an alluring fox spirit disguised as a tavern hostess in a Korean dark fantasy drama. Native Korean pronunciation. Low rich velvety contralto, smoky husky throat with silky breath at the edges, intimate warm full resonance. Magnetically seductive and languid, confident knowing smile, measured lingering vowels and gently caressing phrase endings. She draws a listener closer with a spellbinding voice and concealed danger. Conversational charm, never a bright girlish guide or flat narrator. Intelligible natural speech, not breathless panting. Clean dry close studio recording.'),
 'dokkaebi':('도깨비 · 호방한 거한','A gigantic burly Korean male warrior and honest trader in a Korean historical fantasy drama, middle-aged, native Korean pronunciation. Very deep booming bass, massive chest resonance and a thick coarse sandpaper gravel in the throat. A barrel-chested rough battle veteran, bold hearty commanding delivery and explosive consonants, a broad confident grin and earthy swagger. Enormous physical presence even when speaking conversationally, an occasional hearty rumble of laughter. Robust and vigorous, not frail, not a smooth narrator, not a digitally distorted monster. Clear intelligible words in natural acted Korean dialogue, clean dry studio sound.')}
roles=[];jobs=[]
if '--status' in sys.argv:
 s=json.loads(api('/v1/user/subscription'));print({k:s.get(k) for k in ['voice_limit','character_count','character_limit','can_extend_voice_limit']});sys.exit()
for rid,(name,desc) in prompts.items():
 role=next(r for r in old['roles'] if r['id']==rid).copy();role['target']=name+' — '+desc;role['candidates']=[]
 # The preview paragraph reinforces the character while keeping the first two comparison lines identical.
 extra={'merchant':'허허, 이 장터서 장사한 게 벌써 오십 년이우. 좋은 물건 보는 눈은 아직 멀쩡하니, 걱정 붙들어 매슈. 서두르지 마시고 천천히 골라 보시오.', 'elder':'이 마을을 지킨 지 오래요. 남은 사람들은 내가 돌봐야 하지. 도사 양반, 이번 일은 가볍게 넘길 수 없소. 서둘러 주시오. 부탁하겠소.', 'shaman':'내 눈에는 다 보이오. 오래 묵은 기운이 다시 깨어나고 있소. 내 말을 허투루 듣지 마시오. 더 늦기 전에 막아야 하오. 도사 양반, 정신 바짝 차리시오.', 'jumo':'서둘러 가실 건 없잖소. 이리 가까이 앉아 보시구려. 밤도 깊었는데, 따뜻한 것 한 그릇 들고 가시오. 내 이야기는 천천히 들으시면 되지. 그렇게 경계하지 마시구려.', 'dokkaebi':'하하, 걱정 붙들어 매! 내 덩치만 보고 겁먹었나? 한번 맡았으면 끝까지 책임지는 놈이야. 이 큰 손이 괜히 큰 줄 아나. 자, 물건 한번 내놔 봐.'}[rid]
 text=' '.join(role['lines'])+' '+extra
 while len(text)<100:text+=' '+extra
 designfile=root/(rid+'_design.json')
 if designfile.exists():design=json.loads(designfile.read_text(encoding='utf-8'))
 else:
  body={'model_id':'eleven_ttv_v3','voice_description':desc,'text':text,'guidance_scale':5,'loudness':0,'seed':608104+len(roles)}
  design=json.loads(api('/v1/text-to-voice/design?output_format=mp3_44100_128',body))
  for i,v in enumerate(design['previews'],1):
   (root/f'{rid}_design_{i}.mp3').write_bytes(base64.b64decode(v.pop('audio_base_64')))
  design['request']=body;store(designfile,design);print('DESIGNED',rid,len(design['previews']),flush=True)
 for i,v in enumerate(design['previews'],1):
  vf=root/f'{rid}_{i}_voice.json'
  if vf.exists():voice=json.loads(vf.read_text(encoding='utf-8'))
  else:
   voice=json.loads(api('/v1/text-to-voice',{'voice_name':f'JH608R2 {rid} {i}','voice_description':desc,'generated_voice_id':v['generated_voice_id'],'labels':{'language':'ko','gender':'female' if rid in ['jumo','shaman'] else 'male','age':'old' if rid in ['merchant','elder','shaman'] else 'middle_aged'}}));store(vf,{'voice_id':voice['voice_id'],'name':voice['name']})
  candidate={'voice_id':voice['voice_id'],'name':name+f' {chr(64+i)}','rank':i,'why':name,'risk':'노년의 질감·농밀함·거한의 발성이 실제 대사에서도 유지되는지 확인.','labels':{'age':'old' if rid in ['merchant','elder','shaman'] else 'middle_aged'},'description':desc,'preview_file':f'round2/audio/{rid}_design_{i}.mp3'}
  role['candidates'].append(candidate)
  for line,t in enumerate(role['lines']):
   jobs.append({'role':rid,'rank':i,'voice_id':voice['voice_id'],'name':candidate['name'],'line':line,'file':f'round2/audio/{rid}_{i}_{line+1}.mp3','request':{'text':t,'model_id':'eleven_v4','language_code':'ko','previous_text':role['previous'][line],'next_text':role['next'][line],'voice_settings':{'stability':0.5,'similarity_boost':0.75}}})
 roles.append(role)
plan={'generated_by':'codex','card':608,'round':2,'design_model':'eleven_ttv_v3','tts_model':'eleven_v4','roles':roles,'jobs':jobs};store(root/'plan.json',plan)
def tts(j):
 dst=root/Path(j['file']).name
 if not dst.exists():
  dst.write_bytes(api('/v1/text-to-speech/'+j['voice_id']+'?output_format=mp3_44100_128',j['request']));store(dst.with_suffix('.json'),j)
 print('V4_OK',dst.name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(tts,jobs))
print('ROUND2_DONE',len(roles),len(jobs),flush=True)
