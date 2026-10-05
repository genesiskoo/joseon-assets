"""#630 true engine combat film: exact frame windows, no retiming."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent
OUT = BASE / "deliverables"
OUT.mkdir(exist_ok=True)
FFMPEG, FFPROBE = shutil.which("ffmpeg"), shutil.which("ffprobe")
FONT = "C:/Windows/Fonts/malgun.ttf"
NAMES = ["whirl1","whirl5","whirl10","storm1","storm5","storm10"]
ap = argparse.ArgumentParser()
ap.add_argument("--before-only", action="store_true")
args = ap.parse_args()
before = json.loads((BASE/"before_metadata.json").read_text(encoding="utf-8"))

def run(command, log_name):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", creationflags=subprocess.CREATE_NO_WINDOW)
    (BASE/log_name).write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"{log_name}: exit {result.returncode}\n{result.stdout}")
    return result.stdout

def check_video(path):
    run([FFMPEG,"-v","error","-i",str(path),"-f","null","-"], path.stem+"_decode.raw.log")
    probe = json.loads(run([FFPROBE,"-v","error","-show_entries","stream=codec_name,width,height,pix_fmt,color_range,r_frame_rate,nb_frames:format=duration,size","-of","json",str(path)], path.stem+"_probe.json"))
    video = next(s for s in probe["streams"] if s["codec_name"] == "h264")
    assert video["r_frame_rate"] == "60/1"
    assert path.stat().st_size < 10_000_000, f"{path.name} exceeds 10MB"
    return {"file":path.name,"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"probe":probe}

def master(phase):
    target = OUT/f"630_whirl_structure_{phase}_engine_capture_60fps.mp4"
    if not target.exists() or target.stat().st_size >= 10_000_000:
        run([FFMPEG,"-hide_banner","-y","-i",str(BASE/(phase+".avi")),"-c:v","libx264","-preset","fast","-crf","24","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",str(target)],phase+"_master_encode.raw.log")
    if target.stat().st_size >= 10_000_000:
        run([FFMPEG,"-hide_banner","-y","-i",str(BASE/(phase+".avi")),"-c:v","libx264","-preset","fast","-crf","28","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",str(target)],phase+"_master_size_retry.raw.log")
    return target

if args.before_only:
    file = check_video(master("before"))
    (OUT/"before_video_manifest.json").write_text(json.dumps({"card":630,"source":before["source_head"],"fps":60,"speed":1.0,"checks":before["checks"],"file":file},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"before_video":file["file"],"bytes":file["bytes"]},ensure_ascii=False))
    raise SystemExit(0)

after = json.loads((BASE/"after_metadata.json").read_text(encoding="utf-8"))
for field in ["capture","bounds","combat","time_scale","movie_fps","capture_script_sha256"]:
    assert before[field] == after[field], "combat or fixture differs: " + field

def caption(label, compare):
    height = 590 if compare else 720
    picture = Image.new("RGBA",(1280,height))
    draw = ImageDraw.Draw(picture)
    draw.rectangle((0,0,1279,71 if compare else 49), fill=(16,17,18,255))
    draw.rectangle((0,height-38,1279,height-1), fill=(16,17,18,255))
    skill = "회오리베기" if label.startswith("whirl") else "칼바람"
    lv = label.removeprefix("whirl").removeprefix("storm")
    draw.text((20,7),f"#630 구조 v1 | {skill} Lv{lv} · 실제 전투 강도 사다리",font=ImageFont.truetype(FONT,24),fill="white")
    if compare:
        draw.text((20,40),"변경 전 · 단색 시트 고리",font=ImageFont.truetype(FONT,21),fill=(235,215,190))
        draw.text((660,40),"변경 후 · 몸의 회전 + 칼끝 궤적",font=ImageFont.truetype(FONT,21),fill=(245,232,199))
    draw.text((20,height-31),"동일 배우/카메라/장비/타격/난수 · 정상1× · 기록60fps는 실시간 성능 측정이 아님",font=ImageFont.truetype(FONT,18),fill=(205,205,205))
    target=BASE/(label+("_pair" if compare else "_actual")+"_caption.png")
    picture.save(target)
    return target

def reel(compare, names, suffix=""):
    target=OUT/("630_whirl_structure_"+("before_after" if compare else "actual")+suffix+"_60fps.mp4")
    inputs=["-i",str(BASE/"before.avi"),"-i",str(BASE/"after.avi")] if compare else ["-i",str(BASE/"after.avi")]
    video_after=1 if compare else 0
    first_caption=2 if compare else 1
    for label in names:
        inputs+=["-loop","1","-framerate","60","-i",str(caption(label,compare))]
    n=len(names)
    graph=[]
    if compare:
        graph.append("[0:v]split="+str(n)+"".join(f"[b{i}]" for i in range(n)))
    graph.append(f"[{video_after}:v]split="+str(n)+"".join(f"[a{i}]" for i in range(n)))
    graph.append(f"[{video_after}:a]asplit="+str(n)+"".join(f"[s{i}]" for i in range(n)))
    for i,label in enumerate(names):
        bounds=before["bounds"][label]
        start,end=bounds["BEGIN"]-1,bounds["END"]-1
        trim=f"trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS"
        if compare:
            graph.append(f"[b{i}]{trim},crop=720:540:280:80,scale=640:480[l{i}]")
            graph.append(f"[a{i}]{trim},crop=720:540:280:80,scale=640:480[r{i}]")
            graph.append(f"[l{i}][r{i}]hstack=inputs=2,pad=1280:590:0:72:black[base{i}]")
        else:
            graph.append(f"[a{i}]{trim}[base{i}]")
        graph.append(f"[base{i}][{first_caption+i}:v]overlay=shortest=1[v{i}]")
        graph.append(f"[s{i}]atrim=start={start/60}:end={end/60},asetpts=PTS-STARTPTS[sound{i}]")
    graph.append("".join(f"[v{i}][sound{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[out][audio]")
    run([FFMPEG,"-hide_banner","-y"]+inputs+["-filter_complex",";".join(graph),"-map","[out]","-map","[audio]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-r","60","-t",str(4*n),"-movflags","+faststart",str(target)],target.stem+"_encode.raw.log")
    return target

paths=[]
for compare in [True,False]:
    target=reel(compare,NAMES)
    if target.stat().st_size < 10_000_000:
        paths.append(target)
    else:
        for group,suffix in [(NAMES[:3],"_whirl"),(NAMES[3:],"_storm")]:
            paths.append(reel(compare,group,suffix))
        # Preserve oversized diagnostic only in local scratch, outside deliverables.
        target.replace(BASE/(target.stem+"_oversize.mp4"))
paths += [master("before"),master("after")]
files=[check_video(path) for path in paths]
for file in files:
    stream=next(s for s in file["probe"]["streams"] if s["codec_name"]=="h264")
    if "engine_capture" not in file["file"]:
        assert int(stream["nb_frames"]) == (720 if "_whirl_60fps" in file["file"] or "_storm_60fps" in file["file"] else 1440)
manifest={"card":630,"fps":60,"speed":1.0,"capture_check":f"before{before['checks']}/{before['checks']};after{after['checks']}/{after['checks']} PASS","source_before":before["source_head"],"source_hashes_before":before["source_hashes"],"source_hashes_after":after["source_hashes"],"capture_mode":"Godot MovieMaker, actual actor/combat; not realtime performance evidence","comparison_crop_xywh":[280,80,720,540],"capture":before["capture"],"bounds":before["bounds"],"combat":before["combat"],"invariant_equal":"all fixture and combat fields including per-frame actor/camera positions exactly equal","raw_avi":"local intermediate; MP4 full engine before/after is preserved","files":files}
(OUT/"video_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"videos":[{"file":f["file"],"bytes":f["bytes"]} for f in files],"invariant_equal":True},ensure_ascii=False),flush=True)