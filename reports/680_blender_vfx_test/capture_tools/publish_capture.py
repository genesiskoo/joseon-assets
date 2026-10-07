"""Preserve actual #680 footage/raw provenance; no source/runtime/board mutations."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
base=Path(__file__).resolve().parent; root=base.parent.parent.parent
report=Path('C:/workspace/joseon-assets/reports/680_blender_vfx_test'); art=root/'docs/art/680_blender_vfx_test'
ap=argparse.ArgumentParser(); ap.add_argument('--phase',default='after01'); args=ap.parse_args()
manifest=json.loads((base/'deliverables/video_manifest.json').read_text(encoding='utf-8'))
assert manifest['phase_after']==args.phase and manifest['every_absolute_combat_field_exact']
report.mkdir(parents=True,exist_ok=True); art.mkdir(parents=True,exist_ok=True)
for entry in manifest['files']:
    source=base/'deliverables'/entry['file']; assert source.stat().st_size==entry['bytes']<10_000_000 and hashlib.sha256(source.read_bytes()).hexdigest()==entry['sha256']
    shutil.copy2(source,report/source.name)
for optional in ['680_blender_baked_atlas_preview_24fps.mp4','blender_atlas_preview_manifest.json','680_blender_vfx_rejected_after01_engine_capture_60fps.mp4','rejected_after01_manifest.json','680_blender_vfx_rejected_after02_fire_AB_60fps.mp4','rejected_after02_manifest.json']:
    source=base/'deliverables'/optional
    if source.exists():
        assert source.stat().st_size<10_000_000
        shutil.copy2(source,report/optional)
runtime_archive=report/'capture_runtime'; runtime_archive.mkdir(exist_ok=True)
for source in base.glob('*_changed_runtime_*'):
    if source.is_file():
        assert source.stat().st_size<10_000_000
        shutil.copy2(source,runtime_archive/source.name)
photos=[]; photo_dir=report/'photos'; photo_dir.mkdir(exist_ok=True)
before=json.loads((base/'before_metadata.json').read_text(encoding='utf-8'))
for label,relative_frame in [('fire_weak',74),('fire_strong',74),('sal_strong',90)]:
    frame=before['bounds'][label]['BEGIN']+relative_frame
    shot=before['combat'][label]['shots'][0]; hit=before['combat'][label]['hit_events'][0]['frame']
    assert shot['born_frame']<relative_frame<hit,(label,'still actually flying')
    for phase in ['before',args.phase]:
        side='before' if phase=='before' else 'after'; png=base/f'{side}_{label}_photo.png'
        r=subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-v','error','-y','-i',str(base/(phase+'.avi')),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(png)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW); assert r.returncode==0,r.stdout
        jpg=art/f'{side}_{label}.jpg'
        with Image.open(png) as image:
            assert image.size==(1280,720)
            image.convert('RGB').save(jpg,quality=86,optimize=True)
        assert jpg.stat().st_size<=300_000
        shutil.copy2(jpg,photo_dir/jpg.name)
        photos.append({'jpg':jpg.name,'label':label,'side':side,'source_frame_zero_based':frame,'segment_frame':relative_frame,'before_and_after_same_actual_flight_frame':True,'width':1280,'height':720,'bytes':jpg.stat().st_size,'sha256':hashlib.sha256(jpg.read_bytes()).hexdigest()})
(report/'photos_manifest.json').write_text(json.dumps({'card':680,'photos':photos},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
helpers=report/'capture_tools'; helpers.mkdir(exist_ok=True)
for p in base.iterdir():
    if p.is_file() and p.suffix in ['.py','.gd','.tscn']:
        shutil.copy2(p,helpers/p.name)
entries=[]; archive=report/'capture_raw_originals.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(base.iterdir()):
        if not p.is_file() or p.suffix not in ['.json','.log']:
            continue
        data=p.read_bytes(); z.writestr(p.name,data)
        entries.append({'entry':p.name,'uncompressed_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for e in entries: assert hashlib.sha256(z.read(e['entry'])).hexdigest()==e['sha256']
(report/'capture_raw_zip_manifest.json').write_text(json.dumps({'archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'entries':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1024*1024): h.update(block)
    return h.hexdigest()
intermediates=[]
for phase in ['before']+[p.stem for p in sorted(base.glob('after*.avi'))]:
    if any(Path(e['path']).name==phase+'.avi' for e in intermediates): continue
    p=base/(phase+'.avi'); movie='680_blender_vfx_rejected_after01_engine_capture_60fps.mp4' if phase=='after01' and args.phase!='after01' else (None if phase!='before' and phase!=args.phase else f'680_blender_vfx_{"before" if phase=="before" else "after"}_engine_capture_60fps.mp4'); intermediates.append({'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'git':'ignored local intermediate','shareable_fullengine':movie,'rejected_after02_qa_clip':'680_blender_vfx_rejected_after02_fire_AB_60fps.mp4' if phase=='after02' and args.phase!='after02' else None,'note':'AFTER03 same final visual rejected as final provenance due newly-introduced metadata CRLF/Git LF mismatch; AFTER04 preserves same content with LF source bytes' if phase=='after03' and args.phase=='after04' else None})
(report/'intermediate_avi_manifest.json').write_text(json.dumps({'card':680,'intermediates':intermediates},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(base/'deliverables/video_manifest.json',report/'video_manifest.json')
lines=['# #680 Blender + Godot VFX 실제 전후','',
'시험플래그 Vfx.blender_test_enabled는 기본false이며 촬영·E2e에서 명시적으로 true를 켜는 프로토타입이다. PD채택 전 기본게임에 자동 적용하지 않는다.','',
'실제 화염부(KEY2 벨트 입력)와 나찰녀 살 구슬(native 적 AI)을 약/강 각각 6초씩 기록했다. 정상1× Godot MovieMaker60fps이며 실시간 성능 수치가 아니다. 약/강은 플레이어 정기20/150, 적 지역레벨1/16으로 기존 실제 grade0/2를 선택한다. 5u의 동일 무대·입력·배우·카메라를 썼으며 피해/MP/벨트·발사/명중프레임·속도·모든 DOT/상태 binary64·애니·전투/구슬 RNG·카메라 흔들림 전후 전체 기록이 exact 같다.','',
f'BEFORE와 AFTER 각각 {manifest["before_checks"]}/{manifest["before_checks"]}, {manifest["after_checks"]}/{manifest["after_checks"]} PASS. 불은 발사64→명중83, 살은 발사63→명중117(구간 상대프레임)이며 전후 동일하다. 약불 직접12+DOT7, 강불25+DOT15, 약살1+DOT3, 강살4+DOT9이다. 약살의 zero 정수 피해 틱은 실제 native 콜백에서 생략되어 양수 DOT 콜백3, 강살6이며 전체 상태시계를 그대로 비교했다.','',
'첫 살 구슬 뒤 재발사만 막고 pull/graze hook의 clock을 프레임마다 고정해 한 발의 실제 AI/물리/피격/상태 자연 종료를 격리했다. 새 공격·강제 피해·수동 명중·상태변조는 없다. Main 생성 전 private video680_capture.json을 선택하고 active profile은 비워 기존 저장과 분리했다.','',
'비교는 같은 actual 프레임 (510,210,320,240)을 좌우 640×480으로 2× 확대한 영상이며 확대보기를 화면에 표시했다. 실제 AFTER 편집본과 fullengine BEFORE/AFTER는 원래1280×720 카메라/원음이다. 프레임 추가/감속 없이 [BEGIN,END)360프레임씩 자르고 frame당48000Hz PCM800sample을 맞췄다. 독립 Audio RNG의 variant/pitch 변주는 원음 그대로 보존하며 A/B는 AFTER AUDIO를 명시한다.','',
'촬영 전후 runtime/data/시트/메타/GLB의 raw SHA를 video_manifest에 보존했다. 기준861/881 파일은 bc7b48c5 Git blob과 raw byte exact이며20개의 기존 VFX meta.json만 checkout CRLF이고 LF-normalized bytes는 exact이다(게임 .gd/.gdshader에는 차이0). 원문 byte와 각 예외 SHA를 함께 기록한다. 최종 AFTER 커밋 대조는 root가 확정 후 manifest에 기록한다.','',
'AFTER03과 같은 시각의 최종 AFTER04를 다시 실제 촬영했다. 신규 Blender meta.json2개의 CRLF를 최종 Git blob과 같은 LF로 정리했으며 JSON 값·PNG·GLB·runtime GD는 동일하다. 신규 자료에는 정규화 예외를 추가하지 않는다. 구판 source/runtime 원본과 전체 촬영 기록을 보존하고 최종 LF 원본의 실제 영상·사진·전투 대조를 다시 검증했다.','',
'| 영상 | 길이 / 프레임 | 크기 |','|---|---:|---:|']
for e in manifest['files']:
    v=next(s for s in e['probe']['streams'] if s['codec_name']=='h264'); lines.append(f'| [{e["file"]}](C:/workspace/joseon-assets/reports/680_blender_vfx_test/{e["file"]}) | {e["probe"]["format"]["duration"]}초 / {v["nb_frames"]} | {e["bytes"]:,}B |')
lines+=['','| 실제 비행 동일프레임 | 변경 전 | 변경 후 |','|---|---|---|']
for label,name in [('fire_weak','약 화염부'),('fire_strong','강 화염부'),('sal_strong','강 살 구슬')]:
    frame=next(p['source_frame_zero_based'] for p in photos if p['label']==label); lines.append(f'| {name} · engine{frame} | ![전](before_{label}.jpg) | ![후](after_{label}.jpg) |')
lines+=['',
'첫 setup 실패2회(타입추론/오프닝 우회누락)와 유효 before/after 및 encoder/decode 원문은 capture_raw_originals.zip에 byte 그대로 보존했다. 첫 sandbox 실행의 shadercache 권한 오류도 실패 원문에 남긴다. 유효 BEFORE의 종료 후 기존 ObjectDB11/resource6 메시지는 runtime 오류와 구분하여 원문을 보존했다. AFTER01은48/48과 전체전투 exact를 통과했지만 실제 시각이 너무 약해 기각했다. 큰 투명여백과 낮은 shaderalpha를 공통alpha crop/reanchor·표시크기·gain으로 보완했다. AFTER02도48/48과 exact를 통과했지만 강불이 긴 노란 전선/번개처럼 보여 다시 기각했다. 최종 화염은 따뜻한 주홍 density ramp·낮은 밀도 alpha gamma·탄두 쪽 좁은 core taper로 보완했다. 기각된 actual fullengine(A01)/실제 강불6초AB(A02)·전체 원문/metadata·변경runtime 원본은 rejected_after01/02_manifest와 capture_runtime에 보존한다. 모든 공유MP4 full decode0, 파일당10MB미만이다. 대형AVI는 ignored local 중간물이고 path/bytes/SHA 및 공유본 매핑은 intermediate_avi_manifest에 남긴다.','',
'Blender 제작 방식/원본/렌더 로그와 Godot 조립·회귀시험/최종커밋은 [전체 보고서](C:/workspace/joseon-assets/reports/680_blender_vfx_test/README.md)에 합친다.','']
(art/'README.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
report_text='\n'.join(lines)
for row in photos:
    report_text=report_text.replace(']('+row['jpg']+')','](photos/'+row['jpg']+')')
(report/'CAPTURE_README.md').write_text(report_text,encoding='utf-8',newline='\n')
assert sum(p.stat().st_size for p in art.iterdir() if p.is_file())<2_000_000
files=[p for p in report.rglob('*') if p.is_file()]; assert all(p.stat().st_size<10_000_000 for p in files) and sum(p.stat().st_size for p in files)<50_000_000
print(json.dumps({'report':str(report),'game_art':str(art),'jpgs':len(photos),'report_current_bytes':sum(p.stat().st_size for p in files),'archive_bytes':archive.stat().st_size},ensure_ascii=False))
