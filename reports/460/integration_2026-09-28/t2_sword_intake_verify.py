from pathlib import Path
from PIL import Image, ImageChops
import hashlib
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path("C:/workspace/joseon")
ctx = json.loads((root / "tmp/t2_sword_intake_context.json").read_text(encoding="utf-8"))
game, source, report, gallery, intake = [Path(ctx[k]) for k in ["game", "source", "report", "gallery", "intake"]]
manifest = json.loads((intake / "intake_manifest.json").read_text(encoding="utf-8"))
snapshot = json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = []
for item in manifest["files"]:
    p = game / item["destination"]
    assert sha(p) == item["sha256"] == sha(source / "game/items" / p.name), p
    im = Image.open(p)
    assert im.mode == "RGBA" and im.size == (80, 240) and im.getchannel("A").getextrema() == (0, 255), p
    before = snapshot["before_definitions"][item["definition"]]
    after = (game / item["definition"]).read_text(encoding="utf-8")
    new_path = "res://" + item["destination"]
    assert before.count(item["previous_icon"]) == after.count(new_path) == 1
    normalized_before = before.replace(item["previous_icon"], "<icon_path>", 1)
    normalized_after = after.replace(new_path, "<icon_path>", 1)
    assert normalized_before == normalized_after
    assert hashlib.sha256(normalized_after.encode()).hexdigest() == item["non_icon_fields_sha256"]
    assert sha(game / item["definition"]) == item["definition_after_sha256"]
    assert 'icon = ExtResource("2")' in after and "load_steps=3" in after
    sidecar = (game / (item["destination"] + ".import")).read_text(encoding="utf-8")
    assert "compress/mode=0" in sidecar and "mipmaps/generate=false" in sidecar and "process/size_limit=0" in sidecar
    records.append({"id": item["data_id"], "sha256": sha(p), "size": list(im.size), "alpha": list(im.getchannel("A").getextrema()), "alpha_bbox": list(im.getchannel("A").getbbox()), "non_icon_fields_preserved": True, "existing_resource_id": "2"})
assert len(records) == 4
for rel, digest in snapshot["protected_files"].items():
    assert sha(game / rel) == digest, rel
for rel, digest in snapshot["old_h1_icons"].items():
    assert sha(game / rel) == digest, rel
assert len(snapshot["protected_files"]) == 101 and len(snapshot["old_h1_icons"]) == 3
for rel in ["tests/test_items.gd", "ui/inventory_ui.gd", "ui/vendor_ui.gd", "ui/ui_skin.gd"]:
    old = subprocess.check_output(["git", "-C", str(game), "show", f"{ctx['game_base']}:{rel}"])
    current = (game / rel).read_bytes()
    assert old.replace(b"\r\n", b"\n") == current.replace(b"\r\n", b"\n"), rel

captures = {}
for mode, checks in [("before", 78), ("after", 86)]:
    meta = json.loads((report / f"captures_{mode}.json").read_text(encoding="utf-8"))
    assert meta["exit_code"] == 0 and len(meta["captures"]) == 3
    log_path, error_path = report / meta["stdout"], report / meta["stderr"]
    log = log_path.read_text(encoding="utf-8-sig")
    assert f"E2E icon_intake PASS (검사 {checks})" in log and "E2E SUMMARY: 1/1 PASS" in log
    assert not error_path.read_text(encoding="utf-8-sig").strip()
    assert "SCRIPT ERROR" not in log and "\nERROR:" not in log
    for index, row in enumerate(meta["captures"], 1):
        assert Path(row["source"]).name == f"icon_intake_{index:02d}_{row['state']}.png"
        p = report / f"{row['state']}_{mode}.png"
        assert sha(p) == row["sha256"] and row["mtime"] >= meta["started"]
        assert Image.open(p).size == (1280, 720)
        jpg = gallery / f"{row['state']}_{mode}.jpg"
        assert jpg.stat().st_size == row["jpg_bytes"] <= 300_000
        assert jpg.read_bytes() == (report / jpg.name).read_bytes()
    captures[mode] = {"checks": checks, "metadata": meta, "stdout_sha256": sha(log_path), "stderr_sha256": sha(error_path)}

before_im = Image.open(report / "sword_inventory_before.png").convert("RGB")
after_im = Image.open(report / "sword_inventory_after.png").convert("RGB")
anchors = {"hwando": (1064, 320, 1104, 440), "yedo": (1104, 320, 1144, 440), "leather_shoes": (1184, 320, 1264, 400)}
anchor_records = []
for name, rect in anchors.items():
    identical = ImageChops.difference(before_im.crop(rect), after_im.crop(rect)).getbbox() is None
    assert identical, name
    anchor_records.append({"id": name, "rect": list(rect), "pixels_identical": True})
photos = []
for p in sorted(gallery.glob("*.jpg")):
    assert Image.open(p).size == (1280, 720) and p.stat().st_size <= 300_000
    photos.append({"file": p.name, "bytes": p.stat().st_size, "sha256": sha(p), "size": [1280, 720]})
assert len(photos) == 6 and sum(p["bytes"] for p in photos) <= 2_000_000
import_meta = json.loads((report / "run_import.json").read_text(encoding="utf-8"))
assert import_meta["exit_code"] == 0
assert sha(report / import_meta["raw_log"]) == import_meta["raw_sha256"]
import_log = (report / import_meta["raw_log"]).read_text(encoding="utf-8-sig")
assert "SCRIPT ERROR" not in import_log and "\nERROR:" not in import_log
failed = [p.name for p in report.glob("460_before_*.log") if "E2E icon_intake FAIL" in p.read_text(encoding="utf-8-sig", errors="replace")]
assert len(failed) == 1 and (report / "failed_before_first_frame.png").exists()
output = {"issue": 460, "approval": ctx["approval"], "source_commit": ctx["source_commit"], "game_base": ctx["game_base"], "files": records, "protected_files_count": 101, "other_tres": 63, "previous_png": 38, "old_h1_icons_count": 3, "protected_files": snapshot["protected_files"], "old_h1_icons": snapshot["old_h1_icons"], "test_items_and_renderer_unchanged": True, "approved_anchor_pixels": anchor_records, "gallery": photos, "captures": captures, "engine": "Godot 4.7.2 stable Steam / Forward+ / Vulkan / RTX4070", "input": "actual marked mouse/key events: 1x3 last-cell pick/place, four equip/swap/unequip, two-handed offhand block/restore, four vendor buys/sells and exact price/same-instance preservation, four loot_dropped to Alt floor-label click and inventory recovery", "production_changes": "approved PNG4 and existing Texture2D path4 only; no runtime UI, balance, equipment/shop/drop or floor-model changes", "fixture_initial_failure": {"stdout": failed[0], "frame": "failed_before_first_frame.png", "cause": "Test expected the swapped weapon's old cell even though the offhand had already claimed it, and used a nonexistent message field; fixture corrected to auto-placement (4,0) and bag.get('_msg'). No product code changed."}, "runs": {"import": import_meta}}
(report / "intake_manifest.json").write_bytes((intake / "intake_manifest.json").read_bytes())
(report / "verification.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print("PASS #460: approved SHA/RGBA4; icon-only fields4; other63tres/38PNG +H1PNG3; renderer/test_items unchanged; real input78/86; exact anchor pixels3; photos6 within limits.")
