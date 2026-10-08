"""review_board.py — #214 공방 6종 검토판 한 장 (joseon-assets/workbench/vfx/_review_214.png).
줄마다 큐 하나: 8프레임 시트는 8칸, 정지 텍스처는 텍스처 + 게임 색. 바닥색 = 어두운 석실. 채택안 ★, 기각 이유는 README 표.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import numpy as np
from vfx_workshop import key_alpha, load_dir, colorize, parse_tint, label, FLOOR, ISO_SQUASH  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELL = 150
ROWS = [
    # (제목, 종류, 경로, 색)
    ("fire_burst ★ v1a — 화염 폭발 8f (색띠)", "frames", "fire_burst/fire_burst_v1a_8f", "fire"),
    ("sal_burst ★ v1a — 살(독) 구름 8f (색띠)", "frames", "sal_burst/sal_burst_v1a_8f", "sal"),
    ("hit_spark ★ v1a — 타격 스파크 8f (강철색)", "frames", "hit_spark/hit_spark_v1a_8f", "0.92,0.9,0.8"),
    ("dust_impact ★ v1b — 먼지 임팩트 8f (흙색)", "frames", "dust_impact/dust_impact_v1b_8f", "0.55,0.5,0.42"),
    ("necro_circle ★ c_s51 / b_s33 — 바닥 진 (아이소로 눌러 봄)", "decal", "necro_circle/necro_circle_c_s51_tex.png|necro_circle/necro_circle_b_s33_tex.png", "necro|0.55,0.72,0.30"),
    ("slash_mask ★ strip s7 / arc s8 — 검광 마스크", "mask", "slash_mask/slash_mask_strip_s7_tex.png|slash_mask/slash_mask_arc_s8_tex.png", "0.95,0.93,0.85"),
]


def fit(im, w, h):
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    return im


def main():
    W = CELL * 8
    H = sum(CELL + 26 for _ in ROWS)
    board = Image.new("RGBA", (W, H), FLOOR + (255,))
    y = 0
    for title, kind, path, tint in ROWS:
        label(board, title, 15, (6, y + 3))
        yy = y + 24
        if kind == "frames":
            frames = [key_alpha(f, "black") for f in load_dir(os.path.join(ROOT, path))]
            # 공통 박스 (vfx_sheet.py 와 같게)
            box = None
            for im in frames:
                ys, xs = np.where(np.asarray(im)[..., 3] > 16)
                if xs.size:
                    b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
                    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
            frames = [im.crop(box) for im in frames]
            for i, fr in enumerate(frames):
                im = fit(colorize(fr, parse_tint(tint)), CELL - 8, CELL - 8)
                board.alpha_composite(im, (i * CELL + (CELL - im.width) // 2, yy + (CELL - im.height) // 2))
        else:
            paths = path.split("|")
            tints = tint.split("|")
            x = 0
            for j, p in enumerate(paths):
                tex = Image.open(os.path.join(ROOT, p)).convert("RGBA")
                t = parse_tint(tints[min(j, len(tints) - 1)])
                if kind == "decal":
                    # 흰 원본 + 게임 색(아이소로 눌림) 두 칸씩
                    raw = fit(tex, CELL * 2 - 8, CELL - 8)
                    board.alpha_composite(raw, (x + (CELL * 2 - raw.width) // 2, yy + (CELL - raw.height) // 2))
                    x += CELL * 2
                    col = colorize(tex, t)
                    col = col.resize((col.width, int(col.height * ISO_SQUASH)), Image.LANCZOS)
                    col = fit(col, CELL * 2 - 8, CELL - 8)
                    board.alpha_composite(col, (x + (CELL * 2 - col.width) // 2, yy + (CELL - col.height) // 2))
                    x += CELL * 2
                else:
                    im = fit(colorize(tex, t), CELL * 4 - 12, CELL - 8)
                    board.alpha_composite(im, (x + (CELL * 4 - im.width) // 2, yy + (CELL - im.height) // 2))
                    x += CELL * 4
        ImageDraw.Draw(board).line([(0, y + CELL + 25), (W, y + CELL + 25)], fill=(60, 56, 52, 255), width=1)
        y += CELL + 26
    out = os.path.join(ROOT, "_review_214.png")
    board.convert("RGB").save(out)
    print("BOARD_OK", out, board.size)


if __name__ == "__main__":
    main()
