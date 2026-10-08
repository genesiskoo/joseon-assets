"""#630 finalize immutable capture evidence after root completes tests and commits game code.

Read-only preparation: python finalize_report.py --dry-run
Final archive update: python finalize_report.py --game-commit <SHA>
Only assets reports/630_whirl_structure_v1 is written; runtime/game docs are read-only.
"""
from pathlib import Path
import argparse, hashlib, io, json, re, subprocess, sys, zipfile
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
REPORT = Path("C:/workspace/joseon-assets/reports/630_whirl_structure_v1")
LIMIT_FILE, LIMIT_CARD = 10_000_000, 50_000_000
WROTE_ARCHIVE = False
START, END = "<!-- FINAL_CHECKS630_BEGIN -->", "<!-- FINAL_CHECKS630_END -->"
WANTED_WINDOW = {"whirl_structure_v1", "skill_tiers", "aoe_skills_2", "skill_area", "vfx_cues", "pack_perf"}
RESULT = re.compile(r"^E2E (.+?) (PASS|FAIL) \(검사 (\d+)(?:, 실패 \d+)?\)$", re.M)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

def full_summary(text):
    unit = re.findall(r"^\s*PASS\s+(test_\S+\.gd)\s", text, re.M)
    settings = re.findall(r"^\s*PASS\s+settings restart (write|read)\s", text, re.M)
    tools = re.findall(r"^\s*PASS\s+(\S+ --selftest)\s", text, re.M)
    phase_totals = [tuple(map(int, match)) for match in re.findall(r"^E2E SUMMARY: (\d+)/(\d+) PASS\s*$", text, re.M)]
    aggregate = re.findall(r"^\s*e2e 합 (\d+)/(\d+) PASS", text, re.M)
    scenarios = {name: {"pass": verdict == "PASS", "checks": int(checks)} for name, verdict, checks in RESULT.findall(text)}
    complete = bool(re.search(r"^전부 PASS\s*$", text, re.M))
    return {"complete": complete, "unit_names": unit, "settings_phases": settings, "tool_names": tools,
            "tool_skips": re.findall(r"^\s*PASS\s+(\S+ --selftest).*\bSKIP\b", text, re.M),
            "e2e_phases": phase_totals, "e2e_aggregate": list(map(int, aggregate[-1])) if aggregate else None,
            "e2e_scenarios": scenarios}

def window_summary(logs):
    latest, runs = {}, []
    for path, text in sorted(logs, key=lambda item: (item[0].stat().st_mtime_ns, item[0].name)):
        if "창 모드" not in text:
            continue
        results = RESULT.findall(text)
        for name, verdict, checks in results:
            if name in WANTED_WINDOW:
                latest[name] = {"pass": verdict == "PASS", "checks": int(checks), "console": path.name}
        runs.append({"console": path.name, "complete_pass": bool(re.search(r"^전부 PASS\s*$", text, re.M)),
                     "summaries": [list(map(int, row)) for row in re.findall(r"^E2E SUMMARY: (\d+)/(\d+) PASS\s*$", text, re.M)]})
    return {"latest_per_scenario": latest, "passed": sum(row["pass"] for row in latest.values()), "total": len(latest), "runs": runs}

def phase_originals(logs):
    found = {}
    for console, text in logs:
        for raw in re.findall(r"^E2E_PHASE_RAW (.+?)\s*$", text, re.M):
            directory = Path(raw.strip()).resolve()
            allowed = (ROOT / "tmp/e2e_raw").resolve()
            if not directory.is_relative_to(allowed):
                raise ValueError("phase path is outside this worktree: " + str(directory))
            found.setdefault(directory, []).append(console.name)
    data, records = {}, []
    for directory, consoles in sorted(found.items(), key=lambda item: str(item[0])):
        original, metadata = directory / "godot.raw.log", directory / "phase.json"
        if not original.is_file() or not metadata.is_file():
            raise ValueError("incomplete phase archive: " + str(directory))
        raw, meta_bytes = original.read_bytes(), metadata.read_bytes()
        meta = json.loads(meta_bytes.decode("utf-8-sig"))
        detail = meta.get("godot_log") or {}
        if detail.get("bytes") != len(raw) or detail.get("sha256") != sha(raw):
            raise ValueError("phase original byte/hash mismatch: " + str(original))
        relative = directory.relative_to((ROOT / "tmp/e2e_raw").resolve()).as_posix()
        prefix = "logs/final_checks/phases/" + relative + "/"
        data[prefix + "godot.raw.log"] = raw
        data[prefix + "phase.json"] = meta_bytes
        records.append({"phase": relative, "consoles": consoles, "exit_code": meta["exit_code"],
                        "timed_out": meta["timed_out"], "elapsed_sec": meta["elapsed_sec"], "original_bytes": len(raw), "original_sha256": sha(raw),
                        "phase_json_bytes": len(meta_bytes), "phase_json_sha256": sha(meta_bytes)})
    return data, records

def make_zip(data):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for relative, raw in sorted(data.items()):
            item = zipfile.ZipInfo(relative.removeprefix("logs/final_checks/"), date_time=(2026, 10, 6, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(item, raw)
    zipped = buffer.getvalue()
    if len(zipped) >= LIMIT_FILE:
        raise ValueError("compressed phase bundle exceeds 10MB; split raw phases before finalizing")
    with zipfile.ZipFile(io.BytesIO(zipped)) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("phase ZIP integrity error")
        for relative, raw in data.items():
            if bundle.read(relative.removeprefix("logs/final_checks/")) != raw:
                raise ValueError("phase ZIP changed raw bytes")
    return zipped

def verify_runtime(commit):
    after = json.loads(read(BASE / "after_metadata.json"))
    mismatches = [name for name, value in after["source_hashes"].items() if sha((ROOT / name).read_bytes()) != value]
    if mismatches:
        raise ValueError("AFTER source differs from current runtime: " + ", ".join(mismatches))
    if "core/vfx_whirl.gd" not in after["source_hashes"]:
        raise ValueError("AFTER module SHA missing")
    if sha((BASE / "capture_whirl.gd").read_bytes()) != after["capture_script_sha256"]:
        raise ValueError("capture script changed since BEFORE/AFTER")
    actual_commit = None
    if commit:
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", commit):
            raise ValueError("--game-commit must be a hexadecimal Git SHA")
        actual_commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--verify", commit + "^{commit}"], text=True).strip()
        for name, value in after["source_hashes"].items():
            committed = subprocess.check_output(["git", "-C", str(ROOT), "show", actual_commit + ":" + name], stderr=subprocess.PIPE)
            if sha(committed) != value:
                raise ValueError("game commit differs from captured AFTER bytes: " + name)
    return after, actual_commit

def projected(existing, planned, removals):
    combined = {name: raw for name, raw in existing.items() if name not in removals and name != "archive_manifest.json"}
    combined.update(planned)
    manifest = encoded({"card": 630, "files": [{"file": name, "bytes": len(raw), "sha256": sha(raw)} for name, raw in sorted(combined.items())]})
    return combined, manifest, sum(map(len, combined.values())) + len(manifest)

def main(args):
    global WROTE_ARCHIVE
    if not REPORT.resolve().is_relative_to(Path("C:/workspace/joseon-assets/reports").resolve()):
        raise ValueError("archive path is outside reports")
    after, commit = verify_runtime(args.game_commit)
    logs = []
    for source in sorted(BASE.glob("*.raw.log")):
        if source.name.startswith(("test_", "e2e_structure_")):
            logs.append((source, read(source)))
    full_path = BASE / "test_all_final.raw.log"
    if not full_path.is_file():
        raise ValueError("test_all_final.raw.log is missing")
    summary = full_summary(read(full_path))
    window = window_summary(logs)
    blockers = []
    expected_units = {path.name for path in (ROOT / "tests").glob("test_*.gd")}
    expected_tools = set(re.findall(r'Invoke-Check "([^"\n]+ --selftest)"', read(ROOT / "tools/test.ps1")))
    if not summary["complete"]:
        blockers.append("full final suite has no completed 전부 PASS marker")
    if set(summary["unit_names"]) != expected_units or len(summary["unit_names"]) != len(expected_units):
        blockers.append("unit script result coverage differs from current tests/test_*.gd")
    if set(summary["settings_phases"]) != {"write", "read"}:
        blockers.append("settings write/read results missing")
    if set(summary["tool_names"]) != expected_tools or summary["tool_skips"]:
        blockers.append("tool selftest result coverage missing or SKIP present")
    e2e = summary["e2e_aggregate"]
    if not e2e or e2e[0] != e2e[1] or len(summary["e2e_scenarios"]) != e2e[1] or not all(row["pass"] for row in summary["e2e_scenarios"].values()):
        blockers.append("complete final E2E aggregate/individual PASS evidence missing")
    if window["total"] != len(WANTED_WINDOW) or window["passed"] != len(WANTED_WINDOW):
        blockers.append("latest windowed result for each of six scenarios is not PASS")
    if not commit:
        blockers.append("--game-commit has not been verified")
    phase_data, phases = phase_originals(logs)
    initial = BASE / "e2e_structure_01.raw.log"
    if not any(path == initial for path, _ in logs) or not any("e2e_structure_01.raw.log" in row["consoles"] and row["exit_code"] != 0 for row in phases):
        blockers.append("initial failing E2E console/byte-exact phase original missing")
    planned = {"logs/final_checks/console/" + path.name: path.read_bytes() for path, _ in logs}
    planned["reproduce/finalize_report.py"] = Path(__file__).read_bytes()
    record = {"card": 630, "game_commit": commit, "capture_source_hashes": after["source_hashes"], "runtime_hashes_match": True,
              "full_suite": summary, "windowed": window, "phase_originals": phases, "raw_phase_storage": "uncompressed", "complete": not blockers}
    planned.update(phase_data)
    existing = {path.relative_to(REPORT).as_posix(): path.read_bytes() for path in REPORT.rglob("*") if path.is_file()}
    readme = (REPORT / "README.md").read_text(encoding="utf-8")
    block = [START, "", f"게임 최종 commit: {commit or '(미확정 — dry-run)'}. AFTER 촬영 source SHA와 현재 runtime/해당 commit의 모든 원문이 일치한다.",
             f"종합 최종 결과: 단위 대본 {len(summary['unit_names'])}개, 설정 재시작 {len(summary['settings_phases'])}단계, 도구 셀프테스트 {len(summary['tool_names'])}개. " + (f"E2E {e2e[0]}/{e2e[1]} PASS." if e2e else "E2E 완료 집계 미확정."),
             f"창 모드 {window['passed']}/{window['total']}종의 마지막 개별 실측 PASS. 묶음 실패를 합격으로 바꾸지 않고, 후속 개별 재검증을 시나리오별 마지막 결과로 기록했다.",
             "원문 및 세부 실측은 logs/final_checks/final_checks.json과 console/에 보존한다. 최초 E2E 실패도 그 실행의 godot.raw.log·phase.json byte-exact 원문으로 함께 보존한다. console.merged.raw.log는 같은 원문이므로 추가하지 않는다. 기존 logs/의 진행 중 스냅샷과 구분하여 final_checks/를 최종 검증 근거로 쓴다.", "", END]
    if START in readme:
        if END not in readme:
            raise ValueError("README final-check block is malformed")
        readme = re.sub(re.escape(START) + r".*?" + re.escape(END), "\n".join(block), readme, flags=re.S)
    else:
        readme += "\n" + "\n".join(block) + "\n"
    planned["README.md"] = readme.encode("utf-8")
    planned["logs/final_checks/final_checks.json"] = encoded(record)
    removals = set()
    combined, archive_manifest, total = projected(existing, planned, removals)
    if args.zip_phases or total >= LIMIT_CARD:
        for name in phase_data:
            planned.pop(name)
        removals = {name for name in existing if name.startswith("logs/final_checks/phases/")}
        planned["logs/final_checks/phase_originals.zip"] = make_zip(phase_data)
        record["raw_phase_storage"] = "phase_originals.zip; extracted member byte/hash values recorded per phase"
        planned["logs/final_checks/final_checks.json"] = encoded(record)
        planned["README.md"] += "\n최종 phase 원문은50MB 카드 한도를 지키기 위해 phase_originals.zip에 보존했다. 추출 원문의 크기·SHA는 final_checks.json과 phase.json에 기록하며 ZIP 읽어오기에서 byte-exact 일치를 검증했다.\n".encode("utf-8")
        combined, archive_manifest, total = projected(existing, planned, removals)
    if total >= LIMIT_CARD or any(len(raw) >= LIMIT_FILE for raw in combined.values()):
        blockers.append("projected report exceeds 50MB card or 10MB file limit; no writes performed")
    overview = {"dry_run": args.dry_run, "ready": not blockers, "blockers": blockers, "game_commit": commit,
                "unit": len(summary["unit_names"]), "settings": len(summary["settings_phases"]), "tools": len(summary["tool_names"]),
                "e2e": e2e, "windowed_latest": [window["passed"], window["total"]], "console_logs": len(logs),
                "phase_archives": len(phases), "raw_phase_storage": record["raw_phase_storage"], "projected_total_bytes": total}
    if args.dry_run:
        print(json.dumps(overview, ensure_ascii=False))
        return 0
    if blockers:
        print(json.dumps(overview, ensure_ascii=False))
        return 2
    # All guards pass before mutation. Only this report's generated paths are replaced.
    WROTE_ARCHIVE = True
    for relative, raw in planned.items():
        target = (REPORT / relative).resolve()
        if not target.is_relative_to(REPORT.resolve()):
            raise ValueError("write target escaped report")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for relative in removals:
        (REPORT / relative).unlink()
    (REPORT / "archive_manifest.json").write_bytes(archive_manifest)
    check = json.loads(archive_manifest)
    for item in check["files"]:
        raw = (REPORT / item["file"]).read_bytes()
        if len(raw) != item["bytes"] or sha(raw) != item["sha256"]:
            raise ValueError("final archive hash verification failed: " + item["file"])
    actual_total = sum(path.stat().st_size for path in REPORT.rglob("*") if path.is_file())
    if actual_total != total or actual_total >= LIMIT_CARD:
        raise ValueError("final archive total changed during write; inspect concurrent modifications")
    overview.update({"archive_hash_entries": len(check["files"]), "archive_hash_failures": 0, "actual_total_bytes": actual_total})
    print(json.dumps(overview, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-commit", help="root's final game source commit SHA; required for archive writes")
    parser.add_argument("--dry-run", action="store_true", help="read-only plan; reports pending checks without writing archive")
    parser.add_argument("--zip-phases", action="store_true", help="force byte-exact phase ZIP; also selected automatically if total would exceed 50MB")
    options = parser.parse_args()
    try:
        raise SystemExit(main(options))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({"error": str(error), "archive_written": WROTE_ARCHIVE}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)