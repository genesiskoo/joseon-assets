"""label_sheet.py — 이미지 여러 장을 이름표 달린 격자 한 장으로 (검토용).

python label_sheet.py --out sheet.png --cols 6 --cell 256 [--title 제목] 경로=이름표 경로=이름표 …
"""
import argparse

from PIL import Image, ImageDraw, ImageFont

FONT = "C:/Windows/Fonts/malgun.ttf"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--cell", type=int, default=256)
    ap.add_argument("--title", default="")
    ap.add_argument("items", nargs="+")
    a = ap.parse_args()
    font = ImageFont.truetype(FONT, 18)
    tfont = ImageFont.truetype(FONT, 24)
    pad, lab = 8, 28
    rows = (len(a.items) + a.cols - 1) // a.cols
    top = 44 if a.title else 0
    W = a.cols * (a.cell + pad) + pad
    H = top + rows * (a.cell + lab + pad) + pad
    sheet = Image.new("RGB", (W, H), (38, 36, 34))
    d = ImageDraw.Draw(sheet)
    if a.title:
        d.text((pad + 4, 10), a.title, font=tfont, fill=(235, 225, 205))
    for i, item in enumerate(a.items):
        path, _, label = item.partition("=")
        im = Image.open(path).convert("RGB")
        im.thumbnail((a.cell, a.cell))
        r, c = divmod(i, a.cols)
        x = pad + c * (a.cell + pad)
        y = top + pad + r * (a.cell + lab + pad)
        sheet.paste(im, (x + (a.cell - im.width) // 2, y + (a.cell - im.height) // 2))
        d.text((x + 4, y + a.cell + 3), label or path.split("/")[-1], font=font, fill=(220, 210, 190))
    sheet.save(a.out)
    print("SHEET_OK", a.out, sheet.size)


if __name__ == "__main__":
    main()
