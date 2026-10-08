from pathlib import Path
import hashlib, json, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
wt = Path('C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon')
base = Path('C:/workspace/joseon/._tmp/trace_558_20261002')
candidate = 'f1bf88f05a8eb48dd7d12510011245f3f6631e76'
roots = {
    'focused_1': wt/'tmp/e2e_raw/20261002T1351502942221_26024',
    'focused_2': wt/'tmp/e2e_raw/20261002T1415238741716_62096',
    'full_1': wt/'tmp/e2e_raw/20261002T1426594457684_60640',
}
git = ['git', '-c', 'safe.directory='+wt.as_posix(), '-C', str(wt)]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    assert not path.exists(), 'preserve prior evidence: '+str(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def run(out, label, argv):
    start = time.time()
    result = subprocess.run(argv, cwd=wt, capture_output=True)
    (out/(label+'.stdout.raw.log')).write_bytes(result.stdout)
    (out/(label+'.stderr.raw.log')).write_bytes(result.stderr)
    save(out/(label+'.metadata.json'), {'argv':argv,'returncode':result.returncode,'elapsed_seconds':time.time()-start})
    return result

summary = []
for mode in ('focused_1', 'focused_2'):
    out = base/'analysis'/(mode+'_vs_full_1')
    assert not out.exists(), 'preserve prior comparison directory'
    out.mkdir(parents=True)
    head = run(out, 'head_before', git+['rev-parse','HEAD'])
    assert head.returncode == 0 and head.stdout.decode().strip() == candidate
    status = run(out, 'status_before', git+['status','--porcelain=v1'])
    assert status.returncode == 0 and not status.stdout
    inputs = []
    for label in (mode, 'full_1'):
        source_root = roots[label]
        dest_root = out/'phase_evidence'/label
        dest_root.mkdir(parents=True)
        for phase in sorted(source_root.glob('phase_*')):
            dest = dest_root/phase.name
            dest.mkdir()
            for name in ('phase.json','godot.raw.log','console.merged.raw.log'):
                source = phase/name
                copy = dest/name
                copy.write_bytes(source.read_bytes())
                inputs.append({'source':str(source),'copy':str(copy),'bytes':source.stat().st_size,'sha256':sha(source)})
        for name in ('RUN.json','LAUNCH.json','stdout.raw.log','stderr.raw.log'):
            source = base/'cohort'/label/name
            copy = dest_root/('cohort_'+name)
            copy.write_bytes(source.read_bytes())
            inputs.append({'source':str(source),'copy':str(copy),'bytes':source.stat().st_size,'sha256':sha(source)})
        record = json.loads((base/'cohort'/label/'RUN.json').read_text(encoding='utf-8-sig'))
        assert record['candidate_commit'] == candidate and record['fixed_fps'] == 0
    save(out/'input_manifest.json', {'candidate':candidate,'scope':'completed declared runs only; no game/test launches or candidate writes',
         'script_sha256':sha(wt/'tools/combat_trace_compare.py'),'phase_archive_roots':[str(roots[mode]),str(roots['full_1'])],'inputs':inputs})
    result = run(out, 'compare', [sys.executable,'tools/combat_trace_compare.py',str(roots[mode]),str(roots['full_1']),'--out',str(out/'comparison.json')])
    summary.append({'comparison':mode+'_vs_full_1','returncode':result.returncode,'stdout':result.stdout.decode('utf-8','replace'),'stderr':result.stderr.decode('utf-8','replace'),'report':str(out/'comparison.json')})
    after = run(out, 'head_after', git+['rev-parse','HEAD'])
    status_after = run(out, 'status_after', git+['status','--porcelain=v1'])
    assert head.stdout == after.stdout and not status_after.stdout
    if result.returncode:
        print(result.stdout.decode('utf-8','replace')+result.stderr.decode('utf-8','replace'))
        sys.exit(result.returncode)

save(base/'analysis'/'full_comparison_operations_01.json', {'candidate':candidate,'comparisons':summary,'scope':'read-only analysis, candidate untouched'})
print(json.dumps(summary, ensure_ascii=False, indent=2))
