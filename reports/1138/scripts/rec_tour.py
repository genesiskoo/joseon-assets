"""#1138 비교 영상 — 동작 확인 툴(motion_viewer) 「한 바퀴」를 녹화해 mp4로 (enemy_tour_videos.record_one 과 같은 길).

    python rec_tour.py <작업 트리> <태그> <출력 폴더>
태그마다 두 판: walk = --set=move_speed=1.2 (쫓아옴을 걷기로) · run = 데이터 그대로(보스 쫓기 4.0 = 달리기).
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
root = Path(sys.argv[1]).resolve()
tag = sys.argv[2]
out = Path(sys.argv[3]).resolve()
sys.path.insert(0, str(root / "tools"))
import render_lab as RL  # noqa: E402

WIN = (1280, 720)
CROP = "crop=800:632:190:0"
NOWIN = subprocess.CREATE_NO_WINDOW
godot = RL.godot_bin(None)
out.mkdir(parents=True, exist_ok=True)

runs = {"walk": ["--set=move_speed=1.2"], "run": []}
with RL.E2eLock():
    for name, extra in runs.items():
        raw = out / f"_raw_{tag}_{name}"
        if raw.exists():
            shutil.rmtree(raw)
        cmd = [godot, "--path", str(root), "--windowed", "--position", "0,0", "--resolution", "%dx%d" % WIN,
               "res://tools/motion_viewer.tscn", "--", "--model=boss_heukrang", f"--record={raw.as_posix()}"] + extra
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=NOWIN, timeout=600)
        said = [l for l in r.stdout.splitlines() if l.startswith("[motion_viewer]")]
        frames = sorted(raw.glob("rec_*.png"))
        print(tag, name, len(frames), "frames", said[-3:] if said else r.stderr[-300:], flush=True)
        if not frames:
            continue
        mp4 = out / f"{tag}_{name}.mp4"
        subprocess.run([RL.ffmpeg_bin(), "-hide_banner", "-loglevel", "error", "-y", "-framerate", "30", "-i", str(raw / "rec_%03d.png"),
                        "-vf", CROP, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(mp4)], check=True, creationflags=NOWIN)
        # 판정용 정지 컷 몇 장은 남긴다(대기 · 걷기 · 물기 · 죽기 끝)
        keep = out / f"_stills_{tag}_{name}"
        keep.mkdir(exist_ok=True)
        for i in (15, len(frames) // 3, len(frames) // 2, len(frames) - 5):
            if 0 <= i < len(frames):
                shutil.copy2(frames[i], keep / frames[i].name)
        shutil.rmtree(raw)
        print("  ->", mp4, mp4.stat().st_size // 1024, "KB", flush=True)
