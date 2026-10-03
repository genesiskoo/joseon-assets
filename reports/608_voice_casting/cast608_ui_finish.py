from pathlib import Path
p=Path('C:/workspace/joseon/tmp/cast608_page.html');s=p.read_text(encoding='utf-8')
s=s.replace('<h2>${esc(r.name)}</h2>','<h2>${esc(r.name)}</h2><button data-reject="${r.id}">${choices[r.id]?.voice_id===\'none\'?\'✓ 맞는 후보 없음\':\'맞는 후보 없음\'}</button>')
s=s.replace("if(b.dataset.pick){", "if(b.dataset.reject){choices[b.dataset.reject]={...(choices[b.dataset.reject]||{}),voice_id:'none'};save();renderRoles()}if(b.dataset.pick){")
s=s.replace("c?c.name+' ['+c.voice_id+']':'미선택'","c?c.name+' ['+c.voice_id+']':s.voice_id==='none'?'맞는 후보 없음':'미선택'")
s=s.replace("${c?esc(c.name):'미선택'}", "${c?esc(c.name):s.voice_id==='none'?'맞는 후보 없음':'미선택'}")
p.write_text(s,encoding='utf-8')
print('ADDED_REJECT_OPTION')
