import pathlib,json,shutil,importlib.util,subprocess,sys,html
sys.stdout.reconfigure(encoding='utf-8');root=pathlib.Path('C:/workspace/joseon');p=root/'tmp/audio566';out=pathlib.Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/batch566');out.mkdir(exist_ok=True)
for sub in ['sfx','voices']:shutil.copytree(p/sub,out/'originals'/sub,dirs_exist_ok=True)
shutil.copyfile(p/'suno.json',out/'suno.json');shutil.copyfile(p/'sfx_batch.json',out/'sfx_batch.json')
spec=importlib.util.spec_from_file_location('intake',root/'tools/audio_intake.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
items=[];qa=[]
for f in sorted((p/'sfx').glob('*/*.wav')):
 meta=json.loads(f.with_suffix('.json').read_text(encoding='utf-8'));dst=out/(f.stem+'.wav');m.convert(str(f),str(dst),'sfx',-16,-1.5,False,False);li,tp=m.out_loudness(str(dst));info=m.ffprobe(str(dst));assert tp<=-1.3
 warning='원본 CLIP '+str(meta['clean']['raw']['clipped']) if meta['clean']['raw']['clipped'] else ''
 items.append({'category':'효과음','title':f.stem,'detail':warning,'file':dst.name,'duration':info['dur']});qa.append({'file':dst.name,'lufs':li,'true_peak':tp,'raw_clipped':meta['clean']['raw']['clipped']})
for v in json.loads((p/'voices/manifest.json').read_text(encoding='utf-8')):
 f=p/'voices'/v['file'];dst=out/(f.stem+'.wav');m.convert(str(f),str(dst),'sfx',-18,-1.5,False,False);li,tp=m.out_loudness(str(dst));info=m.ffprobe(str(dst));assert tp<=-1.3
 items.append({'category':'대사','title':v['role']+' · '+v['name'],'detail':v['request']['text'],'file':dst.name,'duration':info['dur']});qa.append({'file':dst.name,'lufs':li,'true_peak':tp})
suno=json.loads((p/'suno.json').read_text(encoding='utf-8'))
for s in reversed(suno['songs']):items.append({'category':'BGM','title':s['title'],'detail':'Suno v6 · Style80 · 가창 없음 지시 · 다운로드 처리 중','url':'https://suno.com'+s['url']})
(out/'list.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8');(out/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
parts=[]
for cat in ['BGM','대사','효과음']:
 parts.append('<h2>'+cat+'</h2>')
 for x in items:
  if x['category']!=cat:continue
  ctrl='<a target="_blank" href="'+x['url']+'">▶ Suno에서 듣기</a>' if 'url' in x else '<button onclick="play(\''+x['file']+'\',this)">▶ 재생</button>'
  parts.append('<article><div><strong>'+html.escape(x['title'])+'</strong><p>'+html.escape(x['detail'])+'</p></div>'+ctrl+'</article>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>사운드 실험 1차 · 조선헌터스</title><style>body{background:#13191c;color:#e7dfcf;font:16px system-ui;max-width:1100px;margin:35px auto;padding:0 25px 110px}h1{font-size:34px}h2{color:#cfb982;margin-top:36px}article{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:16px;border:1px solid #41433c;margin:8px 0;border-radius:8px;background:#1e2528}p{color:#b7b5a9;font-size:14px}a{color:#d7c591}button{background:#413c31;color:#fff2d9;border:1px solid #807153;padding:12px 22px;border-radius:7px;white-space:nowrap;cursor:pointer}footer{position:fixed;bottom:0;left:0;right:0;background:#242d30;padding:16px 25px;display:flex;gap:20px;align-items:center}audio{flex:1}</style><h1>사운드 실험 · 1차</h1><p>BGM 18곡 / Eleven v4 배역 9개 / 효과음 18개, 총 45개 후보.<br>BGM은 빈 공간·굴의 기척·각성 전조 × Weirdness45/65/80 × 2곡. 대사는 세 배역 각각 세 목소리.<br>Suno 다운로드가 준비 상태에 머물러 BGM은 원본 페이지에서 재생합니다. 원본 클리핑이 있는 효과음은 표시했습니다.</p><a href="../">전체 목록</a> · <a href="../compare565/">Typecast / Eleven v4 비교</a>'''+''.join(parts)+'''<footer><strong id="now">항목을 골라 재생하세요</strong><audio id="audio" controls></audio></footer><script>const audio=document.getElementById('audio');function play(file,b){audio.src=file;document.getElementById('now').textContent=b.parentElement.querySelector('strong').textContent;audio.play()}</script></html>'''
(out/'index.html').write_text(page,encoding='utf-8');print('DONE',len(items),'entries',len(qa),'verified local audio',sum(x.get('raw_clipped',0)>0 for x in qa),'raw clipping warnings')
