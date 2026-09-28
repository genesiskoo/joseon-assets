"""#497 원본 1080p 프레임 저장 — python grab.py <clip> <frame> <out.jpg>"""
import re, subprocess, os, sys
WORK = os.path.dirname(os.path.abspath(__file__))
mk = {}
for line in open(os.path.join(WORK, "capture_1080_out.log"), encoding="utf-8", errors="replace"):
    m = re.match(r"CAPTURE (\S+) (BEGIN|END) (\d+)", line.strip())
    if m:
        mk.setdefault(m.group(1), {})[m.group(2)] = int(m.group(3))
clip, f, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
t = (mk[clip]["BEGIN"] + f) / 30
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", os.path.join(WORK, "capture_1080.avi"), "-frames:v", "1", "-q:v", "1", "-qmin", "1", out], check=True)
print(out)
