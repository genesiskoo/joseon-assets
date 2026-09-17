# Motgol Village GPT Image Kit

Date: 2026-06-09

Purpose:

- First GPT Image asset batch for a Godot high-top-down Joseon village.
- Raw images are preserved separately from Godot-ready transparent PNGs.
- Each processed asset has anchor metadata for y-sort placement.

Ground pipeline:

- RD seamless base terrain + GPT path/detail overlays:
  `../../../docs/godot-rd-gpt-ground-pipeline.md`

## Folder Layout

```text
generated/raw/       # GPT Image originals copied from Codex generated_images
generated/rd_terrain_raw/
generated/gpt_ground_overlay_raw/
generated/rejected/  # unused variants
processed/           # transparent Godot-ready PNGs
godot/metadata/      # anchor, canvas, source bbox, and placement metadata
preview/             # contact sheets for visual review
```

## First Batch

| Asset ID | Processed PNG | Canvas | Anchor |
|---|---|---:|---:|
| `building_magistrate_a` | `processed/buildings/building_magistrate_a.png` | `512x512` | `256,375` |
| `building_hanok_small_a` | `processed/buildings/building_hanok_small_a.png` | `256x256` | `128,206` |
| `building_mudang_house_a` | `processed/buildings/building_mudang_house_a.png` | `400x400` | `200,320` |
| `gate_compound_a` | `processed/boundaries/gate_compound_a.png` | `256x256` | `128,191` |
| `prop_market_stall_a` | `processed/props/prop_market_stall_a.png` | `256x256` | `128,201` |
| `tree_pine_a` | `processed/vegetation/tree_pine_a.png` | `256x256` | `128,227` |
| `decal_shadow_under_eaves_a` | `processed/decals/decal_shadow_under_eaves_a.png` | `256x256` | `128,128` |

Preview:

- `preview/first-batch-contact-sheet.png`

## Ground Batch

Accepted RD-derived base terrain:

- `processed/terrain/normalized-base-v2/`
- Eight seamless `256x256` textures covering packed earth, dry yard,
  dead grass, and dark mud.
- The set uses one accepted seamless RD master plus deterministic local
  color and rotation variants. Independent RD generations were too
  inconsistent for a coherent terrain family.

GPT Image path overlays:

| Asset ID | Canvas | Branch Openings |
|---|---:|---|
| `path_main_straight_a` | `512x256` | left, right |
| `path_main_straight_b` | `512x256` | left, right |
| `path_main_curve_a` | `512x512` | bottom, right |
| `path_main_tjunction_a` | `512x512` | left, right, bottom |
| `path_main_cross_a` | `512x512` | left, right, top, bottom |
| `path_narrow_trail_a` | `256x512` | top, bottom |
| `path_courtyard_patch_a` | `512x512` | none |
| `path_building_apron_a` | `512x256` | none |

Paths:

- Processed PNGs: `processed/path_patches/`
- Metadata: `godot/metadata/path_patches/`
- Chroma originals: `generated/gpt_ground_overlay_raw/`
- Prompt set: `generated/gpt_ground_overlay_raw/PROMPTS.md`
- Preview: `preview/ground-overlay-tests/path-patch-contact-sheet.png`
- Connection test: `preview/ground-overlay-tests/path-patch-overlap-test.png`

Connected branches have a baked `20px` endpoint alpha fade. Overlap
neighboring pieces by approximately `24px`; do not place them edge to edge.

RD generation spend for palette/style/terrain probes and recovery:

- Total: `$0.797`
- Remaining balance after the run: `$8.560`

## Gate Split Test

`gate_compound_a` also has a simple horizontal split:

- Body: `processed/boundaries/gate_compound_a_body.png`
- Roof occluder: `processed/occluders/gate_compound_a_roof_occluder.png`

This is only a first-pass automated split. For production, manually mask the roof/eaves so the open passage remains clean.

## Godot Placement Rule

Each scene root should be positioned at the asset anchor in world space.

```gdscript
BuildingRoot.position = world_anchor_position
Sprite2D.centered = false
Sprite2D.position = -anchor_px
```

Example for `building_magistrate_a`:

```gdscript
$Sprite2D.centered = false
$Sprite2D.position = Vector2(-256, -375)
```

Use metadata files in `godot/metadata/` as the source of truth.

## Collision Rule

Do not use the full sprite rectangle.

Draw collision only around:

- wall footprint
- foundation
- posts
- closed doorway edges
- non-walkable steps

Do not include:

- roof surface
- upper eaves
- transparent padding
- decorative overhangs

## Import Settings

Suggested Godot import settings:

- Filter: choose one project-wide style.
  - `off` if the whole project is nearest-neighbor pixel art.
  - `on` if these GPT assets are used as smooth high-res painterly sprites.
- Mipmaps: off for 2D pixel-style maps.
- Repeat: disabled.
- Compression: lossless.

## Quality Notes

- `building_magistrate_a`: good landmark candidate.
- `building_hanok_small_a`: strong reusable house candidate, but still fairly ornate for a common house.
- `building_mudang_house_a`: best story-area building in this batch.
- `gate_compound_a`: good y-sort/pass-through test candidate.
- `prop_market_stall_a`: strong medium prop.
- `tree_pine_a`: good y-sort vegetation test; trunk base anchor is important.
- `decal_shadow_under_eaves_a`: usable as a first contact shadow, but should be tuned in-engine with modulate alpha.

## Prompt Discipline Used

Shared constraints:

- high top-down Godot 2D game asset
- flat chroma-key background
- full object visible
- generous padding
- matte pixel-art-inspired style
- soft diffuse overcast lighting
- low contrast flat shading
- no glossy highlights
- no specular highlights
- no white rim light
- no glowing edges
- no bloom
- no cast shadow on the chroma background

Chroma keys:

- Most assets: `#00ff00`
- Pine tree: `#ff00ff` to avoid conflict with green foliage

## Next Batch

Recommended next assets:

1. `building_thatched_small_a`
2. `building_inn_a`
3. `building_shrine_a`
4. `wall_stone_straight_a`
5. `wall_stone_corner_a`
6. `prop_jangseung_a`
7. `prop_onggi_cluster_a`
8. `decal_mud_patch_a`
