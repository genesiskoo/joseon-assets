"""#1138 비교 영상 합치기 — 왼쪽 = 지금 몸 · 오른쪽 = 새 몸, 위 글자 띠, 판(걷기 한 바퀴 → 달리기 한 바퀴) 이어 붙임.

    python compose.py <rec 폴더> <out.mp4> [--left "글"] [--right "글"]
짧은 쪽은 마지막 장면으로 늘려 길이를 맞춘다(tpad).
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
rec = Path(sys.argv[1])
out = Path(sys.argv[2])
args = sys.argv[3:]
left = args[args.index("--left") + 1] if "--left" in args else "지금 몸 (Hunyuan3D v3 · 10,000)"
right = args[args.index("--right") + 1] if "--right" in args else "새 몸 (Tripo H3.1 시험)"
FONT = "C:/Windows/Fonts/malgunbd.ttf"
W, H, BAR = 800, 632, 46
seg_titles = {"walk": "① 대기 → 걷기(쫓아옴 1.2) → 물기 ×2 → 맞기 ×2 → 죽기", "run": "② 보스 쫓기 4.0 = 달리기 → 물기 ×2 → 맞기 ×2 → 죽기"}


def bar(seg: str) -> Path:
    im = Image.new("RGB", (W * 2, BAR + 30), (22, 20, 24))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 24)
    f2 = ImageFont.truetype(FONT, 18)
    for i, t in enumerate((left, right)):
        tw = d.textlength(t, font=f)
        d.text((i * W + (W - tw) / 2, 8), t, fill=(235, 225, 205), font=f)
    st = seg_titles[seg]
    d.text(((W * 2 - d.textlength(st, font=f2)) / 2, BAR + 4), st, fill=(170, 165, 160), font=f2)
    d.line([(W, 0), (W, BAR + 30)], fill=(90, 85, 80), width=2)
    p = rec / f"_bar_{seg}.png"
    im.save(p)
    return p


def dur(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


parts = []
for seg in ("walk", "run"):
    a, b = rec / f"old_{seg}.mp4", rec / f"new_{seg}.mp4"
    if not (a.exists() and b.exists()):
        print("빠짐:", seg, a.exists(), b.exists())
        continue
    da, db = dur(a), dur(b)
    m = max(da, db)
    p = rec / f"_cmp_{seg}.mp4"
    fc = (f"[0:v]tpad=stop_mode=clone:stop_duration={m - da + 0.04:.3f}[a];"
          f"[1:v]tpad=stop_mode=clone:stop_duration={m - db + 0.04:.3f}[b];"
          f"[a][b]hstack=inputs=2[s];[2:v][s]vstack=inputs=2,trim=duration={m:.3f},setsar=1[v]")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(a), "-i", str(b), "-loop", "1", "-i", str(bar(seg)),
                    "-filter_complex", fc, "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(p)], check=True)
    parts.append(p)
    print(seg, f"지금 {da:.2f}s · 새 {db:.2f}s → {m:.2f}s")
lst = rec / "_concat.txt"
lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                "-movflags", "+faststart", str(out)], check=True)
print("->", out, out.stat().st_size // 1024, "KB", f"{dur(out):.1f}s")
