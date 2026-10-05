from pathlib import Path
import hashlib, json, shutil, subprocess
from PIL import Image
import numpy as np

BASE = Path(__file__).resolve().parent
REPORT = Path('C:/workspace/joseon-assets/reports/629_sword_trail_v2')
GAME = BASE.parents[1] / 'docs/art/629_sword_trail_v2'
OUT = BASE / 'deliverables'
manifest = json.loads((OUT / 'video_manifest.json').read_text(encoding='utf-8'))
assert REPORT.resolve().is_relative_to(Path('C:/workspace/joseon-assets/reports').resolve())
GAME.mkdir(parents=True, exist_ok=True)
files = [(p, Path('video') / p.name) for p in OUT.glob('629_*.mp4')]
files.append((OUT / 'video_manifest.json', Path('video/video_manifest.json')))
files += [(BASE / n, Path('reproduce') / n) for n in ['capture_trail.gd', 'capture_scene.tscn', 'encode_video.py', 'archive_report.py']]
files += [(p, Path('logs') / p.name) for p in BASE.glob('*.log')]
files += [(p, Path('logs') / p.name) for p in BASE.glob('*_probe.json')]
metrics = []
for index, (kind, offset) in enumerate([('basic', 58), ('slash', 75), ('crit', 52)], 1):
    for phase in ['before', 'after']:
        frame = manifest['bounds'][phase][kind]['BEGIN'] - 1 + offset
        name = f'{index:02}_{kind}_{phase}'
        png, jpg = BASE / (name + '.png'), GAME / (name + '.jpg')
        subprocess.run([shutil.which('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(BASE / (phase + '.avi')), '-vf', f'select=eq(n\\,{frame})', '-frames:v', '1', '-update', '1', str(png)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        im = Image.open(png).convert('RGB')
        im.save(jpg, quality=86, optimize=True)
        assert im.width <= 1280 and jpg.stat().st_size <= 300000
        # Same fixed rectangle includes blade/body; diagnostic, not a gameplay score.
        pixels = np.asarray(im.crop((550, 230, 725, 360)), dtype=np.float64) / 255
        y = pixels[...,0] * .2126 + pixels[...,1] * .7152 + pixels[...,2] * .0722
        metrics.append({'file': jpg.name, 'segment': kind, 'phase': phase, 'source_frame_zero_based': frame, 'roi_xyxy': [550,230,725,360], 'luma_p95': float(np.percentile(y,95)), 'bright_fraction_Y_gt_0_8': float(np.mean(y > .8)), 'chroma_mean': float(np.mean(np.max(pixels,axis=-1)-np.min(pixels,axis=-1)))})
        files.extend([(png, Path('frames') / png.name), (jpg, Path('frames') / jpg.name)])
(GAME / 'metrics.json').write_text(json.dumps({'card':629, 'diagnostic':'same ROI and engine frames; actor and target included, not isolated effect measurement', 'frames':metrics}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
files.append((GAME / 'metrics.json', Path('frames/metrics.json')))
archived = []
for source, relative in files:
    assert source.stat().st_size < 10000000
    data = source.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    target = REPORT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    archived.append({'file':relative.as_posix(), 'bytes':len(data), 'sha256':sha})
(REPORT / 'archive_manifest.json').write_text(json.dumps({'card':629, 'files':archived}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(REPORT / 'README.md').write_text('''# #629 검광 v2 실제 전투 영상 — 2026-10-05

PD 지시: 이펙트는 영상으로 보고. 실제 Godot MovieMaker 전투 렌더, 정상1×/기록60fps. 실시간 성능 측정이 아니다.

- video/629_sword_trail_before_after_60fps.mp4: 왼쪽 수정전 / 오른쪽 수정후. 평타3타·참격2회·회오리2회·치명3타, 각4.5초(총18초), 개선본 게임 소리.
- video/629_sword_trail_actual_60fps.mp4: 전체 게임 화면의 개선본 동일 네 구간18초, 게임 소리.
- video/*_engine_capture_60fps.mp4: 자막·크롭 이전 엔진 전체 촬영 전/후 각25.983초. AVI는 74MB의 로컬 인코딩 중간 파일이며 이 저장소에 넣지 않는다.

기준 소스76a5661e. 동일 카메라·무기·위치·시드(GameState20260916, PlayerCombat/Vfx629). 치명 구간만 QA용 crit_chance1이며 실제 게임 밸런스 수정이 아니다. 표적은 AI만 frozen/hp100000의 산적이며 실제 무기 애니·표본·피격·전투 판정을 쓴다. 입력은 기존 자동공격/스킬 경로. before/after 각19/19 PASS.

전후 타격프레임·공격간격·피해·MP debit·전투 RNG.state·리본 표시 프레임 수 모두 일치한다. 치명 명중 뒤 살아 있는 리본의 gold_frames만 달라진다. 피해량19/20/18/30, MP debit0/8/16/0. 캡처 범위와 원본 SHA, 전체디코딩 결과는 video_manifest.json·archive_manifest.json·logs/. 영상 각10MB미만, 카드50MB미만, H264·8bit4:2:0·60fps(full-range yuvj420p), 전체디코딩 오류0. 비교/적용은1080프레임/18초이며 AAC 패딩을 포함한 컨테이너18.021초, 연결 경계 AAC 약1.33ms DTS 보정 경고는 원문에 보존했고 영상 프레임 동기는 그대로다.

reproduce/ 파일을 게임 ._tmp/629_sword_trail_v2/에 복사하고 게임 루트에서 아래를 실행한다. BEFORE는 기준76a5661e, AFTER는 #629 구현 소스에서 따로 촬영한다.

```powershell
godot --path . --scene res://._tmp/629_sword_trail_v2/capture_scene.tscn --windowed --resolution 1280x720 --fixed-fps 60 --disable-vsync --quit-after 3000 --write-movie <작업트리절대경로>/._tmp/629_sword_trail_v2/before.avi --log-file <작업트리절대경로>/._tmp/629_sword_trail_v2/before.engine.log -- --new --phase=before *> ._tmp/629_sword_trail_v2/before.raw.log
# after.avi / after.engine.log / --phase=after / after.raw.log로 개선본 촬영
python ._tmp/629_sword_trail_v2/encode_video.py
python ._tmp/629_sword_trail_v2/archive_report.py
```

초기 촬영의 DamageCalc 정적 클래스를 오토로드 노드로 조회한 오류는 정상 정적 클래스 호출로 수정했다. 초기 오류 원문 발췌와 전투시드 고정 전 진단 로그도 logs/에 보존했다. 최종 촬영은 구문/셰이더/실행 오류0이며 기존 종료 리소스 정리 보고 원문은 포함한다. push는 하지 않는다.
''', encoding='utf-8')
total = sum(p.stat().st_size for p in REPORT.rglob('*') if p.is_file())
assert total < 50000000, total
print(json.dumps({'report':str(REPORT), 'videos':4, 'card_total_bytes':total, 'jpgs':6}, ensure_ascii=False))
