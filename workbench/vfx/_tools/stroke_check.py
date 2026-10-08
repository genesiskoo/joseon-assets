"""stroke_check.py — 「획 단위로 써지는가」를 숫자로 가린다 (#231).

붓글씨 쓰기 영상(검은 바탕 흰 먹, 끝 프레임 = 완성 글자)에서 프레임마다:
  cover = 완성 글자 자리 중 먹이 앉은(밝기 > 0.5) 비율
  mean  = 완성 글자 자리의 평균 밝기
  split = 완성 글자 자리 밝기의 흩어짐(표준편차) — **획으로 쓰면** 이미 쓴 곳 ≈1·안 쓴 곳 ≈0 이라 크고(≥0.35),
          **스르르 나타나면**(크로스페이드) 전부 같이 밝아져 작다(≤0.2)
  stray = 글자 밖에 생긴 먹(손·붓·번짐) 비율
판정 = mean이 0.3~0.7인 구간의 split 최댓값 (쓰기 지수). 0.35 넘으면 「쓴다」.

python stroke_check.py --src clip.mp4 --out contact.png [--cols 10]
"""
import argparse
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "C:/Windows/Fonts/malgun.ttf"


def frames_of(src):
    d = tempfile.mkdtemp(prefix="stroke_")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, os.path.join(d, "f_%04d.png")], check=True)
    fs = sorted(f for f in os.listdir(d) if f.endswith(".png"))
    return [np.asarray(Image.open(os.path.join(d, f)).convert("L"), np.float32) / 255.0 for f in fs]


def key(g):
    return np.clip((g - 0.12) / 0.7, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=10)
    a = ap.parse_args()
    fr = frames_of(a.src)
    alpha = [key(g) for g in fr]
    final = alpha[-1]
    M = final > 0.5
    if M.sum() < 10:
        M = alpha[int(len(alpha) * 0.8)] > 0.5
    rows = []
    for i, al in enumerate(alpha):
        inside = al[M]
        rows.append({
            "i": i,
            "cover": float((inside > 0.5).mean()),
            "mean": float(inside.mean()),
            "split": float(inside.std()),
            "stray": float((al[~M] > 0.3).mean()),
        })
    mid = [r for r in rows if 0.3 <= r["mean"] <= 0.7]
    wscore = max((r["split"] for r in mid), default=0.0)
    first_full = next((r["i"] for r in rows if r["cover"] > 0.9), len(rows) - 1)
    first_ink = next((r["i"] for r in rows if r["cover"] > 0.03), 0)
    # 대조표: 프레임 격자 + 곡선
    n = len(fr)
    step = max(1, n // (a.cols * 3))
    pick = list(range(0, n, step))
    cell = 120
    cols = a.cols
    rws = (len(pick) + cols - 1) // cols
    W, H = cols * (cell + 4) + 4, rws * (cell + 20) + 160
    sheet = Image.new("RGB", (W, H), (22, 21, 20))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(FONT, 13)
    for k, i in enumerate(pick):
        r, c = divmod(k, cols)
        im = Image.fromarray((fr[i] * 255).astype(np.uint8)).resize((cell, cell))
        x, y = 4 + c * (cell + 4), 4 + r * (cell + 20)
        sheet.paste(im.convert("RGB"), (x, y))
        d.text((x + 2, y + cell + 2), "%d  %.0f%%" % (i, rows[i]["cover"] * 100), font=f, fill=(210, 200, 180))
    gy = rws * (cell + 20) + 20
    gh = 110
    d.rectangle((4, gy, W - 4, gy + gh), outline=(70, 66, 60))
    for key_, col in (("cover", (240, 190, 90)), ("mean", (120, 170, 255)), ("split", (230, 90, 70))):
        pts = [(4 + (W - 8) * r["i"] / max(1, n - 1), gy + gh - gh * min(1.0, r[key_] * (2 if key_ == "split" else 1))) for r in rows]
        d.line(pts, fill=col, width=2)
    d.text((8, gy + gh + 6), "%s  frames=%d  쓰기지수(split 최대)=%.2f  첫 먹 %d · 완성 %d · 글자 밖 먹 최대 %.1f%%   [주황 cover · 파랑 mean · 빨강 split×2]" % (
        os.path.basename(a.src), n, wscore, first_ink, first_full, 100 * max(r["stray"] for r in rows)), font=f, fill=(230, 220, 200))
    sheet.save(a.out)
    print("STROKE_OK %s frames=%d write=%.2f first_ink=%d full=%d stray_max=%.3f" % (os.path.basename(a.src), n, wscore, first_ink, first_full, max(r["stray"] for r in rows)))


if __name__ == "__main__":
    main()
