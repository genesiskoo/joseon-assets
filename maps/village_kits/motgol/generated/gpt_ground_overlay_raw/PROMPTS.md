# Motgol GPT Ground Overlay Prompts

Date: 2026-06-09

Tool: built-in GPT Image

## Shared Prompt

```text
Use case: stylized-concept
Asset type: Godot 2D ground overlay
Primary request: Create one [SHAPE] packed-earth path patch for a
Joseon-era village in strict high top-down orthographic view. Match the
Motgol base terrain's dark muted brown-grey palette.
Scene/backdrop: perfectly flat uniform solid #00ff00 chroma-key
background only, with no floor plane, texture, gradient, shadow, or
lighting variation.
Subject: compacted earth with restrained fine gravel and worn soil
detail, an organically irregular edge, and no focal object.
Style/medium: matte pixel-art-inspired 2D game decal, simplified,
desaturated, low contrast.
Lighting/mood: flat neutral diffuse ambient light, matte finish.
Constraints: isolated ground patch only; no characters, buildings,
vegetation, props, grass border, text, watermark, or hard rectangular
outline; do not use #00ff00 inside the patch.
Avoid: glossy or wet ground, shiny stones, specular highlights, rim
light, bloom, cast shadows, contact shadows, over-rendered reflections,
strong bevels, large rocks, and scene illustration.
```

## Shape Variants

| Asset ID | Shape Instruction |
|---|---|
| `path_main_straight_a` | Wide horizontal main road reaching the left and right canvas edges. |
| `path_main_straight_b` | Alternate uneven horizontal road with sparse dull pebble clusters, reaching left and right. |
| `path_main_curve_a` | Broad 90-degree curve entering from bottom and exiting right. |
| `path_main_tjunction_a` | T junction opening at left, right, and bottom; closed at top. |
| `path_main_cross_a` | Four-way intersection opening through all four canvas edges. |
| `path_narrow_trail_a` | Slim slightly meandering foot trail reaching top and bottom. |
| `path_courtyard_patch_a` | Fully contained irregular open courtyard with green padding on every side. |
| `path_building_apron_a` | Fully contained wide shallow entrance wear patch with tapered ends. |

## Post-processing

- Chroma removal with soft matte, despill, and one-pixel edge contract.
- Fixed output canvases of `512x512`, `512x256`, or `256x512`.
- Shared low-saturation brown-grey color normalization.
- `20px` alpha fade at connected branch endpoints.
- Approximately `24px` overlap in Godot.
