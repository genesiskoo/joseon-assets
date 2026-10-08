from pathlib import Path
from PIL import Image, ImageChops
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
ctx = json.loads((main / "tmp/quest_guard_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
report = main / f"._tmp/assets_87/reports/{card}/integration_2026-09-27"
gallery = game / f"docs/art/{card}_quest_item_safety"
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fixture = game / "tests/e2e/scenarios/icon_intake.gd"
fixture.write_text(fixture.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8", newline="\n")
snapshot = json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))
for name, value in snapshot["files"].items():
    assert sha(game / name) == value, name
assert len(snapshot["files"]) == 105
records = []
for p in sorted(gallery.glob("*.jpg")):
    im = Image.open(p)
    assert im.size == (1280, 720) and p.stat().st_size <= 300_000
    records.append({"file":p.name, "bytes":p.stat().st_size, "size":list(im.size), "sha256":sha(p)})
assert len(records) == 6
anchors = {"satgat":(864,400,944,480), "piju":(944,400,1024,480), "injang":(1024,400,1064,440)}
pixels = []
for shot in ["seal_inventory", "seal_vendor_refused", "seal_drop_recovered"]:
    before = Image.open(report / f"{shot}_before.png").convert("RGB")
    after = Image.open(report / f"{shot}_after.png").convert("RGB")
    for name, rect in anchors.items():
        same = ImageChops.difference(before.crop(rect), after.crop(rect)).getbbox() is None
        assert same, (shot, name)
        pixels.append({"shot":shot, "item":name, "rect":rect, "identical":True})
captures = {}
for mode in ["before", "after"]:
    meta = json.loads((report / f"captures_{mode}.json").read_text(encoding="utf-8"))
    body = (report / meta["stdout"]).read_text(encoding="utf-8-sig")
    assert not (report / meta["stderr"]).read_text(encoding="utf-8-sig").strip()
    assert meta["exit_code"] == 0 and "E2E SUMMARY: 1/1 PASS" in body
    n = int(re.search(r"E2E icon_intake PASS \(검사 (\d+)\)", body).group(1))
    assert n == {"before":70,"after":76}[mode]
    captures[mode] = {"checks":n, "stderr_errors":0, "meta":meta}
data = {"issue":card, "protected_definitions":67, "protected_png":38, "protected_file_count":105, "asset_bytes_unchanged":True, "anchor_pixels":pixels, "gallery":records, "actual_windowed":captures, "input":"real marked pointer/click/key events; quest3 outside discard refusal and replace; Ctrl discard and sale refusal; normal3 potion explicit discard; full bag close drops same quest to floor and real Alt name-label pickup recovers it", "scope":"two UI files and existing regression fixtures; item data/PNG/price rules unchanged", "known_limitations":["봉밀굴 봉인 소비/개방 #169 대기", "수하 보스 장산범/불가살이 #69 대기"], "main_landed":False}
(report / "verification.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PASS #{card}: protected105, identical anchor regions9, JPG6 <=300KB, real input before70/after76, stderr0.")
