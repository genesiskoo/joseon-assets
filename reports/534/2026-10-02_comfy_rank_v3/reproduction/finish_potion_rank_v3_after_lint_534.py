"""Preserve copied receipt whitespace, retain the diagnostic, and commit #534."""
import json
import shutil
import subprocess
from pathlib import Path

import commit_potion_rank_v3_534 as task


def main():
    ROOT, ASSET, HERE, REPORT, GAME = task.ROOT, task.ASSET, task.HERE, task.REPORT, task.GAME
    record = ROOT / '._tmp/potion_rank_v3_commits_534.json'
    if record.exists():
        raise SystemExit('Already committed; inspect the record.')
    assert not task.git(GAME, 'diff', '--cached', '--name-only')
    staged_paths = task.git(ASSET, 'diff', '--cached', '--name-only').decode().splitlines()
    assert staged_paths and all(any(path.startswith(folder + '/') for folder in task.ASSET_DIRS) for path in staged_paths)
    attrs = HERE / '.gitattributes'
    assert attrs.read_text(encoding='utf-8') == 'preserved_basic_sources.json -text\n'
    diagnostic = subprocess.run(['git', '-c', 'safe.directory=' + str(ASSET), '-C', str(ASSET),
                                 'diff', '--cached', '--check'], capture_output=True)
    assert diagnostic.returncode and b'preserved_basic_sources.json' in diagnostic.stdout
    for stream, data in [('stdout', diagnostic.stdout), ('stderr', diagnostic.stderr)]:
        path = REPORT / f'lint_recheck_before_attribute_fix.{stream}.raw.log'
        assert not path.exists()
        path.write_bytes(data)
    attrs.write_text('preserved_basic_sources.json -text -whitespace\n', encoding='utf-8', newline='\n')
    task.audit.save_json(REPORT / 'lint_attribute_fix.json', {'card': 534, 'scope': 'preserved_basic_sources.json only',
                         'cause': 'Exact preserved CRLF receipt was reported as trailing whitespace.',
                         'original_bytes_modified': False, 'fix': 'Disable text conversion and whitespace lint for this archived receipt only.',
                         'raw_diagnostic': 'lint_recheck_before_attribute_fix.stdout.raw.log'})
    shutil.copy2(Path(__file__), REPORT / 'reproduction' / Path(__file__).name)
    task.git(ASSET, 'add', '--', *task.ASSET_DIRS)
    asset_blobs = task.verify_stage(ASSET)
    task.audit.save_json(REPORT / 'staged_byte_proof_final.json', {'card': 534, 'status': 'PASS', 'files': asset_blobs,
                         'raw_original_bytes_preserved': True, 'source': 'Git index vs exact current files after scoped receipt attribute fix.'})
    task.git(ASSET, 'add', '--', 'reports/534/2026-10-02_comfy_rank_v3/staged_byte_proof_final.json')
    task.verify_stage(ASSET)
    task.git(ASSET, 'diff', '--cached', '--check')
    task.git(GAME, 'add', '--', *task.GAME_FILES)
    game_blobs = task.verify_stage(GAME)
    task.git(GAME, 'diff', '--cached', '--check')
    assert task.audit.old.snapshot(GAME) == json.loads((HERE / 'runtime_before.json').read_text(encoding='utf-8'))
    task.git(ASSET, 'commit', '-m', 'art(#534): clarify potion efficacy with size and seal hierarchy')
    task.git(GAME, 'commit', '-m', 'docs(#534): review revised potion hierarchy at actual UI sizes')
    result = {'card': 534, 'game': task.git(GAME, 'rev-parse', 'HEAD').decode().strip(),
              'assets': task.git(ASSET, 'rev-parse', 'HEAD').decode().strip(), 'adoption': 'pending_PD',
              'runtime_intake': False, 'runtime_scale_policy_installed': False, 'push': False,
              'asset_files_byte_identical_to_stage': len(asset_blobs) + 1,
              'game_files_byte_identical_to_stage': len(game_blobs)}
    task.audit.save_json(record, result)
    assert not task.git(GAME, 'status', '--porcelain=v1') and not task.git(ASSET, 'status', '--porcelain=v1')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
