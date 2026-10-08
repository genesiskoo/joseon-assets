import pathlib,json,sys,shutil,html,importlib.util
sys.stdout.reconfigure(encoding='utf-8');root=pathlib.Path('C:/workspace/joseon');p=root/'tmp/audio565';out=pathlib.Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/compare565');out.mkdir(exist_ok=True)
shutil.copytree(p/'compare_context',out/'originals',dirs_exist_ok=True);shutil.copytree(p/'compare',out/'experiment1',dirs_exist_ok=True)
spec=importlib.util.spec_from_file_location('intake',root/'tools/audio_intake.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=json.loads((p/'compare_context/manifest.json').read_text(encoding='utf-8'));qa=[];labels={'old':'A · 기존 Typecast normal','smart':'B · Typecast Smart + 문맥','v4_plain':'C · Eleven v4 기본 + 문맥','v4_tagged':'D · Eleven v4 연기 태그 + 문맥'}
voices=json.loads((p/'voices.json').read_text(encoding='utf-8'))['voices'];names={x['voice_id']:x['name'] for x in voices}
content=[]
for row in rows:
 cells=[]
 for v in row['variants']:
  dst=out/(pathlib.Path(v['file']).stem+'.wav');method=m.convert(str(p/'compare_context'/v['file']),str(dst),'sfx',-18,-1.5,False,False);li,tp=m.out_loudness(str(dst));assert tp<=-1.3
  qa.append({'file':dst.name,'lufs':li,'true_peak':tp,'method':method});v['preview']=dst.name
  cells.append('<td><button onclick="play(\''+dst.name+'\',this)">'+labels[v['name']]+'</button><small>'+str(round(v['duration'],2))+'초</small></td>')
 content.append('<article><h2>'+html.escape(row['text'])+'</h2><p>'+row['speaker']+' · '+row['id']+'<br>Typecast '+row['voice_name']+' / Eleven '+html.escape(names[row['eleven_voice_id']])+' · 태그 '+row['tag']+'</p><table><tr>'+''.join(cells)+'</tr></table></article>')
(out/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');(out/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>대사 품질 비교 · 조선헌터스</title><style>body{background:#111619;color:#e7e0d3;font:16px system-ui;max-width:1200px;margin:35px auto;padding:0 25px 120px}a{color:#d3ba80}h1{font-size:34px}article{border:1px solid #414039;background:#1c2225;border-radius:12px;padding:16px 22px;margin:16px 0}h2{font-size:20px;margin:0 0 10px}p,small{color:#b8b4aa;font-size:14px}table{width:100%;table-layout:fixed}button{padding:12px 8px;width:100%;color:#eee4d0;background:#31393c;border:1px solid #72664e;border-radius:7px;cursor:pointer}button:hover{background:#524935}small{display:block;margin:6px}footer{position:fixed;bottom:0;left:0;right:0;background:#22292d;padding:12px 25px;border-top:1px solid #847251;display:flex;align-items:center;gap:25px}audio{flex:1}#now{min-width:280px}</style><h1>대사 품질 비교</h1><p>같은 대사 6줄 × 4버전. A/B는 같은 배역의 설정 비교, C/D는 같은 ElevenLabs 배역의 연기 비교입니다.<br>서비스 간 배역이 다르므로 목소리 취향과 모델 성능을 분리해서 들어주세요. 무당·주모의 Eleven 배역은 임시이며 나이감은 미확정입니다.<br>청취 음량은 -18 LUFS 목표 / -1.5 dBTP 상한으로 맞췄으며 호흡과 무음은 유지했습니다.</p><a href="../">전체 오디오 목록으로</a>'''+''.join(content)+'''<footer><strong id="now">버전을 골라 재생하세요</strong><audio id="audio" controls></audio></footer><script>const a=document.getElementById('audio');function play(file,b){a.src=file;document.getElementById('now').textContent=b.textContent;a.play()}a.onerror=()=>document.getElementById('now').textContent='재생 오류';</script></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
print('PACKED',len(qa),'previews; maxTP',max(x['true_peak'] for x in qa))
