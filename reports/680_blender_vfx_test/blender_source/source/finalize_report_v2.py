"""#680 packing revision2: immutable original384 render; common alpha-union crop only.
Proof: every new atlas cell is byte-exact crop of the preserved revision1 atlas cell.
"""
from pathlib import Path
import copy, hashlib, json, shutil
import numpy as np
from PIL import Image

root = Path('C:/workspace/joseon-assets/workbench/vfx/680_blender_vfx_test').resolve()
report = Path('C:/workspace/joseon-assets/reports/680_blender_vfx_test/blender_source').resolve()
old = json.loads((root / 'revisions/pack_v1/manifest.json').read_text(encoding='utf-8-sig'))
pack = json.loads((root / 'pack_report.json').read_text(encoding='utf-8-sig'))
proof = []
for record in pack:
    cue = 'blender_fire_jet' if record['effect'] == 'fire' else 'blender_sal_mist'
    relative = Path('staged/assets/vfx') / cue / (cue + '_sheet.png')
    previous = Image.open(root / 'revisions/pack_v1' / relative).convert('RGBA')
    current = Image.open(root / relative).convert('RGBA')
    fw, fh = record['fw'], record['fh']
    for i in range(24):
        before = previous.crop(((i % 6) * 384, (i // 6) * 384, (i % 6 + 1) * 384, (i // 6 + 1) * 384)).crop(record['common_crop'])
        after = current.crop(((i % 6) * fw, (i // 6) * fh, (i % 6 + 1) * fw, (i // 6 + 1) * fh))
        if not np.array_equal(np.asarray(before), np.asarray(after)):
            raise SystemExit(f'Revision2 color/alpha mutated outside crop: {cue} frame{i}')
    meta = json.loads((root / 'staged/assets/vfx' / cue / (cue + '_meta.json')).read_text())
    error = [abs(meta['anchor'][0] * fw + meta['common_crop'][0] - meta['source_anchor'][0] * 384), abs(meta['anchor'][1] * fh + meta['common_crop'][1] - meta['source_anchor'][1] * 384)]
    if max(error) > 0.00001:
        raise SystemExit('Emitter anchor moved in original image coordinates: ' + str(error))
    proof.append({'effect': record['effect'], '24_cells_byte_exact_crop': True, 'anchor_pixel_error': error, 'common_crop': record['common_crop']})
for row in old['ignored_intermediate_frames']:
    path = Path(row['path'])
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
        raise SystemExit('Original Blender384 raw frame SHA changed: ' + str(path))
copy_paths = []
for folder in ['source', 'blends', 'previews', 'staged', 'revisions']:
    copy_paths.extend(p for p in (root / folder).rglob('*') if p.is_file() and not p.name.endswith(('.blend1', '.blend2')))
copy_paths.extend(p for p in root.glob('*') if p.is_file() and p.suffix in ['.log', '.json'] and p.name != 'manifest.json')
for source in copy_paths:
    destination = report / source.relative_to(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
manifest = copy.deepcopy(old)
manifest['packing_revision'] = 2
manifest['previous_revision_snapshot'] = 'revisions/pack_v1'
manifest['crop_proofs'] = proof
manifest['original_raw_56_sha_unchanged'] = True
manifest['deliverables'] = pack
manifest['packing_change'] = 'Fixed alpha>2 union over all28 originalframes,8pixelmargin; sal symmetric about192,192. Pixel-exact crop; no source re-render/color/alpha/gain changes.'
files = [p for p in report.rglob('*') if p.is_file() and p not in [report / 'manifest.json', report / 'README.md', report / '.gitignore']]
manifest['preserved_report_files'] = [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest['report_bytes_before_manifest'] = sum(p.stat().st_size for p in files)
if any(p.stat().st_size >= 10 * 1024 * 1024 for p in files) or manifest['report_bytes_before_manifest'] >= 45 * 1024 * 1024:
    raise SystemExit('Producer revision2 report exceeds card media budget')
readme = (root / 'revisions/pack_v1/README.md').read_text(encoding='utf-8-sig')
start = readme.index('Each atlas is RGBA8')
end = readme.index('Blender Z-up', start)
new = '''Packing revision2 uses the same actual384×384 RGBA8 Blender inputs. 28 inputs → four-frame
premultiplied-alpha overlap →24 outputframes at24fps. **Only a fixed common crop changed** after Godot
AFTER01 showed excessive transparent canvas. No pixel color/alpha/exposure changes and no new renders.

- Fire: frame312×90, atlas1872×360, original crop[13,149,325,239], anchor[0.96682564,0.47777778].
  Source alpha>2 union[21,157,317,231]; cropped actualvisible union[8,8,304,82].
- Sal: frame292×158, atlas1752×632, symmetric originalcrop[46,113,338,271], anchor[0.5,0.5].
  Source alpha>2 union[54,121,307,261]; cropped actualvisible union[8,8,261,148].

The nozzle's originalimage position remains384×[0.8194,0.5]; transformedanchor error below0.00001px.
Each newatlas cell was verified pixel-byte-exact against cropping its preserved original revision1
atlas cell. All56 originalrenderedPNG SHA256 values are unchanged. Version1 source, originaluncropped
atlases/metas, oldmanifest and oldREADME are immutable under `revisions/pack_v1/`.
`crop_proofs`/`packing_revision` in manifest and `common_crop`/`source_canvas`/`source_anchor` in metadata
state this transformation explicitly. Godot owns actualquad dimensions and shaderalpha/coregain.

'''
readme = readme[:start] + new + readme[end:]
readme = readme.replace('Producer report before manifest: 2570217 bytes.', f"Producer report before manifest: {manifest['report_bytes_before_manifest']} bytes.")
for target in [root, report]:
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (target / 'README.md').write_text(readme, encoding='utf-8')
print('REVISION2_CROP_VERIFIED ' + json.dumps({'producer_report_bytes': manifest['report_bytes_before_manifest'], 'raw_frames_sha_unchanged': 56, 'proof': proof, 'deliverables': pack}))
