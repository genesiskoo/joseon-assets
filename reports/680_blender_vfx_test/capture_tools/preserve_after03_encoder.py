"""Keep the preceding published encoder originals byte-exact before AFTER04 replaces the report ZIP."""
from pathlib import Path
import hashlib,json,zipfile
base=Path(__file__).resolve().parent
report=Path('C:/workspace/joseon-assets/reports/680_blender_vfx_test')
manifest=json.loads((report/'video_manifest.json').read_text(encoding='utf-8'))
assert manifest['phase_after']=='after03','Only archive the existing actual AFTER03 report.'
rows=[]
with zipfile.ZipFile(report/'capture_raw_originals.zip') as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.startswith('680_blender_vfx_') and (name.endswith('.log') or name.endswith('_probe.json')):
            data=z.read(name); out=base/('after03_original_'+name)
            if out.exists(): assert out.read_bytes()==data
            else: out.write_bytes(data)
            rows.append({'original_zip_entry':name,'preserved_entry':out.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(base/'after03_original_video_manifest.json').write_bytes((report/'video_manifest.json').read_bytes())
(base/'after03_encoder_original_preservation.json').write_text(json.dumps({'phase':'after03','entries':rows,'source_zip':'C:/workspace/joseon-assets/reports/680_blender_vfx_test/capture_raw_originals.zip','purpose':'Original AFTER03 encoder/decode/probe byte preservation before final AFTER04 publication.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'preserved_files':len(rows),'preserved_bytes':sum(r['bytes'] for r in rows)}))
