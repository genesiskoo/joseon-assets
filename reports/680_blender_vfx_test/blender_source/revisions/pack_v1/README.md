# #680 Blender VFX test — producer source

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

Production pass56frames: 52.899s. Fire density correction28frames: 33.377s.
Version1/2/3 representative previews are immutable numbered files. Final fire uses v4, which changes
only actual volume density from1.1→4.4 after the original alpha gate rejected maxima22…57/255.
Sal remains the accepted v3 five-lobe source. Full raw stdout/stderr and the initial failed packing gate are retained.

## Files and budget

`manifest.json` records source paths, byte sizes, SHA256, raw-frame intermediate locations/hashes,
actual hardware/settings/timings and final atlases' seam/alpha metrics. Raw RGBA frames remain in
workbench `frames/` and are ignored; `.blend` authoring files remain local/ignored with hashes.
No large fluid cache exists. Producer report before manifest: 2570217 bytes.
Every delivered/report file is below10MiB; producer subtotal is well below the whole-card50MiB cap.
Game intake is performed by the root only; this producer did not change runtime code or main.
