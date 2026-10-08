from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])

write('tools/combat_trace_compare.py', '''"""#558 natural-clock first-divergence report. Does not launch games or reroll attempts.

Pass each test.ps1 tmp/e2e_raw/<run> directory to check actual phase provenance,
or a trace directory for trace-only analysis (provenance explicitly unchecked).
python tools/combat_trace_compare.py LEFT RIGHT --out comparison.json
Failed/extra attempts are retained. No fixed row counts or widened tolerances.
"""
import argparse
import copy
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

BODY_KEYS = {"doho0", "heukrang0", "guard_bat1", "guard_bat2", "summon_bat1", "summon_bat2"}
DECIMAL = re.compile(r"(?:0|-?[1-9][0-9]*)\\Z")
RAW_KEYS = {"busy_until", "raw_swing", "raw_generation", "raw_current_generation", "raw_mark_swing", "raw_token", "raw_current_token"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal(value, field):
    require(isinstance(value, str) and DECIMAL.fullmatch(value), field + " must be signed64 decimal text")
    require(-(2**63) <= int(value) <= 2**63 - 1, field + " outside signed64")
    return value


def validate_trace(document):
    require(document.get("schema") == 1, "unsupported trace schema")
    battle = document.get("battle", {})
    require(battle.get("scenario") == "balance_boss", "wrong trace scenario")
    require(battle.get("level") in (3, 5), "wrong level")
    require(type(battle.get("attempt")) is int and 1 <= battle["attempt"] <= 3, "wrong attempt")
    decimal(battle.get("base_seed"), "base_seed")
    for key in ("raw_tick_origin", "raw_process_origin"):
        decimal(document.get(key), key)
    streams = document.get("streams", [])
    require(isinstance(streams, list) and 1 <= len(streams) <= 6, "actual stream count outside1..6")
    keys = []
    for stream in streams:
        require(stream.get("body") in BODY_KEYS, "unknown stream role/ordinal")
        keys.append(stream["body"])
        for key in ("seed", "initial", "final", "raw_actor_id", "raw_body_id", "raw_swing_origin"):
            decimal(stream.get(key), stream["body"] + "." + key)
    require(len(set(keys)) == len(keys), "duplicated stream")
    require(set(document.get("not_spawned", [])) == BODY_KEYS - set(keys), "not_spawned does not describe missing actual bodies")
    events = document.get("events", [])
    require(events and events[0].get("kind") == "battle_begin" and events[-1].get("kind") == "battle_end", "missing begin/end")
    last_tick = -1
    for index, event in enumerate(events, 1):
        require(event.get("event_seq") == index, "event_seq gap/duplicate")
        require(type(event.get("tick")) is int and event["tick"] >= last_tick, "relative physical ticks must be ordered")
        last_tick = event["tick"]
        require(type(event.get("physics")) is bool, "actual physics marker missing")
        require(event.get("body") in BODY_KEYS | {"fixture"} and event.get("callsite"), "invalid event identity")
        for key in ("raw_physics_frame", "raw_process_frame"):
            decimal(event.get(key), key)
        state = event.get("state", {})
        if "rng_state" in state:
            decimal(state["rng_state"], "rng_state")
        fields = event.get("fields", {})
        for key in ("attack_rng_state", "seed", "initial", "raw_mark_swing"):
            if key in fields:
                decimal(fields[key], key)
    return (battle["level"], battle["attempt"])


def _phase_has_balance(launch):
    tokens = [s.strip() for s in launch["phase_arg"].split(",") if s.strip()]
    require(tokens == launch["phase_tokens"], "phase token list mismatches actual phase_arg")
    actual = "balance_boss" in tokens or ("all" in tokens and "balance_boss" not in launch["skip"])
    require(actual == launch["contains_balance_boss"], "contains_balance_boss mismatches actual tokens/skip")
    return actual


def load_run(path):
    path = Path(path).resolve()
    phases = sorted(path.rglob("phase.json")) if path.is_dir() else []
    provenance = []
    files = []
    if phases:
        for meta_path in phases:
            meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
            launch = meta["launch"]
            if not _phase_has_balance(launch):
                continue
            require(launch["fixed_fps"] == 0, "natural-clock comparison requires FixedFps0")
            require(launch["combat_trace"] is True and "--combat-trace" in launch["argv"], "phase tracing disabled")
            require(type(meta["runtime_pid"]) is int and meta["runtime_pid"] > 0, "actual engine PID missing")
            require(type(launch["launcher_pid"]) is int and launch["launcher_pid"] > 0, "launcher PID missing")
            args = [a for a in launch["argv"] if a.startswith("--combat-trace-dir=")]
            require(len(args) == 1, "actual trace destination missing/duplicated")
            raw = meta_path.parent / "godot.raw.log"
            require(raw.is_file() and sha256(raw) == meta["godot_log"]["sha256"], "phase raw missing or altered")
            phase_files = sorted(Path(args[0].split("=", 1)[1]).glob("trace_*.json"))
            require(phase_files, "balance phase has no trace files")
            files += [(f, meta["runtime_pid"]) for f in phase_files]
            provenance.append({"phase": str(meta_path), "phase_sha256": sha256(meta_path), "godot_sha256": sha256(raw),
                               "exit_code": meta["exit_code"], "timed_out": meta["timed_out"], "runtime_pid": meta["runtime_pid"],
                               "launch": launch})
        require(provenance, "no actual balance_boss phase")
    else:
        files = [(f, None) for f in sorted(path.rglob("trace_*.json"))] if path.is_dir() else [(path, None)]
    require(files, "no trace files")
    battles = {}
    records = []
    for file, engine_pid in files:
        document = json.loads(file.read_text(encoding="utf-8-sig"))
        key = validate_trace(document)
        if engine_pid is not None:
            require(document.get("engine_pid") == engine_pid, "trace engine PID differs from actual phase ENV")
        require(key not in battles, "duplicated level/attempt; compare one declared run at a time")
        battles[key] = document
        records.append({"file": str(file), "sha256": sha256(file), "level": key[0], "attempt": key[1], "reason": document.get("reason")})
    return {"battles": battles, "files": records, "provenance": provenance,
            "provenance_status": "verified actual phase argv/PIDs/raw bytes" if provenance else "not supplied; trace-only analysis"}


def relative_only(value):
    if isinstance(value, dict):
        return {k: relative_only(v) for k, v in value.items() if not k.startswith("raw_") and k not in RAW_KEYS}
    if isinstance(value, list):
        return [relative_only(v) for v in value]
    return value


def first_difference(left, right):
    for index in range(max(len(left), len(right))):
        a = left[index] if index < len(left) else {"missing": True}
        b = right[index] if index < len(right) else {"missing": True}
        if a != b:
            return {"index": index, "left": a, "right": b}
    return None


def event_context(events, difference):
    if difference is None:
        return None
    index = difference["index"]
    if index >= len(events):
        return {"index": index, "missing": True}
    e = events[index]
    return {"event_seq": e["event_seq"], "kind": e["kind"], "body": e["body"], "callsite": e["callsite"],
            "tick": e["tick"], "physics": e["physics"]}


def compare_battle(left, right):
    le, re_ = left["events"], right["events"]
    identity = lambda es: [(e["kind"], e["callsite"], e["body"], e["physics"]) for e in es]
    order = first_difference(identity(le), identity(re_))
    ticks = first_difference([e["tick"] for e in le], [e["tick"] for e in re_])
    epochs = first_difference([e["game_relative"] for e in le], [e["game_relative"] for e in re_])
    state = first_difference([relative_only({"state": e["state"], "fields": e["fields"]}) for e in le],
                             [relative_only({"state": e["state"], "fields": e["fields"]}) for e in re_])
    rng = first_difference([{k: s[k] for k in ("body", "seed", "initial", "final")} for s in left["streams"]],
                           [{k: s[k] for k in ("body", "seed", "initial", "final")} for s in right["streams"]])
    outcome_same = left.get("outcome") == right.get("outcome")
    differences = [d for d in (order, ticks, epochs, state) if d is not None]
    earliest = min(differences, key=lambda d: d["index"]) if differences else None
    return {"event_order": order, "relative_physics_ticks": ticks, "relative_game_float17": epochs,
            "state_or_payload": state, "rng_streams": rng, "not_spawned_same": left["not_spawned"] == right["not_spawned"],
            "outcome_exact_same": outcome_same, "left_outcome": left.get("outcome"), "right_outcome": right.get("outcome"),
            "left_event_count": len(le), "right_event_count": len(re_),
            "first_observed_left": event_context(le, earliest), "first_observed_right": event_context(re_, earliest),
            "left_overhead": left.get("overhead"), "right_overhead": right.get("overhead"),
            "causation": "not established by first difference; positions/draw counts/epoch floats alone are observations"}


def compare_runs(left, right):
    battles = []
    for key in sorted(set(left["battles"]) | set(right["battles"])):
        a, b = left["battles"].get(key), right["battles"].get(key)
        row = {"level": key[0], "attempt": key[1]}
        if a is None or b is None:
            row.update({"missing_left": a is None, "missing_right": b is None,
                        "existing_outcome": (a or b).get("outcome"), "existing_reason": (a or b).get("reason")})
        else:
            row.update(compare_battle(a, b))
        battles.append(row)
    return {"schema": 1, "comparison": "all actual attempts; no fixed14 rows or tolerance normalization",
            "left_files": left["files"], "right_files": right["files"], "left_provenance": left["provenance"],
            "right_provenance": right["provenance"], "left_provenance_status": left["provenance_status"],
            "right_provenance_status": right["provenance_status"], "battles": battles,
            "parent_536_complete": False, "interpretation": "diagnostic report; no automatic reproduction or root-cause claim"}


def fixture(level=3, attempt=1, won=True):
    stream = {"body": "doho0", "seed": "20260916", "initial": "9007199254740993", "final": "-9007199254740995",
              "raw_actor_id": "91", "raw_body_id": "90", "raw_swing_origin": "101"}
    events = []
    for i, kind in enumerate(("battle_begin", "receive_attack_before", "receive_attack_after", "battle_end"), 1):
        events.append({"event_seq": i, "kind": kind, "body": "fixture" if i in (1,4) else "doho0", "callsite": "unit."+kind,
                       "tick": i-1, "process_frame": i, "physics": i in (2,3), "game_relative": f"{(i-1)/60:.17f}",
                       "raw_physics_frame": str(100+i), "raw_process_frame": str(200+i), "raw_game_time": "77.00000000000000000",
                       "state": {} if i in (1,4) else {"rng_state": stream["final"] if i==3 else stream["initial"], "raw_swing": "101", "swing":0}, "fields": {}})
    return {"schema":1, "engine_pid":991, "battle":{"scenario":"balance_boss","base_seed":"20260916","level":level,"attempt":attempt},
            "raw_epoch":"77.00000000000000000","raw_tick_origin":"100","raw_process_origin":"200","streams":[stream],
            "not_spawned":sorted(BODY_KEYS-{"doho0"}),"events":events,"outcome":{"win":won},"reason":"finished"}


def selftest():
    checks=0
    def check(cond, message):
        nonlocal checks
        checks += 1
        require(cond, message)
    a=fixture()
    validate_trace(a)
    check(a["streams"][0]["initial"] == "9007199254740993", "large int retained")
    check(a["streams"][0]["final"] == "-9007199254740995", "negative retained")
    b=copy.deepcopy(a)
    b["raw_epoch"]="200.00000000000000000"
    b["streams"][0].update(raw_actor_id="401",raw_body_id="402",raw_swing_origin="501")
    for e in b["events"]:
        e["raw_physics_frame"]="500"
        e["raw_process_frame"]="700"
        e["raw_game_time"]="200.00000000000000000"
        if e["state"]: e["state"]["raw_swing"]="501"
    report=compare_battle(a,b)
    check(report["event_order"] is None and report["state_or_payload"] is None and report["rng_streams"] is None, "absolute ids excluded only from comparisons")
    b["events"][1]["fields"]["reason"]="cooldown"
    check(compare_battle(a,b)["state_or_payload"]["index"]==1, "first payload boundary retained")
    b=copy.deepcopy(a);b["events"][2]["tick"]+=1
    check(compare_battle(a,b)["relative_physics_ticks"]["index"]==2, "relative ticks judged separately")
    b=copy.deepcopy(a);b["events"][1]["game_relative"]="0.01666666666666714"
    r=compare_battle(a,b)
    check(r["relative_game_float17"] is not None and r["relative_physics_ticks"] is None, "float epoch difference not erased or conflated")
    for mutate in [lambda d: d["streams"][0].update(final=9007199254740993), lambda d: d["streams"].append(copy.deepcopy(d["streams"][0])),
                   lambda d: d["events"][1].update(event_seq=9), lambda d: d.update(not_spawned=[]),
                   lambda d: d["streams"][0].update(initial=str(2**63))]:
        bad=copy.deepcopy(a); mutate(bad)
        try: validate_trace(bad)
        except ValueError: check(True,"invalid rejected")
        else: check(False,"invalid trace accepted")
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);lp=root/"left";rp=root/"right";lp.mkdir();rp.mkdir()
        for directory,docs in [(lp,[fixture(3,1,False),fixture(3,2,True),fixture(5,1,True)]), (rp,[fixture(3,1,True),fixture(5,1,True)])]:
            for d in docs:
                key=d["battle"]
                (directory/f'trace_991_Lv{key["level"]}_attempt{key["attempt"]}.json').write_text(json.dumps(d),encoding="utf-8")
        l,r=load_run(lp),load_run(rp);out=compare_runs(l,r)
        check(len(out["battles"])==3 and out["battles"][1]["missing_right"],"natural failed and extra attempts retained")
        check(out["battles"][0]["left_outcome"]["win"] is False and not out["battles"][0]["outcome_exact_same"], "failed outcome preserved")
        check(out["parent_536_complete"] is False and "not supplied" in out["left_provenance_status"],"no completion/provenance overclaim")
        phase=root/"run"/"phase_1_solo";phase.mkdir(parents=True)
        raw=phase/"godot.raw.log";raw.write_bytes(bytes(range(256)))
        launch={"phase_arg":"balance_room,balance_boss", "phase_tokens":["balance_room","balance_boss"],"skip":[],"contains_balance_boss":True,
                "fixed_fps":0,"combat_trace":True,"launcher_pid":990,"argv":["--combat-trace", "--combat-trace-dir="+str(lp)]}
        meta={"launch":launch,"runtime_pid":991,"godot_log":{"sha256":sha256(raw)},"exit_code":1,"timed_out":False}
        (phase/"phase.json").write_text(json.dumps(meta),encoding="utf-8")
        verified=load_run(root/"run")
        check(len(verified["battles"])==3 and verified["provenance"][0]["exit_code"]==1,"failed phase actual argv/PID/raw verified")
        raw.write_bytes(b"altered")
        try: load_run(root/"run")
        except ValueError: check(True,"raw tamper rejected")
        else: check(False,"raw tamper accepted")
    print(f"COMBAT_TRACE_COMPARE_TEST checks={checks} fails=0 PASS")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left",nargs="?");parser.add_argument("right",nargs="?")
    parser.add_argument("--out",type=Path);parser.add_argument("--selftest",action="store_true")
    args=parser.parse_args()
    if args.selftest:
        selftest();return 0
    require(args.left and args.right and args.out,"LEFT RIGHT --out required")
    require(not args.out.exists(),"output already exists; preserve previous report")
    report=compare_runs(load_run(args.left),load_run(args.right))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print(json.dumps({"report":str(args.out),"actual_attempt_rows":len(report["battles"]),"parent_536_complete":False}))
    return 0


if __name__=="__main__":
    if hasattr(sys.stdout,"reconfigure"): sys.stdout.reconfigure(encoding="utf-8",errors="replace")
    try: raise SystemExit(main())
    except ValueError as exc:
        print("COMBAT_TRACE_COMPARE FAIL: "+str(exc),file=sys.stderr);raise SystemExit(1)
''')
edit('core/combat_trace.gd', lambda s: replace(s, 'return {"schema": 1, "battle":', 'return {"schema": 1, "engine_pid": OS.get_process_id(), "battle":'))
print('COMPARE558 source written')
