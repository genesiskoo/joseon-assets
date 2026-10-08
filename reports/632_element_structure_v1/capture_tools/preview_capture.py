"""#632 normal-frame contact sheets + baseline full engine MP4."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding="utf-8")
BASE=Path(__file__).resolve().parent
OUT=BASE/"deliverables"
OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument("--phase",default="before")
parser.add_argument("--master",action="store_true")
parser.add_argument("--offset",type=int,default=8)
args=parser.parse_args()
meta=json.loads((BASE/(args.phase+"_metadata.json")).read_text(encoding="utf-8"))
font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",20)
contacts=[]
frames=[]
for label in meta["combat"]:
    record=meta["combat"][label]
    offset=record["hit_events"][0]["frame"]+args.offset
    frame=meta["bounds"][label]["BEGIN"]+offset
    target=BASE/(args.phase+"_"+label+"_impact.png")
    result=subprocess.run([shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-i",str(BASE/(args.phase+".avi")),"-vf",f"select=eq(n\\,{frame})","-frames:v","1","-update","1",str(target)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    shot=Image.open(target).convert("RGB")
    cell=Image.new("RGB",(640,395),(16,16,16))
    cell.paste(shot.resize((640,360)),(0,35))
    draw=ImageDraw.Draw(cell)
    name={"fire":"불","cold":"한기","lightning":"벼락","sal":"적 살"}[record["element"]]
    strength="낮음" if record["strength"]=="low" else "강함"
    draw.text((10,6),f"{args.phase} {name} {strength} · 정상1× 실제 명중",font=font,fill="white")
    contacts.append(cell)
    frames.append({"label":label,"offset":offset,"source_frame_zero_based":frame,"png":target.name})
contact=Image.new("RGB",(1280,1580))
for i,cell in enumerate(contacts):
    contact.paste(cell,((i%2)*640,(i//2)*395))
contact_path=BASE/(args.phase+"_impact_ladder.jpg")
contact.save(contact_path,quality=88)
shutil.copy2(BASE/(args.phase+"_fire_strong_impact.png"),BASE/(args.phase+"_peak.png"))
summary={"phase":args.phase,"contact_sheet":str(contact_path),"peak":str(BASE/(args.phase+"_peak.png")),"frames":frames}
if args.master:
    target=OUT/("632_element_structure_"+args.phase+"_engine_capture_60fps.mp4")
    result=subprocess.run([shutil.which("ffmpeg"),"-hide_banner","-y","-i",str(BASE/(args.phase+".avi")),"-c:v","libx264","-preset","fast","-crf","24","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",str(target)],capture_output=True,text=True)
    (BASE/(args.phase+"_master_encode.raw.log")).write_text(result.stdout+result.stderr,encoding="utf-8")
    assert result.returncode==0
    assert target.stat().st_size<10_000_000
    result=subprocess.run([shutil.which("ffmpeg"),"-v","error","-i",str(target),"-f","null","-"],capture_output=True,text=True)
    (BASE/(args.phase+"_master_decode.raw.log")).write_text(result.stdout+result.stderr,encoding="utf-8")
    assert result.returncode==0
    probe=json.loads(subprocess.check_output([shutil.which("ffprobe"),"-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt,color_range:format=duration,size","-of","json",str(target)],text=True))
    stream=next(row for row in probe["streams"] if row["codec_name"]=="h264")
    assert stream["r_frame_rate"]=="60/1" and stream["nb_frames"]==meta["avi_probe"]["streams"][0]["nb_frames"]
    summary["master"]={"path":str(target),"bytes":target.stat().st_size,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"probe":probe}
(BASE/(args.phase+"_preview_manifest.json")).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({key:value for key,value in summary.items() if key!="frames"},ensure_ascii=False))