from pathlib import Path
import hashlib, json, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
out=base/'analysis/focused_pair'
assert not out.exists(), 'preserve previous comparison directory'
out.mkdir(parents=True)
left=wt/'tmp/e2e_raw/20261002T1351502942221_26024'
right=wt/'tmp/e2e_raw/20261002T1415238741716_62096'
git=['git','-c','safe.directory='+wt.as_posix(),'-C',str(wt)]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(label,args):
    start=time.time()
    result=subprocess.run(args,cwd=wt,capture_output=True)
    (out/(label+'.stdout.raw.log')).write_bytes(result.stdout)
    (out/(label+'.stderr.raw.log')).write_bytes(result.stderr)
    (out/(label+'.metadata.json')).write_text(json.dumps({'argv':args,'exit_code':result.returncode,'elapsed_sec':time.time()-start},indent=2),encoding='utf-8')
    return result
head=run('head_before',git+['rev-parse','HEAD'])
assert head.returncode==0 and head.stdout.decode().strip()=='f1bf88f05a8eb48dd7d12510011245f3f6631e76'
# Archive the completed phases' original bytes without changing their paths or metadata.
inputs=[]
for label,root in [('focused_1',left),('focused_2',right)]:
    phase=root/'phase_1_solo'
    dest=out/'phase_evidence'/label
    dest.mkdir(parents=True)
    for name in ['phase.json','godot.raw.log','console.merged.raw.log']:
        source=phase/name
        (dest/name).write_bytes(source.read_bytes())
        inputs.append({'source':str(source),'copy':str(dest/name),'sha256':sha(source)})
(out/'input_manifest.json').write_text(json.dumps({'candidate':head.stdout.decode().strip(),'script_sha256':sha(wt/'tools/combat_trace_compare.py'),'inputs':inputs,'phase_archive_roots':[str(left),str(right)],'scope':'read-only focused pair; no game launches or candidate changes'},indent=2),encoding='utf-8')
args=[sys.executable,'tools/combat_trace_compare.py',str(left),str(right),'--out',str(out/'comparison.json')]
result=run('compare',args)
print(result.stdout.decode('utf-8','replace')+result.stderr.decode('utf-8','replace'))
after=run('head_after',git+['rev-parse','HEAD'])
assert after.stdout==head.stdout
sys.exit(result.returncode)
