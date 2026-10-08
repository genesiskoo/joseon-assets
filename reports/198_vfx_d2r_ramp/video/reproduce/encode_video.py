"""#198: encode engine-rendered normal-speed VFX comparisons; no generated motion."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

WORK = Path(__file__).resolve().parent / 'video'
FFMPEG, FFPROBE = shutil.which('ffmpeg'), shutil.which('ffprobe')
FONT = Path('C:/Windows/Fonts/malgun.ttf')
RAW = WORK / 'capture_master_corrected.avi'
LOG = WORK / 'capture_corrected.raw.log'
OUT = WORK / 'deliverables'
OUT.mkdir(exist_ok=True)
raw_log = LOG.read_text(encoding='utf-8-sig')
assert 'VIDEO198 checks=63 fails=0 PASS' in raw_log
errors = [line for line in raw_log.splitlines() if re.search(r'SCRIPT ERROR|SHADER ERROR|Parse Error|Compile Error|^ERROR:', line) and 'resources still in use at exit' not in line]
assert not errors, errors
bounds = {}
for name, edge, frame in re.findall(r'CAPTURE (\S+) (BEGIN|END) (\d+)', raw_log):
    bounds.setdefault(name, {})[edge] = int(frame)
assert len(bounds) == 9 and all(b['END'] - b['BEGIN'] == 240 for b in bounds.values())

def run(args, log_name):
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
    (WORK / log_name).write_text(p.stdout, encoding='utf-8')
    if p.returncode:
        print(p.stdout, flush=True)
        raise RuntimeError(log_name)
    return p.stdout

def caption(name, title, footer, compare=False):
    height = 590 if compare else 720
    img = Image.new('RGBA', (1280, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1279, 71 if compare else 49), fill=(16, 17, 18, 255))
    draw.rectangle((0, height - 38, 1279, height - 1), fill=(16, 17, 18, 255))
    draw.text((20, 7), title, font=ImageFont.truetype(str(FONT), 24), fill='white')
    if compare:
        font = ImageFont.truetype(str(FONT), 21)
        draw.text((20, 40), '변경 전 · 단색 틴트', font=font, fill=(235, 215, 190))
        draw.text((660, 40), '변경 후 · 농도별 색띠', font=font, fill=(245, 232, 199))
    draw.text((20, height - 31), footer, font=ImageFont.truetype(str(FONT), 18), fill=(205, 205, 205))
    path = WORK / (name + '.png')
    img.save(path)
    return path

def encode(filter_graph, header, output, audio=False):
    command = [FFMPEG, '-hide_banner', '-y', '-i', str(RAW), '-loop', '1', '-framerate', '60', '-i', str(header), '-filter_complex', filter_graph, '-map', '[out]']
    command += ['-map', '[a]', '-c:a', 'aac', '-b:a', '192k'] if audio else ['-an']
    command += ['-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', '60', '-t', '4', '-movflags', '+faststart', str(output)]
    run(command, output.stem + '_encode.raw.log')

pairs = []
for key, korean in [('fire', '불'), ('cold', '냉기'), ('sal', '살')]:
    footer = '동일 카메라 · 동일 fire_burst 시트 · 크기 2.8 · HDR 3 · 실제 재생 속도 1×'
    if key != 'fire':
        footer = '화염 시트의 팔레트 비교용 · 실제 ' + korean + ' 기술 형상이 아님 · 실제 재생 속도 1×'
    header = caption(key + '_header', '#198 ' + korean + ' | 같은 시트 전후 비교 · 3회 재생', footer, True)
    a, b = bounds[key + '_before'], bounds[key + '_after']
    graph = f"[0:v]trim=start_frame={a['BEGIN']-1}:end_frame={a['END']-1},setpts=PTS-STARTPTS,crop=480:360:320:110,scale=640:480[left];[0:v]trim=start_frame={b['BEGIN']-1}:end_frame={b['END']-1},setpts=PTS-STARTPTS,crop=480:360:320:110,scale=640:480[right];[left][right]hstack=inputs=2,pad=1280:590:0:72:black[base];[base][1:v]overlay=shortest=1[out]"
    target = OUT / (key + '_pair.mp4')
    encode(graph, header, target)
    pairs.append(target)
    print('Encoded comparison:', key, flush=True)

actuals = []
for cue, korean in [('fire_burst', '불 폭발'), ('sal_burst', '살 구름'), ('talisman_fire_hit', '화염부 명중')]:
    name = 'actual_' + cue
    b = bounds[name]
    header = caption(name + '_header', '#198 실제 적용 | ' + korean + ' · 기본 큐 크기 · 3회 재생', '실제 Godot 렌더 · 정상 재생 속도 1× · 기존 시트/입자/수명 · 실시간 성능 측정 영상 아님')
    graph = f"[0:v]trim=start_frame={b['BEGIN']-1}:end_frame={b['END']-1},setpts=PTS-STARTPTS[base];[base][1:v]overlay=shortest=1[out];[0:a]atrim=start={(b['BEGIN']-1)/60}:end={(b['END']-1)/60},asetpts=PTS-STARTPTS[a]"
    target = OUT / (name + '.mp4')
    encode(graph, header, target, True)
    actuals.append(target)
    print('Encoded actual effect:', cue, flush=True)

def concat(parts, target):
    listing = OUT / (target.stem + '_concat.txt')
    listing.write_text(''.join("file '" + part.name + "'\n" for part in parts), encoding='utf-8')
    run([FFMPEG, '-hide_banner', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', '-movflags', '+faststart', str(target)], target.stem + '_concat.raw.log')

comparison = OUT / '198_vfx_before_after_60fps.mp4'
actual = OUT / '198_vfx_actual_60fps.mp4'
concat(pairs, comparison)
concat(actuals, actual)
master = OUT / '198_vfx_engine_capture_60fps.mp4'
run([FFMPEG, '-hide_banner', '-y', '-i', str(RAW), '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(master)], 'master_encode.raw.log')

manifest = {'card': 198, 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'fps': 60, 'speed': 1.0, 'capture_check': '63/63 PASS', 'capture_mode': 'Godot MovieMaker; not realtime performance evidence', 'comparison_crop_xywh': [320, 110, 480, 360], 'raw_intermediate': str(RAW), 'bounds': bounds, 'files': []}
for video in [comparison, actual, master]:
    run([FFMPEG, '-v', 'error', '-i', str(video), '-f', 'null', '-'], video.stem + '_decode.raw.log')
    probe = json.loads(run([FFPROBE, '-v', 'error', '-show_entries', 'stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size', '-of', 'json', str(video)], video.stem + '_probe.json'))
    v = next(s for s in probe['streams'] if s['codec_name'] == 'h264')
    assert v['r_frame_rate'] == '60/1'
    assert video.stat().st_size < 10_000_000
    manifest['files'].append({'file': video.name, 'bytes': video.stat().st_size, 'sha256': hashlib.sha256(video.read_bytes()).hexdigest(), 'probe': probe})
(OUT / 'video_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'deliverables': str(OUT), 'files': [{k:v for k,v in f.items() if k!='probe'} for f in manifest['files']]}, ensure_ascii=False), flush=True)
