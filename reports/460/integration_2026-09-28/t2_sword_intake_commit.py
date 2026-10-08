from pathlib import Path
import hashlib
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path("C:/workspace/joseon")
ctx_path = root / "tmp/t2_sword_intake_context.json"
ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
game, report = Path(ctx["game"]), Path(ctx["report"])
data = json.loads((report / "verification.json").read_text(encoding="utf-8"))
assert data["validation"]["unit_gd"] == 53 and len(data["validation"]["related_e2e"]) == 11
for mode in ["import", "unit", "e2e", "gate"]:
    meta = json.loads((report / f"run_{mode}.json").read_text(encoding="utf-8"))
    assert meta["exit_code"] == 0
    assert hashlib.sha256((report / meta["raw_log"]).read_bytes()).hexdigest() == meta["raw_sha256"]
manifest = json.loads((Path(ctx["intake"]) / "intake_manifest.json").read_text(encoding="utf-8"))
files = []
for item in manifest["files"]:
    files.extend([item["definition"], item["destination"]])
files.extend(["tests/e2e/scenarios/icon_intake.gd", "docs/design/ui_v2.md", "docs/TASK_CURRENT.md", "art/ui_intake_460", "docs/art/460_d1_t2_sword_intake"])
subprocess.run(["git", "-C", str(game), "add", "--", *files], check=True)
subprocess.run(["git", "-C", str(game), "diff", "--cached", "--check"], check=True)
staged = subprocess.check_output(["git", "-C", str(game), "diff", "--cached", "--name-only"], text=True).splitlines()
allowed = [p for p in files if Path(p).suffix]
assert all(p in allowed or p.startswith("art/ui_intake_460/") or p.startswith("docs/art/460_d1_t2_sword_intake/") for p in staged), staged
assert all(not p.endswith(".import") for p in staged), "UI import sidecars follow repository auto-import convention."
subprocess.run(["git", "-C", str(game), "commit", "-m", "feat(#460): 승인 T2 검4 반입과 실제 장비·거래·회수 검수"], check=True)
ctx["game_candidate"] = subprocess.check_output(["git", "-C", str(game), "rev-parse", "HEAD"], text=True).strip()
ctx["status"] = "verified_and_committed"
ctx_path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("GAME_COMMIT", ctx["game_candidate"])
