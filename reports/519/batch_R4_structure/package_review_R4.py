"""Preserve card519 receipts and package bounded, uncropped R4 review JPEGs."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

REPORT = Path(__file__).resolve().parent
REPO = REPORT.parents[2]
PROD = REPO / 'workbench/production/gumiho_phase1_519'
ARCHIVE = REPO / 'reports/519/archive_game_previews_before_R4'
DEFAULT_GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/519-gumiho-phase1/joseon')
SELECTED = [('R4_front_v2', 'R4_front.jpg'), ('R4_rear', 'R4_rear.jpg'),
            ('R4_side', 'R4_side.jpg'), ('R4_low_v2', 'R4_low.jpg'), ('R4_duo_v2', 'R4_duo.jpg')]
EXPECTED_JOBS = ['R4_front', 'R4_rear', 'R4_front_v2', 'R4_side', 'R4_low', 'R4_duo', 'R4_low_v2', 'R4_duo_v2']
TOKEN = re.compile(rb'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|Bearer\s+[A-Za-z0-9_.=-]{20,})')
SIGNED_URL = re.compile(rb'[?&](?:X-Amz-(?:Signature|Security-Token|Credential)|access_token|api_key|token)=[^\s"&]+', re.I)
SECRET_KEY = re.compile(r'^(?:api[_-]?key|authorization|password|secret|auth[_-]?token|access[_-]?token|refresh[_-]?token|cookie|client[_-]?secret)$', re.I)
KEY_NAMES = ['COMFY_CLOUD_API_KEY', 'COMFY_API_KEY']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(repo, *args, binary=False):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=not binary)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def raw_snapshot():
    original = [p for p in git(REPO, 'ls-tree', '-r', '--name-only', 'HEAD', '--', 'reports/519').splitlines()
                if not p.startswith('reports/519/batch_R4_structure/') and (p.endswith('.png') or p.endswith('.api.json') or p.endswith('.job.json'))]
    assert len(original) >= 86
    rows = []
    for relative in original:
        path = REPO / relative
        oid = git(REPO, 'rev-parse', f'HEAD:{relative}').strip()
        assert git(REPO, 'hash-object', f'--path={relative}', str(path)).strip() == oid
        rows.append(dict(path=relative, raw_sha256=sha(path), git_blob=oid,
                         git_blob_sha256=hashlib.sha256(git(REPO, 'cat-file', 'blob', oid, binary=True)).hexdigest()))
    new_raw = []
    for uid in EXPECTED_JOBS:
        for suffix in ['.png', '.api.json', '.job.json', '.history.json', '.prompt.txt']:
            path = REPORT / (uid + suffix)
            assert path.exists(), f'Missing immutable receipt: {path.name}'
            new_raw.append(dict(path=path.relative_to(REPO).as_posix(), raw_sha256=sha(path)))
    return dict(original_records=len(rows), original=rows, new_jobs=8, new_raw=new_raw)


def archive_game(gallery, game):
    relative = 'docs/art/519_gumiho_phase1'
    main_files = set(git(game, 'ls-tree', '-r', '--name-only', 'main', '--', relative).splitlines())
    if (ARCHIVE / 'preservation.json').exists():
        prior = json.loads((ARCHIVE / 'preservation.json').read_text(encoding='utf-8-sig'))
        for row in prior['files']:
            assert sha(ARCHIVE / row['filename']) == row['raw_sha256']
        return prior
    jpgs = list(gallery.glob('*.jpg'))
    assert len(jpgs) == 6
    assert not any(p.relative_to(game).as_posix() in main_files for p in jpgs), 'Main tracks prior preview; report to root before deletion'
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(gallery.iterdir()):
        if not path.is_file():
            continue
        shutil.copyfile(path, ARCHIVE / path.name)
        assert sha(path) == sha(ARCHIVE / path.name)
        rows.append(dict(filename=path.name, raw_sha256=sha(path), bytes=path.stat().st_size))
    record = dict(card=519, previous_game_head=git(game, 'rev-parse', 'HEAD').strip(),
                  main_head=git(game, 'rev-parse', 'main').strip(), main_tracked_preview_files=sorted(main_files),
                  original_jpg_count=6, files=rows, removed_from_main=False)
    write_json(ARCHIVE / 'preservation.json', record)
    return record


def credential_values(game):
    # Values remain only in memory for local comparison; no key or credential digest is recorded.
    values = {os.environ[name] for name in KEY_NAMES if os.environ.get(name)}
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as registry:
            for name in KEY_NAMES:
                try:
                    values.add(winreg.QueryValueEx(registry, name)[0])
                except OSError:
                    pass
    except OSError:
        pass
    env_path = game / '.env'
    if env_path.exists():
        with env_path.open(encoding='utf-8-sig') as stream:
            for line in stream:
                match = re.match(r'\s*(?:export\s+)?(' + '|'.join(KEY_NAMES) + r')\s*=\s*(.*?)\s*$', line)
                if match:
                    values.add(match.group(2).strip().strip(chr(34)).strip(chr(39)))
    return [value for value in values if isinstance(value, str) and len(value) >= 16]


def scan_fields(value, location, findings):
    if isinstance(value, dict):
        for key, child in value.items():
            where = location + '/' + str(key)
            if SECRET_KEY.fullmatch(str(key)) and isinstance(child, str) and child and child not in ['<redacted>', 'REDACTED', '***']:
                findings.append(dict(file=where, reason='Credential-like JSON field; value omitted'))
            scan_fields(child, where, findings)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            scan_fields(child, location + '/' + str(i), findings)
    elif isinstance(value, str) and value.startswith(('{', '[')):
        try:
            scan_fields(json.loads(value), location, findings)
        except json.JSONDecodeError:
            pass


def audit(game):
    known = credential_values(game)
    needles = [value.encode(enc) for value in known for enc in ['utf-8', 'utf-16-le', 'utf-16-be']]
    findings, text_count, png_count = [], 0, 0
    candidates = set((REPO / 'reports/519').rglob('*')) | set(PROD.rglob('*'))
    for path in sorted(candidates):
        if not path.is_file() or '__pycache__' in path.parts or path.name in ['credential_audit_R4.json', 'package_stdout.txt', 'package_post_commit_stdout.txt']:
            continue
        is_png = path.suffix == '.png'
        if not is_png and path.suffix not in ['.json', '.md', '.txt', '.py']:
            continue
        location = path.relative_to(REPO).as_posix()
        bodies = [path.read_bytes()]
        if is_png:
            png_count += 1
            with Image.open(path) as image:
                for key, value in image.info.items():
                    if isinstance(value, bytes):
                        bodies.append(value)
                    elif isinstance(value, str):
                        bodies.append(value.encode('utf-8'))
                        scan_fields(value, location + '/PNG/' + key, findings)
        else:
            text_count += 1
            if path.suffix == '.json':
                scan_fields(json.loads(path.read_text(encoding='utf-8-sig')), location, findings)
        for data in bodies:
            if TOKEN.search(data) or SIGNED_URL.search(data):
                findings.append(dict(file=location, reason='Credential/token/signed URL pattern; value omitted'))
            if any(needle in data for needle in needles):
                findings.append(dict(file=location, reason='Known local credential bytes; value omitted'))
    result = dict(card=519, text_files_checked=text_count, png_bytes_and_decoded_metadata_checked=png_count,
                  actual_local_credentials_compared=len(known), actual_key_values_printed=False,
                  findings=findings, status='PASS' if not findings else 'FAIL')
    write_json(REPORT / 'credential_audit_R4.json', result)
    assert not findings, 'Credential-like content found; report contains only paths/reasons, never values'
    return result


def validate_jobs():
    rows = []
    assert len(list(REPORT.glob('*.job.json'))) == 8
    for uid in EXPECTED_JOBS:
        job_path, api_path = REPORT / f'{uid}.job.json', REPORT / f'{uid}.api.json'
        job = json.loads(job_path.read_text(encoding='utf-8'))
        png = REPORT / job['output']
        assert png == REPORT / f'{uid}.png' and job['state'] == 'downloaded'
        assert sha(png) == job['output_sha256']
        api = json.loads(api_path.read_text(encoding='utf-8'))
        prompts = [node.get('inputs', {}).get('prompt') for node in api.values() if isinstance(node, dict)]
        prompt = next(value for value in prompts if isinstance(value, str))
        assert hashlib.sha256(prompt.encode('utf-8')).hexdigest() == job['prompt_sha256']
        assert (REPORT / f'{uid}.prompt.txt').read_text(encoding='utf-8').rstrip('\n') == prompt.rstrip('\n')
        for ref in job['reference_images']:
            assert sha(Path(ref['path'])) == ref['sha256'], f'Input reference changed: {uid}'
        history_path = REPORT / f'{uid}.history.json'
        history = json.loads(history_path.read_text(encoding='utf-8'))
        assert history['status']['completed'] and history['status']['status_str'] == 'success'
        with Image.open(png) as image:
            assert list(image.size) == job['actual_dimensions'] and image.mode == job['actual_mode']
            image.verify()
        rows.append(dict(id=uid, png_sha256=sha(png), api_sha256=sha(api_path), job_sha256=sha(job_path),
                         history_sha256=sha(history_path), prompt_file_sha256=sha(REPORT / f'{uid}.prompt.txt'),
                         prompt_id=job['prompt_id'], dimensions=job['actual_dimensions']))
    return rows


def save_jpeg(image, destination):
    for quality in [86, 82, 78, 74, 70, 66]:
        image.save(destination, quality=quality, optimize=True)
        if destination.stat().st_size <= 300000:
            return
    raise AssertionError('Review JPEG cannot fit 300KB: ' + destination.name)


def preview(source, destination):
    image = Image.open(source).convert('RGB')
    scale = min(1.0, 1280 / image.width)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    save_jpeg(image, destination)


def before_after(destination):
    sheet = Image.new('RGB', (1280, 960), '#25211e')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 23)
    for uid, x, title in [('R4_front', 20, '수정 전 · 끝10 / 기각'), ('R4_front_v2', 660, '수정 후 · 왼4+오5=끝9 / 후보')]:
        raw = Image.open(REPORT / f'{uid}.png').convert('RGB')
        assert raw.size == (1536, 2048)
        sheet.paste(raw.resize((600, 800), Image.Resampling.LANCZOS), (x, 76))
        draw.text((x, 24), title, font=font, fill='#e5d5bd')
    draw.text((20, 905), '같은 배치의 전신 원화 · 개별 뿌리/관절/아이소는 후속3D 검수 · 새R4 미채택', font=font, fill='#c6b99f')
    save_jpeg(sheet, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=Path, default=DEFAULT_GAME)
    args = parser.parse_args()
    game = args.game.resolve()
    gallery = game / 'docs/art/519_gumiho_phase1'
    snapshot = raw_snapshot()
    snapshot_path = REPORT / 'raw_preservation_R4.json'
    if snapshot_path.exists():
        assert json.loads(snapshot_path.read_text(encoding='utf-8')) == snapshot, 'Original source/receipt bytes changed'
    else:
        write_json(snapshot_path, snapshot)
    protected = [REPO / 'reports/519/gpt_model_selection_2026_10_01.json', gallery / 'model_selection.json']
    protection = {path.as_posix(): sha(path) for path in protected}
    archived = archive_game(gallery, game)
    jobs = validate_jobs()
    security = audit(game)
    review = REPORT / 'review'
    review.mkdir(exist_ok=True)
    for uid, name in SELECTED:
        preview(REPORT / f'{uid}.png', review / name)
    before_after(review / 'R4_front_before_after.jpg')
    names = [name for _, name in SELECTED] + ['R4_front_before_after.jpg']
    rows = []
    main_files = set(git(game, 'ls-tree', '-r', '--name-only', 'main', '--', 'docs/art/519_gumiho_phase1').splitlines())
    for old in gallery.glob('*.jpg'):
        if old.name not in names:
            assert old.relative_to(game).as_posix() not in main_files
            assert sha(old) == sha(ARCHIVE / old.name)
            assert old.resolve().is_relative_to(gallery.resolve())
            old.unlink()
    for name in names:
        path = review / name
        assert Image.open(path).width <= 1280 and path.stat().st_size <= 300000
        shutil.copyfile(path, gallery / name)
        rows.append(dict(filename=name, raw_sha256=sha(path), bytes=path.stat().st_size, size=list(Image.open(path).size)))
    assert len(list(gallery.glob('*.jpg'))) == 6 and sum(row['bytes'] for row in rows) <= 2000000
    assert all(sha(path) == expected for path, expected in protection.items())
    selection = dict(card=519, revision='R4_structure', status='candidate_pending_pd',
                     selected=[dict(id=uid, raw_png=f'reports/519/batch_R4_structure/{uid}.png', sha256=sha(REPORT / f'{uid}.png')) for uid, _ in SELECTED],
                     rejected_ten_tail_ids=['R4_front', 'R4_low', 'R4_duo'],
                     existing_pd_adoption=dict(gaze='C', costume='P1', low_human_pose='P5', hospitality_support='P3'),
                     modeling_complete=False, rigging_complete=False, game_intake_complete=False, main_landed=False)
    write_json(PROD / 'structural_selection_R4.json', selection)
    result = dict(selection, jobs=jobs, source_preservation=snapshot,
                  approval_ledgers_unchanged=protection, archive=archived,
                  observations=dict(front_v2=dict(tail_tips=9, screen_left=4, screen_right=5, hands=2, visible_feet=2, individual_roots_verified=False),
                                    rear=dict(tail_tips=9, below_waist_root_cluster=True, hands=2, visible_feet=2, individual_nine_attachments_verified=False),
                                    side=dict(visible_tail_tips=6, hands=2, visible_feet=2, nine_tail_proof=False, use='costume and limb profile only'),
                                    low_v2=dict(tail_tips=9, screen_left=4, screen_right=5, hands=2, visible_feet=1, rear_foot_occluded=True, both_feet_verified=False),
                                    duo_v2=dict(tail_tips=9, screen_left=4, screen_right=5, gumiho_hands=2, gumiho_visible_feet=2, use='H1 character tone/proportion only, not in-game isometric proof')),
                  remaining_3d_checks=['nine individual roots and independent attachment', 'cross-view joint/shape consistency', 'cloth/tail rigging and collisions', 'actual isometric game readability'],
                  cad_identical_cross_view_geometry_claimed=False, source_pixels_modified=False,
                  comparison='Full source front10 vs corrected front9, same uncropped panel composition',
                  security_audit=security, gallery=rows)
    write_json(REPORT / 'structural_review_R4.json', result)
    write_json(gallery / 'structural_review_R4.json', result)
    print(f'PASS #519 R4: original{snapshot["original_records"]} Git blobs/raw SHA preserved; new8 jobs/PNG/API/job/prompt/history SHA verified; JPEG6 <=1280/300KB; original preview6 archived; no deletion against main')
    print(f'PASS #519 credential audit: PNG bytes/decoded metadata{security["png_bytes_and_decoded_metadata_checked"]}, text{security["text_files_checked"]}, known local credentials{security["actual_local_credentials_compared"]}; findings0/values not printed')


if __name__ == '__main__':
    main()
