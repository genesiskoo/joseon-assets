# Godot GPT Image Village Kit Plan

Date: 2026-06-09

Purpose:

- Build a Joseon-era village map in Godot using high-quality GPT Image generated assets.
- Prefer GPT Image for unique large buildings and visual-rich landmarks.
- Keep the assets usable in Godot through transparent PNG cleanup, y-sort anchors, collision footprints, and optional roof/body splits.

## Core Decision

Use GPT Image as a high-quality one-off asset generator, not as a strict tileset generator.

Recommended split:

- Ground and roads: tilemap or reusable ground patches.
- Large buildings: GPT Image whole sprites, cleaned and anchored.
- Landmark buildings: GPT Image whole sprites, optionally split into body and roof occluder.
- Small props: GPT Image or PixelLab, depending on consistency needs.
- Collision, navigation, and y-sort: authored in Godot, not trusted from the image.

## Godot Scene Structure

Recommended village scene:

```text
MotgolVillage.tscn
└─ Node2D VillageRoot
   ├─ TileMapLayer Ground
   ├─ TileMapLayer Roads
   ├─ Node2D Decals
   ├─ Node2D YSortedWorld        # y_sort_enabled = true
   │  ├─ Building_Magistrate_A
   │  ├─ Building_Hanok_A
   │  ├─ Prop_Jangseung_A
   │  ├─ Prop_MarketStall_A
   │  └─ CharacterRoot
   ├─ Node2D ForegroundOccluders # optional
   ├─ NavigationRegion2D
   └─ CanvasLayer UI
```

Recommended building scene:

```text
Building_Magistrate_A.tscn
└─ Node2D BuildingRoot           # position = y-sort anchor on map
   ├─ Sprite2D Shadow            # optional, z_index = -10
   ├─ Sprite2D Body              # centered = false, position = -anchor_px
   ├─ Sprite2D RoofOccluder      # optional, centered = false, position = -anchor_px
   ├─ StaticBody2D Collision
   │  └─ CollisionPolygon2D
   └─ Area2D InteractionArea     # optional
```

For simple buildings, one `Sprite2D Body` is enough.

For buildings where the player can walk behind eaves, under gates, or near a front porch, split into:

- `Body`: lower walls, foundation, doors, stairs.
- `RoofOccluder`: roof and overhanging eaves that should cover the character.

## Y-Sort Rule

Every large object needs a stable anchor point.

Use this convention:

- Asset canvas: usually `512x512` or `400x400`.
- Anchor: bottom-center of the visible footprint, not image center.
- Godot root node position: world coordinate of that anchor.
- Sprite2D:
  - `centered = false`
  - `position = Vector2(-anchor_x, -anchor_y)`

Example metadata:

```json
{
  "asset_id": "building_magistrate_a",
  "canvas": { "width": 512, "height": 512 },
  "anchor_px": { "x": 256, "y": 438 },
  "sort_mode": "root_y",
  "collision": "footprint_only",
  "roof_split": true
}
```

Practical sorting behavior:

- Character y < building anchor y: character is behind the building.
- Character y > building anchor y: character is in front of the building.
- Do not place the anchor at the center of the sprite; large roofs will sort incorrectly.

## Collision Rule

Do not use the full image rectangle as collision.

Use only the footprint:

- walls at ground level
- foundation
- posts
- closed doors
- stone steps if not walkable

Do not include:

- roof area
- upper eaves
- decorative overhangs
- empty transparent padding

For a large hanok, the collision shape is usually a shallow polygon near the bottom half of the sprite.

## Asset Canvas Sizes

Use fixed canvases so Godot import and placement stay predictable.

| Asset Type | Canvas | Notes |
|---|---:|---|
| Landmark building | `512x512` | Magistrate office, shrine, dungeon gate |
| Large house | `400x400` or `512x512` | Long hanok, inn, noble house |
| Small house | `256x256` | Common house, shed |
| Gate / wall segment | `256x256` | Gate can be split for pass-through |
| Tree / large rock | `256x256` | Needs y-sort anchor |
| Small prop | `128x128` | Jars, crates, tools |
| Tiny prop | `64x64` | Stones, paper scraps, small markers |
| Ground decal | `256x256` | Transparent dirt, straw, stains |

For GPT Image, generate larger than final when possible, then downscale/crop locally.

## Minimum Village Kit

This is the first practical kit for one Joseon village.

### Buildings

| ID | Asset | Canvas | Use |
|---|---:|---:|---|
| `building_hanok_small_a` | small common hanok | `256x256` | repeated houses |
| `building_hanok_small_b` | small thatched house | `256x256` | poor village edge |
| `building_hanok_long_a` | long hanok row | `400x400` | street side |
| `building_inn_a` | tavern / guesthouse | `512x512` | village hub |
| `building_mudang_house_a` | shaman house | `400x400` | story area |
| `building_magistrate_a` | government office | `512x512` | landmark |
| `building_shrine_a` | small shrine / spirit hall | `400x400` | ritual area |
| `building_storehouse_a` | wooden storehouse | `256x256` | filler |

### Boundaries

| ID | Asset | Canvas | Notes |
|---|---:|---:|---|
| `wall_stone_straight_a` | low stone wall straight | `128x128` | repeatable |
| `wall_stone_corner_a` | low stone wall corner | `128x128` | corner module |
| `wall_wood_fence_a` | rough wooden fence | `128x128` | village edge |
| `gate_village_a` | wooden village gate | `256x256` | can split upper beam |
| `gate_compound_a` | hanok compound gate | `256x256` | pass-through needs occluder |

### Props

| ID | Asset | Canvas |
|---|---:|---:|
| `prop_jangseung_a` | village guardian totem | `128x128` |
| `prop_onggi_cluster_a` | clay jar cluster | `128x128` |
| `prop_market_stall_a` | cloth market stall | `256x256` |
| `prop_handcart_a` | wooden handcart | `128x128` |
| `prop_firewood_stack_a` | firewood stack | `128x128` |
| `prop_well_a` | village well | `128x128` |
| `prop_talisman_rope_a` | rope with talismans | `128x128` |
| `prop_stone_lantern_a` | stone lantern | `128x128` |

### Vegetation

| ID | Asset | Canvas | Notes |
|---|---:|---:|---|
| `tree_pine_a` | crooked pine tree | `256x256` | split trunk/foliage if needed |
| `tree_dead_a` | dead branch tree | `256x256` | foreground occluder |
| `bush_dry_a` | dry bush | `128x128` | filler |
| `grass_clump_a` | dead grass clump | `64x64` | decal/prop |

### Ground Decals

Ground should not rely only on GPT whole images. Use decals over a base tilemap.

| ID | Asset | Canvas |
|---|---:|---:|
| `decal_mud_patch_a` | dark mud patch | `256x256` |
| `decal_straw_scatter_a` | scattered straw | `128x128` |
| `decal_pebbles_a` | dull pebbles | `128x128` |
| `decal_talisman_scraps_a` | old paper scraps | `128x128` |
| `decal_shadow_under_eaves_a` | soft building contact shadow | `256x256` |

## Prompt Template: Whole Building

Use this for unique buildings.

```text
Use case: stylized-concept
Asset type: Godot 2D map building sprite
Primary request: one [BUILDING TYPE], Joseon-era Korean village, high top-down game asset
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background only, no ground plane
Subject: [specific building description], full object visible, readable footprint, no characters
Style/medium: matte pixel-art-inspired 2D game asset, clean silhouette, desaturated brown and dark grey palette
Composition/framing: isolated centered object, high top-down view, generous transparent-ready padding
Lighting/mood: soft diffuse overcast lighting, low contrast flat shading
Constraints: background must be one uniform #00ff00 color; do not use #00ff00 in the subject; no text; no watermark
Avoid: glossy highlights, specular highlights, shiny roof, white rim light, glowing edges, bloom, backlight, cast shadow on the green background, realistic material rendering
```

## Prompt Template: Pass-Through Gate

Use for gates where the player may walk under the roof beam.

```text
one Joseon-era Korean wooden compound gate, high top-down Godot 2D game asset,
clear open passage under the gate, visible side posts, dark giwa roof,
perfectly flat solid #00ff00 chroma-key background only,
matte pixel-art-inspired style, desaturated brown grey palette,
soft diffuse overcast lighting, low contrast flat shading,
no characters, no text, no watermark,
no glossy highlights, no specular highlights, no white rim light, no glowing edges, no bloom
```

Postprocess this into:

- `gate_body.png`: posts and lower collision parts.
- `gate_roof_occluder.png`: roof beam and eaves.

## Prompt Template: Prop

```text
one [PROP NAME], Joseon-era Korean village prop, high top-down 2D game asset,
perfectly flat solid #00ff00 chroma-key background only,
isolated centered object, generous padding,
matte pixel-art-inspired style, desaturated earthy palette,
soft diffuse lighting, low contrast,
no characters, no text, no watermark,
no glossy highlights, no specular highlights, no rim light, no bloom
```

## Processing Pipeline

1. Generate raw image on flat `#00ff00`.
2. Save raw image in `generated/raw/`.
3. Remove chroma key and despill green edges.
4. Crop to visible bounding box.
5. Place on fixed canvas: `64`, `128`, `256`, `400`, or `512`.
6. Record anchor metadata.
7. Split roof/body only when gameplay needs occlusion.
8. Draw collision footprint in Godot.
9. Add asset scene to the village kit.

Recommended folders:

```text
maps/village_kits/motgol/
├─ generated/
│  ├─ raw/
│  └─ rejected/
├─ processed/
│  ├─ buildings/
│  ├─ props/
│  ├─ vegetation/
│  ├─ decals/
│  └─ occluders/
├─ godot/
│  ├─ scenes/
│  └─ metadata/
└─ README.md
```

## Godot Import Settings

For pixel-art-style assets:

- Filter: disabled / nearest
- Mipmaps: disabled
- Repeat: disabled
- Compression: lossless

For painterly high-resolution landmark assets:

- Filter can be enabled if the final game uses smooth high-res art.
- Keep all assets in the same filtering style inside one map.
- Avoid mixing nearest pixel props with smooth GPT buildings unless intentionally stylized.

## Suggested Godot Asset Script

Use a small script or convention to apply anchor offsets consistently.

```gdscript
@tool
extends Node2D

@export var anchor_px := Vector2(256, 438)
@export var body: Sprite2D
@export var roof_occluder: Sprite2D
@export var shadow: Sprite2D

func _ready() -> void:
    _apply_anchor()

func _apply_anchor() -> void:
    for sprite in [body, roof_occluder, shadow]:
        if sprite:
            sprite.centered = false
            sprite.position = -anchor_px
```

## Production Notes

- GPT whole buildings are good for unique, non-reused landmarks.
- The more a building must repeat, the more it should be broken into modules.
- For village production, use GPT for visual quality and Godot for structure.
- Do not let the generated image decide collision or sort order.
- Always keep raw, processed, and Godot-ready versions separate.
- Keep one metadata file per asset so anchors and collisions are reproducible.

## First Batch Recommendation

Generate these first:

1. `building_magistrate_a` - landmark quality test.
2. `building_hanok_small_a` - common reusable house.
3. `building_mudang_house_a` - story area building.
4. `gate_compound_a` - roof/body split test.
5. `prop_market_stall_a` - medium prop test.
6. `tree_pine_a` - y-sort vegetation test.
7. `decal_shadow_under_eaves_a` - contact shadow test.

If these seven work in Godot, expand to the full kit.
