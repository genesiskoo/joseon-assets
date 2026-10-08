# GPT Image 2 In-Game Still Probes

Generated with the built-in `image_gen` workflow on 2026-06-07.

## Shared References

- Character identity:
  - `sprites/doho_cref1_spritesheet.png`
  - `sprites/doho_128_dir*.png`
  - `sprites/cheongyeon_cref3a_spritesheet.png`
  - `sprites/gwisae_cref2_spritesheet.png`
- Background references:
  - `workbench/probes/gpt-image2/map-tests-2026-06-07/village-market-high-topdown-matte-v3.png`
  - `workbench/probes/gpt-image2/map-tests-2026-06-07/dungeon-royal-tomb.png`
  - `workbench/probes/gpt-image2/map-tests-2026-06-07/dungeon-dokkaebi-ritual-cave.png`
  - `maps/map2.png`
- UI references:
  - `reference/internal/ui_mockup/ui_village_npc.png`
  - `reference/internal/ui_mockup/ui_battle_dungeon.png`
  - `reference/internal/ui_mockup/ui_dungeon_boss.png`

## Shared Prompt Rules

- True high top-down camera, approximately 70-75 degrees downward.
- 1536x1024 landscape in-game screenshot mockup.
- Characters read as 115-128px gameplay sprites, not concept-art figures.
- Restrained dark lacquered wood and aged-bronze HUD.
- No readable text, random letters, chat log, inventory panel, or watermark.
- Matte lighting, soft diffuse light, minimal specular highlights, low contrast
  shading, no glossy surfaces, no over-rendered reflections, and subtle rim
  light only.

## Still List

1. `01-village-exploration-ui.png`
   - Doho explores a late-Joseon village market junction.
   - Uses one compact top-left portrait, minimap, bottom skill bar, and small
     bottom-right menu buttons.
   - Best current reference for the intended exploration HUD density.
2. `02-forest-party-combat-ui.png`
   - Cheongyeon, Doho, and Gwisae fight dokkaebi foot soldiers and boars on a
     forest road.
   - Uses stacked party portraits, an enemy bar, minimap, and compact skill bar.
   - Good action readability; effects remain small enough for gameplay.
3. `03-royal-tomb-battle-ui.png`
   - Three-character party battles ghost soldiers in a royal tomb chamber.
   - Good room layout, sprite scale, and dungeon mood.
   - Known issue: top-center boss icon reads too much like a western skull.
     Future prompts should specify `dokkaebi mask icon only, no skull icon`.
4. `04-dokkaebi-cave-boss-ui.png`
   - Boss encounter in a dokkaebi ritual cave.
   - Strongest boss-screen candidate: clear arena, party formation, boss scale,
     compact HUD, and Korean folk-supernatural props.

## Follow-Up Prompt Fixes

- For boss and elite enemy UI: `dokkaebi mask silhouette icon only, no skull,
  no bone motif, no western monster icon`.
- For cleaner UI: `no readable labels or numbers anywhere; bars and icons only`.
- For sprite scale: `characters remain below 128px visual height and are placed
  as map sprites, not enlarged illustration figures`.
- For map lighting: use the suppression block in
  `docs/image-generation-lighting-prompt-guide.md`.
