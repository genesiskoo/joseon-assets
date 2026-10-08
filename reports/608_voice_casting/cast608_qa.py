from pathlib import Path
import json,subprocess,re,urllib.request
s=Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/cast608');d=json.loads((s/'list.json').read_text(encoding='utf-8'));checks=[]
for j in d['jobs']:
 file=s/j['file'];r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(file),'-af','loudnorm=I=-20:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 v=json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',r.stderr).group());assert abs(float(v['input_i'])+20)<1.1,(j['file'],v);assert float(v['input_tp'])<=-1.5,(j['file'],v)
 with urllib.request.urlopen('http://127.0.0.1:8767/cast608/'+j['file']) as r:assert r.status==200
 checks.append({'file':j['file'],'lufs':v['input_i'],'tp':v['input_tp'],'http':200})
print('QA_PASS',len(checks),'audio decoded / loudness / true peak / HTTP')
Path('C:/workspace/joseon-assets/reports/608_voice_casting/audio_qa.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
