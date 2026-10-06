from pathlib import Path
import hashlib,json,shutil
source=Path('C:/Users/FORYOUCOM/.codex/worktrees/634-status-structure/joseon/._tmp/672_element_flight_v1')
target=Path('C:/Users/FORYOUCOM/.codex/worktrees/672-element-flight/joseon/._tmp/672_element_flight_v1')
target.mkdir(parents=True,exist_ok=True); rows=[]
for path in sorted(source.iterdir()):
    if not path.is_file() or (path.suffix=='.avi' and path.name!='before.avi'): continue
    dest=target/path.name; digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if dest.exists(): assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest,'refuse unrelated overwrite: '+str(dest)
    else: shutil.copy2(path,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    rows.append({'file':path.name,'bytes':path.stat().st_size,'sha256':digest})
assert next(r['sha256'] for r in rows if r['file']=='capture_flight.gd')=='5ef2977764f17386c37b4ea36b77f5ca1b283e82028de0c59f85517526dbe92e'
(target/'before_transfer_manifest.json').write_text(json.dumps({'source':str(source),'target':str(target),'files':rows,'failed_large_avi':'before_attempt01.avi retained locally in634 source path; failed raw/script copied'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'capture_sha':'fixed5ef297','before_avi':next(r for r in rows if r['file']=='before.avi')}))