"""#1138 ModelDef 값 = quad_gait bake 와 같은 계산(ground_speed)을 굽기 없이 — python md_measure.py <worktree> <glb> <scale>"""
import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "tools"))
import quad_gait as Q  # noqa: E402
g = Q.Glb.load(sys.argv[2]); sc = float(sys.argv[3])
sp = {}
for clip in ("walk", "run"):
    V, td = Q.ground_speed(g, clip)
    sp[clip] = {"v": round(V, 4), "touch": td}
md = {"walk_speed": round(sp["walk"]["v"] * sc, 3), "run_speed": round(sp["run"]["v"] * sc, 3),
      "step_phases": {"walk": [sp["walk"]["touch"]["FL"], sp["walk"]["touch"]["FR"]],
                      "run": [round((sp["run"]["touch"]["BL"] + sp["run"]["touch"]["BR"]) / 2, 3), round((sp["run"]["touch"]["FR"] + sp["run"]["touch"]["FL"]) / 2, 3)]},
      "ground_model_u_s": [sp["walk"]["v"], sp["run"]["v"]]}
print(json.dumps(md, ensure_ascii=False))
