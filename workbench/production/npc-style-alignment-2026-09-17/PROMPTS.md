# NPC 그림체 보정 프롬프트

내장 GPT Image 사용. 내부 모델 ID 미노출. 원본·참조 파일은 manifest.json 참조.

## N01_faces_D03_style.png

참조:

- `C:/workspace/joseon-assets/workbench/production/artwork-sequence-2026-09-17/01_doho_D03_master.png`

```text
Use case: style-transfer.
Create a CHARACTER FACE STYLE MATCH sheet for a Korean fantasy game. Landscape 3:2, 1536x1024. Four equal bust portraits in a clean 2x2 arrangement on a neutral ivory background. Head scale and portrait crop are consistent, all hats fully visible, generous separation.

The ONE attached image, DOHO D03, is the STRICT drawing-style reference. Apply its exact 2D fantasy-game illustration language to ALL FOUR portraits: crisp slender dark outlines, stylized almond-shaped drawn eyes, deliberately simplified nose and lips, smooth skin painted in three broad values, small soft transitions, designed graphic hair locks. Draw everyone as characters from the SAME illustrated cast. Do not use realistic elderly portrait rendering.

TOP LEFT, label DOHO: reproduce the reference's same young Korean man's face, eyes, black hair, knowing smile, black broad hat with blue ornament and bead cords, navy robe and white collar. Bust only; no sword needed.
TOP RIGHT, label MERCHANT KIM: an elderly Korean male merchant with a round broad face, cheerful narrow curved eyes, compact grey moustache and short beard, weathered black gat, plain warm-grey hemp vest over ivory clothes. His facial drawing is as stylized as Doho's. Age shown by cheek shape, grey hair and just three deliberate crease lines, not skin texture.
BOTTOM LEFT, label SHAMAN GRANDMA: an elderly Korean woman with greying hair in a bun, alert almond eyes, lifted fine eyebrows and a shrewd small smile, simple hairpin, muted vermilion Korean jacket with ivory collar. Use the SAME illustrated eye/nose/mouth construction and smooth three-value skin as Doho. Age remains unmistakable through face shape, grey hair and a few elegant age lines. No realistic wrinkles.
BOTTOM RIGHT, label VILLAGE ELDER: a lean elderly Korean man, long face, long white beard drawn in a few large tapered graphic locks, calmly stern almond eyes and straight brows, black gat, plain slate-grey robe and ivory collar. Same clean drawn line quality and simplified face shading as the others.

All four have normal adult proportions. Distinct faces, same artist. Match line weight, edge sharpness, shadow treatment, skin finish, hair treatment and light direction across every portrait. NPC clothing uses clean plain fabric and broad drawn folds, NO Doho embroidery copied onto them. Soft neutral light from upper left throughout. Noble elderly character design can be attractive and expressive without being de-aged.
NO realistic skin, pores, photographic wrinkles, painterly impasto, coarse textile grain, mottled stains, brown wash, weathered skin texture, lens effects, glossy 3D, cartoon dwarf or chibi proportions. Do not age-shift the young Doho. No background scene, props, extra portraits or decorative frames. Only the four small labels above.
The highest priority is that all NPC faces are obviously in the exact same stylized 2D illustration style as the young protagonist.
```

## N02_npc_trio_D03_style.png

참조:

- `C:/workspace/joseon-assets/workbench/production/npc-style-alignment-2026-09-17/N01_faces_D03_style.png`
- `C:/workspace/joseon-assets/workbench/production/artwork-sequence-2026-09-17/01_doho_D03_master.png`

```text
Use case: style-transfer.
Produce one NPC full-body production sheet, 1536x1024 landscape 3:2, three equal columns on clean ivory.
Image 1 is the character face STYLE MATCH sheet. Use TOP RIGHT MERCHANT KIM, BOTTOM LEFT SHAMAN GRANDMA, BOTTOM RIGHT VILLAGE ELDER as the precise NPC face/age/drawing designs. Image 2, DOHO D03, is the full-body drawing and material style reference, NOT a source of NPC outfit decorations.
Use exactly the same polished 2D illustrated character style as these references: slender precise dark contours, stylized drawn almond eyes, smooth skin in a few large values, graceful controlled folds, restrained soft transitions and matte colors. The NPCs must look drawn by Doho's illustrator, not realistic elderly concept paintings.

Three columns with only small headings MERCHANT KIM / SHAMAN GRANDMA / VILLAGE ELDER. In each column one LARGE full-length character, plus one small matching face inset in otherwise empty top corner. Every hat and shoe and prop completely inframe. Keep all figures at same display scale, normal stylized adult anatomy, roughly seven heads, no dwarf/chibi proportions. Subtle elder stoop allowed.

MERCHANT KIM: exact round cheerful elderly face from image 1, grey moustache and short grouped beard, narrow smiling eyes, black gat. Plain warm charcoal-brown vest over ivory wrap shirt and loose ivory trousers, simple dark fabric shoes, rope belt and coin pouch. Small ledger in one hand and conversational open other hand. Stout adult, not a tiny dwarf. Clean large cloth folds, just a few natural seam lines and restrained wear at edges; no decorative brocade or armor.

SHAMAN GRANDMA: exact narrow cunning mature/elderly face from image 1, grey hair up in a bun, simple brass hairpin, expressive almond eyes and knowing smile. Muted vermilion Korean top with ivory collar, muted teal full skirt, plain ochre sash, simple dark cloth shoes. One closed or partly opened paper fan and modest brass bell bundle. Natural practical figure, no young-body makeover. Cloth PLAIN except a small quiet border motif; no mottled patchwork, no rags all over. Her character comes from drawing and gesture.

VILLAGE ELDER: exact stern long elderly face from image 1, long white beard designed into clear tapered locks, black gat. Plain slate-grey long Korean robe, ivory inner and sash, dark simple shoes, weathered wooden staff in one hand. Tall lean adult. Do not copy Doho's navy costume, blue pendant, red sash, celestial emblem or bird embroidery onto this NPC.

Unified neutral studio light upper left, muted cool shadows, warm natural skin, readable clean color planes. Clothing color differences reflect the roles while all share one line-and-shading language. Only small controlled highlights on bells/hairpin; not glossy. Do not add photographed skin wrinkles, pores, gritty canvas, coarse fabric weave, grunge, random stained patches, painterly texture noise, yellow/sepia color filter, environmental background, extra alternate faces or extra poses.
Maintain the three newly drawn NPC faces exactly.
```

## N03_doho_npcs_motgol_style.png

참조:

- `C:/workspace/joseon-assets/workbench/production/artwork-sequence-2026-09-17/01_doho_D03_master.png`
- `C:/workspace/joseon-assets/workbench/production/npc-style-alignment-2026-09-17/N02_npc_trio_D03_style.png`
- `C:/workspace/joseon-assets/workbench/production/artwork-sequence-2026-09-17/10_motgol_day_keyframe.png`

```text
Use case: compositing and style-transfer.
Create one coherent illustrated scene for JOSEON HUNTERS, wide16:9 target1672x941.
Image 1 is DOHO D03, preserve his face and full costume.
Image 2 is the CORRECTED NPC STYLE SHEET, preserve these exact three newly drawn faces and clean clothing. These two images are the only rendering-style authorities. Do not revert the NPCs to realistic portraits.
Image 3 is old Motgol village DESIGN ONLY. Reuse the Korean architecture/pond/well vocabulary while completely repainting its rendering to match images 1 and 2.

Four adults in a medium-wide full-body group at a quiet village market. Doho center-left with a knowing smile, Merchant Kim at far left showing his small ledger, Shaman Grandma center-right with closed fan/bells and a sly smile, Village Elder far right quietly leaning on wooden staff. Same adult world scale, all heads and feet inside margins. Doho black broad hat with blue charm, navy layered robe with its own embroidery, white collar, muted red sash, blue waist pendant, loose black trousers and boots. His ONE sword held relaxed down beside his right leg, blade visible safely angled toward clear foreground, no sword crossing another head.
NPC designs copied from image2: rounded smiling merchant with short grey beard/plain vest and ivory clothes, angular grey-haired grandmother in clean vermilion top/teal skirt/ochre sash, stern long-faced elder with grouped white beard/plain grey robe. Keep the stylized almond eyes, line-drawn noses and mouths, smooth graphic skin shadows of image2. Their age is conveyed by grey hair, silhouette and a few designed age lines; no realistic wrinkle texturing.

Art direction shared by EVERY element: high-quality 2D Korean fantasy character illustration, clear fine dark contours, clean large painted shapes, two or three main values per material with a few soft transitions. Smooth matte surfaces. Background uses the SAME drawing technique, simplified enough to support the cast. Tiled roofs defined as broad grouped bands with a few contour strokes, wood as quiet flat planes with sparse seams, granite with broad facets, trees as broad coherent leaf clusters. No photoreal texture maps, grunge, speckled foliage or stone cracks everywhere.
Background behind cast: modest closed wooden stalls, dark Korean tiled rooflines, small dragon-head well, glimpsed pond pavilion on left, limited props so faces stand out. Background lower contrast than characters but not photographic bokeh. No sepia filter. Shared palette ink navy/ivory/muted red/celadon/neutral grey, restrained brown wood. One soft warm-neutral daylight upperleft, cool muted shadows with identical direction, clean skin tones, small matched ground shadows.
Doho and NPCs must look like a single illustrated cast, not styles pasted together. Calm lively folklore adventure and friendly swagger. No text, UI, extra people, particles, glow, photoreal wrinkles, fabric dirt patches or heavy painterly brush noise.
```

## 첫 통합 시도 — 후속 참조 제외

```text
STYLE HARMONIZATION EDIT for JOSEON HUNTERS. Deliver one landscape 16:9 integrated art-direction test, target 1672x941. Four people in ONE coherent village scene. No panels, portraits, labels, text or UI.

REFERENCE PRIORITY IS CRITICAL:
Image 1, DOHO D03 master, is the SOLE RENDERING STYLE AUTHORITY plus Doho identity. Its controlled fine dark drawing, elegantly simplified face, clean painted color planes, smooth matte cloth, restrained decorative lines and selective soft shading must govern EVERYTHING.
Image 2, the NPC sheet, supplies only the three NPCs' age, identity, clothing, props and roles. Its realistic skin, photographic wrinkles, coarse fabric grain and brown patina are UNWANTED and must be REDRAWN using Image 1's visual grammar.
Image 3, the village, supplies only architecture, pond/pavilion/well and fictional Korean place identity. Its dense realistic materials and tiny foliage detail are UNWANTED. REPAINT it with the same illustrated line-and-paint treatment as Doho.

Composition: medium-wide eye-level three-quarter view in Motgol market courtyard. On the SAME ground plane, Doho slightly left of center chats with three local NPCs. Merchant Kim at far left, grandma center-right, village elder far right. Four figures occupy about two-thirds image height, heads and feet all safely inside frame. Faces large enough to compare drawing styles. No giant foreground hero with tiny NPCs; all adult figures share a believable world scale and similar anatomical stylization. Doho tall but not towering; stooped elders remain adult.

Doho: exactly D03 young Korean man, knowing friendly half-smile, black heukrip with blue ornament/bead cords, deep navy layered robe, white collar, muted red sash, round blue waist charm, black loose trousers and wrapped boots. One sword resting along shoulder, held naturally and angled into open negative space above the group without intersecting heads, no scarf.
Merchant: elderly Korean man, rounded pleasant face, grey beard, worn gat, hemp vest over cream clothes, small ledger. Preserve age with only a few deliberate graphic creases around eyes and smile, NOT pores or hundreds of wrinkles.
Grandma: elderly Korean woman, grey hair tied up, lively knowing eyes, muted red top/teal skirt/ochre ties, fan and brass bells. Draw her eyes, nose, lips, hands and fabric folds with the same clean stylized lines and smooth color planes as Doho; keep her old and dignified, not de-aged or a caricature.
Elder: tall lean elderly Korean man, long white beard drawn as grouped simple tapered locks, black gat, slate-grey robe and ivory inner, wooden staff. Same face construction and shadow simplification as other characters.

Background: closed timber stalls and Korean tiled roofs, a small dragon-head stone well toward rear center and glimpse of pond pavilion left. Strong broad architectural masses; individual tiles indicated by sparse repeated graphic lines, foliage painted as grouped masses, granite as a few large planes. No texture noise, tiny chips everywhere or photographic leaves. Background gently lower in contrast and detail, same drawing medium as characters, never a realistic backdrop behind anime people.

ONE lighting setup for all: soft neutral warm daylight from upper left, muted cool-grey/indigo shadows, broad soft contact shadows in SAME direction. Skin uses a light base plus one broad half-shadow; occlusion accents only where needed. Cloth matte with broad readable folds and sparse line embroidery. Stone, wood and metal also painted, small metal highlights only. No brown/sepia wash, no dirty skin, no HDR, no rim glow, bloom, wet gloss or film grain. Palette shared across all: ink navy, ivory, muted vermilion, pale celadon/teal, warm grey stone and desaturated wood brown. Character accent colors may differ by role; rendering language and color temperature must not.
Target lively Korean folklore adventure with relaxed swagger, not realism, horror or grim misery. Make this look drawn by ONE illustrator using ONE brush/line/shading system.
```

## 사용자 중단 호출 — 완료 파일 미확인

```text
Prompt not available in session store.
```
