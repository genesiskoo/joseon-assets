from pathlib import Path
import json,re,shutil
root=Path('C:/workspace/joseon');p=root/'tmp/audio613';work=Path('C:/Users/FORYOUCOM/.codex/worktrees/613-final-cast/joseon');assets=Path('C:/workspace/joseon-assets');site=assets/'workbench/audio/560_audio_library/release613';report=assets/'reports/613_voice_casting'
rows=json.loads((site/'list.json').read_text(encoding='utf-8'));cast=json.loads((site/'cast.json').read_text(encoding='utf-8'))
page=(site/'index.html').read_text(encoding='utf-8');page=re.sub(r'(<script id="payload" type="application/json">)[\s\S]*?(</script>)',lambda m:m[1]+json.dumps({'rows':rows,'cast':cast},ensure_ascii=False).replace('</','<\\/')+m[2],page,count=1);(site/'index.html').write_text(page,encoding='utf-8')
for name in ['produce.py','intake_voice.py','package.py','verify.py','finish.py','runtime_probe.gd','unit_audio.log','runtime_probe_clean.log','generation.log','intake.log','intake_retry.log','verify.log','verify_retry.log','e2e_audio.log']:shutil.copy2(p/name,report/name)
shutil.copy2(root/'docs/art/613_final_cast/613_final_cast.jpg',report/'613_final_cast.jpg')
qa=json.loads((report/'qa.json').read_text(encoding='utf-8'));qa['engine_checks']=['AUDIO_TEST fails=0 PASS','CAST613_ENGINE_PASS resources=237 play_id=237 stop=PASS, clean exit','browser jumo and dokkaebi actual MP3 readyState4'];qa['e2e_audio_cues']='Not run: project exclusive slot queued behind 307-boss-greetings. Only own waiting runner cancelled. Existing runtime unchanged; all 237 resources/play IDs/stop independently checked.';(report/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
doc=work/'docs/design/audio.md'
with doc.open('a',encoding='utf-8') as f:f.write('\n검증: 237 WAV(PCM16·mono·44100Hz·−18 LUFS ±1.1·TP≤−1.5), 청취 MP3 237개(−20 LUFS ±1.1·TP≤−1.5·HTTP200) PASS. Godot 임포트·test_audio PASS, 독립 엔진 검사 resources=237/play_id=237/stop=PASS 및 정상 종료. 전체 audio_cues e2e는 다른 자리 #307의 단독 창 시험 대기라 미실행이며 우리 대기 프로세스만 정리했다. 음성 재생 코드 변경 없음. 원본·프롬프트·검증은 joseon-assets reports/613_voice_casting, 화면 docs/art/613_final_cast/613_final_cast.jpg.\n')
print('FINISH613')
