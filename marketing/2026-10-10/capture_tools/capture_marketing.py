"""#721: native Godot gameplay capture, audio verification, and 4K screenshots.

Each --track is a short separate Movie Maker recording. --ui both records the same
scenario twice. The transient game checkout must register _marketing_capture.
Masters are deleted only after every deliverable fully decodes and passes checks.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

TRACKS = ["quest_accept", "quest_report", "cave", "effect_fire", "effect_cold",
          "effect_lightning", "effect_flurry", "effect_crit", "loot", "boss", "attack", "imugi"]
SPOILERS = {"quest_report": "quest_completion", "boss": "boss_gameplay", "imugi": "optional_enemy_gameplay"}
FIXTURES = {
    "quest_accept": "New E2E character; all captured dialogue waits for complete voice playback.",
    "quest_report": "Quest acceptance and cave clear prepared through existing damage path outside captured report; voiced report uses actual input.",
    "cave": "Existing slice Lv6 prepared character, learned sword skills and potion belt; real cave click and floor-one combat; normal enemy stats.",
    "boss": "Same prepared character; real boss-floor body and production AI/telegraph; initial charge cooldown set ready as existing heukrang_pounce scenario; normal boss stats.",
    "loot": "Representative magic/rare/unique items prepared using ItemInstance and ItemGen; production loot emission/landing/beams, ground pickup and identification input. Drops are staged, not presented as a random outcome.",
    "attack": "Current production recomputed player stats; stationary high-health dummy; production attack timing and animation; no timing override.",
    "imugi": "Native optional named imugi in actual deep pool; other enemies removed; natural full dive cooldown and normal dive values; prepared character uses actual belt potions.",
    "screenshots": "Native 4K scenic camera positions; static cave/boss enemies held for stills; five action pictures use the disclosed stationary-enemy effect showcase; no image resizing.",
}


def executable(name: str) -> str:
    path = shutil.which(name)
    if path:
        return path
    if name == "ffmpeg":
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    raise RuntimeError(f"Required executable unavailable: {name}")


def logged(command: list[str], log: Path, timeout: int = 1200) -> str:
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                                timeout=timeout,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    raw = log.read_text(encoding="utf-8", errors="replace")
    if result.returncode:
        print(raw, flush=True)
        raise RuntimeError(f"Command failed with exit {result.returncode}: {log}")
    return raw


def source_commit(game: Path) -> str:
    return subprocess.check_output(["git", "-C", str(game), "rev-parse", "HEAD"], text=True).strip()


def isolate_userdir(game: Path) -> None:
    # This file belongs only to the explicitly selected disposable game checkout.
    # Refuse the live main checkout so a capture never changes the player's save location.
    live = Path(r"C:\workspace\joseon").resolve()
    if game == live:
        raise RuntimeError("Use the dedicated marketing game worktree, not the live main checkout.")
    cfg = game / "override.cfg"
    raw = cfg.read_text(encoding="utf-8-sig") if cfg.exists() else ""
    section = '[application]\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="JoseonHunters_wt/721-marketing"\n'
    raw = re.sub(r"(?ms)^\[application\]\s*\n.*?(?=^\[|\Z)", "", raw)
    # Movie Maker initializes its output at boot from the project viewport dimensions,
    # not from --resolution. Configure native 1080p before launching the engine.
    # The capture script retains the game's 1280x720 logical canvas for UI and input.
    raw = re.sub(r"(?ms)^\[display\]\s*\n.*?(?=^\[|\Z)", "", raw)
    display = '[display]\nwindow/size/viewport_width=1920\nwindow/size/viewport_height=1080\nwindow/stretch/mode="canvas_items"\n'
    cfg.write_text(section + "\n" + display + "\n" + raw, encoding="utf-8")


def boundaries(raw: str) -> dict[str, dict[str, int]]:
    found: dict[str, dict[str, int]] = {}
    for name, edge, value in re.findall(r"CAPTURE (\S+) (BEGIN|END) (\d+)", raw):
        clip = found.setdefault(name, {})
        if edge in clip:
            raise RuntimeError(f"Duplicate boundary {name} {edge}")
        clip[edge] = int(value)
    if not found:
        raise RuntimeError("No CAPTURE markers; preserve the master and raw log.")
    for name, clip in found.items():
        if set(clip) != {"BEGIN", "END"} or clip["END"] <= clip["BEGIN"]:
            raise RuntimeError(f"Invalid boundaries: {name} {clip}")
    return found


def probe(path: Path) -> dict:
    return json.loads(subprocess.check_output(
        [executable("ffprobe"), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], text=True))


def verify_video(path: Path, folder: Path) -> dict:
    info = probe(path)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if video is None or audio is None:
        raise RuntimeError(f"Missing video or game audio stream: {path}")
    rate = video.get("avg_frame_rate", "0/1").split("/")
    fps = float(rate[0]) / max(float(rate[1]), 1.0)
    if (video["width"], video["height"]) != (1920, 1080) or abs(fps - 60.0) > 0.001:
        raise RuntimeError(f"Native 1080p60 required: {path}: {video}")
    verify = logged([executable("ffmpeg"), "-hide_banner", "-i", str(path),
                     "-map", "0:v:0", "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-"],
                    folder / f"{path.stem}_verify.log")
    if "mean_volume:" not in verify or "mean_volume: -inf" in verify:
        raise RuntimeError(f"Game audio is empty or silent: {path}")
    if re.search(r"Error while|Invalid data|corrupt|Decode error", verify, re.I):
        raise RuntimeError(f"Deliverable decoding failed: {path}")
    return {"width": video["width"], "height": video["height"], "fps": fps,
            "audio_codec": audio["codec_name"], "audio_channels": audio.get("channels"),
            "duration_seconds": float(info["format"]["duration"]), "fully_decoded": True}


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for part in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(part)
    return hasher.hexdigest()


def metadata(path: Path, track: str, ui: str, commit: str) -> dict:
    fixture = FIXTURES.get(track, "Existing _feel_numbers_demo plate A: stationary showcase enemies, prepared skills/paper, fixed combat RNG, deliberate damage/crit fixtures; current production VFX paths.")
    return {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path),
            "source_commit": commit, "track": track, "ui": ui, "publication": "public",
            "spoiler": SPOILERS.get(track, "none"), "status": "current_game_capture",
            "setup": fixture, "review": "Requires visual editorial selection before social posting."}


def record(args, game: Path, out: Path, track: str, ui: str, commit: str) -> dict:
    folder = out / f"{track}_ui_{ui}"
    folder.mkdir(parents=True, exist_ok=True)
    master = folder / "capture_master.avi"
    raw_log = folder / "capture_raw.log"
    command = [args.godot, "--path", str(game), "--windowed", "--resolution", "1920x1080",
               "--position", "0,0", "--fixed-fps", "60", "--disable-vsync",
               "--log-file", str(folder / "engine.log"), "--write-movie", str(master),
               "--", "--e2e=_marketing_capture", f"--marketing-track={track}", f"--marketing-ui={ui}", "--vfx-fixed-seed"]
    print(f"Recording {track}, UI {ui}, native 1080p60 + game audio", flush=True)
    raw = raw_log.read_text(encoding="utf-8", errors="replace") if args.encode_only else logged(command, raw_log)
    checked = re.sub(r"(?m)^ERROR: .*resources still in use at exit.*$", "", raw)
    if "E2E SUMMARY: 1/1 PASS" not in raw or re.search(r"SCRIPT ERROR|^ERROR:|Parse Error", checked, re.M):
        print(raw, flush=True)
        raise RuntimeError(f"Capture failed; raw footage kept: {raw_log}")
    native = probe(master)
    video = next(s for s in native["streams"] if s["codec_type"] == "video")
    if (video["width"], video["height"]) != (1920, 1080):
        raise RuntimeError(f"Movie Maker framebuffer was not native 1080p: {video}")
    clips = []
    for name, b in boundaries(raw).items():
        target = folder / f"{name}_ui_{ui}_current_public_{SPOILERS.get(track, 'nosp')}.mp4"
        seconds = (b["END"] - b["BEGIN"]) / 60.0
        logged([executable("ffmpeg"), "-hide_banner", "-y", "-i", str(master),
                "-ss", f"{max(0, b['BEGIN'] - 1) / 60.0:.6f}", "-t", f"{seconds:.6f}",
                "-map", "0:v:0", "-map", "0:a:0", "-c:v", "libx264", "-preset", "fast",
                "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(target)], folder / f"{name}_encode.log")
        entry = metadata(target, track, ui, commit)
        entry.update(verify_video(target, folder))
        entry["source_begin_frame"] = b["BEGIN"]
        entry["source_end_frame"] = b["END"]
        clips.append(entry)
        print(f"Verified {target.name}: {entry['duration_seconds']:.2f}s, audible audio", flush=True)
    manifest = {"source_commit": commit, "track": track, "ui": ui,
                "recorded_at_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(),
                "resolution": [1920, 1080], "fps": 60, "game_audio": True,
                "vfx_fixed_seed": "[Vfx] 녹화 모드" in raw, "command": command,
                "master_bytes": master.stat().st_size, "clips": clips,
                "limitation": "Deterministic promotional fixtures; not a realtime performance capture."}
    if not manifest["vfx_fixed_seed"]:
        raise RuntimeError("Requested VFX fixed seed mode did not activate; preserve recording.")
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not args.keep_master:
        master.unlink()
    return manifest


def screenshots(args, game: Path, out: Path, commit: str) -> dict:
    from PIL import Image
    folder = out / "screenshots_4k_no_ui"
    folder.mkdir(parents=True, exist_ok=True)
    command = [args.godot, "--path", str(game), "--windowed", "--resolution", "3840x2160",
               "--position", "0,0", "--disable-vsync", "--fixed-fps", "60",
               "--log-file", str(folder / "engine.log"), "--", "--e2e=_marketing_capture",
               "--marketing-track=screenshots", "--marketing-ui=off", "--e2e-shots", "--vfx-fixed-seed"]
    raw = logged(command, folder / "capture_raw.log")
    if "E2E SUMMARY: 1/1 PASS" not in raw or re.search(r"SCRIPT ERROR|Parse Error", raw):
        print(raw, flush=True)
        raise RuntimeError("Native 4K screenshot scenario failed.")
    entries = []
    for source in dict.fromkeys(re.findall(r"스크린샷 ([^\r\n]+\.png)", raw)):
        source_path = Path(source.strip())
        if not source_path.exists():
            raise RuntimeError(f"Screenshot log path does not exist: {source_path}")
        with Image.open(source_path) as image:
            if image.size != (3840, 2160):
                raise RuntimeError(f"Screenshot is not native 4K: {source_path}: {image.size}")
        label = re.sub(r"^_marketing_capture_\d+_", "", source_path.stem)
        spoiler = "gameplay" if "boss" in label or "imugi" in label else "nosp"
        target = folder / f"{label}_4k_no_ui_current_public_{spoiler}.png"
        shutil.copy2(source_path, target)
        entry = metadata(target, "screenshots", "off", commit)
        entry.update({"width": 3840, "height": 2160, "native_resolution": True, "spoiler": spoiler})
        entries.append(entry)
    if not 10 <= len(entries) <= 20:
        raise RuntimeError(f"Expected 10–20 native 4K screenshots, got {len(entries)}")
    manifest = {"source_commit": commit, "command": command, "screenshots": entries}
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(entries)} original 3840x2160 no-UI PNGs", flush=True)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", type=Path, required=True, help="Dedicated temporary marketing game worktree")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--godot", default=r"C:\Program Files (x86)\Steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe")
    parser.add_argument("--track", choices=TRACKS + ["all", "screenshots"], default="all")
    parser.add_argument("--ui", choices=["on", "off", "both"], default="both")
    parser.add_argument("--expected-commit", default="627061d8")
    parser.add_argument("--keep-master", action="store_true")
    parser.add_argument("--encode-only", action="store_true")
    args = parser.parse_args()
    game, out = args.game.resolve(), args.out.resolve()
    commit = source_commit(game)
    if not commit.startswith(args.expected_commit):
        raise RuntimeError(f"Game source {commit} does not match requested source {args.expected_commit}")
    if not (game / "tests/e2e/scenarios/_marketing_capture.gd").exists():
        raise RuntimeError("Install and register capture-only scripts in the transient game checkout first.")
    isolate_userdir(game)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    if args.track == "screenshots":
        records.append(screenshots(args, game, out, commit))
    else:
        for track in TRACKS if args.track == "all" else [args.track]:
            for ui in ["on", "off"] if args.ui == "both" else [args.ui]:
                records.append(record(args, game, out, track, ui, commit))
    summary = {"source_commit": commit, "results": records}
    (out / f"capture_{args.track}_{args.ui}_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MARKETING CAPTURE COMPLETE", flush=True)


if __name__ == "__main__":
    main()
