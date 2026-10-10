"""#716 판정 사진 (게임 저장소 docs/art/716_damage_numbers/): 줄 = 판(지금 / 새 숫자 강) 또는 (원본 / 적록 색약 시뮬), 칸 = 클립 프레임.
python stills.py <out_dir>   — 프레임 = _frames/<판>_<클립>/(클립 mp4에서 한 번 뽑아 둔 것 — 다시 찍었으면 _frames를 지우고) · 사진 ≤ 1280 폭 · jpg ≤ 300 KB.
<out_dir> = 판정 사진 6장(게임 저장소 docs/art — 카드당 ≤ 6) · 그 밖(광역 8 · Alt 이름표 · 연속 베기) = reports/716/stills/.
색약 시뮬 = Machado 2009 세기 1.0(선형 RGB) — 적록(deut) · 적색(prot) · 청색(trit), colorsci.
"""
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from colorsci import deut, prot, trit

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
FB = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 17)
FR = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 14)
FT = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 19)
W = 1280
ROWLBL = 104


def frame(plate, clip, n):
    fdir = R / "_frames" / f"{plate}_{clip}"
    if not fdir.exists():
        fdir.mkdir(parents=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(R / plate / f"{clip}.mp4"), "-vsync", "0", str(fdir / "%04d.png")], check=True)
    return Image.open(fdir / f"{n + 1:04d}.png").convert("RGB")


SIMS = {"deut": deut, "prot": prot, "trit": trit}


def as_sim(im, kind):
    a = np.asarray(im, dtype=np.float64)
    return Image.fromarray(np.clip(np.round(SIMS[kind](a)), 0, 255).astype(np.uint8))


def still(name, title, rows, cols, aspect=1.25, out=None):
    """rows = [(plate, label, color, 시뮬 = None|"deut"|"prot"|"trit")] · cols = [(clip, n, (x, y, w), header)] — 칸 높이 = w / aspect."""
    cw = (W - ROWLBL) // len(cols)
    ch = round((cw - 4) / aspect)
    top, head = 34, 40
    im = Image.new("RGB", (W, top + head + len(rows) * (ch + 6)), "#0d0d0f")
    d = ImageDraw.Draw(im)
    d.text((10, 6), title, font=FT, fill="#f3e6c4")
    for r, (plate, lbl, col, sim) in enumerate(rows):
        y = top + head + r * (ch + 6)
        d.multiline_text((10, y + ch // 2 - 22), lbl, font=FB, fill=col, spacing=4)
        for i, (clip, n, (x0, y0, w0), header) in enumerate(cols):
            h0 = round(w0 / aspect)
            cell = frame(plate, clip, n).crop((x0, y0, x0 + w0, y0 + h0))
            if sim:
                cell = as_sim(cell, sim)
            im.paste(cell.resize((cw - 4, ch), Image.LANCZOS), (ROWLBL + i * cw + 2, y))
    for i, (clip, n, _, header) in enumerate(cols):
        d.multiline_text((ROWLBL + i * cw + 6, top + 1), header, font=FR, fill="#d8d2c4", spacing=1)
    p = (out or OUT) / f"{name}.jpg"
    q = 90
    while True:
        im.save(p, quality=q, optimize=True)
        if p.stat().st_size <= 300_000 or q <= 60:
            break
        q -= 4
    print(p, im.size, round(p.stat().st_size / 1000), "KB q", q)


EXTRA = R / "stills"
EXTRA.mkdir(exist_ok=True)
AN = [("A", "지금\n판 A", "#f3e6c4", None), ("N716", "새 숫자(강)\n판 N716", "#ffc86a", None)]
CVD = [("N716", "새 숫자(강)\n원본", "#ffc86a", None), ("N716", "적록 색약\n(deut)", "#9fd8ff", "deut"),
       ("N716", "적색 색약\n(prot)", "#9fd8ff", "prot"), ("N716", "청색 색약\n(trit)", "#9fd8ff", "trit")]
CRIT = [("02_crit", 100, (600, 130, 300), "치명 20 — 박힌 첫 프레임\n(f100)"),
        ("02_crit", 106, (600, 130, 300), "+6프레임 — 적이 멈춘 동안\n버팀(f106)"),
        ("02_crit", 156, (560, 110, 340), "큰 치명 121 — 첫 프레임\n(f156 · 상한 12%로 2.6→2.1배)"),
        ("02_crit", 180, (560, 110, 340), "+24프레임 — 오르기 시작\n(f180)")]
FIRE = [("03_fire", 84, (720, 140, 400), "화염부 터짐 — 불 숫자\n(f84 · 판마다 터짐 숫자만 다름)"),
        ("03_fire", 200, (720, 140, 400), "화상 틱 — 숯불 #E3794F 18\n(f200)"),
        ("03_fire", 262, (720, 140, 400), "부적 진(불) 틱 + 화상\n(f262)")]

still("716_crit_A_N716", "치명 — 지금(금빛 채움·튐) vs 새 숫자(강: 금니 #FFB847 · 2.3배로 박혀 적이 멈춘 0.16초 동안 버팀 · 출현 상한 = 화면 높이 12%)", AN, CRIT)
still("716_fire_A_N716", "불 — 지금(부적 터짐도 미색) vs 새 숫자(불 #FF6E3A 알파 1.0 + 표식 · 틱 = 숯불 #E3794F 1.0 · 18)", AN, FIRE, aspect=1.4)
still("716_lightning_A_N716", "벼락(PD ②) — 지금(금빛 표식·미색 숫자) vs 새 숫자(숫자·표식 모두 옅은 보랏빛 흰 #D8CCFF · 이펙트 빛은 금빛 그대로)", AN, [
    ("08_lightning", 72, (700, 170, 360), "벽력부 터짐 — 첫 프레임 +2\n(f72 · 판마다 터짐 숫자만 다름)"),
    ("08_lightning", 84, (700, 140, 360), "+12프레임 — 오름\n(f84)"),
    ("08_lightning", 250, (720, 150, 380), "부적 진(벼락) 틱 셋\n(f250)")], aspect=1.4)
still("716_bg_A_N716", "배경 — 흑랑 굴(어두움 = 채움이 지킨다) · 못골 흙(밝음 = 테가 지킨다): 큰 치명 · 물리 처치(흰 #FFF8EC · 테 12)", AN, [
    ("11_cave", 158, (560, 130, 320), "흑랑 굴 — 큰 치명 121\n(f158)"),
    ("11_cave", 237, (580, 150, 320), "흑랑 굴 — 칼 처치 13\n(f237)"),
    ("12_town", 158, (540, 150, 340), "못골 흙 — 큰 치명 121\n(f158)"),
    ("12_town", 247, (540, 130, 340), "못골 흙 — 칼 처치 13\n(f247)")])
still("716_kill_mixed_A_N716", "섞인 한 방 · 처치 — 칼+무기 불(불 우세 = 불 색 하나 + 표식) · 칼 처치 · 치명 처치 · 화염부 처치(붉은금 없음)", AN, [
    ("01_basic", 268, (560, 110, 300), "칼+무기 불 16\n(f268)"),
    ("06_kill", 46, (520, 130, 320), "칼 처치 12\n(f46)"),
    ("06_kill", 102, (600, 110, 320), "치명 처치 20\n(f102)"),
    ("06_kill", 182, (700, 160, 320), "화염부 처치\n(f182)")])
still("716_cvd_N716", "색약 시뮬 3종(Machado 2009, 세기 1.0) — 새 숫자(강): 치명 금니 · 불 · 숯불 틱 · 벼락이 모양·크기로도 갈리는지", CVD, [
    ("02_crit", 106, (600, 130, 300), "치명 20\n(02 f106)"),
    ("03_fire", 84, (720, 140, 400), "불 터짐\n(03 f84)"),
    ("03_fire", 200, (720, 140, 400), "숯불 틱\n(03 f200)"),
    ("08_lightning", 72, (700, 170, 360), "벼락 터짐\n(08 f72)")], aspect=1.4)
# 그 밖 — reports/716/stills/
still("716_aoe8_A_N716", "회오리베기 여덟 몸 — 치명 40% · 셋 처치 (같은 난수 = 같은 숫자 · 2.3~2.6배 치명 넷이 첫 프레임에 겹침 → #657 bounds)", AN, [
    ("05_aoe8", 63, (440, 60, 540), "닿은 첫 프레임 +1\n(f63)"),
    ("05_aoe8", 70, (440, 60, 540), "+8프레임\n(f70)"),
    ("05_aoe8", 92, (440, 60, 540), "+30프레임 — 보통은 오르고\n치명은 남음(f92)")], aspect=1.4, out=EXTRA)
still("716_elite_alt_A_N716", "Alt 이름표 — 금색 우두머리(이름 금빛) · 파란 정예 위 치명 금니", AN, [
    ("10_elite_alt", 101, (560, 150, 320), "치명 20 — 첫 프레임\n(f101)"),
    ("10_elite_alt", 107, (560, 150, 320), "+6프레임 버팀\n(f107)"),
    ("10_elite_alt", 130, (560, 120, 320), "+29프레임 오름\n(f130)")], aspect=1.4, out=EXTRA)
still("716_flurry_A_N716", "연속 베기 Lv10 — 다섯 타 · 치명 40% (한 적 위에 쌓임)", AN, [
    ("09_flurry", 72, (560, 140, 320), "둘째 타 치명 58\n(f72)"),
    ("09_flurry", 136, (560, 120, 320), "넷째 타 치명\n(f136)"),
    ("09_flurry", 232, (560, 100, 320), "일곱째 타 치명 + 앞 숫자들\n(f232)")], aspect=1.4, out=EXTRA)
