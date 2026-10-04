import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
root=Path('C:/workspace/joseon/._tmp')
records=json.loads((root/'626_generation_registry.json').read_text(encoding='utf-8'))+[json.loads(p.read_text(encoding='utf-8')) for p in sorted((root/'626_generation_parts').glob('*.json'))]
rows=[]
for r in records:
    if not r.get('transparent_background'):continue
    im=Image.open(r['source']).convert('RGBA');a=np.asarray(im)
    alpha=a[:,:,3];active=alpha>=16
    ys,xs=np.where(active)
    hsv=np.asarray(im.convert('RGB').convert('HSV'))/255
    colorful=(hsv[:,:,1]>.65)&(hsv[:,:,2]>.5)
    border=np.concatenate((alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]))
    rows.append({'set':r['set'],'material':r['material'],'native_size':list(im.size),'alpha_min':int(alpha.min()),'alpha_max':int(alpha.max()),'border_alpha_max':int(border.max()),'active_alpha16_fraction':float(active.mean()),'bbox_alpha16':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'bright_saturated_pixels_alpha_ge128':int((colorful&(alpha>=128)).sum()),'bright_saturated_pixels_alpha_1_127':int((colorful&(alpha>0)&(alpha<128)).sum())})
out=root/('626_alpha_'+sys.argv[1]);out.mkdir(exist_ok=False)
(out/'metrics.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
decals=[r for r in records if r.get('transparent_background')]
board=Image.new('RGB',(1280,50+len(decals)*330),'#202020');d=ImageDraw.Draw(board)
d.text((15,8),'#626 알파 확인 · 검정 / 흰색 / 실제 흙 위 합성 · 색 보정 없음',font=font,fill='white')
for i,r in enumerate(decals):
    im=Image.open(r['source']).convert('RGBA').resize((310,310),Image.Resampling.LANCZOS)
    y=50+i*330
    d.text((15,y),r['set']+' '+r['material'],font=font,fill='white')
    for j,color in enumerate(('#000000','#ffffff')):
        bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im);board.paste(bg.convert('RGB'),(320+j*320,y))
    floor=next(k for k in records if k['set']==r['set'] and k['material']=='dirt' and k['revision']==2)
    bg=Image.open(floor['source']).convert('RGBA').resize(im.size,Image.Resampling.LANCZOS);bg.alpha_composite(im);board.paste(bg.convert('RGB'),(960,y))
board.save(out/'probe.jpg',quality=85,optimize=True)
print(json.dumps(rows,ensure_ascii=False))
