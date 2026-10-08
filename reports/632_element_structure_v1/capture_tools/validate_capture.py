"""#632 capture validation and immutable exact comparison metadata."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
LABELS=[element+"_"+strength for element in ["fire","cold","lightning","sal"] for strength in ["low","strong"]]
parser=argparse.ArgumentParser()
parser.add_argument("phase")
args=parser.parse_args()
assert re.fullmatch(r"before|after[0-9]*",args.phase), "invalid capture phase"
is_after=args.phase.startswith("after")
raw_path=BASE/(args.phase+".raw.log")
raw=raw_path.read_text(encoding="utf-8-sig",errors="replace")
result=re.search(r"VIDEO632 phase="+args.phase+r" checks=(\d+) fails=0 PASS",raw)
assert result, "capture did not finish with PASS"
errors=[line for line in raw.splitlines() if re.search(r"SCRIPT ERROR|Parse Error|Compile Error|SHADER ERROR|^ERROR:",line) and not re.match(r"ERROR: \d+ resources still in use at exit",line)]
assert not errors, "\n".join(errors)
fixture=json.loads(re.search(r"^FIXTURE632 (.+)$",raw,re.M)[1])
records={}
for line in re.findall(r"^COMBAT632 (.+)$",raw,re.M):
    record=json.loads(line)
    assert record["segment"] not in records
    records[record["segment"]]=record
assert list(records)==LABELS
bounds={}
for label,edge,frame in re.findall(r"^CAPTURE (\S+) (BEGIN|END) (\d+)$",raw,re.M):
    bounds.setdefault(label,{})[edge]=int(frame)
for label,record in records.items():
    assert bounds[label]["END"]-bounds[label]["BEGIN"]==180
    for field in ["actor_frames","camera_frames","target_frames","player_status_frames","enemy_status_frames","talisman_cd_frames","time_scale_frames"]:
        assert len(record[field])==180,(label,field)
    assert record["hit_events"] and len(record["shots"])==1
    shot=record["shots"][0]
    assert shot["seed"]==632 and shot["born_frame"]<shot["exit_frame"]
    assert shot["final_rng"] != shot["initial_rng"], "actual damage RNG must be consumed"
    assert record["mp_before"]==record["mp_after"], "belt throws/enemy shots do not debit MP"
    assert record["state_rng_before"]==record["state_rng_after"]
    assert len(record["enemy_rng_before"])==len(record["enemy_rng_after"])==len(record["positions"])
    if record["element"] != "sal":
        assert record["stack_before"]==5 and record["stack_after"]==4
        assert shot["hits"]==(1 if record["element"]=="lightning" else 3)
        assert shot["ended"]==( "hit" if record["element"]=="lightning" else "burst")
        assert shot["mult"]==(2.5 if record["strength"]=="strong" else 1.2)
        assert shot["radius"]==(0 if record["element"]=="lightning" else 1.5)
    else:
        assert shot["kind"]=="enemy" and shot["element"]=="sal" and shot["share"]==0.6
        assert record["enemy_damage_mult"]==(2.5 if record["strength"]=="strong" else 1.0)
        assert any(row["mask"] & 16 for row in record["player_status_frames"])
probe=json.loads(subprocess.check_output([shutil.which("ffprobe"),"-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size","-of","json",str(BASE/(args.phase+".avi"))],text=True))
video=next(row for row in probe["streams"] if row["codec_name"]=="mjpeg")
assert (video["width"],video["height"],video["r_frame_rate"])==(1280,720,"60/1")
assert int(video["nb_frames"]) >= bounds[LABELS[-1]]["END"]
head=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
source_names=subprocess.check_output(["git","-C",str(ROOT),"ls-files","core","actors","items","skills","data/items/talisman_fire.tres","data/items/talisman_ice.tres","data/items/talisman_thunder.tres","data/enemies/nachalnyeo.tres"],text=True).splitlines()
source_names=[name for name in source_names if Path(name).suffix in [".gd",".gdshader",".tres"]]
if is_after:
    extra=subprocess.check_output(["git","-C",str(ROOT),"ls-files","--others","--exclude-standard","core","actors","items","skills"],text=True).splitlines()
    source_names += [name for name in extra if Path(name).suffix in [".gd",".gdshader"]]
source_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(set(source_names))}
if args.phase=="before":
    for name,value in source_hashes.items():
        original=subprocess.check_output(["git","-C",str(ROOT),"show",head+":"+name])
        assert hashlib.sha256(original).hexdigest()==value,"BEFORE runtime differs from baseline: "+name
metadata={"card":632,"phase":args.phase,"source_head":head,"source_hashes":source_hashes,"capture_script_sha256":hashlib.sha256((BASE/"capture_elements.gd").read_bytes()).hexdigest(),"raw_log_sha256":hashlib.sha256(raw_path.read_bytes()).hexdigest(),"checks":int(result[1]),"fps":60,"speed":1.0,"fixture":fixture,"bounds":bounds,"combat":records,"avi_probe":probe}
if is_after:
    before=json.loads((BASE/"before_metadata.json").read_text(encoding="utf-8"))
    for field in ["fixture","bounds","combat","capture_script_sha256","fps","speed"]:
        assert metadata[field]==before[field],"before/after exact comparison differs: "+field
(BASE/(args.phase+"_metadata.json")).write_text(json.dumps(metadata,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
summary={"phase":args.phase,"checks":metadata["checks"],"source_head":head,"capture_script_sha256":metadata["capture_script_sha256"],"source_files":len(source_hashes),"invariant_equal":True if is_after else "baseline","engine_frames":video["nb_frames"],"duration":probe["format"]["duration"],"segments":[{"label":label,"bounds":bounds[label],"shot_born_exit":[records[label]["shots"][0]["born_frame"],records[label]["shots"][0]["exit_frame"]],"hits":records[label]["shots"][0].get("hits",1),"power":records[label].get("enemy_damage_mult",records[label]["shots"][0].get("mult")),"hp_after":records[label]["hp_after"]} for label in LABELS]}
print(json.dumps(summary,ensure_ascii=False))