"""#132 approved-board prop inputs: small review sheets, never model textures."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT.parents[2] / "reports" / "132"
OUT.mkdir(parents=True, exist_ok=True)


def sheet(names: list[str], target: str) -> None:
    cols = 2 if len(names) == 4 else 3
    rows = 2 if len(names) == 4 else 1
    canvas = Image.new("RGB", (1280, 720 if rows == 2 else 480), (20, 23, 29))
    draw = ImageDraw.Draw(canvas)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 24) if font_path.exists() else ImageFont.load_default()
    pad = 20
    cell_w = (canvas.width - pad * (cols + 1)) // cols
    cell_h = (canvas.height - pad * (rows + 1)) // rows
    for index, name in enumerate(names):
        x = pad + (index % cols) * (cell_w + pad)
        y = pad + (index // cols) * (cell_h + pad)
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=9, fill=(36, 38, 43), outline=(79, 81, 85), width=2)
        source = Image.open(ROOT / "refs" / f"{name}.png").convert("RGBA")
        source.thumbnail((cell_w - 32, cell_h - 62), Image.Resampling.LANCZOS)
        inset = Image.new("RGBA", source.size, (36, 38, 43, 255))
        inset.alpha_composite(source)
        canvas.paste(inset.convert("RGB"), (x + (cell_w - source.width) // 2, y + 14 + (cell_h - 62 - source.height) // 2))
        draw.text((x + 20, y + cell_h - 38), name.replace("_", " ").upper(), font=font, fill=(232, 223, 207))
    canvas.save(OUT / target, quality=76, optimize=True)


sheet(["bone_heap", "roots", "nest", "palisade"], "den_refs.jpg")
sheet(["seal_stone", "pillar", "broken_statue"], "bongmil_refs.jpg")
