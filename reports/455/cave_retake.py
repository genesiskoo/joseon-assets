from pathlib import Path
import importlib.util, subprocess, re, json, sys
import imageio_ffmpeg
sys.stdout.reconfigure(encoding='utf-8')
root = Path(r'C:/Users/FORYOUCOM/.codex/worktrees/455-slice-capture/joseon')
out = Path('C:/workspace/joseon-assets/reports/455/final')
spec = importlib.util.spec_from_file_location('capture_slice', root / 'tools/capture_slice.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
avi = out / 'cave_retake.avi'
cmd = [r'C:\Program Files (x86)\Steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe','--path',str(root),'--windowed','--resolution','1920x1080','--fixed-fps','30','--disable-vsync','--write-movie',str(avi),'--','--e2e=_slice_capture','--capture-only=cave']
print('Recording clean cave entry retake...', flush=True)
raw = m.run_logged(cmd, out / 'cave_retake_raw.log')
assert 'E2E SUMMARY: 1/1 PASS' in raw
b = {edge:int(frame) for edge, frame in re.findall(r'CAPTURE 04_cave_entry (BEGIN|END) (\d+)',raw)}
start = (b['BEGIN']-1)/30
duration = (b['END']-b['BEGIN'])/30
ff = imageio_ffmpeg.get_ffmpeg_exe()
target = out / '04_cave_entry.mp4'
m.run_logged([ff,'-hide_banner','-y','-i',str(avi),'-ss',str(start),'-t',str(duration),'-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(target)],out/'04_cave_entry_encode.log')
verify=m.run_logged([ff,'-hide_banner','-i',str(target),'-map','0:v:0','-map','0:a:0','-af','volumedetect','-f','null','-'],out/'04_cave_entry_verify.log')
assert 'mean_volume:' in verify and 'mean_volume: -inf' not in verify
m.run_logged([ff,'-hide_banner','-y','-ss',str(duration*.6),'-i',str(target),'-frames:v','1','-vf','scale=640:360','-q:v','3',str(out/'preview/04_cave_entry.jpg')],out/'04_cave_entry_preview.log')
m.run_logged([ff,'-hide_banner','-y','-ss',str(duration-.5),'-i',str(target),'-frames:v','1','-vf','scale=1280:720','-q:v','3',str(out/'preview/cave_tail.jpg')],out/'cave_tail_preview.log')
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
manifest['retake_command']=cmd
for c in manifest['clips']:
    c['source_file']=str(avi if c['id']=='04_cave_entry' else out/'capture_master.avi')
    if c['id']=='04_cave_entry':
        c.update(seconds=round(duration,3),source_begin_frame=b['BEGIN'],source_end_frame=b['END'])
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 버티컬 슬라이스 촬영 #455','','실제 게임 프레임과 게임 소리를 담은 1080p30 MP4. 로딩·순간이동 준비·개발 안내를 제외한 편집용 개별 클립.','','| 파일 | 장면 | 길이 |','|---|---|---|']
for c in manifest['clips']:
    p=c['path'].replace('\\','/')
    lines.append(f"| [{c['id']}.mp4]({p}) | {c['label']} | {c['seconds']:.1f}초 |")
lines += ['', '촬영 준비: e2e 독립 세이브. 마을·대화는 Lv1, 탐험/전투는 Lv6·시작 장비·배운 검술·탕약/영약6개. 도호 명중 확정은 기존 e2e 기본이며 적/보스 수치는 현재 게임 그대로. 실시간 성능 측정 자료는 아니다.', '', '원본 capture_master.avi, 굴 입장 보완 원본 cave_retake.avi, 원문 로그와 manifest.json 프레임 범위를 보존했다. MP4 8개 영상/오디오 전체 디코딩·무음 검사 PASS. 영상과 원본은 로컬 보존, Git에는 촬영 도구·목록·검수 자료만 기록한다.']
(out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
from PIL import Image, ImageDraw
for group in range(2):
    sheet=Image.new('RGB',(1280,768),'#131312'); draw=ImageDraw.Draw(sheet)
    for idx,c in enumerate(manifest['clips'][group*4:(group+1)*4]):
        x,y=(idx%2)*640,(idx//2)*384
        with Image.open(out/'preview'/f"{c['id']}.jpg") as im: sheet.paste(im,(x,y))
        draw.text((x+12,y+364),c['id'],fill='#eee3c9')
    sheet.save(out/f'contact_{group+1}.jpg',quality=82)
print('Clean cave entry verified.',flush=True)
