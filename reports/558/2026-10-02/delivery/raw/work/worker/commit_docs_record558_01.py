from pathlib import Path
import hashlib,json,os,subprocess,sys,time

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
out=Path('C:/workspace/joseon/._tmp/trace_558_20261002/worker/docs_record_01')
before=json.loads((out/'before.json').read_text(encoding='utf-8'))
written=json.loads((out/'written.json').read_text(encoding='utf-8'))
git=['git','-c','safe.directory='+wt.as_posix(),'-c','core.excludesFile='+(out/'empty.ignore').as_posix(),'-C',str(wt)]
def run(label,args):
    start=time.time();env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
    r=subprocess.run(git+args,cwd=wt,capture_output=True,env=env)
    for suffix,data in [('stdout.raw.log',r.stdout),('stderr.raw.log',r.stderr)]:
        p=out/(label+'.'+suffix);assert not p.exists();p.write_bytes(data)
    p=out/(label+'.metadata.json');assert not p.exists()
    p.write_text(json.dumps({'argv':git+args,'returncode':r.returncode,'elapsed_sec':time.time()-start},indent=2)+'\n',encoding='utf-8')
    if r.returncode:print(r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace'))
    assert r.returncode==0,'see saved raw logs for '+label
    return r.stdout
assert run('commit_head_check',['rev-parse','HEAD']).decode().strip()==before['head']
expected=set(written['changed_files'])
status=run('commit_status_check',['status','--porcelain=v1','-z']).decode('utf-8').split('\0')
assert {row[3:] for row in status if row}==expected
assert hashlib.sha256((wt/'docs/design/combat_trace_558_log.md').read_bytes()).hexdigest()==written['log_sha256']
run('stage_docs',['add','--','docs/design/combat_trace_558.md','docs/design/combat_trace_558_log.md'])
staged=run('staged_names',['diff','--cached','--name-only']).decode('utf-8').splitlines()
assert set(staged)==expected
numstat=run('staged_numstat',['diff','--cached','--numstat']).decode('utf-8').splitlines()
assert '1\t0\tdocs/design/combat_trace_558.md' in numstat
run('staged_check',['diff','--cached','--check'])
run('staged_diff',['diff','--cached','--','docs/design/combat_trace_558.md','docs/design/combat_trace_558_log.md'])
message=out/'commit_message.txt';assert not message.exists()
message.write_text('docs(#558): record first default-clock trace cohort\n\nPreserve all six declared attempts, raw provenance, and observed divergence boundaries. Keep runtime policy and #536 completion separate.\n\nAgent: Codex (GPT-6)\n',encoding='utf-8')
run('commit_docs',['commit','-F',str(message)])
head=run('head_after',['rev-parse','HEAD']).decode().strip()
assert not run('status_after',['status','--porcelain=v1'])
assert set(run('committed_names',['diff','--name-only',before['head'],head]).decode('utf-8').splitlines())==expected
rows=[r for r in run('tree_after',['ls-tree','-r','-z','HEAD']).split(b'\0') if r]
non_docs=[r for r in rows if not r.partition(b'\t')[2].startswith(b'docs/')]
prefixes=(b'actors/',b'core/',b'world/',b'ui/',b'data/',b'assets/',b'addons/',b'shaders/')
runtime=[r for r in rows if r.partition(b'\t')[2].startswith(prefixes) or r.partition(b'\t')[2]==b'project.godot']
digest=lambda values:hashlib.sha256(b'\0'.join(values)+b'\0').hexdigest()
game_state=next(r for r in rows if r.partition(b'\t')[2]==b'core/game_state.gd').partition(b'\t')[0].split()[-1].decode()
assert digest(runtime)==before['runtime_blob_manifest_sha256']
assert digest(non_docs)==before['all_non_docs_blob_manifest_sha256']
assert game_state==before['game_state_blob_sha1']
after={'head':head,'parent_head':before['head'],'clean':True,'changed_files':sorted(expected),
       'runtime_git_blob_rows':len(runtime),'runtime_blob_manifest_sha256':digest(runtime),'runtime_blobs_unchanged':True,
       'all_non_docs_git_blob_rows':len(non_docs),'all_non_docs_blob_manifest_sha256':digest(non_docs),'all_non_docs_blobs_unchanged':True,
       'game_state_blob_sha1':game_state,'game_execution_count_for_this_doc_task':0,'test_execution_count_for_this_doc_task':0,
       'main_landed':False,'parent_536_complete':False,'scope':'two explicitly staged docs only; root owns official checks and board'}
target=out/'after.json';assert not target.exists();target.write_text(json.dumps(after,indent=2)+'\n',encoding='utf-8')
print(json.dumps(after,indent=2))
