from pathlib import Path
import json,subprocess,re,hashlib,shutil,urllib.request,sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path('C:/workspace/joseon/tmp/cast608/round2');site=Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/cast608');dst=site/'round2';(dst/'audio').mkdir(parents=True,exist_ok=True)
plan=json.loads((root/'plan.json').read_text(encoding='utf-8'));old=json.loads((site/'list.json').read_text(encoding='utf-8'))
def stats(path):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','loudnorm=I=-20:TP=-2:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',r.stderr).group())
meta=[]
for src in sorted(root.glob('*.mp3')):
 target=dst/'audio'/src.name;initial=stats(src);gain=-20-float(initial['input_i'])
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-af',f'volume={gain}dB,alimiter=limit=0.76736:level=false:latency=true','-ar','44100','-ac','1','-c:a','libmp3lame','-b:a','128k',str(target)],check=True)
 final=stats(target);assert abs(float(final['input_i'])+20)<1.1,(src.name,final);assert float(final['input_tp'])<=-1.5,(src.name,final)
 duration=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(target)],text=True))['format']['duration']);assert .4<duration<90
 meta.append({'file':'audio/'+src.name,'kind':'voice_design_preview' if '_design_' in src.name else 'eleven_v4_dialogue','duration':duration,'input':initial,'final':final,'raw_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
briefs={'merchant':'늙은 성대의 갈라진 결 + 구수한 너스레. 힘 있고 사람 좋은 노장 장사꾼.','elder':'80세 안팎의 거친 노년 저음. 피로와 상실을 품되 단단한 마을 어른.','shaman':'80세 안팎의 마르고 거친 노파 음색. 낮고 단호하게 경고하는 할매.','jumo':'낮은 벨벳·허스키 음색, 농밀한 호흡과 늘어지는 말끝. 사람을 끌어당기는 구미호 주모.','dokkaebi':'굵은 사포 같은 목, 큰 흉성과 호방한 기세. 장비를 연상시키는 털북숭이 거한.'}
for r in plan['roles']:
 r['target']=briefs[r['id']];r['old']=True
 baseline=3 if r['id']=='merchant' else 1
 for j in old['jobs']:
  if j['role']==r['id'] and j['rank']==baseline:
   copy=j.copy();copy['rank']=0;copy['file']='../'+j['file'];copy['name']='1차 기준 · '+j['name'];plan['jobs'].append(copy)
 for c in r['candidates']:
  c['why']=briefs[r['id']];c['preview_file']='audio/'+Path(c['preview_file']).name
for j in plan['jobs']:
 if j['file'].startswith('round2/'):j['file']=j['file'][7:]
plan['voices']=[];plan['scope']='2차 전용 음색 설계 15개. 설계 미리듣기는 eleven_ttv_v3, 동일 문장 대사는 eleven_v4.'
template=Path('C:/workspace/joseon/tmp/cast608_page.html').read_text(encoding='utf-8')
template=template.replace('못골의 목소리를 다시 고르자','노년의 무게 · 구미호의 유혹 · 거한의 흉성').replace('못골 성우 오디션 · 조선헌터스','2차 성우 튜닝 · 조선헌터스').replace('도호의 능청, 촌로의 무게, 주모의 속내. 같은 대사를 듣고 인물마다 어울리는 성우를 골라보세요.','새로 설계한 15개 음색을 같은 대사로 비교합니다. 도호·억쇠의 1차 선택은 그대로 유지합니다.')
start=template.index('<div class="notice">후보 순위는');end=template.index('<nav class="tabs">',start)
template=template[:start]+'''<div class="notice"><b>2차 튜닝</b> · 김 영감·촌장·할매의 노년감 / 주모의 농밀한 유혹 / 도깨비의 굵고 걸걸한 발성.<br>각 후보의 <b>상황 1·2는 Eleven v4</b> 동일 대사·문맥입니다. <b>음색 설계 미리듣기는 eleven_ttv_v3</b> 긴 대사이며 별도 비교용입니다. 모두 −20 LUFS 목표로 맞췄습니다.<br>1차 선택: 도호 K-Actor Lee · 김 영감 Manbo · 억쇠 Jae-seong. 촌장·도깨비 후보 없음. <a href="../">1차 오디션 / 기존 선택 돌아가기</a></div>'''+template[end:]
template=template.replace('<button data-tab="catalog">성우 목록</button>','').replace('joseon-cast608\'','joseon-cast608-round2\'').replace('조선헌터스 성우 선택 #608','조선헌터스 2차 성우 선택 #608').replace('기존 성우 비교','1차 기준 비교').replace('같은 문장·문맥으로 다시 생성','김 영감은 선택한 Manbo, 다른 역은 1차 A안').replace('선택 결과를 복사해 채팅에 보내면 다음 성우 튜닝에 사용합니다.','1차 선택을 유지하면서 2차 음색을 별도로 저장합니다. 선택 결과를 복사해 채팅에 보내주세요.').replace('${c.rank===1?\'우선 제안\':\'대안 \'+c.rank}','${\'새 음색 \'+String.fromCharCode(64+c.rank)}')
template=template.replace('<button class="pick ${choices[r.id]', '<button data-design="${c.preview_file}" data-name="${esc(c.name)}">▶ 음색 설계 미리듣기 (v3)</button><button class="pick ${choices[r.id]')
template=template.replace("if(b.dataset.play)playItems", "if(b.dataset.design)playItems([{src:b.dataset.design,label:b.dataset.name+' / 음색 설계 미리듣기 (eleven_ttv_v3)'}]);if(b.dataset.play)playItems")
template=template.replace('<b>7</b>캐릭터','<b>5</b>튜닝 캐릭터').replace('<b>21</b>후보 배정','<b>15</b>새 음색').replace('<b>${data.jobs.length}</b>v4 오디션','<b>30</b>새 v4 대사').replace('<b>${data.voices.length}</b>성우 목록','<b>15</b>설계 미리듣기')
page=template.replace('__PAYLOAD__',json.dumps(plan,ensure_ascii=False).replace('</','<\\/'));(dst/'index.html').write_text(page,encoding='utf-8');(dst/'list.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8');(dst/'audio_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
original=(site/'index.html').read_text(encoding='utf-8')
if 'href="round2/"' not in original:original=original.replace('<nav class="tabs">','<div class="notice"><a href="round2/"><b>▶ 2차 튜닝 듣기 — 노년감 / 구미호 유혹 / 도깨비 거한 음색</b></a><br>1차 선택·메모는 유지됩니다. 새 음색 15개·v4 대사 30개를 추가했습니다.</div><nav class="tabs">')
(site/'index.html').write_text(original,encoding='utf-8')
report=Path('C:/workspace/joseon-assets/reports/608_voice_casting/round2');shutil.copytree(root,report,dirs_exist_ok=True)
for f in ['cast608_round2.py','cast608_round2_package.py']:shutil.copy2(Path('C:/workspace/joseon/tmp')/f,report/f)
shutil.copy2(dst/'audio_manifest.json',report/'audio_manifest.json')
for m in meta:
 with urllib.request.urlopen('http://127.0.0.1:8767/cast608/round2/'+m['file']) as response:assert response.status==200
print('ROUND2_QA_PASS',len(meta),'audio, LUFS, true peak, decode, HTTP')
