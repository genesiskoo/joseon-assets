# PixelLab MCP Character Pipeline Findings

> Author: OpenAI Codex
>
> Updated: 2026-06-07

## Decision

PixelLab character generation uses `create_character` with `mode: "v3"` by
default. `standard` is reserved for cheap connection checks and rough
silhouette tests. `pro` requires an explicit cost review before ordering.

Default character preset:

```json
{
  "body_type": "humanoid",
  "mode": "v3",
  "size": 96,
  "outline": "selective outline",
  "detail": "high detail",
  "view": "high top-down"
}
```

The machine-readable copy is stored at
`production/presets/pixellab_character_v3.json`.

## Doho Test Results

| Test | Mode | Requested size | Output | Cost | Result |
|---|---|---:|---:|---:|---|
| Four-direction baseline | standard | 96 | 136x136 | 1 | Small figure and weak detail |
| High top-down baseline | standard | 96 | 136x136 | 1 | Better camera angle, but detail remained limited |
| Rectangular map object | object pipeline | 60x90 | 60x90 preview | - | Wrong model for production characters |
| Eight-direction character | v3 | 96 | 184x184 | 3 | Clearly better silhouette, costume detail, and direction consistency |

The strongest improvement came from changing the generation mode to `v3`.
Changing only the view or detail setting in `standard` did not close the
quality gap.

## V3 Behavior

- `v3` always generates eight directions.
- The tested `size: 96` request returned `184x184` canvases because PixelLab
  adds animation and alignment padding around the character.
- `high top-down` and `high detail` are accepted and useful.
- `n_directions`, `proportions`, `shading`, and `text_guidance_scale` are
  ignored by `v3`.
- `create_character` accepts one scalar `size`, so rectangular character
  canvases such as 60x90 cannot be requested directly.
- Do not infer in-game sprite size from the downloaded canvas size. Normalize
  and align approved output in the finishing step.

## GPT Image Reference Test

GPT Image produced a much stronger tall Doho design reference than the first
PixelLab `standard` result. It is useful for:

- locking costume, silhouette, materials, and palette;
- writing a more concrete PixelLab text prompt;
- visual review beside the PixelLab result;
- later manual cleanup and paint-over.

The current PixelLab MCP `create_character` schema does not expose a
`reference_image` input for `v3`. Therefore the reference is retained as a
design and review source, not silently uploaded through a separate REST path.
`create_8_direction_object` has a reference-image input, but it is a different,
more expensive object workflow and is not the default character pipeline.

## Operating Rules

1. Generate or select the approved character concept reference.
2. Extract concrete visual traits into the PixelLab prompt.
3. Order directly through PixelLab MCP using the v3 preset.
4. Download all eight directions into the order's `raw/` directory.
5. Review hat, weapon side, costume layers, palette, feet, and center point.
6. Normalize approved assets for the target Godot canvas.
7. Publish only through the manifest and publish tool.

Every order should record its PixelLab character ID, mode, cost, requested
size, actual canvas size, prompt, and review status in `brief.md`.
