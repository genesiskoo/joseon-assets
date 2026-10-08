import argparse
import subprocess
from pathlib import Path

EXE = Path('C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe')
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/534-potion-grade-art/joseon')
HERE = Path('C:/workspace/joseon/._tmp/assets_534/workbench/production/item_icons_534/rank_v3_2026-10-02')
REPORT = Path('C:/workspace/joseon/._tmp/assets_534/reports/534/2026-10-02_comfy_rank_v3')
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = subprocess.SW_HIDE


def run(label, arguments):
    if (REPORT / f'{label}.stdout.raw.log').exists():
        raise SystemExit('Preserved raw log exists; use a new run label instead of overwriting it: ' + label)
    result = subprocess.run([str(EXE), '--path', str(GAME), *arguments], cwd=GAME,
                            startupinfo=startup, capture_output=True, timeout=180)
    (REPORT / f'{label}.stdout.raw.log').write_bytes(result.stdout)
    (REPORT / f'{label}.stderr.raw.log').write_bytes(result.stderr)
    output = (result.stdout + result.stderr).decode('utf-8', errors='replace')
    if result.returncode or 'SCRIPT ERROR' in output or 'ERROR:' in output:
        print(output, flush=True)
        raise SystemExit(result.returncode or 1)
    if not label.startswith('import') and f'GODOT_534_PASS mode={label} items=6 candidate4/scale_proposal' not in output:
        print(output, flush=True)
        raise SystemExit('Expected actual UiSkin render proof is missing.')
    print(f'PASS {label}; engine/script errors=0; raw stdout/stderr retained.', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-import', action='store_true')
    parser.add_argument('--import-label', default='import')
    args = parser.parse_args()
    if not args.skip_import:
        run(args.import_label, ['--headless', '--import'])
    for mode in ('overview', 'actual', 'belt_stress', 'black', 'grayscale'):
        run(mode, ['-s', str(HERE / 'qa_godot.gd'), '--', '--root=' + str(HERE), '--out=' + str(HERE / 'qa'), '--mode=' + mode])


if __name__ == '__main__':
    main()
