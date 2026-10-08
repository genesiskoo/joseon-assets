"""Native baked Blender RGBA atlas playback, labelled separately from actual Godot capture."""
from pathlib import Path
import argparse,json,subprocess,shutil,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
ap=argparse.ArgumentParser(); ap.add_argument('--fire-sheet',required=True); ap.add_argument('--fire-meta',required=True); ap.add_argument('--sal-sheet',required=True); ap.add_argument('--sal-meta',required=True); args=ap.parse_args()
base=Path(__file__).resolve().parent; frames=base/'blender_preview_frames'; frames.mkdir(exist_ok=True)
font='C:/Windows/Fonts/malgun.ttf'; rows=[]
for kind in ['fire','sal']:
    sheet=Path(getattr(args,kind+'_sheet')); meta_path=Path(getattr(args,kind+'_meta')); meta=json.loads(meta_path.read_text(encoding='utf-8')); image=Image.open(sheet).convert('RGBA')
    assert image.size==(meta['cols']*meta['fw'],meta['rows']*meta['fh']) and meta['loop'] and meta['total']>=16
    rows.append({'kind':kind,'image':image,'meta':meta,'sheet':str(sheet),'sheet_sha256':hashlib.sha256(sheet.read_bytes()).hexdigest(),'meta_path':str(meta_path),'meta_sha256':hashlib.sha256(meta_path.read_bytes()).hexdigest()})
fps=24; count=96
for n in range(count):
    out=Image.new('RGBA',(960,600),(15,18,24,255)); draw=ImageDraw.Draw(out)
    draw.text((24,15),'#680 Blender 볼륨 렌더 시트 · RGBA 프레임 재생',font=ImageFont.truetype(font,27),fill='white')
    draw.text((24,55),'아래는 구운 재료 미리보기 · 실제 Godot 결합 효과는 별도 영상',font=ImageFont.truetype(font,19),fill=(190,190,196))
    for i,row in enumerate(rows):
        x=24+i*480; y=150; size=432; meta=row['meta']; cell=int(n*float(meta['fps'])/fps)%meta['total']; cx=(cell%meta['cols'])*meta['fw']; cy=(cell//meta['cols'])*meta['fh']
        for yy in range(0,size,24):
            for xx in range(0,size,24):
                shade=(25,27,32,255) if (xx//24+yy//24)%2 else (42,44,49,255); draw.rectangle((x+xx,y+yy,x+xx+23,y+yy+23),fill=shade)
        frame=row['image'].crop((cx,cy,cx+meta['fw'],cy+meta['fh']))
        ratio=min(size/frame.width,size/frame.height); frame=frame.resize((round(frame.width*ratio),round(frame.height*ratio)),Image.Resampling.LANCZOS)
        out.alpha_composite(frame,(x+(size-frame.width)//2,y+(size-frame.height)//2))
        name='화염 후류' if row['kind']=='fire' else '살 안개'; draw.text((x,112),f'{name} · {meta["total"]}프레임 / {meta["fps"]:g}fps',font=ImageFont.truetype(font,22),fill=(232,218,194))
    out.convert('RGB').save(frames/f'{n:04d}.png')
out=base/'deliverables/680_blender_baked_atlas_preview_24fps.mp4'
r=subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-y','-framerate',str(fps),'-i',str(frames/'%04d.png'),'-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW); (base/'blender_preview_encode.raw.log').write_bytes(r.stdout); assert r.returncode==0
r=subprocess.run([shutil.which('ffmpeg'),'-v','error','-i',str(out),'-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW); (base/'blender_preview_decode.raw.log').write_bytes(r.stdout); assert r.returncode==0 and out.stat().st_size<10_000_000
manifest={'card':680,'kind':'offline Blender baked volume material preview, not Godot gameplay','fps':fps,'frames':count,'seconds':count/fps,'normal_source_speed':True,'display_aspect':'native cropped fw/fh, no stretch','sources':[{k:v for k,v in row.items() if k!='image'} for row in rows],'video':{'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'full_decode_exit':0}}
(base/'deliverables/blender_atlas_preview_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest['video']))
