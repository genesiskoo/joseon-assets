"""#634 byte-preserving report archive; no AVI/runtime/editor/game-doc writes."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
DEST=Path('C:/workspace/joseon-assets/reports/634_status_structure_v1')
ap=argparse.ArgumentParser()
ap.add_argument('--phase',default='after02')
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
assert hashlib.sha256((BASE/'capture_status.gd').read_bytes()).hexdigest()==before['capture_script_sha256']==after['capture_script_sha256']
if a.game_commit:
    commit_full=subprocess.check_output(['git','-C',str(ROOT),'rev-parse',a.game_commit],text=True).strip()
    video['source_after_capture_head']=after['source_head']
    video['source_after_commit']=commit_full
    video['source_after_commit_verified']={'commit':commit_full,'raw_source_files':len(after['source_hashes']),'all_raw_byte_sha256_match':True}
    (BASE/'deliverables/video_manifest.json').write_text(json.dumps(video,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
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
for name in ['capture_status.gd','capture_scene.tscn','validate_capture.py','validate_source_provenance.py','preview_status.py','make_photos.py','encode_video.py','archive_report.py','publish_game_art.py','before_attempt01_capture_status.gd']:
    add(BASE/name,Path('capture_tools')/name)
for source in sorted(BASE.glob('*metadata.json')):
    add(source,Path('metadata')/source.name)
for pattern in ['*preview_manifest.json','*temporal_manifest.json','*audio_comparison.json','*smoke_manifest.json','*line_endings.json']:
    for source in sorted(BASE.glob(pattern)):
        add(source,Path('metadata/diagnostic')/source.name)
for phase in ['before',a.phase]:
    for suffix in ['_status_lifecycle_contact.jpg','_peak.png']:
        add(BASE/(phase+suffix),Path('images')/(phase+suffix))
for phase in ['before',a.phase]:
    for label in ['frozen','sal']:
        add(BASE/(phase+'_'+label+'_photo_peak.png'),Path('images')/(phase+'_'+label+'_photo_peak.png'))
logs=[]
compressed_capture={}
for folder in [BASE,ROOT/'._tmp/634_status_structure']:
    if not folder.exists():
        continue
    for source in sorted(folder.glob('*.raw.log'))+sorted(folder.glob('*.engine.log')):
        if source.name in a.exclude_log:
            continue
        relative=Path('logs')/folder.name/source.name
        if re.match(r'^(before(?:_attempt\d+)?|after\d+)\.(raw|engine)\.log$',source.name):
            compressed_capture[relative.as_posix()]=source
        else:
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
zip_path=BASE/'capture_raw_originals.zip'
zip_rows=[]
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
    for relative,source in sorted(compressed_capture.items()):
        data=source.read_bytes()
        bundle.write(source,relative)
        zip_rows.append({'file':relative,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source':str(source)})
with zipfile.ZipFile(zip_path) as bundle:
    assert bundle.testzip() is None
    for row in zip_rows:
        data=bundle.read(row['file'])
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
zip_manifest=BASE/'capture_raw_zip_manifest.json'
zip_manifest.write_text(json.dumps({'compression':'ZIP DEFLATE only; all raw/engine bytes and error lines retained exactly','zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'zip_bytes':zip_path.stat().st_size,'uncompressed_bytes':sum(r['bytes'] for r in zip_rows),'files':zip_rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
add(zip_path,'logs/capture_raw_originals.zip')
add(zip_manifest,'logs/capture_raw_zip_manifest.json')
originals=[{'local_file':source.name,'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'location':str(source),'policy':'local ignored oversized intermediate; full-engine final MP4 archived'} for source in sorted(BASE.glob('*.avi'))]
failed_baseline=Path('C:/Users/FORYOUCOM/.codex/worktrees/632-element-structure/joseon/._tmp/634_status_structure_v1/before_attempt01.avi')
if failed_baseline.is_file():
    originals.append({'local_file':failed_baseline.name,'bytes':failed_baseline.stat().st_size,'sha256':hashlib.sha256(failed_baseline.read_bytes()).hexdigest(),'location':str(failed_baseline),'policy':'first failed fixture original retained locally; complete raw/engine preserved in ZIP'})
source_note={'game_commit':a.game_commit or 'pending root final code commit; exact captured source hashes in video_manifest.json','before_baseline':video['source_before'],'before_capture_head':before['source_head'],'source_files_before':146,'source_files_after':147,'save_isolation':'video634_capture.json selected BEFORE Main instantiate; active_profile empty; no reset_game/shared save_e2e','status_end':'burn/chill/frozen native expiry; sal actual salpuri input240 first mask32 snapshot242','after_phase':a.phase,'capture_sha256':before['capture_script_sha256'],'capture_checks':{'before':37,'after':37,'fails':0},'normal_speed':1.0,'recorded_fps':60,'frame_mapping':'AVI zero-based N=Engine process counter N; trim [BEGIN,END) 360 frames,800 audio samples per video frame','audio':'Existing independent Audio RNG changes per-take variant/pitch. A/B and actual reel use the same AFTER native source audio; full-engine movies retain their own native audio. Source audio SHA comparison included.','errors':'All capture raw preserved. Existing post-PASS teardown ObjectDB/resource warnings classified separately; initial fixture/manager/E2E failures are also retained.'}
readme=(ROOT/'docs/art/634_status_structure_v1/README.md').read_text(encoding='utf-8')
for photo in json.loads((BASE/'deliverables/photos/photos_manifest.json').read_text(encoding='utf-8'))['photos']:
    readme=readme.replace(']('+photo['jpg']+')','](photos/'+photo['jpg']+')')
readme += '\n\nArchive game commit: `'+source_note['game_commit']+'`. Capture logs with repetitive full per-frame arrays are losslessly preserved in `logs/capture_raw_originals.zip`; `logs/capture_raw_zip_manifest.json` records every uncompressed byte count and SHA. Every E2E phase referenced by copied logs includes original godot.raw.log and phase.json. Intermediate AVIs remain local with exact byte/SHA registry.\n'

extra={'local_originals.json':json.dumps(originals,ensure_ascii=False,indent=2)+'\n','capture_summary.json':json.dumps(source_note,ensure_ascii=False,indent=2)+'\n','README.md':readme}
planned=sum(path.stat().st_size for path in plan.values())+sum(len(value.encode('utf-8')) for value in extra.values())
print(json.dumps({'dry_run':a.dry_run,'files':len(plan)+len(extra),'planned_bytes':planned,'phase_originals':len(phase_dirs),'game_commit':source_note['game_commit']},ensure_ascii=False),flush=True)
assert planned<49_500_000,'archive needs phase/raw ZIP conservation; ask root to choose preservation plan'
if a.dry_run:
    raise SystemExit(0)
DEST.mkdir(parents=True,exist_ok=True)
(DEST/'.gitattributes').write_text('* -text -diff\n',encoding='utf-8',newline='\n')
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
(DEST/'archive_manifest.json').write_text(json.dumps({'card':634,'game_commit':source_note['game_commit'],'files':manifest,'bytes_without_manifest':sum(r['bytes'] for r in manifest)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
total=sum(p.stat().st_size for p in DEST.rglob('*') if p.is_file())
assert total<50_000_000,total
print(json.dumps({'archive':str(DEST),'files':len(manifest)+1,'bytes':total},ensure_ascii=False),flush=True)
