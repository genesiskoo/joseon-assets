import hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
root=Path('C:/workspace/joseon/._tmp')
records=json.loads((root/'626_generation_registry.json').read_text(encoding='utf-8'))
records += [json.loads(p.read_text(encoding='utf-8')) for p in sorted((root/'626_generation_parts').glob('*.json'))]
label=sys.argv[1]
out=root/f'626_qa_{label}'
out.mkdir(exist_ok=False)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
stats=[]
for rec in records:
    if rec.get('transparent_background'):
        continue
    image=Image.open(rec['source']).convert('RGB')
    w,h=image.size
    a=np.asarray(image,dtype=float)
    x=float(np.abs(a[:,0]-a[:,-1]).mean())
    y=float(np.abs(a[0]-a[-1]).mean())
    inside_x=float(np.abs(a[:,1:]-a[:,:-1]).mean())
    inside_y=float(np.abs(a[1:]-a[:-1]).mean())
    hsv=np.asarray(image.convert('HSV'),dtype=float)/255
    row={**{k:v for k,v in rec.items() if k not in ('prompt','refs')},'native_size':[w,h], 'bytes':Path(rec['source']).stat().st_size,'sha256':hashlib.sha256(Path(rec['source']).read_bytes()).hexdigest(),'rgb_mean':a.mean(axis=(0,1)).round(3).tolist(),'hsv_s_mean':float(hsv[:,:,1].mean()),'value_mean':float(hsv[:,:,2].mean()),'wrap_mae_x':x,'wrap_mae_y':y,'internal_neighbor_mae_x':inside_x,'internal_neighbor_mae_y':inside_y,'wrap_ratio_x':x/max(inside_x,0.001),'wrap_ratio_y':y/max(inside_y,0.001)}
    stats.append(row)
    stem=f"{rec['set']}_{rec['material']}_r{rec['revision']}"
    offset=ImageChops.offset(image,w//2,h//2)
    offset.save(out/(stem+'_offset.png'))
    thumb=image.resize((310,310),Image.Resampling.LANCZOS)
    half=offset.resize((310,310),Image.Resampling.LANCZOS)
    repeated=Image.new('RGB',(620,620))
    for yy in (0,310):
        for xx in (0,310):
            repeated.paste(thumb,(xx,yy))
    board=Image.new('RGB',(1280,680),'#202020')
    d=ImageDraw.Draw(board)
    d.text((16,8),f"{stem} · 원본 / 반 칸 이동 / 2×2 반복",font=font,fill='white')
    board.paste(thumb,(16,65));board.paste(half,(336,65));board.paste(repeated,(656,55))
    board.save(out/(stem+'_qa.jpg'),quality=83,optimize=True)
(out/'metrics.json').write_text(json.dumps({'card':626,'diagnostic_only':True,'criterion':'Wrap ratio is diagnostic; human review still required. No seamlessness claim.', 'records':stats},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'folder':str(out),'images':len(stats),'total_raw_bytes':sum(r['bytes'] for r in stats),'metrics':[{k:r[k] for k in ('set','material','revision','native_size','rgb_mean','wrap_ratio_x','wrap_ratio_y')} for r in stats]},ensure_ascii=False))
