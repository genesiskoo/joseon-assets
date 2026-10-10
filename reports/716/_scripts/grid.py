"""확인용: python grid.py <plate> <clip> <n> <x0> <y0> <w> <h> — 잘라서 4배 + 10px 눈금(원본 좌표)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parent.parent
plate, clip, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
x0, y0, w, h = map(int, sys.argv[4:8])
S = 4
f = Image.open(R / "_frames" / f"{plate}_{clip}" / f"{n + 1:04d}.png").convert("RGB").crop((x0, y0, x0 + w, y0 + h)).resize((w * S, h * S), Image.NEAREST)
d = ImageDraw.Draw(f)
for x in range(0, w, 10):
    d.line([(x * S, 0), (x * S, h * S)], fill=(0, 255, 0) if (x0 + x) % 50 == 0 else (0, 90, 0))
    if (x0 + x) % 50 == 0:
        d.text((x * S + 2, 2), str(x0 + x), fill=(0, 255, 0))
for y in range(0, h, 10):
    d.line([(0, y * S), (w * S, y * S)], fill=(0, 255, 0) if (y0 + y) % 50 == 0 else (0, 90, 0))
    if (y0 + y) % 50 == 0:
        d.text((2, y * S + 2), str(y0 + y), fill=(0, 255, 0))
out = R / "_frames" / f"grid_{plate}_{clip}_{n}.png"
f.save(out)
print(out)
