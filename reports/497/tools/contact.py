"""#497 스크린샷 후보 — 클립마다 1초 간격 썸네일 대조표 + 30초 몽타주 라우드니스."""
import subprocess, sys, json, os
from PIL import Image, ImageDraw, ImageFont

SRC = r"C:\workspace\joseon-assets\reports\455\final"
OUT = r"C:\workspace\joseon\tmp\ile_497\work"
CLIPS = ["01_motgol_walk", "02_dialogue_quest", "05_dungeon_combat", "06_heukrang_boss", "07_loot_inventory", "08_skills_equipment", "03_field_exploration", "04_cave_entry"]
TW, TH = 384, 216


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


font = ImageFont.load_default()
for c in CLIPS:
    p = os.path.join(SRC, c + ".mp4")
    d = dur(p)
    tdir = os.path.join(OUT, "thumbs_" + c)
    os.makedirs(tdir, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-vf", f"fps=1,scale={TW}:{TH}", os.path.join(tdir, "t_%03d.jpg")], check=True)
    files = sorted(f for f in os.listdir(tdir) if f.endswith(".jpg"))
    cols = 5
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * TW, rows * (TH + 16)), (20, 20, 20))
    dr = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(os.path.join(tdir, f))
        x, y = (i % cols) * TW, (i // cols) * (TH + 16)
        sheet.paste(im, (x, y))
        # fps=1 필터의 i번째 프레임 ≈ i+0.5초 근처
        dr.text((x + 4, y + TH + 2), f"{c} t={i + 0.5:.1f}s", fill=(255, 220, 120), font=font)
    sheet.save(os.path.join(OUT, f"sheet_{c}.jpg"), quality=80)
    print(c, f"{d:.2f}s", len(files), "frames", flush=True)

m = r"C:\workspace\joseon-assets\reports\456\joseon_hunters_vertical_slice_30s.mp4"
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", m, "-af", "loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
print(r.stderr[-900:])
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,bit_rate,sample_rate,channels", "-of", "compact", m], capture_output=True, text=True)
print(r.stdout)
