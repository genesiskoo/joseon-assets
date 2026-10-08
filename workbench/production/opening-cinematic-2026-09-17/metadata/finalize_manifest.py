"""Record local output metadata and hashes; never store signed upload URLs."""
from pathlib import Path
import hashlib, json, sys
from PIL import Image

root = Path(sys.argv[1])
path = root / 'metadata' / 'manifest.json'
data = json.loads(path.read_text(encoding='utf-8-sig'))
data['technical_outputs'] = {}
for shot in ['OP04', 'OP06', 'OP11']:
    probe = root / 'metadata' / f'{shot}_ffprobe.json'
    if probe.exists():
        data['technical_outputs'][shot] = json.loads(probe.read_text(encoding='utf-8-sig'))
data['file_inventory'] = []
for file in sorted(root.rglob('*')):
    if not file.is_file() or file == path:
        continue
    entry = {'path':file.relative_to(root).as_posix(), 'bytes':file.stat().st_size,
             'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    if file.suffix.lower() in ['.jpg','.png']:
        with Image.open(file) as img:
            entry['width'], entry['height'] = img.size
    data['file_inventory'].append(entry)
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(data['file_inventory']),'outputs':list(data['technical_outputs'])}))
