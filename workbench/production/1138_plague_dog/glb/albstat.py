"""알베도 통계 — python albstat.py <worktree> <glb>..."""
import sys
from pathlib import Path
import numpy as np
root = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(root / "tools"))
import albedo_ops as A  # noqa: E402
for p in sys.argv[2:]:
    js, b = A.read_glb(p)
    im = A.to_array(A.load_image(js, b, A.base_color_image(js))[0])[..., :3].astype(np.float64)
    if im.max() > 1.5: im /= 255.0
    L = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
    mx = im.max(axis=2); mn = im.min(axis=2); sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
    print(Path(p).name, "lum %.3f sat %.3f rgb %s std %.3f" % (L.mean(), sat.mean(), np.round(im.reshape(-1, 3).mean(0), 3).tolist(), L.std()))
