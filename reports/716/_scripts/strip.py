"""확인용 띠: python strip.py <plate> <clip> <x0> <y0> <w> <h> <n1,n2,…> [out] — 클립 프레임 n(0부터)을 잘라 가로로 잇는다(_frames/ 에서)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parent.parent
plate, clip = sys.argv[1], sys.argv[2]
x0, y0, w, h = map(int, sys.argv[3:7])
ns = [int(v) for v in sys.argv[7].split(",")]
out = Path(sys.argv[8]) if len(sys.argv) > 8 else R / "_frames" / f"strip_{plate}_{clip}.png"
scale = 2 if w * len(ns) <= 1600 else 1
im = Image.new("RGB", (w * scale * len(ns), h * scale + 18), "#000")
d = ImageDraw.Draw(im)
for i, n in enumerate(ns):
    f = Image.open(R / "_frames" / f"{plate}_{clip}" / f"{n + 1:04d}.png").convert("RGB").crop((x0, y0, x0 + w, y0 + h))
    im.paste(f.resize((w * scale, h * scale), Image.NEAREST), (i * w * scale, 18))
    d.text((i * w * scale + 4, 2), f"n{n}", fill="#ff0")
im.save(out)
print(out)
