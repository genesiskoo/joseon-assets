"""#716 피해 숫자 판정 영상 — 같은 대본 _feel_numbers_demo 를 판 A(지금)·N716(새 숫자 강)·N716L(새 숫자 약)로 찍은 클립을 나란히.
python make_media.py   (events.py 뒤 · 결과 = reports/716/)
  716_A_N716_sbs_1·_2.mp4   지금 | 새 숫자(강), 1배, 클립 01~07 · 08~12 이음(파일 < 10MB) · 소리 왼쪽 귀 = 지금, 오른쪽 귀 = 새 숫자
  716_A_N716_slow025.mp4    같은 나란히 0.25배 — 클립마다 숫자가 튀는 창만(SLOW, 소리 없음)
  716_N716_N716L_sbs.mp4    새 숫자(강) | 새 숫자(약), 1배
화면 = 1280×720 원본에서 클립마다 싸움 자리를 잘라 640×420 두 칸으로(확대 1.0~1.33배, lanczos). 오른쪽 아래 f = 클립 프레임(60fps, 1프레임 = 1틱).
"""
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent
LBL = R / "_labels"
SEG = R / "_segments"
LBL.mkdir(exist_ok=True)
SEG.mkdir(exist_ok=True)
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
FONT_R = "C:/Windows/Fonts/malgun.ttf"
MONO = "C\\:/Windows/Fonts/consola.ttf"
EV = json.loads((R / "events.json").read_text(encoding="utf-8"))
PW, PH = 640, 420

NAMES = {
    "01_basic": "칼 연타 — 보통 셋 · 큰 타격 · 칼+무기 불(불 우세) · 칼+무기 불(불 30%)",
    "02_crit": "보통 → 치명 → 큰 치명",
    "03_fire": "화염부 던지기(터짐 + 화상 틱) → 부적 진(불) 틱",
    "04_cold": "빙결부 던지기 → 부적 진(한기) 틱",
    "05_aoe8": "회오리베기 여덟 몸 — 치명 40% · 셋 처치",
    "06_kill": "칼 처치 → 치명 처치 → 화염부 처치",
    "07_bulgasari_heat": "불가살이 — 철갑 칼 둘 → 달아오름 → 칼 둘",
    "08_lightning": "벽력부 던지기(벼락 숫자·표식) → 부적 진(벼락) 틱",
    "09_flurry": "연속 베기 Lv10 — 다섯 타 · 치명 40%",
    "10_elite_alt": "Alt 이름표 — 금색 우두머리 · 파란 정예 · 칼 치명 40%",
    "11_cave": "흑랑 굴(어두움) — 보통 · 치명 · 큰 치명 · 칼 처치 · 화염부",
    "12_town": "못골 흙(밝음) — 보통 · 치명 · 큰 치명 · 칼 처치",
}
CROP = {
    "01_basic": (480, 110, 480, 315),
    "02_crit": (520, 110, 480, 315),
    "03_fire": (600, 90, 520, 341),
    "04_cold": (600, 90, 520, 341),
    "05_aoe8": (440, 60, 560, 368),
    "06_kill": (500, 100, 560, 368),
    "07_bulgasari_heat": (420, 40, 600, 394),
    "08_lightning": (600, 100, 560, 368),
    "09_flurry": (480, 90, 520, 341),
    "10_elite_alt": (460, 100, 520, 341),
    "11_cave": (460, 80, 600, 394),
    "12_town": (440, 60, 600, 394),
}
## 0.25배 창(클립 프레임) — 숫자가 튀는 순간만: 01 큰 타격·섞인 둘 · 02 전부 · 03 터짐·화상 틱 · 04 터짐 · 05 회오리 · 06 처치 셋 · 07 달아오른 뒤
SLOW = {"01_basic": (204, 340), "02_crit": (37, 224), "03_fire": (75, 200), "04_cold": (72, 150), "05_aoe8": (56, 137), "06_kill": (37, 247), "07_bulgasari_heat": (160, 240),
        "08_lightning": (66, 160), "09_flurry": (36, 270), "10_elite_alt": (96, 230), "11_cave": (96, 250), "12_town": (96, 300)}
PLATE_LABEL = {"A": ("지금 (판 A)", "#f3e6c4"), "N716": ("새 숫자(강) — 판 N716", "#ffc86a"), "N716L": ("새 숫자(약) — 판 N716L", "#9fd8ff")}


def png(name, im):
    p = LBL / f"{name}.png"
    im.save(p)
    return p


def label(name, big, color):
    fb = ImageFont.truetype(FONT_B, 24)
    im = Image.new("RGBA", (PW - 20, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tw = d.textlength(big, font=fb)
    d.rounded_rectangle((0, 0, int(tw) + 24, 40), 8, fill=(10, 10, 12, 200))
    d.text((12, 2), big, font=fb, fill=color)
    return png(name, im)


def footer(name, text):
    f = ImageFont.truetype(FONT_R, 16)
    im = Image.new("RGBA", (2 * PW, 30), (8, 8, 10, 235))
    ImageDraw.Draw(im).text((12, 4), text, font=f, fill="#cfc8b8")
    return png(name, im)


def run(args, log):
    with open(SEG / log, "w", encoding="utf-8") as fh:
        r = subprocess.run(args, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode:
        print((SEG / log).read_text(encoding="utf-8", errors="replace")[-3000:])
        raise SystemExit(f"ffmpeg failed: {log}")


def segment(left, right, clip, slow, tag):
    c = EV[left]["clips"][clip]
    n_frames = min(c["frames"], EV[right]["clips"][clip]["frames"])
    if slow:
        start, end = SLOW[clip]
        end = min(n_frames, end)
    else:
        start, end = 0, n_frames
    x, y, w, h = CROP[clip]
    crop = f"crop={w}:{h}:{x}:{y},scale={PW}:{PH}:flags=lanczos"
    ll = label(f"{clip}_{tag}_L", *PLATE_LABEL[left])
    lr = label(f"{clip}_{tag}_R", *PLATE_LABEL[right])
    foot = footer(f"{clip}_{tag}_{'slow' if slow else 'sbs'}_foot",
                  (f"0.25배 · {NAMES[clip]}" if slow else f"1배 · {NAMES[clip]} · 소리: 왼쪽 귀 = 왼쪽 판, 오른쪽 귀 = 오른쪽 판"))
    ins = ["-i", str(R / left / f"{clip}.mp4"), "-i", str(R / right / f"{clip}.mp4"), "-i", str(ll), "-i", str(lr), "-i", str(foot)]
    trim = f"trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,"
    g = (f"[0:v]{trim}{crop}[c0];[c0][2:v]overlay=8:8[p0];"
         f"[1:v]{trim}{crop}[c1];[c1][3:v]overlay=8:8[p1];"
         f"[p0][p1]hstack=2[hs];[hs]pad={2 * PW}:{PH + 30}:0:0:color=0x0a0a0c[pd];[pd][4:v]overlay=0:{PH}[v0];"
         f"[v0]drawtext=fontfile='{MONO}':text='f %{{eif\\:n+{start}\\:d}}':x={2 * PW}-90:y={PH + 6}:fontsize=17:fontcolor=0xd8d2c4"
         + (",setpts=4*PTS,fps=60" if slow else "") + ",format=yuv420p[v]")
    if not slow:
        g += (f";[0:a]atrim=end_sample={int(end / 60 * 48000)},asetpts=PTS-STARTPTS,pan=mono|c0=0.5*c0+0.5*c1[al];"
              f"[1:a]atrim=end_sample={int(end / 60 * 48000)},asetpts=PTS-STARTPTS,pan=mono|c0=0.5*c0+0.5*c1[ar];"
              f"[al][ar]join=inputs=2:channel_layout=stereo,aresample=48000[a]")
    gp = SEG / f"{clip}_{tag}_{'slow' if slow else 'sbs'}.txt"
    gp.write_text(g, encoding="utf-8")
    out = SEG / f"{clip}_{tag}_{'slow' if slow else 'sbs'}.mp4"
    maps = ["-map", "[v]"] + (["-map", "[a]", "-c:a", "aac", "-b:a", "160k", "-ar", "48000"] if not slow else ["-an"])
    run(["ffmpeg", "-hide_banner", "-y", *ins, "-/filter_complex", str(gp), *maps, "-r", "60",
         "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p", str(out)], f"{out.stem}.log")
    return out, start, end


def concat(parts, out_name):
    lst = SEG / f"{out_name}.list"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    out = R / f"{out_name}.mp4"
    run(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)], f"{out_name}_concat.log")
    print("wrote", out, round(out.stat().st_size / 1e6, 2), "MB")


windows = {}
for left, right, tag, slow_too in [("A", "N716", "AN", True), ("N716", "N716L", "NL", False)]:
    sbs, slow = [], []
    for clip in NAMES:
        p, s0, s1 = segment(left, right, clip, False, tag)
        sbs.append(p)
        windows[f"{tag}_{clip}_sbs"] = [s0, s1]
        if slow_too:
            q, w0, w1 = segment(left, right, clip, True, tag)
            slow.append(q)
            windows[f"{tag}_{clip}_slow"] = [w0, w1]
    concat(sbs[:7], f"716_{left}_{right}_sbs_1")   # 01~07 · 파일 하나 < 10MB(D-100)
    concat(sbs[7:], f"716_{left}_{right}_sbs_2")   # 08~12(검수 뒤 더한 클립)
    if slow_too:
        concat(slow[:7], f"716_{left}_{right}_slow025_1")
        concat(slow[7:], f"716_{left}_{right}_slow025_2")
(SEG / "windows.json").write_text(json.dumps(windows, indent=1), encoding="utf-8")
print(json.dumps(windows))


## 74fps 0.25배 — 판 N716 02 치명만 한 칸(사양 S11 「--fixed-fps 74」: 54ms 박힘 = 74Hz 4프레임 · 60fps는 3프레임). 클립 프레임 창은 events가 아니라 74fps 로그에서.
def slow74():
    import re
    raw = (R / "N716_74fps" / "capture_raw.log").read_text(encoding="utf-8", errors="replace")
    b = int(re.search(r"CAPTURE 02_crit BEGIN (\d+)", raw).group(1))
    hits = [int(f) - b + 1 for f in re.findall(r"NUMDEMO 02_crit DMG (\d+)", raw)]
    start, end = max(0, hits[1] - 8), hits[2] + 90
    x, y, w, h = CROP["02_crit"]
    lab = label("02_crit_74_L", "새 숫자(강) — 74fps 녹화 · 0.25배", "#ffc86a")
    foot = footer("02_crit_74_foot", "74fps(물리 60Hz) · 0.25배 · 치명 → 큰 치명 — 박힘 54ms = 74Hz 4프레임")
    g = (f"[0:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale={2 * PW}:{2 * PH}:flags=lanczos[c];"
         f"[c][1:v]overlay=8:8[p];[p]pad={2 * PW}:{2 * PH + 30}:0:0:color=0x0a0a0c[pd];[pd][2:v]overlay=0:{2 * PH}[v0];"
         f"[v0]drawtext=fontfile='{MONO}':text='f %{{eif\\:n+{start}\\:d}}':x={2 * PW}-90:y={2 * PH + 6}:fontsize=17:fontcolor=0xd8d2c4,setpts=4*PTS,fps=60,format=yuv420p[v]")
    gp = SEG / "02_crit_74_slow.txt"
    gp.write_text(g, encoding="utf-8")
    out = R / "716_N716_74fps_crit_slow025.mp4"
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(R / "N716_74fps" / "02_crit.mp4"), "-i", str(lab), "-i", str(foot), "-/filter_complex", str(gp),
         "-map", "[v]", "-an", "-r", "60", "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], "02_crit_74_slow.log")
    print("wrote", out, round(out.stat().st_size / 1e6, 2), "MB", "window", start, end)


if (R / "N716_74fps" / "02_crit.mp4").exists():
    slow74()
