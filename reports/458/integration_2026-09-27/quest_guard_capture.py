from pathlib import Path
from PIL import Image
import hashlib
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/quest_guard_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
mode = sys.argv[1]
assert mode in ["before", "after"]
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
report = main / f"._tmp/assets_87/reports/{card}/integration_2026-09-27"
gallery = game / f"docs/art/{card}_quest_item_safety"
gallery.mkdir(parents=True, exist_ok=True)
user = Path("C:/Users/FORYOUCOM/AppData/Roaming/Godot/app_userdata/Joseon Hunters/wt/codex-87-ui-wood-skin/e2e")
args = ["C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe", "--path", str(game), "--windowed", "--resolution", "1280x720", "--", "--e2e=icon_intake", "--e2e-shots", "--icon-intake-seal-only"]
if mode == "before":
    args.append("--quest-safety-before")
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
stamp = time.strftime("%H%M%S")
out, err = report / f"{card}_{mode}_{stamp}.log", report / f"{card}_{mode}_{stamp}_errors.log"
started = time.time()
with out.open("wb") as stdout, err.open("wb") as stderr:
    proc = subprocess.run(args, cwd=game, stdout=stdout, stderr=stderr, startupinfo=startup, timeout=180)
body = out.read_text(encoding="utf-8-sig", errors="replace")
errors = err.read_text(encoding="utf-8-sig", errors="replace")
print(body, end="")
if errors:
    print(errors, end="")
assert proc.returncode == 0 and "E2E SUMMARY: 1/1 PASS" in body and not errors.strip(), "Capture failed; raw logs preserved above."
records = []
for index, state in enumerate(["seal_inventory", "seal_vendor_refused", "seal_drop_recovered"], 1):
    source = user / f"icon_intake_{index:02d}_{state}.png"
    assert source.exists() and source.stat().st_mtime >= started
    raw = report / f"{state}_{mode}.png"
    raw.write_bytes(source.read_bytes())
    im = Image.open(raw).convert("RGB")
    assert im.size == (1280, 720)
    jpg = gallery / f"{state}_{mode}.jpg"
    im.save(jpg, quality=85, optimize=True)
    assert jpg.stat().st_size <= 300_000
    (report / jpg.name).write_bytes(jpg.read_bytes())
    records.append({"state":state, "source":source.as_posix(), "mtime":source.stat().st_mtime, "sha256":hashlib.sha256(raw.read_bytes()).hexdigest(), "size":list(im.size), "jpg_bytes":jpg.stat().st_size})
(report / f"captures_{mode}.json").write_text(json.dumps({"started":started, "exit_code":proc.returncode, "command":args, "game_head":subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=game, text=True).strip(), "stdout":out.name, "stderr":err.name, "captures":records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PASS #{card} {mode}: actual quest input +3 fresh frames; JPG width1280/<=300KB.")
