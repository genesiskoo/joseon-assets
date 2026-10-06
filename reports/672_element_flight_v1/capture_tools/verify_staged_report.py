from pathlib import Path
import hashlib,json,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
repo=Path('C:/workspace/joseon-assets')
base=repo/'reports/672_element_flight_v1'
m=json.loads((base/'archive_manifest.json').read_text(encoding='utf-8'))
rows=m['files']+[{'file':'archive_manifest.json','bytes':(base/'archive_manifest.json').stat().st_size,'sha256':hashlib.sha256((base/'archive_manifest.json').read_bytes()).hexdigest()}]
actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
assert actual=={row['file'] for row in rows},'archive manifest topology differs'
for row in rows:
    data=(base/row['file']).read_bytes()
    assert len(data)==row['bytes']<10_000_000 and hashlib.sha256(data).hexdigest()==row['sha256'],row['file']
    staged=subprocess.check_output(['git','-C',str(repo),'show',':reports/672_element_flight_v1/'+row['file']])
    assert staged==data,'staged blob mismatch: '+row['file']
assert sum(r['bytes'] for r in rows)<50_000_000
print(json.dumps({'card':672,'game_commit':m['game_commit'],'archive_files':len(rows),'archive_bytes':sum(r['bytes'] for r in rows),'original_archive_staged_bytes_sha_exact':True,'all_files_under10MB':True,'total_under50MB':True},ensure_ascii=False))