"""#716 피해 숫자 판정 영상 — 판 A·N716·N716L raw 로그(capture_raw.log) → events.json + 표.
NUMDEMO <clip> DMG <frame> <amount> <foe> <crit> <kill> · CAPTURE <clip> BEGIN|END <frame> · NUMDEMO INFO plate=… style=…
클립 프레임 n(0부터, 클립 mp4 기준) = 적은 프레임 − BEGIN + 1 (물리 단계에서 적힌 줄 — #698 README와 같은 맞춤).
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent
PLATES = ["A", "N716", "N716L"]
out = {}
for plate in PLATES:
    raw = (R / plate / "capture_raw.log").read_text(encoding="utf-8", errors="replace")
    info = re.search(r"NUMDEMO INFO plate=(\S+) style=(\S+)", raw)
    bounds = {}
    for name, edge, f in re.findall(r"CAPTURE (\S+) (BEGIN|END) (\d+)", raw):
        bounds.setdefault(name, {})[edge] = int(f)
    clips = {}
    for name, b in bounds.items():
        clips[name] = {"begin": b["BEGIN"], "end": b["END"], "frames": b["END"] - b["BEGIN"], "hits": []}
    for name, f, amt, foe, crit, kill in re.findall(r"NUMDEMO (\S+) DMG (\d+) (\d+) (-?\d+) (\d) (\d)", raw):
        c = clips[name]
        c["hits"].append({"n": int(f) - c["begin"] + 1, "amount": int(amt), "foe": int(foe), "crit": crit == "1", "kill": kill == "1"})
    out[plate] = {"plate": info.group(1) if info else None, "style": info.group(2) if info else None, "clips": clips}

# 같은 대본 = 같은 숫자·같은 프레임인가
ref = out["A"]["clips"]
for plate in PLATES[1:]:
    for name, c in out[plate]["clips"].items():
        a = ref[name]
        same = [(h["n"], h["amount"], h["foe"], h["crit"]) for h in c["hits"]] == [(h["n"], h["amount"], h["foe"], h["crit"]) for h in a["hits"]]
        print(f"{plate} {name}: frames {c['frames']} (A {a['frames']}) · hits {len(c['hits'])} · same as A = {same}")
(R / "events.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
for plate in PLATES:
    print(f"\n## {plate} (style = {out[plate]['style']})")
    for name, c in out[plate]["clips"].items():
        hs = " ".join(f"n{h['n']}:{h['amount']}{'*' if h['crit'] else ''}{'†' if h['kill'] else ''}@{h['foe']}" for h in c["hits"])
        print(f"{name} {c['frames']}f  {hs}")
