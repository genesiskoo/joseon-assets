"""Deterministic alpha/ratio packaging and contact plates; no creative edits."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    inputs=json.loads((ROOT/'inputs.json').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'generation_sources.json').read_text(encoding='utf-8'))
    assert len(inputs['items'])==len(sources['items'])==3
    for directory in ['source/items','game/items','qa']:
        (ROOT/directory).mkdir(parents=True,exist_ok=True)
    rows=[]
    for spec,gen in zip(inputs['items'],sources['items']):
        uid=spec['item_id'];assert uid==gen['id']
        native=Path(gen['native_path'])
        version_suffix='_'+gen['version'] if gen.get('version') else ''
        original=ROOT/'source/items'/f'{uid}{version_suffix}.png'
        if original.exists():
            assert sha(original)==sha(native)
        else:
            shutil.copyfile(native,original)
        raw=Image.open(original)
        assert raw.mode=='RGBA' and raw.getchannel('A').getextrema()==(0,255)
        alpha=raw.getchannel('A').point(lambda a:a if a>=16 else 0)
        bbox=alpha.getbbox()
        assert bbox and 0<bbox[0]<bbox[2]<raw.width and 0<bbox[1]<bbox[3]<raw.height
        art=raw.copy();art.putalpha(alpha);art=art.crop(bbox)
        size=(spec['output_width'],spec['output_height'])
        pad=max(5,round(min(size)*.08))
        scale=min((size[0]-2*pad)/art.width,(size[1]-2*pad)/art.height)
        shown=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
        packed=Image.new('RGBA',size)
        packed.alpha_composite(shown,((size[0]-shown.width)//2,(size[1]-shown.height)//2))
        dest=ROOT/'game/items'/f'{uid}.png';packed.save(dest,optimize=True)
        bounds=packed.getchannel('A').getbbox()
        assert bounds and min(bounds[:2])>=2 and max(bounds[2:])<=78
        assert packed.getchannel('A').getextrema()==(0,255)
        for field in ['definition','base_definition','base_reference']:
            assert sha(Path(spec[field+'_path']))==spec[field+'_sha256']
        rows.append(dict(spec,source_path=original.relative_to(ROOT).as_posix(),source_sha256=sha(original),source_size=list(raw.size),source_bbox=list(bbox),source_alpha=list(raw.getchannel('A').getextrema()),game_path=dest.relative_to(ROOT).as_posix(),game_sha256=sha(dest),game_size=list(size),visible_bbox=list(bounds)))
    manifest=dict(card=483,parent_card=274,status='candidate_not_installed',method='native image_gen originals; unchanged common alpha16/8percent/Lanczos ratio packing',logical_cell_px=40,output_scale=2,items=rows)
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    prompts='# #483 Native image_gen prompts\n\n'+'\n\n'.join('## '+r['id']+'\n\n'+r['prompt']+'\n\nNative original: '+r['native_path'] for r in sources['items'])+'\n'
    (ROOT/'PROMPTS.md').write_text(prompts,encoding='utf-8',newline='\n')
    head=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
    sheet=Image.new('RGB',(1280,760),(26,23,21));draw=ImageDraw.Draw(sheet)
    draw.text((24,18),'#483 D1 대표유니크 장신구3 — 원화 / 베이스 대조 / 40px',font=head,fill=(235,216,187))
    for i,row in enumerate(rows):
        x=20+i*420
        draw.rectangle((x,65,x+400,707),fill=(34,30,27),outline=(88,72,52))
        art=Image.open(ROOT/row['source_path']).crop(tuple(row['source_bbox']))
        art.thumbnail((315,330),Image.Resampling.LANCZOS)
        sheet.paste(art,(x+43+(315-art.width)//2,83+(330-art.height)//2),art)
        draw.text((x+17,426),row['display_name'],font=head,fill=(232,216,190))
        draw.text((x+17,462),row['note'],font=small,fill=(185,168,144))
        draw.text((x+17,493),'40px: 일반 베이스 / 유니크 후보 / 무채색',font=small,fill=(177,162,140))
        icon=Image.open(ROOT/row['game_path']).resize((40,40),Image.Resampling.LANCZOS)
        base=Image.open(row['base_reference_path']).convert('RGBA').resize((40,40),Image.Resampling.LANCZOS)
        gray=Image.merge('RGBA',(*([icon.convert('L')]*3),icon.getchannel('A')))
        for j,img in enumerate([base,icon,gray]):
            px=x+49+j*114;py=530
            draw.rectangle((px,py,px+40,py+40),fill=(0,0,0),outline=(100,82,58))
            sheet.paste(img,(px,py),img)
        draw.text((x+20,597),row['base_display_name']+' 베이스 · 1×1 / 80×80 RGBA',font=small,fill=(177,162,140))
        draw.text((x+20,630),row['item_id'],font=small,fill=(153,143,127))
        draw.text((x+20,660),'전용 icon 연결 선행 · 게임 미반입',font=small,fill=(153,143,127))
    sheet.save(ROOT/'qa/overview.png',optimize=True)
    sheet.save(ROOT/'qa/overview.jpg',quality=85,optimize=True)
    print('PACKED',[(r['item_id'],r['source_size'],r['game_size'],r['visible_bbox']) for r in rows])

if __name__=='__main__':
    main()
