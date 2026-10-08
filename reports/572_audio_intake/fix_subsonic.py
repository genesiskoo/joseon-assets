import pathlib,json,shutil,hashlib
p=pathlib.Path('C:/workspace/joseon/tmp/audio572');work=pathlib.Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon');lib=pathlib.Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/release572')
mp=p/'sfx_intake.json';rows=json.loads(mp.read_text(encoding='utf-8'));by_target={x['target'].replace('\\','/'):x for x in rows}
for target,source in [('combat/hit_3.wav','combat/hit_1.wav'),('combat/step_stone_2.wav','combat/step_stone_1.wav'),('combat/step_stone_4.wav','combat/step_stone_1.wav'),('world/drop_2.wav','world/drop_1.wav')]:
 dst=work/'assets/audio/sfx'/target;src=work/'assets/audio/sfx'/source;r=by_target['assets/audio/sfx/'+target];template=by_target['assets/audio/sfx/'+source]
 shutil.copyfile(src,dst)
 for key in ['source','source_sha256','sha256','format','loudness']:r[key]=template[key]
 shutil.copyfile(dst,lib/'sfx'/target)
 print('SUBSONIC_REPLACED',target)
mp.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=work/'docs/design/audio_572_manifest.json';j=json.loads(manifest.read_text(encoding='utf-8'))
for record in j['files']:
 if record['target'] in by_target:
  r=by_target[record['target']]
  record.update(source=pathlib.Path(r['source']).as_posix(),source_sha256=r['source_sha256'],sha256=r['sha256'],duration=r['format']['dur'],loudness=r['loudness'])
manifest.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
for folder in [lib,lib.parent/'compare567']:
 js=folder/'list.json';data=json.loads(js.read_text(encoding='utf-8'))
 for r in data:
  if r.get('origin')!='게임 반입 #572' or r.get('category')!='효과음':continue
  path=r['path'].replace('../release572/','')
  key='assets/audio/'+path
  if key in by_target:r['duration']=by_target[key]['format']['dur']
 js.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 # Rewrite only the embedded list, retaining all existing page wording.
 import re
 page=folder/'index.html';s=page.read_text(encoding='utf-8')
 s=re.sub(r'const data=\[.*?\];const \$',lambda m:'const data='+json.dumps(data,ensure_ascii=False)+';const $',s,flags=re.S)
 page.write_text(s,encoding='utf-8')
