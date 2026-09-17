# GPT Image 2 Map Tests

Generated with the built-in `image_gen` workflow on 2026-06-07.

## Shared map requirements

- Oblique high top-down pixel-art environment concept for an action RPG.
- Layout and architecture scaled for a player character rendered about
  128 pixels tall.
- Main routes are roughly 3-4 character widths; narrow routes remain at least
  1.5-2 character widths.
- Clear entrances, loops, chokepoints, shortcuts, combat spaces, landmarks,
  elevation, and collision-friendly boundaries.
- Premium 32-bit pixel art with deliberate pixel clusters and readable value
  grouping.
- No labels, UI, grid lines, logo, watermark, modern objects, or non-Korean
  architectural motifs.

## Map variants

1. `village-riverside-market.png`
   - Prosperous late-Joseon riverside village in early autumn.
   - Central market combat square, two looping side streets, three exits,
     alleys, courtyards, blacksmith, jangseung, stream, bridge, and rice fields.
   - Warm late-afternoon light and an approachable everyday-life mood.
2. `village-mountain-fortress.png`
   - Remote mountain fortress village on three ascending tiers.
   - Lower trade yard, central training plaza, upper command courtyard,
     wall loop, two gates, concealed cave exit, ramps, stairs, and shortcuts.
   - Cold post-rain dawn, blue mountain mist, and warm torch accents.
3. `dungeon-royal-tomb.png`
   - Haunted underground royal tomb beneath a ruined late-Joseon palace.
   - Entrance hall, two reconnecting puzzle branches, flooded chamber, trap
     corridor, ritual hub, side rooms, shortcut gate, and deep boss chamber.
   - Indigo-charcoal-jade palette with blue ghost fire and vermilion talismans.
4. `dungeon-dokkaebi-ritual-cave.png`
   - Mountain cavern containing a hidden Joseon-era shaman sanctuary.
   - Entrance canyon, central ritual arena, two elevated side loops, lower
     river route, optional alcoves, bridges, shortcut, and circular boss arena.
   - Teal spectral light, underground water, granite, roots, ropes, drums, and
     a cracked stone-mask altar.

## High top-down gameplay crop

### `village-market-high-topdown-matte-v2.png`

- Style and camera reference:
  `ig_06fca7360c32cc73016a256bcc29d0819183e0e2cf9cdb8c65.png`
- True high top-down camera at roughly 70-75 degrees, nearly orthographic,
  with no horizon and no isometric diamond projection.
- One local village gameplay screen instead of a full settlement overview.
- Broad packed-earth junction, cropped modular hanok buildings, low stone
  walls, market props, a persimmon tree, an irrigation stream, and one bridge.
- Open routes sized for a 128px-tall player sprite; no characters in the image.
- Modular construction language: repeating terrain, wall, fence, roof, gate,
  and bridge pieces with independent map-object props.

Lighting block:

```text
One soft warm directional light from the upper left with weak ambient fill.
Mostly matte, high-roughness surfaces. Use broad quiet value groups instead
of scattered sharp highlights. Roof tile, stone, wood, cloth, soil, foliage,
and pottery remain matte. Reserve the brightest values for a few sun-facing
edges and the stream only. No rim lighting, no edge sparkle on rocks or roof
tiles, no glossy coating, no bloom, no wet-looking ground, and no repeated
white highlight dots.
```

### `village-market-high-topdown-matte-v3.png`

- Same high top-down village target and modular construction language as v2.
- Tested the shorter suppression phrases commonly used in image prompts.
- Central gameplay area remains open and contains no characters.

Suppression block:

```text
matte lighting
soft diffuse lighting
minimal specular highlights
low contrast shading
matte finish
avoid glossy surfaces
avoid plastic-looking materials
avoid over-rendered reflections
subtle rim light only
no shiny roof tiles
no shiny stone
no shiny pottery
no decorative white reflection dots
no edge sparkle on rocks or roof tiles
no bloom
no glowing edges
no excessive reflections
```

Result note:

- Global contrast and glossy material response were reduced.
- Repeated bright pixels remained on some roof-tile ends and stream rocks.
- Future iterations should constrain roof and rock highlight colors at the
  palette level rather than relying only on general lighting adjectives.
