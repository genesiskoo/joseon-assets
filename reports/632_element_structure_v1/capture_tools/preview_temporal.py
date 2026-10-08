"""Temporal shape audit using exact Godot AVI counter mapping."""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
p=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--phase',default='after02')
a=ap.parse_args()
m=json.loads((p/(a.phase+'_metadata.json')).read_text(encoding='utf-8'))
offsets=[2,8,14,24]
labels=['fire_strong','cold_strong','lightning_strong','sal_strong']
canvas=Image.new('RGB',(2560,2060),(16,16,16))
f=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
records=[]
for row,label in enumerate(labels):
    hit=m['combat'][label]['hit_events'][0]['frame']
    begin=m['bounds'][label]['BEGIN']
    selected=[begin+hit+d for d in offsets]
    pattern=p/(a.phase+'_'+label+'_temporal_%02d.png')
    vf='select='+ '+'.join('eq(n\\,'+str(n)+')' for n in selected)
    vf=vf.replace('\\\\','\\')
    r=subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(p/(a.phase+'.avi')),'-vf',vf,'-fps_mode','vfr',str(pattern)],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    for col,off in enumerate(offsets):
        path=p/(a.phase+'_'+label+'_temporal_%02d.png'%(col+1))
        im=Image.open(path).convert('RGB').crop((280,80,1000,620)).resize((640,480))
        cell=Image.new('RGB',(640,515),(16,16,16))
        cell.paste(im,(0,35))
        ImageDraw.Draw(cell).text((10,5),label+' hit+%d frames (%.3fs)'%(off,off/60),font=f,fill='white')
        canvas.paste(cell,(col*640,row*515))
        records.append({'label':label,'hit_offset':off,'source_frame_zero_based':selected[col],'file':path.name})
path=p/(a.phase+'_strong_temporal_contact.jpg')
canvas.save(path,quality=88)
(p/(a.phase+'_temporal_manifest.json')).write_text(json.dumps({'frame_mapping':'AVI zero-based N=Engine process counter N','crop_xywh':[280,80,720,540],'frames':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(path))
