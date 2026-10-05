"""Attach final committed source, complete QA raw logs and hashes without re-encoding."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess

BASE = Path(__file__).resolve().parent
GAME = BASE.parents[1]
REPORT = Path('C:/workspace/joseon-assets/reports/629_sword_trail_v2')
assert REPORT.resolve().is_relative_to(Path('C:/workspace/joseon-assets/reports').resolve())
manifest_path = REPORT / 'video/video_manifest.json'
video = json.loads(manifest_path.read_text(encoding='utf-8'))
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=GAME, text=True).strip()
assert subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=GAME, text=True).strip() == ''
full = (BASE / 'full_test.raw.log').read_text(encoding='utf-8-sig')
assert 'E2E body_arts FAIL (검사 65, 실패 1)' in full
unit_passes = re.findall(r'^\s+PASS\s+(test_\S+\.gd)\s', full, re.M)
assert len(unit_passes) == len(set(unit_passes)) == 97
assert len(re.findall(r'^\s+PASS\s+settings restart (?:write|read)\s', full, re.M)) == 2
assert len(re.findall(r'^\s+PASS\s+\S+\.(?:gd|py) --selftest\s', full, re.M)) == 23
assert not re.search(r'^\s+(?:FAIL|TIMEOUT)\s', full, re.M)
final_e2e = (BASE / 'final_e2e.raw.log').read_text(encoding='utf-8-sig')
assert '전부 PASS' in final_e2e and 'E2E SUMMARY:' in final_e2e
assert all(a == b for a, b in re.findall(r'E2E SUMMARY: (\d+)/(\d+) PASS', final_e2e))
assert sum(int(a) for a, b in re.findall(r'E2E SUMMARY: (\d+)/(\d+) PASS', final_e2e)) == 140
paths = ['actors/sword_trail.gd','actors/actor_visual.gd','actors/player_combat.gd','core/vfx_meshes.gd']
video['after_source_commit'] = commit
video['after_runtime_sha256'] = {p:hashlib.sha256((GAME / p).read_bytes()).hexdigest() for p in paths}
video['final_full_regression'] = {
    'initial': 'test.ps1 exit1; units97/settings2/tools23/runner5 PASS; E2E139/140, unseeded body_arts fixture failed',
    'fixture_fix': 'body_arts native bandit seed248 before first physics attack; no runtime changes',
    'final': 'test.ps1 -E2e exit0; E2E140/140; runner5/5 PASS',
    'raw_logs': ['logs/full_test.raw.log', 'logs/final_e2e.raw.log'],
}
video['pixel_format'] = 'full-range 8bit 4:2:0 (yuvj420p); H264'
for f in video['files']:
    target = REPORT / 'video' / f['file']
    assert hashlib.sha256(target.read_bytes()).hexdigest() == f['sha256']
    probe = subprocess.check_output([shutil.which('ffprobe'), '-v', 'error', '-show_entries', 'stream=codec_name,width,height,pix_fmt,color_range,r_frame_rate,nb_frames:format=duration,size', '-of', 'json', str(target)], text=True)
    f['probe'] = json.loads(probe)
manifest_path.write_text(json.dumps(video, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
readme = REPORT / 'README.md'
readme_text = readme.read_text(encoding='utf-8')
readme_text = readme_text.split('\n## 최종 소스와 검증\n')[0]
readme_text = readme_text.replace('H264/yuv420p/60fps, 전체디코딩 오류0.',
    'H264·8bit4:2:0·60fps(full-range yuvj420p), 전체디코딩 오류0. 비교/적용은1080프레임/18초이며 AAC 패딩을 포함한 컨테이너18.021초, 연결 경계 AAC 약1.33ms DTS 보정 경고는 원문에 보존했고 영상 프레임 동기는 그대로다.')
readme.write_text(readme_text + '\n## 최종 소스와 검증\n\n'
    + f'게임 소스 커밋 `{commit}`. 영상 적용 런타임의 SHA256은 `video/video_manifest.json`에 기록했다.\n\n'
    + '최초 전체 검사: 단위97·설정 재시작2·도구23·러너5/5 PASS, E2E139/140의 기존 body_arts 피격 fixture만 실패. 산적 몸 시드가 고정되지 않은 시험을 첫 물리 공격 전 seed248로 고정하고 실패 진단을 추가했다. 실제 AI·명중·방패 경로와 게임 런타임은 유지한다. 보완 뒤 단독2회66검사 PASS, 최종 `test.ps1 -E2e` 종료0·140/140 PASS. 최초 실패와 최종 성공 원문 및 E2E 각 phase 상세 원문을 logs/에 함께 보존했다.\n', encoding='utf-8')
# Keep failed attempts separately alongside the successful final raw output.
for p in BASE.glob('*.log'):
    shutil.copy2(p, REPORT / 'logs' / p.name)
for p in (GAME / '._tmp/629_sword_trail/unit').glob('*.log'):
    shutil.copy2(p, REPORT / 'logs' / ('unit_' + p.name))
for p in [BASE / 'archive_report.py', BASE / 'encode_video.py', BASE / 'finalize_report.py']:
    shutil.copy2(p, REPORT / 'reproduce' / p.name)
raws = []
for log in sorted(BASE.glob('*e2e*.raw.log')) + [BASE / 'full_test.raw.log'] + sorted(BASE.glob('body_arts*.raw.log')):
    text = log.read_text(encoding='utf-8-sig')
    for raw in re.findall(r'^E2E_PHASE_RAW (.+)$', text, re.M):
        folder = Path(raw.strip())
        assert folder.resolve().is_relative_to((GAME / 'tmp/e2e_raw').resolve())
        destination = REPORT / 'logs/e2e_raw' / folder.parent.name / folder.name
        shutil.copytree(folder, destination, dirs_exist_ok=True)
        raws.append(str(destination.relative_to(REPORT)))
archive = []
# These are byte-hashed raw artifacts; Git must not normalize their line endings.
(REPORT / '.gitattributes').write_bytes(b'* -text -diff\n')
for p in sorted(REPORT.rglob('*')):
    if p.is_file() and p.name != 'archive_manifest.json':
        assert p.stat().st_size < 10000000, p
        archive.append({'file':p.relative_to(REPORT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
total = sum(f['bytes'] for f in archive)
assert total < 50000000, total
(REPORT / 'archive_manifest.json').write_text(json.dumps({'card':629,'game_commit':commit,'files':archive,'e2e_raw_folders':raws}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'game_commit':commit,'files':len(archive),'card_total_bytes':total,'e2e_raw_folders':len(raws)}, ensure_ascii=False))
