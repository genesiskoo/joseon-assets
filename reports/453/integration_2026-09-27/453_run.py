from pathlib import Path
import hashlib, json, os, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')
game=Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
report=Path('C:/workspace/joseon/._tmp/assets_87/reports/453/integration_2026-09-27')
mode=sys.argv[1]
exe='C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
env=dict(os.environ,GODOT_BIN=exe,PYTHONIOENCODING='utf-8')
if mode=='import':
    cmd=[exe,'--headless','--path',str(game),'--import']
elif mode=='unit':
    cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(game/'tools/test.ps1'),'-Unit']
elif mode=='e2e':
    cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(game/'tools/test.ps1'),'-E2e','-Scenario','icon_intake,item_ui,ui_tooltips,ui_docks,ui_windows,hover_target,vendor_quest,vendor_prices,shaman_heal,pickup_equip,loot_drop']
elif mode=='gate':
    cmd=[sys.executable,'C:/workspace/joseon/tmp/453_gate.py']
elif mode=='land':
    cmd=[sys.executable,str(game/'tools/wt.py'),'land','--no-test','-m','승인 재료6종 PNG·ItemDef.icon 반입, 실제 입력/전후3쌍·단위53/관련E2E11/빠른검사 PASS']
else:
    raise ValueError(mode)
info=subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow=0
started=time.time()
path=report/f'453_{mode}_{time.strftime("%H%M%S")}.log'
with path.open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=game,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,startupinfo=info)
    for raw in iter(proc.stdout.readline,b''):
        log.write(raw)
        log.flush()
        print(raw.decode('utf-8-sig',errors='replace'),end='',flush=True)
    rc=proc.wait()
(report/f'run_{mode}.json').write_text(json.dumps({'mode':mode,'command':cmd,'cwd':str(game),'started':started,
    'elapsed':time.time()-started,'exit_code':rc,'raw_log':path.name,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'RUN_END mode={mode} exit={rc} seconds={time.time()-started:.1f} raw={path}',flush=True)
sys.exit(rc)
