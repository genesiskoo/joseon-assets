"""Check immutable card519 sources and bounded previews against staged/committed Git blobs."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

REPORT = Path(__file__).resolve().parent
ASSET = REPORT.parents[2]
RECORD = REPORT / 'git_blob_verification_R4.json'
DEFAULT_GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/519-gumiho-phase1/joseon')


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def git(repo, *args, binary=False):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=not binary)


def expected_files(game):
    snapshot = load(REPORT / 'raw_preservation_R4.json')
    review = load(REPORT / 'structural_review_R4.json')
    archive = load(ASSET / 'reports/519/archive_game_previews_before_R4/preservation.json')
    rows = []
    for row in snapshot['original']:
        rows.append(dict(scope='asset', category='previous_raw', path=row['path'], raw_sha256=row['raw_sha256']))
    for row in snapshot['new_raw']:
        rows.append(dict(scope='asset', category='new_raw', path=row['path'], raw_sha256=row['raw_sha256']))
    for row in archive['files']:
        rows.append(dict(scope='asset', category='previous_gallery_archive',
                         path='reports/519/archive_game_previews_before_R4/' + row['filename'], raw_sha256=row['raw_sha256']))
    for row in review['gallery']:
        for scope, prefix in [('asset', 'reports/519/batch_R4_structure/review/'), ('game', 'docs/art/519_gumiho_phase1/')]:
            rows.append(dict(scope=scope, category='review_jpeg', path=prefix + row['filename'], raw_sha256=row['raw_sha256']))
    for ref in sorted((ASSET / 'workbench/production/gumiho_phase1_519/refs').glob('*.png')):
        rows.append(dict(scope='asset', category='input_reference', path=ref.relative_to(ASSET).as_posix(), raw_sha256=sha_bytes(ref.read_bytes())))
    for absolute, expected in review['approval_ledgers_unchanged'].items():
        path = Path(absolute)
        scope, repo = ('asset', ASSET) if path.is_relative_to(ASSET) else ('game', game)
        rows.append(dict(scope=scope, category='protected_approval', path=path.relative_to(repo).as_posix(), raw_sha256=expected))
    return rows


def verify(rows, game, staged):
    for row in rows:
        repo = ASSET if row['scope'] == 'asset' else game
        path = repo / row['path']
        assert sha_bytes(path.read_bytes()) == row['raw_sha256'], f'Raw bytes changed: {row["scope"]}/{row["path"]}'
        ref = (':' if staged else 'HEAD:') + row['path']
        oid = git(repo, 'rev-parse', ref).strip()
        assert oid == git(repo, 'hash-object', '--path=' + row['path'], str(path)).strip(), f'Git blob differs from worktree: {row["path"]}'
        blob_sha = sha_bytes(git(repo, 'cat-file', 'blob', oid, binary=True))
        if 'git_blob' in row:
            assert oid == row['git_blob'] and blob_sha == row['git_blob_sha256'], f'Recorded Git blob changed: {row["path"]}'
        else:
            row.update(git_blob=oid, git_blob_sha256=blob_sha, git_blob_bytes_equal_raw=(blob_sha == row['raw_sha256']))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=Path, default=DEFAULT_GAME)
    parser.add_argument('--stage-record', action='store_true')
    args = parser.parse_args()
    game = args.game.resolve()
    if args.stage_record:
        rows = verify(expected_files(game), game, staged=True)
        result = dict(card=519, status='PASS', recorded_from='staged index',
                      raw_and_git_blob_hashes_separate=True, files=rows,
                      note='Raw SHA preserves physical bytes; Git blob SHA also records any normal Git newline filter.')
        RECORD.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    else:
        result = load(RECORD)
        rows = verify(result['files'], game, staged=False)
    filtered = sum(not row['git_blob_bytes_equal_raw'] for row in rows)
    print(f'PASS #519 Git blobs: {len(rows)} sources/receipts/archive/previews/approval records, raw SHA intact; newline-filtered records {filtered}; tree={"INDEX" if args.stage_record else "HEAD"}')


if __name__ == '__main__':
    main()
