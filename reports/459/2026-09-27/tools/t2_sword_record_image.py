from pathlib import Path
import hashlib
import json
import shutil
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ctx = json.loads(Path("C:/workspace/joseon/tmp/t2_sword_context.json").read_text(encoding="utf-8"))
root = Path(ctx["production"])
id, generated = sys.argv[1:]
inputs = json.loads((root / "inputs.json").read_text(encoding="utf-8"))
entry = next(e for e in inputs["items"] if e["item_id"] == id)
src = Path(generated)
dest = root / "source/items" / f"{id}.png"
assert src.is_file() and not dest.exists()
shutil.copy2(src, dest)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(src) == sha(dest)
im = Image.open(dest)
assert "A" in im.getbands() and im.getchannel("A").getextrema() == (0,255)
path = root / "generation_sources.json"
data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"card":ctx["card"],"status":"in_progress","items":[]}
assert not any(e["item_id"] == id for e in data["items"])
data["items"].append({"item_id":id, "display_name":entry["display_name"], "generated_path":src.as_posix(), "project_original":dest.relative_to(root).as_posix(), "original_sha256":sha(dest), "source_size":list(im.size), "source_alpha":[0,255], "prompt_sha256":hashlib.sha256(entry["prompt"].encode("utf-8")).hexdigest(), "method":"built-in image_gen", "transparent_background":True, "style_reference_paths":[(root / "references" / name).as_posix() for name in ["accepted_hwando.png", "accepted_yedo.png"]], "reference_roles":"style only, no edit target"})
if len(data["items"]) == 4:
    data["status"] = "complete"
path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps({"item_id":id,"source":dest.as_posix(),"size":list(im.size),"alpha":[0,255],"sha256":sha(dest)},ensure_ascii=False))
