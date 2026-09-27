from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/t2_sword_context.json").read_text(encoding="utf-8"))
root, report = Path(ctx["production"]), Path(ctx["report"])
old = root / "source/items/saingeom.png"
new = Path(sys.argv[1])
history = report / "iterations/r1"
assert not history.exists()
history.mkdir(parents=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
preserved = history / "saingeom.png"
shutil.copy2(old, preserved)
assert sha(old) == sha(preserved)
for name in ["manifest.json", "generation_sources.json", "inputs.json"]:
    shutil.copy2(root / name, history / name)
for name in ["overview.png", "godot_after.png", "godot_sizes.png"]:
    shutil.copy2(root / "qa" / name, history / name)
for mode in ["after", "sizes"]:
    shutil.copy2(report / f"459_godot_{mode}.log", history / f"459_godot_{mode}.log")
data = json.loads((root / "generation_sources.json").read_text(encoding="utf-8"))
entry = next(x for x in data["items"] if x["item_id"] == "saingeom")
initial = dict(entry)
assert initial["original_sha256"] == sha(preserved)
prompt = (root / "EDIT_SAINGEOM.txt").read_text(encoding="utf-8").rstrip("\n")
im = Image.open(new)
assert "A" in im.getbands() and im.getchannel("A").getextrema() == (0,255)
shutil.copy2(new, old)
assert sha(new) == sha(old)
entry.update(generated_path=new.as_posix(), original_sha256=sha(old), source_size=list(im.size), prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(), revision=2, prompt_file="EDIT_SAINGEOM.txt", edit_target_at_call=initial["project_original"], edit_target_sha256=initial["original_sha256"], preserved_edit_target=preserved.as_posix(), initial_generation=initial, reference_roles="first image edit target; images2/3 style references", referenced_image_paths_at_call=[old.as_posix(),(root / "references/accepted_hwando.png").as_posix(),(root / "references/accepted_yedo.png").as_posix()])
(root / "generation_sources.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
inputs = json.loads((root / "inputs.json").read_text(encoding="utf-8"))
row = next(x for x in inputs["items"] if x["item_id"] == "saingeom")
row.update(edit_prompt=prompt, silhouette="폭 넓은 양날 · 낮은 사각 의장 금속", selected_revision=2)
(root / "inputs.json").write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
with (root / "PROMPTS.md").open("a",encoding="utf-8",newline="\n") as f:
    f.write("\n## 사인검 40×120 판독 보정 / revision2\n\n"+prompt+"\n")
env = dict(os.environ)
env["PYTHONIOENCODING"] = "utf-8"
p = subprocess.run([sys.executable,str(root / "prepare_assets.py")],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(report / f"{ctx['card']}_pack_r2.log").write_bytes(p.stdout)
print(p.stdout.decode("utf-8",errors="replace"))
p.check_returncode()
ctx.update(status="rendered_r1_and_edited_r2",built_in_generations=4,built_in_edits=1,selected_saingeom_revision=2)
(main / "tmp/t2_sword_context.json").write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Saingeom r1/raw/captures preserved; selected r2 original saved unchanged")
