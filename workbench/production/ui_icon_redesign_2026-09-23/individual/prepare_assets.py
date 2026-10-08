"""Pack approved ImageGen paintings as reusable transparent items and square skills.

Run from any directory: python prepare_assets.py. Source PNGs remain untouched.
The game-ready item canvas is 2x its 40px inventory footprint, with no frame.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
GAME = ROOT / "game"
QA = ROOT / "qa"
ITEMS = {
    "hwando": (1, 3),
    "cotton_dopo": (2, 3),
    "leather_shoes": (2, 2),
    "paeraengi": (2, 2),
    "mukham": (1, 2),
    "cotton_belt": (2, 1),
    "silver_ring": (1, 1),
    "jade_charm": (1, 1),
    "hp_potion": (1, 1),
    "mp_potion": (1, 1),
    "talisman_fire": (1, 1),
}
SKILLS = (
    "slash",
    "lunge",
    "whirlwind",
    "fire_talisman",
    "frost_talisman",
    "power_shield",
)
DARK = (23, 21, 19)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pack_item(name: str, footprint: tuple[int, int]) -> dict:
    source = SOURCE / "items" / f"{name}.png"
    image = Image.open(source).convert("RGBA")
    alpha = image.getchannel("A").point(lambda value: value if value >= 16 else 0)
    image.putalpha(alpha)
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError(f"{name}: source has no visible alpha")
    image = image.crop(bbox)
    width, height = (footprint[0] * 80, footprint[1] * 80)
    pad = max(5, round(min(width, height) * 0.08))
    scale = min((width - 2 * pad) / image.width, (height - 2 * pad) / image.height)
    shown = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(shown, ((width - shown.width) // 2, (height - shown.height) // 2))
    output = GAME / "items" / f"{name}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)
    out_alpha = canvas.getchannel("A")
    if out_alpha.getextrema()[0] != 0 or out_alpha.getextrema()[1] < 240:
        raise ValueError(f"{name}: lost transparent silhouette or opaque subject")
    return {"id": name, "footprint": list(footprint), "source_size": list(Image.open(source).size),
            "source_sha256": digest(source), "game_size": [width, height], "game_sha256": digest(output),
            "visible_bbox": list(out_alpha.getbbox())}


def pack_skill(name: str) -> dict:
    source = SOURCE / "skills" / f"{name}.png"
    image = Image.open(source).convert("RGBA")
    base = Image.new("RGBA", image.size, (*DARK, 255))
    base.alpha_composite(image)
    output = GAME / "skills" / f"{name}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").resize((128, 128), Image.Resampling.LANCZOS).save(output, optimize=True)
    return {"id": name, "source_size": list(image.size), "source_sha256": digest(source),
            "game_size": [128, 128], "game_sha256": digest(output)}


def draw_qa() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    # Every item is shown at its real 40px-cell footprint with a separate slot.
    sheet = Image.new("RGB", (640, 470), (35, 29, 24))
    draw = ImageDraw.Draw(sheet)
    for index, (name, (cells_x, cells_y)) in enumerate(ITEMS.items()):
        col, row = index % 4, index // 4
        x, y = 10 + col * 158, 18 + row * 150
        w, h = cells_x * 40, cells_y * 40
        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=DARK, outline=(87, 76, 66), width=1)
        icon = Image.open(GAME / "items" / f"{name}.png").convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
        sheet.paste(icon, (x, y), icon)
        draw.text((x, y + 123), name, fill=(225, 213, 193))
    sheet.save(QA / "items_40px.png", optimize=True)

    sizes = (24, 30, 48, 60)
    preview = Image.new("RGB", (660, 466), (35, 29, 24))
    draw = ImageDraw.Draw(preview)
    for row, name in enumerate(SKILLS):
        draw.text((12, 19 + row * 74), name, fill=(225, 213, 193))
        image = Image.open(GAME / "skills" / f"{name}.png").convert("RGB")
        for col, size in enumerate(sizes):
            x, y = 169 + col * 117, 8 + row * 74
            draw.rectangle((x - 2, y - 2, x + size + 1, y + size + 1), outline=(111, 92, 66), width=1)
            preview.paste(image.resize((size, size), Image.Resampling.LANCZOS), (x, y))
            if row == 0:
                draw.text((x, 440), f"{size}px", fill=(225, 213, 193))
    preview.save(QA / "skills_24_30_48_60px.png", optimize=True)


def main() -> None:
    items = [pack_item(name, footprint) for name, footprint in ITEMS.items()]
    skills = [pack_skill(name) for name in SKILLS]
    draw_qa()
    manifest = {"method": "built-in image_gen sources; deterministic Pillow alpha cleanup and Lanczos packing",
                "reference_style": "A_painted.png", "reference_items": "D1_inventory_objects.png",
                "logical_cell_px": 40, "items": items, "skills": skills}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS {len(items)} transparent items + {len(skills)} opaque skills; QA previews written")


if __name__ == "__main__":
    main()
