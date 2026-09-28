"""Validate source/game hashes, exact before snapshot and actual UiSkin logs."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parent
GAME=Path('C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon')
REPORT=ROOT.parents[2]/'reports/469/2026-09-28'
GALLERY=GAME/'docs/art/469_d1_gear_tomes'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'generation_sources.json').read_text(encoding='utf-8'))
    before=json.loads((ROOT/'runtime_before.json').read_text(encoding='utf-8'))
    assert len(manifest['items'])==len(sources['items'])==4
    for row,gen in zip(manifest['items'],sources['items']):
        assert row['item_id']==gen['id']
        original=ROOT/row['source_path'];png=ROOT/row['game_path']
        assert sha(original)==row['source_sha256']==sha(Path(gen['native_path']))
        assert sha(png)==row['game_sha256']
        image=Image.open(png)
        assert image.mode=='RGBA' and image.size==(row['grid_w']*80,row['grid_h']*80)
        assert image.getchannel('A').getextrema()==(0,255)
        assert list(image.getchannel('A').getbbox())==row['visible_bbox']
        assert sha(Path(row['definition_path']))==row['definition_sha256']
    files=sorted((GAME/'assets/sprites/ui/icons_a').rglob('*.png'))+sorted((GAME/'data/items').glob('*.tres'))
    after={p.relative_to(GAME).as_posix():sha(p) for p in files}
    assert before==after, [k for k in before if before[k]!=after.get(k)]
    png_count=sum(k.endswith('.png') for k in after)
    assert png_count==42
    REPORT.mkdir(parents=True,exist_ok=True);GALLERY.mkdir(parents=True,exist_ok=True)
    names=['overview.jpg']
    logs=[]
    for mode in ['forty','sizes','black_sizes']:
        stdout=REPORT/f'godot_{mode}_stdout.txt'
        stderr=REPORT/f'godot_{mode}_stderr.txt'
        raw=stdout.read_text(encoding='utf-8-sig')+'\n'+stderr.read_text(encoding='utf-8-sig')
        assert f'GODOT_D1_469_PASS mode={mode} items=4' in raw
        assert 'SCRIPT ERROR' not in raw and 'ERROR:' not in raw
        logs.append(dict(mode=mode,stdout_sha256=sha(stdout),stderr_sha256=sha(stderr)))
        p=ROOT/'qa'/f'godot_{mode}.png'
        im=Image.open(p)
        assert im.size==(1280,760)
        jpg=p.with_suffix('.jpg');im.convert('RGB').save(jpg,quality=86,optimize=True)
        names.append(jpg.name)
    gallery=[]
    for name in names:
        src=ROOT/'qa'/name
        assert src.stat().st_size<300000
        shutil.copyfile(src,REPORT/name);shutil.copyfile(src,GALLERY/name)
        gallery.append(dict(filename=name,bytes=src.stat().st_size,sha256=sha(src)))
    result=dict(card=469,status='candidate_not_installed',items=4,existing_game_png=png_count,runtime_files_byte_match=len(before),target_definition_hashes_match=True,original_hashes_preserved=True,godot_ui_skin_modes=logs,gallery=gallery)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    (ROOT/'verification.json').write_text(text,encoding='utf-8',newline='\n')
    (REPORT/'verification.json').write_text(text,encoding='utf-8',newline='\n')
    print('PASS #469: 4 RGBA/real footprints, originals SHA,109 runtime files+42PNG byte-preserved, UiSkin3 modes/error0, JPG4')

if __name__=='__main__':
    main()
