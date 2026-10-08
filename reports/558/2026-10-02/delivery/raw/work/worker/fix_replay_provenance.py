from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

WT = Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
EVIDENCE = Path('C:/workspace/joseon/._tmp/trace_558_20261002/worker')
BASE = 'f1bf88f05a8eb48dd7d12510011245f3f6631e76'
FILES = ('tools/balance_replay.py', 'docs/design/combat_trace_558.md')


def git(*args):
    return subprocess.run(['git', '-c', f'safe.directory={WT.as_posix()}', '-C', str(WT), *args], capture_output=True, check=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise RuntimeError('expected exactly one unchanged patch anchor')
    return text.replace(before, after, 1)


def patch(out):
    if git('rev-parse', 'HEAD').stdout.decode().strip() != BASE or git('status', '--porcelain').stdout:
        raise RuntimeError('candidate HEAD/clean precondition changed; do not overwrite other edits')
    originals, blob_shas, endings = {}, {}, {}
    for name in FILES:
        blob = git('show', f'HEAD:{name}').stdout
        original = (WT / name).read_bytes()
        if original.replace(b'\r\n', b'\n') != blob.replace(b'\r\n', b'\n'):
            raise RuntimeError(f'working bytes differ: {name}')
        crlf, lf = original.count(b'\r\n'), original.count(b'\n')
        if crlf and crlf != lf:
            raise RuntimeError(f'mixed newline bytes: {name}')
        endings[name] = 'CRLF' if crlf else 'LF'
        blob_shas[name] = sha(blob)
        originals[name] = original
        dest = out / 'originals' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(original)
        dest.with_suffix(dest.suffix + '.git_blob').write_bytes(blob)

    source = originals[FILES[0]].replace(b'\r\n', b'\n').decode('utf-8')
    source = replace_once(source,
        '            if name == "environment":\n                a.pop("pid"); b.pop("pid")\n            if a != b:\n',
        '            if name == "environment":\n                a.pop("pid"); b.pop("pid")\n'
        '            elif name == "launch":\n'
        '                # Per-run provenance stays in raw/report, outside experimental equality.\n'
        '                for field in ("launcher_pid", "launched_utc"):\n'
        '                    a.pop(field, None); b.pop(field, None)\n'
        '            if a != b:\n')

    tests = '''        launch_left = dict(launch, launcher_pid=2011, launched_utc="2026-10-02T10:00:00Z")
        launch_right = dict(launch, launcher_pid=2012, launched_utc="2026-10-02T10:01:00Z")
        left_raw = good.replace(encoded(launch).encode(), encoded(launch_left).encode(), 1)
        right_raw = good.replace(encoded(launch).encode(), encoded(launch_right).encode(), 1)
        first, second = fixture(1, left_raw), fixture(2, right_raw)
        raw_before = {p: p.read_bytes() for p in directory.glob("*.raw.log")}
        provenance_report = compare_manifests([first, second])
        check(provenance_report["pass"], "different launcher PID/UTC with identical conditions accepted")
        check([r["launch"] for r in provenance_report.get("runs", [])] == [launch_left, launch_right],
              "exact launcher provenance retained in both report inputs")
        check(all(p.read_bytes() == body for p, body in raw_before.items()), "comparison preserves original raw bytes")
        strict_conditions = {
            "actual argv": right_raw.replace(b'"C:/fixture"', b'"C:/other_fixture"', 1),
            "actual executable": right_raw.replace(b'"exe":"godot"', b'"exe":"other_godot"', 1),
            "fixed FPS": right_raw.replace(b'"fixed_fps":60', b'"fixed_fps":0', 1),
            "engine version": right_raw.replace(b'"patch":2', b'"patch":3', 1),
            "engine hash": right_raw.replace(b'"hash":"ed1daf0bf"', b'"hash":"different_hash"', 1),
            "environment user directory": right_raw.replace(b'"user_dir":"C:/fixture/user"', b'"user_dir":"C:/other/user"', 1),
            "original seed": right_raw.replace(b"seed=23271941", b"seed=23271942"),
            "starting stats": right_raw.replace(b'"hp0":"130.00000000000000000"', b'"hp0":"131.00000000000000000"', 1)
                                      .replace(b'"max_hp":"130.00000000000000000"', b'"max_hp":"131.00000000000000000"', 1),
            "potion criterion": right_raw.replace(b'"potions":3', b'"potions":4', 1),
            "time criterion": right_raw.replace(b'"sec":"20.00000000000000000"', b'"sec":"46.00000000000000000"', 1),
            "other launch field": right_raw.replace(encoded(launch_right).encode(), encoded(dict(launch_right, other_provenance="different")).encode(), 1),
        }
        for label, changed in strict_conditions.items():
            second = fixture(2, changed)
            check(not compare_manifests([first, second])["pass"], "launcher provenance exclusion still rejects " + label)
        second = fixture(2, right_raw)
        second_manifest = json.loads(second.read_text(encoding="utf-8"))
        second_manifest["command"].extend(["-Slots", "2"])
        write_json(second, second_manifest)
        check(not compare_manifests([first, second])["pass"], "actual test.ps1 invocation remains strict")
        first = fixture(1)
'''
    source = replace_once(source,
        '        check(compare_manifests([first, second])["pass"], "two independent complete manifests accepted")\n',
        '        check(compare_manifests([first, second])["pass"], "two independent complete manifests accepted")\n' + tests)

    doc = originals[FILES[1]].replace(b'\r\n', b'\n').decode('utf-8')
    anchor = '단위 = signed64 extrema/2^53 초과/음수 JSON 문자열'
    sentence = '기존 고정60 진단 `balance_replay.py`는 실행별 `launch.launcher_pid`·`launch.launched_utc` 두 값만 실험 동일성 비교에서 제외하고 입력 원문·보고서에는 그대로 보존한다. 실제 argv·fixed_fps·엔진·환경·시드·스탯·기준은 계속 엄격히 검사한다.\n\n'
    doc = replace_once(doc, anchor, sentence + anchor)
    for name, text in zip(FILES, (source, doc)):
        data = text.encode('utf-8')
        if endings[name] == 'CRLF':
            data = data.replace(b'\n', b'\r\n')
        (WT / name).write_bytes(data)
    metadata = {'baseline_head': BASE, 'scope': list(FILES), 'before': {k: sha(v) for k, v in originals.items()},
                'before_git_blob': blob_shas, 'preserved_line_endings': endings,
                'after': {k: sha((WT / k).read_bytes()) for k in FILES}, 'game_execution': 0, 'cohort_head_preserved': BASE}
    (out / 'PATCH.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'patch': str(out), **metadata}))


def run_selftest(out):
    command = [sys.executable, '-B', 'tools/balance_replay.py', '--selftest']
    result = subprocess.run(command, cwd=WT, capture_output=True)
    (out / 'balance_replay.stdout.raw.log').write_bytes(result.stdout)
    (out / 'balance_replay.stderr.raw.log').write_bytes(result.stderr)
    metadata = {'head': git('rev-parse', 'HEAD').stdout.decode().strip(), 'argv': command, 'exit_code': result.returncode,
                'stdout_sha256': sha(result.stdout), 'stderr_sha256': sha(result.stderr), 'stderr_bytes': len(result.stderr),
                'scope': 'pure Python builtin selftest only; Godot/cohort executions=0'}
    (out / 'SELFTEST.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'raw': str(out), **metadata}))
    print(result.stdout.decode('utf-8', errors='backslashreplace'), end='')
    if result.stderr:
        print(result.stderr.decode('utf-8', errors='backslashreplace'), end='')
    return result.returncode


def commit(out):
    steps = []

    def run(*args):
        command = ['git', '-c', f'safe.directory={WT.as_posix()}', '-C', str(WT), *args]
        result = subprocess.run(command, capture_output=True)
        stem = f'{len(steps) + 1:02d}_{args[0]}'
        (out / (stem + '.stdout.raw.log')).write_bytes(result.stdout)
        (out / (stem + '.stderr.raw.log')).write_bytes(result.stderr)
        steps.append({'argv': command, 'exit_code': result.returncode,
                      'stdout_sha256': sha(result.stdout), 'stderr_sha256': sha(result.stderr)})
        (out / 'GIT_STEPS.json').write_text(json.dumps(steps, indent=2) + '\n', encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'git failed; original output preserved in {out / stem}')
        return result.stdout.decode('utf-8').strip()

    if run('rev-parse', 'HEAD') != BASE:
        raise RuntimeError('HEAD changed while reviewing; stop rather than revert others')
    if run('diff', '--cached', '--name-only'):
        raise RuntimeError('pre-existing staged changes; do not commit another worker scope')
    if set(run('diff', '--name-only').splitlines()) != set(FILES):
        raise RuntimeError('working diff differs from exactly two authorized files')
    run('diff', '--check')
    run('add', '--', *FILES)
    if set(run('diff', '--cached', '--name-only').splitlines()) != set(FILES):
        raise RuntimeError('staged scope differs from exactly two authorized files')
    run('diff', '--cached', '--check')
    run('commit', '-m', 'fix(#558): preserve launch provenance outside replay equality', '-m', 'Agent: Codex (GPT-6)')
    head = run('rev-parse', 'HEAD')
    status = run('status', '--porcelain')
    message = run('show', '-s', '--format=%B', 'HEAD')
    actual_files = run('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines()
    if status or set(actual_files) != set(FILES) or 'Agent: Codex (GPT-6)' not in message:
        raise RuntimeError('post-commit scope/clean/footer validation differs')
    metadata = {'head': head, 'baseline_head': BASE, 'clean': True, 'files': actual_files, 'message': message,
                'cohort_head_preserved': BASE, 'game_or_cohort_executions': 0}
    (out / 'COMMIT.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'raw': str(out), **metadata}))


if __name__ == '__main__':
    mode = sys.argv[1]
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    out = EVIDENCE / f'{mode}_{stamp}_{os.getpid()}'
    out.mkdir(parents=True, exist_ok=False)
    try:
        if mode == 'patch':
            patch(out)
        elif mode == 'selftest':
            raise SystemExit(run_selftest(out))
        elif mode == 'commit':
            commit(out)
        else:
            raise RuntimeError('unsupported mode')
    except Exception:
        (out / 'failure.stderr.raw.log').write_bytes(traceback.format_exc().encode('utf-8'))
        raise
