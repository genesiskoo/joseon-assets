"""#630 read and validate one actual capture before runtime source changes."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('phase', choices=['before', 'after'])
args = ap.parse_args()
raw_path = BASE / (args.phase + '.raw.log')
raw = raw_path.read_text(encoding='utf-8-sig')
result = re.search(r'VIDEO630 phase=' + args.phase + r' checks=(\d+) fails=(\d+) (PASS|FAIL)', raw)
assert result and result[2] == '0' and result[3] == 'PASS', 'capture check failed'
errors = [s for s in raw.splitlines() if re.search(r'SCRIPT ERROR|SHADER ERROR|Parse Error|Compile Error|^ERROR:', s) and 'resources still in use at exit' not in s]
assert not errors, errors
bounds = {}
for name, edge, frame in re.findall(r'CAPTURE (\S+) (BEGIN|END) (\d+)', raw):
    bounds.setdefault(name, {})[edge] = int(frame)
expected = ['whirl1', 'whirl5', 'whirl10', 'storm1', 'storm5', 'storm10']
assert list(bounds) == expected
assert all(b['END'] - b['BEGIN'] == 240 for b in bounds.values())
fixture = json.loads(next(s.removeprefix('FIXTURE630 ') for s in raw.splitlines() if s.startswith('FIXTURE630 ')))
combat = {r['segment']: r for r in [json.loads(s.removeprefix('COMBAT630 ')) for s in raw.splitlines() if s.startswith('COMBAT630 ')]}
assert list(combat) == expected
for record in combat.values():
    assert record['frames'] == 240
    assert len(record['camera_frames']) == len(record['actor_frames']) == 240
    assert record['drawing_frames'] > 10 and len(record['hit_events']) >= 4 and record['mp_debit'] > 0
    assert record['rng_before'] != record['rng_after']
    assert record['state_rng_before'] == record['state_rng_after']
    assert record['stats'] == fixture['base_stats']
probe_cmd = [shutil.which('ffprobe'), '-v', 'error', '-show_entries', 'stream=codec_name,width,height,pix_fmt,color_range,r_frame_rate,nb_frames:format=duration,size', '-of', 'json', str(BASE / (args.phase + '.avi'))]
probe_result = subprocess.run(probe_cmd, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
probe = json.loads(probe_result.stdout)
video = next(s for s in probe['streams'] if s['codec_name'] == 'mjpeg')
assert [video['width'], video['height'], video['r_frame_rate']] == [1280, 720, '60/1']
assert int(video['nb_frames']) > bounds['storm10']['END']
source_names = ['core/vfx.gd', 'core/vfx_meshes.gd', 'actors/player_combat.gd', 'actors/sword_trail.gd', 'actors/actor_visual.gd', 'data/skills/whirl.tres', 'data/skills/blade_storm.tres']
if args.phase == "after":
    source_names.append("core/vfx_whirl.gd")
    changed = subprocess.check_output(["git","-C",str(ROOT),"diff","--name-only"],text=True).splitlines()
    fresh = subprocess.check_output(["git","-C",str(ROOT),"ls-files","--others","--exclude-standard"],text=True).splitlines()
    source_names += [name for name in changed + fresh if name.startswith(("core/","actors/","skills/","assets/")) and (ROOT/name).is_file()]
source_hashes = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(set(source_names))}
metadata = {'card':630, 'phase':args.phase, 'source_head':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(), 'source_hashes':source_hashes, 'raw_log_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(), 'checks':int(result[1]), 'capture':fixture, 'bounds':bounds, 'combat':combat, 'avi_probe':probe, 'time_scale':1.0, 'movie_fps':60, 'capture_script_sha256':hashlib.sha256((BASE/'capture_whirl.gd').read_bytes()).hexdigest()}
if args.phase == 'after':
    before = json.loads((BASE/'before_metadata.json').read_text(encoding='utf-8'))
    for field in ['capture', 'bounds', 'combat', 'time_scale', 'movie_fps', 'capture_script_sha256']:
        assert before[field] == metadata[field], 'before/after differ: ' + field
target = BASE / (args.phase + '_metadata.json')
target.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'phase':args.phase,'checks':metadata['checks'],'bounds':bounds,'source_head':metadata['source_head'],'invariant_equal':True if args.phase=='after' else 'baseline','combat':[{k:v for k,v in r.items() if k in ['segment','damage','mp_debit','drawing_frames','storm_revs','targets_hit']} for r in combat.values()]},ensure_ascii=False))