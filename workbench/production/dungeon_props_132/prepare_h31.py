"""Non-destructive runtime preparation of approved Comfy H3.1 props.

Run with --game-tools C:/workspace/joseon/tools; raw Cloud outputs stay in reports/132.
Only root scale/pivot, matte material metadata and texture resolution are changed.
"""
import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[2]
REPORT = ASSETS / "reports/132/comfy_h31"
PROFILE = {
    "bone_heap": (0, 1.5), "roots": (1, 1.6), "nest": (0, 1.4),
    "palisade": (1, 1.7), "seal_stone": (0, 1.8),
    "pillar": (1, 2.0), "broken_statue": (1, 1.3),
}
PREP_VERSION = 2
FLAT_LIMITS = {"bone_heap": (1.5, 0.5, 1.0), "nest": (1.4, 0.4, 1.2),
               "seal_stone": (1.8, 0.25, 1.8)}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def bounds(ops, document, blob):
    points = []
    worlds = ops._node_worlds(document)
    for i, node in enumerate(document.get("nodes", [])):
        if "mesh" not in node:
            continue
        if "skin" in node:
            raise RuntimeError("A static prop unexpectedly contains a skin")
        for primitive in document["meshes"][node["mesh"]]["primitives"]:
            p = ops.accessor(document, blob, primitive["attributes"]["POSITION"])
            m = worlds[i]
            points.append(p @ m[:3, :3].T + m[:3, 3])
    p = np.concatenate(points)
    return p.min(0), p.max(0)

def triangle_count(document):
    return sum(document["accessors"][pr["indices"] if "indices" in pr else pr["attributes"]["POSITION"]]["count"] // 3
               for mesh in document.get("meshes", []) for pr in mesh["primitives"])

def prepare(ops, asset):
    raw = REPORT / f"{asset}_h31_raw_v1.glb"
    if not raw.exists():
        raw = REPORT / f"{asset}_h31_raw_v2.glb"
    if not raw.exists():
        print(f"{asset}: Cloud output not collected yet")
        return
    final = HERE / "models" / f"{asset}.glb"
    evidence = REPORT / f"{asset}_runtime_v{PREP_VERSION}.json"
    if final.exists() and evidence.exists():
        saved = json.loads(evidence.read_text(encoding="utf-8"))
        if sha(raw) == saved["source_sha256"] and sha(final) == saved["output_sha256"]:
            print(f"{asset}: already prepared; SHA unchanged")
            return
        raise RuntimeError(f"Existing delivery differs; refusing to overwrite {asset}")
    original_sha = sha(raw)
    document, blob = ops.read_glb(str(raw))
    if document.get("skins") or document.get("animations"):
        raise RuntimeError("Static prop must have neither skins nor animation")
    lo, hi = bounds(ops, document, blob)
    axis, target = PROFILE[asset]
    # Tripo H3.1 returns X-forward. A -90 degree Y turn gives the project's -Z front.
    rotation = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]], dtype=float)
    rotated_dims = (hi - lo)[[2, 1, 0]]
    scale = target / float(rotated_dims[axis])
    if asset in FLAT_LIMITS:
        scale = min(limit / float(span) for limit, span in zip(FLAT_LIMITS[asset], rotated_dims))
    elif asset == "palisade":
        scale = min(scale, 1.8 / float(rotated_dims[0]))
    center = (lo + hi) / 2
    matrix = np.eye(4)
    matrix[:3, :3] = rotation * scale
    rotated_center = rotation @ center
    matrix[:3, 3] = [-rotated_center[0] * scale, -lo[1] * scale, -rotated_center[2] * scale]
    # Uniform scale retains the approved silhouette; height/footprint are reported exactly.
    scene = document["scenes"][document.get("scene", 0)]
    index = len(document["nodes"])
    document["nodes"].append({"name": asset + "_ground_pivot", "matrix": matrix.T.reshape(-1).tolist(),
                              "children": list(scene["nodes"])})
    scene["nodes"] = [index]
    for material in document.get("materials", []):
        pbr = material.setdefault("pbrMetallicRoughness", {})
        pbr["metallicFactor"] = 0.0
        pbr["roughnessFactor"] = 1.0
        material["emissiveFactor"] = [0, 0, 0]
        material.pop("emissiveTexture", None)
        for extension in ("KHR_materials_specular", "KHR_materials_ior", "KHR_materials_emissive_strength"):
            material.get("extensions", {}).pop(extension, None)
    for key in ("extensionsUsed", "extensionsRequired"):
        if key in document:
            document[key] = [x for x in document[key] if x not in
                             ("KHR_materials_specular", "KHR_materials_ior", "KHR_materials_emissive_strength")]
    textures = []
    for i, entry in enumerate(document.get("images", [])):
        picture, mime = ops.load_image(document, blob, i)
        before = list(picture.size)
        if max(picture.size) > 1024:
            picture.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            blob = ops.replace_view(document, blob, entry["bufferView"], ops.encode_image(picture, mime))
        textures.append({"index": i, "before": before, "after": list(picture.size)})
    final.parent.mkdir(parents=True, exist_ok=True)
    if final.exists():
        preserved = REPORT / "runtime_prior_v1" / final.name
        preserved.parent.mkdir(parents=True, exist_ok=True)
        if not preserved.exists():
            shutil.copyfile(final, preserved)
    ops.write_glb(str(final), document, blob)
    check_document, check_blob = ops.read_glb(str(final))
    new_lo, new_hi = bounds(ops, check_document, check_blob)
    if abs(float(new_lo[1])) > 1e-5 or np.max(np.abs(((new_lo + new_hi) / 2)[[0, 2]])) > 1e-5:
        raise RuntimeError("Prepared prop is not grounded or centered")
    if triangle_count(check_document) > 10000:
        raise RuntimeError("Prop exceeds 10k triangle budget")
    if original_sha != sha(raw):
        raise RuntimeError("Raw Cloud GLB was modified")
    result = {"asset": asset, "source": raw.name, "source_sha256": original_sha,
              "output": str(final.relative_to(ASSETS)).replace("\\", "/"), "output_sha256": sha(final),
              "triangles": triangle_count(check_document), "raw_bounds": [lo.tolist(), hi.tolist()],
              "scale": scale, "target_axis_xyz": axis, "target_axis_metres": target,
              "preparation_revision": PREP_VERSION, "yaw_rotation_degrees": -90,
              "bounds_min": new_lo.tolist(), "bounds_max": new_hi.tolist(),
              "dimensions_xyz": (new_hi - new_lo).tolist(), "textures": textures,
              "material": {"metallic": 0.0, "roughness": 1.0, "emission": 0.0},
              "raw_preserved": True, "game_intake": False}
    evidence.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ops.preview(check_document, check_blob).save(REPORT / f"{asset}_runtime_preview.png")
    print(f"{asset}: {result['triangles']} tris, dimensions {result['dimensions_xyz']}, grounded, 1K, matte")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-tools", type=Path, required=True)
    parser.add_argument("assets", nargs="*", default=list(PROFILE))
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("asset_albedo_ops", args.game_tools / "albedo_ops.py")
    ops = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ops)
    for asset in args.assets:
        if asset not in PROFILE:
            raise ValueError(asset)
        prepare(ops, asset)
