from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ctx = json.loads(Path("C:/workspace/joseon/tmp/t2_sword_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
game, root, report = [Path(ctx[k]) for k in ["game", "production", "report"]]
godot = "C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe"
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
results_file = report / "render_commands.json"
results = json.loads(results_file.read_text(encoding="utf-8")) if results_file.exists() else []
revision = next((arg.split("=", 1)[1] for arg in sys.argv[1:] if arg.startswith("--revision=")), "")
assert revision in ["", "r2"]
out_dir = root / "qa" / revision if revision else root / "qa"
out_dir.mkdir(parents=True, exist_ok=True)
for mode in [arg for arg in sys.argv[1:] if not arg.startswith("--revision=")] or ["after", "sizes"]:
    assert mode in ["before", "after", "sizes"]
    capture = out_dir / f"godot_{mode}.png"
    assert not capture.exists(), "Preserve the original capture instead of silently repeating it"
    command = [godot, "--path", str(game), "--windowed", "--resolution", "1280x720", "-s", str(root / "qa_godot.gd"), "--", "--root="+str(root), "--mode="+mode, "--out="+str(out_dir)]
    started = time.time()
    process = subprocess.Popen(command, cwd=game, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=startup)
    try:
        raw, _ = process.communicate(timeout=45)
    except subprocess.TimeoutExpired:
        process.kill()
        raw, _ = process.communicate()
        (report / f"{card}_godot_{mode}_timeout.log").write_bytes(raw)
        print(raw.decode("utf-8", errors="replace"))
        raise
    (report / f"{card}_godot_{mode}{'_' + revision if revision else ''}.log").write_bytes(raw)
    body = raw.decode("utf-8", errors="replace")
    print(body, end="")
    assert process.returncode == 0 and f"GODOT_D1_{card} PASS" in body
    assert "ERROR:" not in body and "SCRIPT ERROR" not in body
    assert capture.exists() and capture.stat().st_mtime >= started - 2
    results.append({"mode":mode, "revision":revision, "command":command, "returncode":process.returncode, "started_epoch":started, "seconds":round(time.time()-started,3), "raw_sha256":hashlib.sha256(raw).hexdigest(), "capture_sha256":hashlib.sha256(capture.read_bytes()).hexdigest()})
    results_file.write_text(json.dumps(results, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(f"PASS #{card} actual shared UiSkin modes: {[r['mode'] for r in results]}")
