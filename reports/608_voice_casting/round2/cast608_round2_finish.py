from pathlib import Path
import json,re,shutil
site=Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/cast608/round2');report=Path('C:/workspace/joseon-assets/reports/608_voice_casting/round2')
data=json.loads((site/'list.json').read_text(encoding='utf-8'))
checks={'merchant':'중년처럼 매끈하지 않은지, 늙은 목의 결과 유쾌한 너스레가 함께 들리는지.','elder':'노년의 갈라진 결과 책임감 있는 무게가 느껴지는지. 약한 속삭임으로 빠지지 않는지.','shaman':'젊은 상담사 대신 마르고 거친 노파로 들리는지. 경고가 단호하고 또렷한지.','jumo':'낮고 농밀한 음색과 말끝의 유혹이 실제 v4 대사에서도 남는지. 평범한 안내 음성이 아닌지.','dokkaebi':'배에서 울리는 거한의 흉성·거친 목·호방한 기세가 함께 들리는지. 매끈한 낭독이 아닌지.'}
for r in data['roles']:
 for c in r['candidates']:c['risk']=checks[r['id']]
text=(site/'index.html').read_text(encoding='utf-8');text=re.sub(r'(<script id="payload" type="application/json">)[\s\S]*?(</script>)',lambda m:m[1]+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+m[2],text,count=1)
text=text.replace('추천 1순위 차례로 듣기','A안 차례로 듣기').replace('김 영감은 선택한 Manbo, 다른 역은 1차 A안','${esc(data.jobs.find(j=>j.role===r.id&&j.rank===0)?.name||\'1차 기준\')}')
for name in ['cast608_round2.py','cast608_round2_package.py','cast608_round2_finish.py']:shutil.copy2(Path('C:/workspace/joseon/tmp')/name,report/name)
(site/'index.html').write_text(text,encoding='utf-8');(site/'list.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
Path('C:/workspace/joseon/tmp/cast608/round2_qa.json').write_text(json.dumps({'audio_count':45,'new_v4_dialogue_count':30,'designed_voices':15,'models':{'design':'eleven_ttv_v3','dialogue':'eleven_v4'},'checks':['decode','LUFS within 1.1 of -20','true peak <= -1.5','HTTP 200 all45','browser v4 jumo and dokkaebi','browser design preview','original choice preserved after reload'],'generated_by':'codex'},indent=2),encoding='utf-8')
shutil.copy2(Path('C:/workspace/joseon/tmp/cast608/round2_qa.json'),report/'qa.json')
print('FINISHED')
