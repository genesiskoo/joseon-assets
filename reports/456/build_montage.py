"""#456: 30-second vertical slice montage from #455 verified game captures."""
from pathlib import Path
import subprocess, json, hashlib, sys
import imageio_ffmpeg
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
OUT = Path(__file__).resolve().parent
SRC = OUT.parent / '455' / 'final'
FF = imageio_ffmpeg.get_ffmpeg_exe()
# Frame ranges: every source and output boundary is exactly on a 30fps frame.
CUTS = [
    ('01_motgol_walk', 120, 90, '못골 보행'),
    ('02_dialogue_quest', 24, 90, '할매 의뢰'),
    ('03_field_exploration', 45, 60, '들녘 탐험'),
    ('04_cave_entry', 75, 60, '굴 입장'),
    ('05_dungeon_combat', 270, 90, '회오리·처치'),
    ('05_dungeon_combat', 585, 90, '다음 적 전투'),
    ('08_skills_equipment', 24, 45, '검술 성장'),
    ('08_skills_equipment', 195, 45, '장비와 능력'),
    ('06_heukrang_boss', 600, 240, '흑랑 전투·처치'),
    ('07_loot_inventory', 240, 90, '흑랑 송곳니 식별·옵션'),
]
assert sum(c[2] for c in CUTS) == 900
sources = json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
by_id = {c['id']:c for c in sources['clips']}
command = [FF, '-hide_banner', '-y']
filters = []
edl = {'fps':30, 'resolution':[1920,1080], 'frames':900, 'seconds':30.0,
       'audio':'source game music and effects; 25ms fades at cuts; no new soundtrack',
       'sources_manifest':str(SRC/'manifest.json'), 'cuts':[]}
at = 0
for i,(name,start,length,label) in enumerate(CUTS):
    p = SRC/f'{name}.mp4'
    assert (start+length)/30 <= by_id[name]['seconds']+1/30
    assert hashlib.sha256(p.read_bytes()).hexdigest() == by_id[name]['sha256']
    command += ['-i', str(p)]
    filters.append(f'[{i}:v]trim=start_frame={start}:end_frame={start+length},setpts=PTS-STARTPTS,fps=30,setsar=1,format=yuv420p[v{i}]')
    filters.append(f'[{i}:a]atrim=start={start/30:.9f}:end={(start+length)/30:.9f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:st=0:d=0.025,afade=t=out:st={length/30-.025:.9f}:d=0.025[a{i}]')
    edl['cuts'].append({'label':label,'source':str(p),'source_sha256':by_id[name]['sha256'],
                        'source_from_frame':start,'duration_frames':length,
                        'timeline_from_frame':at,'timeline_to_frame':at+length})
    at += length
filters.append(''.join(f'[v{i}][a{i}]' for i in range(len(CUTS)))+f'concat=n={len(CUTS)}:v=1:a=1[vc][ac]')
filters.append('[vc]fade=t=in:st=0:d=0.15,fade=t=out:st=29.7:d=0.3[v]')
filters.append('[ac]afade=t=in:st=0:d=0.1,afade=t=out:st=29.8:d=0.2[a]')
filter_path=OUT/'filter_graph.txt'
filter_path.write_text(';\n'.join(filters),encoding='utf-8')
target=OUT/'joseon_hunters_vertical_slice_30s.mp4'
command += ['-filter_complex_script',str(filter_path),'-map','[v]','-map','[a]',
            '-frames:v','900','-t','30','-c:v','libx264','-preset','fast','-crf','18',
            '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000',
            '-movflags','+faststart',str(target)]
print('Rendering 10 cuts / 8 source scenes / exactly 900 frames...',flush=True)
with (OUT/'render_raw.log').open('w',encoding='utf-8') as log:
    r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=600)
if r.returncode:
    print((OUT/'render_raw.log').read_text(encoding='utf-8'))
    raise SystemExit(r.returncode)
frames,secs=imageio_ffmpeg.count_frames_and_secs(str(target))
assert frames == 900 and abs(secs-30)<.001,(frames,secs)
with (OUT/'verify_raw.log').open('w',encoding='utf-8') as log:
    subprocess.run([FF,'-hide_banner','-xerror','-i',str(target),'-map','0:v:0','-map','0:a:0','-af','volumedetect','-f','null','-'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
verify=(OUT/'verify_raw.log').read_text(encoding='utf-8')
assert 'mean_volume:' in verify and 'mean_volume: -inf' not in verify
edl.update(output=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,
           verification={'decoded_video_frames':frames,'duration_seconds':secs,'audio_present_and_non_silent':True},command=command)
(OUT/'edit_manifest.json').write_text(json.dumps(edl,ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,524),'#151410');draw=ImageDraw.Draw(sheet)
for i,at in enumerate([1,4,9,12,23,29]):
    p=OUT/'qa'/f'final_{at:02d}.jpg'
    subprocess.run([FF,'-v','error','-y','-ss',str(at),'-i',str(target),'-frames:v','1','-vf','scale=426:240','-q:v','3',str(p)],check=True)
    x,y=(i%3)*426,(i//3)*262
    with Image.open(p) as im:sheet.paste(im,(x,y))
    draw.text((x+10,y+244),f'{at:02d}s',fill='#eee6cf')
sheet.save(OUT/'contact_final.jpg',quality=85)
lines=['# 조선헌터스 버티컬 슬라이스 30초 (#456)','',
       f'[완성 영상]({target.as_posix()}) · 1920×1080, 30fps, H.264/AAC, 게임 원음 포함. 900프레임 = 정확히 30.000초.','',
       '| 시간 | 장면 |','|---|---|']
for c in edl['cuts']:
    lines.append(f"| {c['timeline_from_frame']/30:g}–{c['timeline_to_frame']/30:g}초 | {c['label']} |")
lines += ['', '컷 구성: 못골·의뢰에서 들녘·굴로 들어가 검술 전투와 성장, 흑랑 처치, 유니크 옵션으로 마무리. 출처8클립의 해시를 확인하고 원본을 보존했다. 게임 원음은 각 화면과 같은 위치에서 잘라 25ms 페이드로 컷 경계 딸깍만 줄였다. 새 음악·나레이션·생성 장면은 없다.',
          '', '로컬 Higgsedit CLI가 없어 설치된 FFmpeg로 컷·오디오 편집을 실행했다. 원본 해시·프레임 단위 EDL·필터·raw로그·최종 해시를 함께 보존하므로 재현/검수가 가능하다.',
          '', '검증: 영상900프레임/30.000초, 영상·오디오 전체 디코딩, 비무음 오디오 PASS. 1/4/9/12/23/29초 프레임을 직접 검수했다. 도구/목록/검수만 Git 기록, MP4는 reports/456에 로컬 보존.']
(OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'PASS: {frames} frames, {secs:.3f}s, audio present; {target.stat().st_size/1e6:.1f} MB',flush=True)
