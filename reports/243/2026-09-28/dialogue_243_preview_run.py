from pathlib import Path
import json, os, subprocess, sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
root=Path("C:/workspace/joseon")
ctx=json.loads((root/"tmp/dialogue_243_context.json").read_text(encoding="utf-8"))
report=Path(ctx["report"])
script=report/"dialogue_243_preview.gd"
shutil.copyfile(root/"tmp/dialogue_243_preview.gd",script)
command=["C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe","--path",ctx["game"],"--script",str(script),"--windowed","--resolution","1280x720","--position","0,0"]
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
with (report/"preview.raw.log").open("wb") as log:
    proc=subprocess.Popen(command,cwd=ctx["game"],stdout=log,stderr=subprocess.STDOUT,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
    try: code=proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.terminate();proc.wait(timeout=10);code=124
raw=(report/"preview.raw.log").read_text(encoding="utf-8-sig",errors="replace")
print(raw,end="",flush=True)
assert code==0,code
assert "ART243_PREVIEW_PASS" in raw
assert "SCRIPT ERROR" not in raw and "ERROR:" not in raw
shots=json.loads((report/"preview_capture.json").read_text(encoding="utf-8"))
assert len(shots["snapshots"])==5
print("PASS #243 transient dialogue art preview; captures5; existing game files unchanged")
