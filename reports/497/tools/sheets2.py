"""#497 새 1080p 녹화 — 장면별 대조표(장면 안 프레임 번호 표시)."""
import re, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont

WORK = os.path.dirname(os.path.abspath(__file__))
AVI = os.path.join(WORK, "capture_1080.avi")
mk = {}
for line in open(os.path.join(WORK, "capture_1080_out.log"), encoding="utf-8", errors="replace"):
    m = re.match(r"CAPTURE (\S+) (BEGIN|END) (\d+)", line.strip())
    if m:
        mk.setdefault(m.group(1), {})[m.group(2)] = int(m.group(3))

TW, TH = 320, 180
rate = {"05_dungeon_combat": 2, "06_heukrang_boss": 2}
font = ImageFont.load_default()
for clip, be in mk.items():
    b, e = be["BEGIN"], be["END"]
    r = rate.get(clip, 1)
    step = 30 // r
    frames = list(range(0, e - b, step))
    tdir = os.path.join(WORK, "t2_" + clip)
    os.makedirs(tdir, exist_ok=True)
    # 한 번에: select로 step 간격 프레임만
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{b / 30:.4f}", "-t", f"{(e - b) / 30:.4f}", "-i", AVI,
                    "-vf", f"select='not(mod(n\\,{step}))',scale={TW}:{TH}", "-vsync", "vfr", os.path.join(tdir, "f_%04d.jpg")], check=True)
    files = sorted(os.listdir(tdir))
    cols = 6
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * TW, rows * (TH + 14)), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        x, y = (i % cols) * TW, (i // cols) * (TH + 14)
        sheet.paste(Image.open(os.path.join(tdir, f)), (x, y))
        d.text((x + 3, y + TH + 1), f"{clip[:2]} f{i * step} ({i * step / 30:.1f}s)", fill=(255, 220, 120), font=font)
    sheet.save(os.path.join(WORK, f"s2_{clip}.jpg"), quality=78)
    print(clip, b, e, len(files))
