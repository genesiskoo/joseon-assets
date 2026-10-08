"""Preserve native originals and pack each #469 item at its actual footprint."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    inputs = json.loads((ROOT/'inputs.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT/'generation_sources.json').read_text(encoding='utf-8'))
    assert [x['item_id'] for x in inputs['items']] == [x['id'] for x in sources['items']]
    for d in ['source/items','game/items','qa']:
        (ROOT/d).mkdir(parents=True,exist_ok=True)
    rows=[]
    for spec,gen in zip(inputs['items'],sources['items']):
        item_id=spec['item_id']
        original=ROOT/'source/items'/f'{item_id}.png'
        native=Path(gen['native_path'])
        if original.exists():
            assert sha(original)==sha(native)
        else:
            shutil.copyfile(native,original)
        raw=Image.open(original)
        assert raw.mode=='RGBA' and raw.getchannel('A').getextrema()[0]==0 and raw.getchannel('A').getextrema()[1]>=250
        alpha=raw.getchannel('A').point(lambda a:a if a>=16 else 0)
        bbox=alpha.getbbox()
        assert bbox and 0<bbox[0]<bbox[2]<raw.width and 0<bbox[1]<bbox[3]<raw.height
        art=raw.copy();art.putalpha(alpha);art=art.crop(bbox)
        size=(spec['output_width'],spec['output_height'])
        pad=max(5,round(min(size)*.08))
        scale=min((size[0]-pad*2)/art.width,(size[1]-pad*2)/art.height)
        shown=art.resize((max(1,round(art.width*scale)),max(1,round(art.height*scale))),Image.Resampling.LANCZOS)
        packed=Image.new('RGBA',size)
        packed.alpha_composite(shown,((size[0]-shown.width)//2,(size[1]-shown.height)//2))
        dest=ROOT/'game/items'/f'{item_id}.png';packed.save(dest,optimize=True)
        bound=packed.getchannel('A').getbbox()
        assert bound and bound[0]>=2 and bound[1]>=2 and bound[2]<=size[0]-2 and bound[3]<=size[1]-2
        assert packed.getchannel('A').getextrema()==(0,255)
        assert sha(Path(spec['definition_path']))==spec['definition_sha256']
        rows.append(dict(spec,source_path=original.relative_to(ROOT).as_posix(),source_sha256=sha(original),source_size=list(raw.size),source_bbox=list(bbox),source_alpha=list(raw.getchannel('A').getextrema()),game_path=dest.relative_to(ROOT).as_posix(),game_sha256=sha(dest),game_size=list(size),visible_bbox=list(bound)))
    manifest=dict(card=469,parent_card=274,status='candidate_not_installed',method='native image_gen originals; alpha16/8percent/Lanczos ratio packing',logical_cell_px=40,output_scale=2,items=rows)
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    prompts='# #469 Native image_gen prompts\n\n'+'\n\n'.join('## '+x['id']+'\n\n'+x['prompt']+'\n\nNative original: '+x['native_path'] for x in sources['items'])+'\n'
    (ROOT/'PROMPTS.md').write_text(prompts,encoding='utf-8',newline='\n')
    head=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
    sheet=Image.new('RGB',(1280,830),(26,23,21));draw=ImageDraw.Draw(sheet)
    draw.text((25,18),'#469 D1 광다회·목화·부첩2 — 원화 / 실제 점유40px',font=head,fill=(235,216,187))
    for i,row in enumerate(rows):
        x,y=20+(i%2)*630,65+(i//2)*375
        draw.rectangle((x,y,x+610,y+358),fill=(34,30,27),outline=(88,72,52))
        art=Image.open(ROOT/row['source_path']).crop(tuple(row['source_bbox']))
        art.thumbnail((290,245),Image.Resampling.LANCZOS)
        sheet.paste(art,(x+16+(290-art.width)//2,y+16+(245-art.height)//2),art)
        actual=(row['grid_w']*40,row['grid_h']*40)
        icon=Image.open(ROOT/row['game_path']).resize(actual,Image.Resampling.LANCZOS)
        px,py=x+420-actual[0]//2,y+60
        draw.rectangle((px,py,px+actual[0],py+actual[1]),fill=(3,3,3),outline=(100,82,58))
        sheet.paste(icon,(px,py),icon)
        draw.text((x+337,y+165),f"40px × {row['grid_w']}×{row['grid_h']}칸",font=small,fill=(177,162,140))
        draw.text((x+18,y+273),row['display_name'],font=head,fill=(232,216,190))
        draw.text((x+18,y+310),row['note'],font=small,fill=(185,168,144))
        draw.text((x+18,y+334),f"{row['item_id']} · {row['output_width']}×{row['output_height']} RGBA",font=small,fill=(153,143,127))
    sheet.save(ROOT/'qa/overview.png',optimize=True)
    sheet.save(ROOT/'qa/overview.jpg',quality=85,optimize=True)
    print('PACKED',len(rows),[(r['item_id'],r['source_size'],r['game_size'],r['visible_bbox']) for r in rows])

if __name__=='__main__':
    main()
