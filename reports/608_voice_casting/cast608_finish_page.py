from pathlib import Path
import json,shutil
p=Path('C:/workspace/joseon/tmp/cast608_page.html');html=p.read_text(encoding='utf-8')
html=html.replace("voice_id:b.dataset.id};save();renderRoles()", "voice_id:choices[b.dataset.pick]?.voice_id===b.dataset.id?null:b.dataset.id};save();renderRoles()")
html=html.replace("voice_id:'none'};save();renderRoles()", "voice_id:choices[b.dataset.reject]?.voice_id==='none'?null:'none'};save();renderRoles()")
html=html.replace("${esc(c.labels.age||'연령 미표기')}","${esc(({young:'청년',middle_aged:'중년',old:'노년'})[c.labels.age]||'연령 미표기')}")
p.write_text(html,encoding='utf-8')
site=Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/cast608');d=json.loads((site/'list.json').read_text(encoding='utf-8'))
public={v['voice_id']:v for v in json.loads(Path('C:/workspace/joseon/tmp/cast608/catalog.json').read_text(encoding='utf-8'))['voices']}
for v in d['voices']:
 if v['voice_id'] in public and public[v['voice_id']].get('preview_url'):v['preview_url']=public[v['voice_id']]['preview_url']
(site/'list.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
(site/'index.html').write_text(html.replace('__PAYLOAD__',json.dumps(d,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
r=Path('C:/workspace/joseon-assets/reports/608_voice_casting')
for name in ['cast608_finish_page.py','cast608_ui_finish.py','cast608_normalize.py','cast608_qa.py','cast608_page.html']:shutil.copy2(Path('C:/workspace/joseon/tmp')/name,r/name)
shutil.copy2(Path('C:/workspace/joseon/tmp/cast608/qa.log'),r/'qa.log')
print('PAGE_FINALIZED')
