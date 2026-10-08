"""vfx_workshop.py — VFX 공방 도우미 (보드 #214). 원본 영상·이미지 → 고르기용 대조표 · N프레임 추출 · 게임 바닥색 미리보기.

게임 반입(시트·메타·.import)은 joseon/tools/vfx_sheet.py 가 맡는다 — 여기는 "고르고 보여 주기" 전용이다.
키잉은 vfx_sheet.key_alpha 를 그대로 불러 쓴다(미리보기 = 게임에 들어갈 알파와 같은 값).

  python vfx_workshop.py contact --src clip.mp4 --out contact.png            # 원본 전 프레임 + 먹 양 곡선
  python vfx_workshop.py pick    --src clip.mp4 --n 8 --out dir [--start i --end j] [--ease 1.0]
  python vfx_workshop.py preview --frames dir1,dir2 --labels a,b --tint r,g,b --units 1.2 --fps 16 --out x.gif [--ground]
  python vfx_workshop.py strip   --frames dir --tint r,g,b --out strip.png     # 고른 N장을 바닥색 위에 한 줄로
  python vfx_workshop.py still   --src img.png --out tex.png [--max 512] [--circle]   # 정지 텍스처: 키잉·트림·축소

게임 척도: 아이소 65px/유닛(vfx.md §2). 미리보기는 2배(130px/유닛)로 그리고, 옆에 도호 키(1.7유닛) 막대를 세운다.
바닥 데칼(--ground)은 카메라 피치 35.264° 만큼 세로를 눌러(×0.577) 게임에서 보이는 모양으로 그린다.
"""
import argparse, math, os, subprocess, sys, tempfile
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont
import numpy as np

sys.path.insert(0, r"C:\workspace\joseon\tools")
from vfx_sheet import key_alpha  # noqa: E402  (게임 반입과 같은 키잉)

PPU = 130                      # 미리보기 px/유닛 (게임 65의 2배)
FLOOR = (34, 31, 29)           # 어두운 석실 바닥 (던전 앰비언트 0.16 근처)
ISO_SQUASH = math.sin(math.radians(35.264))   # 바닥 데칼이 아이소 카메라에서 눌리는 비율
FONT = r"C:\Windows\Fonts\malgun.ttf"


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def prep(img, crop=None, black=0):
    """키잉 전 손질: crop = (L,T,R,B) 픽셀 잘라내기(바닥 반사·심지 등), black = 검정점(그 아래 밝기는 0 — 회색 바닥·안개 바탕 제거)."""
    if crop:
        l, t, r, b = crop
        img = img.crop((l, t, img.width - r, img.height - b))
    if black > 0:
        a = np.asarray(img.convert("RGB")).astype(np.float32)
        a = np.clip((a - black) * 255.0 / (255.0 - black), 0, 255)
        img = Image.fromarray(a.astype(np.uint8), "RGB")
    return img.convert("RGBA")


def all_frames(src, crop=None, black=0):
    """영상 원본 프레임 전부(원래 fps) → 손질 → 키잉된 RGBA 목록."""
    tmp = tempfile.mkdtemp(prefix="vfxws_")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, os.path.join(tmp, "f_%04d.png")], check=True)
    files = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
    return [key_alpha(prep(Image.open(os.path.join(tmp, f)), crop, black), "black") for f in files]


def parse_crop(s):
    return tuple(int(x) for x in s.split(",")) if s else None


def ink(frames):
    """프레임별 먹 양 = 알파 합 / (넓이 × 255)."""
    return [float(np.asarray(im)[..., 3].astype(np.float32).sum()) / (im.width * im.height * 255.0) for im in frames]


def auto_window(curve, lo=0.06, tail=0.12):
    peak = int(np.argmax(curve))
    mx = max(curve) or 1.0
    start = next((i for i, v in enumerate(curve) if v >= lo * mx), 0)
    end = peak
    for i in range(peak, len(curve)):
        if curve[i] >= tail * mx:
            end = i
    return start, end


def pick_indices(start, end, n, ease=1.0):
    t = np.linspace(0.0, 1.0, n) ** ease   # ease > 1 = 앞(터지는 순간)을 촘촘히
    return [int(round(start + (end - start) * x)) for x in t]


def tinted(im, tint, alpha_mul=1.0):
    a = np.asarray(im).astype(np.float32)
    rgb = a[..., :3] * np.array(tint, np.float32)[None, None, :]
    alpha = a[..., 3] * alpha_mul
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 255)]).astype(np.uint8), "RGBA")


RAMPS = {   # 색띠 (#198 제안 = D2R 그라데이션 맵): 먹 농도(알파) → 색. 옅은 가장자리 = 어두운 색, 짙은 속 = 밝은 색
    "fire": [(0.0, (70, 10, 4)), (0.35, (175, 42, 10)), (0.6, (240, 120, 30)), (0.85, (255, 200, 95)), (1.0, (255, 245, 215))],
    "sal": [(0.0, (18, 24, 12)), (0.4, (66, 92, 34)), (0.75, (132, 165, 70)), (1.0, (210, 232, 160))],
    "necro": [(0.0, (26, 0, 6)), (0.55, (105, 10, 18)), (0.9, (165, 24, 28)), (1.0, (200, 45, 40))],   # 검붉은 음기 — 연분홍으로 뜨지 않게 꼭대기를 낮춤
}


def ramped(im, stops, alpha_mul=1.0):
    a = np.asarray(im).astype(np.float32)
    t = a[..., 3] / 255.0
    xs = [s[0] for s in stops]
    rgb = np.stack([np.interp(t, xs, [s[1][c] for s in stops]) for c in range(3)], axis=-1)
    return Image.fromarray(np.dstack([rgb, np.clip(a[..., 3] * alpha_mul, 0, 255)]).astype(np.uint8), "RGBA")


def colorize(im, tint):
    """tint = (r,g,b) 곱(지금 게임 방식: AnimatedSprite3D.modulate) 또는 RAMPS 이름(색띠)."""
    return ramped(im, RAMPS[tint]) if isinstance(tint, str) else tinted(im, tint)


def parse_tint(s):
    return s if s in RAMPS else tuple(float(x) for x in s.split(","))


def compose(fr, tint, units, ground, canvas=(360, 300), anchor_y=0.55, show_ref=True):
    """틴트한 프레임을 바닥색 캔버스에 게임 척도로 얹는다. 폭 = units 유닛 (Vfx._make_sheet_node: pixel_size = units / fw)."""
    W, H = canvas
    bg = Image.new("RGBA", (W, H), FLOOR + (255,))
    if show_ref:   # 도호 키 1.7유닛 막대 (왼쪽 가장자리)
        d = ImageDraw.Draw(bg)
        h = int(1.7 * PPU * (1.0 if not ground else 1.0))
        x0, y1 = 14, int(H * 0.92)
        d.rounded_rectangle([x0, y1 - h, x0 + 16, y1], radius=8, fill=(70, 66, 62, 255))
    if fr is None:
        return bg
    w = max(1, int(units * PPU))
    h = max(1, int(fr.height * w / fr.width))
    if ground:
        h = max(1, int(h * ISO_SQUASH))
    im = colorize(fr, tint).resize((w, h), Image.LANCZOS)
    cx, cy = W // 2 + 12, int(H * anchor_y)
    bg.alpha_composite(im, (cx - w // 2, cy - h // 2))
    return bg


def label(img, text, size=18, pos=(8, 4), fill=(235, 228, 210, 255)):
    d = ImageDraw.Draw(img)
    d.text(pos, text, font=font(size), fill=fill)
    return img


def load_dir(folder):
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    return [Image.open(os.path.join(folder, f)).convert("RGBA") for f in files]


# ---------- 명령 ----------

def cmd_contact(a):
    frames = all_frames(a.src, parse_crop(a.crop), a.black)
    curve = ink(frames)
    s, e = auto_window(curve)
    cols = a.cols
    cell = 120
    rows = math.ceil(len(frames) / cols)
    chart_h = 90
    sheet = Image.new("RGBA", (cols * cell, rows * cell + chart_h + 28), (10, 10, 12, 255))
    for i, fr in enumerate(frames):
        im = fr.copy()
        im.thumbnail((cell - 4, cell - 4))
        x, y = (i % cols) * cell, (i // cols) * cell
        tile = Image.new("RGBA", (cell, cell), (22, 20, 20, 255) if s <= i <= e else (8, 8, 10, 255))
        tile.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
        sheet.alpha_composite(tile, (x, y))
        label(sheet, str(i), 13, (x + 3, y + 1), (200, 190, 160, 255))
    # 먹 양 곡선
    d = ImageDraw.Draw(sheet)
    y0 = rows * cell + 20
    mx = max(curve) or 1.0
    pts = [(int((i + 0.5) * sheet.width / len(curve)), int(y0 + chart_h - 8 - (v / mx) * (chart_h - 16))) for i, v in enumerate(curve)]
    d.line(pts, fill=(230, 180, 90, 255), width=2)
    label(sheet, "%s  frames=%d  auto window %d..%d (밝은 칸)" % (os.path.basename(a.src), len(frames), s, e), 14, (6, rows * cell + 2))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    sheet.convert("RGB").save(a.out)
    print("CONTACT_OK %s frames=%d window=%d..%d peak=%d" % (a.out, len(frames), s, e, int(np.argmax(curve))))


def cmd_pick(a):
    frames = all_frames(a.src, parse_crop(a.crop), a.black)
    curve = ink(frames)
    s, e = auto_window(curve)
    if a.start >= 0:
        s = a.start
    if a.end >= 0:
        e = a.end
    idx = pick_indices(s, e, a.n, a.ease)
    os.makedirs(a.out, exist_ok=True)
    for f in os.listdir(a.out):
        if f.endswith(".png"):
            os.remove(os.path.join(a.out, f))
    for k, i in enumerate(idx):
        # 저장은 원본 그대로(검은 배경 RGB) — vfx_sheet.py 가 --key black 으로 다시 키잉한다(반입 경로와 같게)
        fr = frames[i]
        a_ = np.asarray(fr).astype(np.float32)
        rgb = a_[..., :3] * (a_[..., 3:4] / 255.0)   # 키잉 전 모습으로 되돌림(검은 배경 합성)
        Image.fromarray(rgb.astype(np.uint8), "RGB").save(os.path.join(a.out, "f_%02d.png" % k))
    print("PICK_OK %s n=%d idx=%s window=%d..%d" % (a.out, a.n, idx, s, e))


def cmd_preview(a):
    dirs = a.frames.split(",")
    labels = a.labels.split(",") if a.labels else [os.path.basename(d.rstrip("/\\")) for d in dirs]
    tints = [parse_tint(t) for t in a.tint.split("|")]   # 칸마다 색: "fire|1,0.82,0.58|fire"
    tints += [tints[-1]] * (len(dirs) - len(tints))
    sets = []
    for d in dirs:   # 키잉 → 전 프레임 공통 박스로 크롭 (vfx_sheet.py 와 같게 — 게임에서 units = 이 박스의 폭)
        ks = [key_alpha(f, "black") for f in load_dir(d)]
        box = None
        for im in ks:
            ys, xs = np.where(np.asarray(im)[..., 3] > 16)
            if xs.size:
                b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
                box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
        if box:
            box = (max(0, box[0] - 4), max(0, box[1] - 4), box[2] + 4, box[3] + 4)
            ks = [im.crop(box) for im in ks]
        sets.append(ks)
    n = max(len(s) for s in sets)
    W, H = a.w, a.h
    panels = []
    for k in range(n + a.pause):
        row = Image.new("RGBA", (W * len(sets), H), FLOOR + (255,))
        for j, frames in enumerate(sets):
            keyed = frames[k] if k < len(frames) else None
            p = compose(keyed, tints[j], a.units, a.ground, (W, H), a.anchor)
            label(p, labels[j], 18)
            row.alpha_composite(p, (j * W, 0))
            ImageDraw.Draw(row).line([(j * W, 0), (j * W, H)], fill=(60, 56, 52, 255), width=2)
        panels.append(row.convert("RGB"))
    dur = int(round(1000.0 / a.fps))
    panels[0].save(a.out, save_all=True, append_images=panels[1:], duration=dur, loop=0, disposal=2)
    print("PREVIEW_OK %s frames=%d fps=%g" % (a.out, len(panels), a.fps))


def cmd_strip(a):
    frames = [key_alpha(f, "black") for f in load_dir(a.frames)]
    tint = parse_tint(a.tint)
    cell = a.cell
    out = Image.new("RGBA", (cell * len(frames), cell + 24), FLOOR + (255,))
    for i, fr in enumerate(frames):
        im = colorize(fr, tint)
        im.thumbnail((cell - 6, cell - 6))
        out.alpha_composite(im, (i * cell + (cell - im.width) // 2, 24 + (cell - im.height) // 2))
        label(out, str(i + 1), 13, (i * cell + 4, 2), (190, 180, 150, 255))
    if a.title:
        label(out, a.title, 13, (cell * len(frames) - 8 - 7 * len(a.title), 2))
    out.convert("RGB").save(a.out)
    print("STRIP_OK %s" % a.out)


def cmd_still(a):
    im = key_alpha(Image.open(a.src).convert("RGBA"), "black")
    arr = np.asarray(im)
    ys, xs = np.where(arr[..., 3] > 16)
    if xs.size == 0:
        raise SystemExit("빈 이미지")
    if a.circle:   # 원형 진: 중심 기준 정사각 트림(한쪽으로 쏠린 잉크 튐 때문에 중심이 흔들리지 않게 캔버스 중심 고정)
        cx, cy = im.width / 2, im.height / 2
        r = max(abs(xs - cx).max(), abs(ys - cy).max()) + 4
        box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    else:
        box = (max(0, xs.min() - 4), max(0, ys.min() - 4), min(im.width, xs.max() + 5), min(im.height, ys.max() + 5))
    im = im.crop(box)
    im.thumbnail((a.max, a.max), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    im.save(a.out)
    cov = float(np.asarray(im)[..., 3].mean()) / 255.0
    print("STILL_OK %s %dx%d coverage=%.3f" % (a.out, im.width, im.height, cov))


def cmd_decal(a):
    """바닥 진 시연: 각도로 그려짐(0.3초) → 천천히 돌며 맥동 → 커지며 사라짐. 아이소로 눌러 그린다 (적용 카드의 decal 종류 모양)."""
    srcs = a.src.split(",")
    labels = a.labels.split(",") if a.labels else [os.path.splitext(os.path.basename(s))[0] for s in srcs]
    tints = [parse_tint(t) for t in a.tint.split("|")]
    tints += [tints[-1]] * (len(srcs) - len(tints))
    texs = [Image.open(s).convert("RGBA") for s in srcs]
    W, H = a.w, a.h
    n = int(a.sec * a.fps)
    out = []
    for k in range(n + 6):
        t = k / max(n - 1, 1)
        row = Image.new("RGBA", (W * len(texs), H), FLOOR + (255,))
        for j, tex in enumerate(texs):
            p = compose(None, tints[j], a.units, True, (W, H))
            if k < n:
                reveal = min(1.0, t / 0.2)                  # 0~20%: 시계 방향으로 그려짐
                rot = -a.spin * t * a.sec                   # 도/초
                pulse = 0.82 + 0.18 * math.sin(t * a.sec * math.tau * 1.5)
                fade = 1.0 if t < 0.8 else max(0.0, 1.0 - (t - 0.8) / 0.2)
                grow = 1.0 + (0.12 * (t - 0.8) / 0.2 if t > 0.8 else 0.0)
                im = tex.rotate(rot, resample=Image.BICUBIC)
                arr = np.asarray(im).astype(np.float32)
                hh, ww = arr.shape[:2]
                yy, xx = np.mgrid[0:hh, 0:ww]
                ang = (np.degrees(np.arctan2(xx - ww / 2, -(yy - hh / 2))) + 360.0) % 360.0   # 12시 = 0, 시계 방향
                mask = (ang <= reveal * 360.0).astype(np.float32)
                arr[..., 3] *= mask * (pulse if reveal >= 1.0 else 1.0) * fade
                im = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
                w = int(a.units * PPU * grow)
                h = int(w * ISO_SQUASH)
                im = colorize(im, tints[j]).resize((w, h), Image.LANCZOS)
                p.alpha_composite(im, (W // 2 + 12 - w // 2, int(H * 0.62) - h // 2))
            label(p, labels[j], 18)
            row.alpha_composite(p, (j * W, 0))
            ImageDraw.Draw(row).line([(j * W, 0), (j * W, H)], fill=(60, 56, 52, 255), width=2)
        out.append(row.convert("RGB"))
    out[0].save(a.out, save_all=True, append_images=out[1:], duration=int(1000 / a.fps), loop=0, disposal=2)
    print("DECAL_OK %s frames=%d" % (a.out, len(out)))


def warp_strip(strip, head_deg, tail_deg, r0, r1, size):
    """띠 마스크(가로 = 꼬리→머리)를 호에 감는다. 각도 0 = 12시, 시계 방향. u = 꼬리(0)→머리(1), v = 안(0)→바깥(1)."""
    s = np.asarray(strip).astype(np.float32)
    sh, sw = s.shape[:2]
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    cx, cy = size / 2.0, size * 0.62
    ang = np.degrees(np.arctan2(xx - cx, -(yy - cy)))
    rad = np.hypot(xx - cx, yy - cy)
    span = head_deg - tail_deg
    u = (ang - tail_deg) / span if span > 1e-3 else np.zeros_like(ang)
    v = (rad - r0) / (r1 - r0)
    ok = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
    ui = np.clip((u * (sw - 1)).astype(int), 0, sw - 1)
    vi = np.clip(((1.0 - v) * (sh - 1)).astype(int), 0, sh - 1)   # 띠 위쪽 = 칼끝(바깥)
    out = np.zeros((size, size, 4), np.float32)
    out[ok] = s[vi[ok], ui[ok]]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA")


def cmd_trail(a):
    """검광 띠 시연: 칼끝이 호를 따라 돌고, 꼬리가 0.18초 뒤를 따라가며 옅어진다 (SwordTrail 리본에 마스크를 얹은 모양)."""
    srcs = a.src.split(",")
    labels = a.labels.split(",") if a.labels else [os.path.splitext(os.path.basename(s))[0] for s in srcs]
    tint = parse_tint(a.tint)
    strips = [Image.open(s).convert("RGBA") for s in srcs]
    W = H = a.size
    n = a.frames
    out = []
    for k in range(n + 5):
        row = Image.new("RGBA", (W * len(strips), H), FLOOR + (255,))
        for j, strip in enumerate(strips):
            p = Image.new("RGBA", (W, H), FLOOR + (255,))
            if k < n:
                t = k / max(n - 1, 1)
                head = -80.0 + 170.0 * min(1.0, t / 0.7)
                tail = max(-80.0, head - 110.0 * min(1.0, t / 0.35) - (110.0 * (t - 0.7) / 0.3 if t > 0.7 else 0.0))
                if head - tail > 2.0:
                    im = warp_strip(strip, head, tail, W * 0.22, W * 0.44, W)
                    p.alpha_composite(colorize(im, tint))
            label(p, labels[j], 18)
            row.alpha_composite(p, (j * W, 0))
            ImageDraw.Draw(row).line([(j * W, 0), (j * W, H)], fill=(60, 56, 52, 255), width=2)
        out.append(row.convert("RGB"))
    out[0].save(a.out, save_all=True, append_images=out[1:], duration=int(1000 / a.fps), loop=0, disposal=2)
    print("TRAIL_OK %s frames=%d" % (a.out, len(out)))


def _polar(size, cx=None, cy=None):
    cx = size[0] / 2.0 if cx is None else cx
    cy = size[1] / 2.0 if cy is None else cy
    yy, xx = np.mgrid[0:size[1], 0:size[0]].astype(np.float32)
    ang = (np.degrees(np.arctan2(xx - cx, -(yy - cy))) + 360.0) % 360.0   # 12시 = 0, 시계 방향
    rad = np.hypot(xx - cx, yy - cy)
    return ang, rad


def cmd_spark8(a):
    """정지 섬광 한 장 → N프레임 터짐: 가운데 섬광은 줄며 먼저 꺼지고, 빛살은 바깥으로 자라며 늦게 꺼진다 (결정적, 크레딧 0).
    저장은 검은 바탕 RGB — vfx_sheet.py 가 --key black 으로 다시 키잉한다(반입 경로와 같게)."""
    src = key_alpha(prep(Image.open(a.src)), "black")
    S = src.width
    ang, rad = _polar((S, S))
    rn = rad / (S / 2.0)
    core_m = np.clip(1.0 - (rn - a.core) / 0.08, 0.0, 1.0)          # 가운데 원(부드러운 가장자리)
    arr = np.asarray(src).astype(np.float32)
    core = arr.copy(); core[..., 3] *= core_m
    rays = arr.copy(); rays[..., 3] *= (1.0 - core_m)
    core_im = Image.fromarray(core.clip(0, 255).astype(np.uint8), "RGBA")
    rays_im = Image.fromarray(rays.clip(0, 255).astype(np.uint8), "RGBA")
    os.makedirs(a.out, exist_ok=True)
    for f in os.listdir(a.out):
        if f.endswith(".png"):
            os.remove(os.path.join(a.out, f))
    for i in range(a.n):
        t = i / max(a.n - 1, 1)
        canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        for layer, sc, al in (
            (rays_im, 0.55 + 0.8 * (1.0 - (1.0 - t) ** 2), 1.0 if t < 0.35 else max(0.0, 1.0 - ((t - 0.35) / 0.65) ** 1.1)),
            (core_im, 1.15 - 0.8 * t, max(0.0, 1.0 - t / 0.55)),
        ):
            if al <= 0.0:
                continue
            w = max(1, int(S * sc))
            im = layer.rotate(a.spin * t, resample=Image.BICUBIC).resize((w, w), Image.LANCZOS)
            px = np.asarray(im).astype(np.float32)
            px[..., 3] *= al
            im = Image.fromarray(px.clip(0, 255).astype(np.uint8), "RGBA")
            if w > S:
                o = (w - S) // 2
                im = im.crop((o, o, o + S, o + S))
                canvas.alpha_composite(im)
            else:
                canvas.alpha_composite(im, ((S - w) // 2, (S - w) // 2))
        c = np.asarray(canvas).astype(np.float32)
        rgb = c[..., :3] * (c[..., 3:4] / 255.0)
        Image.fromarray(rgb.clip(0, 255).astype(np.uint8), "RGB").save(os.path.join(a.out, "f_%02d.png" % i))
    print("SPARK8_OK %s n=%d" % (a.out, a.n))


def cmd_arc(a):
    """붓결 고리 → 반달 슬래시 마스크: a0~a1 도 구간만 남기고 양 끝을 taper 도에 걸쳐 가늘게, 머리(a1) 쪽을 밝게."""
    ring = key_alpha(prep(Image.open(a.src)), "black")
    arr = np.asarray(ring).astype(np.float32)
    ang, rad = _polar(ring.size)
    rel = ((ang - a.a0 + 360.0) % 360.0)
    span = (a.a1 - a.a0) % 360.0
    u = rel / span                                            # 0 = 꼬리, 1 = 머리
    inside = rel <= span
    tail = np.clip(rel / a.taper, 0.0, 1.0)
    head = np.clip((span - rel) / (a.taper * 0.5), 0.0, 1.0)
    w = np.where(inside, tail * head * (0.45 + 0.55 * np.clip(u, 0, 1)), 0.0)
    arr[..., 3] *= w
    im = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    ys, xs = np.where(np.asarray(im)[..., 3] > 12)
    im = im.crop((max(0, xs.min() - 4), max(0, ys.min() - 4), xs.max() + 5, ys.max() + 5))
    im.thumbnail((a.max, a.max), Image.LANCZOS)
    im.save(a.out)
    print("ARC_OK %s %dx%d" % (a.out, im.width, im.height))


def cmd_bend(a):
    """가로 붓 띠(꼬리 = 왼쪽, 머리 = 오른쪽) → 반달 슬래시 마스크(정지): tail~head 도 구간의 호에 감는다. 위쪽 = 칼끝(바깥)."""
    strip = key_alpha(prep(Image.open(a.src)), "black")
    ys, xs = np.where(np.asarray(strip)[..., 3] > 16)
    strip = strip.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    im = warp_strip(strip, a.head, a.tail, a.size * a.r0, a.size * a.r1, a.size)
    ys, xs = np.where(np.asarray(im)[..., 3] > 12)
    im = im.crop((max(0, xs.min() - 4), max(0, ys.min() - 4), xs.max() + 5, ys.max() + 5))
    im.save(a.out)
    print("BEND_OK %s %dx%d" % (a.out, im.width, im.height))


def cmd_unwrap(a):
    """붓결 고리 → 가로 띠(극좌표 펴기): x = 각도(꼬리→머리), y = 반지름(바깥 = 위 = 칼끝). SwordTrail 리본 UV용."""
    ring = key_alpha(prep(Image.open(a.src)), "black")
    arr = np.asarray(ring).astype(np.float32)
    S = ring.width
    ys, xs = np.where(arr[..., 3] > 24)
    cx, cy = S / 2.0, S / 2.0
    r = np.hypot(xs - cx, ys - cy)
    r0, r1 = np.percentile(r, 1), np.percentile(r, 99.5)
    W, H = a.w, a.h
    uu, vv = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
    th = np.radians(a.a0 + (a.a1 - a.a0) * uu)
    rr = r1 - (r1 - r0) * vv                                  # 위 = 바깥
    sx = np.clip((cx + rr * np.sin(th)).astype(int), 0, S - 1)
    sy = np.clip((cy - rr * np.cos(th)).astype(int), 0, S - 1)
    out = arr[sy, sx]
    fade = np.clip(uu / 0.35, 0, 1) ** 1.4 * np.clip((1 - uu) / 0.04, 0, 1)   # 꼬리(왼쪽) 옅게, 머리(오른쪽) 또렷이
    out[..., 3] *= fade
    Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA").save(a.out)
    print("UNWRAP_OK %s %dx%d r=%.0f..%.0f" % (a.out, W, H, r0, r1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("contact"); c.add_argument("--src", required=True); c.add_argument("--out", required=True); c.add_argument("--cols", type=int, default=11)
    c.add_argument("--crop", default=""); c.add_argument("--black", type=int, default=0)
    p = sub.add_parser("pick"); p.add_argument("--src", required=True); p.add_argument("--out", required=True)
    p.add_argument("--crop", default="", help="키잉 전 잘라내기 L,T,R,B 픽셀"); p.add_argument("--black", type=int, default=0, help="검정점 0~255")
    p.add_argument("--n", type=int, default=8); p.add_argument("--start", type=int, default=-1); p.add_argument("--end", type=int, default=-1)
    p.add_argument("--ease", type=float, default=1.0)
    v = sub.add_parser("preview"); v.add_argument("--frames", required=True); v.add_argument("--labels", default="")
    v.add_argument("--tint", default="1,1,1"); v.add_argument("--units", type=float, default=1.0); v.add_argument("--fps", type=float, default=16)
    v.add_argument("--out", required=True); v.add_argument("--ground", action="store_true"); v.add_argument("--pause", type=int, default=6)
    v.add_argument("--w", type=int, default=360); v.add_argument("--h", type=int, default=300); v.add_argument("--anchor", type=float, default=0.55)
    s = sub.add_parser("strip"); s.add_argument("--frames", required=True); s.add_argument("--tint", default="1,1,1"); s.add_argument("--out", required=True)
    s.add_argument("--cell", type=int, default=150); s.add_argument("--title", default="")
    t = sub.add_parser("still"); t.add_argument("--src", required=True); t.add_argument("--out", required=True)
    t.add_argument("--max", type=int, default=512); t.add_argument("--circle", action="store_true")
    d = sub.add_parser("decal"); d.add_argument("--src", required=True); d.add_argument("--labels", default="")
    d.add_argument("--tint", default="1,1,1"); d.add_argument("--units", type=float, default=2.0); d.add_argument("--sec", type=float, default=1.6)
    d.add_argument("--fps", type=float, default=20); d.add_argument("--spin", type=float, default=40.0); d.add_argument("--out", required=True)
    d.add_argument("--w", type=int, default=360); d.add_argument("--h", type=int, default=300)
    r = sub.add_parser("trail"); r.add_argument("--src", required=True); r.add_argument("--labels", default="")
    r.add_argument("--tint", default="1,1,1"); r.add_argument("--frames", type=int, default=14); r.add_argument("--fps", type=float, default=30)
    r.add_argument("--size", type=int, default=320); r.add_argument("--out", required=True)
    k = sub.add_parser("spark8"); k.add_argument("--src", required=True); k.add_argument("--out", required=True)
    k.add_argument("--n", type=int, default=8); k.add_argument("--core", type=float, default=0.22); k.add_argument("--spin", type=float, default=10.0)
    q = sub.add_parser("arc"); q.add_argument("--src", required=True); q.add_argument("--out", required=True)
    q.add_argument("--a0", type=float, default=-80.0); q.add_argument("--a1", type=float, default=80.0); q.add_argument("--taper", type=float, default=40.0)
    q.add_argument("--max", type=int, default=512)
    u = sub.add_parser("unwrap"); u.add_argument("--src", required=True); u.add_argument("--out", required=True)
    u.add_argument("--a0", type=float, default=0.0); u.add_argument("--a1", type=float, default=200.0)
    u.add_argument("--w", type=int, default=1024); u.add_argument("--h", type=int, default=128)
    b = sub.add_parser("bend"); b.add_argument("--src", required=True); b.add_argument("--out", required=True)
    b.add_argument("--tail", type=float, default=-75.0); b.add_argument("--head", type=float, default=75.0)
    b.add_argument("--r0", type=float, default=0.26); b.add_argument("--r1", type=float, default=0.46); b.add_argument("--size", type=int, default=768)
    a = ap.parse_args()
    {"contact": cmd_contact, "pick": cmd_pick, "preview": cmd_preview, "strip": cmd_strip, "still": cmd_still,
     "decal": cmd_decal, "trail": cmd_trail, "spark8": cmd_spark8, "arc": cmd_arc, "unwrap": cmd_unwrap, "bend": cmd_bend}[a.cmd](a)


if __name__ == "__main__":
    main()
