from pathlib import Path
import json
import shutil
ctx = json.loads(Path("C:/workspace/joseon/tmp/t2_sword_intake_context.json").read_text(encoding="utf-8"))
assert ctx["status"] == "prepared_before_intake"
game,report = Path(ctx["game"]),Path(ctx["report"])
failed = Path("C:/Users/FORYOUCOM/AppData/Roaming/Godot/app_userdata/Joseon Hunters/wt/codex-87-ui-wood-skin/e2e/icon_intake_01_sword_inventory.png")
dest = report / "failed_before_first_frame.png"
assert failed.is_file() and not dest.exists()
shutil.copy2(failed,dest)
path = game / "tests/e2e/scenarios/icon_intake.gd"
body = path.read_text(encoding="utf-8")
start = body.index("## #460: 승인 T2 검4")
body = body[:start]+Path("C:/workspace/joseon/tmp/460_sword_review.gd").read_text(encoding="utf-8")
path.write_text(body,encoding="utf-8",newline="\n")
print("Fixture corrected: 2H offhand return precedes old weapon; PanelUi._msg API. Failed raw logs/frame preserved; product assets unchanged.")
