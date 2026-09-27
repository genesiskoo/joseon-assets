from pathlib import Path
import json, hashlib
out=Path('C:/workspace/joseon-assets/reports/455/final')
p=out/'manifest.json'
m=json.loads(p.read_text(encoding='utf-8'))
for c in m['clips']:
    video=Path(c['path'])
    c['bytes']=video.stat().st_size
    c['sha256']=hashlib.sha256(video.read_bytes()).hexdigest()
m['validation']={'window_capture_checks':33,'headless_checks':32,'runner_selftest':5,'decoded_audio_video':8,'non_silent_audio':8}
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('8 final clips:',round(sum(c['seconds'] for c in m['clips']),1),'seconds')
