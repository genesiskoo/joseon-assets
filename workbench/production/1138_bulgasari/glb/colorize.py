"""#1138 알베도 색만 바꾸기 — 털 결(밝기)은 Tripo 그대로, 빛깔은 지금 흑랑(#118 슬레이트)의 평균색으로. 붉은 눈은 그대로.

    python colorize.py <worktree> <in.glb> <out.glb> <ref.glb> [--lum 0.24] [--contrast 1.35]
- ref.glb 알베도의 평균색(rgb)을 빛깔로 쓴다(밝기는 따로 맞춘다).
- 밝기 L = 0.2126R + 0.7152G + 0.0722B → 평균 주변으로 contrast 배 늘리고 → 평균이 --lum 이 되게 곱 → L × (ref 색 / ref 밝기).
- 붉은 눈 = 채도 0.35↑ · 색상 빨강(345°~20°) · 밝기 0.12↑ → 원래 색 유지(가장자리 부드럽게).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "tools"))
import albedo_ops as A  # noqa: E402

src, out, ref = sys.argv[2], sys.argv[3], sys.argv[4]
args = sys.argv[5:]
lum_t = float(args[args.index("--lum") + 1]) if "--lum" in args else 0.24
k_con = float(args[args.index("--contrast") + 1]) if "--contrast" in args else 1.35

rjs, rb = A.read_glb(ref)
rimg = A.to_array(A.load_image(rjs, rb, A.base_color_image(rjs))[0])[..., :3]
ref_rgb = rimg.reshape(-1, 3).mean(axis=0)
ref_l = float(ref_rgb @ np.array([0.2126, 0.7152, 0.0722]))
tint = ref_rgb / ref_l

js, b = A.read_glb(src)
img, mime = A.load_image(js, b, A.base_color_image(js))
a = A.to_array(img)[..., :3]
L = a @ np.array([0.2126, 0.7152, 0.0722])
m = L.mean()
L2 = np.clip(m + (L - m) * k_con, 0, 1)
L2 = np.clip(L2 * (lum_t / max(1e-6, L2.mean())), 0, 1)
new = np.clip(L2[..., None] * tint[None, None, :], 0, 1)
# 붉은 눈은 그대로
mx, mn = a.max(axis=2), a.min(axis=2)
sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
r, g, bb = a[..., 0], a[..., 1], a[..., 2]
red = (r >= g) & (r >= bb) & ((r - np.maximum(g, bb)) > 0.08)
keep = np.clip((sat - 0.35) / 0.15, 0, 1) * red * (mx > 0.12)
out_rgb = new * (1 - keep[..., None]) + a * keep[..., None]
res = Image.fromarray((np.clip(out_rgb, 0, 1) * 255 + 0.5).astype(np.uint8))
binc = A.put_albedo(js, b, res)
A.write_glb(out, js, binc)
print("ref rgb %s (밝기 %.3f) · 새 밝기 평균 %.3f · 눈 유지 칸 %d" % (np.round(ref_rgb, 3), ref_l, float(L2.mean()), int((keep > 0.5).sum())))
print("->", out)
