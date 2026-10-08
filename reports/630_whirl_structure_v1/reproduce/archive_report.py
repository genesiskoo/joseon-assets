"""#630 archive verified engine film, source fingerprints, raw logs, six supplemental frames."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")
BASE=Path(__file__).resolve().parent
OUT=BASE/"deliverables"
REPORT=Path("C:/workspace/joseon-assets/reports/630_whirl_structure_v1")
PREVIEWS=OUT/"previews"
PREVIEWS.mkdir(exist_ok=True)
manifest=json.loads((OUT/"video_manifest.json").read_text(encoding="utf-8"))
assert REPORT.resolve().is_relative_to(Path("C:/workspace/joseon-assets/reports").resolve())
files=[(OUT/item["file"],Path("video")/item["file"]) for item in manifest["files"]]
files.append((OUT/"video_manifest.json",Path("video/video_manifest.json")))
for name in ["after01_peak.png","after01_ladder_contact.jpg","after01_pair_contact.jpg"]:
    files.append((BASE/name,Path("initial_visual_review")/name))
for name in ["after_peak.png","after_ladder_contact.jpg","after_pair_contact.jpg"]:
    files.append((BASE/name,Path("final_visual_review")/name))
for name in ["capture_scene.tscn","capture_whirl.gd","validate_capture.py","preview_capture.py","encode_video.py","archive_report.py"]:
    files.append((BASE/name,Path("reproduce")/name))
for name in ["before_metadata.json","after_metadata.json","after01_metadata.json"]:
    files.append((BASE/name,Path("metadata")/name))
files += [(source,Path("logs")/source.name) for source in BASE.glob("*.log")]
files += [(source,Path("logs")/source.name) for source in BASE.glob("*_probe.json")]
frames=[]
for index,segment in enumerate(["whirl1","whirl5","whirl10"],1):
    for phase in ["before","after"]:
        frame=manifest["bounds"][segment]["BEGIN"]-1+58
        name=f"{index:02}_{segment}_{phase}"
        png,jpg=PREVIEWS/(name+".png"),PREVIEWS/(name+".jpg")
        subprocess.run([shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-i",str(BASE/(phase+".avi")),"-vf",f"select=eq(n\\,{frame})","-frames:v","1","-update","1",str(png)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        image=Image.open(png).convert("RGB")
        image.save(jpg,quality=84,optimize=True)
        assert image.width<=1280 and jpg.stat().st_size<=300000
        files += [(png,Path("frames")/png.name),(jpg,Path("frames")/jpg.name)]
        frames.append({"file":jpg.name,"segment":segment,"phase":phase,"source_frame_zero_based":frame,"width":image.width,"height":image.height,"bytes":jpg.stat().st_size})
(PREVIEWS/"frames_manifest.json").write_text(json.dumps({"card":630,"frames":frames},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
files.append((PREVIEWS/"frames_manifest.json",Path("frames/frames_manifest.json")))
assert all(source.stat().st_size<10_000_000 for source,relative in files)
assert sum(source.stat().st_size for source,relative in files)<49_000_000
local_intermediates=[]
for phase in ["before","after01","after"]:
    source=BASE/(phase+".avi")
    local_intermediates.append({"phase":phase,"local_path":str(source),"bytes":source.stat().st_size,"sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"role":"local MovieMaker encoding intermediate, not included in report or Git"})
(OUT/"local_intermediates_manifest.json").write_text(json.dumps({"card":630,"files":local_intermediates},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
files.append((OUT/"local_intermediates_manifest.json",Path("metadata/local_intermediates_manifest.json")))
archived=[]
for source,relative in files:
    data=source.read_bytes()
    target=REPORT/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    archived.append({"file":relative.as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
(REPORT/"archive_manifest.json").write_text(json.dumps({"card":630,"files":archived},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=["# #630 회오리/칼바람 구조 v1 — 실제 전투 영상","","PD 지시: 이펙트는 영상으로 보고. 실제 Godot MovieMaker 60fps·정상1×. 회오리베기/칼바람 Lv1·5·10 각각240프레임(4초), 비교/실제 적용 총24초. 기록60fps는 실시간 성능 측정이 아니다. 비교는 왼쪽 기존/오른쪽 개선, 동일 crop(280,80,720,540)·640×480축소와 개선본 게임 소리. 실제 적용은 전체1280×720 화면, 엔진 보존본은 자막·크롭 이전 전체 촬영.","","| 영상 | 길이 | bytes |","|---|---:|---:|"]
for item in manifest["files"]:
    lines.append(f"| video/{item['file']} | {float(item['probe']['format']['duration']):.6f}초 | {item['bytes']} |")
lines += ["","먹 몸통은 blend_mix·안개 적용·opacity .26(잔상 .12), 밝은 심은 blend_add·fog_disabled·opacity .86(잔상 .58)이며 개선본의 현재 구현값이다. 모든 영상 H264·8bit4:2:0·60fps. 실제 pix_fmt/color_range는 video_manifest.json probe에 표기한다. 전체디코딩 오류0, 각 파일10MB미만·카드50MB미만. 큰 AVI는 로컬 인코딩 중간파일이며 전체 엔진 MP4를 보존한다. 로컬 AVI의 절대 위치·크기·SHA256은 metadata/local_intermediates_manifest.json에 기록한다.","",f"기준 소스 {manifest['source_before']}. 전후 실제 촬영 각73/73PASS. 같은 넓은 방(흑랑굴1층), 도호·철검·camera(-35.264°,45°,ortho11), 힘15/민첩15/체력20/정기20·산적8명(1.7u/3.1u 고리)·HP100000·AI frozen·crit0/sure_hit. 캐릭터Lv30은 학습 요구 충족용이며 능력치를 올리지 않는다. 회오리 한 번 실제시전(frame30), 칼바람은 실제 우클릭 frame30→180홀드(2.5초)·해제 뒤 도는 바퀴까지 정상 종료. 도호 발밑 cursor고정으로 제자리회전; 무기/클립/수명/판정은 실제 게임 경로.","","global/Vfx/PlayerCombat 시드630·GameState20260916. 전후 기록 필드가 정확히 같다: 타격프레임/대상/피해·MP debit/net·전투/GameState RNG.state·리본 표시 프레임·칼바람 바퀴/명중합·반경·스탯·240프레임 도호/카메라 좌표. 서로 다른 스킬레벨 사이 피해·반경·MP차이는 기존 게임 수치다.","","| 구간 | 피해 | MP debit | 맞힌 대상 | 바퀴 |","|---|---:|---:|---:|---:|"]
for label,r in manifest["combat"].items():
    lines.append(f"| {label} | {r['damage']} | {r['mp_debit']:.6f} | {r['targets_hit']} | {r['storm_revs']} |")
lines += ["","metadata/에 source/대본SHA·rawSHA·fixture·bounds·combat 전체, reproduce/에 촬영/검증/인코딩/아카이브 대본. BEFORE는 기준소스, AFTER는#630구현소스. 파일해시·길이는 archive_manifest.json. initial_visual_review와 after01 원문/메타는 메뉴 정지 예약 타이머 수정 전 최초 검수본이며, 최종 영상은 process_always=false를 반영한 AFTER02(after.*)다. 비정지 전투 메타는 두 개선본에서도 정확히 같다. 6장1280폭 JPG는 회오리Lv1/5/10의 동일 절대 엔진프레임을 추출한 보조자료.","","정상 scene 촬영은 실행/셰이더 오류0. VIDEO630 PASS·Done recording 뒤 종료단계의 기존 ObjectDB11/리소스6 정리 보고는 raw전체보존. #629기준before와 동일하며 tools/test.ps1:924,986-987의 기존 종료보고 허용목록 자기검사와 일치한다. 최초 --check-only/--script 진입은 autoload GameState가 없는 독립실행이라 컴파일오류를 기록했고, 정상projectscene 최종촬영은 모두 통과했다. parse.raw.log/parse.engine.log도 보존했다.","","재현: reproduce 파일을 게임 ._tmp/630_whirl_structure/에 복사한 뒤 기준/개선작업트리 각각에서 호출. 경로는 작업트리절대경로.","",chr(96)*3+"powershell","godot --path . --scene res://._tmp/630_whirl_structure/capture_scene.tscn --windowed --resolution 1280x720 --fixed-fps 60 --disable-vsync --quit-after 3600 --write-movie <작업트리>/._tmp/630_whirl_structure/before.avi --log-file <작업트리>/._tmp/630_whirl_structure/before.engine.log -- --new --phase=before *> ._tmp/630_whirl_structure/before.raw.log","python ._tmp/630_whirl_structure/validate_capture.py before","# AFTER: after.avi/after.engine.log/--phase=after/after.raw.log","python ._tmp/630_whirl_structure/validate_capture.py after","python ._tmp/630_whirl_structure/encode_video.py","python ._tmp/630_whirl_structure/archive_report.py",chr(96)*3]
(REPORT/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
all_files=[p for p in REPORT.rglob("*") if p.is_file()]
total=sum(p.stat().st_size for p in all_files)
assert total<50_000_000
print(json.dumps({"report":str(REPORT),"videos":len(manifest["files"]),"total_bytes":total,"jpgs":6,"preview_directory":str(PREVIEWS)},ensure_ascii=False),flush=True)