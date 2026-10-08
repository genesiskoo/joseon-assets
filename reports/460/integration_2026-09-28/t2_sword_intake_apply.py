from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
context = main / "tmp/t2_sword_intake_context.json"
ctx = json.loads(context.read_text(encoding="utf-8"))
assert ctx["status"] == "prepared_before_intake"
card = ctx["card"]
game,source,report = [Path(ctx[k]) for k in ["game","source","report"]]
capture = json.loads((report / "captures_before.json").read_text(encoding="utf-8"))
assert capture["exit_code"] == 0 and len(capture["captures"]) == 3
production = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
snapshot = json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
for rel,digest in snapshot["protected_files"].items():
    assert sha(game / rel) == digest,rel
destination_dir = game / "assets/sprites/ui/icons_a/items"
for e in production["items"]:
    assert not (destination_dir / (e["item_id"]+".png")).exists()
    assert sha(source / "game/items" / (e["item_id"]+".png")) == e["game_sha256"]
source_paths = [str(source / "game/items" / (e["item_id"]+".png")).replace("'","''") for e in production["items"]]
copy_script = "$taskIconDest = '"+str(destination_dir).replace("'","''")+"'; Copy-Item -LiteralPath @("+",".join("'"+p+"'" for p in source_paths)+") -Destination $taskIconDest"
env = dict(os.environ,PYTHONIOENCODING="utf-8")
p = subprocess.run(["powershell.exe","-NoProfile","-Command",copy_script],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(report / "copy_icons.log").write_bytes(p.stdout)
print(p.stdout.decode("utf-8-sig",errors="replace"))
p.check_returncode()
records = []
for e in production["items"]:
    id = e["item_id"]
    rel = f"data/items/{id}.tres"
    path = game / rel
    old = path.read_text(encoding="utf-8")
    assert old == snapshot["before_definitions"][rel] and old.count(e["current_icon"]) == 1
    dest = f"assets/sprites/ui/icons_a/items/{id}.png"
    resource = "res://"+dest
    new = old.replace(e["current_icon"],resource,1)
    assert old.replace(e["current_icon"],"<icon_path>",1) == new.replace(resource,"<icon_path>",1)
    assert 'icon = ExtResource("2")' in new and "load_steps=3" in new
    path.write_text(new,encoding="utf-8",newline="\n")
    image = Image.open(game / dest)
    assert image.mode == "RGBA" and image.size == (80,240) and image.getchannel("A").getextrema() == (0,255)
    assert sha(game / dest) == e["game_sha256"]
    records.append({"data_id":id,"display_name":e["display_name"],"definition":rel,"source":f"workbench/production/item_icons_459/game/items/{id}.png","destination":dest,"sha256":e["game_sha256"],"game_size":[80,240],"footprint":[1,3],"previous_icon":e["current_icon"],"definition_before_sha256":hashlib.sha256(old.encode()).hexdigest(),"definition_after_sha256":sha(path),"non_icon_fields_sha256":hashlib.sha256(old.replace(e["current_icon"],"<icon_path>",1).encode()).hexdigest(),"unchanged_except_icon_path":True})
intake = Path(ctx["intake"])
intake.mkdir(parents=True,exist_ok=True)
manifest = {"issue":card,"production_issue":459,"source_repository":"joseon-assets","source_commit":ctx["source_commit"],"game_base":ctx["game_base"],"approval":ctx["approval"],"method":"PowerShell Copy-Item of approved PNG bytes; existing Texture2D path only; UiSkin alpha-region unchanged","files":records,"protected_files":snapshot["protected_files"],"old_h1_icons_preserved":snapshot["old_h1_icons"]}
(intake / "intake_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
task = game / "docs/TASK_CURRENT.md"
task.write_text(task.read_text(encoding="utf-8")+f"\n- 2026-09-28 #{card} `icons_a/items` ← `C:/workspace/joseon-assets/workbench/production/item_icons_459/game/items` (승인 {ctx['source_commit'][:8]}) → 본국검·제독검·쌍수도·사인검r2 PNG4/Texture2D경로만. 1×3·쌓기·수치·가격·양손/보조·바닥모델·기존101파일 보존.\n",encoding="utf-8",newline="\n")
ctx["status"] = "applied_approved_png4"
context.write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PASS approvedPNG4 exact SHA/RGBA80×240; existing resource path only; all non-icon fields preserved")
