from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
assets_main = Path("C:/workspace/joseon-assets")
ctx_path = main / "tmp/quest_guard_context.json"
ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
card = ctx["card"]
report = assets / f"reports/{card}/integration_2026-09-27"
env = dict(os.environ, PYTHONIOENCODING="utf-8", GODOT_BIN="C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe")

def run(tree, args):
    p = subprocess.run(args, cwd=tree, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode:
        print(p.stdout.decode("utf-8-sig", errors="replace"), end="", flush=True)
        raise SystemExit(p.returncode)
    return p.stdout

head = lambda tree:run(tree, ["git", "rev-parse", "HEAD"]).decode().strip()
assert head(main) == head(game)
ctx["game_landed"] = head(main)
assert run(main, ["git", "diff", "--name-only", ctx["game_commit"], "HEAD"]).decode().splitlines() == ["docs/STATE.md"]
meta = json.loads((report / "run_land.json").read_text(encoding="utf-8"))
body = (report / meta["raw_log"]).read_text(encoding="utf-8-sig")
assert meta["exit_code"] == 0 and "✅ 착륙" in body and "임포트 필요 없음" in body
gate_path = report / "run_main_gate.json"
if gate_path.exists():
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    raw = (report / gate["raw_log"]).read_bytes()
    assert gate["exit_code"] == 0 and hashlib.sha256(raw).hexdigest() == gate["raw_sha256"]
    assert b"SCRIPT ERROR 0" in raw and "러너 자기검사 PASS 5/5" in raw.decode("utf-8-sig")
    print("Previously completed main boot/runner remains valid; no code change since gate.", flush=True)
else:
    started = time.time()
    command = [sys.executable, str(main / "tmp/quest_guard_main_gate.py")]
    p = subprocess.run(command, cwd=main, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    path = report / f"{card}_main_gate_{time.strftime('%H%M%S')}.log"
    path.write_bytes(p.stdout)
    print(p.stdout.decode("utf-8-sig", errors="replace"), end="", flush=True)
    assert p.returncode == 0 and b"SCRIPT ERROR 0" in p.stdout and "러너 자기검사 PASS 5/5" in p.stdout.decode("utf-8-sig")
    gate = {"command":command, "exit_code":p.returncode, "started":started, "elapsed":time.time()-started, "raw_log":path.name, "raw_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    gate_path.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
eol_only = []
for name, digest in json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))["files"].items():
    raw = (main / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        assert name.endswith(".tres") and hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() == digest, name
        assert run(main, ["git", "show", f"HEAD:{name}"]) == raw.replace(b"\r\n", b"\n"), name
        eol_only.append(name)
assert eol_only == ["data/items/coin.tres", "data/items/ident_scroll.tres", "data/items/town_portal.tres"]
p = report / "verification.json"
data = json.loads(p.read_text(encoding="utf-8"))
data["main_landed"] = True
data["landing"] = {"approval":"PD 2026-09-27 승인 다음작업", "game_main":ctx["game_landed"], "candidate":ctx["game_commit"], "same_runtime_after_doc_only_rebase":True, "protected_main_exact_sha":102, "protected_main_crlf_only":eol_only, "protected_main_canonical_content_equal":105, "import_required":False, "reason":"modified existing scripts only; no new imported assets/classes", "run":meta, "main_gate":gate, "pushed":False}
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(report / "ACCEPTANCE.md").write_text(f"# #{card} 채택·착륙\n\nPD 2026-09-27 「승인 다음작업」으로 후보 game{ctx['game_commit']}·검수{ctx['assets_commit']} 승인. STATE 기록만 rebase 후 game {ctx['game_landed']} 착륙, 제품 코드 동일·정의/PNG105 Git 내용 동일. 본진 실제파일102 SHA 동일, 기존3정의(coin/ident_scroll/town_portal)는 CRLF 차이만 있어 LF 정규화 및 Git blob 일치를 확인했으며 직접 고치지 않았다. 단위53/관련E2E12·732/창70·76 PASS. 기존 스크립트만 수정해 착륙 도구는 임포트 필요 없음을 판정했다. 별도 본진 빠른 검사에서 부팅SCRIPT ERROR0·오토로드10/10·주 장면OK·러너5/5를 확인했다. 원시 도구 stdout은 run_land/run_main_gate 기록으로 보존한다. 미push. 후보 QA의 미병합 표기는 제작 시점 기록이며 이 문서가 최종 채택 결과다.\n", encoding="utf-8")
for name in ["quest_guard_main_gate.py", "quest_guard_land_finish.py", "quest_guard_land.py"]:
    (report / name).write_bytes((main / "tmp" / name).read_bytes())
run(assets, ["git", "add", "--", f"reports/{card}"])
run(assets, ["git", "diff", "--cached", "--check", "--", ".", f":(exclude)reports/{card}/**/*.log"])
print(run(assets, ["git", "commit", "-m", f"test(#{card}): PD 채택·본진 부팅과 코드/자산 보존 기록"]).decode("utf-8"), end="", flush=True)
print(run(assets, ["git", "rebase", "main"]).decode("utf-8"), end="", flush=True)
ctx["assets_landed"] = head(assets)
print(run(assets_main, ["git", "merge", "--ff-only", ctx["assets_landed"]]).decode("utf-8"), end="", flush=True)
assert not run(main, ["git", "status", "--porcelain"]).strip()
state = main / "docs/STATE.md"
body = state.read_text(encoding="utf-8")
old = next(line for line in body.splitlines() if line.startswith(f"- 2026-09-27 Codex: #{card} 퀘스트"))
new = f"- 2026-09-27 Codex: #{card} 퀘스트 커서 버림·툴팁 정합성 승인 착륙 game{ctx['game_landed'][:8]}/assets{ctx['assets_landed'][:8]}. 단위53(item_ui37)/관련E2E12·732/창70·76/본진부팅·러너PASS. 정의67·PNG38 보존·JPG6, 가방가득참 닫기 회수 안전망 유지. 미push."
body = body.replace(old, new, 1).replace(f"퀘스트 커서 버림·툴팁 #{card} 후보 PD 확인(전후6장).", f"퀘스트 커서 버림·툴팁 #{card} 승인 완료. 다음 #274 미제작 아이콘 묶음.", 1)
body = body.replace("퀘스트 버림/툴팁 정합성은 후속UI,", f"퀘스트 버림/툴팁 후속#{card} 완료,", 1)
assert all(len(line) <= 300 for line in body.splitlines())
state.write_text(body, encoding="utf-8", newline="\n")
print(run(main, [sys.executable, "tools/doc_budget.py"]).decode("utf-8-sig"), end="", flush=True)
run(main, ["git", "add", "--", "docs/STATE.md"])
run(main, ["git", "diff", "--cached", "--check"])
print(run(main, ["git", "commit", "-m", f"docs(#{card}): 퀘스트 물건 UI 착륙과 다음 아이콘 제작 기록"]).decode("utf-8"), end="", flush=True)
ctx["state_landed"] = head(main)
ctx["status"] = "complete"
ctx_path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
msg = f"PD 「승인 다음작업」으로 game{ctx['game_landed'][:8]}·검수assets{ctx['assets_landed'][:8]} 착륙 완료. 기존 스크립트 수정만이라 임포트 불필요 판정, 별도 본진 부팅SCRIPT ERROR0·오토로드10/10·주 장면OK·러너5/5 PASS. 검증된 후보와 제품 코드 동일(STATE만 rebase), 단위53/관련E2E12·732/창70·76·정의/PNG105 Git내용 보존(본진 실제102SHA+기존CRLF차이3, 정규화 검증). 전후3쌍 docs/art/458_quest_item_safety, 원본/raw/ACCEPTANCE 자산 reports/458. 가방 가득 참 닫기 회수 안전망 유지. 미push. 다음 #274 미제작 묶음 제작."
print(run(main, [sys.executable, "tools/board.py", "note", str(card), msg]).decode("utf-8-sig"), end="", flush=True)
print(run(main, [sys.executable, "tools/board.py", "note", "273", msg]).decode("utf-8-sig"), end="", flush=True)
print(json.dumps({"game":ctx["game_landed"], "assets":ctx["assets_landed"], "state":ctx["state_landed"], "complete":True}), flush=True)
