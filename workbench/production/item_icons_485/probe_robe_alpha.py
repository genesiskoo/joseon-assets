"""Read alpha samples to distinguish RGB matte from rendered background."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parent
im=Image.open(ROOT/'source/items/u_seonnyeo_robe.png')
points=[(20,700),(50,700),(70,850),(95,1250),(500,35),(500,70),(970,750),(500,1490),(500,400)]
rows=[dict(pixel=[x,y],rgba=list(im.getpixel((x,y)))) for x,y in points]
(ROOT/'robe_alpha_probe.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(rows))
