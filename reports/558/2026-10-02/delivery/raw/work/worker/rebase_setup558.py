from pathlib import Path
import hashlib, json, os, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
WT = Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
OUT = Path(__file__).parent
EXPECTED = '4b4f0bcfd91da40797d5affe403362e492fd597f'
MAIN_EXPECTED = '705a28d3c2923185d30a2beb4600f2321f687303'
index = 1
while (OUT / f'rebase_setup_{index:02d}.manifest.json').exists():
    index += 1
PREFIX = OUT / f'rebase_setup_{index:02d}'
manifest = {'scope': 'own #558 worktree rebase/setup only; balance/full E2E runs=0', 'steps': []}

def save():
    Path(str(PREFIX) + '.manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

def run(label, args, timeout=1800, allowed=(0,)):
    logbase = Path(str(PREFIX) + '.' + label)
    assert not Path(str(logbase) + '.stdout.raw.log').exists()
    started = time.time()
    result = subprocess.run(args, cwd=WT, capture_output=True, timeout=timeout)
    Path(str(logbase) + '.stdout.raw.log').write_bytes(result.stdout)
    Path(str(logbase) + '.stderr.raw.log').write_bytes(result.stderr)
    step = {'label': label, 'argv': args, 'cwd': str(WT), 'exit_code': result.returncode, 'elapsed_sec': time.time() - started,
            'stdout': str(logbase) + '.stdout.raw.log', 'stderr': str(logbase) + '.stderr.raw.log'}
    manifest['steps'].append(step)
    save()
    print(json.dumps(step, ensure_ascii=False), flush=True)
    if result.returncode not in allowed:
        print(result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace'), flush=True)
        raise RuntimeError(label + ' failed; raw evidence retained')
    return result.stdout

def git(label, *args, allowed=(0,)):
    return run(label, ['git', '-c', 'safe.directory=' + WT.as_posix(), '-C', str(WT), *args], allowed=allowed)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def snapshot(label, head, files):
    out = {'head': head, 'files': {}}
    for i, name in enumerate(files):
        blob = git(f'{label}_blob_{i + 1:02d}', 'show', head + ':' + name)
        disk = (WT / name).read_bytes()
        out['files'][name] = {'git_blob_sha256': digest(blob), 'disk_sha256': digest(disk), 'disk_lf_sha256': digest(disk.replace(b'\r\n', b'\n'))}
    out['aggregate_git_sha256'] = digest(''.join(name + '\0' + out['files'][name]['git_blob_sha256'] + '\n' for name in sorted(files)).encode('utf-8'))
    out['aggregate_disk_sha256'] = digest(''.join(name + '\0' + out['files'][name]['disk_sha256'] + '\n' for name in sorted(files)).encode('utf-8'))
    return out

try:
    status = git('pre_status', 'status', '--porcelain=v1').decode('utf-8').strip()
    head = git('pre_head', 'rev-parse', 'HEAD').decode('ascii').strip()
    target = git('pre_main', 'rev-parse', 'main').decode('ascii').strip()
    branch = git('pre_branch', 'branch', '--show-current').decode('ascii').strip()
    assert not status and head == EXPECTED and branch == 'codex/558-combat-clock-trace', 'own worktree identity/clean HEAD differs'
    assert target == MAIN_EXPECTED, 'main advanced; coordinate exact declared candidate first'
    files = git('owned_files', 'diff-tree', '--no-commit-id', '--name-only', '-r', head).decode('utf-8').splitlines()
    assert len(files) == 17
    manifest['before'] = snapshot('before', head, files)
    manifest['target_main'] = target
    save()
    git('rebase', 'rebase', target)
    rebased = git('rebased_head', 'rev-parse', 'HEAD').decode('ascii').strip()
    manifest['rebased_head'] = rebased
    save()
    setup = run('setup', [sys.executable, 'tools/wt.py', 'setup', '--card', '558'])
    print(setup.decode('utf-8', 'replace'), flush=True)
    manifest['after'] = snapshot('after', rebased, files)
    manifest['changed_git_sources'] = [name for name in files if manifest['before']['files'][name]['git_blob_sha256'] != manifest['after']['files'][name]['git_blob_sha256']]
    manifest['changed_disk_only'] = [name for name in files if manifest['before']['files'][name]['disk_sha256'] != manifest['after']['files'][name]['disk_sha256'] and name not in manifest['changed_git_sources']]
    manifest['final_status'] = git('final_status', 'status', '--porcelain=v1').decode('utf-8').strip()
    git('final_head', 'log', '-1', '--format=fuller')
    git('main_ancestor', 'merge-base', '--is-ancestor', target, rebased)
    git('diff_check', 'diff', '--check')
    assert not manifest['final_status'], 'setup caused tracked changes; inspect own files before cohort'
    assert not any(x in setup.decode('utf-8', 'replace') for x in ['SCRIPT ERROR:', 'Parse Error:', 'Compile Error:']), 'setup compilation diagnostic'
    manifest['status'] = 'PASS clean rebase/setup; no balance/full E2E'
    save()
    print(json.dumps({'status': manifest['status'], 'head': rebased, 'changed_git_sources': manifest['changed_git_sources'],
                      'changed_disk_only': manifest['changed_disk_only'], 'source_sha256': manifest['after']['aggregate_git_sha256'], 'manifest': str(PREFIX) + '.manifest.json'}, ensure_ascii=False), flush=True)
except Exception as exc:
    manifest['status'] = 'STOP'
    manifest['error'] = str(exc)
    save()
    raise
