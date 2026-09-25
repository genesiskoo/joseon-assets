"""Resize generated #87 raster sources into exact UI texture dimensions.

Only trims transparent padding and resamples; material design is image_gen output.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "prepared"
OUT.mkdir(exist_ok=True)
SPECS = {
    "panel": {"src": "panel_source_v1.png", "size": (400, 216),
              "slice_px": {"left": 16, "top": 43, "right": 16, "bottom": 15},
              "content_padding_px": {"left": 22, "top": 40, "right": 22, "bottom": 18}},
    "button": {"src": "button_source_v1.png", "size": (240, 50),
               "slice_px": {"left": 9, "top": 9, "right": 9, "bottom": 9},
               "content_padding_px": {"left": 11, "top": 10, "right": 11, "bottom": 10}},
    "orb": {"src": "orb_source_v1.png", "size": (144, 144),
            "center_open_radius_px": 50},
}

manifest = {"card": 87, "style": "#393 A coloured art + D2b dark wood inventory",
            "source_mode": "built-in image_gen; crop transparent padding and resample only", "parts": {}}
for name, spec in SPECS.items():
    source = Image.open(ROOT / spec["src"]).convert("RGBA")
    alpha = source.getchannel("A")
    box = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
    if box is None:
        raise ValueError(f"empty source: {name}")
    if name == "orb":
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        side = max(box[2] - box[0], box[3] - box[1])
        box = (round(cx-side/2), round(cy-side/2), round(cx+side/2), round(cy+side/2))
    target = source.crop(box).resize(spec["size"], Image.Resampling.LANCZOS)
    target.save(OUT / f"{name}.png", optimize=True)
    item = {"source": spec["src"], "source_size_px": list(source.size), "alpha_crop_px": list(box),
            "output": f"prepared/{name}.png", "output_size_px": list(spec["size"])}
    item.update({key: value for key, value in spec.items() if key not in ("src", "size")})
    arr = np.asarray(target, dtype=np.float32)
    if name == "panel":
        # Quiet content field, excluding frame/header. HSV V=max RGB, S=range/max.
        region = arr[56:197, 24:376, :3] / 255
        mx = region.max(axis=2)
        mn = region.min(axis=2)
        sat = np.where(mx > 0, (mx-mn) / np.maximum(mx, 1e-6), 0)
        item["content_median_s"] = round(float(np.median(sat)), 3)
        item["content_median_v"] = round(float(np.median(mx)), 3)
        item["content_vivid_pct"] = round(float(np.mean((sat > .45) & (mx > .30))) * 100, 3)
    if name == "orb":
        item["alpha_center"] = int(target.getchannel("A").getpixel((72, 72)))
        item["alpha_outside"] = int(target.getchannel("A").getpixel((0, 0)))
    if name == "panel":
        item["visible_rect_equals_input_rect"] = True
        item["small_panel_rule"] = "height < 96 or width < 160: flat ink panel with 1px brass line"
    if name == "button":
        item["visible_rect_equals_input_rect"] = True
        item["states"] = {
            "normal": [1.0, 1.0, 1.0],
            "hover": [1.25, 1.2, 1.05],
            "disabled": [0.45, 0.44, 0.42],
        }
    manifest["parts"][name] = item
    print(name, item)

manifest["parts"]["title_tab"] = {
    "source": "joseon/assets/sprites/ui/skin/title_tab.svg",
    "source_mode": "repo-native SVG recolor; not raster generation",
    "size_px": [96, 32], "slice_px": {"left": 8, "top": 8, "right": 8, "bottom": 8},
    "content_padding_px": {"left": 16, "top": 5, "right": 16, "bottom": 5},
    "placement": "horizontally centered on PanelUi top rail",
    "input": "decorative only; no tab click",
}
manifest["parts"]["close_x"] = {
    "source_mode": "repo-native draw_line in PanelUi",
    "visible_and_click_rect_px": [26, 26],
    "placement_px": "panel right -35, panel top +7",
    "action": "set_open(false), same path as Esc",
}
(ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
