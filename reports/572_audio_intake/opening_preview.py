import pathlib,json,shutil
root=pathlib.Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library');shutil.copyfile('C:/workspace/joseon/tmp/audio572/opening_decode.wav',root/'release572/bgm/opening_preview.wav')
for folder in ['release572','compare567']:
 p=root/folder/'list.json';rows=json.loads(p.read_text(encoding='utf-8'))
 for r in rows:
  if r.get('origin')=='게임 반입 #572' and r.get('group')=='opening':r['path']=r['path'].replace('opening.ogg','opening_preview.wav')
 p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 h=root/folder/'index.html';s=h.read_text(encoding='utf-8').replace('release572/bgm/opening.ogg','release572/bgm/opening_preview.wav')
 if folder=='release572':s=s.replace('bgm/opening.ogg','bgm/opening_preview.wav')
 h.write_text(s,encoding='utf-8')
