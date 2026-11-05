"""#1138 다리 사이 막 끊기 — 한 삼각형의 세 꼭짓점 주인 뼈가 서로 다른 다리(앞 왼↔앞 오른 · 뒤 왼↔뒤 오른 · 앞↔뒤)나 다리↔꼬리면
그 삼각형을 넓이 0(같은 꼭짓점 셋)으로 바꾼다 — 색인 수 · 다른 바이트는 그대로(write_any). 긴 털이 두 다리를 이어 걷기에서 막이 늘어나던 것.

    python cut_leg_bridges.py <worktree> <in.glb> <out.glb>
"""
import sys
from pathlib import Path
import numpy as np
root = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(root / "tools"))
import quad_rig as R  # noqa: E402
from glb_pose import Glb  # noqa: E402

g = Glb.load(sys.argv[2])
S = R.glb_skin(g)
names = S["names"]
own = S["J"][np.arange(len(S["J"])), np.argmax(S["W"], axis=1)]
def limb(n):
    for k in ("FL", "FR", "BL", "BR"):
        if n.startswith(k):
            return k
    return "T" if n.startswith("Tail") else ""
L = np.array([limb(names[j]) for j in own])
F = S["F"]
lf = L[F]  # (n,3)
bad = np.zeros(len(F), bool)
for a in range(3):
    for b in range(a + 1, 3):
        x, y = lf[:, a], lf[:, b]
        legx = np.isin(x, ["FL", "FR", "BL", "BR"]); legy = np.isin(y, ["FL", "FR", "BL", "BR"])
        bad |= (legx & legy & (x != y)) | (legx & (y == "T")) | (legy & (x == "T"))
print("삼각형 %d 중 다리 사이 막 %d (%.2f%%)" % (len(F), int(bad.sum()), 100.0 * bad.mean()))
node = g.js["nodes"][S["node"]]
for pr, info in zip(g.js["meshes"][node["mesh"]]["primitives"], S["prims"]):
    if "indices" not in pr:
        continue
    idx = R.read_any(g, pr["indices"]).astype(np.int64).reshape(-1, 3)
    sel = (F[:, 0] >= info["base"]) & (F[:, 0] < info["base"] + info["n"])
    b = bad[sel]
    idx[b] = idx[b][:, :1]  # 넓이 0
    R.write_any(g, pr["indices"], idx.reshape(-1, 1))
g.save(sys.argv[3])
print("->", sys.argv[3])
