# Imagine Video (i2v) Test from Existing GPT-Image2 Probes
Date: 2026-06-09
Sources: workbench/probes/gpt-image2/

## Selection Criteria (per imagine skill guidelines)
- Preferred sources with relatively clear silhouettes and readable large shapes.
- Environments (background kit) prioritized for reliability — slow camera moves + atmospheric elements (mist, lights, talismans) animate cleanly.
- Narrative event stills selected when they had strong depth/composition (hero + distant threat) rather than heavy particle/energy overload.
- Avoided most heavy effect-heavy character shots and anything with dense UI or overly intricate busy geometry where possible.
- All sources are 1536x1024 landscape from the event/background probe batches.

## Selected & Animated

### 01 - Motgol Arrival (event-cel-like)
Source: event-cel-like-01-2026-06-08/01-cut0-motgol-arrival-cel-like-01.png
- Strong back-view hero (Doho) + massive gumiho silhouette in the sky.
- Good candidate for trailer-style slow push + environmental wind on talismans.
Video: 01_motgol_arrival_6s_720p.mp4

Prompt used:
"From behind, the swordsman in a traditional Korean gat hat and brown coat stands in the ruined moonlit village. In the distant sky, the giant glowing nine-tailed fox spirit silhouette shifts very subtly. Paper talismans, banners and debris flutter gently in the night wind. Slow, smooth camera push forward following the character down the path, gradually revealing more of the destroyed market and strengthening the presence of the fox spirit in the clouds. Atmospheric, mysterious, restrained motion only. No sudden actions from the character."

### 02 - Village Background
Source: background-kit-2026-06-09/joseon_background_village_v1.png
- Wide Joseon mountain village at dusk with jangseung, thatched roofs, mountains.
- Excellent for environmental motion: mist, window lights, hanging talismans.
Video: 02_village_background_6s_720p.mp4

Prompt used:
"Wide establishing view of a traditional Joseon-era mountain village at dusk with mountains in the background. Gentle mist drifts slowly between thatched roofs and wooden structures. Warm lights glow in windows. Talismans hanging from the large jangseung totem and wooden eaves sway very subtly in a light breeze. Slow, smooth, cinematic camera pan from left to right across the village path, or a very gentle forward dolly. Calm, atmospheric, mysterious mood with minimal but living environmental motion."

### 03 - Forest Clearing
Source: background-kit-2026-06-09/joseon_background_forest_v2.png
- Night forest with giant sacred pine, talismans, blue spirit flames on ground.
- Very animation-friendly: mist, subtle flame flicker, paper charm movement, parallax on rocks.
Video: 03_forest_clearing_6s_720p.mp4

Prompt used:
"Deep night forest clearing dominated by a massive ancient pine tree with talismans tied around its trunk. Small blue spirit flames flicker softly on the ground among mossy rocks and smaller sacred markers. Mist moves slowly between the trees. Very slow, smooth camera push forward through the clearing toward the great tree, with gentle parallax on foreground rocks and talismans. Dark, sacred, mysterious atmosphere. Only subtle natural motion from mist, flames and slight sway of paper charms."

## Notes & Recommendations
- Background shots (02 and 03) are generally safer and more predictable for first i2v passes.
- The arrival shot (01) is the most "cinematic event" of the batch and worth reviewing for how well the distant gumiho silhouette and foreground talismans hold up under motion.
- If results show warping on complex energy or multiple characters, next tests should either:
  - Use image_edit first to simplify the source (reduce effects, flatten lighting)
  - Or craft prompts that explicitly lock character poses and only move camera + very light secondary elements.
- All videos are 6 seconds @ 720p as recommended by the imagine video guidelines (short shots, frequent cuts).

## Next possible tests from this folder
- Gumiho appearance chamber scenes (cel-like and cel-animation versions)
- Other backgrounds (dungeon, representative)
- Keyart calibration images (with "camera move only" prompts)
- Sumukhwa style versions for different motion character

Generated via image_to_video on existing approved/probe GPT-Image2 stills.
