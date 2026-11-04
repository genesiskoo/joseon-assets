"""GLB 미리보기 네 장(앞 · 옆 · 뒤 · 게임 각도) — albedo_ops.render_flat 그대로 (창 없음).

    python preview4.py <worktree> <glb> <out.png>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "tools"))
import albedo_ops as A  # noqa: E402

js, binc = A.read_glb(sys.argv[2])
img_i = A.base_color_image(js)
tex = A.to_array(A.load_image(js, binc, img_i)[0])
parts = A.surfaces(js, binc, img_i)
views = [(0.0, 0.0), (90.0, 0.0), (180.0, 0.0), (-45.0, 35.264)]
tiles = [A.render_flat(parts, tex, A._rot(y, p), (420, 420)) for y, p in views]
Image.fromarray((np.clip(np.hstack(tiles), 0, 1) * 255).astype(np.uint8)).save(sys.argv[3])
print("->", sys.argv[3])
