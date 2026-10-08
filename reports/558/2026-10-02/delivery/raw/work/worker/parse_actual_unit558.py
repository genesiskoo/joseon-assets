from pathlib import Path
import subprocess, json, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
out=Path(__file__).parent
raw=(out/'balance_verbose_02.stdout.raw.log').read_text(encoding='utf-8')
rows=[json.loads(m.group(1)) for m in re.finditer(r'BALANCE_TRACE_FILE (\{[^\r\n]+\})',raw)]
assert len(rows)==1 and rows[0]['saved']
prefix=out/'actual_unit_trace_parse_01'
argv=[sys.executable,'tools/combat_trace_compare.py',rows[0]['path'],rows[0]['path'],'--out',str(prefix)+'.comparison.json']
assert not Path(str(prefix)+'.stdout.raw.log').exists()
result=subprocess.run(argv,cwd=wt,capture_output=True)
Path(str(prefix)+'.stdout.raw.log').write_bytes(result.stdout)
Path(str(prefix)+'.stderr.raw.log').write_bytes(result.stderr)
Path(str(prefix)+'.metadata.json').write_text(json.dumps({'argv':argv,'exit_code':result.returncode,'scope':'unit output parser compatibility only; not actual default cohort'},indent=2),encoding='utf-8')
print(result.stdout.decode('utf-8','replace')+result.stderr.decode('utf-8','replace'))
sys.exit(result.returncode)
