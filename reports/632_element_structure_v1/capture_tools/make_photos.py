"""Six synchronized 1280px photo proofs, same actual engine frames before/after."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
OUT=BASE/'deliverables'/'photos'
ap=argparse.ArgumentParser()
ap.add_argument('--phase',default='after03')
ap.add_argument('--offset',type=int,default=8)
ap.add_argument('--dry-run',action='store_true')
a=ap.parse_args()
metas={phase:json.loads((BASE/(phase+'_metadata.json')).read_text(encoding='utf-8')) for phase in ['before',a.phase]}
assert metas['before']['bounds']==metas[a.phase]['bounds']
assert metas['before']['combat']==metas[a.phase]['combat']
labels=['fire_strong','cold_strong','sal_strong']
rows=[]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
for label in labels:
    m=metas['before']
    frame=m['bounds'][label]['BEGIN']+m['combat'][label]['hit_events'][0]['frame']+a.offset
    for phase,word in [('before','변경 전'),(a.phase,'변경 후')]:
        output=OUT/(('before' if phase=='before' else 'after')+'_'+label+'.jpg')
        rows.append({'phase':phase,'label':label,'source_frame_zero_based':frame,'hit_offset_frames':a.offset,'event_reference':'first native HP-loss snapshot','jpg':output.name})
        if a.dry_run:
            continue
        OUT.mkdir(parents=True,exist_ok=True)
        raw=BASE/(phase+'_'+label+'_photo_peak.png')
        r=subprocess.run([shutil.which('ffmpeg'),'-v','error','-y','-i',str(BASE/(phase+'.avi')),'-vf',f'select=eq(n\\,{frame})','-frames:v','1','-update','1',str(raw)],capture_output=True,text=True)
        assert r.returncode==0,r.stderr
        picture=Image.new('RGB',(1280,760),(16,17,18))
        picture.paste(Image.open(raw).convert('RGB'),(0,40))
        element={'fire':'불 부적','cold':'한기 부적','sal':'적 살 투사체'}[label.split('_')[0]]
        ImageDraw.Draw(picture).text((16,6),f'#632 {word} · {element} 강함 · 동일 실제 엔진 frame {frame} · 정상 1×',font=font,fill='white')
        for quality in [90,86,82,78,74]:
            picture.save(output,quality=quality,optimize=True)
            if output.stat().st_size<=300_000:
                break
        assert output.stat().st_size<=300_000
        rows[-1].update({'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_png_sha256':hashlib.sha256(raw.read_bytes()).hexdigest()})
if not a.dry_run:
    (OUT/'photos_manifest.json').write_text(json.dumps({'card':632,'frame_mapping':'AVI zero-based N=Engine process counter N','width':1280,'max_bytes':300000,'photos':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'same_frame_pairs':rows},ensure_ascii=False))
