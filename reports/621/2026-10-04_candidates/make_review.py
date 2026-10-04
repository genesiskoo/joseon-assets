import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[3]; base=root/'workbench/production/skill_icons_621'; out=root/'reports/621/2026-10-04_candidates'
fontpath=str(Path(sys.argv[1])) if len(sys.argv)>1 else 'C:/Windows/Fonts/malgun.ttf'
font=ImageFont.truetype(fontpath,22); small=ImageFont.truetype(fontpath,16)
skills=[('blink','축지법'),('light_step','경공'),('clone','분신술'),('hide','은형술'),('iron_body','금강불괴'),('first_cut','첫 칼'),('thunder_lore','벽력부 익히기')]
def key(direction,skill):
    rev='r2' if (direction,skill) in [('A','clone'),('B','thunder_lore')] else 'r1'
    return f'{direction}_{skill}_{rev}'
def asset(k,size): return Image.open(base/'exports'/f'{k}_{size}.png').convert('RGB')
def save(im,name):
    assert im.width<=1280
    for q in (90,85,80,75,70,65,60,50):
        im.save(out/name,quality=q,optimize=True)
        if (out/name).stat().st_size<=300000: return
    raise AssertionError('review JPG budget')
for direction,title in [('A','인물·동작 중심'),('B','큰 형태·상징 강조')]:
    im=Image.new('RGB',(1280,750),'#171715'); d=ImageDraw.Draw(im)
    d.text((18,12),f'#621 · {direction}안 · {title} · 미채택 후보 / 128px 파일을 2배로 표시',font=font,fill='#eee6d5')
    for n,(sid,name) in enumerate(skills):
        x=16+(n%4)*316; y=62+(n//4)*335; k=key(direction,sid)
        d.text((x,y),f'{name} · {k}',font=small,fill='#ded4bd')
        im.paste(asset(k,128).resize((288,288),Image.Resampling.LANCZOS),(x,y+27))
    d.text((968,518),'H1 + #498 먹·무광 바탕\nUI 테두리 없음\n게임 반입 0\n생성 원본과 이전 판 보존',font=small,fill='#c6bda9',spacing=9)
    save(im,f'0{1 if direction=="A" else 2}_{direction}_overview.jpg')
proof=Image.new('RGB',(1280,1410),'#232321'); d=ImageDraw.Draw(proof)
d.text((18,10),'실제 크기 대조 · 128 / 64 / 40 / 내부34px · 게임 스크린샷 아님',font=font,fill='#eee6d5')
for n,(sid,name) in enumerate(skills):
    y=56+n*192; d.text((16,y),name,font=small,fill='#eee6d5')
    for col,dr in enumerate(('A','B')):
        x=154+col*555; k=key(dr,sid); d.text((x,y),dr,font=small,fill='#eee6d5')
        for dx,size in ((28,128),(170,64),(250,40),(316,34)):
            p=asset(k,size if size in (128,64,40) else 128)
            if size==34: p=p.resize((34,34),Image.Resampling.LANCZOS)
            proof.paste(p,(x+dx,y+24)); d.text((x+dx,y+size+26),str(size)+' (1×)',font=small,fill='#cfc5b1')
        tiny=asset(k,40).resize((160,160),Image.Resampling.NEAREST)
        proof.paste(tiny.resize((112,112),Image.Resampling.NEAREST),(x+414,y+24))
        d.text((x+414,y+116),'40px 픽셀 확대',font=small,fill='#cfc5b1')
save(proof,'03_actual_slot_sizes.jpg')
compare=Image.new('RGB',(1280,650),'#1b1b19'); d=ImageDraw.Draw(compare)
d.text((18,12),'기존 채택 #498과 새 #621 · 같은40px와 확대 · 미리보기 비교',font=font,fill='#eee6d5')
canon=Path('C:/workspace/joseon-assets/workbench/production/skill_icons_498/game')
for n,sid in enumerate(('sword_mastery','breath','combo','pouch')):
    x=22+n*310; p=Image.open(canon/f'{sid}.png').convert('RGB').resize((40,40),Image.Resampling.LANCZOS)
    d.text((x,62),f'채택 #498 · {sid}',font=small,fill='#ddd2bd'); compare.paste(p,(x,93)); compare.paste(p.resize((200,200),Image.Resampling.NEAREST),(x,143))
for n,(dr,sid) in enumerate((('B','light_step'),('A','clone'),('A','hide'),('B','thunder_lore'))):
    x=22+n*310; k=key(dr,sid); p=asset(k,40)
    d.text((x,368),f'후보 #621 · {k}',font=small,fill='#ddd2bd'); compare.paste(p,(x,399)); compare.paste(p.resize((200,200),Image.Resampling.NEAREST),(x,449))
save(compare,'04_adopted_medium_comparison.jpg')
change=Image.new('RGB',(1280,760),'#171715'); d=ImageDraw.Draw(change)
d.text((18,10),'보정 전·후 · 같은 구도 · 뒤 분신 먹색 / 부적 단순화',font=font,fill='#eee6d5')
for n,(prefix,label) in enumerate((('A_clone','분신 A'),('B_thunder_lore','부적 숙련 B'))):
    for col,rev in enumerate(('r1','r2')):
        x=18+col*632; y=54+n*350; k=f'{prefix}_{rev}'; d.text((x,y),f'{label} · {"전" if rev=="r1" else "후"} · {rev}',font=small,fill='#ddd2bd')
        change.paste(asset(k,128).resize((296,296),Image.Resampling.LANCZOS),(x,y+28)); change.paste(asset(k,40),(x+320,y+28)); change.paste(asset(k,40).resize((240,240),Image.Resampling.NEAREST),(x+320,y+82))
save(change,'05_corrections_before_after.jpg')
print(json.dumps([{'file':p.name,'size':Image.open(p).size,'bytes':p.stat().st_size} for p in sorted(out.glob('*.jpg'))],ensure_ascii=False))
