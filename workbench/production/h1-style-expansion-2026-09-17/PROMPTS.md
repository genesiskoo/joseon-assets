# H1 production prompts and QA
Built-in image_gen; actual model ID not exposed. Timestamp is source PNG LastWriteTime, not server generation time.

## H1-X01 - 도호·NPC 공통 화풍 비교
Output: iterations/01_cast_comparison_r0.png
Mode: built-in image_gen / reference-guided generation
Status: superseded
QA: 독립 QA: 화풍·H1·주인공 위계·해부·프레임 통과. B2 노년성이 약해 얼굴만 수정.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\korean-character-refinement-2026-09-17\K2_korean_manhwa.png
```text
Use case: stylized-concept. Asset H1-X01: production-quality shared-style cast lineup for Joseon Hunters, fictional Korean dark fantasy action RPG. Create ONE wide landscape illustration, 4 complete full-body figures with generous space around hats, weapons and feet, on a plain warm charcoal background, a common ground line, neutral inspection lighting. Quiet small labels only: "DOHO · H1", "KIM · B1", "SHAMAN · B2", "ELDER · B3".
Input 1 is the APPROVED H1/H2/H3 board. ONLY the LEFTMOST H1 figure is both the Doho character identity and shared visual-style anchor. Ignore H2/H3. Closely preserve H1's clean-shaven Korean face, playful half-smile, narrow controlled eyes, relaxed athletic proportions, wide thin black gat with blue badge and bead cords, deep navy layered dopo with split short angled front hems revealing voluminous black trousers, white collar, dark wrist wraps, dull red sash with TWO trailing ends, one round blue waist charm, black boots. His right hand holds a straight sword over his shoulder with the blade clear of the hat and face, left hand resting by the scabbard. Retain the strong relaxed open stance and silhouette of H1, no beard, no scarf.
Input 2 is supporting NPC identity only: preserve the SECOND, THIRD and FOURTH figures from that sheet; do NOT use its first plain Doho figure. B1 is a shorter stout elderly Korean male merchant with round welcoming face, short grey moustache/goatee, black gat, soot-brown overvest over ivory wide sleeves, baggy trousers, ledger and coin pouch, sly welcoming open palm. B2 is a slim elderly Korean woman with a narrow knowing face, grey hair in a LOW chignon with simple binyeo, muted brick-red jeogori, white collar and deep teal chima, closed black fan and small brass ritual bells, slightly crooked amused smile. B3 is a tall stern elderly Korean village elder with broad angular face, thin grey brows, long straight white beard, black gat, charcoal robe and plain wooden staff.
All FOUR must be drawn by the SAME illustrator using H1's Korean manhwa facial abstraction, thin confident ink contours, broad soft MATTE painted shadow planes and sparse large cloth folds. Age is communicated by shape and a few deliberate lines, never photoreal skin. Their costume colors and distinct silhouettes are retained. Doho gets the clearest focal silhouette and slightly stronger face/white-collar separation; NPCs remain individually memorable without looking like other protagonists. Korean collars and closures, grounded fabric. Muted navy/charcoal/earth/ivory/brick/teal; no glossy gold embroidery, no ornament inflation, no western comic exaggeration, no chibi, no generic Chinese fantasy armor, no porcelain/glossy skin. Neutral readability must coexist with the dark restrained palette. Complete correct anatomy and props; no extra figures, no decorative frame, no text other than the four small labels. Target landscape 2048x1152.
```

## H1-X01r1 - 도호·NPC 공통 화풍 비교 / B2 나이 보정
Output: 01_cast_comparison.png
Mode: built-in image_gen / targeted edit
Status: visual_qa_pass
QA: 독립 재검수 통과: B2 노년성 개선, H1/다른 인물/손/검/소품 회귀 없음. 원화 검수이며 3D 미검증.
References in exact call order:
1. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-f7fd1965-f62b-45af-875f-2cea2e287893.png
```text
Edit target: supplied H1-X01 four-person cast sheet. Make ONE surgical correction: the THIRD character, SHAMAN B2, must read clearly as an elderly Korean grandmother, approximately late 60s/70s, while retaining her slender face and mischievous knowing smile. In the SAME restrained H1 manhwa linework, slightly lower the upper eyelids, add a few deliberate eye-corner and cheek age lines, subtly soften the sag of cheeks/jaw. Keep her exact grey low chignon, facial identity, pose, costume, fan and bells. NO photoreal skin, no dense wrinkles or ugly caricature.
Preserve all other content: Doho H1 on the left, merchant B1 and elder B3 faces/bodies, four poses, scale and positions, all garments/colors, hands, props, labels, sword, framing, plain charcoal background and matte lighting. Do not redesign or beautify any other face. Full original composition and resolution.
```

## H1-X02 - 못골 통합 초안
Output: iterations/02_motgol_close.png
Mode: built-in image_gen / reference-guided generation
Status: superseded
QA: 공통화풍 양호. 인물비중이 실제보다 약2배 크고 상점천이 일본 노렌처럼 읽힐 여지 → 시점/천구조 보정.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-af073d7b-b9db-4df2-9490-f2910f203e27.png
3. C:\workspace\joseon\tmp\h1_artwork_build\references\actual_town.png
```text
Use case: stylized-concept. H1-X02: ONE production environment illustration for MOTGOL village in Joseon Hunters, fictional KOREAN dark fantasy. Wide landscape 2048x1152, fixed orthographic isometric camera approx 35 degrees down / 45 degrees yaw, matching a playable 3D ARPG view. This is a target concept painting, not a screenshot or UI mockup.
References: image 1 APPROVED board LEFT H1 ONLY = exact Doho identity and common drawing style. Image 2 = corrected shared-style cast identities (Doho, stout elderly Kim merchant, elderly woman shaman, stern elder); preserve their proportions and mature faces. Image 3 = CURRENT ACTUAL GAME screenshot for camera angle and small on-screen actor scale ONLY. Discard its checker ground, capsules, boxes, labels, dialogue/HUD and rendering defects.
Scene: a small worn Korean village shop courtyard at dim overcast dusk. Broad stone threshold, packed dark earth and irregular simple grey stone pavers, muted soot-brown timber shop with paper lattice doors and a modest low curved grey giwa roof, low stone retaining wall, one jars-and-ledger stall. A shrine alcove is visible to one side. Large calm shapes; walkable court remains clearly open. The architecture uses Korean timber/post spacing and hanji doors, no Chinese palace eaves or Japanese shrine gates.
Doho H1 walks in the clear center foreground, about 14-17 percent of image height, navy split layered robe revealing trousers, red sash with two tails, blue waist charm, white collar, black gat, straight sword held easily across his shoulder. Stout elder Kim stands at his shop counter with ledger, white sleeves and brown vest. The SHAMAN is visibly ELDERLY, grey low chignon, few deliberate facial age lines, brick red jeogori/deep teal chima, fan and brass bells near shrine. Only these THREE figures; coherent physical size and feet firmly grounded. They are interacting lightly, not combat. Doho is the focal figure; keep his hat, face/collar, sash and sword distinct.
Use the SAME restrained H1 Korean manhwa fine ink edges, broad soft matte painted planes and limited large folds for BOTH people and architecture. Stone and wood are drawn in the same hand, not photoreal background under anime figures. Muted charcoal/navy/mineral-grey/soot-brown; limited brick/teal accents. Low cool ambient light, one small warm paper-lantern pool at shop, sufficient neutral reflected light to read silhouettes and paths. Dark fantasy weathered atmosphere with lively personalities. No golden sunshine wash, no bright pastel village, no glossy material, no fog that hides traversal, no dense embroidery/noise, no extra crowd, no western medieval props, no HUD, no frame. Small discreet bottom-left title only: "H1-X02 / MOTGOL".
```

## H1-X02r1 - 못골 통합 / 넓은 시점
Output: 02_motgol_wide.png
Mode: built-in image_gen / composition and storefront edit
Status: visual_qa_pass
QA: 시점 후퇴·천 가리개 정리. 원화 인물비중은 개선됐으며 실제3D 정합은 별도 시험. 독립검수: 환경 원화 합격, 실제3D/게임가독성·가림·애니는 미검증.
References in exact call order:
1. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-d3b8eebd-c04b-4d22-af80-c2bd10d482ae.png
```text
Edit the supplied village concept into a WIDER gameplay-scale version of the SAME location and cast. Preserve the H1 Korean manhwa drawing style, charcoal/earth palette, cool ambient and small warm lantern pools, and the exact identities/costumes of Doho, Kim and the elderly shaman.
Camera correction: pull the orthographic camera back by about TWO TIMES. Reveal substantially MORE courtyard and surrounding Korean buildings on all sides. In the same landscape canvas, the FULL Doho figure including gat must be only 14 percent of image HEIGHT, approximately 135 pixels in a 940-pixel high canvas. Merchant and shaman at consistent small human scale. Keep a wide open playable ground, Doho near center and the two NPC stations separated at the upper-left shop and upper-right shrine. This is an overview, with small characters rather than a character-portrait composition. No pasted miniature cast: all buildings and ground must recede coherently with the camera.
Cultural correction within the shop: REMOVE the dark blue hanging split curtains with circular crests and the vertical patterned cloth strip on the shop's left post. Replace these with simple bare Korean wood lintel / open wooden shutters. Keep hanji lattice doors and grey giwa roof. The commercial lantern becomes a plain rectangular wood-framed paper lantern, no Chinese characters. Keep the shrine's restrained paper talismans, earthenware jars and old stonework.
Doho remains H1, clean-shaven, black gat, navy split robe over visible trousers, white collar, dull red sash with two tails, small blue round waist charm and straight sword over shoulder. Shaman remains visibly elderly with grey LOW chignon, wrinkled eyes/cheeks, brick jeogori/teal chima, fan and bells. Exactly three human figures. No new figures or animals. No HUD, debug UI, checker tiles, glossy materials, pale daylight or western scenery. Same clean hand-drawn matte treatment for people and environment. Bottom-left discreet title "H1-X02 / MOTGOL — WIDE". Target 2048x1152 landscape.
```

## H1-M01F - 도호 H1 정면 / 3D 입력
Output: 04_doho_front.png
Mode: built-in image_gen / identity-preserving pose derivative
Status: input_visual_qa_pass
QA: 독립 QA: H1 복식·앞트임·분리바지·무광·T-pose 확인. 주먹손이라 손펴는 동작은 미검증. 실제3D 합격과 구분.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
```text
Use case: stylized-concept. Asset H1-M01-F. ONE single full-body FRONT ORTHOGRAPHIC character production reference for 3D reconstruction. Portrait 1024x1536, plain neutral medium-grey background, shadowless neutral diffuse light, generous margins, all hat and boot edges inside the image. Exactly ONE figure, no layout, no extra side/back views, no labels, no props floating beside body.
Reference = APPROVED H1/H2/H3 board. Use ONLY LEFT H1. Faithfully translate that exact H1 man into a neutral rigging T-pose, retaining H1's identity and clothing, not redesigning. Adult clean-shaven Korean male, same controlled manhwa eyes and faint sly smile, relaxed straight spine, natural roughly seven-and-a-half-head proportions, wide thin black gat with cylindrical crown and small blue badge, black hair tied back, short neat bead cords. Deep matte navy layered dopo, white overlapping collar, dark inner wrap, broad upper sleeves narrowing to dark forearm wraps. Deep dull-red waist sash with exactly TWO ends resting downward off the left side, ONE small round blue charm at front waist. Front coat hems are SHORT ANGLED split panels opening above knees, exposing roomy black trousers and separated legs; longer rear tails visible only behind, not a closed floor-length skirt. Subtle low-contrast woven pattern only where present in H1, no gold embroidery. Black calf boots.
T-pose: facing straight forward, head upright, BOTH arms perfectly horizontal and fully separated from torso, sleeves resting by gravity with clean contours under arms, elbows extended, hands in simple relaxed CLOSED FISTS suitable for later sword socket. Legs straight and slightly spread, feet forward flat, no contrapposto. NO sword and NO scabbard in this reconstruction input: weapons will be separate 3D attachments. Keep waist sash/charm and costume structures intact.
Same fine H1 Korean manhwa drawing, simplified large matte painted planes with clear material boundaries; no glossy PBR or photoreal skin, no dramatic shadows, no rimlight, no perspective foreshortening, no mask/scarf/beard, no armor, no extra garments or accessories, no black floating backdrop. This is a faithful neutral-pose derivative of LEFT H1, not the middle H2's long skirt or right H3.
```

## H1-M01B - 도호 H1 후면 / 3D 입력
Output: 05_doho_back.png
Mode: built-in image_gen / identity-preserving pose derivative
Status: input_visual_qa_pass
QA: 독립 QA: 정면/후면 의상·허리끈 위치 연결. 후면 머리·옷자락은 제작상 추론, 실제3D 미검증.
References in exact call order:
1. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-ebad1a1c-e64e-49c9-b94d-c6f7eddd4d87.png
2. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
```text
Use case: stylized-concept. H1-M01-B, single BACK ORTHOGRAPHIC production reference for 3D reconstruction. Reproduce the EXACT same character, outfit, body proportions, camera scale, neutral grey background and neutral matte lighting as input 1, but seen directly FROM BEHIND, still in a level T-pose. Input 2's LEFT H1 is the approved character identity; ignore H2/H3.
One figure only, complete hat/hands/boots inside frame. Back of a clean-shaven Korean man with tied-back black hair under the same thin broad black gat. The back of the navy layered dopo is simple broad dark navy panels with a central seam and split lower tails, sparse subtle tone-on-tone cloth pattern, no new insignia, no large embroidered medallion. Back belt is plain dull red; its TWO sash tails wrap from the FRONT tied knot on the character's left, so in this BACK view the tails are visible on image RIGHT. The small blue charm remains at the FRONT waist and is NOT duplicated on the back. White collar visible only as a narrow edge at the neck. Same black voluminous trousers, same calf boots and black forearm wraps. Both arms perfectly horizontal, hands closed relaxed fists. No sword/scabbard, no floating props, no loose cape, no hood or scarf, no facial features drawn on back of head.
Ensure the rear coat tails are separated to support leg movement and keep the H1 front-side panel lengths consistent with image1. The sleeves have exactly the same large hanging silhouette as the front image. No perspective, no three-quarter view, no labels, no shadow gradients or strong baked light. Portrait 1024x1536, same framing as input1 with enough margin to avoid clipping fists.
```

## H1-X03 - 석실 던전 통합
Output: 03_sealed_chamber.png
Mode: built-in image_gen / reference-guided generation
Status: superseded
QA: 무광 석재·도호/산적·이동면 판독 양호. 현재캡처보다 인물비중이 커 실제크기 검증은 별도. 독립검수: 환경 원화 합격, 실제3D/게임가독성·가림·애니는 미검증. 현행 art_3d_pipeline 산적 무기는 나무곤봉으로 확인되어 칼→곤봉 수정본으로 대체.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-d3b8eebd-c04b-4d22-af80-c2bd10d482ae.png
3. C:\workspace\joseon\tmp\h1_artwork_build\references\actual_dungeon.png
```text
Use case: stylized-concept. H1-X03: ONE wide orthographic ISOMETRIC PLAYABLE DUNGEON VIEW for Joseon Hunters, a fictional Korean dark fantasy ARPG. Target 2048x1152. Establish H1's illustration style across hero, enemy and stone environment while obeying small in-game actor scale.
Reference 1: approved LEFTMOST H1 only for Doho and the shared fine ink / broad matte painted shadows. Ignore its other two characters. Reference 2: recent town illustration for the SHARED HAND-DRAWN material language only, NOT its oversized character scale. Reference 3: current actual Godot dungeon screenshot for isometric axis, camera distance, torch-pool lighting and dark atmosphere ONLY. Remove ALL checker/black grid defects, dithering, capsules, portal covering player, labels and HUD. The floor must be continuous visible stone, not black tile holes.
Composition/scale: an orthographic camera looking down about 35 degrees, yaw 45 degrees. Show a roomy stone chamber AND the start of two corridors, roughly eighteen metres across the wide frame. One floor tile = 1 metre; Doho is 1.7 metres tall. Make the ENTIRE Doho figure including hat only about ONE SEVENTH of the canvas HEIGHT (14 percent), deliberately small in the room, NOT a large portrait or toy diorama. One bandit is similar human scale. Leave a broad uncluttered playable floor, clear paths, no obstructing front wall.
Scene: grey-green Korean granite blocks, broad uneven stone slabs with sparse broken corners and subdued moss, heavy stone lintel with simple Korean lattice seal motif and worn paper talismans, short descending stone stair at the back, one small earthenware jar by the wall, two restrained warm wall-lantern pools. Cool charcoal shadows and faint mineral-grey bounce make stone floors/paths readable. Low ambient, no bright fill over the entire scene. No photoreal surface grime, ornate gothic detail or Chinese/Japanese architectural symbols.
Doho H1 stands at the lower center facing diagonally toward one plague-afflicted Korean bandit higher-right with 3 metres of clear separation, both fully visible. Doho keeps his black gat, clean-shaven sly face, navy layered split hems over black loose trousers, white collar, dull red sash two ends and one round blue charm. He holds his straight sword in a relaxed ready position, weapon apart from body, no glow hiding it. Bandit: adult Korean male, grey-green sickly skin, rough dark-brown short jeogori and patched trousers, cloth head tie, rusty single-edged short blade; hunched threatening stance but clearly the same H1 manhwa drawing medium. No armor inflation or oversized fantasy sword.
Fine controlled ink contours, broad matte color shapes, low saturation and sparse large folds. Character faces, cloth, wood and stone share one illustrator. PC has the clearer silhouette and contrast than enemy and background. No dramatic closeup, no huge actors, no UI, no extra creatures, no lens perspective, no sunlight, no black floor voids. Small bottom-left title only: "H1-X03 / SEALED CHAMBER".
```

## H1-X03r1 - 석실 통합 / 현행 산적 곤봉
Output: 03b_sealed_chamber_club.png
Mode: built-in image_gen / targeted prop correction
Status: visual_qa_pass
QA: 산적의 칼만 나무 곤봉으로 정정(art_3d_pipeline §3). 부모 재검수: 도호 검·배경·인물·조명 회귀 없음. 원화 합격, 실제3D는 별도.
References in exact call order:
1. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-eb2b42bc-ded4-4106-8a2e-1f8bda79a81c.png
```text
Edit target = supplied H1-X03 dungeon illustration. Make exactly ONE targeted correction for the current game specification: the enemy bandit at upper right holds a rough short WOODEN CLUB in his right hand, NOT a metal blade. Replace only his knife/short sword with a clearly readable worn brown wooden cudgel of plausible hand length, a thick blunt striking end and correct grip. No metal blade, no spikes, no glow. Preserve everything else precisely: camera framing, floor/stonework, lighting and shadows, bandit's identity and stance, Doho H1 pose/sword/navy clothes/black gat/red sash, scale, two figures, all environment objects and title. Same hand-drawn H1 matte style. Doho's straight sword MUST remain a sword, untouched.
```

## H1-M02F - 김 영감 B1 정면 / 3D 입력
Output: 06_merchant_front.png
Mode: built-in image_gen / identity-preserving pose derivative
Status: input_visual_qa_pass
QA: 부모 QA: B1 연령·체형·복장·T-pose·빈손 확인. 손펴는 동작은 미검증. 독립 검수에서도 고령상인·앞뒤연결·프레임 합격.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-af073d7b-b9db-4df2-9490-f2910f203e27.png
```text
Use case: stylized-concept. H1-M02-F. ONE single full-body FRONT ORTHOGRAPHIC neutral T-pose character input for 3D reconstruction. Portrait 1024x1536, neutral medium grey plain backdrop, soft even neutral inspection lighting, complete gat, fists and shoes with clear margin. ONE figure only, no inset portraits, no labels, no extra views.
Input1 = shared style H1, LEFTMOST figure only, for fine Korean manhwa ink and matte big painted shadow shapes. DO NOT copy Doho's clothes or youthful face. Input2 = approved-working cast sheet; use the SECOND character "KIM B1" only, the short stout elderly Korean merchant with rounded expressive face, short grey moustache/goatee, arched grey brows and sly welcoming half-smile. Preserve his identity.
He has a plain black Korean gat WITHOUT Doho's blue badge, simple black hat cords, dark soot-brown sleeveless overvest reaching upper thigh over a warm ivory jeogori with ample loose sleeves, subtle very low contrast cloth weave, simple rope belt and ONE small brown coin pouch at hip. Baggy warm ivory baji trousers, ivory ankle wraps, worn black/brown low Korean shoes. His body is stout and stocky with a round belly, clearly older than Doho, not a muscular soldier or chibi. Natural elderly adult proportions, around 1.6 metres in the future model.
Rigging pose: straight-on front, both arms horizontal at shoulder level fully separated from torso, fists gently closed, legs slightly apart and shoes flat facing front. NO ledger or coins in his hands, no separate props: ledger will be a separate accessory. Do not add weapons, armor, colorful sashes, jewelry or extra pouches. Keep the natural cloth layers, collar overlap, vest hem and trousers clear. Age shown by broad face forms and a few controlled eye/cheek lines, never photoreal wrinkled skin. Match the face of the second character in image2 exactly within the neutral pose. Matte muted earthy palette. No cinematic/rim lighting, no dark cast shadows baked into clothing, no glossy skin or gold decoration. All anatomy complete.
```

## H1-M02B - 김 영감 B1 후면 / 3D 입력
Output: 07_merchant_back.png
Mode: built-in image_gen / identity-preserving pose derivative
Status: input_visual_qa_pass
QA: 부모 QA: 전후 복식·주머니 동일 신체측면·체형·전신 프레임 확인. 후면은 제작상 추론. 독립 검수에서도 고령상인·앞뒤연결·프레임 합격.
References in exact call order:
1. C:\Users\FORYOUCOM\.codex\generated_images\01a0ab0c-798a-7282-8f8b-e183b8b90559\exec-5fb42af1-d867-4c6e-b380-31c038ea9bec.png
```text
Use case: stylized-concept. H1-M02-B, a single direct BACK ORTHOGRAPHIC T-pose reference of EXACTLY the same elderly stout Korean merchant in the supplied front input. Preserve the same full-body scale, grey background, matte even light and 1024x1536 portrait framing. One figure only, no labels, no inset, no props.
Rotate the SAME merchant 180 degrees, without changing proportions/clothes. Back of plain thin black gat, small grey-black hair bun and simple tied cord, neck under the same white collar. Brown sleeveless overvest with broad simple back panel and central seam, same subtle tone-on-tone cloth pattern and hem reaching upper thigh. Ivory loose jeogori sleeves hang in matching shapes from horizontal T-pose arms. Rope belt continues around the waist without adding a second bow at the back. The single small coin pouch is on image LEFT in this rear view because it was image RIGHT in the front view; it must not duplicate. Warm ivory voluminous baji trousers, ivory ankle wraps and low black/brown Korean shoes, two feet firmly apart. Same simple closed fists, arms fully horizontal and separated from body. NO face at the back, no ledger, no weapons, no extra pockets, no Doho blue badge, no red sash. H1 fine ink and broad matte painted shading across the entire figure. No glossy 3D render, no dramatic shadow, no photoreal skin. Keep generous margins so hands, hat and feet never crop.
```

## H1-C01 - 귀새 G02 / 초기 앞뒤 시트
Output: iterations/08_gwisae_r0.png
Mode: built-in image_gen / reference-guided generation
Status: superseded
QA: 독립 QA: 정체성/화풍 통과. 후면 두 탈의 허리 좌우가 모호해 정후면으로 수정.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:/workspace/joseon-assets/sheets/approved-2026-09-17/catalog_gwisae_G01-G03.png
3. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Create a polished 16:9 character production catalog plate for GWISAE from Joseon Hunters, a Korean dark fantasy action RPG. This is a style transfer of an already approved character, not a redesign.
REFERENCE ROLES: image 1 is a three-option Doho board; ONLY its LEFT H1 supplies the drawing style: delicate Korean manhwa contour lines, restrained facial details, large clean matte shadow planes, simple major fabric folds, quiet material surfaces. Do not copy Doho's outfit or face. Image 2 is the Gwisae identity board; use ONLY the MIDDLE G02. Ignore G01 and G03. Image 3 is the accepted H1 shared-cast style demonstration.
LAYOUT: tasteful charcoal-gray neutral studio sheet. Large complete front three-quarter full-body character at left (45% width), same character full-body rear three-quarter at center (30%), at right a close detail of her worn mask and three neatly separated accessories: one curved dagger with short red tassel, two spare masks together, long dark-red ribbon. All images are the SAME design. Generous margins; no cropped hair, boots, hands or blades. Small exact heading "GWISAE / H1" only; no prose.
IDENTITY: adult agile Korean woman, high long black ponytail with small red cords; ivory wooden gaksital mask with gently closed smiling eyes, small red forehead circle and red cheeks, subtle aged material. Black and muted crimson split-front short overcoat with purple inner layer; baggy black trousers visibly separated from coat tails, black wrapped boots and wrists. Preserve the G02 major overlap and hem shapes, but simplify dense embroidery into sparse dark-red border motifs; broad matte fabrics like H1. TWO spare masks hang at her anatomical LEFT hip (viewer RIGHT in front view, viewer LEFT in back view): one dark patterned mask and one brown smiling carved mask. They must remain the same two masks on the same belt attachment, not three. One single-edged curved dagger held safely down in anatomical right hand, long loose red ribbon from belt moves gently, no ribbon tangles with hands. Human anatomy and sensible grip. Read as a distinctive player character rather than generic ninja. No uncovered new face, no katana, no kimono/obi, no bulky Western armor.
LIGHTING: neutral soft even production light, original colors clearly visible with dark body values retained; no dramatic rim light, no scene lights baked on cloth, no photorealistic skin or microtexture, no bright anime cel gloss, no new blue charms. The two views must match proportions and accessory placement.
```

## H1-C01r1 - 귀새 G02 / H1 카탈로그
Output: 08_gwisae.png
Mode: built-in image_gen / localized reference edit
Status: visual_qa_pass
QA: 독립 QA 통과: 정후면 왼 허리 두 탈·오른손 곡단검 연결, G02 각시탈·기동형 복식 유지. 실제 메시·리깅은 미검증.
References in exact call order:
1. C:/Users/FORYOUCOM/.codex/generated_images/01a0ab0c-798a-7282-8f8b-e183b8b90559/exec-edcab808-aa92-49b9-a356-92a3414b518c.png
```text
Edit this supplied GWISAE / H1 production plate with ONE strictly localized correction to the MIDDLE full-body rear-view figure only. Preserve every pixel outside the middle figure area as closely as possible: the front-view figure, all right-hand accessory details, close-up mask portrait, typography, palette, texture and composition are already correct.
Replace the middle rear-three-quarter view by a CLEAR DIRECT REAR VIEW of the same character at the same height and position. Head looking straight away, no face visible, black ponytail and same rear coat panels. Her anatomical RIGHT hand is on viewer RIGHT and holds the same curved dagger down. Her anatomical LEFT hip is on viewer LEFT: attach EXACTLY TWO spare masks to that left-side belt attachment (one dark patterned mask and one brown smiling mask), visibly hanging at the LEFT OUTER hip. NO mask or mask attachment at the right hip or center of her back. The pair may rotate slightly to show their carved faces but the straps must attach at the left belt seam. Match the two spare masks and clothing to the untouched large front figure. Keep the exact same boots, coat, muted red sash, purple lining, ponytail and style; do not add or remove any other prop. Fully framed feet and hair. This is a continuity correction, not a redesign.
```

## H1-C02 - 청연 C01 / 초기 앞뒤 시트
Output: iterations/09_cheongyeon_r0.png
Mode: built-in image_gen / reference-guided generation
Status: superseded
QA: 독립 QA: 후면 소품 손 배치 모호, 치맛단 봉황 문양 복구 필요.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:/workspace/joseon-assets/sheets/approved-2026-09-17/catalog_cheongyeon_C01-C03.png
3. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Create a polished 16:9 production character catalog for CHEONGYEON from Joseon Hunters. Preserve the approved LEFT C01 character in reference 2, but render her in the drawing style of ONLY LEFT H1 in reference 1. Reference 3 demonstrates H1 used consistently across ages. This is one character's style translation, not options or a redesigned costume.
STYLE: Korean manhwa fine confident outlines, restrained eyes/nose/mouth, broad simple matte shadow masses, clear major folds. Match H1's relatively quiet cloth surfaces; drastically simplify fine decorative noise while preserving the C01 distinct silhouette and key accessories. No photorealistic cloth or glossy skin.
DESIGN: serene adult Korean woman, slender but credible human anatomy, black loosely flowing hair with slim braids, small distinctive black-and-dull-gold ceremonial headpiece precisely as C01 (not tall emperor crown). Ivory layered long hanbok over pale-celadon underdress, generous hanging sleeves, crossed white collar, low-contrast limited embroidery near hems, celadon sash, carved pale jade round pendant, two paper talismans. A dark navy/black folding fan with sparse golden moon-and-star marks in right hand; a small cluster of aged brass bells with tassels in left hand. Keep these C01 features, no sword, no Doho red sash or blue bead necklace.
LAYOUT: dark warm neutral gray studio background, 16:9. Left: large 3/4 front complete full-body pose with fan and bells, calm faint knowing smile; feet visible. Middle: matching rear 3/4 full-body view with sleeves hanging and hair resting naturally, same headpiece and layers. Right top: one face close-up exactly same adult woman and small headpiece. Right bottom: clearly separated open celestial fan, brass bell cluster, jade pendant/talismans. Use small exact heading "CHEONGYEON / H1". Nothing else written.
PRODUCTION LIGHT: soft neutral fill sufficient to see local ivory and celadon colors, not white emissive glow; dark outline and matte gray shadows keep her in the same moody world. No scene environment, no floating magic, no glamour lighting, no bright cheerful anime shine, no complex ornate embroidery, no Japanese miko design, no Chinese xianxia flowery accessories. Full framing with safe margins, readable hands gripping the correct objects, consistent scale/proportions between front and rear.
```

## H1-C02r1 - 청연 C01 / H1 카탈로그
Output: 09_cheongyeon.png
Mode: built-in image_gen / localized reference edit
Status: visual_qa_pass
QA: 독립 QA 통과: 정후면 오른 부채·왼 방울, C01 봉황·상아/청록 복식·얼굴 유지. 실제 메시·리깅은 미검증.
References in exact call order:
1. C:/Users/FORYOUCOM/.codex/generated_images/01a0ab0c-798a-7282-8f8b-e183b8b90559/exec-da5d1405-3344-413c-9a24-9162d5950e36.png
2. C:/workspace/joseon-assets/sheets/approved-2026-09-17/catalog_cheongyeon_C01-C03.png
```text
Correct the supplied CHEONGYEON / H1 catalog with only these two changes. Keep the layout, adult woman's exact face, full-body front pose, headpiece, colors, right detail boxes and delicate matte H1 drawing style.
1. Replace the MIDDLE rear three-quarter figure with a STRICT DIRECT BACK VIEW of the same character. Her head looks straight away, no face visible, hair hangs on her back. Front view holds fan in anatomical RIGHT hand and bells in LEFT; therefore in this direct rear view the closed black fan must be on VIEWER RIGHT, held by her right hand, and the identical brass bell cluster must be on VIEWER LEFT, held by her left hand. Make both hands clearly visible beside the sleeves. Preserve the same ivory long hanbok/celadon underskirt, small black-gold headpiece and rear layers; ivory ribbons and braids remain. Keep equal height, safe margins, feet intact.
2. On the LOWER FRONT HEM panel of the LEFT standing figure, restore one sparse pale dull-gold PHOENIX embroidery from the approved C01 character: long curved neck, beak, one spread wing, long flowing tail feathers. Replace the current vague floral motif only in this small lower hem region. It must remain very low contrast and subordinate to the large cloth shapes, not a bright ornate mural. Leave upper robe motifs alone. No new decorations elsewhere.
Do not swap objects in the already correct front figure or alter the portrait. This is production continuity cleanup, not another design option.
```

## H1-N02 - 무당 할매 B2 / 개별 시트
Output: 10_shaman.png
Mode: built-in image_gen / reference-guided generation
Status: visual_qa_pass
QA: 독립 QA 통과: 노년의 얼굴·낮은 쪽머리·벽돌색/청록 복식·능청 유지. 앞뒤 소품 손 위치 일치. 실제 메시·리깅 미검증.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Create a polished 16:9 individual NPC production catalog for Joseon Hunters. Reference 1 supplies ONLY the LEFT H1 drawing grammar: Korean manhwa fine restrained lines, broad matte shadow shapes, major folds and quiet textures. Reference 2 is the already approved shared cast lineup, for this NPC's exact face, age, body and clothing. Do not copy Doho's clothes or face. Dark warm gray neutral studio background with soft even production light; sufficiently visible local colors, no dramatic rim light or scene lighting.
LAYOUT: left large complete FRONT three-quarter full-body presentation, middle smaller strictly DIRECT BACK full-body view at matching proportion, right upper a detailed same-face portrait; right lower the character's individual props separated on clean negative space. Neutral comfortable standing, full hair/headwear, feet and hands in frame, wide margins. The strict rear view has no visible face. Hands and props must maintain anatomical sides. This is one fixed design shown consistently, no variants. Restrained simple layout, only exact short heading specified below, no paragraphs.
CHARACTER: SHAMAN GRANDMOTHER B2, the THIRD figure in reference 2. Clearly an ELDERLY Korean woman about 70: lean narrow long face, higher cheekbones, creased eyelids, thin lips, a mischievous knowing sideways smile; gray hair in a LOW CHIGNON with a simple horizontal binyeo. Keep her elderly age in both full-body and portrait without photorealistic wrinkles. Slender slightly stooped but spirited body. Muted dark-brick-red jeogori with white collar and short dark tie, desaturated deep teal full chima skirt, worn cloth shoes. No crown, no tall bun, no glam youthful face, no sorceress armor. Large simple matte cloth folds, not dense embroidery.
In FRONT she holds one CLOSED pale folding fan in her anatomical RIGHT hand (viewer left) and a small aged brass bell cluster in LEFT hand (viewer right). In the DIRECT BACK view, fan is on viewer RIGHT, bells viewer LEFT. Props below portrait: that same closed fan and that same brass bell cluster, full length, separate. Do not introduce a staff or mask. Heading exactly "SHAMAN / H1".
```

## H1-N03 - 촌장 B3 / 개별 시트
Output: 11_elder.png
Mode: built-in image_gen / reference-guided generation
Status: visual_qa_pass
QA: 직접 검수: 각진 노년 얼굴·긴 백수염·먹색 도포 유지, 정면 왼/후면 오른 지팡이 연속성·전신 프레임 통과. 실제 메시·리깅 미검증.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Create a polished 16:9 individual NPC production catalog for Joseon Hunters. Reference 1 supplies ONLY the LEFT H1 drawing grammar: Korean manhwa fine restrained lines, broad matte shadow shapes, major folds and quiet textures. Reference 2 is the already approved shared cast lineup, for this NPC's exact face, age, body and clothing. Do not copy Doho's clothes or face. Dark warm gray neutral studio background with soft even production light; sufficiently visible local colors, no dramatic rim light or scene lighting.
LAYOUT: left large complete FRONT three-quarter full-body presentation, middle smaller strictly DIRECT BACK full-body view at matching proportion, right upper a detailed same-face portrait; right lower the character's individual props separated on clean negative space. Neutral comfortable standing, full hair/headwear, feet and hands in frame, wide margins. The strict rear view has no visible face. Hands and props must maintain anatomical sides. This is one fixed design shown consistently, no variants. Restrained simple layout, only exact short heading specified below, no paragraphs.
CHARACTER: VILLAGE ELDER B3, the FOURTH/rightmost figure in reference 2. An OLD Korean man about 75, broad angular face, square cheekbone planes, heavy grey brows and stern worried eyes, long straight white beard and moustache, noticeably old without photorealistic skin. Firm slightly stooped substantial body in a charcoal gray long Korean dopo, white collar, plain pale-grey knotted waist sash, black trousers and worn dark shoes. Simple black gat, no Doho blue badge or beads. Preserve the B3 unadorned plain dark robe, no metallic armor, no decorative embroidery, no vivid PC colors.
He holds one sturdy old crooked natural wooden walking staff in his anatomical RIGHT hand. In front view staff is on viewer LEFT; in DIRECT BACK view it is on viewer RIGHT. Other hand relaxed empty. Portrait head must be the same square-faced old man with long white beard, distinct from round-faced merchant and young Doho. Separated prop study: entire same wooden walking staff in two modest angles and simple cloth waist knot. Heading exactly "ELDER / H1".
```

## H1-F01 - 구미호 F01·F03 / 변신 전후
Output: 12_gumiho_forms.png
Mode: built-in image_gen / reference-guided generation
Status: visual_qa_pass
QA: 독립 QA 통과: 같은 성인 얼굴·흑발·금안, 인간형 귀/꼬리 없음, 변신형 왼4+중앙1+오른4=9개 꼬리 끝 확인. 실제3D 미제작.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:/workspace/joseon-assets/sheets/approved-2026-09-17/catalog_gumiho_F01-F03.png
3. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Create a premium 16:9 two-form character comparison catalog for GUMIHO in Joseon Hunters, in the same common H1 Korean manhwa art style. Reference 1: ONLY LEFT H1 supplies fine drawing lines, restrained human facial planes, quiet matte broad cloth shadows. Reference 2: approved GUMIHO identity; use LEFT F01 human and RIGHT F03 transformed, ignore F02 completely. Reference 3: accepted H1 shared-character rendering style.
COMPOSITION: neutral dark charcoal-brown studio sheet, LEFT 35% F01 complete full-body human with small label "F01"; RIGHT 65% F03 complete full-body transformed with generous space for ALL NINE tails and small label "F03". Clear gap between the two figures. Upper heading "GUMIHO / H1". Same height from scalp to feet in both; tails can extend above head. No extras, no other text, no inset that could look like another form.
SAME IDENTITY IN BOTH: mature adult Korean woman, long black partly pinned hair with dull gold hairpins, narrow golden amber eyes, controlled dangerous slight smile, same beautiful but sharp face proportions. Deep oxblood-red Korean layered long hanbok with white narrow crossed collar, gold border motifs and a few broad phoenix-like embroidery motifs, brass-gold waist clasp/pendants, ivory tassel; sensible H1 simplification of the source ornamentation, clean broad fabric planes, no photoreal brocade. Left F01: entirely human, ordinary human ears, NO fox ears, NO tail, one small curved dagger held low in her anatomical left hand (as source F01), other hand resting elegantly by waist, quiet predatory composure. Right F03: exactly the SAME woman and face, same base red hanbok with more open flowing red-gold outer hems; hands gracefully joined at waist, no dagger.
CRITICAL TAIL COUNT: F03 has EXACTLY NINE large GOLDEN FOX TAILS attached naturally at her lower back. Lay them out as a clean countable fan: ONE central upward tail, FOUR spreading out to viewer LEFT of it, FOUR spreading out to viewer RIGHT. Exactly nine distinct pointed fluffy tips, all inside frame with visible negative-space gaps between every adjacent tip. Each tail must read as one broad tapered volume from a shared lower-back root to its single tip. No branching, no second row of hidden tips, no tails belonging to F01. Golden fur is subdued warm ochre with soft matte planes, not glowing yellow light or finely noisy realistic fur. Keep the tails behind her body without covering her face/hands or merging into her black hair.
Consistent soft neutral illumination to inspect local colors, muted dark-fantasy values, a limited bright face/collar, thin delicate line work. No revealing redesign, no cosplay ears, no anime doll face, no Western fantasy armor, no Chinese imperial headdress, no decorative UI frames. Correct human hands, full garment hems and feet visible, no cropped tips. Before finishing verify 1+4+4 tail tips and face continuity.
```

## H1-BG01 - 석실 던전 / 모듈 목표 원화
Output: 13_dungeon_modules.png
Mode: built-in image_gen / reference-guided generation
Status: concept_visual_qa_pass
QA: 직접 검수: 바닥·벽·코너·문틀·봉인문·기둥·계단2·화로9종 구분. 중립 목표 원화이며 정밀치수·반복 텍스처 합격을 의미하지 않음. 실제GLB 후보는 별도3d_modules.
References in exact call order:
1. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/03b_sealed_chamber_club.png
3. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
```text
Use case: stylized-concept. Create one 16:9 production environment kit sheet for the sealed stone dungeon of Joseon Hunters. Match the H1 Korean manhwa art direction: thin purposeful contours, broad matte stone planes, few simple chips, subdued cool gray/brown palette. Reference1 is the H1 shared character plate for rendering grammar only, reference2 is accepted dungeon mood/material, reference3 is the APPROVED H1 board with only LEFT H1 supplying style. Production sheet is neutral softly lit with warm charcoal background, NOT a dark scene.
Show NINE carefully separated modular objects in a clean 3x3 arrangement with wide empty spacing and tiny clear labels only. Consistent isometric camera and relative scale; no objects overlap.
Top row: (1) FLOOR, a 1x1 tile thin square slab of worn Korean granite subdivided into a few broad blocks, perfectly square edges suitable for repeated tiling, no large central crack leading nowhere. (2) WALL, a 1 tile wide by 2 tiles high solid stone wall segment built of quiet rectangular blocks, squared ends and flat top. (3) CORNER, the matching L-shaped external stone wall corner.
Middle row: (4) FRAME, a 3 tile wide stone doorway surround with one large rectangular opening and simple lintel. (5) SEAL, a separate thick granite door slab, a restrained incised circular eight-direction seal and a few hanging red-stamped paper talismans; Korean fantasy ritual feel, no skull relief, no torii. (6) PILLAR, one chunky plain granite pillar on a square foot with modest chipped edges.
Bottom row: (7) STAIRS UP, shallow broad stone steps on a compact square footprint. (8) STAIRS DOWN, the matching opening stair section descending within a stone surround. (9) BRAZIER, a plain aged iron low brazier with charred wood and NO large flame, the object itself clearly inspectable.
Sparse restrained hand-painted material, no photoreal texture or shiny polished marble, no Victorian Gothic arches or Chinese dragon carvings. Square module boundaries must be readable. No measurement claims in text, no splash effects, no characters, no floating labels besides those nine names. Header "SEALED CHAMBER / H1". This is visual kit concept, not an assembled dungeon screenshot.
```

## H1-BG02 - 못골 / 건축·소품 목표 원화
Output: 14_motgol_modules_props.png
Mode: built-in image_gen / reference-guided generation
Status: concept_visual_qa_pass
QA: 직접 검수: 목조·기와·한지·옹기·상자·사각등·평상에 H1의 무광 면 적용. 시트의 소품은 상대 확대됨. 실제GLB치수·배치 검수는 별도.
References in exact call order:
1. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/02_motgol_wide.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Use case: stylized-concept. Create a 16:9 production environment and prop kit sheet for MOTGOL, the worn Korean village of Joseon Hunters. Reference1 is the accepted H1 town location: preserve its Korean timber, pale plaster, paper lattice doors, dark gray roof tiles, rough granite foundations, earth-brown wood. Reference2 is the H1 common character style, fine Korean manhwa lines and broad matte shaded planes; environment uses the same amount of simplification. No photorealism or exaggerated cute-cartoon proportions.
Show SEVEN separated objects in a neat wide composition on charcoal-gray neutral studio ground, consistent isometric angle and honest relative scale, large enough to inspect. Top: one big SINGLE-BAY SHOP FACADE with low dark tiled eave, heavy weathered posts, half plaster/half wood wall, low raised stone plinth, a plain Korean wooden counter. Adjacent the separate PAPER DOOR panel showing timber grid and translucent weathered hanji, plus a small WOODEN SIGN board hung from a bracket. Below show four individual props: a squat warm dark-brown ONGGI clay jar with lid; a simple WOODEN CRATE with thick battens; a SQUARE PAPER LANTERN with plain wood frame and a small warm inner light; a low TIMBER BENCH. Each object has its own blank surrounding space, no duplicates.
Use small exact labels "SHOP", "PAPER DOOR", "SIGN", "ONGGI", "CRATE", "LANTERN", "BENCH"; header "MOTGOL / H1". The sign's face is plain with no fake lettering. Avoid hanging blue crested split curtains, Japanese noren, torii, cherry blossom motifs or round red Chinese lanterns. Soft neutral studio light to preserve material color, minimal shadow, no night fog or cinematic bloom. Cracked plaster, wood grain and pottery scratches are sparse large marks, not tiny noise. This is a reusable asset design sheet, not a town scene or actual 3D render.
```

## H1-E01 - 산적 / 중립 3D 입력
Output: 15_bandit_input.png
Mode: built-in image_gen / reference-guided generation
Status: input_visual_qa_pass
QA: 삼베·머리띠·회녹 피부, 2팔/2다리·사지 분리·전신 프레임 확인. 곤봉은 별도 소품. 실제3D 미검증.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Use case: stylized-concept / production model input. Joseon Hunters Korean dark fantasy, H1 shared style. Reference 1 supplies ONLY the LEFT H1 drawing style, not costume: fine controlled Korean manhwa contours, broad simple MATTE shaded planes, a handful of important folds, subdued colors and readable silhouette; no photorealism, no ornamental noise. Reference 2 is H1's consistent mixed cast and material simplicity.
Create ONE isolated complete character on uniform medium-neutral gray background, shadow-free neutral studio light, no dramatic rim lighting or environmental highlights baked in, no scenery, no ground props, no captions, no montage, no inset, no duplicate views, no frame. Entire subject with generous margin on every side, clear separations between body parts, no object touching the edges. Stable human/animal anatomy as specified. A clear 3D-generation input illustration, not a splash poster.
SUBJECT: plague-sick BANDIT, adult Korean male grunt about 1.5m height. Front view facing camera, upright neutral relaxed A-pose with both arms held 30 degrees clear from torso and empty loosely closed hands, legs apart. Short stocky sinewy body, permanently slightly hunched shoulders but no action twist. Sallow desaturated gray-green skin, gaunt cheekbones, crooked brow and hostile tired eyes, short untidy black hair under a plain worn dark cloth headband. Ragged coarse hemp short jeogori in dirty muted earth-gray, visible crossed Korean collar, fraying sleeve ends, rough rope waist belt, baggy patched hemp trousers, dark cloth wrist/ankle wraps and worn straw sandals. Visible forearms. Compact worn clothing, no long coat, no decorative pattern. Consistent broad matte rendering. This enemy fights using a WOODEN CLUB produced separately; DO NOT draw a weapon in these hands or attach any weapon to body. No sword, shield, metal armor, modern clothes, samurai/kimono, undead exposed bones, gore or body wounds. He must read as a sick impoverished Korean bandit rather than a Western orc. Portrait format 2:3.
```

## H1-E02 - 박쥐 / 중립 3D 입력
Output: 16_bat_input.png
Mode: built-in image_gen / reference-guided generation
Status: input_visual_qa_pass
QA: 자흑색 날개2·귀2·후지2·꼬리막, 펼친 날개 형상 확인. 날개끝 여백은 좁지만 잘림 없음. 실제3D·비행 리그 미검증.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Use case: stylized-concept / production model input. Joseon Hunters Korean dark fantasy, H1 shared style. Reference 1 supplies ONLY the LEFT H1 drawing style, not costume: fine controlled Korean manhwa contours, broad simple MATTE shaded planes, a handful of important folds, subdued colors and readable silhouette; no photorealism, no ornamental noise. Reference 2 is H1's consistent mixed cast and material simplicity.
Create ONE isolated complete character on uniform medium-neutral gray background, shadow-free neutral studio light, no dramatic rim lighting or environmental highlights baked in, no scenery, no ground props, no captions, no montage, no inset, no duplicate views, no frame. Entire subject with generous margin on every side, clear separations between body parts, no object touching the edges. Stable human/animal anatomy as specified. A clear 3D-generation input illustration, not a splash poster.
SUBJECT: a small MONSTROUS BAT, exact specification body height approx0.7m and wingspan1.2m. Frontal symmetrical spread-wing neutral airborne pose, wings extended left/right with clean separate outlines, all tips visible. Compact stout dark purple-black furred mammalian body, a small snarling muzzle, two pointed ears and two bright red amber eyes, short fangs but no gore. Leathery purple-black wing membranes stretched between clear long finger bones, each wing structurally one arm with a short thumb claw near shoulder; two small separate tucked hindlegs with claws, modest tail membrane. Wings should be broad readable planes, not a collection of knives or feathery bird wings. Fur stylized in only a few broad triangular tufts, no noisy individual fibers, no magic particles, no glow haze. Same H1 restrained line and flat matte values, dark plum highlights allow the shape to be seen on medium gray. Landscape 3:2. Exactly2wings,2ears,2eyes,2hindlegs. No spread eagle feathers, no wyvern long neck, no humanoid features.
```

## H1-E03 - 부적술사 / 중립 3D 입력
Output: 17_talisman_caster_input.png
Mode: built-in image_gen / reference-guided generation
Status: input_visual_qa_pass
QA: 현행 흰도포·창백한 가면·양손목 종이부적 유지, 던질 부적 별도. 빈손·팔/몸 간격·전신 확인. 실제3D 미검증.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Use case: stylized-concept / production model input. Joseon Hunters Korean dark fantasy, H1 shared style. Reference 1 supplies ONLY the LEFT H1 drawing style, not costume: fine controlled Korean manhwa contours, broad simple MATTE shaded planes, a handful of important folds, subdued colors and readable silhouette; no photorealism, no ornamental noise. Reference 2 is H1's consistent mixed cast and material simplicity.
Create ONE isolated complete character on uniform medium-neutral gray background, shadow-free neutral studio light, no dramatic rim lighting or environmental highlights baked in, no scenery, no ground props, no captions, no montage, no inset, no duplicate views, no frame. Entire subject with generous margin on every side, clear separations between body parts, no object touching the edges. Stable human/animal anatomy as specified. A clear 3D-generation input illustration, not a splash poster.
SUBJECT: TALISMAN CASTER, a sinister masked adult Korean human enemy approx1.6m. Full front view neutral A-pose, arms 30 degrees separated from torso, empty visible loosely closed hands, feet apart; lean elongated body under a RAGGED OFF-WHITE Korean dopo (WHITE, NOT BLACK), narrow crossed collar and long tattered split hems that reveal muted charcoal trousers and wrapped old shoes. Cloth is matte soiled ivory with gray/beige fold shadows; no glowing fabric. A PALE CHALK MASK covers the face, simple elongated human mask with narrow dark eye-slits, understated ink strokes, no oni horns, no clown red circles, no grinning metal skull. Black hair tied compactly behind head. Two short faded paper talismans tied at each wrist as flat cloth-like strips following gravity, not floating or covering fingers; these identify the caster. Rough pale rope belt. No ornate embroidery, no pagoda hat, no sword, no staff, no armor, no giant glowing magic disc. Future thrown paper projectiles are separate props; no floating cards around the model input. No gore. Neutral pose and obvious left/right limbs suitable for rigging. Portrait2:3.
```

## H1-E04 - 흑랑 / 중립 3D 입력
Output: 18_heukrang_input.png
Mode: built-in image_gen / reference-guided generation
Status: input_visual_qa_pass
QA: 거대한 검은 4족 늑대·붉은 눈·꼬리1·분리된 발4 확인. 연기는 후속VFX로 분리, 입력은 불투명 털 덩어리. 실제3D·4족 리그 미검증.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
```text
Use case: stylized-concept / production model input. Joseon Hunters Korean dark fantasy, H1 shared style. Reference 1 supplies ONLY the LEFT H1 drawing style, not costume: fine controlled Korean manhwa contours, broad simple MATTE shaded planes, a handful of important folds, subdued colors and readable silhouette; no photorealism, no ornamental noise. Reference 2 is H1's consistent mixed cast and material simplicity.
Create ONE isolated complete character on uniform medium-neutral gray background, shadow-free neutral studio light, no dramatic rim lighting or environmental highlights baked in, no scenery, no ground props, no captions, no montage, no inset, no duplicate views, no frame. Entire subject with generous margin on every side, clear separations between body parts, no object touching the edges. Stable human/animal anatomy as specified. A clear 3D-generation input illustration, not a splash poster.
SUBJECT: HEUKRANG, the enormous BLACK FOUR-LEGGED WOLF boss, roughly2.4m tall at its highest point. One complete three-quarter side view, facing viewer left, calm standing neutral quadruped pose with four clearly separated paws on same ground, head level, mouth just slightly open with a few teeth, ears alert. Massive shoulder hump, long canine snout, strong thick neck and chest, heavy broad paws, anatomically canine joints and hocks, one bushy tail. Black charcoal fur forms smoky swept-back tufts around shoulders and spine but must stay as SOLID broad readable fur volumes, not transparent swirling VFX. Two deep RED eyes as small sharp accents; no large red glow and no full-body fire. H1 fine contours and broad matte shading applied to beast anatomy. Subtle cool gray planes let black body read under neutral studio light. No human stance, no werewolf arms, no horns, no armor, no collar, no chains, no ground fog, no magical floating runes. Exactly four grounded legs and one tail, every paw and tail tip visible with generous margins. Landscape3:2.
```

## H1-P01 - 검·검집·곤봉·부적 / 분리 소품
Output: 19_weapons_props.png
Mode: built-in image_gen / reference-guided generation
Status: concept_visual_qa_pass
QA: 직접검수: 직검/검집/나무곤봉/종이부적 분리, 칼끝·손잡이 프레임과 재질 구분. 실제 무기 원점·축·치수는 별도GLB 검사, 원화측면은 정밀도면 아님.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/03b_sealed_chamber_club.png
```text
Create a neutral 16:9 weapon and prop production sheet for Joseon Hunters, matching ONLY the LEFT H1 character's drawing and equipment in reference1. Reference2 is the accepted H1 dungeon and enemy wooden club. Do not redesign the character weapons. Matte Korean fantasy game prop look, fine controlled outlines and large simple steel/wood/paper planes, dark warm gray background, soft even studio light. No hand holding an object, no characters, no scene.
Four clearly separated groups:
1. DOHO SWORD: a single straight slender Korean fantasy steel sword matching H1 shoulder sword, simple straight/very modest oval crossguard, dark wrapped straight grip with small brass collars and restrained round pommel, single clean tapered point; broad-side full-length view plus a small matching edge/profile view. Not a katana, no curved blade, no oversized ornate fantasy sword or inscriptions.
2. SCABBARD: one matching plain dark scabbard with dull brass fittings at mouth and tip, proportional to that sword, shown separately and fully inside frame.
3. BANDIT CLUB: plain uneven slightly tapered wooden striking club, heavy thicker rough head and simple narrower wrapped hand grip; one full side view and one small end-on cross-section. No nails, blades, glowing rune or metal spike.
4. TALISMAN: two simple thin beige paper strips with stylized worn black ritual strokes and faded red stamp (visual fictional markings, not readable real writing), one straight and one slightly bent to show negligible thickness.
Place each group with ample negative space and small exact labels "SWORD", "SCABBARD", "CLUB", "TALISMAN"; heading "EQUIPMENT / H1". All full tips and handles visible, no cropped blades. The grip centers and directions must be unambiguous for 3D hand sockets, but do not draw axes, measurements or claims. No baked emissive effects or bright rim light. Slight steel edge highlight, aged dull metal, matte dark wood, flat paper.
```

## H1-K01 - H1 3인방 키아트 / 초기 프레임
Output: iterations/20_keyart_r0.png
Mode: built-in image_gen / reference-guided generation
Status: superseded
QA: 인물정체성과주인공위계양호. 도호 발끝 잘림을 수정.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/08_gwisae.png
3. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/09_cheongyeon.png
4. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/03b_sealed_chamber_club.png
```text
Create one finished wide 16:9 key art illustration for JOSEON HUNTERS, a Korean dark-fantasy isometric action RPG. No text or logo. Use the same H1 Korean manhwa illustrator across all characters AND scenery: delicate purposeful contours, restrained handsome faces, large MATTE painted shadow planes, confident major cloth folds, quiet rough stone/wood surfaces, low overall saturation. Dramatic but readable; not photoreal, not glossy anime.
REFERENCES: Image1 ONLY the LEFT H1 is DOHO's exact approved identity and strongest style anchor; ignore H2/H3. Image2 is the corrected GWISAE character catalog: preserve its front design and left-hip two masks. Image3 is CHEONGYEON corrected catalog. Image4 is the accepted H1 dungeon/town dark-material language. All identities remain distinct. Do NOT put Doho's clothes on others.
COMPOSITION: Doho dominates the center foreground, his body roughly 75% of canvas height, his face highest local contrast. Three-quarter body, relaxed confident ready stance with separated legs, turned toward viewer. Clean-shaven young adult Korean face, sly half smile, narrow alert eyes; black wide-brim gat with small blue badge and bead strings, navy layered split-front dopo showing black baggy trousers, white collar, muted red sash with exactly two loose ends, one round blue waist charm, black boots/wrist wraps. Right hand casually rests his single straight sword over the right shoulder, blade clear of hat and face, left hand near matching dark scabbard. Preserve H1's costume and silhouette with restrained ornamentation, no scarf or beard.
GWISAE stands behind him at viewer left at about 50% canvas height: adult Korean woman in ivory smiling gaksital with red circles, high black ponytail, black/crimson split coat and purple inner layer, black trousers/boots, two spare masks at HER LEFT hip, one curved dagger held low in right hand, short red ribbon sweeping aside. CHEONGYEON stands behind at viewer right at similar smaller scale: same serene adult woman, small black-gold headpiece, ivory/pale celadon long hanbok and broad sleeves, black celestial fan in right hand, brass bells in left, jade charm. Neither support obscures Doho or becomes a generic NPC.
LOCATION: worn Korean granite dungeon entrance beneath a simple low tiled village gate at the edge of Motgol; cracked stone threshold, restrained wooden beams and paper seals, distant dark rooflines, a suggestion of an unsafe passage beyond. The stone and timber share the same simplified matte planes as the clothing. Avoid giant decorative architecture swallowing the characters. No torii/noren/Chinese dragon palace, no Western Gothic castle.
LIGHT: low cool charcoal ambient light, one small warm brazier reflected subtly on lower stone, very restrained cool seal-light in the doorway. Doho's face/white collar and sword edge get the strongest readable separation, red sash second, supporting faces readable but less contrast. Cheongyeon's ivory cloth stays gray in shadow rather than lighting up the whole picture. Only a little dust and mist near distant ground, no bloom or particle storm. Strong depth and triangular staging, heroic swagger without losing danger. Entire hats, hands, blades and boots remain in frame; no extra people or limbs. This is a cast key art, not a gameplay screenshot, class-selection UI or photoreal movie poster.
```

## H1-CS04 - 봉인 벽 / 컷씬 목표 원화
Output: 21_seal_wall_cutscene.png
Mode: built-in image_gen / reference-guided generation
Status: visual_qa_pass
QA: 독립QA합격: storyline §2.4 도호+무당·푸른봉인균열·잠깐진지전환 일치. 허리검집/어깨검중복없음, 인물과석벽무광명암정합. 기존컷4이며흡수후전체8컷재번호는미정리.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/10_shaman.png
3. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/03b_sealed_chamber_club.png
4. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/13_dungeon_modules.png
```text
Create a finished cinematic 16:9 illustrated story keyframe: "The Seal Wall" from Joseon Hunters. No text, no subtitles, no logo, no panels. References: image1 ONLY the LEFT H1 Doho (ignore H2/H3); image2 the approved H1 elderly shaman B2 catalog; image3 the accepted H1 sealed-chamber materials/lighting; image4 stone-kit design for Korean rectangular stone doorway and paper seals. Same fine Korean manhwa linework and broad matte shadows on faces, clothing, stone and wood. No photoreal materials or glossy anime.
STORY ACTION: At the ruined dungeon entrance just outside Motgol, Doho pauses facing a ancient SEALED GRANITE WALL. Worn ritual writing and paper seals tremble along a hairline crack, with a narrow cold BLUE light leaking through. The elderly shaman stands slightly behind him, explaining the seal's age with a grave knowing look. Doho's playful face becomes briefly attentive and serious, a measured confident gaze rather than horror or despair.
COMPOSITION: eye-level medium-wide oblique view. Doho foreground left-center in 3/4 SIDE view so we can see his distinctive clean-shaven Korean face beneath the black gat while his body/gaze point toward the tall stone seal at right. One hand rests naturally on the hilt of the SWORD SHEATHED at his left hip; sword NOT drawn and no shoulder sword duplication. Exact H1 navy split-front layered dopo, white collar, two-ended dull red sash, one blue waist charm, black trousers/boots, gat badge/beads, no scarf/beard. Behind left, B2 is clearly an elderly Korean woman with narrow lined face, gray LOW chignon/binyeo, dark brick jeogori and teal chima. She holds a closed dark fan in one hand, small brass bells in the other, posture alert but grounded. Do not make her youthful or a witch caricature.
RIGHT of picture: simple worn Korean granite lintel and a wall-sized stone slab with a modest circular incised seal, a few torn paper talismans; restrained fictional ink ritual strokes, not readable prose. Blue leakage limited to the crack, catching Doho's eye and thin edge of white collar. A small warm lantern farther behind gives faint warmth to shaman's cheek; low cool ambient light keeps background dark and matte. Foreground path is readable, far threshold feels dangerous but contains no visible monster and no gore. No Gumiho reveal, no giant holographic magic circle, no lightning storm, no horror ghosts. Leave lower10% quieter for future subtitle placement but add no black bar. Both characters' hands, hat/head and feet inside frame, consistent old/new costume details. Let the scene convey a brief switch from sly confidence to focused attention.
```

## H1-K01r1 - H1 3인방 / 키아트
Output: 20_keyart.png
Mode: built-in image_gen / localized framing edit
Status: visual_qa_pass
QA: 독립 원화 QA 합격: 중앙 도호가 크기·자세·검 방향으로 먼저 읽힘. G02 여분 탈 2개·C01 부채/방울·전신 프레임 유지. 캐스트 키아트이며 EA 3클래스 제공을 뜻하지 않음.
References in exact call order:
1. C:/Users/FORYOUCOM/.codex/generated_images/01a0ab0c-798a-7282-8f8b-e183b8b90559/exec-c527c242-0749-429f-826b-8a1beb8d738d.png
```text
Reframe this exact finished key art by pulling the camera back about 15-18% so the ENTIRE THREE CHARACTERS, including all of Doho's boots, both Gwisae boots and Cheongyeon's feet/lower hem, fit comfortably inside the image. Preserve their exact faces, costumes, hand-held objects, pose relationships, background design, dark lighting and overall composition. Doho must remain the largest central leading figure; don't shrink him to the supporting characters' size. Show the whole black gat with at least a small margin above it and foreground stone ground below both of his boots. Extend the existing Korean stone entrance and dark sky naturally as needed to keep the wide16:9 format. Keep sword clear of hat and face. No new characters, no redraw of wardrobe, no new ornaments or effects. The only goal is clean complete framing without changing this selected composition. No logo or text.
```

## H1-UI01 - PC·NPC·구미호 / 초상 8종
Output: 22_portraits.png
Mode: built-in image_gen / reference-guided generation
Status: visual_qa_pass
QA: 독립 원화 QA 합격: PC/NPC의 얼굴·나이·표정 구분, 구미호 F01/F03 동일 인물, 선·무광 명암 정합. UI 얼굴 우선 크롭으로 갓 끝 일부 잘림. 128px 표시 검수는 별도 페이지에 기록.
References in exact call order:
1. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
2. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/08_gwisae.png
3. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/09_cheongyeon.png
4. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/01_cast_comparison.png
5. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/12_gumiho_forms.png
```text
Create a unified character portrait art sheet for Joseon Hunters using exactly eight square portrait cells arranged FOUR columns by TWO rows, equal size and consistent framing. 16:9 landscape canvas with dark neutral gray gutters. Exact row1 labels below portraits: "DOHO", "GWISAE", "CHEONGYEON", "GUMIHO F01". Exact row2: "MERCHANT", "SHAMAN", "ELDER", "GUMIHO F03". No other text, no HUD, no health bars or menu widgets. This is portrait artwork for future UI use, not new UI layout.
All eight are drawn by the SAME H1 Korean manhwa artist: fine lines, restrained facial features, broad matte face planes, sparse age lines, muted cloth colors, soft neutral light, charcoal solid background. Each is head-and-upper-chest only, head sized consistently, every hat brim and hairstyle fully inside its cell with margin. Highest clarity on eyes, eyebrows, mouth and signature collar/mask. No glossy beauty skin, no photoreal elderly faces, no chibi.
REFERENCES: 1 approved H1/H2/H3 board ONLY LEFT H1 for Doho exact face and style. 2 corrected GWISAE identity. 3 corrected CHEONGYEON identity. 4 H1 shared-cast lineup with B1 round older merchant, B2 narrow elderly woman, B3 angular old bearded elder. 5 GUMIHO paired forms.
DOHO: same clean-shaven young Korean man, sly half-smile, black gat with blue badge/bead strings, navy coat/white collar; no beard/scarf.
GWISAE: same ivory gaksital with red forehead/cheek circles worn over adult face, black high ponytail/red cords, dark red black coat.
CHEONGYEON: same serene adult Korean face, black hair with thin braids, small black-and-gold headpiece, ivory/celadon collar.
MERCHANT: a stout OLD Korean man, round face with short gray moustache/goatee, narrowed smiling eyes, plain black gat, brown vest/ivory collar, no Doho bead badge.
SHAMAN: clearly OLD Korean woman, narrow long face, gray low chignon with horizontal binyeo, thin sly smile, brick-red jeogori/white collar; retain age70 facial abstraction, not middle-aged glam.
ELDER: OLD Korean man, broad angular stern face, gray brows and long white beard/moustache, plain black gat, charcoal robe/white collar.
GUMIHO F01 and F03: exactly SAME adult Korean woman's face proportions, long black hair/gold pins/golden eyes, dark crimson lips and oxblood-red gold-trimmed hanbok. F01 controlled smile, human ears/no fox traits. F03 slight cold intensity, same human face with a restrained hint of golden tail fur behind shoulders only; this is cropped portrait detail, not a tail-count diagram. No fox ears added.
Maintain each distinct age/personality and wardrobe while matching facial scale, line thickness, shadow softness and material finish. Each label must correspond to its portrait, no duplicated PC face for an NPC, no merged cells, no extra faces.
```

## H1-TEX01 - 목재·기와·회벽·한지 / 재질 아틀라스
Output: 23_material_atlas.png
Mode: built-in image_gen / reference-guided generation
Status: material_trial_candidate
QA: 4분면 배치와 무광 색조 확인: 좌상 목재·우상 기와·좌하 회벽·우하 한지. 기와에 얕은 명암이 남고 완전 반복 타일링은 미검증. 원본 PNG 편집 없이 실제 GLB UV 적용 시험용이며 최종 ≤1K 규격 합격을 뜻하지 않음.
References in exact call order:
1. C:\workspace\joseon-assets\workbench\production\h1-style-expansion-2026-09-17/14_motgol_modules_props.png
2. C:\workspace\joseon-assets\sheets\approved-2026-09-17-h1\K2_H_doho_hero_options.png
```text
Create one SQUARE 1:1 game-ready ALBEDO MATERIAL ATLAS for the H1 Korean dark fantasy village in the references. Four precisely EQUAL square quadrants in a 2x2 grid, no gutters, NO text, labels, border, frame or shadow between quadrants. Each quadrant fills exactly its quarter. This is a completely flat orthographic texture image, NOT four physical samples, NOT a prop sheet, not a rendered wall.
TOP LEFT: worn muted warm brown Korean timber planks, 3 broad boards, sparse large grain strokes and a couple of restrained knots. Matte hand-painted low-noise wood, base warm umber, not orange, no shiny varnish.
TOP RIGHT: dark slate-gray Korean giwa ceramic roofing, 3 broad staggered rows of simple curved tiles, thin restrained seams and modest chipped marks. Shapes are drawn FLAT as diffuse material information, not physically raised 3D tiles; no directional shadow or highlight. Base medium-dark cool gray so it remains visible under low scene light, not black.
BOTTOM LEFT: aged warm gray-ivory Korean plaster, mostly a quiet broad matte surface, a few broad subtle worn patches, no brick showing through, no large cracks, no text or grime painting a scene.
BOTTOM RIGHT: unlit warm off-white HANJI paper, very subtle sparse fibrous marks and a few soft broad irregular flecks. No lattice bars, no lantern frame, no candles, no glow, no Chinese characters.
Match the H1 matte hand-painted Korean manhwa material grammar of reference1's village and reference2's LEFT H1 ONLY: large simple color areas, carefully restrained outlines, limited shallow value variation, no photographic microtexture. The wood is warm dark brown, roof cool charcoal gray, plaster warm grey ivory, hanji slightly pale tan. Colors must be clear albedo colors without environmental lighting.
CRITICAL: uniform flat illumination, NO gradients across a quadrant, NO ambient occlusion at quadrant edges, NO baked rim light, NO vignette, NO perspective, NO specular, NO cast shadow, NO extra objects. Keep each material's edges continuous as much as possible for repeated UV sampling. Straight quadrant division exactly50% horizontally/vertically. Output square 1024x1024.
```
