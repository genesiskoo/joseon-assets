"""#1099 이야기 두루마리 겹 정리 + 합성 미리보기.
사용: python -E -P compose.py <scroll_A 폴더>
 - out/<job>/<job>.png → clean/<job>.png (흰 바탕 정리: 밝기 0.95 위 = 순백)
 - 묶음 겹(villagers · slashes) → 연결 덩어리로 잘라 clean/<job>_<n>.png
 - layout.json(배치표, 1536x1024 두루마리 좌표) 대로 한지 위에 곱해 preview_s0/s4/s5.png
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = sys.argv[1]
OUT, CLEAN = os.path.join(ROOT, "out"), os.path.join(ROOT, "clean")
os.makedirs(CLEAN, exist_ok=True)
W, H = 1536, 1024


def clean(job):
    p = os.path.join(OUT, job, job + ".png")
    if not os.path.exists(p):
        return None
    src = Image.open(p)
    if src.mode == "RGBA":  # Codex가 가끔 투명 바탕으로 낸다 → 흰 종이에 눌러 편다
        rgba = np.asarray(src).astype(np.float32) / 255.0
        a = rgba[..., :3] * rgba[..., 3:4] + (1.0 - rgba[..., 3:4])
    else:
        a = np.asarray(src.convert("RGB")).astype(np.float32) / 255.0
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    white = (lum > 0.95) & (sat < 0.08)
    a[white] = 1.0
    im = Image.fromarray((a * 255).astype(np.uint8))
    im.save(os.path.join(CLEAN, job + ".png"))
    return im


def split(im, job, min_area=1500):
    """흰 바탕 묶음 겹을 덩어리로 자른다(번진 먹을 잇도록 흐림 → 문턱)."""
    g = np.asarray(im.convert("L")).astype(np.float32) / 255.0
    mask = Image.fromarray(((g < 0.9) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(25))
    m = np.asarray(mask) > 0
    lab = np.zeros(m.shape, np.int32)
    n = 0
    boxes = []
    ys, xs = np.nonzero(m)
    seen = np.zeros(m.shape, bool)
    for y0, x0 in zip(ys[::97], xs[::97]):
        if seen[y0, x0]:
            continue
        stack = [(y0, x0)]
        seen[y0, x0] = True
        y1 = y2 = y0; x1 = x2 = x0; area = 0; pix = []
        while stack:
            y, x = stack.pop(); area += 1; pix.append((y, x))
            y1, y2, x1, x2 = min(y1, y), max(y2, y), min(x1, x), max(x2, x)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True; stack.append((yy, xx))
        if area >= min_area:
            boxes.append((x1, y1, x2 + 1, y2 + 1, pix))
    boxes.sort(key=lambda b: (b[1] // 300, b[0]))
    out = []
    src = np.asarray(im).copy()
    for i, (bx1, by1, bx2, by2, pix) in enumerate(boxes):
        b = (bx1, by1, bx2, by2)
        keep = np.zeros(m.shape, bool)
        ys_, xs_ = zip(*pix); keep[list(ys_), list(xs_)] = True
        part = src.copy(); part[~keep] = 255  # 상자가 겹쳐도 옆 덩어리는 안 딸려 온다
        c = Image.fromarray(part).crop(b)
        name = f"{job}_{i}"
        c.save(os.path.join(CLEAN, name + ".png"))
        out.append((name, b))
    return out


def paper():
    rng = np.random.default_rng(7)
    base = np.array([236, 226, 204], np.float32) / 255.0
    low = Image.fromarray((rng.random((H // 128, W // 128)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    fib = Image.fromarray((rng.random((H, W)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    n = (np.asarray(low) / 255.0 - 0.5) * 0.018 + (np.asarray(fib) / 255.0 - 0.5) * 0.03
    return np.clip(base[None, None, :] + n[..., None], 0, 1)


def place(canvas, name, box, dilute=0.0, blank=False):
    """box = [x, y, w] (높이는 비율대로) · 곱하기 · dilute = 회색으로 빠짐 · blank = 빈 한지 자리(흐린 테만)."""
    src = Image.open(os.path.join(CLEAN, name + ".png")).convert("RGB")
    x, y, w = box
    h = int(src.height * w / src.width)
    src = src.resize((w, h), Image.LANCZOS)
    a = np.asarray(src).astype(np.float32) / 255.0
    if dilute:
        a = 1.0 - (1.0 - a) * (1.0 - dilute)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
    if blank:
        ink = 1.0 - sub.mean(axis=2)
        m = Image.fromarray((np.clip(ink * 3, 0, 1) * 255).astype(np.uint8))
        edge = np.asarray(m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.8))) / 255.0
        inside = np.asarray(m.filter(ImageFilter.GaussianBlur(0.8))) / 255.0
        pap = paper()[y0:y1, x0:x1]
        region = canvas[y0:y1, x0:x1]
        region[:] = region * (1 - inside[..., None]) + pap * inside[..., None]
        region[:] = region * (1 - 0.35 * np.clip(edge * 2, 0, 1)[..., None])
        return
    canvas[y0:y1, x0:x1] *= sub


def ring(canvas, name, box, grow=28):
    """도호 둘레만 번짐이 비켜 감 — 몸 모양을 키운 자리에 빈 한지를 깐다(D-123 §1-3)."""
    src = Image.open(os.path.join(CLEAN, name + ".png")).convert("L")
    x, y, w = box
    h = int(src.height * w / src.width)
    ink = 255 - np.asarray(src.resize((w, h), Image.LANCZOS))
    m = Image.new("L", (W, H), 0)
    m.paste(Image.fromarray(((ink > 25) * 255).astype(np.uint8)), (x, y))
    m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1)).filter(ImageFilter.GaussianBlur(grow * 0.6))
    k = (np.asarray(m) / 255.0)[..., None]
    canvas[:] = canvas * (1 - k) + paper() * k


def bleed(canvas, cx, cy, radius, strength, seed=3):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - cx) / 1.6) ** 2 + (yy - cy) ** 2)
    noise = np.asarray(Image.fromarray((rng.random((H // 24, W // 24)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)) / 255.0
    f = np.clip(1.0 - d / (radius * (0.7 + 0.6 * noise)), 0, 1) ** 1.5 * strength
    canvas *= (1.0 - f * 0.35)[..., None]


def compose(layout, state):
    c = paper()
    L = layout
    for name in L["always"]:
        place(c, name, L["boxes"][name])
    kills = state.get("kills", [])
    bleed(c, *L["tavern"], radius=160 + 170 * len(kills), strength=0.6 + 0.15 * len(kills))
    grey = set(L["grey_order"][: L["grey_per_kill"] * len(kills)])
    for name in L["villagers"]:
        place(c, name, L["boxes"][name], dilute=0.72 if name in grey else 0.0)
    if state.get("empty"):
        place(c, "L04_jumo_child", L["boxes"]["L04_jumo_child"], blank=True)
    else:
        place(c, "L04_jumo_child", L["boxes"]["L04_jumo_child"])
    for k in kills:
        for name in L["kill_layers"][k]:
            place(c, name, L["boxes"][name])
    if state.get("streams"):
        place(c, "L10_nine_streams", L["boxes"]["L10_nine_streams"])
    if state.get("streams"):
        ring(c, state["doho"], L["boxes"][state["doho"]])
    place(c, state["doho"], L["boxes"][state["doho"]])
    if state.get("gold"):
        gx, gy = L["gold"]
        yy, xx = np.mgrid[0:H, 0:W]
        g = np.exp(-(((xx - gx) ** 2 + (yy - gy) ** 2) / (2 * 3.0 ** 2)))[..., None]
        c = c * (1 - g) + np.array([0.85, 0.66, 0.22]) * g
    return Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8))


if __name__ == "__main__":
    jobs = sorted(d for d in os.listdir(OUT) if os.path.isdir(os.path.join(OUT, d)))
    made = {}
    for j in jobs:
        im = clean(j)
        if im is None:
            print(j, "없음"); continue
        if j in ("L03_villagers", "L09_slashes"):
            parts = split(im, j)
            made[j] = parts
            print(j, "→", len(parts), "덩어리")
        else:
            print(j, "정리")
    lp = os.path.join(ROOT, "layout.json")
    if len(sys.argv) > 2 and sys.argv[2] == "preview" and os.path.exists(lp):
        layout = json.load(open(lp, encoding="utf-8"))
        states = {
            "s0": {"kills": [], "doho": "L11_doho_pass"},
            "s4": {"kills": ["heukrang", "beom", "bulgasari"], "empty": True, "doho": "L11_doho_pass"},
            "s5": {"kills": ["heukrang", "beom", "bulgasari"], "empty": True, "streams": True, "gold": True, "doho": "L12_doho_cave"},
        }
        for k, s in states.items():
            compose(layout, s).save(os.path.join(ROOT, f"preview_{k}.png"))
            print("미리보기", k)
