"""#1138 소품 알베도 손질 — 채도 누르기(옛 #557 반입 결과 채도에 맞춤) + (사발) 속 흰 술빛 누르기(#1078 감사 B4).
    python grade.py <작업 트리> <in.glb> <out.glb> --sat 0.40 [--bri 1.0] [--press 0.40] [--stats]
- 채도 = 픽셀 RGB 평균(가운데)에서 벌어진 만큼 × sat (Godot Image.adjust_bcs 와 같은 꼴) · 밝기 = × bri.
- press = 흰빛(밝고 채도 낮은 곳) 가면 — 밝기 0.55→0.75 · 채도 0.30→0.15 사이 부드럽게 — 를 그 밝기(0~1)로 내린다. 색조는 그대로(곱).
- 같은 크기·이름·형식(JPEG)으로 put_albedo → 임포트가 옛 텍스처 파일(<glb>_Material_001_albedo.jpg)을 그대로 덮는다.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--sat", type=float, default=1.0)
ap.add_argument("--bri", type=float, default=1.0)
ap.add_argument("--press", type=float, default=0.0)
ap.add_argument("--stats", action="store_true")
ap.add_argument("--tone", default="", help="흰빛 자리를 이 색(R,G,B 0~1)으로 — 결(밝기 흔들림)은 원래 밝기 비로 남긴다 · press 대신")
a = ap.parse_args()
sys.path.insert(0, str(Path(a.root).resolve() / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import albedo_ops as A  # noqa: E402

js, b = A.read_glb(a.src)
img, mime = A.load_image(js, b, A.base_color_image(js))
mode = img.mode
rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0


def smooth(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
mx, mn = rgb.max(axis=2), rgb.min(axis=2)
sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0.0)
white = smooth(lum, 0.55, 0.75) * (1.0 - smooth(sat, 0.15, 0.30))
if a.stats:
    print("흰빛 가면 > 0.5 = %.2f%% · 그 평균 밝기 %.3f · 전체 평균 밝기 %.3f" % (
        100.0 * float((white > 0.5).mean()), float(lum[white > 0.5].mean()) if (white > 0.5).any() else 0.0, float(lum.mean())))
if a.tone:
    tone = np.array([float(v) for v in a.tone.split(",")], dtype=np.float32)
    wl = float(lum[white > 0.5].mean()) if (white > 0.5).any() else 1.0
    tinted = tone[None, None, :] * np.clip(lum / max(wl, 1e-4), 0.0, 1.3)[..., None]
    rgb = rgb + white[..., None] * (tinted - rgb)
elif a.press > 0.0:
    k = np.where(lum > 1e-4, np.minimum(1.0, a.press / np.maximum(lum, 1e-4)), 1.0)
    rgb = rgb * (1.0 - white[..., None] * (1.0 - k[..., None]))
rgb = rgb * a.bri
center = rgb.mean(axis=2, keepdims=True)
rgb = center + (rgb - center) * a.sat
out = Image.fromarray((np.clip(rgb, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8), "RGB")
if mode != "RGB":
    out = out.convert(mode)
binc = A.put_albedo(js, b, out)
A.write_glb(a.out, js, binc)
print("손질", Path(a.out).name, "· 채도 ×%.3f · 밝기 ×%.2f · 흰빛 %s" % (a.sat, a.bri, ("→ 색 %s" % a.tone) if a.tone else (("누름 → %.2f" % a.press) if a.press else "그대로")))
