import pathlib,json,hashlib,shutil
p=pathlib.Path('C:/workspace/joseon/tmp/audio572');work=pathlib.Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon');dst=work/'assets/audio/bgm/opening.ogg';sha=hashlib.sha256(dst.read_bytes()).hexdigest()
meta=json.loads((p/'opening_intake.json').read_text(encoding='utf-8'));meta[0]['sha256']=sha
(p/'opening_intake.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
mp=work/'data/audio/production_572.json';j=json.loads(mp.read_text(encoding='utf-8'))
next(x for x in j['files'] if x['target']=='assets/audio/bgm/opening.ogg')['sha256']=sha
mp.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copyfile(dst,'C:/workspace/joseon-assets/workbench/audio/560_audio_library/release572/bgm/opening.ogg')
print('OPENING_AUDIO_ONLY',sha)
