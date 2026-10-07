"""Preserve #680 producer sources/results/raw logs with byte/SHA256 manifests.
Only writes this card's owned asset workbench and reports/blender_source folders.
"""
import argparse, hashlib, json, shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
parser.add_argument('--report', required=True)
args = parser.parse_args()
root = Path(args.root).resolve()
report = Path(args.report).resolve()
report.mkdir(parents=True, exist_ok=True)


def entry(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


copy_paths = []
for folder in ['source', 'blends', 'previews', 'staged']:
    copy_paths += [p for p in (root / folder).rglob('*') if p.is_file() and not p.name.endswith(('.blend1', '.blend2'))]
copy_paths += [p for p in root.glob('*') if p.is_file() and (p.suffix in ['.log', '.json'])]
for path in copy_paths:
    destination = report / path.relative_to(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
report_files = [entry(p) for p in report.rglob('*') if p.is_file() and p.name not in ['manifest.json', 'README.md', '.gitignore']]
raw_frames = [entry(p) for p in (root / 'frames').rglob('*.png')]
render = json.loads((root / 'full_render_report.json').read_text(encoding='utf-8-sig'))
fire_render = json.loads((root / 'full_fire_render_report.json').read_text(encoding='utf-8-sig'))
pack = json.loads((root / 'pack_report.json').read_text(encoding='utf-8-sig'))
manifest = {'schema': 1, 'card': 680, 'method': render['method'], 'seed': 680, 'hardware': render['hardware'], 'blender': render['blender'], 'render_settings': {'engine': 'BLENDER_EEVEE', 'size': [384, 384], 'rgba': 8, 'taa_render_samples': 64, 'volumetric_samples': 64, 'volumetric_tile_size': 2, 'volumetric_shadow_samples': 16, 'use_volumetric_shadows': True, 'fps': 24, 'view_transform': 'AgX', 'look': 'AgX - Medium High Contrast'}, 'source_variants': {'fire': 'source/make_blender_vfx.py (v4 density only correction)', 'sal': 'source/make_blender_vfx_v3.py (same sal fields in final source)'}, 'timings': {'full_56_frames_seconds': render['elapsed_seconds'], 'fire_v4_28_frames_seconds': fire_render['elapsed_seconds']}, 'deliverables': pack, 'preserved_report_files': report_files, 'ignored_intermediate_frames': raw_frames, 'report_bytes_before_manifest': sum(e['bytes'] for e in report_files)}
if any(e['bytes'] >= 10 * 1024 * 1024 for e in report_files):
    raise SystemExit('Per-file 10MiB cap exceeded')
if manifest['report_bytes_before_manifest'] >= 45 * 1024 * 1024:
    raise SystemExit('Producer report leaves too little space under whole-card 50MiB cap')
for target in [root, report]:
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (target / 'README.md').write_text(f'''# #680 Blender VFX test — producer source

These are actual Blender 5.2.2 LTS renders on NVIDIA GeForce RTX 4070, OpenGL 4.6 NVIDIA 595.79.
Method: animated procedural **3D participating volumes** (Principled Volume, periodic 4D Noise/domain warp,
five ellipsoid smoke lobes, narrow emissive fire core and curved fraying branches). This is not a fluid solver
simulation or a baked fluid cache. All generation is local; paid services/downloads/installs: zero.

## Final resources

- `staged/assets/vfx/blender_fire_jet/blender_fire_jet_sheet.png` + `_meta.json`
- `staged/assets/vfx/blender_sal_mist/blender_sal_mist_sheet.png` + `_meta.json`
- `staged/assets/vfx/blender_hybrid/ember.glb` (12 vertices/20 triangles, 2064 bytes)
- `staged/assets/vfx/blender_hybrid/drop.glb` (42 vertices/80 triangles, 3740 bytes)

Each atlas is RGBA8, 2304×1536 = 6×4 frames at 384×384. 28 actual rendered inputs → four-frame
premultiplied-alpha overlap → 24 output frames at 24fps. Fixed full-canvas common crop `[0,0,384,384]`.
Fire nozzle anchor `[0.8194,0.5]`, source on the right and tail on the left; nominal Godot width1.5u.
Sal anchor `[0.5,0.5]`, centered dark purple billows; nominal Godot width1.8u. Read actual alpha/seam
measurements from the metadata/pack report; no alpha/keying generation substitutes were used.

Blender Z-up becomes glTF/Godot Y-up via exporter `export_yup=True`. Both meshes' long axis is +Y.
Ember bounds: X±0.024149474, Y±0.075000003, Z±0.022967281.
Drop bounds: X±0.033287026, Y[-0.064999998,0.089999996], Z±0.034999996; pointed end +Y.
The Godot factory owns runtime scaling, opacity, HDR core gain, particle count and visibility.

## Renderer and reproduction

Renderer: Eevee, TAA64, volume64, tile2, volume shadows16, fixed orthographic camera,
AgX/Medium High Contrast, RGBA PNG. Seed680. Periodic density/advection controls have actual
29-frame keyframes retained in the `.blend` authoring files. Materials/node fields and camera are all
in the scene; generation Python remains authoritative for the mesh exports and final per-frame settings.

`E:/SteamLibrary/steamapps/common/Blender/blender.exe --background --factory-startup --python source/make_blender_vfx.py -- --root <owned_workbench_path> --mode full --size 384 --samples 64`

`python source/pack_atlases.py --root <owned_workbench_path>`

Production pass56frames: {render['elapsed_seconds']:.3f}s. Fire density correction28frames: {fire_render['elapsed_seconds']:.3f}s.
Version1/2/3 representative previews are immutable numbered files. Final fire uses v4, which changes
only actual volume density from1.1→4.4 after the original alpha gate rejected maxima22…57/255.
Sal remains the accepted v3 five-lobe source. Full raw stdout/stderr and the initial failed packing gate are retained.

## Files and budget

`manifest.json` records source paths, byte sizes, SHA256, raw-frame intermediate locations/hashes,
actual hardware/settings/timings and final atlases' seam/alpha metrics. Raw RGBA frames remain in
workbench `frames/` and are ignored; `.blend` authoring files remain local/ignored with hashes.
No large fluid cache exists. Producer report before manifest: {manifest['report_bytes_before_manifest']} bytes.
Every delivered/report file is below10MiB; producer subtotal is well below the whole-card50MiB cap.
Game intake is performed by the root only; this producer did not change runtime code or main.
''', encoding='utf-8')
(report / '.gitignore').write_text('/blends/\n*.blend1\n*.blend2\n', encoding='utf-8')
print('PRODUCER_MANIFEST ' + json.dumps({'report': str(report), 'files': len(report_files), 'report_bytes': manifest['report_bytes_before_manifest'], 'ignored_raw_frames': len(raw_frames), 'deliverables': pack}))
