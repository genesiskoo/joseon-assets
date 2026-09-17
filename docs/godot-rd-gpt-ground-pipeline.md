# Godot RD + GPT Ground Pipeline

Date: 2026-06-09

## Decision

Use a hybrid ground pipeline:

- **Retro Diffusion**: seamless base terrain textures.
- **GPT Image**: non-repeating path patches and detail decals.
- **Godot**: repetition, layer composition, opacity, contact shadow strength, navigation, and collision.

Do not replace the current PixelLab 32px tileset with another 32px Wang tileset. The current 128px characters and high-detail GPT buildings need a larger and quieter ground scale.

Target base texture:

- Native size: `256x256`.
- Seamless on both axes.
- No embedded light direction.
- No large landmarks or recognizable repeated objects.
- Used as a repeating texture, not as a gameplay-grid tile.

## Responsibility Split

| Layer | Tool | Reason |
|---|---|---|
| Base terrain | RD | Seamless repetition and low-cost variants |
| Secondary terrain fill | RD | Same texture family and palette |
| Path patches | GPT Image | Large irregular silhouettes and natural edges |
| Detail decals | GPT Image | Unique visual storytelling details |
| Building contact shadows | GPT Image or local mask | Irregular large silhouettes |
| Small prop/tree shadows | Godot/local mask | Better consistency and controllable opacity |
| Buildings and large props | GPT Image | Higher visual quality |
| Collision/navigation | Godot | Must follow gameplay, not generated pixels |

## Visual Hierarchy

The ground must remain quieter than characters and buildings.

Priority:

```text
characters > landmark buildings > props > path patches > detail decals > base terrain
```

Base terrain requirements:

- Low contrast.
- Matte surface.
- Desaturated brown, grey, and olive colors.
- No bright isolated pixels.
- No directional cast shadows.
- No reflective wet highlights unless the terrain is explicitly water or mud.
- Texture features should usually stay within `2-12px` at native `256x256`.
- Avoid stones, leaves, or cracks larger than roughly `24px`; those belong in overlays.

## Shared Palette

Before RD production generation:

1. Extract a small palette image from the accepted Motgol GPT assets.
2. Prioritize:
   - dark giwa grey
   - warm old wood brown
   - packed earth brown
   - muted stone grey
   - dark olive
   - muted paper beige
3. Use the palette through RD `input_palette`.
4. If generation still drifts, use RD `color_style_transfer` with an accepted Motgol composite reference.

Recommended palette size:

- `16-24` colors.
- Saved as `maps/village_kits/motgol/palettes/motgol-ground-palette.png`.

## RD Base Terrain Strategy

### Style Probe

Test the same packed-earth prompt with two styles:

1. `rd_fast__texture`
2. `rd_plus__textured`

Shared payload:

```json
{
  "prompt": "seamless flat top-down game ground texture, dark muted packed earth in a Joseon-era Korean village, compact dry soil, tiny dull pebbles, subtle footprints and grain, matte diffuse surface, desaturated brown grey palette, low contrast, no objects, no grass clumps, no large stones, no directional lighting, no highlights, no shine",
  "width": 256,
  "height": 256,
  "num_images": 2,
  "seed": 2026060901,
  "tile_x": true,
  "tile_y": true,
  "check_cost": true
}
```

Run `check_cost` separately for each style. After approval, remove only `check_cost`; do not change the dimensions, image count, seed, or prompt.

Selection criteria:

- Invisible seam in a `4x4` repetition preview.
- No obvious 256px periodic object.
- Color matches the GPT buildings.
- Texture remains quiet under a 128px character.
- No high-contrast pixel clusters that look like specular highlights.

### First Production Set

Generate four terrain families.

| ID | Description | Primary Use |
|---|---|---|
| `terrain_earth_packed` | dark packed earth | dominant village ground |
| `terrain_yard_dry` | trampled dry yard soil | hanok courtyards |
| `terrain_grass_dead` | dark olive dead grass and soil | village edges |
| `terrain_mud_dark` | damp compact mud without shine | drains and damaged areas |

Start with two variants per family:

```text
terrain_earth_packed_a_256.png
terrain_earth_packed_b_256.png
terrain_yard_dry_a_256.png
terrain_yard_dry_b_256.png
...
```

Expand to four variants only after the Godot composite test passes.

### RD Prompt Templates

Packed earth:

```text
seamless flat top-down game ground texture, dark muted packed earth,
compact dry soil, tiny dull pebbles, very subtle irregular grain,
matte diffuse surface, desaturated brown grey palette, low contrast,
no objects, no grass clumps, no large stones, no directional lighting,
no highlights, no shine, no border
```

Dry yard:

```text
seamless flat top-down Joseon village courtyard ground texture,
trampled dry earth, faint straw fibers and compact soil variation,
quiet matte surface, muted warm brown palette, low contrast,
no objects, no large straw piles, no footprints larger than a few pixels,
no directional lighting, no highlights, no shine
```

Dead grass:

```text
seamless flat top-down rural ground texture,
dark desaturated olive dead grass mixed with compact brown soil,
very small sparse grass marks, matte diffuse surface, low contrast,
no yellow field, no bright green, no large grass clumps,
no directional lighting, no highlights, no shine
```

Dark mud:

```text
seamless flat top-down compact dark mud texture,
damp brown soil with shallow dull variation, no puddle reflection,
matte diffuse surface, desaturated brown charcoal palette, low contrast,
no objects, no deep footprints, no water highlights,
no directional lighting, no specular shine
```

## GPT Path Patch Strategy

Path patches are not seamless textures. They are large transparent shapes placed over RD terrain.

### Initial Path Kit

| ID | Final Canvas | Shape |
|---|---:|---|
| `path_main_straight_a` | `512x256` | wide straight road |
| `path_main_straight_b` | `512x256` | alternate straight road |
| `path_main_curve_a` | `512x512` | broad 90-degree curve |
| `path_main_tjunction_a` | `512x512` | T junction |
| `path_main_cross_a` | `512x512` | four-way crossing |
| `path_narrow_trail_a` | `256x512` | narrow footpath |
| `path_courtyard_patch_a` | `512x512` | irregular open yard |
| `path_building_apron_a` | `512x256` | worn area in front of a building |

Rules:

- Generate on flat chroma background.
- Ends of roads should extend to the canvas edge for overlap.
- Outer edges should be irregular, not rectangular.
- No hard outline.
- No baked cast shadow.
- No bright stones or isolated highlights.
- Final alpha edge should be feathered by roughly `8-24px`, depending on canvas size.
- For the Motgol first batch, branch endpoints use a `20px` alpha fade.
- Overlap connected Motgol pieces by about `24px`; do not butt endpoints together.

Prompt template:

```text
one irregular [PATH SHAPE] packed-earth road patch for a Joseon village,
high top-down Godot 2D ground overlay,
perfectly flat solid #00ff00 chroma-key background,
dark muted compact soil with subtle dull pebbles and light wear,
soft uneven transparent-ready outer edges, road ends continue to canvas edges,
matte low-contrast surface, no hard border, no cast shadow,
no glossy highlights, no rim light, no bloom, no text
```

## GPT Detail Decal Strategy

Detail decals carry variation and narrative information that should not repeat with the base texture.

### Neutral Decals

| ID | Canvas |
|---|---:|
| `decal_mud_patch_a` | `256x256` |
| `decal_straw_scatter_a` | `128x128` |
| `decal_pebbles_a` | `128x128` |
| `decal_cart_tracks_a` | `256x128` |
| `decal_footprints_a` | `256x128` |
| `decal_dry_grass_edge_a` | `256x256` |
| `decal_broken_stone_scatter_a` | `256x256` |

### Story Decals

| ID | Canvas |
|---|---:|
| `decal_talisman_scraps_a` | `128x128` |
| `decal_ritual_ash_a` | `256x256` |
| `decal_dark_spirit_stain_a` | `256x256` |
| `decal_blood_trail_muted_a` | `256x128` |
| `decal_burn_mark_a` | `256x256` |

Rules:

- Transparent PNG.
- No y-sort.
- No collision.
- Default `z_index` below all world objects.
- Rotation allowed only for decals without a visible lighting direction.
- Maintain at least three variants for high-frequency decals such as straw, pebbles, and mud.

## Contact Shadow Strategy

Do not generate every contact shadow with GPT Image.

Use three classes:

### Class A: Procedural / Shared Mask

For:

- jars
- crates
- market props
- small rocks
- trees

Use:

- one soft ellipse or irregular oval texture;
- Godot `self_modulate` or material alpha;
- scale per object;
- opacity around `0.15-0.35`.

### Class B: GPT Building Shadow

For:

- large hanok
- magistrate office
- compound gate
- wide roof eaves

Generate a specific wide irregular shadow only when a generic mask cannot follow the footprint.

### Class C: Authored Occlusion

For:

- gate passages
- porch interiors
- areas under roof overhangs

Use a manually masked shadow or a dedicated Godot polygon. Gameplay readability is more important than generated realism.

## Godot Layer Structure

Recommended scene:

```text
MotgolVillage
├─ GroundRoot                       z = -100
│  ├─ BaseTerrain                   z = -100
│  ├─ SecondaryTerrain              z = -95
│  ├─ PathPatches                   z = -90
│  ├─ DetailDecals                  z = -80
│  └─ ContactShadows                z = -20
├─ YSortedWorld                     y_sort_enabled = true
│  ├─ Buildings
│  ├─ Props
│  ├─ Vegetation
│  └─ Characters
├─ ForegroundOccluders
└─ NavigationRegion2D
```

Base terrain implementation:

- Preferred: `Polygon2D` or a region-based `Sprite2D` with repeated UVs.
- Set the CanvasItem texture repeat mode so UVs outside the source texture repeat.
- `Polygon2D` supports texture offset, rotation, scale, and explicit UVs.
- Keep visual terrain independent from the collision/navigation grid.

Use `TileMapLayer` only when editor painting, terrain metadata, collision, or a strict cell grid is useful. Do not force the 256px visual base texture into a 32px art tile.

## Folder Structure

Add to the Motgol kit:

```text
maps/village_kits/motgol/
├─ generated/
│  ├─ raw/                     # existing GPT building raw files
│  ├─ rd_terrain_raw/
│  └─ gpt_ground_overlay_raw/
├─ palettes/
│  └─ motgol-ground-palette.png
├─ processed/
│  ├─ terrain/
│  │  ├─ base/
│  │  └─ variants/
│  ├─ path_patches/
│  ├─ detail_decals/
│  └─ contact_shadows/
├─ godot/
│  ├─ metadata/
│  ├─ materials/
│  └─ scenes/
└─ preview/
   ├─ terrain-repeat-tests/
   └─ ground-composite-tests/
```

## Metadata

RD terrain metadata:

```json
{
  "asset_id": "terrain_earth_packed_a",
  "source": "retro_diffusion",
  "prompt_style": "rd_plus__textured",
  "size": { "width": 256, "height": 256 },
  "tile_x": true,
  "tile_y": true,
  "seed": 2026060901,
  "palette": "palettes/motgol-ground-palette.png",
  "godot": {
    "texture_repeat": true,
    "filter": "project_default",
    "z_index": -100
  }
}
```

GPT overlay metadata:

```json
{
  "asset_id": "path_main_curve_a",
  "source": "gpt_image",
  "canvas": { "width": 512, "height": 512 },
  "z_index": -90,
  "collision": false,
  "y_sort": false,
  "rotation_allowed": true,
  "scale_range": [0.9, 1.1],
  "edge_feather_px": 16
}
```

## Validation Gates

### RD Terrain

Every candidate must pass:

1. `4x4` repeat preview with no visible seams.
2. `8x8` repeat preview with no obvious periodic landmark.
3. Composite with a 128px character.
4. Composite with `building_hanok_small_a`.
5. Grayscale test: base terrain must be lower contrast than the building.
6. No isolated bright pixels that read as wet shine.

### GPT Path Patches

Every candidate must pass:

1. Clean alpha with no green fringe.
2. Two overlapping copies do not form a hard rectangular edge.
3. Straight-to-curve overlap looks acceptable.
4. No baked lighting direction.
5. No object-sized stones or props embedded in the road.

### Full Ground Composite

Create one `1536x1024` test composition containing:

- two RD base terrain variants;
- one main path;
- one courtyard patch;
- five detail decals;
- two building shadows;
- current Motgol buildings, market stall, and pine tree;
- one 128px character.

Approve only if:

- characters and buildings remain dominant;
- terrain styles do not look like separate asset packs;
- repetition is not obvious at normal camera zoom;
- no shadow conflicts with the scene lighting;
- path edges remain readable but not outlined.

## Execution Plan

### Phase 0: Palette

- Build `motgol-ground-palette.png` locally from accepted GPT assets.
- No paid generation.

### Phase 1: RD Style Probe

- One packed-earth prompt.
- Two images with `rd_fast__texture`.
- Two images with `rd_plus__textured`.
- Run `check_cost` first.
- Select one style before generating other terrain families.

Approximate formula-based cost at `256x256`, before exact `check_cost`:

- RD Fast: about `$0.028` per image.
- RD Plus: about `$0.058` per image.
- Four-image probe: about `$0.172` total.

### Phase 2: RD Initial Terrain Set

- Four terrain families.
- Two variants each.
- Eight images total.
- Generate repeat previews and reject weak candidates.

Approximate RD Plus cost:

- about `$0.46` for eight `256x256` images;
- exact amount must come from `check_cost`.

### Phase 3: GPT Path Kit

Generate:

- 2 straight paths
- 1 curve
- 1 T junction
- 1 crossroad
- 1 narrow trail
- 1 courtyard
- 1 building apron

Process:

- chroma removal
- despill
- crop/fixed canvas
- edge feather
- metadata

### Phase 4: GPT Detail Kit

Generate neutral decals first:

- mud
- straw
- pebbles
- cart tracks
- dry grass edge

Story decals come after the neutral map composition passes.

### Phase 5: Godot Composite Test

- Build one test scene.
- Test texture repetition, overlay placement, opacity, and z-order.
- Do not expand the asset set until this scene passes.

## 2026-06-09 Execution Result

### RD Terrain

- Palette created:
  `maps/village_kits/motgol/palettes/motgol-ground-palette.png`
- Style probes and recovery candidates preserved under:
  `maps/village_kits/motgol/generated/rd_terrain_raw/`
- RD Plus produced the best seamless packed-earth master, but repeated
  attempts at separate terrain families often produced borders, scenes, or
  oversized stones.
- Final accepted approach: derive a coherent eight-texture family from the
  accepted seamless master using deterministic local color and rotation
  variants.
- Final textures:
  `maps/village_kits/motgol/processed/terrain/normalized-base-v2/`
- Total RD spend: `$0.797`.
- Remaining RD balance after the run: `$8.560`.

### GPT Path Kit

- Eight path and yard overlays generated with built-in GPT Image.
- Chroma originals:
  `maps/village_kits/motgol/generated/gpt_ground_overlay_raw/`
- Final transparent assets:
  `maps/village_kits/motgol/processed/path_patches/`
- Godot metadata:
  `maps/village_kits/motgol/godot/metadata/path_patches/`
- Processing applied:
  chroma removal, despill, fixed canvas crop, matte color normalization,
  per-asset opacity reduction, and `20px` branch endpoint alpha fades.
- Review images:
  `maps/village_kits/motgol/preview/ground-overlay-tests/`

The path kit is suitable for irregular authored layouts, not exact
Wang-tile assembly. Use rotation and approximately `24px` overlap. The two
straight variants intentionally retain different surface detail, so avoid
alternating them every segment where the texture change would become a
visible pattern.

## Stop Conditions

Stop and revise the pipeline if:

- RD base terrain still looks visibly pixel-blocky next to GPT buildings;
- a 256px repeat is obvious at the normal camera zoom;
- palette transfer creates excessive dithering;
- GPT path patches look painted on rather than embedded in the ground;
- contact shadows introduce a second lighting direction.

If RD and GPT remain visually incompatible after palette and contrast normalization, use RD only as an underpainting and apply a common local color reduction/LUT pass to the final composite asset set.

## Official Godot References

- `CanvasItem.texture_repeat`: repeated sampling outside texture extents.
  - <https://docs.godotengine.org/en/stable/classes/class_canvasitem.html>
- `Polygon2D`: texture, UV, texture offset, rotation, and scale.
  - <https://docs.godotengine.org/en/stable/classes/class_polygon2d.html>
- `Sprite2D.region_enabled` and `region_rect`.
  - <https://docs.godotengine.org/en/stable/classes/class_sprite2d.html>
- `TileMapLayer`: tile rendering and y-sort origin where a tile grid is actually useful.
  - <https://docs.godotengine.org/en/stable/classes/class_tilemaplayer.html>
