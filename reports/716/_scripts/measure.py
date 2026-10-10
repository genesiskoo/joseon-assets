"""#716 캡처 픽셀 판정 (damage_numbers_v2 §7 — 채움 중앙 대비 ≥ 4.5:1 · 불↔금니 deut ΔE ≥ 12).
python measure.py   — 판 N716(와 같은 자리면 판 A) 클립 프레임에서 숫자 하나씩: 상자 안 채움 마스크 → 채움 중앙(침식 1) · 테(채움 바깥 1~2px 중 어두운 절반) · 바탕(상자 가장자리, 채움 4px 밖) 중앙값.
채움 마스크: mode lum = 밝기 > (최소+최대)/2 · mode sat = 채도 > 0.42 이고 밝기 > 상자 중앙값 (치명 후광·흰 번쩍을 빼려고).
결과 = 표(markdown) + _measure/<이름>.png(확인용: 원본 | 채움 빨강 · 테 초록 · 바탕 파랑).
영상은 h264 crf 18(4:2:0) — 1~2px 테는 색 번짐이 있어 값은 「화면에서 이 정도」로 읽는다.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from colorsci import contrast, de76, de2000, deut, prot, trit, hexrgb

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent
DBG = R / "_measure"
DBG.mkdir(exist_ok=True)

# 이름 · 클립 · n · 판 N716 상자(x, y, w, h) · 채움 찾기 · 사양 헥스 · 판 A 상자(같은 숫자 · 보통 숫자는 가로 흔들림이 난수라 자리가 다르다 — None = 판 A 없음)
# 검수 뒤 다시 찍음(#716 fix): 상자는 새 클립 프레임에서 다시 잡았다 · 부적 터짐 숫자는 판마다 1~4 다름(부적 비행 난수 — 이름은 판 N716 값)
SAMPLES = [
    ("물리 보통 12 (들녘)", "01_basic", 46, (705, 248, 26, 19), "lum", "#F2EDE0", (710, 249, 24, 18)),
    ("칼+무기 불(불 우세) 16", "01_basic", 268, (704, 249, 28, 20), "sat", "#FF6E3A", (703, 249, 24, 18)),
    ("부적 화염 터짐 11", "03_fire", 84, (902, 220, 24, 19), "sat", "#FF6E3A", (909, 221, 22, 18)),
    ("부적 빙결 7", "04_cold", 100, (869, 221, 14, 18), "lum", "#7FD0FF", (877, 223, 14, 18)),
    ("벽력부 터짐 24", "08_lightning", 72, (865, 251, 22, 17), "lum", "#D8CCFF", None),
    ("치명 20(+6f, 버팀)", "02_crit", 106, (698, 246, 46, 26), "sat", "#FFB847", None),
    ("큰 치명 121(오름)", "02_crit", 180, (682, 172, 70, 40), "sat", "#FFB847", None),
    ("처치(화염부) 12", "06_kill", 182, (843, 267, 46, 32), "sat", "#FF6E3A", None),
    ("화상 틱 8", "03_fire", 200, (909, 240, 13, 17), "sat", "#E3794F", (909, 240, 13, 17)),
    ("진(불) 틱 4", "03_fire", 262, (908, 233, 14, 16), "sat", "#E3794F", None),
    ("물리 보통 12 (흑랑 굴)", "11_cave", 46, (709, 247, 25, 19), "lum", "#F2EDE0", (707, 248, 22, 18)),
    ("물리 처치 13 (흑랑 굴)", "11_cave", 237, (718, 218, 40, 30), "lum", "#FFF8EC", (716, 219, 44, 35)),
    ("물리 보통 12 (못골 흙)", "12_town", 46, (705, 247, 27, 18), "lum", "#F2EDE0", (705, 248, 24, 19)),
    ("물리 처치 13 (못골 흙)", "12_town", 247, (685, 191, 42, 32), "lum", "#FFF8EC", (684, 193, 40, 33)),
]


def frame(plate, clip, n):
    return np.asarray(Image.open(R / "_frames" / f"{plate}_{clip}" / f"{n + 1:04d}.png").convert("RGB"), dtype=np.float64)


def measure(img, box, mode):
    x, y, w, h = box
    a = img[y:y + h, x:x + w]
    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    if mode == "lum":
        fill = lum > (lum.min() + lum.max()) / 2
    else:
        fill = (sat > 0.42) & (lum > np.median(lum))
        if fill.sum() < 6:   # 판 A의 미색 숫자 — 밝기로
            fill = lum > (lum.min() + lum.max()) / 2
    lab, n = ndimage.label(fill)
    if n > 1:   # 작은 티끌(번짐·불똥)은 뺀다 — 4px 넘는 덩어리만
        sizes = ndimage.sum(fill, lab, range(1, n + 1))
        fill = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 4])
    core = ndimage.binary_erosion(fill)
    if core.sum() < 3:
        core = fill & (lum >= np.median(lum[fill]))
    ring = ndimage.binary_dilation(fill, iterations=2) & ~fill
    ring_l = lum[ring]
    edge = ring & (lum <= np.median(ring_l))
    bg = ~ndimage.binary_dilation(fill, iterations=4)
    fc = np.median(a[core], 0)
    oc = np.median(a[edge], 0)
    bc = np.median(a[bg], 0) if bg.any() else oc
    dbg = a.copy()
    dbg[core] = [255, 0, 0]
    dbg[edge] = [0, 255, 0]
    dbg[bg] = dbg[bg] * 0.4 + np.array([0, 0, 150]) * 0.6
    return fc, oc, bc, int(core.sum()), np.concatenate([a, dbg], 1)


def hx(c):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)


rows = []
got = {}
for name, clip, n, box, mode, spec, box_a in SAMPLES:
    for plate, b in [("N716", box)] + ([("A", box_a)] if box_a else []):
        m = mode if plate == "N716" or "틱" in name else "lum"
        if plate == "A" and "처치" in name and "물리" in name:
            m = "sat"   # 판 A 처치 = 붉은금 채움
        fc, oc, bc, npx, dbg = measure(frame(plate, clip, n), b, m)
        Image.fromarray(dbg.astype(np.uint8)).resize((dbg.shape[1] * 8, dbg.shape[0] * 8), Image.NEAREST).save(DBG / f"{plate}_{clip}_{n}.png")
        got[(plate, name)] = fc
        rows.append((plate, name, f"{clip} f{n}", spec if plate == "N716" else "—", hx(fc), npx, hx(oc), contrast(fc, oc), hx(bc), contrast(fc, bc)))

print("| 판 | 숫자 | 프레임 | 사양 채움 | 화면 채움 중앙 (px) | 화면 테 | 채움:테 | 화면 바탕 | 채움:바탕 |")
print("|---|---|---|---|---|---|---|---|---|")
for p, name, fr, spec, f, npx, o, c1, b, c2 in rows:
    print(f"| {p} | {name} | {fr} | {spec} | {f} ({npx}) | {o} | {c1:.1f} | {b} | {c2:.1f} |")

print("\n| 쌍 | 화면 ΔE76 | 적록 deut ΔE76 (2000) | 적색 prot ΔE76 (2000) | 청색 trit ΔE76 (2000) |")
print("|---|---|---|---|---|")
pairs = [("부적 화염 터짐 11", "치명 20(+6f, 버팀)"), ("부적 화염 터짐 11", "큰 치명 121(오름)"), ("칼+무기 불(불 우세) 16", "치명 20(+6f, 버팀)"),
         ("처치(화염부) 12", "큰 치명 121(오름)"), ("화상 틱 8", "치명 20(+6f, 버팀)"), ("화상 틱 8", "부적 화염 터짐 11"),
         ("벽력부 터짐 24", "치명 20(+6f, 버팀)"), ("벽력부 터짐 24", "부적 빙결 7")]


def sims(ca, cb):
    return " | ".join(f"{de76(f(ca), f(cb)):.1f} ({de2000(f(ca), f(cb)):.1f})" for f in (deut, prot, trit))


for a, b in pairs:
    ca, cb = got[("N716", a)], got[("N716", b)]
    print(f"| {a} ↔ {b} | {de76(ca, cb):.1f} | {sims(ca, cb)} |")
f, g = hexrgb("#FF6E3A"), hexrgb("#FFB847")
print(f"| (헥스) #FF6E3A ↔ #FFB847 | {de76(f, g):.1f} | {sims(f, g)} |")
