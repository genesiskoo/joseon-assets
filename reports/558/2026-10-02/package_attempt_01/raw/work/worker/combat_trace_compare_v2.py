"""#558 natural-clock first-divergence report. Never launches games or rerolls.

Give each test.ps1 tmp/e2e_raw/<run> directory to verify the actual phase
argv, raw ENV/FILE/ATTEMPT/TRIES and saved traces together. A trace directory
alone is supported, but its actual-attempt completeness is explicitly unchecked.
python tools/combat_trace_compare.py LEFT RIGHT --out comparison.json
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
DECIMAL = re.compile(r"(?:0|-?[1-9][0-9]*)\Z")
FLOAT17 = re.compile(r"-?[0-9]+\.[0-9]{17}\Z")
RAW_KEYS = {"busy_until", "raw_swing", "raw_generation", "raw_current_generation", "raw_mark_swing", "raw_token", "raw_current_token"}
TAGS = ("BALANCE_REPLAY_ENV", "BALANCE_TRACE_FILE", "BALANCE_REPLAY_ATTEMPT", "BALANCE_REPLAY_TRIES")
OUTCOME_FLOATS = {"sec", "phase2", "hp0", "hp", "hp_min", "max_hp", "boss_hp"}
OUTCOME_COUNTS = {"attacks", "hits", "guards", "summoned", "used", "input_polls"}
OUTCOME_FIELDS = OUTCOME_FLOATS | OUTCOME_COUNTS | {"win", "input_ticks_ok"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal(value, field):
    require(isinstance(value, str) and DECIMAL.fullmatch(value), field + " must be signed64 decimal text")
    require(-(2**63) <= int(value) <= 2**63 - 1, field + " outside signed64")
    return value


def battle_key(row):
    require(type(row.get("level")) is int and row["level"] in (3, 5), "wrong level")
    require(type(row.get("attempt")) is int and 1 <= row["attempt"] <= 3, "wrong attempt")
    return (row["level"], row["attempt"])


def validate_trace(document):
    require(document.get("schema") == 1, "unsupported trace schema")
    battle = document.get("battle", {})
    require(battle.get("scenario") == "balance_boss", "wrong trace scenario")
    key = battle_key(battle)
    decimal(battle.get("base_seed"), "base_seed")
    for field in ("raw_tick_origin", "raw_process_origin"):
        decimal(document.get(field), field)
    streams = document.get("streams", [])
    require(isinstance(streams, list) and 1 <= len(streams) <= 6, "actual stream count outside1..6")
    keys = []
    for stream in streams:
        require(stream.get("body") in BODY_KEYS, "unknown stream role/ordinal")
        keys.append(stream["body"])
        for field in ("seed", "initial", "final", "raw_actor_id", "raw_body_id", "raw_swing_origin"):
            decimal(stream.get(field), stream["body"] + "." + field)
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
        for field in ("raw_physics_frame", "raw_process_frame"):
            decimal(event.get(field), field)
        state = event.get("state", {})
        if "rng_state" in state:
            decimal(state["rng_state"], "rng_state")
        for field in ("attack_rng_state", "seed", "initial", "raw_mark_swing"):
            if field in event.get("fields", {}):
                decimal(event["fields"][field], field)
    return key


def _equals_options(args, prefix):
    return [a.split("=", 1)[1] for a in args if a.startswith(prefix + "=")]


def validate_launch(launch):
    argv = launch.get("argv", [])
    require(isinstance(argv, list) and all(isinstance(a, str) for a in argv) and argv.count("--") == 1, "actual argv/user separator missing")
    separator = argv.index("--")
    engine, user = argv[:separator], argv[separator + 1:]
    e2e = _equals_options(user, "--e2e")
    require(e2e == [launch.get("phase_arg")], "actual --e2e differs from phase_arg")
    tokens = [s.strip() for s in e2e[0].split(",") if s.strip()]
    require(tokens == launch.get("phase_tokens"), "phase token list differs from actual --e2e")
    skipped = _equals_options(user, "--e2e-skip")
    require(len(skipped) <= 1, "actual --e2e-skip duplicated")
    skip = [s.strip() for s in skipped[0].split(",") if s.strip()] if skipped else []
    require(skip == launch.get("skip"), "actual --e2e-skip differs from phase skip")
    fixed = []
    for index, arg in enumerate(engine):
        if arg == "--fixed-fps":
            require(index + 1 < len(engine), "actual --fixed-fps missing value")
            fixed.append(engine[index + 1])
        elif arg.startswith("--fixed-fps="):
            fixed.append(arg.split("=", 1)[1])
    require(len(fixed) <= 1 and (not fixed or fixed[0].isdigit()), "actual --fixed-fps invalid/duplicated")
    require(not any(a.startswith("--fixed-fps") for a in user), "engine FPS flag misplaced in user CLI")
    actual_fps = int(fixed[0]) if fixed else 0
    require(type(launch.get("fixed_fps")) is int and actual_fps == launch["fixed_fps"], "actual --fixed-fps differs from launch metadata")
    require(actual_fps == 0, "natural-clock comparison requires actual FixedFps0")
    actual = ("balance_boss" in tokens or "all" in tokens) and "balance_boss" not in skip
    require(actual is launch.get("contains_balance_boss"), "contains_balance_boss differs from actual phase tokens/skip")
    require(type(launch.get("launcher_pid")) is int and launch["launcher_pid"] > 0, "launcher PID missing")
    if not actual:
        return None
    require(launch.get("combat_trace") is True and user.count("--combat-trace") == 1, "actual phase tracing disabled/duplicated")
    destinations = _equals_options(user, "--combat-trace-dir")
    require(len(destinations) == 1 and Path(destinations[0]).is_absolute(), "actual trace destination missing/duplicated/nonabsolute")
    return {"user_cli": user, "directory": Path(destinations[0]).resolve()}


def read_raw_rows(raw):
    rows = {tag: [] for tag in TAGS}
    # Read raw bytes without rewriting them. SHA/byte checks use the original file.
    for line_number, line in enumerate(raw.read_bytes().decode("utf-8-sig", "strict").splitlines(), 1):
        for tag in TAGS:
            prefix = tag + " "
            stripped = line.strip()
            if stripped.startswith("· "):
                stripped = stripped[2:]
            if not stripped.startswith(prefix):
                continue
            try:
                row = json.loads(stripped[len(prefix):])
            except json.JSONDecodeError as exc:
                raise ValueError(f"{tag} invalid JSON at raw line {line_number}: {exc}") from exc
            require(isinstance(row, dict), tag + " must contain an object")
            rows[tag].append({"raw_line": line_number, "row": row})
    return rows


def validate_attempt(row):
    key = battle_key(row)
    require(set(row) == OUTCOME_FIELDS | {"level", "attempt", "potions"}, "ATTEMPT fields missing/unexpected")
    require(type(row["win"]) is bool and type(row["input_ticks_ok"]) is bool, "ATTEMPT result/input bool missing")
    require(type(row["potions"]) is int and row["potions"] > 0, "ATTEMPT potion budget missing")
    for field in OUTCOME_COUNTS:
        require(type(row[field]) is int and row[field] >= 0, "ATTEMPT count invalid: " + field)
    for field in OUTCOME_FLOATS:
        require(isinstance(row[field], str) and FLOAT17.fullmatch(row[field]), "ATTEMPT float17 text missing: " + field)
    return key


def verify_phase(meta, meta_path, actual):
    raw = meta_path.parent / "godot.raw.log"
    detail = meta.get("godot_log") or {}
    require(raw.is_file() and sha256(raw) == detail.get("sha256"), "phase raw missing or altered")
    require(raw.stat().st_size == detail.get("bytes"), "phase raw byte count differs from manifest")
    rows = read_raw_rows(raw)
    environments = rows["BALANCE_REPLAY_ENV"]
    require(len(environments) == 1, "exactly one actual balance ENV required")
    env = environments[0]["row"]
    engine_pid = meta.get("runtime_pid")
    require(type(engine_pid) is int and engine_pid > 0 and env.get("pid") == engine_pid, "raw ENV PID differs from phase runtime PID")
    require(env.get("scenario") == "balance_boss" and env.get("user_cli") == actual["user_cli"], "raw ENV user CLI differs from actual argv")
    directory = actual["directory"]
    files = sorted(directory.glob("trace_*.json"))
    manifests, documents, records = {}, {}, []
    for item in rows["BALANCE_TRACE_FILE"]:
        manifest = item["row"]
        key = battle_key(manifest)
        require(key not in manifests, "duplicate raw TRACE_FILE level/attempt")
        require(manifest.get("saved") is True and manifest.get("pid") == engine_pid, "raw TRACE_FILE unsaved or engine PID mismatch")
        file = Path(manifest.get("path", "")).resolve()
        expected = directory / f"trace_{engine_pid}_Lv{key[0]}_attempt{key[1]}.json"
        require(file == expected and file.is_file(), "raw TRACE_FILE path/file missing or differs from actual trace directory")
        document = json.loads(file.read_text(encoding="utf-8-sig"))
        require(validate_trace(document) == key and document.get("engine_pid") == engine_pid, "trace document differs from raw FILE level/attempt/PID")
        require(document.get("reason") == manifest.get("reason") and len(document["events"]) == manifest.get("events"), "trace reason/event count differs from raw FILE")
        require(document.get("overhead", {}).get("observe_usec") == manifest.get("observe_usec"), "trace overhead differs from raw FILE")
        decimal(manifest.get("observe_usec"), "FILE observe_usec")
        decimal(manifest.get("serialization_usec"), "FILE serialization_usec")
        manifests[key], documents[key] = item, document
        records.append({"file": str(file), "sha256": sha256(file), "level": key[0], "attempt": key[1], "reason": document["reason"]})
    require(set(files) == {Path(r["file"]) for r in records}, "trace files and raw FILE manifest differ; extra/unlisted attempts")
    attempts = {}
    for item in rows["BALANCE_REPLAY_ATTEMPT"]:
        row = item["row"]
        key = validate_attempt(row)
        require(key not in attempts and key in documents, "ATTEMPT duplicated or saved failed/retry trace missing")
        doc, manifest = documents[key], manifests[key]
        require(doc["reason"] == "finished" and manifest["raw_line"] < item["raw_line"], "ATTEMPT lacks preceding completed FILE")
        require(doc.get("outcome") == {k: v for k, v in row.items() if k not in {"level", "attempt", "potions"}}, "ATTEMPT exact outcome differs from trace")
        roles = {s["body"] for s in doc["streams"]}
        require({"doho0", "heukrang0", "guard_bat1", "guard_bat2"} <= roles, "completed attempt lacks actual four base bodies")
        require(row["guards"] == len(roles & {"guard_bat1", "guard_bat2"}) and row["summoned"] == len(roles & {"summon_bat1", "summon_bat2"}), "actual body counts differ from ATTEMPT")
        attempts[key] = item
    for key, doc in documents.items():
        if doc["reason"] == "finished":
            require(key in attempts, "completed trace lacks raw ATTEMPT")
        else:
            require(key not in attempts and doc.get("outcome") == {}, "aborted trace must preserve empty unfinished outcome")
    tries = {}
    for item in rows["BALANCE_REPLAY_TRIES"]:
        row = item["row"]
        level = row.get("level")
        require(type(level) is int and level in (3, 5) and level not in tries, "TRIES level missing/duplicated")
        values = row.get("tries")
        require(isinstance(values, list) and 1 <= len(values) <= 3 and all(v in ("처치", "패") for v in values), "TRIES actual outcomes invalid")
        keys = [(level, n) for n in range(1, len(values) + 1)]
        require({k for k in documents if k[0] == level} == set(keys), "TRIES and all saved level attempts differ")
        for key, value in zip(keys, values):
            require(key in attempts and attempts[key]["raw_line"] < item["raw_line"], "TRIES references missing/late ATTEMPT")
            require(value == ("처치" if attempts[key]["row"]["win"] else "패"), "TRIES win/loss differs from ATTEMPT")
        require(all(v == "패" for v in values[:-1]) and (values[-1] == "처치" or len(values) == 3), "TRIES violates original stop-on-win/three-attempt bound")
        tries[level] = item
    ordered_keys = [battle_key(item["row"]) for item in rows["BALANCE_TRACE_FILE"]]
    expected_keys = [(level, n) for level in (3, 5) for n in range(1, 1 + sum(k[0] == level for k in documents))]
    require(ordered_keys == expected_keys, "actual FILE attempts are not ordered original level/attempt prefixes")
    require(type(meta.get("timed_out")) is bool and type(meta.get("exit_code")) is int, "actual phase exit/timeout metadata missing")
    interrupted = meta["timed_out"] or meta["exit_code"] != 0
    if not interrupted:
        require(set(tries) == {3, 5}, "successful phase lacks both completed TRIES rows")
    proof = {"phase": str(meta_path), "phase_sha256": sha256(meta_path), "godot_sha256": sha256(raw),
             "exit_code": meta["exit_code"], "timed_out": meta["timed_out"], "runtime_pid": engine_pid,
             "launch": meta["launch"], "raw_rows": rows, "incomplete_levels": sorted({k[0] for k in documents} - set(tries)),
             "hard_kill_limit": "a killed process may lose its active in-memory trace; raw failure/timeout is preserved"}
    return documents, records, proof


def load_run(path):
    path = Path(path).resolve()
    phases = sorted(path.rglob("phase.json")) if path.is_dir() else []
    provenance, records, battles = [], [], {}
    if phases:
        for meta_path in phases:
            meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
            actual = validate_launch(meta["launch"])
            if actual is None:
                continue
            docs, files, proof = verify_phase(meta, meta_path, actual)
            require(not set(docs) & set(battles), "duplicated level/attempt; compare one declared run at a time")
            battles.update(docs)
            records.extend(files)
            provenance.append(proof)
        require(provenance, "no actual balance_boss phase")
    else:
        files = sorted(path.rglob("trace_*.json")) if path.is_dir() else [path]
        require(files, "no trace files")
        for file in files:
            document = json.loads(file.read_text(encoding="utf-8-sig"))
            key = validate_trace(document)
            require(key not in battles, "duplicated level/attempt; compare one declared run at a time")
            battles[key] = document
            records.append({"file": str(file), "sha256": sha256(file), "level": key[0], "attempt": key[1], "reason": document.get("reason")})
    return {"battles": battles, "files": records, "provenance": provenance,
            "provenance_status": "verified actual argv/ENV/FILE/ATTEMPT/TRIES and saved raw bytes" if provenance else "not supplied; trace-only analysis, attempt completeness unchecked"}


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
    return {"event_seq": e["event_seq"], "kind": e["kind"], "body": e["body"], "callsite": e["callsite"], "tick": e["tick"], "physics": e["physics"]}


def compare_battle(left, right):
    le, re_ = left["events"], right["events"]
    identity = lambda es: [(e["kind"], e["callsite"], e["body"], e["physics"]) for e in es]
    order = first_difference(identity(le), identity(re_))
    ticks = first_difference([e["tick"] for e in le], [e["tick"] for e in re_])
    epochs = first_difference([e["game_relative"] for e in le], [e["game_relative"] for e in re_])
    state = first_difference([relative_only({"state": e["state"], "fields": e["fields"]}) for e in le], [relative_only({"state": e["state"], "fields": e["fields"]}) for e in re_])
    rng = first_difference([{k: s[k] for k in ("body", "seed", "initial", "final")} for s in left["streams"]], [{k: s[k] for k in ("body", "seed", "initial", "final")} for s in right["streams"]])
    outcome_same = left.get("outcome") == right.get("outcome")
    differences = [d for d in (order, ticks, state) if d is not None]
    earliest = min(differences, key=lambda d: d["index"]) if differences else None
    return {"event_order": order, "relative_physics_ticks": ticks, "relative_game_float17": epochs,
            "state_or_payload": state, "rng_streams": rng, "not_spawned_same": left["not_spawned"] == right["not_spawned"],
            "outcome_exact_same": outcome_same, "left_outcome": left.get("outcome"), "right_outcome": right.get("outcome"),
            "left_event_count": len(le), "right_event_count": len(re_),
            "first_event_tick_state_left": event_context(le, earliest), "first_event_tick_state_right": event_context(re_, earliest),
            "first_clock_float_left": event_context(le, epochs), "first_clock_float_right": event_context(re_, epochs),
            "clock_float_only": epochs is not None and earliest is None and rng is None and outcome_same and left["not_spawned"] == right["not_spawned"],
            "left_overhead": left.get("overhead"), "right_overhead": right.get("overhead"),
            "causation": "not established; event/tick/state and float-only observations are reported separately"}


def compare_runs(left, right):
    battles = []
    for key in sorted(set(left["battles"]) | set(right["battles"])):
        a, b = left["battles"].get(key), right["battles"].get(key)
        row = {"level": key[0], "attempt": key[1]}
        if a is None or b is None:
            row.update({"missing_left": a is None, "missing_right": b is None, "existing_outcome": (a or b).get("outcome"), "existing_reason": (a or b).get("reason")})
        else:
            row.update(compare_battle(a, b))
        battles.append(row)
    return {"schema": 1, "comparison": "all raw-manifest attempts when provenance supplied; trace-only completeness unchecked; no fixed14 rows/tolerance normalization",
            "left_files": left["files"], "right_files": right["files"], "left_provenance": left["provenance"], "right_provenance": right["provenance"],
            "left_provenance_status": left["provenance_status"], "right_provenance_status": right["provenance_status"], "battles": battles,
            "parent_536_complete": False, "interpretation": "diagnostic report; no automatic reproduction or root-cause claim"}


def fixture(level=3, attempt=1, won=True):
    streams = []
    for i, body in enumerate(("doho0", "heukrang0", "guard_bat1", "guard_bat2")):
        streams.append({"body": body, "seed": str(20260916 + i), "initial": "9007199254740993", "final": "-9007199254740995",
                        "raw_actor_id": str(91 + i), "raw_body_id": str(90 + i), "raw_swing_origin": "101"})
    events = []
    for i, kind in enumerate(("battle_begin", "receive_attack_before", "receive_attack_after", "battle_end"), 1):
        events.append({"event_seq": i, "kind": kind, "body": "fixture" if i in (1, 4) else "doho0", "callsite": "unit." + kind,
                       "tick": i - 1, "process_frame": i, "physics": i in (2, 3), "game_relative": f"{(i - 1) / 60:.17f}",
                       "raw_physics_frame": str(100 + i), "raw_process_frame": str(200 + i), "raw_game_time": "77.00000000000000000",
                       "state": {} if i in (1, 4) else {"rng_state": streams[0]["final"] if i == 3 else streams[0]["initial"], "raw_swing": "101", "swing": 0}, "fields": {}})
    outcome = {"win": won, "input_ticks_ok": True, **{k: 1 for k in OUTCOME_COUNTS}, **{k: "1.00000000000000000" for k in OUTCOME_FLOATS}}
    outcome.update(guards=2, summoned=0)
    return {"schema": 1, "engine_pid": 991, "battle": {"scenario": "balance_boss", "base_seed": "20260916", "level": level, "attempt": attempt},
            "raw_epoch": "77.00000000000000000", "raw_tick_origin": "100", "raw_process_origin": "200", "streams": streams,
            "not_spawned": sorted(BODY_KEYS - {s["body"] for s in streams}), "events": events, "outcome": outcome, "reason": "finished",
            "overhead": {"observe_usec": "101", "wall_usec": "201", "event_count": len(events)}}


def write_synthetic_run(root, documents, exit_code=0, timed_out=False):
    phase = root / "phase_1_solo"
    phase.mkdir(parents=True)
    directory = root / "traces"
    directory.mkdir()
    argv = ["--path", str(root), "--headless", "--", "--e2e=balance_room,balance_boss", "--combat-trace", "--combat-trace-dir=" + str(directory)]
    launch = {"phase_arg": "balance_room,balance_boss", "phase_tokens": ["balance_room", "balance_boss"], "skip": [], "contains_balance_boss": True,
              "fixed_fps": 0, "combat_trace": True, "launcher_pid": 990, "argv": argv}
    env = {"scenario": "balance_boss", "pid": 991, "user_cli": argv[argv.index("--") + 1:]}
    raw_lines = ["Godot synthetic selftest fixture", "  · BALANCE_REPLAY_ENV " + json.dumps(env)]
    by_level = {}
    for doc in documents:
        key = doc["battle"]
        path = directory / f'trace_991_Lv{key["level"]}_attempt{key["attempt"]}.json'
        path.write_text(json.dumps(doc), encoding="utf-8")
        manifest = {"path": str(path), "saved": True, "pid": 991, "level": key["level"], "attempt": key["attempt"], "reason": doc["reason"],
                    "events": len(doc["events"]), "observe_usec": doc["overhead"]["observe_usec"], "serialization_usec": "77"}
        raw_lines.append("BALANCE_TRACE_FILE " + json.dumps(manifest))
        if doc["reason"] == "finished":
            row = {"level": key["level"], "attempt": key["attempt"], "potions": 3, **doc["outcome"]}
            raw_lines.append("  · BALANCE_REPLAY_ATTEMPT " + json.dumps(row))
            by_level.setdefault(key["level"], []).append("처치" if row["win"] else "패")
            if row["win"] or key["attempt"] == 3:
                raw_lines.append("  · BALANCE_REPLAY_TRIES " + json.dumps({"level": key["level"], "tries": by_level[key["level"]]}, ensure_ascii=False))
    raw = phase / "godot.raw.log"
    raw.write_bytes(("\r\n".join(raw_lines) + "\r\n").encode("utf-8"))
    meta = {"launch": launch, "runtime_pid": 991, "godot_log": {"sha256": sha256(raw), "bytes": raw.stat().st_size}, "exit_code": exit_code, "timed_out": timed_out}
    meta_path = phase / "phase.json"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    return meta_path, raw


def selftest():
    checks = 0
    def check(condition, message):
        nonlocal checks
        checks += 1
        require(condition, message)
    def rejects(fn, message):
        try:
            fn()
        except ValueError:
            check(True, message)
        else:
            check(False, message)
    a = fixture()
    validate_trace(a)
    check(a["streams"][0]["initial"] == "9007199254740993", "large int retained")
    check(a["streams"][0]["final"] == "-9007199254740995", "negative retained")
    b = copy.deepcopy(a)
    b["raw_epoch"] = "200.00000000000000000"
    for stream in b["streams"]:
        stream.update(raw_actor_id="401", raw_body_id="402", raw_swing_origin="501")
    for event in b["events"]:
        event.update(raw_physics_frame="500", raw_process_frame="700", raw_game_time="200.00000000000000000")
        if event["state"]:
            event["state"]["raw_swing"] = "501"
    report = compare_battle(a, b)
    check(report["event_order"] is None and report["state_or_payload"] is None and report["rng_streams"] is None, "absolute ids excluded only from comparisons")
    b["events"][1]["fields"]["reason"] = "cooldown"
    check(compare_battle(a, b)["state_or_payload"]["index"] == 1, "first payload boundary retained")
    b = copy.deepcopy(a)
    b["events"][2]["tick"] += 1
    check(compare_battle(a, b)["relative_physics_ticks"]["index"] == 2, "relative ticks judged separately")
    b = copy.deepcopy(a)
    b["events"][1]["game_relative"] = "0.01666666666666714"
    report = compare_battle(a, b)
    check(report["relative_game_float17"] is not None and report["relative_physics_ticks"] is None, "float epoch difference not erased")
    check(report["clock_float_only"] and report["first_event_tick_state_left"] is None and report["first_clock_float_left"]["event_seq"] == 2, "clock-only observation never claims first gameplay event")
    b["events"][2]["fields"]["reason"] = "busy"
    report = compare_battle(a, b)
    check(report["first_event_tick_state_left"]["event_seq"] == 3 and report["first_clock_float_left"]["event_seq"] == 2, "earlier clock float is separated from later state boundary")
    for mutate in (lambda d: d["streams"][0].update(final=9007199254740993), lambda d: d["streams"].append(copy.deepcopy(d["streams"][0])),
                   lambda d: d["events"][1].update(event_seq=9), lambda d: d.update(not_spawned=[]), lambda d: d["streams"][0].update(initial=str(2**63))):
        bad = copy.deepcopy(a)
        mutate(bad)
        rejects(lambda: validate_trace(bad), "invalid signed64/schema rejected")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        left_docs = [fixture(3, 1, False), fixture(3, 2, True), fixture(5, 1, True)]
        right_docs = [fixture(3, 1, True), fixture(5, 1, True)]
        lm, lr = write_synthetic_run(root / "left", left_docs, exit_code=1)
        rm, rr = write_synthetic_run(root / "right", right_docs)
        left, right = load_run(root / "left"), load_run(root / "right")
        out = compare_runs(left, right)
        check(len(out["battles"]) == 3 and out["battles"][1]["missing_right"], "all failed/retry rows retained")
        check(not out["battles"][0]["left_outcome"]["win"] and not out["battles"][0]["outcome_exact_same"], "failed result retained")
        check(left["provenance"][0]["exit_code"] == 1 and len(left["provenance"][0]["raw_rows"]["BALANCE_REPLAY_ATTEMPT"]) == 3, "failed actual phase retains every raw ATTEMPT")
        check(out["parent_536_complete"] is False and "verified" in out["left_provenance_status"], "actual raw manifest verified without parent completion")
        check("completeness unchecked" in load_run(root / "left" / "traces")["provenance_status"], "trace-only completeness not claimed")
        original_meta, original_raw = lm.read_bytes(), lr.read_bytes()
        def bad_meta(mutator):
            meta = json.loads(original_meta)
            mutator(meta)
            lm.write_text(json.dumps(meta), encoding="utf-8")
            try:
                load_run(root / "left")
            finally:
                lm.write_bytes(original_meta)
        for mutator in (lambda m: m["launch"].update(phase_arg="balance_boss"),
                        lambda m: m["launch"].update(skip=["balance_boss"]),
                        lambda m: m["launch"]["argv"].insert(3, "--fixed-fps=60"),
                        lambda m: m["launch"].update(fixed_fps=60),
                        lambda m: m.update(runtime_pid=992),
                        lambda m: m["launch"].update(launcher_pid=0),
                        lambda m: m["launch"]["argv"].remove("--"),
                        lambda m: m["launch"]["argv"].append("--e2e=balance_boss")):
            rejects(lambda mutator=mutator: bad_meta(mutator), "actual argv/metadata/PID mismatch rejected")
        def bad_raw(mutator):
            lines = original_raw.decode("utf-8").splitlines()
            revised = mutator(lines)
            lr.write_bytes(("\n".join(revised) + "\n").encode("utf-8"))
            meta = json.loads(original_meta)
            meta["godot_log"] = {"sha256": sha256(lr), "bytes": lr.stat().st_size}
            lm.write_text(json.dumps(meta), encoding="utf-8")
            try:
                load_run(root / "left")
            finally:
                lr.write_bytes(original_raw)
                lm.write_bytes(original_meta)
        def change_row(lines, tag, mutate):
            for i, line in enumerate(lines):
                if tag + " " in line:
                    prefix, payload = line.split(tag + " ", 1)
                    row = json.loads(payload)
                    mutate(row)
                    lines[i] = prefix + tag + " " + json.dumps(row, ensure_ascii=False)
                    break
            return lines
        for tag, mutator in (("BALANCE_REPLAY_ENV", lambda r: r.update(pid=992)),
                             ("BALANCE_REPLAY_ENV", lambda r: r["user_cli"].append("--e2e-shots")),
                             ("BALANCE_TRACE_FILE", lambda r: r.update(saved=False)),
                             ("BALANCE_TRACE_FILE", lambda r: r.update(path=str(root / "wrong.json"))),
                             ("BALANCE_TRACE_FILE", lambda r: r.update(events=99)),
                             ("BALANCE_REPLAY_ATTEMPT", lambda r: r.update(win=True)),
                             ("BALANCE_REPLAY_TRIES", lambda r: r.update(tries=["처치"]))):
            rejects(lambda tag=tag, mutator=mutator: bad_raw(lambda lines: change_row(lines, tag, mutator)), "raw ENV/FILE/ATTEMPT/TRIES mismatch rejected")
        for tag in ("BALANCE_REPLAY_ENV", "BALANCE_REPLAY_ATTEMPT", "BALANCE_REPLAY_TRIES"):
            # Right phase is successful, so missing any summary row cannot be explained as interruption.
            saved_rm, saved_rr = rm.read_bytes(), rr.read_bytes()
            rr.write_bytes(b"\n".join(line for line in saved_rr.splitlines() if tag.encode() not in line) + b"\n")
            meta = json.loads(saved_rm)
            meta["godot_log"].update(sha256=sha256(rr), bytes=rr.stat().st_size)
            rm.write_text(json.dumps(meta), encoding="utf-8")
            rejects(lambda: load_run(root / "right"), "missing raw summary row rejected")
            rm.write_bytes(saved_rm)
            rr.write_bytes(saved_rr)
        missing = root / "left" / "traces" / "trace_991_Lv3_attempt1.json"
        missing_bytes = missing.read_bytes()
        missing.unlink()
        rejects(lambda: load_run(root / "left"), "failed first trace missing despite raw proof is rejected")
        # Even symmetric missing files cannot silently turn into an equal comparison.
        other = root / "right" / "traces" / "trace_991_Lv3_attempt1.json"
        other_bytes = other.read_bytes()
        other.unlink()
        rejects(lambda: compare_runs(load_run(root / "left"), load_run(root / "right")), "missing corresponding files in both runs rejected")
        missing.write_bytes(missing_bytes)
        other.write_bytes(other_bytes)
        lr.write_bytes(b"altered")
        rejects(lambda: load_run(root / "left"), "raw byte tamper rejected")
        lr.write_bytes(original_raw)
        # Interrupted attempts have an explicit saved abort FILE, but no completed ATTEMPT/TRIES.
        abort = fixture(3, 2, False)
        abort.update(reason="runner_timeout", outcome={})
        write_synthetic_run(root / "abort", [fixture(3, 1, False), abort], exit_code=1)
        interrupted = load_run(root / "abort")
        check(len(interrupted["battles"]) == 2 and interrupted["battles"][(3, 2)]["reason"] == "runner_timeout", "saved interrupted attempt retained without inventing outcome")
        check(interrupted["provenance"][0]["incomplete_levels"] == [3], "incomplete level explicitly reported")
        all_lost = [fixture(level, attempt, False) for level in (3, 5) for attempt in (1, 2, 3)]
        write_synthetic_run(root / "lost", all_lost, exit_code=1)
        check(len(load_run(root / "lost")["battles"]) == 6, "all three failures on both levels retained")
    print(f"COMBAT_TRACE_COMPARE_TEST checks={checks} fails=0 PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", nargs="?")
    parser.add_argument("right", nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    require(args.left and args.right and args.out, "LEFT RIGHT --out required")
    require(not args.out.exists(), "output already exists; preserve previous report")
    report = compare_runs(load_run(args.left), load_run(args.right))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(args.out), "actual_attempt_rows": len(report["battles"]), "parent_536_complete": False}))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        print("COMBAT_TRACE_COMPARE FAIL: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
