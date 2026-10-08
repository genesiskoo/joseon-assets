# GPT Image 2 Style Tests

Generated with the built-in `image_gen` workflow on 2026-06-07.

## Shared concept

- Landscape key visual for a Korean historical dark-fantasy game.
- One late-Joseon Korean female monster hunter in a dark indigo combat-adapted
  durumagi, holding a hwando and paper talismans.
- One towering horned dokkaebi emerging from blue ghost fire.
- Ruined late-Joseon palace courtyard under a full moon.
- Hunter in the lower-left and dokkaebi in the upper-right.
- No text, logo, watermark, UI, modern objects, Japanese motifs, or generic
  Chinese fantasy armor.

## Style variants

1. `joseon-hunter-16bit-action-rpg.png`
   - Authentic 16-bit action RPG pixel art, crisp pixel clusters, 24-color
     palette, one-pixel dark outlines, strong silhouettes.
2. `joseon-hunter-minhwa-pixel-art.png`
   - Joseon minhwa-inspired pixel art, flattened perspective, decorative
     contours, folk-painting geometry, restrained obangsaek palette.
3. `joseon-hunter-sumukhwa.png`
   - Korean sumuk-damchae on aged hanji, expressive ink, broad negative space,
     restrained indigo, pale blue, and vermilion washes.
4. `joseon-hunter-woodblock-print.png`
   - Hand-carved Korean woodblock print, coarse black key lines, visible gouge
     texture, uneven ink pressure, limited four-ink palette.
5. `joseon-hunter-hd2d.png`
   - HD-2D presentation with pixel-art figures and architecture, layered depth,
     volumetric moonlight, particles, fog, and restrained reflections.
6. `joseon-hunter-cel-animation.png`
   - Hand-drawn cel-animation key visual, precise line art, two-to-three-tone
     cel shading, painted background, dynamic cloth and spectral fire.

## i2v Motion Previews (2026-06-09)

i2v generated from the style test images to preview how each artistic style would handle subtle cinematic animation. Prompts reuse the shared concept and style-specific details, with very slow camera push-in and style-appropriate secondary motion (wind on talismans/cloth, fire/ink shifts, limited pixel steps, etc.). 6s @ 720p. These serve as motion references for further calibration or PixelLab animation planning. One (cel-animation) hit a temporary rate limit and was retried.

### 16bit-action-rpg
- File: joseon-hunter-16bit-action-rpg_i2v_6s_720p.mp4
- Source: joseon-hunter-16bit-action-rpg.png

**Prompt used:**
"Landscape key visual in authentic 16-bit action RPG pixel art style for a Korean historical dark-fantasy game. Late-Joseon female monster hunter in dark indigo combat-adapted durumagi holding hwando and paper talismans in lower left. Towering horned dokkaebi emerging from blue ghost fire in upper right. Ruined late-Joseon palace courtyard under full moon. Crisp pixel clusters, 24-color palette, strong silhouettes. Very slow smooth camera push-in from wide establishing shot, subtle wind moving talismans and fabric in pixel steps, dokkaebi fire flickers with limited animation, atmospheric moonlit mood. Present tense, minimal but readable motion suitable for pixel style reference. Clear strong silhouettes."

### cel-animation
- File: joseon-hunter-cel-animation_i2v_6s_720p.mp4 (retried after rate limit)
- Source: joseon-hunter-cel-animation.png

**Prompt used:**
"Landscape key visual in hand-drawn cel-animation style for a Korean historical dark-fantasy game. Late-Joseon female monster hunter in dark indigo combat-adapted durumagi holding hwando and paper talismans in lower left. Towering horned dokkaebi emerging from blue ghost fire in upper right. Ruined late-Joseon palace courtyard under full moon. Precise line art, two-to-three-tone cel shading, painted background, dynamic cloth and spectral fire. Very slow smooth camera push-in, subtle wind on hunter's clothing and talismans, dokkaebi's fire and form shifts dynamically but restrained, atmospheric moonlit mood. Present tense, minimal but living motion. Clear readable silhouettes."

### hd2d
- File: joseon-hunter-hd2d_i2v_6s_720p.mp4
- Source: joseon-hunter-hd2d.png

**Prompt used:**
"Landscape key visual in HD-2D style for a Korean historical dark-fantasy game. Late-Joseon female monster hunter in dark indigo combat-adapted durumagi holding hwando and paper talismans in lower left. Towering horned dokkaebi emerging from blue ghost fire in upper right. Ruined late-Joseon palace courtyard under full moon. Pixel-art figures with layered depth, volumetric moonlight, particles, fog, restrained reflections. Very slow smooth camera push-in with parallax on layers, subtle wind on clothing and talismans, dokkaebi fire and mist move atmospherically, atmospheric moonlit mood. Present tense, minimal but living motion. Clear readable silhouettes."

### minhwa-pixel-art
- File: joseon-hunter-minhwa-pixel-art_i2v_6s_720p.mp4
- Source: joseon-hunter-minhwa-pixel-art.png

**Prompt used:**
"Landscape key visual in Joseon minhwa-inspired pixel art style for a Korean historical dark-fantasy game. Late-Joseon female monster hunter in dark indigo combat-adapted durumagi holding hwando and paper talismans in lower left. Towering horned dokkaebi emerging from blue ghost fire in upper right. Ruined late-Joseon palace courtyard under full moon. Flattened perspective, decorative contours, folk-painting geometry, restrained obangsaek palette. Very slow smooth camera push-in, subtle wind on talismans and fabric in stylized steps, dokkaebi fire flickers decoratively, atmospheric moonlit mood. Present tense, minimal but readable motion suitable for folk pixel style reference. Clear strong silhouettes."

### sumukhwa
- File: joseon-hunter-sumukhwa_i2v_6s_720p.mp4
- Source: joseon-hunter-sumukhwa.png

**Prompt used:**
"Landscape key visual in Korean sumuk-damchae ink painting style on aged hanji for a Korean historical dark-fantasy game. Late-Joseon female monster hunter in dark indigo combat-adapted durumagi holding hwando and paper talismans in lower left. Towering horned dokkaebi emerging from blue ghost fire in upper right. Ruined late-Joseon palace courtyard under full moon. Expressive ink, broad negative space, restrained indigo, pale blue, and vermilion washes. Very slow smooth camera push-in with ink-like subtle shifts, wind on clothing and talismans as soft ink movement, dokkaebi fire and form drift like ink wash, atmospheric moonlit mood. Present tense, minimal but living motion suitable for sumukhwa style reference. Clear readable silhouettes."

### woodblock-print
- File: joseon-hunter-woodblock-print_i2v_6s_720p.mp4
- Source: joseon-hunter-woodblock-print.png

**Prompt used:**
"Landscape key visual in hand-carved Korean woodblock print style for a Korean historical dark-fantasy game. Late-Joseon female monster hunter in dark indigo combat-adapted durumagi holding hwando and paper talismans in lower left. Towering horned dokkaebi emerging from blue ghost fire in upper right. Ruined late-Joseon palace courtyard under full moon. Coarse black key lines, visible gouge texture, uneven ink pressure, limited four-ink palette. Very slow smooth camera push-in with woodblock-like subtle shifts, wind on talismans and fabric as carved line movement, dokkaebi fire and form with textured ink drift, atmospheric moonlit mood. Present tense, minimal but readable motion suitable for woodblock style reference. Clear strong silhouettes."

These i2v previews can help decide which styles best support subtle animation for key visuals or further production (e.g. cel and hd2d may offer more dynamic secondary motion while pixel/ink styles stay more restrained). Videos copied alongside sources for easy comparison.
