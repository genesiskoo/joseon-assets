"""#632 byte-preserving report archive; no AVI/runtime/editor/game-doc writes."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
DEST=Path('C:/workspace/joseon-assets/reports/632_element_structure_v1')
ap=argparse.ArgumentParser()
ap.add_argument('--phase',default='after03')
ap.add_argument('--game-commit',help='optional final game commit, verified against every captured source byte')
ap.add_argument('--dry-run',action='store_true')
ap.add_argument('--exclude-log',action='append',default=[],help='ongoing root test console excluded until immutable final log is ready')
a=ap.parse_args()
before=json.loads((BASE/'before_metadata.json').read_text(encoding='utf-8'))
after=json.loads((BASE/(a.phase+'_metadata.json')).read_text(encoding='utf-8'))
video=json.loads((BASE/'deliverables/video_manifest.json').read_text(encoding='utf-8'))
assert video['phase_after']==a.phase
assert video['combat_fields_exact'] and before['combat']==after['combat']
assert video['source_hashes_after']==after['source_hashes']
for name,digest in after['source_hashes'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'runtime changed since capture: '+name
    if a.game_commit:
        original=subprocess.check_output(['git','-C',str(ROOT),'show',a.game_commit+':'+name])
        assert hashlib.sha256(original).hexdigest()==digest,'game commit/capture source differs: '+name
assert hashlib.sha256((BASE/'capture_elements.gd').read_bytes()).hexdigest()==before['capture_script_sha256']==after['capture_script_sha256']
plan={}
def add(source,relative):
    source=Path(source)
    if source.is_file():
        relative=Path(relative).as_posix()
        assert source.stat().st_size<10_000_000,(source.name,'file exceeds10MB; AVI local only')
        assert relative not in plan or plan[relative]==source,(relative,'duplicate destination')
        plan[relative]=source
for row in video['files']:
    source=BASE/'deliverables'/row['file']
    assert source.stat().st_size==row['bytes'] and hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    add(source,row['file'])
add(BASE/'deliverables/video_manifest.json','video_manifest.json')
for source in sorted((BASE/'deliverables/photos').glob('*')):
    add(source,Path('photos')/source.name)
for name in ['capture_elements.gd','capture_scene.tscn','validate_capture.py','preview_capture.py','preview_temporal.py','make_photos.py','encode_video.py','archive_report.py','publish_game_art.py']:
    add(BASE/name,Path('capture_tools')/name)
for source in sorted(BASE.glob('*metadata.json')):
    add(source,Path('metadata')/source.name)
for pattern in ['*preview_manifest.json','*temporal_manifest.json','*audio_comparison.json','*smoke_manifest.json','*line_endings.json']:
    for source in sorted(BASE.glob(pattern)):
        add(source,Path('metadata/diagnostic')/source.name)
for phase in ['before','after02','after03',a.phase]:
    for suffix in ['_impact_ladder.jpg','_strong_temporal_contact.jpg','_peak.png']:
        add(BASE/(phase+suffix),Path('images')/(phase+suffix))
for phase in ['before',a.phase]:
    for label in ['cold_strong','sal_strong']:
        add(BASE/(phase+'_'+label+'_photo_peak.png'),Path('images')/(phase+'_'+label+'_photo_peak.png'))
logs=[]
for folder in [BASE,ROOT/'._tmp/632_element_structure']:
    if not folder.exists():
        continue
    for source in sorted(folder.glob('*.raw.log'))+sorted(folder.glob('*.engine.log')):
        if source.name in a.exclude_log:
            continue
        relative=Path('logs')/folder.name/source.name
        add(source,relative)
        logs.append(source)
phase_dirs=set()
for source in logs:
    raw=source.read_text(encoding='utf-8-sig',errors='replace')
    for found in re.findall(r'^E2E_PHASE_RAW (.+)$',raw,re.M):
        candidate=Path(found.strip()).resolve()
        safe_root=(ROOT/'tmp/e2e_raw').resolve()
        assert candidate.is_relative_to(safe_root),'phase path escapes owned game tree: '+str(candidate)
        assert candidate.is_dir(),'missing preserved raw phase: '+str(candidate)
        phase_dirs.add(candidate)
for folder in sorted(phase_dirs):
    relative=folder.relative_to(ROOT/'tmp/e2e_raw')
    for name in ['godot.raw.log','phase.json']:
        source=folder/name
        assert source.is_file(),'required original phase missing: '+str(source)
        add(source,Path('logs/e2e_raw')/relative/name)
originals=[{'local_file':source.name,'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'location':str(source),'policy':'local ignored oversized intermediate; full-engine final MP4 archived'} for source in sorted(BASE.glob('*.avi'))]
source_note={'game_commit':a.game_commit or 'pending root final code commit; exact captured source hashes in video_manifest.json','before_baseline':before['source_head'],'after_phase':a.phase,'capture_sha256':before['capture_script_sha256'],'capture_checks':{'before':47,'after':47,'fails':0},'normal_speed':1.0,'recorded_fps':60,'frame_mapping':'AVI zero-based N=Engine process counter N; trim [BEGIN,END) 180 frames,800 audio samples per video frame','audio':'Existing independent Audio RNG changes per-take variant/pitch. A/B and actual reel use the same AFTER native source audio; full-engine movies retain their own native audio. Source audio SHA comparison included.','errors':'All capture raw preserved. Existing post-PASS teardown ObjectDB/resource warnings classified separately; initial fixture/manager/E2E failures are also retained.'}
readme=f'''# #632 Element structure v1\n\nActual Godot actor/input/talisman/enemy-projectile before/after, eight normal-speed3s takes(24s total), 60fps recorded, identical camera/stats/seed/consumables/damage/hits/status/positions. Recorded60fps is not a realtime performance measurement.\n\nBefore: `{before['source_head']}`. After game commit: `{source_note['game_commit']}`. New `core/vfx_elements.gd` and all source byte hashes are in `video_manifest.json`. Capture SHA `{before['capture_script_sha256']}` stayed unchanged. Both captures47/47 PASS; full combat metadata exact.\n\nThe comparison crop is fixed(280,80,720,540) scaled640x480 per side. Actual and full-engine footage use1280x720 original camera. Each take is [BEGIN,END), AVI zero-based counter N. Six photos pair the exact same engine frames.\n\nFire/cold preserve current radius1.5 AOE and3 target hits; lightning preserves existing single-target1 hit(no chain). Sal is the actual nachalnyeo enemy orb, never a new player spell. Low/strong talisman multipliers1.2/2.5 follow SPI20/150; sal area levels1/16 follow normal1/2.5 damage scaling. MP unchanged; belt5→4. Status details are a separate#634.\n\nOriginal per-take sound is not byte-identical because existing Audio randomizes independent variation/pitch. The A/B and actual edit share the AFTER native soundtrack with exact800sample/frame trims. Full-engine videos retain each native soundtrack. Original sound fingerprints are preserved.\n\nLogs include initial failures and final passes without removing error lines. Successful capture shutdown retains11 ObjectDB/6resources in-use teardown messages; no live runtime/shader error in valid captures. MovieMaker AVI intermediates remain local, excluded from git by size; `local_originals.json` records exact byte sizes and SHA256. Final MP4 full-engine source movies are preserved here. All original E2E phases referenced by copied logs include godot.raw.log and phase.json; merged console duplicates are omitted.\n\n`archive_manifest.json` checks every archived byte. Each file<10MB and card total<50MB. Reproducible capture/encode scripts are in `capture_tools/`.\n'''
extra={'local_originals.json':json.dumps(originals,ensure_ascii=False,indent=2)+'\n','capture_summary.json':json.dumps(source_note,ensure_ascii=False,indent=2)+'\n','README.md':readme}
planned=sum(path.stat().st_size for path in plan.values())+sum(len(value.encode('utf-8')) for value in extra.values())
print(json.dumps({'dry_run':a.dry_run,'files':len(plan)+len(extra),'planned_bytes':planned,'phase_originals':len(phase_dirs),'game_commit':source_note['game_commit']},ensure_ascii=False),flush=True)
assert planned<49_500_000,'archive needs phase/raw ZIP conservation; ask root to choose preservation plan'
if a.dry_run:
    raise SystemExit(0)
DEST.mkdir(parents=True,exist_ok=True)
for relative,source in plan.items():
    target=DEST/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==hashlib.sha256(source.read_bytes()).hexdigest()
for name,value in extra.items():
    (DEST/name).write_text(value,encoding='utf-8')
manifest=[]
for target in sorted(DEST.rglob('*')):
    if target.is_file() and target.name!='archive_manifest.json':
        size=target.stat().st_size
        assert size<10_000_000,target.name
        manifest.append({'file':target.relative_to(DEST).as_posix(),'bytes':size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(DEST/'archive_manifest.json').write_text(json.dumps({'card':632,'game_commit':source_note['game_commit'],'files':manifest,'bytes_without_manifest':sum(r['bytes'] for r in manifest)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
total=sum(p.stat().st_size for p in DEST.rglob('*') if p.is_file())
assert total<50_000_000,total
print(json.dumps({'archive':str(DEST),'files':len(manifest)+1,'bytes':total},ensure_ascii=False),flush=True)
