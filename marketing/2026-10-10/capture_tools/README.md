# Marketing capture #721

Only install these scripts in the dedicated temporary `627061d8` game worktree. Production gameplay files remain unchanged. Keep the scripts/specification in the marketing package for reproduction.

Copy `_marketing_capture.gd` and `_marketing_effects.gd` into `tests/e2e/scenarios/` in that checkout. Add the following entry to `SCENARIOS` in `tests/e2e/e2e_runner.gd`:

```gdscript
"_marketing_capture": "res://tests/e2e/scenarios/_marketing_capture.gd",
```

Run headless import once. Then run captures serially; no other graphical Godot process should run concurrently.

```powershell
godot --headless --path D:/CodexScratch/joseon-marketing721/game --import
python capture_marketing.py --game D:/CodexScratch/joseon-marketing721/game --out D:/CodexScratch/joseon-marketing721/output --track cave --ui both
python capture_marketing.py --game D:/CodexScratch/joseon-marketing721/game --out D:/CodexScratch/joseon-marketing721/output --track quest_accept --ui both
python capture_marketing.py --game D:/CodexScratch/joseon-marketing721/game --out D:/CodexScratch/joseon-marketing721/output --track quest_report --ui both
python capture_marketing.py --game D:/CodexScratch/joseon-marketing721/game --out D:/CodexScratch/joseon-marketing721/output --track all --ui both
python capture_marketing.py --game D:/CodexScratch/joseon-marketing721/game --out D:/CodexScratch/joseon-marketing721/output --track screenshots
```

Supported video tracks: `quest_accept`, `quest_report`, `cave`, `effect_fire`, `effect_cold`, `effect_lightning`, `effect_flurry`, `effect_crit`, `loot`, `boss`, `attack`, `imugi`. `--track all` records these video tracks only. Screenshots are a separate pass. `--encode-only` reuses that track/UI's existing `capture_master.avi` and `capture_raw.log`. `--keep-master` preserves the working AVI after verification.

Movie Maker initializes dimensions from project settings at boot. The runner sets temporary `override.cfg` display viewport dimensions to 1920×1080 before launch; the capture script sets the logical canvas back to the production 1280×720 contract using `CONTENT_SCALE_MODE_CANVAS_ITEMS`. Thus game rendering and movies are native 1080p while UI placement and input coordinates retain normal behavior. The 4K screenshot pass instead fixes a native 3840×2160 viewport and scales only its on-screen presentation.

The runner gives the temporary game a dedicated `JoseonHunters_wt/721-marketing` user directory and refuses the live main checkout. It uses the separate E2E save. UI-off uses CanvasItem visibility layers and viewport culling: hidden controls still receive the same input events. Label3D names, their child plates/element icons and the system cursor are hidden through camera render-layer exclusion; world 3D VFX and telegraph meshes remain. Developer FeelLab station meshes and labels are excluded in both UI-on and UI-off output. This works even when NPC/popup processing restores visible flags. It verifies original movie dimensions, actual 60 fps, audio stream, audible audio and complete MP4 decoding. No scaling filter is used. Native 4K PNG dimensions are asserted inside Godot and independently verified after copying.

The effect tracks inherit stationary-enemy showcase setup from `_feel_numbers_demo` on current plate A; damage/crit fixtures and prepared skills are documented in every manifest. The existing E2E `sure_hit` setting guarantees player hits; captures do not represent normal hit probability. Quest-report preparation clears the floor through the existing damage path before the captured report. Boss, imugi and completed-quest tracks carry spoiler tags. All media has per-file publication/spoiler/source/hash fields and a visual-selection note; inspect clips before editorial use. A failure preserves raw logs and working video and prints the raw error log.
