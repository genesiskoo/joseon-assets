"""#1109 1막 두루마리판 겹 → joseon-assets 1109_act1_scroll/{layers, clean, pieces, layout.json}.
- layers = Codex 원본 그대로 · clean = 흰 종이에 눌러 편 흑백(L) · pieces = 묶음 겹(사람 여섯 · 연기 모양 셋)을 덩어리로 자른 것
- layout.json = 두루마리 좌표(4608×1024: 판 0 = 0~1536 · 들길 1536~3072 · 먼 고을 3072~4608)의 겹 자리 · 셰이더 칸 · 시간표(_cues)
사용: python -E -P build.py <act1_A 폴더> <joseon-assets 1109 폴더>"""
import glob, json, os, shutil, sys
import numpy as np
from PIL import Image, ImageFilter

SRC, DST = sys.argv[1], sys.argv[2]
for d in ("layers", "clean", "pieces", "prompts"):
    os.makedirs(os.path.join(DST, d), exist_ok=True)


def flat(p):
    im = Image.open(p)
    if im.mode == "RGBA":
        a = np.asarray(im).astype(np.float32) / 255.0
        rgb = a[..., :3] * a[..., 3:4] + (1.0 - a[..., 3:4])
    else:
        rgb = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    g = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    g[g > 0.95] = 1.0
    return Image.fromarray(np.clip(g * 255 + 0.5, 0, 255).astype(np.uint8), "L")


def split(im, job, n_want, min_area=1500):
    g = np.asarray(im).astype(np.float32) / 255.0
    m = np.asarray(Image.fromarray(((g < 0.9) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(25))) > 0
    seen = np.zeros(m.shape, bool)
    comps = []
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys[::97], xs[::97]):
        if seen[y0, x0]:
            continue
        stack = [(y0, x0)]
        seen[y0, x0] = True
        pix = []
        while stack:
            y, x = stack.pop()
            pix.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if len(pix) >= min_area:
            comps.append(pix)
    comps.sort(key=lambda c: -len(c))
    comps = comps[:n_want]
    comps.sort(key=lambda c: min(x for _, x in c))
    src = np.asarray(im)
    out = []
    for i, pix in enumerate(comps):
        keep = np.zeros(m.shape, bool)
        yy, xx = zip(*pix)
        keep[list(yy), list(xx)] = True
        part = src.copy()
        part[~keep] = 255
        b = (min(xx), min(yy), max(xx) + 1, max(yy) + 1)
        name = f"{job}_{i}"
        Image.fromarray(part).crop(b).save(os.path.join(DST, "pieces", name + ".png"), optimize=True)
        out.append((name, b))
    print(job, "→", len(out), "덩어리", [o[1] for o in out])
    return out


for p in sorted(glob.glob(os.path.join(SRC, "out", "A*", "A*.png"))):
    job = os.path.splitext(os.path.basename(p))[0]
    if os.path.basename(os.path.dirname(p)) != job:
        continue  # 버린 판(A1_chain_seal_v1 등)
    shutil.copy(p, os.path.join(DST, "layers", job + ".png"))
    shutil.copy(os.path.join(SRC, job + ".txt"), os.path.join(DST, "prompts", job + ".txt"))
    g = flat(p)
    g.save(os.path.join(DST, "clean", job + ".png"), optimize=True)
    if job == "A5_far_people":
        split(g, job, 6)
    elif job == "A7_smoke_shapes":
        split(g, job, 3)
shutil.copy(os.path.join(SRC, "common.txt"), os.path.join(DST, "prompts", "common.txt"))

# ---------------------------------------------------------------- 배치표
SWEEP_L = [-1, 0]
SWEEP_R = [1, 0]
boxes = {}
cues = []


def lay(key, file, box, **params):
    boxes[key] = {"file": file, "box": box, "params": params}


# 판 0 — 굴 어귀 쇠사슬 · 산마루 산군 범(흐린 먹, 약조)
lay("A1", "A1_chain_seal", [-81, 346, 326], order_mode=1, sweep_dir=SWEEP_R, sweep_mix=0.6, rim_amount=0.6, edge_feather=0.03)
lay("A2", "A2_sansin_tiger", [700, 170, 250], order_mode=1, sweep_dir=[0, 1], sweep_mix=0.6, density=0.75, edge_feather=0.03)
# 실연기 ② — 굴에서 오른쪽 끝까지 높이 흐름(가늘게) · 지나간 뒤 풀림
for i, x in enumerate([60, 1590, 3120]):
    lay(f"T{i}", "A8_smoke_trail", [x, -150, 1536], order_mode=2, sweep_dir=SWEEP_R, density=0.55, bleed=0.2, edge_feather=0.02)
# 들길 · 먼 고을
lay("A3", "A3_road", [1440, 90, 1536], order_mode=2, sweep_dir=SWEEP_L, edge_feather=0.08, bleed=0.35)
lay("A4", "A4_far_village", [3072, 60, 1536], order_mode=0, drop_uv=[0.55, 0.62], edge_feather=0.08, bleed=0.4)
people_x = [3560, 3665, 3755, 3860, 3965, 4070]
for i, x in enumerate(people_x):
    lay(f"P{i}", f"A5_far_people_{i}", [x, 670, 72 if i != 1 else 46], order_mode=1, sweep_dir=[0, 1], sweep_mix=0.7, edge_feather=0.015)
lay("A6", "A6_smoke_fox", [3260, 400, 760], order_mode=1, sweep_dir=SWEEP_L, sweep_mix=0.6, rim_amount=0.5, bleed=0.45)
for i, x in enumerate([3360, 3480, 3620]):
    lay(f"S{i}", f"A7_smoke_shapes_{i}", [x, 500, 120], order_mode=1, sweep_dir=[0, -1], sweep_mix=0.7, edge_feather=0.02, bleed=0.4)
# 연기 자취 ④ — 먼 고을에서 들길을 건너 주막까지(굵게)
for i, (x, w) in enumerate([(3072, 1536), (1536, 1536), (620, 936)]):
    lay(f"TR{i}", "A8_smoke_trail", [x, 700 - int(412 * w / 1536), w], order_mode=2, sweep_dir=SWEEP_L, density=0.85, bleed=0.4, edge_feather=0.02)
# 마른 발자국 — 340 폭 열 장을 오른쪽부터(원화 발자국이 커서 줄여 잇는다) · 마지막은 고개 마루로 오르는 돌린 두 장
FW = 340
for k in range(10):
    x = 1536 + k * FW
    lay(f"F{k}", "A9_footprints", [x, 760 - int(760 * FW / 1536), FW], order_mode=2, sweep_dir=SWEEP_L, soft=0.03, bleed=0.05, rim_amount=0.0, edge_feather=0.01)
lay("FC", "A9_footprints", [1356, 520, FW, 62.5], order_mode=2, sweep_dir=SWEEP_L, soft=0.03, bleed=0.05, rim_amount=0.0, edge_feather=0.01)
lay("FD", "A9_footprints", [1352, 434, 176, 65.2], order_mode=2, sweep_dir=SWEEP_L, soft=0.03, bleed=0.05, rim_amount=0.0, edge_feather=0.01)


def q(k, ch, t0, dur, to):
    cues.append([k, ch, t0, dur, to])


q("A1", "progress", 11.0, 3.6, 1.0)
q("A2", "progress", 15.0, 4.0, 1.0)
for i, t in enumerate([23.0, 29.5, 34.5]):
    q(f"T{i}", "progress", t, 5.5, 1.0)
    q(f"T{i}", "wash", 50.0 + i * 0.6, 5.0, 0.85)
q("A4", "progress", 40.0, 4.5, 1.0)
for i in range(6):
    q(f"P{i}", "progress", 43.0 + i * 0.4, 2.4, 1.0)
    q(f"P{i}", "dilute", 54.0 + i * 0.7, 2.0, 0.72)
q("A6", "progress", 44.0, 3.0, 1.0)
q("A6", "wash", 49.0, 3.0, 1.0)
for i in range(3):
    q(f"S{i}", "progress", 48.5 + i * 1.6, 2.6, 1.0)
    q(f"S{i}", "dilute", 58.5, 3.0, 0.5)
q("F9", "progress", 60.0, 3.0, 1.0)
q("A3", "progress", 64.0, 4.0, 1.0)
for i, t in enumerate([64.5, 68.0, 76.0]):
    q(f"TR{i}", "progress", t, 4.0, 1.0)
for j, k in enumerate(range(8, -1, -1)):
    q(f"F{k}", "progress", 65.5 + j * 0.95, 1.6, 1.0)
q("FC", "progress", 114.0, 2.4, 1.0)
q("FD", "progress", 116.2, 2.0, 1.0)

layout = {
    "_doc": "#1109 1막 두루마리판 배치표 — 두루마리 좌표 4608×1024 · box = [x, y, w(, 돌림 도)] · _cues = [겹, 채널, 시작 초, 길이, 끝 값] · 판 0 겹은 1099_story_scroll/layout.json",
    "cave": [85, 445],
    "gold": [3420, 470],
    "pieces": ["A5_far_people_", "A7_smoke_shapes_"],
    "boxes": boxes,
    "_cues": cues,
}
json.dump(layout, open(os.path.join(DST, "layout.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("layout", len(boxes), "겹", len(cues), "큐")
