"""Tripo 여러 방향 입력 — 네 장을 같은 틀로 (#1138).

같은 정사각 캔버스 · 같은 몸 키(px) · 발끝 = 같은 바닥 줄 · 가로 가운데.
옆(왼쪽) 한 장의 길이가 캔버스 폭을 정하고, 그 배율의 「몸 키」를 정면·뒤에도 쓴다.
오른쪽 = 왼쪽 옆을 좌우 뒤집은 것(서 있는 대칭 자세).

    python frame_views.py <side_left.png> <front.png> <back.png> <out_dir> [--size 1536] [--margin 0.07]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


def bbox(img: Image.Image, thr: int = 236) -> tuple[int, int, int, int]:
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    m = (a < thr).any(axis=2)  # 흰 바탕이 아닌 칸
    # 외톨이 점(바탕 얼룩) 무시 — 줄·칸마다 3px 넘게 있어야 몸
    rows = np.where(m.sum(axis=1) > 3)[0]
    cols = np.where(m.sum(axis=0) > 3)[0]
    return int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1


def whiten(img: Image.Image, thr: int = 238) -> Image.Image:
    """바탕 = 순백. 생성 그림의 바탕은 250~254라 순백 캔버스에 붙이면 옅은 사각 경계가 남는다(2차 판독 ⑦).
    가장자리에서 이어진 밝은 칸만 255로 — 몸 안의 밝은 점(송곳니·눈빛)은 그대로."""
    a = np.asarray(img.convert("RGB")).copy()
    light = (a >= thr).all(axis=2)
    h, w = light.shape
    seen = np.zeros_like(light)
    stack = [(y, x) for y in (0, h - 1) for x in range(w) if light[y, x]] + [(y, x) for x in (0, w - 1) for y in range(h) if light[y, x]]
    for y, x in stack:
        seen[y, x] = True
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    a[seen] = 255
    return Image.fromarray(a)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    size = int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 1536
    margin = float(sys.argv[sys.argv.index("--margin") + 1]) if "--margin" in sys.argv else 0.07
    side_p, front_p, back_p, out_dir = args[:4]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    side = whiten(Image.open(side_p))
    front = whiten(Image.open(front_p))
    back = whiten(Image.open(back_p))
    boxes = {k: bbox(v) for k, v in (("side", side), ("front", front), ("back", back))}
    sx0, sy0, sx1, sy1 = boxes["side"]
    usable = size * (1 - 2 * margin)
    k_side = usable / max(sx1 - sx0, sy1 - sy0)
    body_h = (sy1 - sy0) * k_side  # 이 틀의 몸 키(px)
    ground = int(round(size * (1 - margin)))  # 발끝 줄
    report = {"size": size, "body_h_px": round(body_h, 1), "ground_y": ground}
    views = {}
    for key, img in (("side", side), ("front", front), ("back", back)):
        x0, y0, x1, y1 = boxes[key]
        crop = img.crop((x0, y0, x1, y1))
        k = body_h / (y1 - y0)
        w, h = max(1, round(crop.width * k)), max(1, round(crop.height * k))
        crop = crop.resize((w, h), Image.LANCZOS)
        canvas = Image.new("RGB", (size, size), (255, 255, 255))
        canvas.paste(crop, ((size - w) // 2, ground - h))
        views[key] = canvas
        report[key] = {"src_bbox": [x0, y0, x1, y1], "scale": round(k, 4), "w": w, "h": h}
    views["right"] = ImageOps.mirror(views["side"])
    names = {"front": "1_front.png", "side": "2_left.png", "back": "3_back.png", "right": "4_right.png"}
    for key, name in names.items():
        views[key].save(out / name)
    sheet = Image.new("RGB", (size * 2, size * 2), (255, 255, 255))
    for i, key in enumerate(("front", "side", "back", "right")):
        sheet.paste(views[key], ((i % 2) * size, (i // 2) * size))
    sheet.resize((1280, 1280), Image.LANCZOS).save(out / "sheet.jpg", quality=86)
    print(report)


if __name__ == "__main__":
    main()
