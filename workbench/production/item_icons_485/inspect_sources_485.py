"""Preserve and inspect native image outputs without changing their pixels."""
from pathlib import Path
import json
import shutil
from PIL import Image
from prepare_485 import sha
ROOT=Path(__file__).resolve().parent
sources=json.loads((ROOT/'generation_sources.json').read_text(encoding='utf-8'))
rows=[]
for gen in sources['items']:
    native=Path(gen['native_path']);copy=ROOT/'source/items'/f"{gen['id']}.png"
    copy.parent.mkdir(parents=True,exist_ok=True)
    if copy.exists(): assert sha(copy)==sha(native)
    else: shutil.copyfile(native,copy)
    im=Image.open(copy)
    alpha=im.getchannel('A') if im.mode=='RGBA' else None
    bbox=alpha.point(lambda v:v if v>=16 else 0).getbbox() if alpha else None
    row=dict(id=gen['id'],native_path=gen['native_path'],source_path=copy.relative_to(ROOT).as_posix(),sha256=sha(copy),mode=im.mode,size=list(im.size),alpha_range=list(alpha.getextrema()) if alpha else None,bbox_alpha16=list(bbox) if bbox else None)
    rows.append(row)
(ROOT/'source_inspection_v1.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(rows,ensure_ascii=False))
