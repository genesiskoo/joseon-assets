from pathlib import Path
import hashlib,json,os,subprocess,sys,time

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
out=Path('C:/workspace/joseon/._tmp/trace_558_20261002/worker/docs_record_01')
before=json.loads((out/'before.json').read_text(encoding='utf-8'))
ignore=out/'empty.ignore';assert not ignore.exists();ignore.write_bytes(b'')
git=['git','-c','safe.directory='+wt.as_posix(),'-c','core.excludesFile='+ignore.as_posix(),'-C',str(wt)]
def run(label,argv):
    start=time.time();env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
    r=subprocess.run(argv,cwd=wt,capture_output=True,env=env)
    for suffix,data in [('stdout.raw.log',r.stdout),('stderr.raw.log',r.stderr)]:
        p=out/(label+'.'+suffix);assert not p.exists();p.write_bytes(data)
    p=out/(label+'.metadata.json');assert not p.exists()
    p.write_text(json.dumps({'argv':argv,'returncode':r.returncode,'elapsed_sec':time.time()-start},indent=2)+'\n',encoding='utf-8')
    if r.returncode: print(r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace'))
    assert r.returncode==0,'see saved raw logs for '+label
    return r.stdout
head=run('write_head_check',git+['rev-parse','HEAD']).decode().strip()
assert head==before['head']
assert not run('write_status_check',git+['status','--porcelain=v1'])
target=wt/'docs/design/combat_trace_558_log.md'
assert not target.exists(),'do not overwrite another worker file'
spec=wt/'docs/design/combat_trace_558.md'
original=spec.read_bytes()
eol=b'\r\n' if b'\r\n' in original else b'\n'
lines=original.splitlines(keepends=True)
reference='실측·검증·착륙 상태는 [combat_trace_558_log.md](combat_trace_558_log.md)에 별도로 기록한다.'.encode('utf-8')+eol
assert len(lines)>3 and lines[0].startswith(b'# #558')
assert not any(b'combat_trace_558_log.md' in line for line in lines)
lines.insert(3,reference)
target.write_bytes((out/'combat_trace_558_log.draft.md').read_bytes())
spec.write_bytes(b''.join(lines))
(out/'spec_before.bytes').write_bytes(original)
run('doc_budget',['python','tools/doc_budget.py'])
run('docs_diff_check',git+['diff','--check'])
run('spec_diff',git+['diff','--','docs/design/combat_trace_558.md'])
run('write_status_after',git+['status','--porcelain=v1'])
record={'head':head,'changed_files':['docs/design/combat_trace_558.md','docs/design/combat_trace_558_log.md'],
        'spec_added_reference_lines':1,'log_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'game_execution_count':0,'test_execution_count':0,'scope':'two approved docs only; no staging/commit/main/board/runtime mutations'}
(out/'written.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
