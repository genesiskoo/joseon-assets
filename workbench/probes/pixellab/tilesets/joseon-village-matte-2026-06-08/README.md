# Joseon Village Matte PixelLab Tilesets

Date: 2026-06-08

Purpose:

- PixelLab top-down Wang tileset probes for a dark Joseon-era village map.
- Avoid the glossy / rim-lit look seen in GPT Image 2 concept outputs.
- 32px tiles for high top-down map construction around 128px characters.

Common constraints:

- high top-down
- 32x32 tiles
- matte flat pixel art
- overcast diffuse light
- low contrast
- no white edge lines
- no highlights
- no shine
- no rim light

## Files

### 01 Packed Earth To Stone Courtyard

- PixelLab ID: `8005eb68-b533-4cb6-9b4e-ab56a220ecd1`
- Style: `selective outline`, `basic shading`, `low detail`
- PNG: `01-packed-earth-to-stone-courtyard-32.png`
- Preview: `01-packed-earth-to-stone-courtyard-32-preview-4x.png`
- Lower base tile ID: `e11630a0-b981-4b8b-b8b2-9a5ffe74afaa`
- Upper base tile ID: `af5c8da8-4fb2-4e18-806a-8a468c4d5fe2`
- Note: readable, but bright transition outlines can read like rim light.

### 02 Packed Earth To Stone Courtyard Lineless Flat

- PixelLab ID: `312293c3-131c-421c-b5b4-f070bd55b1ec`
- Style: `lineless`, `flat shading`, `low detail`
- PNG: `02-packed-earth-to-stone-courtyard-32-lineless-flat.png`
- Preview: `02-packed-earth-to-stone-courtyard-32-lineless-flat-preview-4x.png`
- Lower base tile ID: `dfddadce-e23e-40e2-af9c-472bd8f049a4`
- Upper base tile ID: `bd6d984e-837d-4334-b774-2b32d370ffbc`
- Note: best raw PixelLab stone-yard candidate, but stone highlights are still a bit bright.

### 02 Muted Postprocess

- Source: `02-packed-earth-to-stone-courtyard-32-lineless-flat.png`
- PNG: `02-packed-earth-to-stone-courtyard-32-lineless-flat-muted.png`
- Preview: `02-packed-earth-to-stone-courtyard-32-lineless-flat-muted-preview-4x.png`
- Note: recommended current-use candidate. Bright pixels were locally reduced while preserving tile layout.

### 03 Packed Earth To Dry Grass

- PixelLab ID: `abc51f23-302f-49f6-b0f6-b9ee029010cc`
- Style: `lineless`, `flat shading`, `low detail`
- PNG: `03-packed-earth-to-dry-grass-32-lineless-flat.png`
- Preview: `03-packed-earth-to-dry-grass-32-lineless-flat-preview-4x.png`
- Lower base tile ID: `dfddadce-e23e-40e2-af9c-472bd8f049a4`
- Upper base tile ID: `b95adb93-6ad5-4fd0-ba80-376caa6aad5c`
- Note: too yellow and bright for the current dark village mood.

### 04 Night Earth To Olive Yard

- PixelLab ID: `2f8621dd-d8e3-4267-b68d-cc250e58e37a`
- Style: `lineless`, `flat shading`, `low detail`
- PNG: `04-night-earth-to-olive-yard-32-lineless-flat.png`
- Preview: `04-night-earth-to-olive-yard-32-lineless-flat-preview-4x.png`
- Lower base tile ID: `e5f79b70-e73c-449b-adb7-4b5b9a6c9a9c`
- Upper base tile ID: `c93bc2c6-1155-4847-8478-6e27a744b8a1`
- Note: darker palette, but yellow-green transition pixels remain too visible.

## Recommendation

Use `02-packed-earth-to-stone-courtyard-32-lineless-flat-muted.png` as the current map-production candidate.

For additional connected tilesets, chain from:

- lower earth base: `dfddadce-e23e-40e2-af9c-472bd8f049a4`
- stone courtyard base: `bd6d984e-837d-4334-b774-2b32d370ffbc`

Suggested next terrains:

- packed earth -> dark mud alley
- packed earth -> hanok wooden porch floor
- stone courtyard -> shrine courtyard stone
- stone courtyard -> broken dungeon threshold

Comparison sheet:

- `comparison-preview-4x-grid.png`
