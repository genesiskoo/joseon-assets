"""Package native #467 originals at the locked 1×1 inventory footprint."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
GAME = Path("C:/workspace/joseon")
LABELS = {
    "pouch": "복주머니",
    "myeongdu": "명두",
    "yagwangju": "야광주",
    "jade_ring": "옥가락지",
    "gold_ring": "금가락지",
}
NOTES = {
    "pouch": "무명 천주머니 · 홍/남색 매듭",
    "myeongdu": "놋쇠 무구 거울 · 남색 걸이",
    "yagwangju": "청백 구슬 · 절제된 금속 걸이",
    "jade_ring": "담록색 옥 · 두꺼운 고리",
    "gold_ring": "두툼한 금 · 손마감 테두리",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def field(text: str, name: str, kind: str = "str") -> str | int:
    pattern = rf"^{re.escape(name)} = (.+)$"
    match = re.search(pattern, text, re.MULTILINE)
    assert match, name
    value = match.group(1)
    return int(value) if kind == "int" else value.strip('"')


def main() -> None:
    sources = json.loads((ROOT / "generation_sources.json").read_text(encoding="utf-8"))
    assert [r["id"] for r in sources["items"]] == list(LABELS)
    for dirname in ("source/items", "game/items", "qa"):
        (ROOT / dirname).mkdir(parents=True, exist_ok=True)
    records = []
    for row in sources["items"]:
        item_id = row["id"]
        definition = GAME / "data/items" / f"{item_id}.tres"
        spec = definition.read_text(encoding="utf-8")
        assert field(spec, "id") == item_id
        assert field(spec, "display_name") == LABELS[item_id]
        assert field(spec, "size") == "Vector2i(1, 1)"
        assert field(spec, "slot", "int") == (3 if item_id.endswith("ring") else 2)
        assert field(spec, "tier", "int") == {"pouch": 1, "myeongdu": 2, "yagwangju": 3, "jade_ring": 1, "gold_ring": 2}[item_id]
        native = Path(row["native_path"])
        assert native.is_file(), native
        variant = row.get("alternate_v1_native_path")
        if variant:
            older = ROOT / "source/items" / f"{item_id}.png"
            assert older.is_file() and digest(older) == digest(Path(variant))
            backup = ROOT / "game/variants" / f"{item_id}_v1.png"
            backup.parent.mkdir(parents=True, exist_ok=True)
            current_game = ROOT / "game/items" / f"{item_id}.png"
            if not backup.exists():
                assert current_game.is_file()
                shutil.copyfile(current_game, backup)
            original = ROOT / "source/items" / f"{item_id}_v2.png"
        else:
            original = ROOT / "source/items" / f"{item_id}.png"
        if original.exists():
            assert digest(original) == digest(native), item_id
        else:
            shutil.copyfile(native, original)
        raw = Image.open(original)
        assert raw.mode == "RGBA", (item_id, raw.mode)
        assert raw.getchannel("A").getextrema()[0] == 0
        assert raw.getchannel("A").getextrema()[1] >= 250
        alpha = raw.getchannel("A").point(lambda a: a if a >= 16 else 0)
        bbox = alpha.getbbox()
        assert bbox and 0 < bbox[0] < bbox[2] < raw.width and 0 < bbox[1] < bbox[3] < raw.height
        art = raw.copy()
        art.putalpha(alpha)
        art = art.crop(bbox)
        side, pad = 80, 6
        scale = min((side - 2 * pad) / art.width, (side - 2 * pad) / art.height)
        shown = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.Resampling.LANCZOS)
        packed = Image.new("RGBA", (side, side))
        packed.alpha_composite(shown, ((side - shown.width) // 2, (side - shown.height) // 2))
        dest = ROOT / "game/items" / f"{item_id}.png"
        packed.save(dest, optimize=True)
        visible = packed.getchannel("A").getbbox()
        assert visible and visible[0] >= 2 and visible[1] >= 2 and visible[2] <= 78 and visible[3] <= 78
        records.append({
            "item_id": item_id,
            "display_name": LABELS[item_id],
            "tier": field(spec, "tier", "int"),
            "slot": field(spec, "slot", "int"),
            "grid_w": 1,
            "grid_h": 1,
            "output_width": 80,
            "output_height": 80,
            "definition_path": definition.as_posix(),
            "definition_sha256": digest(definition),
            "source_path": original.relative_to(ROOT).as_posix(),
            "source_size": list(raw.size),
            "source_bbox": list(bbox),
            "source_alpha": list(raw.getchannel("A").getextrema()),
            "source_sha256": digest(original),
            "game_path": dest.relative_to(ROOT).as_posix(),
            "game_size": [80, 80],
            "visible_bbox": list(visible),
            "game_sha256": digest(dest),
            "note": NOTES[item_id],
            "alternate_v1_source_path": f"source/items/{item_id}.png" if variant else None,
            "alternate_v1_game_path": f"game/variants/{item_id}_v1.png" if variant else None,
        })
    manifest = {
        "card": 467,
        "parent_card": 274,
        "status": "candidate_not_installed",
        "method": "native image_gen originals, alpha16, 8percent padding, Lanczos packing",
        "logical_cell_px": 40,
        "output_scale": 2,
        "items": records,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    font_path = "C:/Windows/Fonts/malgun.ttf"
    heading = ImageFont.truetype(font_path, 22)
    body = ImageFont.truetype(font_path, 15)
    sheet = Image.new("RGB", (1280, 790), (26, 23, 21))
    draw = ImageDraw.Draw(sheet)
    draw.text((26, 20), "#467 D1 1칸 장신구 5종 — 원화 / 실제 40px 검수", font=heading, fill=(233, 215, 187))
    for i, record in enumerate(records):
        x, y = 22 + (i % 3) * 420, 70 + (i // 3) * 350
        draw.rectangle((x, y, x + 400, y + 328), fill=(34, 30, 27), outline=(85, 70, 52))
        art = Image.open(ROOT / record["source_path"]).crop(tuple(record["source_bbox"]))
        art.thumbnail((240, 218), Image.Resampling.LANCZOS)
        sheet.paste(art, (x + 18 + (240 - art.width) // 2, y + 12 + (218 - art.height) // 2), art)
        icon = Image.open(ROOT / record["game_path"])
        draw.rectangle((x + 303, y + 50, x + 343, y + 90), fill=(4, 4, 4), outline=(99, 82, 58))
        small = icon.resize((40, 40), Image.Resampling.LANCZOS)
        sheet.paste(small, (x + 303, y + 50), small)
        draw.rectangle((x + 295, y + 143, x + 375, y + 223), fill=(7, 7, 7), outline=(99, 82, 58))
        sheet.paste(icon, (x + 295, y + 143), icon)
        draw.text((x + 15, y + 248), record["display_name"], font=heading, fill=(229, 215, 190))
        draw.text((x + 15, y + 283), record["note"], font=body, fill=(180, 165, 142))
        draw.text((x + 15, y + 307), f"{record['item_id']} · 80×80 RGBA · T{record['tier']}", font=body, fill=(151, 141, 124))
    sheet.save(ROOT / "qa/overview.png", optimize=True)
    sheet.save(ROOT / "qa/overview.jpg", quality=84, optimize=True)
    print("PACKED", len(records), [(r["item_id"], r["source_size"], r["visible_bbox"]) for r in records])


if __name__ == "__main__":
    main()
