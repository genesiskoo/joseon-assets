"""Pack #454 ImageGen originals and preview them through the game's UiSkin.

This never generates images, changes ItemDefs, or installs candidate art in game.
The same alpha16 / 8% padding / Lanczos contract as approved #393 is retained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8", newline="\n")


def dump(path: Path, data: object) -> None:
    put(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def pack(root: Path) -> dict:
    entries = json.loads((root / "inputs.json").read_text(encoding="utf-8"))["items"]
    sources = json.loads((root / "generation_sources.json").read_text(encoding="utf-8"))
    assert {r["item_id"] for r in sources["items"]} == {r["item_id"] for r in entries}
    results = []
    for e in entries:
        name = e["item_id"]
        src = root / "source/items" / f"{name}.png"
        raw = Image.open(src)
        if "A" not in raw.getbands():
            raise ValueError(f"{name}: source lacks a real alpha channel")
        art = raw.convert("RGBA")
        source_alpha = art.getchannel("A")
        if source_alpha.getextrema()[0] != 0 or source_alpha.getextrema()[1] < 250:
            raise ValueError(f"{name}: expected transparent background and near-opaque object (alpha>=250)")
        alpha = source_alpha.point(lambda a: a if a >= 16 else 0)
        bbox = alpha.getbbox()
        if bbox is None:
            raise ValueError(f"{name}: empty original")
        if bbox[0] == 0 or bbox[1] == 0 or bbox[2] == art.width or bbox[3] == art.height:
            raise ValueError(f"{name}: original object touches an edge")
        art.putalpha(alpha)
        art = art.crop(bbox)
        size = (80 * e["grid_w"], 80 * e["grid_h"])
        assert size == (e["output_width"], e["output_height"])
        pad = max(5, round(min(size) * .08))
        scale = min((size[0] - 2 * pad) / art.width, (size[1] - 2 * pad) / art.height)
        shown = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.Resampling.LANCZOS)
        out = Image.new("RGBA", size)
        out.alpha_composite(shown, ((size[0] - shown.width) // 2, (size[1] - shown.height) // 2))
        dest = root / "game/items" / f"{name}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        out.save(dest, optimize=True)
        visible = out.getchannel("A").getbbox()
        assert visible and visible[0] >= 2 and visible[1] >= 2
        assert visible[2] <= size[0] - 2 and visible[3] <= size[1] - 2
        assert out.getchannel("A").getextrema()[0] == 0 and out.getchannel("A").getextrema()[1] >= 250
        results.append(dict(e, source_size=list(raw.size), source_bbox=list(bbox), source_alpha=list(source_alpha.getextrema()), packed_alpha=list(out.getchannel("A").getextrema()),
                            source_sha256=sha(src), game_size=list(size), game_sha256=sha(dest),
                            visible_bbox=list(visible), definition_sha256=sha(Path(e["definition_path"]))))
    manifest = {"card": 454, "parent_card": 274, "status": "candidate_not_installed",
                "method": "built-in image_gen originals; approved #393 deterministic alpha16/8%/Lanczos packing",
                "logical_cell_px": 40, "output_scale": 2, "items": results}
    dump(root / "manifest.json", manifest)
    return manifest


def font(size: int):
    for path in ["C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def contact(root: Path, manifest: dict) -> None:
    sheet = Image.new("RGB", (1280, 720), (25, 23, 21))
    draw = ImageDraw.Draw(sheet)
    draw.text((26, 17), "D1 퀘스트 봉인물3 · #454", font=font(26), fill=(228, 216, 192))
    draw.text((26, 55), "확대 원화 + 40px 파일 축소 · 1×1칸 · 후보 / 게임 미반입", font=font(17), fill=(160, 150, 130))
    for i, e in enumerate(manifest["items"]):
        x, y = 22 + i * 421, 96
        draw.rectangle((x, y, x + 405, y + 588), fill=(31, 28, 24), outline=(77, 67, 52))
        raw = Image.open(root / "source/items" / (e["item_id"] + ".png")).convert("RGBA").crop(tuple(e["source_bbox"]))
        raw.thumbnail((345, 367), Image.Resampling.LANCZOS)
        sheet.paste(raw, (x + 202 - raw.width // 2, y + 202 - raw.height // 2), raw)
        draw.text((x + 19, y + 414), e["display_name"], font=font(22), fill=(229, 215, 190))
        draw.text((x + 19, y + 450), e["silhouette"], font=font(16), fill=(175, 162, 143))
        draw.text((x + 19, y + 493), "40px 파일 축소", font=font(16), fill=(175, 162, 143))
        draw.rectangle((x + 294, y + 490, x + 333, y + 529), fill=(23, 21, 19), outline=(101, 84, 66))
        art = Image.open(root / "game/items" / (e["item_id"] + ".png")).convert("RGBA").resize((40, 40), Image.Resampling.LANCZOS)
        sheet.paste(art, (x + 294, y + 490), art)
        draw.text((x + 19, y + 554), e["item_id"] + " · 80×80 RGBA", font=font(15), fill=(155, 147, 131))
    path = root / "qa"
    path.mkdir(parents=True, exist_ok=True)
    sheet.save(path / "overview.png", optimize=True)
    sheet.save(path / "overview.jpg", quality=85, optimize=True)


GDSCRIPT = r'''extends SceneTree
## #454: current ItemDef and UiSkin, candidate art in memory only. No installation.

class Plate extends Node2D:
	var skin
	var body: Font
	var heading: Font
	var rows: Array = []
	var references: Array = []
	var mode := "before"
	var dimensions := Vector2i(1280, 720)

	func label(at: Vector2, text: String, size: int = 16, bright: bool = false) -> void:
		draw_string(heading if bright else body, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color("e5d5bd") if bright else Color("a79b87"))

	func object_at(r: Rect2, row: Dictionary, future: bool, black: bool = false) -> void:
		if black:
			draw_rect(r, Color.BLACK)
			draw_rect(r, skin.SLOT_RIM, false, 1.0)
		else:
			skin.item_slot(self, r, true)
		var art = row.future if future else row.definition.icon
		if not skin.item_icon(self, r, art, 1.0, 8.0):
			var fs := 20 if r.size.x >= 80 else 16
			draw_string(body, r.position + Vector2(r.size.x * .5 - fs * .5, r.size.y * .5 + fs * .4), row.definition.glyph, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, row.definition.color)

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, dimensions), Color("211d19"))
		var title := "기존 표시" if mode == "before" else "후보 그림"
		if mode == "sizes": title = "30·48·60px 칸 크기 검수"
		label(Vector2(26, 36), "D1 퀘스트 봉인물3 · " + title, 24, true)
		label(Vector2(26, 65), "실제 공통 UiSkin · 현재 1×1칸/쌓기1 정의 · 후보는 검수 메모리에서만 사용", 15)
		if mode == "sizes":
			for i in rows.size():
				var row: Dictionary = rows[i]
				var x := 28 + i * 420
				label(Vector2(x, 120), row.spec.display_name, 20, true)
				for j in 3:
					var side: int = [30, 48, 60][j]
					var y := 170 + j * 170
					object_at(Rect2(x + 150, y, side, side), row, true)
					object_at(Rect2(x + 260, y, side, side), row, true, true)
					label(Vector2(x + 14, y + 26), "%dpx/칸" % side, 17)
			return
		label(Vector2(28, 166), "현재40px", 15)
		label(Vector2(28, 348), "검정40px", 15)
		for i in rows.size():
			var row: Dictionary = rows[i]
			var x := 80 + i * 405
			label(Vector2(x, 112), row.spec.display_name, 21, true)
			label(Vector2(x, 138), "1×1칸 · 퀘스트 · 쌓기1", 15)
			object_at(Rect2(x + 140, 190, 40, 40), row, mode != "before")
			object_at(Rect2(x + 140, 368, 40, 40), row, mode != "before", true)
		label(Vector2(28, 505), "같은 화풍 기준 · 기존 채택 D1", 18, true)
		for i in references.size():
			var row: Dictionary = references[i]
			var w: float = row.spec.grid_w * 40
			var h: float = row.spec.grid_h * 40
			var x := 340 + i * 250
			object_at(Rect2(x, 530, w, h), row, false)
			label(Vector2(x, 688), row.spec.display_name, 15)

var out_dir := ""
var mode := "before"
var pack_root := ""

func _initialize() -> void:
	_launch.call_deferred()

func _launch() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--root="): pack_root = arg.trim_prefix("--root=")
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
		if arg.begins_with("--out="): out_dir = arg.trim_prefix("--out=")
	if pack_root.is_empty() or out_dir.is_empty():
		push_error("root and out are required")
		quit(1)
		return
	var config = JSON.parse_string(FileAccess.get_file_as_string(pack_root.path_join("manifest.json")))
	var plate := Plate.new()
	plate.skin = load("res://ui/ui_skin.gd")
	var fonts = load("res://ui/ui_fonts.gd")
	plate.body = ThemeDB.fallback_font
	plate.heading = fonts.heading()
	plate.mode = mode
	plate.dimensions = Vector2i(1280, 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.size = plate.dimensions
	root.title = "#454 D1 소지품 후보 검수"
	for spec in config.items:
		var definition = load("res://data/items/%s.tres" % spec.item_id)
		assert(definition != null, "missing current definition")
		assert(definition.icon == null, "candidate current icon must be unspecified")
		assert(definition.size == Vector2i(spec.grid_w, spec.grid_h), "footprint mismatch")
		assert(definition.display_name == spec.display_name, "name mismatch")
		assert(definition.quest_item and definition.max_stack == 1, "quest/stack mismatch")
		var texture: Texture2D = null
		if mode != "before":
			var im := Image.load_from_file(pack_root.path_join("game/items/%s.png" % spec.item_id))
			assert(im != null and im.get_size() == Vector2i(spec.output_width, spec.output_height), "packed PNG mismatch")
			texture = ImageTexture.create_from_image(im)
			# Virtual future resource identity selects the real alpha-aware UiSkin path.
			# No file is written to res://assets, and this process is short-lived.
			texture.take_over_path("res://assets/sprites/ui/icons_a/items/%s.png" % spec.item_id)
		plate.rows.append({"definition": definition, "future": texture, "spec": spec})
	for id in ["paeraengi", "leather_shoes", "cotton_belt"]:
		var definition = load("res://data/items/%s.tres" % id)
		plate.references.append({"definition": definition, "future": null, "spec": {"display_name": definition.display_name, "grid_w": definition.size.x, "grid_h": definition.size.y}})
	root.add_child(plate)
	plate.queue_redraw()
	_capture.call_deferred(plate)

func _capture(plate: Plate) -> void:
	await process_frame
	await process_frame
	await create_timer(.35).timeout
	var image := root.get_texture().get_image()
	assert(image.get_size() == plate.dimensions, "capture dimensions mismatch")
	var path := out_dir.path_join("godot_%s.png" % mode)
	var err := image.save_png(path)
	print("GODOT_D1_454 %s %s · items3/footprints3/names3/render3" % ["PASS" if err == OK else "FAIL", path])
	quit(0 if err == OK else 1)
'''


def build(root: Path) -> None:
    manifest = pack(root)
    contact(root, manifest)
    put(root / "qa_godot.gd", GDSCRIPT)
    print("PASS #454 originals3 real alpha / source edges3 / packed PNG3 / footprints3 / SHA3")
    for e in manifest["items"]:
        print(f'  {e["item_id"]}: source{e["source_size"]} → {e["game_size"]}, bbox{e["visible_bbox"]}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    build(args.root)
