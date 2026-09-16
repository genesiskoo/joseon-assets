"""Create frame-accurate 4fps review sheets and technical probes from 24fps clips."""
import argparse,json,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('clip');p.add_argument('--ffmpeg',required=True);p.add_argument('--ffprobe',required=True)
a=p.parse_args();source=a.root/'clips'/f'{a.clip}.mp4';review=a.root/'review';review.mkdir(exist_ok=True)
probe=json.loads(subprocess.check_output([a.ffprobe,'-v','error','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames','-of','json',str(source)],text=True))
v=[s for s in probe['streams'] if s['codec_type']=='video'][0];assert v['r_frame_rate']=='24/1',probe
(a.root/'metadata'/f'{a.clip}_ffprobe.json').write_text(json.dumps(probe,indent=2),encoding='utf-8')
subprocess.run([a.ffmpeg,'-v','error','-i',str(source),'-f','null','-'],check=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
with tempfile.TemporaryDirectory(prefix='joseon_r2_qc_') as temp:
 subprocess.run([a.ffmpeg,'-v','error','-i',str(source),'-vf',r'select=not(mod(n\,6))','-fps_mode','vfr',str(Path(temp)/'f_%04d.png')],check=True)
 frames=sorted(Path(temp).glob('*.png'))
 for page,begin in enumerate(range(0,len(frames),20),1):
  chunk=frames[begin:begin+20];w,h,bar,cols=480,270,30,4;rows=(len(chunk)+3)//4
  sheet=Image.new('RGB',(cols*w,rows*(h+bar)),'#101010');draw=ImageDraw.Draw(sheet)
  for j,path in enumerate(chunk):
   idx=begin+j;im=Image.open(path).convert('RGB');x=j%cols*w;y=j//cols*(h+bar)
   sheet.paste(im.resize((w,h),Image.Resampling.LANCZOS),(x,y+bar));draw.text((x+8,y+3),f'{a.clip} {idx*0.25:05.2f}s',font=font,fill='white')
   im.save(review/f'{a.clip}_{idx*0.25:05.2f}s.jpg',quality=94)
  sheet.save(review/f'{a.clip}_contact_{page}.jpg',quality=94)
 print(json.dumps({'clip':a.clip,'sample_frames':len(frames),'pages':page,'probe':probe,'decode':'passed'}))
