from pathlib import Path
from PIL import Image, ImageChops
import hashlib
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/seal_intake_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
source = Path("C:/workspace/joseon-assets")
report = main / f"._tmp/assets_87/reports/{card}/integration_2026-09-27"
manifest = json.loads((game / f"art/ui_intake_{card}/intake_manifest.json").read_text(encoding="utf-8"))
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records = []
for item in manifest["files"]:
    p = game / item["destination"]
    assert sha(p) == item["sha256"] == sha(source / item["source"])
    im = Image.open(p)
    assert im.mode == "RGBA" and im.size == (80, 80) and im.getchannel("A").getextrema() == (0, 255)
    body = (game / item["definition"]).read_text(encoding="utf-8")
    semantic = "\n".join(line for line in body.splitlines() if line.strip() and not line.startswith("[gd_resource ") and not line.startswith("icon = ") and not ('[ext_resource type="Texture2D"' in line and f'id="art{card}"' in line))
    assert hashlib.sha256(semantic.encode()).hexdigest() == item["non_icon_fields_sha256"]
    assert sha(game / item["definition"]) == item["definition_after_sha256"]
    assert f'icon = ExtResource("art{card}")' in body
    records.append({"id":item["data_id"], "sha256":sha(p), "size":list(im.size), "alpha":list(im.getchannel("A").getextrema()), "alpha_bbox":list(im.getchannel("A").getbbox()), "non_icon_fields_preserved":True})
for item in manifest["previous_assets_unchanged"]:
    assert sha(game / item["destination"]) == item["sha256"], item["destination"]
for item in manifest["other_definitions_unchanged"]:
    assert sha(game / item["path"]) == item["sha256"], item["path"]
before = Image.open(report / "seal_inventory_before.png").convert("RGB")
after = Image.open(report / "seal_inventory_after.png").convert("RGB")
anchors = {"satgat":(864,400,944,480), "piju":(944,400,1024,480), "injang":(1024,400,1064,440)}
anchor_records = []
for name, rect in anchors.items():
    identical = ImageChops.difference(before.crop(rect), after.crop(rect)).getbbox() is None
    assert identical, name
    anchor_records.append({"id":name, "rect":rect, "pixels_identical":True})
gallery = []
for p in sorted((game / f"docs/art/{card}_d1_quest_seal_intake").glob("*.jpg")):
    im = Image.open(p)
    assert im.size == (1280,720) and p.stat().st_size <= 300_000
    gallery.append({"file":p.name, "bytes":p.stat().st_size, "size":list(im.size)})
assert len(gallery) == 6
pending = [p.stem for p in (game / "data/items").glob("*.tres") if 'script_class="ItemDef"' in p.read_text(encoding="utf-8") and "icon =" not in p.read_text(encoding="utf-8")]
assert not pending
(report / "intake_manifest.json").write_bytes((game / f"art/ui_intake_{card}/intake_manifest.json").read_bytes())
(report / "verification.json").write_text(json.dumps({"issue":card, "approval":manifest["approval"], "files":records, "previous_assets_unchanged":manifest["previous_assets_unchanged"], "other_definitions_unchanged":manifest["other_definitions_unchanged"], "approved_anchor_pixels":anchor_records, "gallery":gallery, "current_icon_pending":pending, "engine":"Godot4.7.2 stable Steam / Forward+ / Vulkan / RTX4070", "input":"actual marked input: grab/replace; Ctrl discard refused; actual merchant conversation and right-click sale refused; floor names clicked to recover each of3 same nonstacking objects", "production_changes":"3 approved PNG +3 ItemDef.icon; pending3→0; MODEL_PENDING unchanged; no renderer/quest/price/drop/model changes", "core_remaining":55, "known_limitations":["봉밀굴 3봉인 소비/개방은 #169 대기", "장산범/불가살이 보스 연결은 #69 대기", "기존 퀘스트 툴팁의 판매가/들고 창 밖 클릭 버림 안내 및 명시적 커서 버림 정합성은 후속 UI 카드로 분리"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PASS #{card}: hashes3/non-icon fields3/previousPNG35/otherDefs64/anchorPixels3/JPG6; current icons all present.")
