"""끝 카드 = main.jpg + STEAM · 2027 한 줄"""
from PIL import Image, ImageDraw, ImageFont
FONT = r"C:\workspace\joseon\assets\fonts\gungsuh\Gungsuh-Regular.ttf"
im = Image.open("../drive/main.jpg").convert("RGB")
d = ImageDraw.Draw(im)
f = ImageFont.truetype(FONT, 36)
text, sp = "STEAM  ·  2027", 8
w = sum(d.textlength(c, font=f) for c in text) + sp * (len(text) - 1)
# 제목 블록 가운데(main.jpg: 제목 x=120, 폭 ≈ 770)
x = 120 + (770 - w) / 2
for c in text:
    d.text((x, 650), c, font=f, fill=(240, 208, 140))
    x += d.textlength(c, font=f) + sp
im.save("endcard.png")
print("endcard.png", im.size)
