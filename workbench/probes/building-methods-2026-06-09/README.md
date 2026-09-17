# 400px Joseon Building Method Comparison

Date: 2026-06-09

Goal:

- Test two production approaches for a large high-top-down Joseon-era building.
- Target use: Unity/Godot map object or prefab around a 400px canvas.

## Method A: PixelLab Assembly

Folder:

- `pixellab-assembled/`

PixelLab tool:

- `create_map_object`
- `view`: `high top-down`
- `outline`: `lineless`
- `shading`: `flat shading`
- `detail`: `low detail`
- component size: `160-256px`

Generated component IDs:

- `685fdede-eddf-4c91-b0d7-e6a69e14db1a`: left roof-end prompt, saved as `part-01-roof-left-160.png`
- `337a5ea1-5739-4fe9-bb0f-83f3483732aa`: center roof prompt, saved as `part-02-roof-center-192.png`
- `f940f45b-3947-4129-957e-b9797da59ca5`: right roof-end prompt, saved as `part-03-roof-right-160.png`
- `6256bec5-2cd2-4ad6-a31e-7408d5f67e71`: body/foundation prompt, saved as `part-04-body-foundation-256.png`
- `1f1299ee-cdf5-47be-b853-8bf5a3cc4712`: porch/stair prompt, saved as `part-05-porch-stair-192.png`

Assembly outputs:

- `pixellab-assembled-400.png`
  - 400x400 transparent canvas.
  - Made by 9-slice/repeating `part-04-body-foundation-256.png`.
  - Best demonstration of how a 256px source can become a wider building.
- `pixellab-assembled-400-prefab-parts.png`
  - Uses multiple generated parts as separate prefab-like child sprites.
  - Shows the Unity/Godot scene assembly approach, but the parts do not connect cleanly.
- `pixellab-assembled-400-compound.png`
  - Current representative PixelLab assembly result.
  - Combines a repeated long front building with a central rear hall.

Notes:

- PixelLab did not strictly obey "roof module" or "wall module"; several parts came back as complete small buildings.
- For real production, create simpler repeatable modules: roof strip, roof end cap, wall bay, door bay, stone stair, porch plank.
- The assembled result is easier to edit, collide, layer, and reuse than a single generated image.

## Method B: GPT Image Whole Sprite

Folder:

- `gpt-image-whole/`

Built-in image generation prompt:

```text
one large Joseon-era Korean magistrate office building, high top-down game asset,
perfectly flat #00ff00 chroma-key background, wide dark giwa tile-roof government office,
raised wooden body, paper windows, central doorway, low stone steps,
matte pixel-art-inspired 2D game asset, desaturated brown and dark grey palette,
soft diffuse overcast lighting, low contrast flat shading,
no glossy highlights, no specular highlights, no shiny roof, no white rim light,
no glowing edges, no bloom, no backlight
```

Outputs:

- `gpt-whole-green-source.png`
  - Original generated image with green background.
- `gpt-whole-400-transparent.png`
  - First chroma-key removal and 400x400 fit.
- `gpt-whole-400-transparent-clean.png`
  - Recommended whole-sprite candidate.
  - More aggressive green removal and despill.

Notes:

- GPT Image produced a more coherent and impressive building silhouette.
- It still produced more fine roof detail and subtle highlight density than the PixelLab result.
- Chroma-key removal left green edge pixels on the first pass; the clean version reduces that.
- This method is best for unique landmarks or concept-to-final placeholders, not modular map production.

## Comparisons

- `comparison-pixellab-assembly-vs-gpt-whole.png`
  - Early 9-slice PixelLab assembly vs GPT whole.
- `comparison-prefab-parts-vs-gpt-whole-clean.png`
  - Multi-part prefab layout vs cleaned GPT whole.
- `comparison-compound-assembly-vs-gpt-whole-clean.png`
  - Current representative comparison.

## Practical Conclusion

Use PixelLab assembly when:

- the building must be reusable or configurable;
- collision, occlusion, and sorting need to be clean;
- the same roof/wall/door parts will appear across many maps;
- the building must fit a tile-grid workflow.

Use GPT whole sprite when:

- the building is a unique landmark;
- fast visual direction matters more than modularity;
- the asset will be manually cleaned or repainted afterward;
- the final game object can tolerate being one large sprite.

Recommended next PixelLab prompt strategy:

- Ask for very small, literal parts, not architectural concepts.
- Better: `32x96 dark giwa roof repeat strip`, `64x96 left roof cap`, `64x96 right roof cap`, `64x64 paper window wall bay`, `64x64 central wooden door bay`.
- Avoid words like `large building`, `magistrate office`, or `gatehouse` when generating individual modules; those words cause PixelLab to complete the whole building.
