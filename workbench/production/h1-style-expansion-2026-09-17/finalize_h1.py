import hashlib
import json
import pathlib
import shutil

root = pathlib.Path(r"C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17")
scratch = pathlib.Path(r"C:/workspace/joseon/tmp/h1_artwork_build")
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8-sig"))
module_manifest = json.loads((root / "3d_modules/manifest.json").read_text(encoding="utf-8-sig"))
images = json.loads((root / "delivery_check.json").read_text(encoding="utf-8-sig"))
links = json.loads((root / "html_validation.json").read_text(encoding="utf-8-sig"))
models = []
for item in module_manifest["assets"]:
    relative = "3d_modules/" + item["file"]
    path = root / relative
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest.lower() == item["sha256"].lower(), relative
    models.append({"file": relative, "sha256": digest, "manifest_hash_matches": True})
assert len(models) == 18
for name in ("H1_doho.glb", "H1_merchant.glb"):
    relative = "3d_trial/" + name
    digest = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    if name == "H1_doho.glb":
        assert digest.upper() == "E5FEA5C6383180D1369D5F1975F804C4F3A2DD70A608918E26593D94C2511749"
    models.append({"file": relative, "sha256": digest})
assert images["active_images"] == 23 and images["superseded_images"] == 6
assert all(x["exists"] and x["sha256_matches"] for x in images["image_checks"])
assert not links["missing"]
for name in ("README.md", "build_gallery.py", "check_gallery.py", "finalize_h1.py", "browser_qa.json"):
    shutil.copyfile(scratch / name, root / name)
summary = {
    "date": "2026-09-17",
    "status": "Reviewable H1 art production; final game intake incomplete",
    "latest_images_including_material": 23,
    "superseded_images": 6,
    "canonical_glb_candidates": models,
    "canonical_glb_count": len(models),
    "enemy_glb_count": 0,
    "enemy_meshy_credits_used": 0,
    "actor_trial_meshy_credits_used": 80,
    "enemy_transfer": "Awaiting explicit user approval after automatic approval review rejection: four concept images to Meshy, four generations, up to 120 credits",
    "original_png_hashes_match": True,
    "html_missing_links": 0,
    "game_intake_performed": False,
    "remaining_qa": [
        "Hand-tip shape and cloth overlap",
        "Merchant identity/height and triangle budget",
        "Actor and inherited stair textures 2K and material atlas 1254-square exceed 1K contract",
        "Environment seamless tiling, game collision, navigation and occlusion integration",
        "Doho hit/die and enemy generation/rigging/animation"
    ]
}
(root / "delivery_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"latest_images": 23, "superseded_images": 6, "canonical_glb_candidates": len(models), "hash_and_link_checks": "PASS", "enemy_transfer": "approval_pending"}, ensure_ascii=False))
