from pathlib import Path
import argparse,json,shutil,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(); ap.add_argument('--phase',default='before'); a=ap.parse_args()
m=json.loads((BASE/(a.phase+'_metadata.json')).read_text(encoding='utf-8'))
canvas=Image.new('RGB',(3200,2060),(16,16,16)); font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
rows=[]
for row,label in enumerate(['fire','cold','lightning','sal']):
    r=m['combat'][label]; born=r['shots'][0]['born_frame']; hit=r['hit_events'][0]['frame']
    states=r['player_status_frames' if label=='sal' else 'enemy_status_frames']
    bit={'fire':4,'cold':3,'lightning':0,'sal':16}[label]
    active=[i for i,s in enumerate(states) if int(s['mask'])&bit]
    offsets=[born+1,(born+hit)//2,hit+8,hit+60,(active[-1]+9 if active else hit+120)]
    stages=['first observed flight+1','native flight midpoint','first HP loss+8','actual ongoing+60','native full expiry' if active else 'native after-hit']
    frames=[m['bounds'][label]['BEGIN']+i for i in offsets]
    unique=sorted(set(frames)); pattern=BASE/(a.phase+'_'+label+'_flightstage_%02d.png')
    vf='select='+'+'.join('eq(n\\,'+str(f)+')' for f in unique)
    run=subprocess.run([shutil.which('ffmpeg'),'-v','error','-y','-i',str(BASE/(a.phase+'.avi')),'-vf',vf,'-fps_mode','vfr',str(pattern)],capture_output=True,text=True)
    assert run.returncode==0,run.stderr
    files={f:BASE/(a.phase+'_'+label+'_flightstage_%02d.png'%(i+1)) for i,f in enumerate(unique)}
    for col,(offset,frame,stage) in enumerate(zip(offsets,frames,stages)):
        original=Image.open(files[frame]).convert('RGB'); cell=Image.new('RGB',(640,515),(16,16,16))
        cell.paste(original.crop((280,80,1000,620)).resize((640,480)),(0,35))
        ImageDraw.Draw(cell).text((8,5),f'{a.phase} {label} {stage} · frame{frame}',font=font,fill='white')
        canvas.paste(cell,(col*640,row*515)); rows.append({'element':label,'stage':stage,'source_frame_zero_based':frame,'segment_frame':offset,'png':files[frame].name,'native_status':states[offset]})
        if label=='fire' and col==1: shutil.copy2(files[frame],BASE/(a.phase+'_flight_peak.png'))
path=BASE/(a.phase+'_flight_lifecycle_contact.jpg'); canvas.save(path,quality=86)
(BASE/(a.phase+'_flight_preview_manifest.json')).write_text(json.dumps({'phase':a.phase,'frame_mapping':'AVI zero-based N=Engine process counter N','fixture':'isolated actual first shot; stationary5u; pull clock held only in capture','first_flight_reference':'first observed real projectile after ready +1; fixed seed applied before collision','same_timeline_note':'native travel and hit time intentionally differ AFTER; stage frames explicitly labeled','crop_xywh':[280,80,720,540],'stages':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(str(path))