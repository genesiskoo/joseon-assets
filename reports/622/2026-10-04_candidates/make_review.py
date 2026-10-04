import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[3]
base=root/'workbench/production/steam_art_622'
out=root/'reports/622/2026-10-04_candidates'
fontpath=str(Path(sys.argv[1])) if len(sys.argv)>1 else 'C:/Windows/Fonts/malgun.ttf'
font=ImageFont.truetype(fontpath,24); small=ImageFont.truetype(fontpath,17)
def save(im,name):
    im.thumbnail((1280,1800),Image.Resampling.LANCZOS)
    for q in (90,85,80,75,70,65,60,50):
        im.save(out/name,quality=q,optimize=True)
        if (out/name).stat().st_size<=300000: return
    raise AssertionError('JPG budget')
def image(key): return Image.open(base/'exports'/f'{key}.png').convert('RGBA')
def panel(im,rect,key,label):
    x,y,w,h=rect; d=ImageDraw.Draw(im); d.text((x+4,y),label,font=small,fill='#e5dfd0')
    p=ImageOps.contain(image(key),(w,h-28),Image.Resampling.LANCZOS)
    im.paste(p.convert('RGB'),(x+(w-p.width)//2,y+28))
headers=Image.new('RGB',(1280,1280),'#151515')
panel(headers,(10,0,1260,635),'A_header_r1','A · 봉인문 앞 도호 / header 920×430')
panel(headers,(10,640,1260,635),'B_header_r1','B · 검 준비 자세 / header 920×430')
save(headers,'01_header_pair.jpg')
portraits=Image.new('RGB',(1280,530),'#151515')
for i,(key,label) in enumerate([('A_vertical_r1','A · 세로 캡슐'),('B_vertical_r1','B · 세로 캡슐'),('A_library_capsule_r1','A · 라이브러리'),('B_library_capsule_r1','B · 라이브러리')]):
    panel(portraits,(i*320+5,0,310,515),key,label)
save(portraits,'02_portrait_pair.jpg')
small_keys=['A_small_r1','B_small_r1']
if (base/'exports/A_small_r2.png').exists() and (base/'exports/B_small_r2.png').exists(): small_keys=['A_small_r1','A_small_r2','B_small_r1','B_small_r2']
proof=Image.new('RGB',(1280,80+225*len(small_keys)),'#252525'); d=ImageDraw.Draw(proof)
d.text((18,10),'작은 캡슐 · 462×174 / 184×69 / 120×45 · 실제 1배 + 확대',font=font,fill='#eeeeee')
for i,k in enumerate(small_keys):
    y=65+i*225; d.text((18,y),k,font=small,fill='#e5dfd0'); y+=26
    for x,s in ((18,(462,174)),(500,(184,69)),(702,(120,45))):
        p=image(k).resize(s,Image.Resampling.LANCZOS); proof.paste(p.convert('RGB'),(x,y)); d.text((x,y+s[1]+3),f'{s[0]}×{s[1]} (1×)',font=small,fill='#e5dfd0')
    tiny=image(k).resize((120,45),Image.Resampling.LANCZOS).resize((360,135),Image.Resampling.NEAREST); proof.paste(tiny.convert('RGB'),(882,y)); d.text((882,y+140),'120×45 (3× 픽셀 확대)',font=small,fill='#e5dfd0')
save(proof,'03_small_actual_scale.jpg')
hero=Image.new('RGB',(1280,1800),'#151515')
for i,k in enumerate(('A_library_hero_r1','A_library_hero_r2','B_library_hero_r1','B_library_hero_r2')):
    p=image(k).resize((1260,407),Image.Resampling.LANCZOS).convert('RGB')
    # Annotation only, not a production artwork change.
    dd=ImageDraw.Draw(p); scale=1260/3840; box=[round(v*scale) for v in (1490,430,2350,810)]; dd.rectangle(box,outline='#54e2bd',width=2)
    y=i*445+28; hero.paste(p,((1280-p.width)//2,y)); ImageDraw.Draw(hero).text((12,i*445+2),k+' · 초록 = 860×380 안전 영역 (3840×1240)',font=small,fill='#e5dfd0')
save(hero,'04_hero_safe_before_after.jpg')
logo=Image.new('RGB',(1280,440),'#191919'); d=ImageDraw.Draw(logo)
for i,k in enumerate(('logo_common_r1','logo_common_r2')):
    p=ImageOps.contain(image(k),(620,395),Image.Resampling.LANCZOS); logo.paste(p,(i*640+(640-p.width)//2,35),p); d.text((i*640+10,6),k+' · alpha 검수',font=small,fill='#e5dfd0')
save(logo,'05_logo_before_after.jpg')
if (base/'exports/A_page_background_r1.png').exists() and (base/'exports/B_page_background_r1.png').exists():
    overview=Image.new('RGB',(1280,795),'#151515')
    for i,(k,l) in enumerate((('A_main_r1','A · 메인 캡슐'),('B_main_r1','B · 메인 캡슐'),('A_page_background_r1','A · 페이지 배경'),('B_page_background_r1','B · 페이지 배경'))):panel(overview,(10+(i%2)*640,(i//2)*395,620,385),k,l)
    save(overview,'06_main_and_background.jpg')
print(json.dumps([{'file':p.name,'bytes':p.stat().st_size} for p in out.glob('*.jpg')],ensure_ascii=False))
