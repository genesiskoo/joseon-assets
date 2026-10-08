from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/t2_sword_intake_context.json").read_text(encoding="utf-8"))
game,report = Path(ctx["game"]),Path(ctx["report"])
mode = sys.argv[1]
godot = "C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe"
env = dict(os.environ,GODOT_BIN=godot,PYTHONIOENCODING="utf-8")
scenarios = "icon_intake,item_ui,equipment_ui,ui_tooltips,ui_docks,ui_windows,hover_target,vendor_quest,vendor_prices,pickup_equip,loot_drop"
if mode == "import":
    command = [godot,"--headless","--path",str(game),"--import"]
elif mode in ["unit","e2e"]:
    command = ["powershell.exe","-NoProfile","-ExecutionPolicy","Bypass","-File",str(game / "tools/test.ps1"),"-Unit" if mode == "unit" else "-E2e"]
    if mode == "e2e":
        command += ["-Scenario",scenarios]
elif mode == "gate":
    command = [sys.executable,str(main / "tmp/t2_sword_intake_gate.py")]
elif mode == "land":
    command = [sys.executable,"tools/wt.py","land","--no-test","-m","승인 T2 검4 PNG/Texture2D경로 반입, 실제 양손·거래·줍기/전후3쌍·단위53/관련11/빠른검사 PASS"]
else:
    raise ValueError(mode)
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
started = time.time()
log = report / f"{ctx['card']}_{mode}_{time.strftime('%H%M%S')}.log"
with log.open("wb") as out:
    process = subprocess.Popen(command,cwd=game,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,startupinfo=startup)
    for raw in iter(process.stdout.readline,b""):
        out.write(raw)
        out.flush()
        print(raw.decode("utf-8-sig",errors="replace"),end="",flush=True)
    rc = process.wait()
meta = {"mode":mode,"command":command,"cwd":game.as_posix(),"started":started,"elapsed":time.time()-started,"exit_code":rc,"raw_log":log.name,"raw_sha256":hashlib.sha256(log.read_bytes()).hexdigest()}
(report / f"run_{mode}.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"RUN_END mode={mode} exit={rc} seconds={meta['elapsed']:.1f} raw={log}",flush=True)
sys.exit(rc)
