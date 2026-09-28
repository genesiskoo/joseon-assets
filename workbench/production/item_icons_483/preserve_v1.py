"""Keep the first candidate, source metadata, renders and raw logs before v2."""
from pathlib import Path
import shutil
from prepare_483 import sha
ROOT=Path(__file__).resolve().parent
REPORT=ROOT.parents[2]/'reports/483/2026-09-28'
OLD=ROOT/'variants/v1'
OLD.mkdir(parents=True,exist_ok=True)
for rel in ['generation_sources.json','manifest.json','verification.json','game/items/u_jangsanbeom_eye.png','qa/overview.png','qa/overview.jpg']:
    src=ROOT/rel;dest=OLD/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        assert sha(dest)==sha(src)
    else:
        shutil.copyfile(src,dest)
for mode in ['forty','sizes','black_sizes','base_compare']:
    for suffix in ['png','jpg']:
        src=ROOT/'qa'/f'godot_{mode}.{suffix}';dest=OLD/'qa'/src.name
        if dest.exists(): assert sha(dest)==sha(src)
        else: shutil.copyfile(src,dest)
    for kind in ['stdout','stderr']:
        src=REPORT/f'godot_{mode}_{kind}.txt';dest=OLD/'logs'/src.name
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists(): assert sha(dest)==sha(src)
        else: shutil.copyfile(src,dest)
print('PRESERVED #483 v1 mirror, manifest/prompts, gallery/raw before v2')
