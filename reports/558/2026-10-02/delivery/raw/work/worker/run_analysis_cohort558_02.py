from pathlib import Path
import json, subprocess, sys, time

base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
args=[sys.executable,str(base/'worker/analyze_cohort558_01.py')]
start=time.time()
r=subprocess.run(args,capture_output=True)
for suffix,data in [('stdout.raw.log',r.stdout),('stderr.raw.log',r.stderr)]:
    path=base/'worker'/('cohort_analysis_02.'+suffix)
    assert not path.exists()
    path.write_bytes(data)
meta=base/'worker/cohort_analysis_02.metadata.json'
assert not meta.exists()
meta.write_text(json.dumps({'argv':args,'returncode':r.returncode,'elapsed_seconds':time.time()-start},indent=2)+'\n',encoding='utf-8')
if r.returncode:
    print(r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace'))
else:
    print(json.dumps({'returncode':r.returncode,'stdout_bytes':len(r.stdout),'stderr_bytes':len(r.stderr),'analysis':str(base/'analysis/cohort_first_divergence_01.json')}))
sys.exit(r.returncode)
