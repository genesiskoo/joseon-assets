import pathlib,json,urllib.request,sys,re
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library');page=base/'release572/index.html'
html=page.read_text(encoding='utf-8').replace("if(s!=='새 생성 #567')","if(s!=='게임 반입 #572')")
html=re.sub(r'<p class="hint">.*?</p>','<p class="hint">효과음: 실제 타격·발소리·기합·UI 교체본입니다.<br>대사: 최신 대본을 같은 대화 분기의 앞뒤 문맥과 함께 ElevenLabs v4로 생성했습니다. 독립 인사·소문은 다른 분기의 대사를 섞지 않았습니다.<br>판소리: 오프닝 A1은 게임에서 한 번 재생하며 오프닝을 닫으면 원래 BGM이 이어집니다.</p>',html,flags=re.S)
page.write_text(html,encoding='utf-8')
rows=json.loads((base/'release572/list.json').read_text(encoding='utf-8'))
assert len(rows)==267
assert all((base/'release572'/x['path']).is_file() for x in rows)
with urllib.request.urlopen('http://127.0.0.1:8767/release572/') as r:assert r.status==200
for kind in ['대사','효과음','BGM','환경음']:
 x=next(x for x in rows if x['category']==kind)
 with urllib.request.urlopen('http://127.0.0.1:8767/release572/'+x['path']) as r:assert r.status==200;assert len(r.read())>100
 print('HTTP_OK',kind,x['path'])
print('PACKAGE_QA 267 files PASS')
