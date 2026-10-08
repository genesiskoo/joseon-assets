"""#634 actual onset, ongoing after impact, and native end contact sheet."""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--phase',default='before')
a=ap.parse_args()
m=json.loads((BASE/(a.phase+'_metadata.json')).read_text(encoding='utf-8'))
canvas=Image.new('RGB',(1920,2060),(16,16,16))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
rows=[]
for row,label in enumerate(['burn','chill','frozen','sal']):
    record=m['combat'][label]
    states=record['player_status_frames'] if label=='sal' else record['enemy_status_frames']
    bit={'burn':4,'chill':1,'frozen':2,'sal':16}[label]
    active=[i for i,s in enumerate(states) if int(s['mask'])&bit]
    offsets=[active[0]+8,active[0]+({'burn':72,'chill':45,'frozen':60,'sal':72}[label]),active[-1]+9]
    frames=[m['bounds'][label]['BEGIN']+offset for offset in offsets]
    pattern=BASE/(a.phase+'_'+label+'_stage_%02d.png')
    vf='select='+ '+'.join('eq(n\\,'+str(frame)+')' for frame in frames)
    r=subprocess.run([shutil.which('ffmpeg'),'-v','error','-y','-i',str(BASE/(a.phase+'.avi')),'-vf',vf,'-fps_mode','vfr',str(pattern)],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    for col,(offset,frame) in enumerate(zip(offsets,frames)):
        source=BASE/(a.phase+'_'+label+'_stage_%02d.png'%(col+1))
        original=Image.open(source).convert('RGB')
        cell=Image.new('RGB',(640,515),(16,16,16))
        cell.paste(original.crop((280,80,1000,620)).resize((640,480)),(0,35))
        stage=['onset','ongoing',('actual salpuri clear' if label=='sal' else 'native end')][col]
        ImageDraw.Draw(cell).text((10,5),f'{a.phase} {label} {stage} · engine frame {frame}',font=font,fill='white')
        canvas.paste(cell,(col*640,row*515))
        rows.append({'label':label,'stage':stage,'source_frame_zero_based':frame,'segment_frame':offset,'status':states[offset],'png':source.name})
        if col==1 and label=='burn':
            shutil.copy2(source,BASE/(a.phase+'_peak.png'))
path=BASE/(a.phase+'_status_lifecycle_contact.jpg')
canvas.save(path,quality=87)
(BASE/(a.phase+'_preview_manifest.json')).write_text(json.dumps({'phase':a.phase,'frame_mapping':'AVIzero-based N=Engine process counter N','reference':'first active status snapshot, not stale callback frame index','crop_xywh':[280,80,720,540],'stages':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(path))
