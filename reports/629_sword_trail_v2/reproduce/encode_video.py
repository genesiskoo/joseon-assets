"""#629: encode actual Godot combat before/after. No invented motion or retiming."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

WORK = Path(__file__).resolve().parent
OUT = WORK / 'deliverables'
OUT.mkdir(exist_ok=True)
FFMPEG, FFPROBE = shutil.which('ffmpeg'), shutil.which('ffprobe')
FONT = 'C:/Windows/Fonts/malgun.ttf'
BOUNDS, COMBAT = {}, {}
for phase in ['before', 'after']:
    log = (WORK / (phase + '.raw.log')).read_text(encoding='utf-8-sig')
    assert f'VIDEO629 phase={phase} checks=19 fails=0 PASS' in log
    errors = [s for s in log.splitlines() if re.search(r'SCRIPT ERROR|SHADER ERROR|Parse Error|Compile Error|^ERROR:', s) and 'resources still in use at exit' not in s]
    assert not errors, errors
    bounds = {}
    for name, edge, frame in re.findall(r'CAPTURE (\S+) (BEGIN|END) (\d+)', log):
        bounds.setdefault(name, {})[edge] = int(frame)
    assert len(bounds) == 4 and all(b['END'] - b['BEGIN'] == 270 for b in bounds.values())
    BOUNDS[phase] = bounds
    COMBAT[phase] = {r['segment']: r for r in [json.loads(s.removeprefix('COMBAT629 ')) for s in log.splitlines() if s.startswith('COMBAT629 ')]}
assert BOUNDS['before'] == BOUNDS['after']
for key, before in COMBAT['before'].items():
    after = COMBAT['after'][key]
    assert {k: v for k, v in before.items() if k != 'gold_frames'} == {k: v for k, v in after.items() if k != 'gold_frames'}, (before, after)
    assert before['gold_frames'] == 0
    assert after['gold_frames'] > 0 if key == 'crit' else after['gold_frames'] == 0

def run(args, filename):
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
    (WORK / filename).write_text(p.stdout, encoding='utf-8')
    if p.returncode:
        print(p.stdout, flush=True)
        raise RuntimeError(filename)
    return p.stdout

def caption(name, title, compare):
    h = 590 if compare else 720
    im = Image.new('RGBA', (1280, h))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1279, 71 if compare else 49), fill=(16, 17, 18, 255))
    d.rectangle((0, h-38, 1279, h-1), fill=(16, 17, 18, 255))
    d.text((20, 7), '#629 검광 v2 | ' + title, font=ImageFont.truetype(FONT, 24), fill='white')
    if compare:
        d.text((20, 40), '변경 전 · 단색 가산 검광', font=ImageFont.truetype(FONT, 21), fill=(235, 215, 190))
        d.text((660, 40), '변경 후 · 먹 외곽 + 밝은 날', font=ImageFont.truetype(FONT, 21), fill=(245, 232, 199))
    d.text((20, h-31), '실제 Godot 전투 · 동일 카메라/장비/난수 · 정상 재생 1× · 고정60fps 기록은 성능 측정 아님', font=ImageFont.truetype(FONT, 17), fill=(205, 205, 205))
    target = WORK / (name + '_caption.png')
    im.save(target)
    return target

def encode(key, title, compare):
    b = BOUNDS['before'][key]
    start, end = b['BEGIN']-1, b['END']-1
    header = caption(key + ('_pair' if compare else '_actual'), title, compare)
    output = OUT / (key + ('_pair' if compare else '_actual') + '.mp4')
    if compare:
        inputs = ['-i', str(WORK / 'before.avi'), '-i', str(WORK / 'after.avi'), '-loop', '1', '-framerate', '60', '-i', str(header)]
        graph = f'[0:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,crop=480:360:420:140,scale=640:480[l];[1:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,crop=480:360:420:140,scale=640:480[r];[l][r]hstack=inputs=2,pad=1280:590:0:72:black[base];[base][2:v]overlay=shortest=1[out];[1:a]atrim=start={start/60}:end={end/60},asetpts=PTS-STARTPTS[a]'
    else:
        inputs = ['-i', str(WORK / 'after.avi'), '-loop', '1', '-framerate', '60', '-i', str(header)]
        graph = f'[0:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS[base];[base][1:v]overlay=shortest=1[out];[0:a]atrim=start={start/60}:end={end/60},asetpts=PTS-STARTPTS[a]'
    run([FFMPEG, '-hide_banner', '-y'] + inputs + ['-filter_complex', graph, '-map', '[out]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-r', '60', '-t', '4.5', '-movflags', '+faststart', str(output)], output.stem + '_encode.raw.log')
    print('Encoded', output.name, flush=True)
    return output

names = [('basic', '평타 3타 · 흰 칼날'), ('slash', '참격 2회 · 도력 청 칼끝'), ('whirl', '회오리 2회 · 몸을 따라 도는 검광'), ('crit', '치명 3타 · 실제 명중 뒤 금니')]
pairs, actuals = [], []
for key, title in names:
    pairs.append(encode(key, title, True))
    actuals.append(encode(key, title, False))

def concat(parts, name):
    target = OUT / name
    listing = OUT / (target.stem + '_concat.txt')
    listing.write_text(''.join("file '" + p.name + "'\n" for p in parts), encoding='utf-8')
    run([FFMPEG, '-hide_banner', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', '-movflags', '+faststart', str(target)], target.stem + '_concat.raw.log')
    return target

videos = [concat(pairs, '629_sword_trail_before_after_60fps.mp4'), concat(actuals, '629_sword_trail_actual_60fps.mp4')]
for phase in ['before', 'after']:
    target = OUT / ('629_sword_trail_' + phase + '_engine_capture_60fps.mp4')
    run([FFMPEG, '-hide_banner', '-y', '-i', str(WORK / (phase + '.avi')), '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(target)], phase + '_master_encode.raw.log')
    videos.append(target)

manifest = {'card': 629, 'before_source': '76a5661ecbebb1896f6237fc2afa3a29093d707b', 'fps': 60, 'speed': 1.0, 'capture_check': 'before19/19; after19/19 PASS', 'capture_mode': 'Godot MovieMaker, actual actor/combat; not realtime performance evidence', 'comparison_crop_xywh': [420,140,480,360], 'bounds': BOUNDS, 'combat': COMBAT, 'combat_equality': 'all recorded combat/sample timing fields equal; only post-hit gold_frames differs', 'files': []}
for video in videos:
    run([FFMPEG, '-v', 'error', '-i', str(video), '-f', 'null', '-'], video.stem + '_decode.raw.log')
    probe = json.loads(run([FFPROBE, '-v', 'error', '-show_entries', 'stream=codec_name,width,height,pix_fmt,color_range,r_frame_rate,nb_frames:format=duration,size', '-of', 'json', str(video)], video.stem + '_probe.json'))
    v = next(s for s in probe['streams'] if s['codec_name'] == 'h264')
    assert v['r_frame_rate'] == '60/1'
    assert video.stat().st_size < 10_000_000
    manifest['files'].append({'file': video.name, 'bytes': video.stat().st_size, 'sha256': hashlib.sha256(video.read_bytes()).hexdigest(), 'probe': probe})
(OUT / 'video_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'combat_equality': True, 'files': [{k:v for k,v in f.items() if k != 'probe'} for f in manifest['files']]}, ensure_ascii=False), flush=True)
