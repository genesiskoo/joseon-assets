from pathlib import Path
from PIL import Image
import hashlib
import json
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path("C:/workspace/joseon")
ctx = json.loads((root / "tmp/dialogue_243_context.json").read_text(encoding="utf-8"))
prod = Path(ctx["production"])
records = json.loads((root / "tmp/dialogue_243_generated.json").read_text(encoding="utf-8"))
for record in records:
    p = Path(record["native_path"])
    dest = prod / "source" / f"{record['id']}.png"
    if dest.exists():
        assert dest.read_bytes() == p.read_bytes()
    else:
        shutil.copy2(p, dest)
    im = Image.open(dest)
    assert im.mode == "RGBA" and im.size == (1024, 1536)
    alpha = im.getchannel("A")
    assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 250
    box = alpha.point(lambda a: 255 if a >= 16 else 0).getbbox()
    record.update(saved_path=dest.relative_to(Path(ctx["assets"])).as_posix(),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),size=list(im.size),alpha=list(alpha.getextrema()),alpha16_bbox=list(box))
(prod / "generation_sources.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
prompts = "# #243 native image_gen prompts\n\n"
for record in records:
    prompts += f"## {record['id']}\n\nDisposition: {record['disposition']}\n\n{record['prompt']}\n\nNative saved path: {record['native_path']}\n"
(prod / "PROMPTS.md").write_text(prompts,encoding="utf-8",newline="\n")
print([(r["id"],r["size"],r["alpha"],r["alpha16_bbox"]) for r in records])
