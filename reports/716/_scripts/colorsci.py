"""#716 색 셈 — sRGB ↔ 선형 · Machado(2009) 적록 색약(deuteranopia, 세기 1.0) 시뮬 · CIELAB(D65) · ΔE76/ΔE2000 · WCAG 대비."""
import numpy as np

# Machado, Oliveira, Fernandes 2009 — deuteranopia severity 1.0 (선형 RGB에 곱한다)
DEUT = np.array([[0.367322, 0.860646, -0.227968],
                 [0.280085, 0.672501, 0.047413],
                 [-0.011820, 0.042940, 0.968881]])


def to_lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(l):
    l = np.clip(l, 0.0, 1.0)
    return np.where(l <= 0.0031308, l * 12.92, 1.055 * l ** (1 / 2.4) - 0.055) * 255.0


def deut(rgb):
    """rgb (…,3) 0..255 → 색약 시뮬 rgb 0..255."""
    lin = to_lin(rgb)
    return to_srgb(lin @ DEUT.T)


def lab(rgb):
    lin = to_lin(rgb)
    m = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def de76(a, b):
    return float(np.linalg.norm(lab(a) - lab(b)))


def de2000(a, b):
    L1, a1, b1 = lab(a)
    L2, a2, b2 = lab(b)
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    if C1p * C2p == 0:
        dh = 0
    elif dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = 1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp)) + 0.32 * np.cos(np.radians(3 * hbp + 6)) - 0.20 * np.cos(np.radians(4 * hbp - 63))
    dth = 30 * np.exp(-((hbp - 275) / 25) ** 2)
    Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dth)) * Rc
    return float(np.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh)))


def rel_lum(rgb):
    l = to_lin(rgb)
    return float(l[..., 0] * 0.2126 + l[..., 1] * 0.7152 + l[..., 2] * 0.0722)


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


if __name__ == "__main__":
    fire, gold, ink = hexrgb("#FF6E3A"), hexrgb("#FFB847"), hexrgb("#0D0B12")
    print("hex fire vs gold: dE76 %.1f dE2000 %.1f | deut dE76 %.1f dE2000 %.1f" % (de76(fire, gold), de2000(fire, gold), de76(deut(fire), deut(gold)), de2000(deut(fire), deut(gold))))
    for n, h in [("phys", "#F2EDE0"), ("fire", "#FF6E3A"), ("cold", "#7FD0FF"), ("light", "#D8CCFF"), ("gold", "#FFB847"), ("ember", "#D9623A")]:
        print(n, "contrast vs ink %.1f" % contrast(hexrgb(h), ink))
