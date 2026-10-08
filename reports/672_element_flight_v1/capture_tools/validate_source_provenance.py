from pathlib import Path
import hashlib,json,subprocess
base=Path('._tmp/672_element_flight_v1'); root=Path.cwd()
before=json.loads((base/'before_metadata.json').read_text(encoding='utf-8'))
after=json.loads((base/'after01_metadata.json').read_text(encoding='utf-8'))
commit=subprocess.check_output(['git','rev-parse','507ce464'],text=True).strip()
for name,digest in before['source_hashes'].items():
    data=subprocess.check_output(['git','show',commit+':'+name])
    assert hashlib.sha256(data).hexdigest()==digest,'baseline commit differs: '+name
for name,digest in after['source_hashes'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
m=json.loads((base/'deliverables/video_manifest.json').read_text(encoding='utf-8'))
m['source_before_capture_head']=before['source_head']
m['source_before']=commit
m['source_before_commit_verified']={'commit':commit,'raw_source_files':len(before['source_hashes']),'all_raw_byte_sha256_match':True,'capture_at_uncommitted634_final':'original before_metadata.source_head retains actual earlier HEAD; every recorded runtime/data byte matches final634 commit'}
m['source_after_commit']='pending root final #672 code commit; captured raw source148 retained'
(base/'deliverables/video_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'before_commit':commit,'before_source_files':len(before['source_hashes']),'after_source_files':len(after['source_hashes']),'raw_source_exact':True}))