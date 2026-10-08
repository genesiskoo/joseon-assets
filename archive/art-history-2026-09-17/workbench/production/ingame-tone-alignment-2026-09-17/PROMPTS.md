# 3D·인게임 기준 톤 정합 프롬프트

도구: 내장 image_gen. 실제 모델 ID 미노출. 참조 순서는 아래와 같다.
실제 캡처·모델 렌더와 생성 목표 시안은 구분한다. 원본 참조의 동결 사본은 references/에 보존했다.

## GT1 — B 인물 4인 게임 톤 시트

출력: GT1_B_cast_game_tone.png

1. C:/workspace/joseon/tmp/ingame-tone-2026-09-17/references/meshy_clean_actual_render.png
2. C:/workspace/joseon-assets/workbench/production/npc-variants-2026-09-17/NPC_B_expressive.png
3. C:/workspace/joseon/assets/models/tilekit_stone/floor_floor_tex_raw.png

```text
Use case: stylized-concept.
Create a 1536x1024 production-facing full-body cast tone sheet for JOSEON HUNTERS. This is Korean DARK FANTASY, matching actual stylized 3D game assets, with quietly sardonic personalities. Four adults on one plain muted charcoal-grey background, evenly spaced, complete hats, hands, props and feet safely inside the frame. Small title "B — GAME TONE". No dramatic scenery or decorative frame.

REFERENCE ROLES:
Image 1 is an ACTUAL GODOT MODEL RENDER, and governs Doho's proportions, color blocks, material finish, silhouette and level of detail. Use the RIGHT-HAND doho_meshy character: black wide-brim heukrip, big deep-navy coat masses, restrained dull-red waist sash, light inner collar, slim dark legs and boots, sword. Do NOT copy the checkerboard, debug lettering, second model or capsule. Do NOT invent intricate gold embroidery, extra necklaces or bright ornamental jewelry missing from this game asset.
Image 2 is the preferred NPC SET B. Preserve B1/B2/B3's recognizable FACE SHAPES, grey hair, role costumes, expressive asymmetry and distinct body silhouettes. It is an identity and personality reference, NOT an authority for bright white lighting or intricate cloth decoration.
Image 3 is actual in-game stone texture. Use it as the muted mineral/olive-grey palette and broad hand-painted material-scale reference only. Never transfer stone pattern onto clothing.

Cast left to right:
DOHO: lean young adult male swordsman, narrow knowing eyes, slight crooked half-smile, black heukrip with a small subdued blue front ornament, navy layered dopo, dull-red sash and restrained waist charm, ivory-grey collar, black boots. Sword lowered at his side and fully inside frame.
B1 MERCHANT: compact stout older man with the SAME generous round face, grey curled moustache and goatee as SET B; a closed-mouth wry smile. Soot-brown plain vest, smoke-ivory shirt and trousers, black gat, ledger and old coin pouch.
B2 SHAMAN: SAME slim sharp face, sly asymmetrical smile and swept high grey bun as SET B, no round grandmother redesign. Muted oxblood-red jeogori, deep desaturated teal long skirt, tarnished ochre sash, plain dark folding fan and small dull-brass bell bundle.
B3 ELDER: SAME broad shoulders, angular stern face, heavy brow and long grey-white beard as SET B. Black gat, plain charcoal robe, dirty-ivory sash, rough wooden staff. Quietly unimpressed, not villainous.

RENDERING: coherent stylized real-time RPG character concept, solid simple three-dimensional volumes, restrained drawn definition around eyes and folds, broad hand-painted matte albedo patches; practical worn fabric, leather and tarnished metal, without photoreal pores or micro-grunge. Faces are mature and distinct, with slightly simplified sculptural planes. The darkest values live in hats, hair and deep folds. Keep skin and grey hair readable but muted; no pink glowing porcelain faces. Neutral soft cool inspection lighting with modest form shadows; SHOW true darker material colors rather than hiding everything with underexposure. Large clothing color masses, sparse seams, almost no repeating embroidery. Navy, charcoal, soot brown, cold stone grey, dirty ivory; dull-red and teal only in limited identifying accents. Grounded, worn, sombre world; character humor lives in eyes and mouth, not a sunny atmosphere. No pastel colors, no golden sunlight, no shiny silk, no glossy 3D toy look, no bloom, no backlight halos, no anime beauty-airbrush, no crushed black silhouettes.
```

## GT2 — 현재 석재·카메라 기준 던전 톤 시안

출력: GT2_isometric_dungeon_tone.png

1. C:/workspace/joseon/tmp/ingame-tone-2026-09-17/references/portal_roundtrip_01_portal_open.png
2. C:/workspace/joseon/tmp/ingame-tone-2026-09-17/references/meshy_clean_actual_render.png
3. C:/workspace/joseon/assets/models/tilekit_stone/floor_floor_tex_raw.png
4. C:/workspace/joseon/assets/models/tilekit_stone/wall_wall_tex_raw.png
5. C:/Users/FORYOUCOM/.codex/generated_images/01a0ab0c-798a-7282-8f8b-e183b8b90559/exec-f8b7906c-ef3d-4169-8077-8a7d7f8f013d.png

```text
Use case: stylized-concept.
Create a 16:9 landscape visual-development concept for the CURRENT 3D isometric game Joseon Hunters, about 1672x941 pixels. A grounded Korean DARK FANTASY dungeon with stylized hand-painted game materials and simple modular geometry. This is a proposed art-direction study, not a claim to be an actual game screenshot. No UI, no HUD, no labels, no logos.

REFERENCE HIERARCHY:
1: actual current Godot dungeon. Use its orthographic isometric camera, modest character-to-tile scale, restrained almost-black surrounding space, muted grey masonry and localized visibility. Do not copy debug text, HUD, blue portal ring, stippled transparency artifacts or missing/cutout wall bugs. Build coherent continuous masonry.
2: actual Godot character model viewer. Use ONLY the right-hand doho_meshy character for navy/black/dull red color masses, low-detail matte clothing, hat silhouette and adult proportions. Do not copy checkerboard, lettering, second character or capsule.
3 and 4: actual current floor and wall textures. These strongly govern the broad desaturated mineral-grey stone planes, sparse cracks, modest olive moss, chunky block edges, and simple Korean lattice relief. Keep this hand-painted scale; no photogrammetry.
5: new darker cast sheet. Use ONLY its leftmost DOHO as identity support, not its studio background. Other NPCs do not appear in the dungeon.

Scene: a compact sealed Korean underground stone chamber, cutaway foreground walls for gameplay visibility, one short 2-tile-wide passage and stone stairs disappearing into shadow at the far side. Continuous walls of large chunky stone blocks, a few Korean geometric lattice-carved stones and one weathered paper seal on a lintel. Large square floor slabs. One small clay oil lamp or wall torch provides a restrained muted-amber local pool; a barely luminous thin cold-blue seal crack at the distant doorway is a secondary accent, no large magical circles.
Doho stands within the near chamber, three-quarter isometric angle, facing toward the stair passage with a sword held low. Single character. Entire full body and sword legible. Black Korean heukrip, deep-navy broad robe, muted-red sash, pale small collar, dark boots; no glowing weapon, no elaborate jewellery or repeating embroidery. Character height roughly one eighth of image height, comparable to current game view, not a giant foreground hero. Architecture respects a human-height doorway and consistent tiles.

RENDERING AND VALUES: solid low-poly-style volumes with broad hand-painted matte colors, limited edge highlights, clean silhouette, readable planes and sparse seams. No delicate illustrative contour decoration. Deep charcoal and near-black around the room; cold muted slate/olive-grey masonry; blue-black robe; tiny dull-red and tarnished-amber accents. Pool lighting reveals the traversable near floor and the character without flooding the whole scene. Corners recede into darkness but the walkable floor, sword hand and hat/shoulder silhouette remain readable. Keep actual game material simplicity even when the composition becomes more atmospheric. Darkness comes from restrained color, massing and localized light, not from photographic grime or featureless black crushing. No sunny village mood, no lush greenery, no pastel sky, no glossy PBR, no huge bloom, no volumetric god rays, no film grain, no depth-of-field blur, no ornate gothic-European architecture, no extra characters.
```
