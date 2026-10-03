from pathlib import Path
import json,subprocess,re,shutil,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
p=Path('C:/workspace/joseon/tmp/cast608');site=Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/cast608');site.mkdir(parents=True,exist_ok=True)
plan=json.loads((p/'plan.json').read_text(encoding='utf-8'));tested={j['voice_id'] for j in plan['jobs'] if (p/'raw'/j['file']).exists()};account=json.loads((p/'account.json').read_text(encoding='utf-8'))['voices'];cat=json.loads((p/'catalog.json').read_text(encoding='utf-8'))
voices={}
def add(v,account=False):
 labels=v.get('labels',{});id=v['voice_id'];old=voices.get(id,{});gender=labels.get('gender',v.get('gender',''));age=labels.get('age',v.get('age',''));language=labels.get('language',v.get('language',''))
 preview=v.get('preview_url')
 if language!='ko':
  verified=next((x for x in v.get('verified_languages',[]) if x.get('language')=='ko' and x.get('preview_url')),None)
  if verified:preview=verified['preview_url']
 voices[id]={'voice_id':id,'name':v['name'],'description':v.get('description') or '', 'gender':gender.lower(),'age':age.replace('-','_'),'language':language,'preview_url':preview,'in_account':account or old.get('in_account',False),'tested':id in tested}
for v in cat['voices']:add(v)
for v in json.loads((p/'korean.json').read_text(encoding='utf-8'))['voices']:
 if v.get('language')=='ko' and v['voice_id'] not in voices:add(v)
for v in account:add(v,True)
metadata=[]
for j in plan['jobs']:
 src=p/'raw'/j['file'];assert src.exists(),src
 dst=site/j['file'];dst.parent.mkdir(exist_ok=True)
 run=subprocess.run(['ffmpeg','-hide_banner','-loglevel','info','-i',str(src),'-af','loudnorm=I=-20:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 stats=json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',run.stderr).group())
 filt='loudnorm=I=-20:TP=-2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true'.format(**stats)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-af',filt,'-ar','44100','-ac','1','-c:a','libmp3lame','-b:a','128k',str(dst)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(dst)],text=True));duration=float(probe['format']['duration']);assert .4<duration<40
 metadata.append({'file':j['file'],'duration':duration,'raw_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'input_loudness':stats,'target_lufs':-20})
payload={'roles':plan['roles'],'jobs':plan['jobs'],'voices':list(voices.values()),'scope':f"2026-10-04 계정 성우 {len(account)}개 전체 + 한국어/ko-KR 라이브러리 {len(cat['voices'])}개 전체(6페이지) + 추가 한국어 원어민 검색 결과. 중복 제거 {len(voices)}개. 원어민은 주 언어 ko 표기로 구분하며, 다른 언어 성우의 한국어 검증 표기는 원어민과 구분합니다."}
text=Path('C:/workspace/joseon/tmp/cast608_page.html').read_text(encoding='utf-8').replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
(site/'index.html').write_text(text,encoding='utf-8');(site/'list.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');(site/'audio_manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
report=Path('C:/workspace/joseon-assets/reports/608_voice_casting');report.mkdir(parents=True,exist_ok=True)
shutil.copytree(p,report,dirs_exist_ok=True)
(report/'account.json').write_text(json.dumps({'voices':[{'voice_id':v['voice_id'],'name':v['name'],'description':v.get('description'),'labels':v.get('labels'),'category':v.get('category'),'preview_url':v.get('preview_url')} for v in account],'has_more':False},ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['cast608_fetch.py','cast608_more.py','cast608_plan.py','cast608_generate.py','cast608_package.py','cast608_page.html']:shutil.copy2(Path('C:/workspace/joseon/tmp')/name,report/name)
shutil.copy2(site/'audio_manifest.json',report/'audio_manifest.json')
(report/'README.md').write_text('# #608 v4 재캐스팅 오디션\n\n7명 × 후보3명 × 대사2줄 =42개 + 기존5역 비교10개, 총52개. 실제모델 eleven_v4·ko·stability0.5·similarity0.75·앞뒤 문맥 동일. 등록 설명 기준 우선제안이며 음색/연기 최종판정은 PD. 한국어 목록query language=ko&locale=ko-KR 전체6페이지545개+계정98개+추가native검색, 안전 필드만 페이지에 노출. 표준 미리듣기는 등록자 모델, 오디션은실제v4로구분. 전체동일−20LUFS/−2dBTP. 키는저장하지 않음.\n\n청취 http://127.0.0.1:8767/cast608/ . 게임 성우 교체는 최종 캐스팅 선택 뒤.\n',encoding='utf-8')
print('PACKAGED',len(plan['jobs']),'clips',len(voices),'voices',sum(v['language']=='ko' for v in voices.values()),'native','bytes',sum(f.stat().st_size for f in report.rglob('*') if f.is_file())+sum(f.stat().st_size for f in site.rglob('*') if f.is_file()))
