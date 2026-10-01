"""Commit only card #534's review docs and separately audited asset revision."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image
import finalize_potion_rank_v3_534 as audit

ROOT, ASSET, HERE, REPORT, GAME = audit.ROOT, audit.ASSET, audit.HERE, audit.REPORT, audit.GAME
GAME_FILES = ['docs/art/534_potion_grade/' + name for name in
              ['actual.jpg', 'alpha_comparison.jpg', 'before_actual.jpg', 'before_overview.jpg',
               'belt_stress.jpg', 'overview.jpg', 'blind.jpg']]
GAME_FILES += ['docs/design/ui_v2.md', 'docs/design/potion_rank_534_2026-10-02.md', 'docs/design/potion_rank_534_log.md']
ASSET_DIRS = ['workbench/production/item_icons_534/rank_v3_2026-10-02', 'reports/534/2026-10-02_comfy_rank_v3']


def git(repo, *args):
    result = subprocess.run(['git', '-c', 'safe.directory=' + str(repo), '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        print((result.stdout + result.stderr).decode('utf-8', errors='replace'))
        raise SystemExit(result.returncode)
    return result.stdout


def verify_stage(repo):
    rows = []
    for relative in git(repo, 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z').decode().split('\0'):
        if not relative:
            continue
        source = (repo / relative).read_bytes()
        staged = git(repo, 'show', ':' + relative)
        assert staged == source, 'Staging altered exact bytes: ' + relative
        rows.append({'path': relative, 'sha256': hashlib.sha256(staged).hexdigest(), 'bytes': len(staged)})
    return rows


def main():
    record = ROOT / '._tmp/potion_rank_v3_commits_534.json'
    if record.exists():
        raise SystemExit('The candidate commits already exist; inspect their record instead.')
    assert not git(GAME, 'diff', '--cached', '--name-only')
    assert not git(ASSET, 'diff', '--cached', '--name-only')
    game_status = git(GAME, 'status', '--porcelain=v1', '--untracked-files=all').decode()
    assert all(line[3:] in GAME_FILES for line in game_status.splitlines())
    asset_status = git(ASSET, 'status', '--porcelain=v1', '--untracked-files=all').decode()
    assert all(any(line[3:].startswith(folder + '/') for folder in ASSET_DIRS) for line in asset_status.splitlines())
    assert audit.old.snapshot(GAME) == json.loads((HERE / 'runtime_before.json').read_text(encoding='utf-8'))
    shutil.copy2(Path(__file__), REPORT / 'reproduction' / Path(__file__).name)
    checked, findings = [], []
    for folder in (HERE, REPORT):
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            text = None
            if path.suffix.lower() in ('.json', '.txt', '.md', '.py', '.gd', '.ps1', '.log'):
                text = path.read_bytes().decode('utf-8-sig', errors='replace')
                if path.suffix == '.json':
                    audit.scan.walk(json.loads(text), path.relative_to(ASSET).as_posix(), findings)
            elif path.suffix.lower() == '.png':
                text = json.dumps(Image.open(path).info, default=str)
            if text is None:
                continue
            if audit.scan.TOKEN_VALUE.search(text) or audit.scan.SIGNED_URL.search(text):
                findings.append({'path': path.relative_to(ASSET).as_posix(), 'reason': 'Credential pattern; value not printed'})
            checked.append({'path': path.relative_to(ASSET).as_posix(), 'sha256': audit.sha(path)})
    assert not findings, 'Secret-like contents found; no staging or publishing occurred.'
    audit.save_json(REPORT / 'receipt_audit_final.json', {'card': 534, 'status': 'PASS', 'checked_files': len(checked),
                                                       'findings': findings, 'checked': checked, 'png_metadata_included': True,
                                                       'secret_values_printed': False})
    git(ASSET, 'add', '--', *ASSET_DIRS)
    asset_blobs = verify_stage(ASSET)
    audit.save_json(REPORT / 'staged_byte_proof.json', {'card': 534, 'status': 'PASS', 'files': asset_blobs,
                                                      'raw_original_bytes_preserved': True, 'source': 'git index vs exact current files'})
    git(ASSET, 'add', '--', str((REPORT / 'staged_byte_proof.json').relative_to(ASSET)).replace('\\', '/'))
    verify_stage(ASSET)
    git(ASSET, 'diff', '--cached', '--check')
    git(GAME, 'add', '--', *GAME_FILES)
    game_blobs = verify_stage(GAME)
    git(GAME, 'diff', '--cached', '--check')
    git(ASSET, 'commit', '-m', 'art(#534): clarify potion efficacy with size and seal hierarchy')
    git(GAME, 'commit', '-m', 'docs(#534): review revised potion hierarchy at actual UI sizes')
    result = {'card': 534, 'game': git(GAME, 'rev-parse', 'HEAD').decode().strip(),
              'assets': git(ASSET, 'rev-parse', 'HEAD').decode().strip(), 'adoption': 'pending_PD',
              'runtime_intake': False, 'runtime_scale_policy_installed': False, 'push': False,
              'asset_files_byte_identical_to_stage': len(asset_blobs) + 1, 'game_files_byte_identical_to_stage': len(game_blobs)}
    audit.save_json(record, result)
    assert not git(GAME, 'status', '--porcelain=v1') and not git(ASSET, 'status', '--porcelain=v1')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
