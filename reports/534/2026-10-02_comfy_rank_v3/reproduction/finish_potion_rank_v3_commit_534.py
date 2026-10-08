"""Finish #534 after preserving one copied CRLF receipt's exact Git bytes."""
import json
import shutil
from pathlib import Path

import commit_potion_rank_v3_534 as previous


def main():
    ROOT, ASSET, HERE, REPORT, GAME = previous.ROOT, previous.ASSET, previous.HERE, previous.REPORT, previous.GAME
    record = ROOT / '._tmp/potion_rank_v3_commits_534.json'
    if record.exists():
        raise SystemExit('Already committed; inspect the candidate record.')
    assert not previous.git(GAME, 'diff', '--cached', '--name-only')
    staged = previous.git(ASSET, 'diff', '--cached', '--name-only').decode().splitlines()
    assert staged and all(any(path.startswith(folder + '/') for folder in previous.ASSET_DIRS) for path in staged)
    attrs = HERE / '.gitattributes'
    assert not attrs.exists()
    attrs.write_text('preserved_basic_sources.json -text\n', encoding='utf-8', newline='\n')
    # Transcript of the previous tool result, unabridged. Original receipt file is unchanged.
    failure = '''Traceback (most recent call last):
  File "C:\\workspace\\joseon\\._tmp\\commit_potion_rank_v3_534.py", line 95, in <module>
    main()
  File "C:\\workspace\\joseon\\._tmp\\commit_potion_rank_v3_534.py", line 74, in main
    asset_blobs = verify_stage(ASSET)
                  ^^^^^^^^^^^^^^^^^^^
  File "C:\\workspace\\joseon\\._tmp\\commit_potion_rank_v3_534.py", line 35, in verify_stage
    assert staged == source, 'Staging altered exact bytes: ' + relative
           ^^^^^^^^^^^^^^^^
AssertionError: Staging altered exact bytes: workbench/production/item_icons_534/rank_v3_2026-10-02/preserved_basic_sources.json
'''
    (REPORT / 'commit_attempt1.tool_output.txt').write_text(failure, encoding='utf-8', newline='\r\n')
    previous.audit.save_json(REPORT / 'commit_byte_fix.json', {'card': 534, 'attempt1': 'failed before commit',
                              'exact_transcript': 'commit_attempt1.tool_output.txt',
                              'cause': 'Git text normalization of copied preserved_basic_sources.json',
                              'fix': 'One-file -text attribute; reapply staging only for card revision paths.',
                              'original_file_bytes_modified': False})
    shutil.copy2(Path(__file__), REPORT / 'reproduction' / Path(__file__).name)
    previous.git(ASSET, 'add', '--', *previous.ASSET_DIRS)
    previous.git(ASSET, 'add', '--renormalize', '--', *previous.ASSET_DIRS)
    asset_blobs = previous.verify_stage(ASSET)
    previous.audit.save_json(REPORT / 'staged_byte_proof.json', {'card': 534, 'status': 'PASS', 'files': asset_blobs,
                                                              'raw_original_bytes_preserved': True,
                                                              'source': 'git index vs exact current files'})
    previous.git(ASSET, 'add', '--', 'reports/534/2026-10-02_comfy_rank_v3/staged_byte_proof.json')
    previous.verify_stage(ASSET)
    previous.git(ASSET, 'diff', '--cached', '--check')
    previous.git(GAME, 'add', '--', *previous.GAME_FILES)
    game_blobs = previous.verify_stage(GAME)
    previous.git(GAME, 'diff', '--cached', '--check')
    previous.git(ASSET, 'commit', '-m', 'art(#534): clarify potion efficacy with size and seal hierarchy')
    previous.git(GAME, 'commit', '-m', 'docs(#534): review revised potion hierarchy at actual UI sizes')
    result = {'card': 534, 'game': previous.git(GAME, 'rev-parse', 'HEAD').decode().strip(),
              'assets': previous.git(ASSET, 'rev-parse', 'HEAD').decode().strip(), 'adoption': 'pending_PD',
              'runtime_intake': False, 'runtime_scale_policy_installed': False, 'push': False,
              'asset_files_byte_identical_to_stage': len(asset_blobs) + 1,
              'game_files_byte_identical_to_stage': len(game_blobs)}
    previous.audit.save_json(record, result)
    assert not previous.git(GAME, 'status', '--porcelain=v1') and not previous.git(ASSET, 'status', '--porcelain=v1')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
