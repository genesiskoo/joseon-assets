from pathlib import Path
import json,subprocess,sys,time
base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
argv=[sys.executable,str(base/'worker/analyze_first_impact558_01.py')]
start=time.time();r=subprocess.run(argv,capture_output=True)
for suffix,data in [('stdout.raw.log',r.stdout),('stderr.raw.log',r.stderr)]:
    path=base/'worker'/('first_impact_analysis_01.'+suffix);assert not path.exists();path.write_bytes(data)
path=base/'worker/first_impact_analysis_01.metadata.json';assert not path.exists()
path.write_text(json.dumps({'argv':argv,'returncode':r.returncode,'elapsed_seconds':time.time()-start},indent=2)+'\n',encoding='utf-8')
if r.returncode:print(r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace'))
else:print(json.dumps({'returncode':r.returncode,'stdout_bytes':len(r.stdout),'stderr_bytes':len(r.stderr),'report':str(base/'analysis/cohort_preparation_and_first_impact_01.json')}))
sys.exit(r.returncode)
