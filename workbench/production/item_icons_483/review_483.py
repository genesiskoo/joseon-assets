"""Validate preserved contracts/originals and actual UiSkin render logs."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
from prepare_483 import GAME, runtime_files, sha

ROOT=Path(__file__).resolve().parent
REPORT=ROOT.parents[2]/'reports/483/2026-09-28'
GALLERY=GAME/'docs/art/483_d1_unique_charms'

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'generation_sources.json').read_text(encoding='utf-8'))
    before=json.loads((ROOT/'runtime_before.json').read_text(encoding='utf-8'))
    assert len(manifest['items'])==len(sources['items'])==3
    for row,gen in zip(manifest['items'],sources['items']):
        assert row['item_id']==gen['id']
        assert sha(ROOT/row['source_path'])==row['source_sha256']==sha(Path(gen['native_path']))
        assert sha(ROOT/row['game_path'])==row['game_sha256']
        image=Image.open(ROOT/row['game_path'])
        assert image.mode=='RGBA' and image.size==(80,80)
        assert image.getchannel('A').getextrema()==(0,255)
        assert list(image.getchannel('A').getbbox())==row['visible_bbox']
        for field in ['definition','base_definition','base_reference']:
            assert sha(Path(row[field+'_path']))==row[field+'_sha256']
    after={p.relative_to(GAME).as_posix():sha(p) for p in runtime_files()}
    assert before==after,[k for k in before if before[k]!=after.get(k)]
    png_count=sum(k.endswith('.png') for k in after)
    assert png_count==42
    REPORT.mkdir(parents=True,exist_ok=True);GALLERY.mkdir(parents=True,exist_ok=True)
    names=['overview.jpg'];logs=[]
    for mode in ['forty','sizes','black_sizes','base_compare']:
        stdout=REPORT/f'godot_{mode}_stdout.txt';stderr=REPORT/f'godot_{mode}_stderr.txt'
        raw=stdout.read_text(encoding='utf-8-sig')+'\n'+stderr.read_text(encoding='utf-8-sig')
        assert f'GODOT_D1_483_PASS mode={mode} items=3' in raw
        assert 'SCRIPT ERROR' not in raw and 'ERROR:' not in raw
        logs.append(dict(mode=mode,stdout_sha256=sha(stdout),stderr_sha256=sha(stderr)))
        p=ROOT/'qa'/f'godot_{mode}.png';im=Image.open(p)
        assert im.size==(1280,760)
        jpg=p.with_suffix('.jpg');im.convert('RGB').save(jpg,quality=86,optimize=True)
        names.append(jpg.name)
    old_metadata=json.loads((ROOT/'variants/v1/generation_sources.json').read_text(encoding='utf-8'))
    old_manifest=json.loads((ROOT/'variants/v1/manifest.json').read_text(encoding='utf-8'))
    old_eye=next(r for r in old_manifest['items'] if r['item_id']=='u_jangsanbeom_eye')
    old_gen=next(r for r in old_metadata['items'] if r['id']=='u_jangsanbeom_eye')
    assert sha(ROOT/old_eye['source_path'])==old_eye['source_sha256']==sha(Path(old_gen['native_path']))
    assert sha(ROOT/'variants/v1/game/items/u_jangsanbeom_eye.png')==old_eye['game_sha256']
    assert manifest['items'][1]['source_path'].endswith('_v2.png')
    pair=Image.new('RGB',(1280,730),(33,29,25));draw=ImageDraw.Draw(pair)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
    draw.text((26,19),'#483 장산범의 눈 — 같은 UiSkin·구도·배율의 보강 전후',font=font,fill=(230,210,181))
    for x,name,path in [(115,'BEFORE · v1 눈빛 대비 약함',ROOT/'variants/v1/qa/godot_forty.png'),(740,'AFTER · v2 눈빛 대비 보강',ROOT/'qa/godot_forty.png')]:
        draw.text((x,74),name,font=font,fill=(230,210,181))
        im=Image.open(path).crop((427,90,845,655))
        pair.paste(im,(x,110))
    draw.text((26,697),'원안/프롬프트/패킹/raw 보존 · 물체와 UiSkin 규칙은 동일 · 최종 후보 v2',font=small,fill=(177,162,140))
    pair.save(ROOT/'qa/mirror_before_after.jpg',quality=86,optimize=True)
    names.append('mirror_before_after.jpg')
    gallery=[]
    assert len(names)<=6
    for name in names:
        src=ROOT/'qa'/name
        assert src.stat().st_size<300000
        shutil.copyfile(src,REPORT/name);shutil.copyfile(src,GALLERY/name)
        gallery.append(dict(filename=name,bytes=src.stat().st_size,sha256=sha(src)))
    result=dict(card=483,status='candidate_not_installed',binding_status='unique_icon_path_not_implemented',items=3,selected_mirror_version='v2',v1_mirror_and_metadata_preserved=True,existing_game_png=png_count,runtime_files_byte_match=len(before),unique_and_base_definition_hashes_match=True,original_hashes_preserved=True,godot_ui_skin_modes=logs,gallery=gallery)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    (ROOT/'verification.json').write_text(text,encoding='utf-8',newline='\n')
    (REPORT/'verification.json').write_text(text,encoding='utf-8',newline='\n')
    print('PASS #483: 3RGBA/1x1, native SHA+v1 preserved, runtime',len(before),'files+PNG42 byte-preserved, actual UiSkin4modes/error0, JPG6')

if __name__=='__main__':
    main()
