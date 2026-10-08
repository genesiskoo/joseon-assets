"""stroke_sprite.py — 붓글씨 쓰기 영상 → 쓰는 구간 N장 스프라이트 프레임 (#231).

첫 먹(글자 자리 먹 3%)부터 완성(97%)까지를 N장으로 고르고, 완성 뒤 한 장을 더해 끝을 붙잡는다.
출력 = 검은 바탕 흰 먹 RGB 프레임 f_00.png… (intake_vfx.ps1 -Src <폴더> 입구) + 한 줄 띠(검토용).

python stroke_sprite.py --src clip.mp4 --out <폴더> [--n 14] [--full 0.97] [--ease 1.0]
"""
import argparse
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image


def frames_of(src):
    d = tempfile.mkdtemp(prefix="sprite_")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, os.path.join(d, "f_%04d.png")], check=True)
    fs = sorted(f for f in os.listdir(d) if f.endswith(".png"))
    out = [np.asarray(Image.open(os.path.join(d, f)).convert("L"), np.float32) / 255.0 for f in fs]
    shutil.rmtree(d, ignore_errors=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--full", type=float, default=0.97)
    ap.add_argument("--ease", type=float, default=1.0)
    ap.add_argument("--by", choices=("time", "cover"), default="time",
                    help="time = 쓰는 구간을 시간으로 고르게 · cover = 먹이 찬 양으로 고르게(획 사이 멈춤을 건너뛴다 — Seedance)")
    a = ap.parse_args()
    fr = frames_of(a.src)
    alpha = [np.clip((g - 0.12) / 0.7, 0, 1) for g in fr]
    M = alpha[-1] > 0.5
    cover = [float((al[M] > 0.5).mean()) for al in alpha]
    i0 = max(0, next((i for i, c in enumerate(cover) if c > 0.03), 0) - 1)
    i1 = next((i for i, c in enumerate(cover) if c >= a.full), len(fr) - 1)
    idx = []
    for k in range(a.n):
        u = (k / (a.n - 1)) ** a.ease
        if a.by == "cover":
            target = cover[i0] + u * (cover[i1] - cover[i0])
            idx.append(next((i for i in range(i0, i1 + 1) if cover[i] >= target - 1e-6), i1))
        else:
            idx.append(int(round(i0 + u * (i1 - i0))))
    idx.append(min(len(fr) - 1, i1 + 3))                   # 완성 뒤 한 장 (먹이 가라앉은 끝)
    os.makedirs(a.out, exist_ok=True)
    for f in os.listdir(a.out):
        if f.startswith("f_") and f.endswith(".png"):
            os.remove(os.path.join(a.out, f))
    for k, i in enumerate(idx):
        g = (alpha[i] * 255).astype(np.uint8)
        Image.fromarray(np.stack([g, g, g], -1)).save(os.path.join(a.out, "f_%02d.png" % k))
    cell = 96
    strip = Image.new("L", (len(idx) * (cell + 2), cell), 30)
    for k, i in enumerate(idx):
        strip.paste(Image.fromarray((alpha[i] * 255).astype(np.uint8)).resize((cell, cell)), (k * (cell + 2), 0))
    strip.save(os.path.join(a.out, "_strip.png"))
    print("SPRITE_OK %s frames=%d pick=%s cover=%s" % (os.path.basename(a.src), len(idx), idx, [round(cover[i], 2) for i in idx]))


if __name__ == "__main__":
    main()
