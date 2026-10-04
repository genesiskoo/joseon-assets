import csv,hashlib,json,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageOps
sys.stdout.reconfigure(encoding='utf-8')
key,src=sys.argv[1:]
root=Path(__file__).resolve().parents[3]
base=root/'workbench/production/steam_art_622'
src=Path(src)
raw=base/'raw'/f'{key}.png'
if src.resolve()!=raw.resolve():
    assert not raw.exists(), raw
    shutil.copy2(src,raw)
im=Image.open(raw).convert('RGBA')
plan=json.loads((base/'plan.json').read_text(encoding='utf-8'))
name='logo' if key.startswith('logo_') else '_'.join(key.split('_')[1:-1])
dim=plan['logo'] if name=='logo' else next(a for a in plan['assets'] if a['name']==name)
size=(dim['width'],dim['height'])
if name=='logo':
    export=Image.new('RGBA',size,(0,0,0,0)); small=ImageOps.contain(im,size,Image.Resampling.LANCZOS); export.alpha_composite(small,((size[0]-small.width)//2,(size[1]-small.height)//2)); crop=None
else:
    ratio=size[0]/size[1]
    if im.width/im.height>ratio:
        w=im.height*ratio; crop=[(im.width-w)/2,0,(im.width+w)/2,im.height]
    else:
        h=im.width/ratio; crop=[0,(im.height-h)/2,im.width,(im.height+h)/2]
    export=im.crop(crop).resize(size,Image.Resampling.LANCZOS).convert('RGB')
dst=base/'exports'/f'{key}.png'; export.save(dst)
if name=='small':
    for w,h in ((120,45),(184,69)): export.resize((w,h),Image.Resampling.LANCZOS).save(base/'exports'/f'{key}_{w}x{h}.png')
manifest=base/'outputs.json'
data=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {'card':622,'outputs':{}}
alpha=im.getchannel('A')
data['outputs'][key]={'native_path':str(raw.relative_to(root)).replace('\\','/'),'native_size':list(im.size),'native_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'native_bytes':raw.stat().st_size,'alpha_extrema':list(alpha.getextrema()),'alpha_bbox':alpha.getbbox(),'export_path':str(dst.relative_to(root)).replace('\\','/'),'export_size':list(size),'export_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'mechanical_crop_native_rect':crop,'utc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen_builtin','model':'builtin-default-version-not-exposed','pd_adopted':False,'visual_review':'pending'}
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
csvpath=root/'art-direction/manifests/generations.csv'
with csvpath.open('a',encoding='utf-8',newline='') as f:
    csv.writer(f).writerow([datetime.now(timezone.utc).isoformat(),'image_gen_builtin','builtin-default-version-not-exposed',key,'steam_art','joseon_h1_d072','; '.join(r['path'] for r in plan['refs']),str(raw.relative_to(root)).replace('\\','/'),'pending','Steam #622 candidate; no adoption/game intake/upload; native dimensions and exact export in outputs.json'])
print(json.dumps({'key':key,'native':im.size,'export':size,'alpha':alpha.getextrema(),'bytes':raw.stat().st_size,'path':str(dst),'originals_total_bytes':sum(r['native_bytes'] for r in data['outputs'].values())},ensure_ascii=False))
