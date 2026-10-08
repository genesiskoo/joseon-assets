# H1 icon packaging (#86)

Only packaging: preserve source RGBA, crop alpha bounding box, isotropically resize its longest side to 103px (integer rounding), center on a transparent 128×128 canvas. No background removal, chroma keying, painting, palette correction, or silhouette changes. Lanczos resampling uses premultiplied alpha to avoid edge halos.

## Input

`source_map.json` is a list, with one record per item:

```json
[
  {"id":"iron_sword", "name":"철검", "source":"sources/iron_sword.png", "prompt":"Exact generation prompt"}
]
```

Relative source paths resolve against the map's directory. Nonempty `name` and `prompt` are required. Duplicate/unknown ids fail before writing. IDs accepted:

`coin`, `cotton_belt`, `cotton_robe`, `hp_potion`, `hwando`, `ident_scroll`, `iron_sword`, `jade_charm`, `leather_armor`, `leather_shoes`, `long_sword`, `mp_potion`, `quilted_robe`, `silver_ring`, `straw_shoes`, `town_portal`, `wooden_sword`.

## Run

```powershell
python tmp/icons_h1_86/package_icons.py tmp/icons_h1_86/source_map.json --repo C:/workspace/joseon
python tmp/icons_h1_86/package_icons.py tmp/icons_h1_86/source_map.json --complete --repo C:/workspace/joseon
```

Pillow is required. Default output is `output/` next to the map. Override with `--output <folder>`. `--complete` requires exactly the 17 IDs; otherwise partial batches are allowed. `--repo` adds old icon thumbnails by resolving `icon = ExtResource(...)` in the matching `data/items/<id>.tres`.

## Outputs and gates

- `output/<id>.png`: native 128px RGBA.
- `output/manifest.json`: exact prompt, source/output SHA256, dimensions, alpha histogram counts, alpha bounding boxes, padding in left/top/right/bottom order, and slot-safe bounds. Bboxes use exclusive right/bottom coordinates. Valid outputs fit `[12,12,116,116]`.
- `output/contact_icons_h1.png`: labeled 4-column grid, native 128px tiles on dark/light backgrounds, 32px and 40px previews on both backgrounds, optional old 40px thumbnail. Preview images never replace production output.

Source rejected and **not processed** if it has no alpha channel, alpha extrema are not exactly `[0,255]`, or alpha bbox spans ≥98% of both dimensions with ≥95% opaque coverage of that bbox. The rejection is recorded under `rejected_sources`, printed with `STOP source`, and exits with code 2 after packaging other valid sources. No background removal is attempted. This numeric gate cannot distinguish a painted checkerboard surrounded by transparent padding; parent must visually inspect every generated source and contact sheet.

Only `manifest.items` are current successful outputs. Use a fresh output directory for each batch, because old files in reused output directories are intentionally not deleted. `manifest.complete` is true only with all 17 successful outputs and no rejection. Invalid complete maps fail immediately before producing a manifest.
