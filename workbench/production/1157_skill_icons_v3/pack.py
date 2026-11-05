# 후보 → 128/64/40 내보내기 + 비교 띠(jpg) — #1157
import sys, json, hashlib, pathlib
from PIL import Image, ImageDraw
D = pathlib.Path(__file__).parent
RAW, EXP = D / "raw", D / "exports"
EXP.mkdir(exist_ok=True)
OLD = pathlib.Path(r"C:/workspace/joseon/assets/sprites/ui/icons_a/skills")

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def square(im):
    w, h = im.size; s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))

def cell(im, size=40, inner=34):
    c = Image.new("RGB", (size, size), (58, 44, 30))  # 나무 틀 흉내
    d = ImageDraw.Draw(c); d.rectangle([0, 0, size - 1, size - 1], outline=(150, 118, 70))
    c.paste(im.convert("RGB").resize((inner, inner), Image.LANCZOS), ((size - inner) // 2, (size - inner) // 2))
    return c

def export(sid):
    out = {}
    for v in "AB":
        p = RAW / f"{v}_{sid}.png"
        if not p.exists(): continue
        im = square(Image.open(p).convert("RGBA"))
        rec = {"raw": p.name, "raw_size": Image.open(p).size, "raw_sha256": sha(p)}
        for s in (128, 64, 40):
            q = EXP / f"{v}_{sid}_{s}.png"
            im.resize((s, s), Image.LANCZOS).save(q)
            rec[f"e{s}"] = q.name; rec[f"e{s}_sha256"] = sha(q)
        out[v] = rec
    return out

def strip(sids, name):
    # 한 줄 = 칸: A 256 · B 256 · A 40칸 · B 40칸 · 옛 이웃 아이콘 40칸 셋
    neigh = ["thunder_lore", "whirlwind", "seal_array", "hide", "clone"]
    H = 256; rows = []
    for sid in sids:
        row = Image.new("RGB", (256 * 2 + 20 + 48 * 7, H), (24, 22, 20))
        x = 0
        for v in "AB":
            p = RAW / f"{v}_{sid}.png"
            if p.exists(): row.paste(square(Image.open(p).convert("RGB")).resize((256, 256), Image.LANCZOS), (x, 0))
            x += 256
        x += 20
        for v in "AB":
            p = RAW / f"{v}_{sid}.png"
            if p.exists(): row.paste(cell(square(Image.open(p).convert("RGBA")).resize((128, 128), Image.LANCZOS)), (x, 108))
            x += 48
        for n in neigh:
            row.paste(cell(Image.open(OLD / f"{n}.png").convert("RGBA")), (x, 108)); x += 48
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, H * len(rows) + 4 * (len(rows) - 1)), (0, 0, 0))
    for i, r in enumerate(rows): sheet.paste(r, (0, i * (H + 4)))
    if sheet.width > 1280: sheet = sheet.resize((1280, int(sheet.height * 1280 / sheet.width)), Image.LANCZOS)
    sheet.save(D / f"{name}.jpg", quality=86)

if __name__ == "__main__":
    sids = sys.argv[2:]
    man = D / "outputs.json"
    data = json.loads(man.read_text(encoding="utf-8")) if man.exists() else {}
    for s in sids: data[s] = export(s)
    man.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    strip(sids, sys.argv[1])
    print("ok", sys.argv[1])
