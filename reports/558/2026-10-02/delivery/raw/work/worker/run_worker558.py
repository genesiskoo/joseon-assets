from pathlib import Path
import subprocess, sys, json, time, shutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

WT=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
OUT=Path('C:/workspace/joseon/._tmp/trace_558_20261002/worker')
COMMANDS={
 'import':['godot','--path',str(WT),'--headless','--editor','--import','--quit'],
 'trace_unit':['godot','--path',str(WT),'--headless','-s','tests/test_combat_trace.gd'],
 'balance_unit':['godot','--path',str(WT),'--headless','-s','tests/test_balance_rng.gd'],
 'balance_verbose':['godot','--path',str(WT),'--headless','--verbose','-s','tests/test_balance_rng.gd'],
 'replay_self':['python','tools/balance_replay.py','--selftest'],
 'trace_self':['python','tools/combat_trace_compare.py','--selftest'],
 'ps_self':['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File','tools/test.ps1','-SelfTestTimeout'],
 'unit':['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File','tools/test.ps1','-Unit'],
 'budget':['python','tools/doc_budget.py'],
 'diff':['git','-c','safe.directory='+str(WT).replace('\\','/'),'diff','--check'],
}
label=sys.argv[1]
cmd=COMMANDS[label]
cmd[0]=shutil.which(cmd[0]) or cmd[0]
index=1
while (OUT/f'{label}_{index:02d}.stdout.raw.log').exists(): index+=1
prefix=OUT/f'{label}_{index:02d}'
start=time.time()
result=subprocess.run(cmd,cwd=WT,capture_output=True,timeout=3600)
Path(str(prefix)+'.stdout.raw.log').write_bytes(result.stdout)
Path(str(prefix)+'.stderr.raw.log').write_bytes(result.stderr)
Path(str(prefix)+'.metadata.json').write_text(json.dumps({'argv':cmd,'exit_code':result.returncode,'elapsed_sec':time.time()-start},indent=2),encoding='utf-8')
print(json.dumps({'label':label,'exit_code':result.returncode,'elapsed_sec':round(time.time()-start,1),'prefix':str(prefix)},ensure_ascii=False))
output=(result.stdout+result.stderr).decode('utf-8','replace')
invalid=any(x in output for x in ['SCRIPT ERROR:', 'Parse Error:', 'Compile Error:']) and label!='ps_self'
invalid=invalid or (label in ('trace_unit','balance_unit','balance_verbose','import') and 'ERROR:' in output)
if result.returncode or invalid: print(output)
else: print('\n'.join(output.splitlines()[-8:]))
sys.exit(result.returncode or (1 if invalid else 0))
