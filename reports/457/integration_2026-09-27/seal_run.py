from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/seal_intake_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
report = main / f"._tmp/assets_87/reports/{card}/integration_2026-09-27"
mode = sys.argv[1]
exe = "C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe"
env = dict(os.environ, GODOT_BIN=exe, PYTHONIOENCODING="utf-8")
if mode == "import":
    command = [exe, "--headless", "--path", str(game), "--import"]
elif mode == "unit":
    command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(game / "tools/test.ps1"), "-Unit"]
elif mode == "e2e":
    command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(game / "tools/test.ps1"), "-E2e", "-Scenario", "icon_intake,item_ui,ui_tooltips,ui_docks,ui_windows,hover_target,vendor_quest,pickup_equip,loot_drop,potion_tiers,quest_journal,boss_floor"]
elif mode == "gate":
    command = [sys.executable, str(main / "tmp/453_gate.py")]
elif mode == "land":
    command = [sys.executable, str(game / "tools/wt.py"), "land", "--no-test", "-m", "승인 봉인물3 PNG·ItemDef.icon 반입, 실제 입력·전후3쌍·관련 검사 PASS"]
else:
    raise ValueError(mode)
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
started = time.time()
path = report / f"{card}_{mode}_{time.strftime('%H%M%S')}.log"
with path.open("wb") as log:
    proc = subprocess.Popen(command, cwd=game, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=startup)
    for raw in iter(proc.stdout.readline, b""):
        log.write(raw)
        log.flush()
        print(raw.decode("utf-8-sig", errors="replace"), end="", flush=True)
    rc = proc.wait()
(report / f"run_{mode}.json").write_text(json.dumps({"mode":mode, "command":command, "cwd":str(game), "started":started, "elapsed":time.time()-started, "exit_code":rc, "raw_log":path.name, "raw_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"RUN_END #{card} mode={mode} exit={rc} seconds={time.time()-started:.1f} raw={path}", flush=True)
sys.exit(rc)
