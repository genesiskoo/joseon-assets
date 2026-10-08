"""#630 same-frame preview only; geometry and playback are untouched."""
from pathlib import Path
import argparse,json,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument("--phase",default="after",choices=["after","after01"])
args=ap.parse_args()
metadata=json.loads((BASE/(args.phase+"_metadata.json")).read_text(encoding="utf-8"))
before=json.loads((BASE/"before_metadata.json").read_text(encoding="utf-8"))
assert metadata["bounds"]==before["bounds"]
font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",22)
labels=["whirl1","whirl5","whirl10","storm1","storm5","storm10"]
for label in labels:
    frame=metadata["bounds"][label]["BEGIN"]-1+(58 if label.startswith("whirl") else 96)
    for phase in ["before",args.phase]:
        target=BASE/(phase+"_"+label+"_peak.png")
        subprocess.run([shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-i",str(BASE/(phase+".avi")),"-vf",f"select=eq(n\\,{frame})","-frames:v","1","-update","1",str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    if label=="whirl10":
        shutil.copy2(BASE/(args.phase+"_"+label+"_peak.png"),BASE/(args.phase+"_peak.png"))
ladder=Image.new("RGB",(1920,1030),(15,16,17))
draw=ImageDraw.Draw(ladder)
pair=Image.new("RGB",(1280,3090),(15,16,17))
pdraw=ImageDraw.Draw(pair)
for i,label in enumerate(labels):
    korean=("회오리" if label.startswith("whirl") else "칼바람")+" Lv"+label.removeprefix("whirl").removeprefix("storm")
    x,y=(i%3)*640,(i//3)*515
    draw.text((x+12,y+5),args.phase+" "+korean+" · 정상1× 엔진프레임",font=font,fill="white")
    with Image.open(BASE/(args.phase+"_"+label+"_peak.png")) as image:
        ladder.paste(image.crop((280,80,1000,620)).resize((640,480)),(x,y+35))
    py=i*515
    pdraw.text((12,py+5),korean+" 변경 전",font=font,fill="white")
    pdraw.text((652,py+5),korean+" "+args.phase,font=font,fill="white")
    for j,phase in enumerate(["before",args.phase]):
        with Image.open(BASE/(phase+"_"+label+"_peak.png")) as image:
            pair.paste(image.crop((280,80,1000,620)).resize((640,480)),(640*j,py+35))
ladder.save(BASE/(args.phase+"_ladder_contact.jpg"),quality=88,optimize=True)
pair.save(BASE/(args.phase+"_pair_contact.jpg"),quality=86,optimize=True)
print(json.dumps({"phase":args.phase,"peak":str(BASE/(args.phase+"_peak.png")),"ladder_contact":str(BASE/(args.phase+"_ladder_contact.jpg")),"pair_contact":str(BASE/(args.phase+"_pair_contact.jpg"))},ensure_ascii=False))