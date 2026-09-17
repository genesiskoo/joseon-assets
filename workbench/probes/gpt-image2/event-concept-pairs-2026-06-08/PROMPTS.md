# GPT Image 2 Event Concept Pairs

Generated with the built-in `image_gen` workflow on 2026-06-08.

## Source Documents

- `C:/workspace/joseon/docs/design/storyline.md`
  - Cutscene 0: pansori opening, Motgol falls into sickness, Doho enters the
    ruined market.
  - Cutscene 6: Gumiho appears in the deepest boss chamber, Cheongyeon's vision
    warns Doho.
- `C:/workspace/joseon/docs/design/concept_art_list.md`
  - CA-S0 and CA-S6 are trailer/event-cut priority scenes.
- `C:/workspace/joseon/docs/design/narrative.md`
  - Doho: wandering Taoist, black gat, grey scarf, brown practical dopo, sword
    carried like a staff, sly but serious when needed.
  - Cheongyeon: shamanic vision, fan and ritual bells.
  - Gumiho: human-form nine-tailed fox boss, crimson and muted gold hanbok.

## Shared Rules

- 1536x1024 landscape event concept art.
- Korean Joseon visual identity.
- No subtitles, logo, watermark, UI, or readable text.
- No gore or heavy horror tone; use visual darkness while preserving the
  "Joseon groove fantasy" tone.
- Matte lighting, minimal specular highlights, no glossy skin, no over-rendered
  reflections, no continuous rim light.

## Images

1. `01-cut0-motgol-arrival-cel-animation.png`
   - Scene: Doho enters the abandoned Motgol market after the pansori opening.
   - Style: premium hand-drawn cel-animation key visual.
   - Notes: strong composition and clear Doho silhouette; best candidate for a
     trailer-intro event still.
2. `02-cut0-motgol-arrival-sumukhwa.png`
   - Scene: same Cutscene 0 moment.
   - Style: Korean sumukhwa / sumuk-damchae on aged hanji.
   - Notes: good use of negative space and tail-shaped ink cloud. Stronger as
     a poetic interstitial than a literal storyboard frame.
3. `03-cut6-gumiho-appearance-cel-animation.png`
   - Scene: Doho confronts the human-form Gumiho while Cheongyeon's vision
     warns him.
   - Style: cel-animation target.
   - Notes: strong character staging. The render leans slightly cinematic
     painterly; for stricter cel style, repeat with `flat anime cel shading`,
     `clean color shapes`, and `no painterly texture`.
4. `04-cut6-gumiho-appearance-sumukhwa.png`
   - Scene: same Cutscene 6 moment.
   - Style: Korean sumukhwa / sumuk-damchae.
   - Notes: strongest mood candidate for the boss-reveal event; Gumiho, Doho,
     and Cheongyeon's vision remain readable.

## Reuse Prompt Fixes

- Strict cel version:

```text
flat anime cel shading, clean two-step shadow shapes, crisp inked outlines,
painted background, no painterly brush texture on characters, no photoreal
rendering, no glossy highlights
```

- Stricter ink version:

```text
ink density and negative space only, sparse diluted color wash, no digital
lighting, no glowing edges, no hard specular highlights, no red artist seal
```
