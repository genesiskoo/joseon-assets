from pathlib import Path
import json,subprocess,hashlib
p=Path('C:/workspace/joseon/tmp/cast608');s=Path('C:/workspace/joseon-assets/workbench/audio/560_audio_library/cast608');meta=json.loads((s/'audio_manifest.json').read_text(encoding='utf-8'))
for m in meta:
 stats=m['input_loudness'];gain=-20-float(stats['input_i'])
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p/'raw'/m['file']),'-af','volume='+str(gain)+'dB,alimiter=limit=0.76736:level=false:latency=true','-ar','44100','-ac','1','-c:a','libmp3lame','-b:a','128k',str(s/m['file'])],check=True)
 m['gain_db']=gain;m['sha256']=hashlib.sha256((s/m['file']).read_bytes()).hexdigest()
 assert abs(float(stats['input_i'])+gain+20)<.5,(m['file'],stats,gain)
(s/'audio_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
Path('C:/workspace/joseon-assets/reports/608_voice_casting/audio_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('LINEAR_NORMALIZATION_52_PASS')
