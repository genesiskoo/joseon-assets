import pathlib,sys,json,hashlib
root=pathlib.Path('C:/workspace/joseon');work=pathlib.Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon');sys.path.insert(0,str(root/'tools'));import audio_intake as ai
p=root/'tmp/audio572/sfx_intake.json';rows=json.loads(p.read_text(encoding='utf-8'))
for r in rows:
 if r['loudness'][1]<=-1.5:continue
 dst=work/r['target'];tp=-1.5-(r['loudness'][1]+1.5)-.2
 ai.convert(r['source'],str(dst),'sfx',-16,tp,True,False)
 r['loudness']=ai.out_loudness(str(dst));r['sha256']=hashlib.sha256(dst.read_bytes()).hexdigest();r['format']=ai.ffprobe(str(dst))
 print('PEAK_FIXED',dst.name,r['loudness'],flush=True)
assert all(r['loudness'][1]<=-1.5 for r in rows)
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
