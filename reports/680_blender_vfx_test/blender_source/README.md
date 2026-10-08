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

Packing revision2 uses the same actual384×384 RGBA8 Blender inputs. 28 inputs → four-frame
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
workbench `frames/` and are ignored. Editable `.blend` copies are included under report `blends/`; workbench authoring copies remain ignored with hashes.
No large fluid cache exists. Producer report before manifest: 3934665 bytes.
Every delivered/report file is below10MiB; producer subtotal is well below the whole-card50MiB cap.
Game intake is performed by the root only; this producer did not change runtime code or main.
