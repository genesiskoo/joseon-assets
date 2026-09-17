"""Build the approved 50-second H1 previs locally. Native remote renderer failed.
Only authored narrative/title text is burned in; no transcription or speech.
Repro: python assemble_local.py --ffmpeg <ffmpeg> --ffprobe <ffprobe>
"""
import argparse, json, subprocess, hashlib, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ap=argparse.ArgumentParser()
ap.add_argument("--ffmpeg",required=True); ap.add_argument("--ffprobe",required=True)
a=ap.parse_args()
edit=Path(__file__).resolve().parent; root=edit.parent
edl=json.loads((edit/"edl.json").read_text(encoding="utf-8-sig"))
segments=list(edl["EDL"])
segments.insert(11,{"id":"H11","file":None,"from":0,"dur":4,"at":43})
assert len(segments)==13
cursor=0
for s in segments:
    assert abs(s["at"]-cursor)<1e-6
    cursor+=s["dur"]
assert cursor==50
font=edit/"fonts"/"NanumMyeongjo-Regular.ttf"
assert font.exists()
# ASS is authored graphics timing, not speech transcription.
def stamp(t):
    cs=round(t*100)
    return f"{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}"
header="""[Script Info]
Title: Joseon Hunters H1 opening previs
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Saseol,NanumMyeongjo,34,&H00D2E6F0,&H00D2E6F0,&H001A1411,&H80000000,0,0,0,0,100,100,0,0,1,1.1,2,8,80,80,0,1
Style: Title,NanumMyeongjo,88,&H00A4CBDF,&H00A4CBDF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: English,NanumMyeongjo,23,&H007B94A4,&H007B94A4,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
events=[]
for c in edl["CAPTIONS"]:
    y=583 if "\n" in c["text"] else 621
    body=c["text"].replace("\n",r"\N")
    events.append(f'Dialogue: 0,{stamp(c["at"])},{stamp(c["at"]+c["dur"])},Saseol,,0,0,0,,'
                  +rf'{{\an8\pos(640,{y})\fad(250,250)}}'+body)
events.extend([
    r"Dialogue: 1,0:00:43.00,0:00:47.00,Title,,0,0,0,,{\an5\pos(640,346)\fad(600,400)}조선헌터스",
    r"Dialogue: 1,0:00:43.00,0:00:47.00,English,,0,0,0,,{\an5\pos(640,428)\fad(600,400)}JOSEON HUNTERS"
])
(edit/"saseol_title.ass").write_text(header+"\n".join(events)+"\n",encoding="utf-8-sig")
cmd=[a.ffmpeg,"-hide_banner","-y","-filter_complex_threads","2"]
input_files=[]
filters=[]
for i,s in enumerate(segments):
    if s["id"]=="H11":
        cmd+=["-f","lavfi","-i","color=c=0x080c13:size=1280x720:rate=24:duration=4"]
    else:
        file=root/"clips"/Path(s["file"]).name
        if s["id"]=="H12":
            file=root/"runtime"/"H12_actual_game_start_GT1_3s_720p24.mp4"
        assert file.exists(),file
        input_files.append(file)
        cmd+=["-i",str(file)]
    start=round(s["from"]*24); end=start+round(s["dur"]*24)
    chain=f"[{i}:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,setsar=1,format=yuv420p"
    if s["id"]=="H01": chain+=",fade=t=in:st=0:d=0.35"
    if s["id"]=="H10": chain+=",fade=t=out:st=3.75:d=0.25"
    if s["id"]=="H12": chain+=",fade=t=in:st=0:d=0.5"
    filters.append(chain+f"[v{i}]")
cmd+=["-i",str(edit/"temp_soundtrack.wav")]
filters.append("".join(f"[v{i}]" for i in range(13))+"concat=n=13:v=1:a=0[cut]")
draw=[]
for c in edl["CAPTIONS"]:
    two="\n" in c["text"]; y,h=(570,150) if two else (604,116)
    draw.append(f"drawbox=x=0:y={y}:w=1280:h={h}:color=0x05070b@0.32:t=fill:enable='between(t,{c['at']},{c['at']+c['dur']})'")
draw.append("drawbox=x=530:y=266:w=220:h=1:color=0x756447@0.8:t=fill:enable='between(t,43.25,46.6)'")
draw.append("ass=filename=saseol_title.ass:fontsdir=fonts")
filters.append("[cut]"+",".join(draw)+"[out]")
filters.append("[13:a]atrim=duration=50,asetpts=PTS-STARTPTS,afade=t=out:st=49.5:d=0.5[aout]")
(edit/"filters.ffscript").write_text(";\n".join(filters),encoding="utf-8")
out=edit/"joseon_h1_opening_previs_50s_v001.mp4"
cmd+=["-filter_complex_script","filters.ffscript","-map","[out]","-map","[aout]",
      "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-r","24",
      "-frames:v","1200","-threads","4","-c:a","aac","-b:a","192k","-ar","48000",
      "-t","50","-movflags","+faststart",str(out)]
with (edit/"render_local.log").open("w",encoding="utf-8") as log:
    subprocess.run(cmd,cwd=edit,stdout=log,stderr=subprocess.STDOUT,check=True)
probe=json.loads(subprocess.check_output([a.ffprobe,"-v","error","-show_entries",
    "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels:format=duration,size",
    "-of","json",str(out)],text=True))
v=next(x for x in probe["streams"] if x["codec_type"]=="video")
audio=[x for x in probe["streams"] if x["codec_type"]=="audio"]
assert(v["width"],v["height"],v["r_frame_rate"],v["nb_frames"])==(1280,720,"24/1","1200"),probe
assert len(audio)==1 and audio[0]["channels"]==2,probe
assert abs(float(probe["format"]["duration"])-50)<1/24,probe
subprocess.run([a.ffmpeg,"-v","error","-i",str(out),"-f","null","-"],check=True)
audit={"renderer":"local FFmpeg 8.1 libx264/libass; remote Higgsedit calls failed serialization before an output was recovered",
       "native_higgsedit_script":"edit.mjs is prepared but not used to render this delivered MP4",
       "probe":probe,"full_decode":"passed","frame_target":1200,"duration_target":50,
       "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"edit_segments":segments,
       "qa_scope":"technical validation and sampled frames, not continuous normal-speed audiovisual review"}
(root/"metadata"/"render_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
times=[2,6,10.5,15.5,18.5,20.5,22.5,25.5,30,35.75,41,45,48.5]
sheet=Image.new("RGB",(3*480,5*300),"#101010")
d=ImageDraw.Draw(sheet); label=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",18)
for j,t in enumerate(times):
    frame=root/"review"/f"FINAL_{t:05.2f}s.png"
    subprocess.run([a.ffmpeg,"-v","error","-ss",str(t),"-i",str(out),"-frames:v","1","-update","1","-y",str(frame)],check=True)
    im=Image.open(frame).convert("RGB")
    x=j%3*480;y=j//3*300
    sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y+30))
    d.text((x+8,y+5),f"PREVIS {t:.2f}s",fill="white",font=label)
sheet.save(root/"review"/"FINAL_contact.jpg",quality=94)
print(json.dumps({"output":str(out),"probe":probe,"sha256":audit["sha256"]},ensure_ascii=False))

