"""#497 특정 장면 구간을 중간 해상도로 — python focus.py <clip> <from> <to> <step> <out.jpg>"""
import re, subprocess, os, sys, io
from PIL import Image, ImageDraw, ImageFont

WORK = os.path.dirname(os.path.abspath(__file__))
AVI = os.path.join(WORK, "capture_1080.avi")
mk = {}
for line in open(os.path.join(WORK, "capture_1080_out.log"), encoding="utf-8", errors="replace"):
    m = re.match(r"CAPTURE (\S+) (BEGIN|END) (\d+)", line.strip())
    if m:
        mk.setdefault(m.group(1), {})[m.group(2)] = int(m.group(3))
clip, a, b, step, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
base = mk[clip]["BEGIN"]
TW, TH = 480, 270
frames = list(range(a, b + 1, step))
cols = 4
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TW, rows * (TH + 14)), (16, 16, 16))
d = ImageDraw.Draw(sheet)
font = ImageFont.load_default()
for i, f in enumerate(frames):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(base + f) / 30:.4f}", "-i", AVI, "-frames:v", "1", "-vf", f"scale={TW}:{TH}", "-f", "image2pipe", "-vcodec", "mjpeg", "-"], capture_output=True, check=True)
    im = Image.open(io.BytesIO(r.stdout))
    x, y = (i % cols) * TW, (i // cols) * (TH + 14)
    sheet.paste(im, (x, y))
    d.text((x + 3, y + TH + 1), f"{clip[:2]} f{f} ({f / 30:.2f}s)", fill=(255, 220, 120), font=font)
sheet.save(out, quality=80)
print(out, len(frames))
