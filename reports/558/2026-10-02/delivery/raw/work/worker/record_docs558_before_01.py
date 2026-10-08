from pathlib import Path
import hashlib,json,subprocess,sys,time

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
wt=Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
out=Path('C:/workspace/joseon/._tmp/trace_558_20261002/worker/docs_record_01')
assert not out.exists(),'preserve earlier evidence'
out.mkdir(parents=True)
git=['git','-c','safe.directory='+wt.as_posix(),'-C',str(wt)]
def run(label,args):
    start=time.time();r=subprocess.run(git+args,capture_output=True)
    (out/(label+'.stdout.raw.log')).write_bytes(r.stdout)
    (out/(label+'.stderr.raw.log')).write_bytes(r.stderr)
    (out/(label+'.metadata.json')).write_text(json.dumps({'argv':git+args,'returncode':r.returncode,'elapsed_sec':time.time()-start},indent=2),encoding='utf-8')
    assert r.returncode==0,r.stderr.decode('utf-8','replace')
    return r.stdout
head=run('head_before',['rev-parse','HEAD']).decode().strip()
assert head=='c85149ee44c6c7b1183fcdeefb92a3912705d039'
status=run('status_before',['status','--porcelain=v1'])
assert not status,'do not touch another worker change'
rows=run('tree_before',['ls-tree','-r','-z','HEAD']).split(b'\0')
rows=[r for r in rows if r]
non_docs=[r for r in rows if not r.partition(b'\t')[2].startswith(b'docs/')]
runtime_prefixes=(b'actors/',b'core/',b'world/',b'ui/',b'data/',b'assets/',b'addons/',b'shaders/')
runtime=[r for r in rows if r.partition(b'\t')[2].startswith(runtime_prefixes) or r.partition(b'\t')[2]==b'project.godot']
def digest(values):return hashlib.sha256(b'\0'.join(values)+b'\0').hexdigest()
game_state=next(r for r in rows if r.partition(b'\t')[2]==b'core/game_state.gd').partition(b'\t')[0].split()[-1].decode()
manifest={'head':head,'clean':True,'runtime_scope':['actors','core','world','ui','data','assets','addons','shaders','project.godot'],
          'runtime_git_blob_rows':len(runtime),'runtime_blob_manifest_sha256':digest(runtime),
          'all_non_docs_git_blob_rows':len(non_docs),'all_non_docs_blob_manifest_sha256':digest(non_docs),
          'game_state_blob_sha1':game_state,
          'game_execution_count_for_this_doc_task':0,'test_execution_count_for_this_doc_task':0}
(out/'before.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
