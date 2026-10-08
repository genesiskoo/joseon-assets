from pathlib import Path
import hashlib,json,sys

sys.stdout.reconfigure(encoding='utf-8',errors='replace')
base=Path('C:/workspace/joseon/._tmp/trace_558_20261002')
out=base/'analysis'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={};phases={}
for name in ('focused_pair','focused_1_vs_full_1','focused_2_vs_full_1'):
    report=json.loads((out/name/'comparison.json').read_text(encoding='utf-8'))
    assert report['left_provenance_status']==report['right_provenance_status']=='verified actual argv/ENV/FILE/ATTEMPT/TRIES and saved raw bytes'
    for side in ('left','right'):
        for record in report[side+'_files']:
            assert sha(record['file'])==record['sha256']
            files[record['file']]=record['sha256']
        for proof in report[side+'_provenance']:
            assert sha(proof['phase'])==proof['phase_sha256']
            raw=Path(proof['phase']).parent/'godot.raw.log'
            assert sha(raw)==proof['godot_sha256']
            phases[proof['phase']]={'phase_sha256':proof['phase_sha256'],'godot_sha256':proof['godot_sha256']}
    manifest=json.loads((out/name/'input_manifest.json').read_text(encoding='utf-8'))
    for record in manifest['inputs']:
        assert sha(record['source'])==sha(record['copy'])==record['sha256']
histories=json.loads((out/'cohort_observed_rng_01.json').read_text(encoding='utf-8'))
firsts={mode:{battle:rows['doho0'][0] for battle,rows in records.items()} for mode,records in histories.items()}
target=out/'evidence_integrity_01.json'
assert not target.exists()
data={'candidate':'f1bf88f05a8eb48dd7d12510011245f3f6631e76','unique_actual_trace_files':len(files),'all_actual_traces':files,'balance_phase_proofs':phases,
      'original_sources_and_byte_copies_unchanged':True,'first_observed_doho_rng':firsts,
      'scope':'byte hashes and existing report reads only; no formal comparator/test/game execution or candidate writes'}
target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'trace_files':len(files),'phase_proofs':len(phases),'all_original_sources_unchanged':True,'firsts':firsts},ensure_ascii=False,indent=2))
