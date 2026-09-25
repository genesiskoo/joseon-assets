"""Save the 12 common UI window states before/after #87 as compact JPEGs.

Usage: python capture_report.py --before <Godot main user://e2e> --after <Godot worktree user://e2e>
The capture sources are E2E outputs; this only converts format and measures fixed empty wood patches.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

NAMES = [
    "hud", "hover_npc", "hover_item", "character", "inventory", "skills",
    "dialog_merchant", "vendor", "dialog_shaman", "dialog_elder", "waypoint", "title",
]
BOXES = {
    "character_empty_wood": (220, 80, 390, 135),
    "inventory_empty_wood": (1140, 85, 1240, 295),
}


def sample(path: Path, box: tuple[int, int, int, int]) -> dict[str, float]:
    rgb = np.asarray(Image.open(path).convert("RGB").crop(box), dtype=np.float32) / 255.0
    hi = rgb.max(axis=2)
    lo = rgb.min(axis=2)
    sat = np.where(hi > 0, (hi - lo) / np.maximum(hi, 1e-6), 0)
    return {
        "median_s": round(float(np.median(sat)), 3),
        "median_v": round(float(np.median(hi)), 3),
        "vivid_pct": round(float(np.mean((sat > 0.45) & (hi > 0.30))) * 100.0, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    args = parser.parse_args()
    out = Path(__file__).resolve().parents[3] / "reports" / "87" / "ui_windows"
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"card": 87, "scenario": "ui_windows", "states": NAMES, "measurements": {}}
    for index, name in enumerate(NAMES, start=1):
        filename = f"ui_windows_{index:02d}_{name}.png"
        for phase, src in [("before", args.before / filename), ("after", args.after / filename)]:
            if not src.is_file():
                raise FileNotFoundError(src)
            with Image.open(src) as opened:
                img = opened.convert("RGB")
                if img.size != (1280, 720):
                    raise ValueError(f"unexpected capture size: {src} = {img.size}")
                img.save(out / f"{name}_{phase}.jpg", "JPEG", quality=82, optimize=True)
        if name in ("character", "inventory"):
            box_name = "character_empty_wood" if name == "character" else "inventory_empty_wood"
            box = BOXES[box_name]
            manifest["measurements"][box_name] = {
                "box_1280x720": list(box),
                "before": sample(args.before / filename, box),
                "after": sample(args.after / filename, box),
            }
    (out.parent / "metrics.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["measurements"], ensure_ascii=False, indent=2))
    print(f"saved 24 before/after JPEGs: {out}")


if __name__ == "__main__":
    main()
