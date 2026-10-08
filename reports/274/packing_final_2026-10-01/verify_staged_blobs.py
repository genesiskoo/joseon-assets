"""Verify card274's index blobs against source bytes without printing source content."""
from pathlib import Path
import hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('staged_blob_audit.json')
ALLOWED=('workbench/production/item_icons_274_final/','reports/274/')
def run(*args):
    return subprocess.run(['git','-C',str(ROOT),*args],check=True,capture_output=True).stdout
def digest(data):return hashlib.sha256(data).hexdigest()
staged=[p.decode('utf-8') for p in run('diff','--cached','--name-only','-z').split(b'\0') if p]
assert staged and all(p.startswith(ALLOWED) for p in staged)
entries=[]
for record in run('ls-files','--stage','-z').split(b'\0'):
    if not record:continue
    meta,path=record.split(b'\t',1)
    mode,oid,stage=meta.decode('ascii').split()
    rel=path.decode('utf-8')
    if not rel.startswith(ALLOWED) or rel==OUT.relative_to(ROOT).as_posix():continue
    assert stage=='0' and mode=='100644'
    entries.append((rel,oid))
proc=subprocess.run(['git','-C',str(ROOT),'cat-file','--batch'],input=('\n'.join(oid for _,oid in entries)+'\n').encode('ascii'),check=True,capture_output=True)
position=0;rows=[]
for rel,oid in entries:
    end=proc.stdout.index(b'\n',position)
    found,kind,n=proc.stdout[position:end].decode('ascii').split()
    assert found==oid and kind=='blob'
    count=int(n);position=end+1
    data=proc.stdout[position:position+count];position+=count
    assert proc.stdout[position:position+1]==b'\n';position+=1
    disk=(ROOT/rel).read_bytes()
    assert data==disk,f'index changed source bytes: {rel}'
    rows.append({'path':rel,'git_blob':oid,'sha256':digest(data),'bytes':count})
assert position==len(proc.stdout)
result={'card':274,'result':'PASS','staged_count':len(staged),'verified_blobs':len(rows),'verified_bytes':sum(r['bytes'] for r in rows),'mode':'index blob equals current disk byte-for-byte','self_receipt_excluded':OUT.relative_to(ROOT).as_posix(),'secret_values_not_printed':True,'files':rows}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=True))
