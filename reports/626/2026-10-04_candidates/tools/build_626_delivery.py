import hashlib, json, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
root=Path('C:/workspace/joseon/._tmp')
records=json.loads((root/'626_generation_registry.json').read_text(encoding='utf-8'))+[json.loads(p.read_text(encoding='utf-8')) for p in sorted((root/'626_generation_parts').glob('*.json'))]
assert len(records)==24 and len({r['source'] for r in records})==24
out=root/'626_delivery_20261004'
out.mkdir(exist_ok=False)
production=out/'production';production.mkdir()
report=out/'review';report.mkdir()
raw=out/'raw';raw.mkdir()
base_keys=['stone_large','stone_small','dirt','mine_cinder','bone_grit','damp_organic']
decal_keys=['heukrang_scatter','beom_root_scatter','mine_scrap_scatter','bongmil_seal_scatter']
labels={'stone_large':'大石 큰 석재','stone_small':'礫 작은 석재','dirt':'土 다져진 흙','mine_cinder':'滓 광재','bone_grit':'骨 뼈 부스러기','damp_organic':'濕 습한 유기물','heukrang_scatter':'흑랑굴 잔해','beom_root_scatter':'범굴 뿌리·낙엽','mine_scrap_scatter':'광산 쇳조각','bongmil_seal_scatter':'봉밀굴 봉인 종이'}
selected={}
for r in records:
    k=(r['set'],r['material'])
    if k not in selected or selected[k]['revision']<r['revision']:selected[k]=r
assert len(selected)==20
image_cache={};delivery=[];native=[];metrics=[];alpha=[]
for r in records:
    p=Path(r['source']);im=Image.open(p)
    native.append({**{k:v for k,v in r.items() if k not in ('source','refs')},'native_file':f"native/{r['set']}/{r['material']}_r{r['revision']}.png",'source_filename':p.name,'native_size':list(im.size),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'references':[{'source_filename':Path(ref).name,'sha256':hashlib.sha256(Path(ref).read_bytes()).hexdigest()} for ref in r['refs']]})
for k,r in selected.items():
    set_name,material=k
    src=Image.open(r['source']).convert('RGBA' if r['transparent_background'] else 'RGB')
    im=src.resize((1024,1024),Image.Resampling.LANCZOS)
    kind='decals' if r['transparent_background'] else 'textures'
    path=production/set_name/kind/(material+'.png');path.parent.mkdir(parents=True,exist_ok=True);im.save(path,optimize=True)
    image_cache[k]=im
    source_sha=hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()
    row={'set':set_name,'material':material,'kind':kind,'revision':r['revision'],'file':path.relative_to(production).as_posix(),'native_file':f"native/{set_name}/{material}_r{r['revision']}.png",'source_sha256':source_sha,'source_size':list(src.size),'export_size':[1024,1024],'export_mode':im.mode,'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'export_bytes':path.stat().st_size,'operation':'Mechanical Pillow LANCZOS resize only; no repaint, color grade, lighting or seam modification.'}
    delivery.append(row)
    a=np.asarray(im,dtype=float)
    if not r['transparent_background']:
        xx=float(np.abs(a[:,0]-a[:,-1]).mean());yy=float(np.abs(a[0]-a[-1]).mean())
        ix=float(np.abs(a[:,1:]-a[:,:-1]).mean());iy=float(np.abs(a[1:]-a[:-1]).mean())
        hsv=np.asarray(im.convert('HSV'),dtype=float)/255
        metrics.append({'set':set_name,'material':material,'rgb_mean':a.mean(axis=(0,1)).round(3).tolist(),'s_mean':float(hsv[:,:,1].mean()),'v_mean':float(hsv[:,:,2].mean()),'wrap_mae_x':xx,'wrap_mae_y':yy,'internal_neighbor_mae_x':ix,'internal_neighbor_mae_y':iy,'ratio_x':xx/max(ix,0.001),'ratio_y':yy/max(iy,0.001),'assessment':'Diagnostic numbers, not a mathematical seamlessness certification. Review cyclic offset and repeated previews.'})
    else:
        aa=a[:,:,3];active=aa>=16;ys,xs=np.where(active)
        hsv=np.asarray(im.convert('RGB').convert('HSV'),dtype=float)/255
        colors=(hsv[:,:,1]>.65)&(hsv[:,:,2]>.5)
        border=np.concatenate((aa[0],aa[-1],aa[:,0],aa[:,-1]))
        assert border.max()==0 and aa.max()==255
        alpha.append({'set':set_name,'material':material,'alpha_min':int(aa.min()),'alpha_max':int(aa.max()),'border_alpha_max':int(border.max()),'active_alpha16_fraction':float(active.mean()),'bbox_alpha16':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'bright_saturated_alpha_ge128':int((colors&(aa>=128)).sum()),'bright_saturated_alpha_1_127':int((colors&(aa>0)&(aa<128)).sum()),'assessment':'Native partial-alpha color fringes retained; tested over white/black and earth. No alpha thresholding or semantic pixel repair.'})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
reviews=[]
def save(im,name,sources):
    path=report/name
    for q in (92,88,84,80,76,72,68,64,60):
        im.save(path,quality=q,optimize=True)
        if path.stat().st_size<=300000:break
    assert im.width<=1280 and path.stat().st_size<=300000
    reviews.append({'file':name,'size':list(im.size),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sources':sources,'operation':'Layout/compression, cyclic offsets, alpha proof compositing only; no retouch.'})
def header(im,text):ImageDraw.Draw(im).text((16,8),text,font=font,fill='white')
sheet=Image.new('RGB',(1280,598),'#202020');header(sheet,'#626 바닥 재질 12장 · A 흙빛 회갈색 / B 더 어두운 회갈색 · 후보')
d=ImageDraw.Draw(sheet)
for row,set_name in enumerate(('A','B')):
    y=50+row*265
    for col,material in enumerate(base_keys):
        x=10+col*210
        d.text((x,y),set_name+' '+labels[material],font=small,fill='#e7d9b4')
        sheet.paste(image_cache[(set_name,material)].resize((200,200),Image.Resampling.LANCZOS),(x,y+29))
save(sheet,'01_materials_ab.jpg',[r['file'] for r in delivery if r['kind']=='textures'])
biomes=[('흑랑굴','dirt','heukrang_scatter'),('범굴','damp_organic','beom_root_scatter'),('쇠부리 광산','mine_cinder','mine_scrap_scatter'),('봉밀굴','stone_large','bongmil_seal_scatter')]
for pair,name in ((biomes[:2],'02_heukrang_beom_ab.jpg'),(biomes[2:],'03_mine_bongmil_ab.jpg')):
    sheet=Image.new('RGB',(1280,1370),'#202020');header(sheet,'#626 지역별 A/B · 평면 알파 합성 · 실제 게임 셰이더 화면 아님')
    d=ImageDraw.Draw(sheet);sources=[]
    for row,(area,base,decal) in enumerate(pair):
        for col,set_name in enumerate(('A','B')):
            x=15+col*640;y=50+row*655
            d.text((x,y),set_name+' '+area+' · '+labels[base]+' + '+labels[decal],font=small,fill='#e7d9b4')
            im=image_cache[(set_name,base)].convert('RGBA');im.alpha_composite(image_cache[(set_name,decal)])
            sheet.paste(im.convert('RGB').resize((610,610),Image.Resampling.LANCZOS),(x,y+29))
            sources += [next(r['file'] for r in delivery if r['set']==set_name and r['material']==m) for m in (base,decal)]
    save(sheet,name,sources)
sheet=Image.new('RGB',(1280,765),'#202020');header(sheet,'#626 투명 데칼 8장 · 체크 배경에서 알파 확인 · 새 원화 미채택')
d=ImageDraw.Draw(sheet)
checker=Image.new('RGBA',(300,300));cd=ImageDraw.Draw(checker)
for y in range(0,300,25):
    for x in range(0,300,25):cd.rectangle((x,y,x+24,y+24),fill='#777777' if (x//25+y//25)%2 else '#999999')
for row,set_name in enumerate(('A','B')):
    for col,material in enumerate(decal_keys):
        x=10+col*320;y=50+row*355
        d.text((x,y),set_name+' '+labels[material],font=small,fill='#e7d9b4')
        im=checker.copy();im.alpha_composite(image_cache[(set_name,material)].resize((300,300),Image.Resampling.LANCZOS));sheet.paste(im.convert('RGB'),(x,y+29))
save(sheet,'04_alpha_decals.jpg',[r['file'] for r in delivery if r['kind']=='decals'])
sheet=Image.new('RGB',(1280,598),'#202020');header(sheet,'#626 이음새 검수 · 1024 결과를 가로·세로 512px 순환 이동')
d=ImageDraw.Draw(sheet)
for row,set_name in enumerate(('A','B')):
    for col,material in enumerate(base_keys):
        x=10+col*210;y=50+row*265
        d.text((x,y),set_name+' '+labels[material],font=small,fill='#e7d9b4')
        offset=ImageChops.offset(image_cache[(set_name,material)],512,512)
        sheet.paste(offset.resize((200,200),Image.Resampling.LANCZOS),(x,y+29))
save(sheet,'05_half_offset_seams.jpg',[r['file'] for r in delivery if r['kind']=='textures'])
sheet=Image.new('RGB',(1280,1020),'#202020');header(sheet,'#626 붓질 변경 전/후 + 큰 석재 2×2 반복 · 픽셀 이음새는 별도 확인')
d=ImageDraw.Draw(sheet);sources=[]
for col,set_name in enumerate(('A','B')):
    x=15+col*640
    r1=next(r for r in records if r['set']==set_name and r['material']=='stone_large' and r['revision']==1)
    for sub,(revision,im) in enumerate(((1,Image.open(r1['source']).convert('RGB')),(2,image_cache[(set_name,'stone_large')]))):
        xx=x+sub*310;d.text((xx,51),f'{set_name} R{revision} '+('변경 전' if revision==1 else '변경 후'),font=small,fill='#e7d9b4')
        sheet.paste(im.resize((300,300),Image.Resampling.LANCZOS),(xx,80))
    thumb=image_cache[(set_name,'stone_large')].resize((300,300),Image.Resampling.LANCZOS)
    d.text((x,392),set_name+' R2 2×2 반복',font=small,fill='#e7d9b4')
    for yy in (0,300):
        for xx in (0,300):sheet.paste(thumb,(x+xx,420+yy))
    sources += [f"native/{set_name}/stone_large_r1.png",f"{set_name}/textures/stone_large.png"]
save(sheet,'06_style_before_after_repeat.jpg',sources)
manifest={'card':626,'candidate_only':True,'game_intake':False,'tool':'Codex builtin image_gen','model_version':'not exposed by tool','native_count':24,'native_bytes':sum(r['bytes'] for r in native),'native_max_bytes':max(r['bytes'] for r in native),'native_sizes':sorted({tuple(r['native_size']) for r in native}),'candidate_exports':delivery,'reviews':reviews,'floor_metrics':metrics,'alpha_metrics':alpha,'material_span_recommended_units':2.5,'texel_density_recommended_px_per_unit':409.6,'card195_span_alternative_units':3,'card195_density_alternative_px_per_unit':1024/3,'density_note':'#120 band400~900. 3m is below band;2.5m recommendation must be evaluated in #195. No engine density test has been run for these candidates.'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(out/'native_generation.json').write_text(json.dumps({'card':626,'candidate_only':True,'records':native},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
archive=raw/'626_dungeon_materials_native_20261004.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for r,n in zip(records,native):z.write(r['source'],n['native_file'])
    z.write(out/'native_generation.json','native_generation.json')
    z.write(root/'626_plan.json','plan.json')
    style=Path('C:/Users/FORYOUCOM/.codex/worktrees/266-peddler-gamble/joseon/assets/models/tilekit_cave/floor_floor_tex_raw_0.png')
    z.write(style,'references/existing_cave_floor.png')
    for p in (root/'626_qa_all_bases').glob('*.jpg'):z.write(p,'qa/native/'+p.name)
    z.write(root/'626_qa_all_bases/metrics.json','qa/native/metrics.json')
archive_record={'file':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'native_images':24,'originals_retained_at_generated_image_paths':True,'release_pending':True}
(raw/'archive.json').write_text(json.dumps(archive_record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'native_count':24,'native_bytes':manifest['native_bytes'],'exports':len(delivery),'export_bytes':sum(r['export_bytes'] for r in delivery),'review_count':len(reviews),'review_bytes':sum(r['bytes'] for r in reviews),'archive':archive_record,'alpha_borders_all_zero':all(r['border_alpha_max']==0 for r in alpha),'wrap_max_rgb_mae':max(max(r['wrap_mae_x'],r['wrap_mae_y']) for r in metrics)},ensure_ascii=False))
