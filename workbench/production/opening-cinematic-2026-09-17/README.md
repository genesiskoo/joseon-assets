# Joseon Hunters — Opening cinematic pilot

2026-09-17. Three completed Seedance 2.5 trial clips. These are individual shot tests, not a finished 90-second opening. No clip has been promoted to an official game asset.

| Shot | Video | Preliminary sample review |
|---|---|---|
| OP04 — nine shadow reflections | [Play](clips/OP04_v001_seedance25_720p.mp4) | Nine tips persist; reduce the large bend around 4.5–5.5s |
| OP06 — two villagers | [Play](clips/OP06_v001_seedance25_720p.mp4) | Support/sitting action holds; slight downward camera reframing |
| OP11 — Doho | [Play](clips/OP11_v001_seedance25_720p.mp4) | Hat, face, sword and grip hold; strengthen subtle acting |

All three: 1280×720, 24fps, 241 frames, 10.041667 seconds, H.264, no audio stream. Full decode passed. Visual review uses 21 samples per clip at 0.5-second intervals plus full-resolution 0/5/10s frames; this does not establish full-speed playback approval. Doho's feet are offscreen, so step count and grounding are not verified.

- [Full production manifest](metadata/manifest.json): submitted prompts, exact media UUIDs, jobs, results, estimates, technical outputs and SHA-256 inventory.
- [OP04 review](review/OP04_contact_2fps.jpg) · [OP06 review](review/OP06_contact_2fps.jpg) · [OP11 review](review/OP11_contact_2fps.jpg).
- [Detailed Korean report](C:/workspace/joseon/docs/design/opening_cinematic_pilot_2026-09-17.md).

Keyframes: built-in ImageGen, six generated candidates/revisions, three selected. Actual backend image model ID not exposed. This pilot follows the D03 style branch in its original plan; concurrent world-style explorations remain separate unselected candidates.

Estimated Higgsfield video cost: 65×3=195 credits. Image generation, soundtrack and editing excluded. Per-job actual billing is not available; shared account balance cannot isolate these clips. Final observed balance: 2,824 (Ultra).

OP11 first submission returned no job:

```text
seedance_2_5 backend request failed (429): not_enough_boost_credits
```

One identical retry after OP04 completed was accepted and finished. No model change or credit purchase. Exact underlying limit is not established by this response.

Original PNGs and MP4s are preserved. `metadata/upload_refs/` holds the JPEG copies actually sent as start images. `review/` holds derived QA frames; the original clips were not edited.
