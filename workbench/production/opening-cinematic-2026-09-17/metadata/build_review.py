"""Extract an exact frame every 0.5 s from a 24 fps pilot; make a labelled QC sheet."""
from pathlib import Path
import argparse, json, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
p.add_argument('asset_root', type=Path)
p.add_argument('shot', choices=['OP04', 'OP06', 'OP11'])
p.add_argument('--ffmpeg', required=True)
a = p.parse_args()
clip = a.asset_root / 'clips' / f'{a.shot}_v001_seedance25_720p.mp4'
review = a.asset_root / 'review'
review.mkdir(exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 21)
with tempfile.TemporaryDirectory(prefix='joseon_pilot_qc_') as tmp:
    subprocess.run([a.ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(clip),
        '-vf', r'select=not(mod(n\,12))', '-fps_mode', 'vfr', str(Path(tmp)/'frame_%03d.png')], check=True)
    frames = sorted(Path(tmp).glob('frame_*.png'))
    width, height, bar, cols = 480, 270, 30, 4
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols*width, rows*(height+bar)), '#141414')
    d = ImageDraw.Draw(sheet)
    for index, path in enumerate(frames):
        img = Image.open(path).convert('RGB')
        x, y = index%cols*width, index//cols*(height+bar)
        sheet.paste(img.resize((width,height), Image.Resampling.LANCZOS), (x,y+bar))
        d.text((x+10,y+3), f'{a.shot} | {index*0.5:04.1f}s', font=font, fill='white')
        if index in (0, 10, 20):
            img.save(review / f'{a.shot}_{index*0.5:04.1f}s.png')
    out = review/f'{a.shot}_contact_2fps.jpg'
    sheet.save(out, quality=94)
    print(json.dumps({'shot':a.shot,'samples':len(frames),'sample_interval_s':0.5,'contact_sheet':str(out)}))
