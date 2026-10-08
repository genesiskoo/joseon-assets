from pathlib import Path
from PIL import Image
import hashlib, json, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')

mode = sys.argv[1]
assert mode in ('before', 'after')
game = Path(r'C:/Users/FORYOUCOM/.codex/worktrees/293-monster-elite-ui/joseon')
assets = Path(r'C:/Users/FORYOUCOM/.codex/worktrees/393-ui-icon-redesign/joseon-assets')
root = Path(r'C:/workspace/joseon')
user = Path(r'C:/Users/FORYOUCOM/AppData/Roaming/Godot/app_userdata/Joseon Hunters/wt/codex-293-monster-elite-ui/e2e')
report = assets / 'reports/450/integration_2026-09-27'
gallery = game / 'docs/art/450_d1_t2_intake'
report.mkdir(parents=True, exist_ok=True)
gallery.mkdir(parents=True, exist_ok=True)
exe = r'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
args = [exe, '--path', str(game), '--windowed', '--resolution', '1280x720', '--',
    '--e2e=icon_intake', '--e2e-shots', '--icon-intake-t2-only']
if mode == 'before':
    args.append('--icon-intake-before')
stdout = root / f'tmp/450_{mode}.log'
stderr = root / f'tmp/450_{mode}_errors.log'
info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = 0
started = time.time()
with stdout.open('wb') as out, stderr.open('wb') as err:
    run = subprocess.run(args, cwd=game, stdout=out, stderr=err, startupinfo=info, timeout=120)
log = stdout.read_text(encoding='utf-8-sig', errors='replace')
errors = stderr.read_text(encoding='utf-8-sig', errors='replace')
print(log, end='')
if errors:
    print(errors, end='')
assert run.returncode == 0 and 'E2E SUMMARY: 1/1 PASS' in log and not errors.strip(), 'Capture/real input verification failed; raw logs printed.'
records = []
for index, state in enumerate(('t2_inventory', 't2_held', 't2_vendor_tooltip'), 1):
    source = user / f'icon_intake_{index:02d}_{state}.png'
    assert source.exists() and source.stat().st_mtime >= started, f'Not a fresh exact-index capture: {source}'
    raw = report / f'{state}_{mode}.png'
    raw.write_bytes(source.read_bytes())
    im = Image.open(raw).convert('RGB')
    assert im.size == (1280, 720)
    jpg = gallery / f'{state}_{mode}.jpg'
    im.save(jpg, quality=85, optimize=True)
    assert jpg.stat().st_size <= 300_000
    (report / jpg.name).write_bytes(jpg.read_bytes())
    records.append({'state':state,'source':str(source),'mtime':source.stat().st_mtime,
        'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'size':list(im.size),'jpg_bytes':jpg.stat().st_size})
for p in (stdout, stderr):
    (report / p.name).write_bytes(p.read_bytes())
(report / f'captures_{mode}.json').write_text(json.dumps({'started':started,'exit_code':run.returncode,
    'game_head':subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'],text=True).strip(),
    'captures':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {mode}: actual input + 3 fresh exact-index frames; gallery JPG width1280/<=300KB.')
