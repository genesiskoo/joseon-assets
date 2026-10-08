"""Land approved #534 review docs, preserving native logs and production files."""
import importlib.util
import json
import subprocess

import approve_potion_534_queue as task

ROOT, GAME, ASSET, REPORT = task.ROOT, task.GAME, task.ASSET, task.REPORT
spec = importlib.util.spec_from_file_location('potion534_snapshot', ASSET / 'workbench/production/item_icons_534/prepare_534.py')
art = importlib.util.module_from_spec(spec)
spec.loader.exec_module(art)


def native(name, args, cwd=ROOT):
    target = REPORT / f'{name}.stdout.raw.log'
    if target.exists():
        raise SystemExit('Retain existing diagnostic; inspect before retrying: ' + name)
    r = subprocess.run(args, cwd=cwd, env=task.task_env, capture_output=True, timeout=240)
    target.write_bytes(r.stdout)
    (REPORT / f'{name}.stderr.raw.log').write_bytes(r.stderr)
    text = (r.stdout + r.stderr).decode('utf-8', errors='replace')
    if r.returncode or '⏳' in text:
        print(text, flush=True)
        raise SystemExit(r.returncode or 1)
    print(text, flush=True)
    return r.stdout


def main():
    state = json.loads(task.JOURNAL.read_text(encoding='utf-8'))
    if state['phase'] == 'game_landed':
        print('Already landed; inspect the journal.')
        return
    assert state['phase'] == 'prepared'
    assert not task.git(GAME, 'status', '--porcelain').strip()
    before = art.snapshot(ROOT)
    task.write(REPORT / 'game_runtime_before.json', before)
    native('rebase', ['git', '-c', 'safe.directory=' + str(GAME), '-C', str(GAME), 'rebase', 'main'])
    native('doc_budget', ['python', 'tools/doc_budget.py'], GAME)
    native('land', ['python', 'tools/wt.py', 'land', '--site', '534', '-m',
                   'PD 승인 #534 R3 물약4 원화·크기 규격 채택; 실제 반입은 #548, runtime 변경 없음'])
    assert art.snapshot(ROOT) == before
    native('preserve_user', ['python', '._tmp/preserve_main_changes451.py', '--check'])
    state.update(phase='game_landed', game_landed_commit=task.git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
                 game_runtime_files_unchanged=len(before))
    task.write(task.JOURNAL, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
