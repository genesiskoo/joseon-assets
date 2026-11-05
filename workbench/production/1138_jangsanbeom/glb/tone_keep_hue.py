"""#1138 알베도 어둡게 — Tripo 빛깔(분홍 코 · 녹슨 가시)은 살리고 밝기·대비만 옛 몸에 맞춘 뒤 옛 몸 평균색을 일부 섞는다.

    python tone_keep_hue.py <worktree> <in.glb> <out.glb> <ref.glb> [--lum 0.146] [--contrast 2.0] [--sat 1.6] [--mix 0.4]
- L(밝기) = 0.2126R+0.7152G+0.0722B → 평균 주변 contrast 배 → 평균 = --lum.  rgb × (L'/L) = 빛깔 그대로 밝기만.
- 채도 × --sat(밝기 축 둘레) · 옛 몸 평균색(L' × ref/ref밝기)을 --mix 만큼 섞는다.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
root = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(root / "tools"))
import albedo_ops as A  # noqa: E402
src, out, ref = sys.argv[2], sys.argv[3], sys.argv[4]
a = sys.argv[5:]
opt = lambda k, d: float(a[a.index(k) + 1]) if k in a else d
lum_t, k_con, k_sat, mix = opt("--lum", 0.146), opt("--contrast", 2.0), opt("--sat", 1.6), opt("--mix", 0.4)
rjs, rb = A.read_glb(ref)
r = A.to_array(A.load_image(rjs, rb, A.base_color_image(rjs))[0])[..., :3].astype(np.float64)
ref_rgb = r.reshape(-1, 3).mean(0); ref_l = float(ref_rgb @ [0.2126, 0.7152, 0.0722])
js, b = A.read_glb(src)
img, mime = A.load_image(js, b, A.base_color_image(js))
rgb = A.to_array(img)[..., :3].astype(np.float64)
L = rgb @ np.array([0.2126, 0.7152, 0.0722])
m = L.mean()
L2 = np.clip(m + (L - m) * k_con, 0.0, None)
L2 *= lum_t / max(L2.mean(), 1e-6)
rgb2 = rgb * (L2 / np.maximum(L, 1e-4))[..., None]
rgb2 = L2[..., None] + (rgb2 - L2[..., None]) * k_sat
tint = L2[..., None] * (ref_rgb / max(ref_l, 1e-6))
rgb3 = np.clip(rgb2 * (1 - mix) + tint * mix, 0, 1)
res = Image.fromarray((rgb3 * 255 + 0.5).astype(np.uint8))
binc = A.put_albedo(js, b, res)
A.write_glb(out, js, binc)
print("ref rgb", np.round(ref_rgb, 3), "lum %.3f" % ref_l, "| new lum %.3f" % float((rgb3 @ [0.2126, 0.7152, 0.0722]).mean()))
