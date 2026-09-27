"""Freeze #467 visual review and prove that no game runtime file changed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image


ROOT = Path(__file__).resolve().parent
GAME_MAIN = Path("C:/workspace/joseon")
GAME_WT = Path("C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon")
REPORT = ROOT.parents[2] / "reports/467/2026-09-28"
GALLERY = GAME_WT / "docs/art/467_d1_accessories"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_files(game: Path) -> list[Path]:
    return sorted((game / "assets/sprites/ui/icons_a").rglob("*.png")) + sorted((game / "data/items").glob("*.tres"))


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "generation_sources.json").read_text(encoding="utf-8"))
    assert len(manifest["items"]) == len(sources["items"]) == 5
    assert [x["item_id"] for x in manifest["items"]] == [x["id"] for x in sources["items"]]
    assert sources["items"][2]["id"] == "yagwangju" and sources["items"][2]["alternate_v1_native_path"]
    assert manifest["items"][2]["source_path"].endswith("yagwangju_v2.png")
    for row in manifest["items"]:
        src = ROOT / row["source_path"]
        icon = ROOT / row["game_path"]
        assert src.is_file() and icon.is_file()
        assert digest(src) == row["source_sha256"]
        assert digest(icon) == row["game_sha256"]
        raw = Image.open(src)
        png = Image.open(icon)
        assert raw.mode == png.mode == "RGBA" and png.size == (80, 80)
        assert png.getchannel("A").getextrema() == (0, 255)
        assert row["visible_bbox"] == list(png.getchannel("A").getbbox())
        assert digest(GAME_WT / "data/items" / f"{row['item_id']}.tres") == row["definition_sha256"]
    main = runtime_files(GAME_MAIN)
    wt = runtime_files(GAME_WT)
    main_rel = [p.relative_to(GAME_MAIN) for p in main]
    wt_rel = [p.relative_to(GAME_WT) for p in wt]
    assert main_rel == wt_rel
    byte_mismatches = [str(rel) for rel in main_rel if digest(GAME_MAIN / rel) != digest(GAME_WT / rel)]
    content_mismatches = [
        str(rel) for rel in main_rel
        if (GAME_MAIN / rel).read_bytes().replace(b"\r\n", b"\n")
        != (GAME_WT / rel).read_bytes().replace(b"\r\n", b"\n")
    ]
    assert not content_mismatches, content_mismatches[:20]
    icons = [rel for rel in main_rel if rel.suffix == ".png"]
    assert len(icons) == 42, len(icons)
    REPORT.mkdir(parents=True, exist_ok=True)
    GALLERY.mkdir(parents=True, exist_ok=True)
    images = ["overview.jpg"]
    for mode in ("forty", "sizes"):
        raw = ROOT / "qa" / f"godot_{mode}.png"
        assert raw.is_file()
        jpg = ROOT / "qa" / f"godot_{mode}.jpg"
        Image.open(raw).convert("RGB").save(jpg, quality=86, optimize=True)
        images.append(jpg.name)
    gallery = []
    for name in images:
        src = ROOT / "qa" / name
        assert src.stat().st_size <= 300_000, (name, src.stat().st_size)
        shutil.copyfile(src, REPORT / name)
        shutil.copyfile(src, GALLERY / name)
        gallery.append({"filename": name, "bytes": src.stat().st_size, "sha256": digest(src)})
    result = {
        "card": 467,
        "candidate_count": 5,
        "selected_yagwangju_variant": "v2_short_loop_large_pearl",
        "previous_yagwangju_variant_preserved": True,
        "runtime_game_files_compared": len(main_rel),
        "existing_runtime_png": len(icons),
        "runtime_eol_normalized_match_main": True,
        "runtime_byte_differences_due_to_line_endings": byte_mismatches,
        "item_def_sha_match_manifest": True,
        "godot_ui_skin_modes": ["forty", "sizes"],
        "gallery": gallery,
    }
    (ROOT / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (REPORT / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("PASS #467 5 RGBA icons, 2 Godot UiSkin modes, 42 existing PNG and", len(main_rel), "runtime files unchanged, 3 JPG")


if __name__ == "__main__":
    main()
