import pathlib,json,sys,hashlib,concurrent.futures
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path('C:/workspace/joseon');work=pathlib.Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon');p=root/'tmp/audio572'
sys.path.insert(0,str(root/'tools'));import audio_intake as ai
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def convert(job):
 src,dst,kind,lufs,trim,stereo=job;dst.parent.mkdir(parents=True,exist_ok=True)
 old=sha(dst) if dst.exists() else None
 how=ai.convert(str(src),str(dst),kind,lufs,-1.5,trim,stereo)
 meta=ai.ffprobe(str(dst)); loud=ai.out_loudness(str(dst))
 print('INTAKE_OK',dst.name,how,flush=True)
 return dict(source=str(src),target=str(dst.relative_to(work)),source_sha256=sha(src),previous_sha256=old,sha256=sha(dst),format=meta,loudness=loud)
jobs=[];kind=sys.argv[1]
if kind=='voice':
 m=json.loads((p/'voice_manifest.json').read_text(encoding='utf-8'))
 for r in m['lines']:jobs.append((p/'voice'/r['speaker']/(r['id']+'.mp3'),work/'assets/audio/voice'/(r['id']+'.wav'),'sfx',-18,False,False))
elif kind=='opening':jobs.append((pathlib.Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/new_audio/opening/opening_A1.mp3'),work/'assets/audio/bgm/opening.ogg','bgm',-18,False,True))
elif kind=='sfx':
 m=json.loads((p/'sfx_selection.json').read_text());missing=[]
 for cue,r in m.items():
  candidates=[pathlib.Path(x) for x in r['candidates']]
  for meta in (p/'sfx'/cue).glob('*_v*.json'):
   j=json.loads(meta.read_text(encoding='utf-8'));
   if j.get('clean',{}).get('raw',{}).get('clipped',1)==0:candidates.append(meta.with_suffix('.wav'))
  def rank(src):
   j=json.loads(src.with_suffix('.json').read_text(encoding='utf-8'))
   return (abs(j.get('duration',0)-2.5) if cue=='stone_door_sink' else 0,j.get('clean',{}).get('out',{}).get('sub20_pct',100))
  candidates.sort(key=rank)
  if not candidates:missing.append(cue);continue
  for i,t in enumerate(r['targets']):jobs.append((candidates[i%len(candidates)],work/t,'sfx',-16,True,False))
 if missing:
  print('MISSING_CLEAN',json.dumps(missing));(p/'missing_clean.json').write_text(json.dumps(missing));sys.exit(2)
 for cue,target in [('ambient_village','amb_town'),('ambient_cave','amb_dungeon')]:
  candidates=[]
  for meta in (root/'tmp/audio567/sfx'/cue).glob('*.json'):
   if json.loads(meta.read_text(encoding='utf-8')).get('clean',{}).get('raw',{}).get('clipped',1)==0:candidates.append(meta.with_suffix('.wav'))
  assert candidates,cue
  jobs.append((candidates[0],work/f'assets/audio/amb/{target}.ogg','amb',-24,False,True))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(convert,jobs))
(p/(kind+'_intake.json')).write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('INTAKE_DONE',kind,len(results),flush=True)

