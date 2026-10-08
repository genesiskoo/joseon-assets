"""완성 영상 1초 간격 대조표 — python vsheet.py <mp4> <out.jpg>"""
import subprocess, sys, io, json
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
d = float(json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", src], capture_output=True, text=True).stdout)["format"]["duration"])
W, H, cols = 384, 216, 6
ts = [t + 0.5 for t in range(int(d))]
sheet = Image.new("RGB", (cols * W, ((len(ts) + cols - 1) // cols) * (H + 14)), (16, 16, 16))
dr = ImageDraw.Draw(sheet)
for i, t in enumerate(ts):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf", f"scale={W}:{H}", "-f", "image2pipe", "-vcodec", "mjpeg", "-"], capture_output=True, check=True)
    x, y = (i % cols) * W, (i // cols) * (H + 14)
    sheet.paste(Image.open(io.BytesIO(r.stdout)), (x, y))
    dr.text((x + 3, y + H + 1), f"{t:.1f}s", fill=(255, 220, 120))
sheet.save(out, quality=80)
print(out, len(ts))
