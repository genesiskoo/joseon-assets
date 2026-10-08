from pathlib import Path
from PIL import Image
import hashlib, json, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')
mode = sys.argv[1]
assert mode in ('before','after')
game = Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
assets = Path('C:/workspace/joseon/._tmp/assets_87')
user = Path('C:/Users/FORYOUCOM/AppData/Roaming/Godot/app_userdata/Joseon Hunters/wt/codex-87-ui-wood-skin/e2e')
report = assets/'reports/453/integration_2026-09-27'
gallery = game/'docs/art/453_d1_material_intake'
gallery.mkdir(parents=True,exist_ok=True)
exe = 'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
args = [exe,'--path',str(game),'--windowed','--resolution','1280x720','--','--e2e=icon_intake','--e2e-shots','--icon-intake-material-only']
if mode == 'before':
    args.append('--icon-intake-before')
info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = 0
stamp = time.strftime('%H%M%S')
out = report/f'453_{mode}_{stamp}.log'
err = report/f'453_{mode}_{stamp}_errors.log'
started = time.time()
with out.open('wb') as stdout, err.open('wb') as stderr:
    run = subprocess.run(args,cwd=game,stdout=stdout,stderr=stderr,startupinfo=info,timeout=150)
log = out.read_text(encoding='utf-8-sig',errors='replace')
errors = err.read_text(encoding='utf-8-sig',errors='replace')
print(log,end='')
if errors:
    print(errors,end='')
assert run.returncode == 0 and 'E2E SUMMARY: 1/1 PASS' in log and not errors.strip(), 'Capture failed; raw logs preserved above.'
records=[]
for index,state in enumerate(('material_inventory','material_vendor','material_drop_recovered'),1):
    source = user / f'icon_intake_{index:02d}_{state}.png'
    assert source.exists() and source.stat().st_mtime >= started, f'Not fresh exact-index: {source}'
    raw = report/f'{state}_{mode}.png'
    raw.write_bytes(source.read_bytes())
    im = Image.open(raw).convert('RGB')
    assert im.size == (1280,720)
    jpg=gallery/f'{state}_{mode}.jpg'
    im.save(jpg,quality=85,optimize=True)
    assert jpg.stat().st_size <= 300_000
    (report/jpg.name).write_bytes(jpg.read_bytes())
    records.append({'state':state,'source':str(source),'mtime':source.stat().st_mtime,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'size':list(im.size),'jpg_bytes':jpg.stat().st_size})
(report/f'captures_{mode}.json').write_text(json.dumps({'started':started,'exit_code':run.returncode,'command':args,'game_head':subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'],text=True).strip(),'stdout':out.name,'stderr':err.name,'captures':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {mode}: real material input +3 fresh exact-index frames; JPG width1280/<=300KB.')
