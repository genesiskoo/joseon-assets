from pathlib import Path
import json,subprocess,sys,time
base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
argv=[sys.executable,str(base/'worker/verify_analysis_evidence558_01.py')]
start=time.time();r=subprocess.run(argv,capture_output=True)
for suffix,data in [('stdout.raw.log',r.stdout),('stderr.raw.log',r.stderr)]:
    path=base/'worker'/('evidence_integrity_01.'+suffix);assert not path.exists();path.write_bytes(data)
path=base/'worker/evidence_integrity_01.metadata.json';assert not path.exists()
path.write_text(json.dumps({'argv':argv,'returncode':r.returncode,'elapsed_seconds':time.time()-start},indent=2)+'\n',encoding='utf-8')
print(r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace'))
sys.exit(r.returncode)
