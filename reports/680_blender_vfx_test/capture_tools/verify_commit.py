"""Exact AFTER resources vs final Git blobs; only documented baseline CRLF metadata is permitted."""
from pathlib import Path
import sys,subprocess,hashlib,json
root=Path.cwd(); base=root/'._tmp/680_blender_vfx_test/capture'; phase=sys.argv[2] if len(sys.argv)>2 else 'after01'
commit=subprocess.check_output(['git','rev-parse',sys.argv[1]],text=True).strip()
before=json.loads((base/'before_metadata.json').read_text(encoding='utf-8')); after=json.loads((base/(phase+'_metadata.json')).read_text(encoding='utf-8'))
assert after['absolute_combat_invariant_equal']
allowed={e['path']:e for e in before['source_commit_verification']['newline_only_files']}
names=list(after['source_hashes']); data=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(commit+':'+n for n in names)+'\n').encode()); cursor=0; exact=[]; baseline_newline=[]
for name in names:
    end=data.index(b'\n',cursor); header=data[cursor:end].split(); assert len(header)==3,('final resource uncommitted',name)
    size=int(header[2]); blob=data[end+1:end+1+size]; cursor=end+size+2; sha=hashlib.sha256(blob).hexdigest(); captured=after['source_hashes'][name]
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==captured,('runtime changed after capture',name)
    if sha==captured: exact.append(name)
    else:
        assert name in allowed and sha==allowed[name]['git_blob_sha256'] and captured==allowed[name]['raw_sha256'],('new final raw source mismatch',name)
        baseline_newline.append(allowed[name])
result={'commit':commit,'captured_resource_files':len(names),'raw_byte_exact_files':len(exact),'runtime_gd_shader_data_scene_raw_exact':True,'existing_crlf_metadata_exceptions':baseline_newline,'all_after_sources_match_final_commit':True,'runtime_raw_sha256_record':after['source_hashes']}
for path in [base/'deliverables/video_manifest.json',Path('C:/workspace/joseon-assets/reports/680_blender_vfx_test/video_manifest.json')]:
    if path.exists():
        m=json.loads(path.read_text(encoding='utf-8')); m['source_after_commit']=commit; m['source_after_commit_verification']=result
        path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'commit':commit,'captured_resources':len(names),'rawexact':len(exact),'only_baseline_crlf_exceptions':len(baseline_newline)},ensure_ascii=False))
