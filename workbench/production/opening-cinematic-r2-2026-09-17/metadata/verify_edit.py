"""Verify the delivered edit and record inspectable frames without altering media."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
p.add_argument('root', type=Path)
p.add_argument('--ffmpeg', required=True)
p.add_argument('--ffprobe', required=True)
a = p.parse_args()
video = a.root / 'edit/doho_revised_8s_v001.mp4'
probe = json.loads(subprocess.check_output([a.ffprobe, '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(video)], text=True))
stream, = probe['streams']
assert stream['codec_type'] == 'video'
assert (stream['width'], stream['height']) == (1280, 720)
assert stream['r_frame_rate'] == '24/1'
assert int(stream['nb_read_frames']) == 192
assert float(probe['format']['duration']) == 8
subprocess.run([a.ffmpeg, '-v', 'error', '-i', str(video), '-f', 'null', '-'], check=True)
(a.root / 'metadata/final_ffprobe.json').write_text(json.dumps(probe, indent=2), encoding='utf-8')

# Read only known text project files, without blindly extracting archive members.
archive = a.root / 'edit/doho_revised_8s_v001_project.zip'
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name in ('edit.mjs', 'project.json'):
        data = z.read('project/' + name)
        (a.root / 'edit' / name).write_bytes(data)
    archive_listing = [{'path': i.filename, 'bytes': i.file_size} for i in z.infolist()]
(a.root / 'metadata/project_archive_inventory.json').write_text(json.dumps(archive_listing, indent=2), encoding='utf-8')

font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
samples = list(range(0, 192, 12))
samples += [46, 47, 48, 49, 64, 65, 66, 67, 94, 95, 96, 97, 191]
frames = {}
for n in sorted(set(samples)):
    out = a.root / 'review' / f'final_f{n:03d}.png'
    subprocess.run([a.ffmpeg, '-v', 'error', '-y', '-i', str(video), '-vf', f'select=eq(n\\,{n})', '-frames:v', '1', str(out)], check=True)
    frames[n] = out
for label, indices in [('overview', list(range(0, 192, 12))), ('cuts', [46,47,48,49,64,65,66,67,94,95,96,97])]:
    sheet = Image.new('RGB', (1920, ((len(indices)+3)//4)*300), '#111111')
    draw = ImageDraw.Draw(sheet)
    for i, n in enumerate(indices):
        x, y = (i%4)*480, (i//4)*300
        with Image.open(frames[n]) as im:
            sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y+30))
        draw.text((x+8,y+3), f'frame {n} / {n/24:.3f}s', font=font, fill='white')
    sheet.save(a.root/'review'/f'final_{label}.jpg',quality=94)

files = []
for subdir in ('keyframes', 'clips', 'edit'):
    for path in sorted((a.root/subdir).glob('*')):
        if path.is_file():
            files.append({'path':path.relative_to(a.root).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(a.root/'metadata/file_inventory.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
print(json.dumps({'duration':8,'fps':24,'frames':192,'size':[1280,720],'audio_tracks':0,'decode':'passed','archive':'passed','files_hashed':len(files)}))
