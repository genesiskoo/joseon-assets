import pathlib, urllib.request, urllib.error, json, re, wave, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path('C:/workspace/joseon'); out=root/'tmp/audio559/typecast'; out.mkdir(exist_ok=True)
env=dict(line.split('=',1) for line in (root/'.env').read_text(encoding='utf-8-sig').splitlines() if '=' in line and not line.startswith('#'))
key=env['TYPECAST_API_KEY'].strip().strip('"').strip("'")
voices=json.loads((out.parent/'voices.json').read_text(encoding='utf-8'))
cast={'doho':'Taewoo','merchant':'Sangdo','elder':'Sungbae','shaman':'GeumHee','jumo':'Junghee'}
ids={who:next(v['voice_id'] for v in voices if v['voice_name']==name and v['model']=='ssfm-v30') for who,name in cast.items()}
lines=[]; seen=set(); sources={}
for src in sorted((root/'data/dialogue').rglob('*.dialogue')):
 if 'dev' in src.parts: continue
 text=src.read_text(encoding='utf-8-sig'); sources[str(src.relative_to(root))]=hashlib.sha256(text.encode()).hexdigest()
 for line in text.splitlines():
  m=re.match(r'^\s*(doho|merchant|elder|shaman|jumo):\s*(.*?)\s*\[ID:([^\]]+)\]',line)
  if not m: continue
  who,spoken,ident=m.groups(); spoken=re.sub(r'\[[^\]]*\]','',spoken).strip()
  if ident in seen: continue
  seen.add(ident); lines.append({'id':ident,'speaker':who,'text':spoken,'voice_name':cast[who],'voice_id':ids[who],'source':str(src.relative_to(root))})
(out/'manifest.json').write_text(json.dumps({'card':559,'source_sha256':sources,'cast':cast,'lines':lines},ensure_ascii=False,indent=2),encoding='utf-8')
print('PLAN',len(lines),'clips',sum(len(x['text']) for x in lines),'characters',flush=True)
if '--plan' in sys.argv: sys.exit(0)
results=[]
for item in lines:
 folder=out/item['speaker']; folder.mkdir(exist_ok=True); dst=folder/(item['id']+'.wav')
 if not dst.exists():
  body={'voice_id':item['voice_id'],'text':item['text'],'model':'ssfm-v30','language':'kor','prompt':{'emotion_type':'preset','emotion_preset':'normal','emotion_intensity':1},'output':{'audio_format':'wav','audio_tempo':1}}
  req=urllib.request.Request('https://api.typecast.ai/v1/text-to-speech',data=json.dumps(body,ensure_ascii=False).encode(),headers={'X-API-KEY':key,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=120) as r: audio=r.read()
  except urllib.error.HTTPError as e:
   print('HTTP',e.code,e.read().decode()[:2000],flush=True); sys.exit(1)
  if audio[:4]!=b'RIFF': raise ValueError('Not WAV')
  dst.write_bytes(audio)
 with wave.open(str(dst),'rb') as w: duration=w.getnframes()/w.getframerate(); rate=w.getframerate(); channels=w.getnchannels()
 record=dict(item,file=str(dst),duration=round(duration,3),rate=rate,channels=channels)
 results.append(record); (folder/(item['id']+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 print('TTS_OK',item['id'],cast[item['speaker']],round(duration,2),flush=True)
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('TTS_DONE',len(results),round(sum(x['duration'] for x in results),2),flush=True)
