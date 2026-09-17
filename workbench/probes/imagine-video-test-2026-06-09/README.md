# Imagine Video Generation Test - 2026-06-09

## Purpose
Quick capability test of Grok's imagine video tools (image_gen + image_to_video) on a Joseon Hunters style character, following the official imagine skill guidelines.

## Workflow Used
1. Created clean animation-friendly source image with image_gen
   - Prompt incorporated project STYLE_BIBLE + lighting discipline (matte surfaces, single dominant soft light from upper-left, minimal rim, restrained highlights, clear silhouette)
   - Aspect ratio: 16:9
   - Subject: Gumiho (nine-tailed fox spirit) in calm idle pose, simple moonlit shrine clearing

2. Animated with image_to_video
   - Source: the generated still above
   - Duration: 6 seconds (preferred short shot length per skill)
   - Resolution: 720p
   - Prompt focus: subtle breathing + natural tail sway + gentle drifting foxfire embers + slow smooth camera push-in. Minimal motion, present tense, one clear camera move.

## Files
- gumiho_video_test_source.jpg — base frame (good first-frame composition per imagine video guidelines)
- gumiho_idle_test_6s_720p.mp4 — resulting video

## Notes
- Source image deliberately kept simpler than existing dramatic gumiho concept arts to reduce animation warping risk (per "Complex source image" guidance in imagine skill).
- This is a probe/test result. Not for direct use in production assets.
- Future tests could compare: different motions, reference_to_video with multiple refs, using existing project stills (e.g. sheets/ or concept/), or chaining multiple shots.

## Tool Versions
- image_gen (for source)
- image_to_video (default for video in imagine skill)
- Session: 019eab81-40cf-7642-80f2-f423c71349b6

Generated: 2026-06-09 ~17:32-17:33
