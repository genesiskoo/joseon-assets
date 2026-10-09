# #671 백지 부적 아이콘 후보 A

- Tool: Codex built-in image_gen; exact model version not exposed.
- Reference: game icons_a/items/talisman_fire.png, material/shape only.
- Status: **PD adopted 2026-10-09** (judgment board 34 「합쳐」). Game intake = `assets/sprites/ui/icons_a/items/blank_talisman.png` (alpha>40 crop, content 75%, LANCZOS 80×80) wired to `data/items/blank_talisman.tres` — lands with #670+#671.
- Source: 851097 bytes; SHA256 62ABAFF6DB3CC509721A48EED10A0A2032F2EA24558595C0D6439E2DC6D0B6A1.

## Exact generation prompt

Create a transparent-background inventory item icon for the dark Joseon fantasy ARPG Joseon Hunters: ONE completely BLANK traditional Korean talisman paper sheet, used as stackable ammunition before writing spells. Use the attached old fire talisman ONLY as a reference for its object shape and worn hand-painted ARPG material style. A narrow ochre ivory handmade mulberry-paper rectangle tilted slightly clockwise in three-quarter view, curled worn corners, sparse fiber texture, dark warm thin edges, strong compact silhouette and clean readable center, restrained aged-paper highlights, entirely EMPTY front surface. Show only a single sheet, NOT a fan or pile. Full paper fits inside a square canvas with generous transparent margin. Opaque paper with genuinely transparent background. No writing, no Chinese characters, no Korean characters, no red ink, no stamps, no symbol, no magic flame, no glow, no colored fog, no outline stroke, no frame, no shadow backdrop, no hands, no watermark. It must remain recognizable as one blank old paper sheet at 32x32 pixels. New asset candidate, not an overwrite.

## QA
One empty paper sheet; transparent canvas. Slight warm red edge tint remains on the original reference-derived candidate. Preserve it for PD review rather than silently retouching.

- Original RGBA 1254x1254, alpha range 0–255, 1,198,379 fully transparent pixels. blank_a_32.png is a mechanical Lanczos reduction; preview_32.png shows those pixels enlarged on a dark background.
