"""#497 키 비주얼 main.jpg — 도호 단독 키 아트(21_doho_keyart) 1920×1080 + 왼쪽 빈 곳에 게임 제목(궁서, 타이틀 화면과 같은 금빛)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

SRC = r"C:\workspace\joseon-assets\archive\art-history-2026-09-17\workbench\production\artwork-sequence-2026-09-17\21_doho_keyart.png"
FONT = r"C:\workspace\joseon\assets\fonts\gungsuh\Gungsuh-Regular.ttf"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\workspace\joseon\tmp\ile_497\drive\main.jpg"
W, H = 1920, 1080
GOLD = (240, 208, 140)

src = Image.open(SRC).convert("RGB")
# 1672×941 → 16:9 1920×1080 (비율 차이 0.06% — 늘림 대신 살짝 크게 잡아 가운데 자름)
scale = max(W / src.width, H / src.height)
big = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
x0, y0 = (big.width - W) // 2, (big.height - H) // 2
img = big.crop((x0, y0, x0 + W, y0 + H))

# 왼쪽 글자 자리만 살짝 어둡게 (가로 그라데이션)
shade = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(shade)
for x in range(W):
    a = max(0.0, 1.0 - x / 900.0)
    sd.line([(x, 0), (x, H)], fill=int(150 * a * a))
img = Image.composite(Image.new("RGB", (W, H), (8, 8, 10)), img, shade)

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
f_title = ImageFont.truetype(FONT, 150)
f_en = ImageFont.truetype(FONT, 46)

title = "조선헌터스"
tx, ty = 120, 360
# 제목: 글자 사이 살짝 벌림
cx = tx
for ch in title:
    d.text((cx, ty), ch, font=f_title, fill=GOLD + (255,))
    cx += d.textlength(ch, font=f_title) + 10
title_w = cx - 10 - tx

en = "JOSEON HUNTERS"
spacing = 12
en_w = sum(d.textlength(c, font=f_en) for c in en) + spacing * (len(en) - 1)
ex = tx + (title_w - en_w) / 2
ey = ty + 200
for c in en:
    d.text((ex, ey), c, font=f_en, fill=(222, 214, 196, 255))
    ex += d.textlength(c, font=f_en) + spacing
# 가는 선 두 줄
ly = ey - 26
d.line([(tx + 20, ly), (tx + title_w - 20, ly)], fill=GOLD + (170,), width=2)

# 은은한 그림자
shadow = layer.split()[3].filter(ImageFilter.GaussianBlur(10))
img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, shadow.point(lambda v: int(v * 0.7)))
img.paste(layer, (0, 0), layer)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT, quality=92, subsampling=0)
print(OUT, img.size, os.path.getsize(OUT) // 1024, "KB")
