# #632 Element structure v1

Actual Godot actor/input/talisman/enemy-projectile before/after, eight normal-speed3s takes(24s total), 60fps recorded, identical camera/stats/seed/consumables/damage/hits/status/positions. Recorded60fps is not a realtime performance measurement.

Before: `8914e7c0633dfb45b8450f9c3218081cf46cc51a`. After game commit: `d66e6e8a`. New `core/vfx_elements.gd` and all source byte hashes are in `video_manifest.json`. Capture SHA `4d33ee22239e582f68be253ddb73cd826fb40fd588408ec11d9801f6c83cf07f` stayed unchanged. Both captures47/47 PASS; full combat metadata exact.

The comparison crop is fixed(280,80,720,540) scaled640x480 per side. Actual and full-engine footage use1280x720 original camera. Each take is [BEGIN,END), AVI zero-based counter N. Six photos pair the exact same engine frames.

Fire/cold preserve current radius1.5 AOE and3 target hits; lightning preserves existing single-target1 hit(no chain). Sal is the actual nachalnyeo enemy orb, never a new player spell. Low/strong talisman multipliers1.2/2.5 follow SPI20/150; sal area levels1/16 follow normal1/2.5 damage scaling. MP unchanged; belt5→4. Status details are a separate#634.

Original per-take sound is not byte-identical because existing Audio randomizes independent variation/pitch. The A/B and actual edit share the AFTER native soundtrack with exact800sample/frame trims. Full-engine videos retain each native soundtrack. Original sound fingerprints are preserved.

Logs include initial failures and final passes without removing error lines. Successful capture shutdown retains11 ObjectDB/6resources in-use teardown messages; no live runtime/shader error in valid captures. MovieMaker AVI intermediates remain local, excluded from git by size; `local_originals.json` records exact byte sizes and SHA256. Final MP4 full-engine source movies are preserved here. All original E2E phases referenced by copied logs include godot.raw.log and phase.json; merged console duplicates are omitted.

`archive_manifest.json` checks every archived byte. Each file<10MB and card total<50MB. Reproducible capture/encode scripts are in `capture_tools/`.
