from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
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
for tree in [main, game, assets]:
    assert not run(tree, ["git", "status", "--porcelain"]).strip(), tree
assert head(game) == ctx["game_commit"] and head(assets) == ctx["assets_commit"]
incoming = run(main, ["git", "diff", "--name-only", f"{ctx['game_base']}..HEAD"]).decode().splitlines()
assert incoming == ["docs/STATE.md"], f"Incoming runtime change: {incoming}"
data_path = report / "verification.json"
data = json.loads(data_path.read_text(encoding="utf-8"))
assert data["validation"]["unit_gd"] == 53 and data["validation"]["related_checks"] == 732
for name, digest in json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))["files"].items():
    assert hashlib.sha256((game / name).read_bytes()).hexdigest() == digest
for mode, meta in data["validation"]["runs"].items():
    assert meta["exit_code"] == 0 and hashlib.sha256((report / meta["raw_log"]).read_bytes()).hexdigest() == meta["raw_sha256"]
print(run(main, [sys.executable, "tools/board.py", "note", str(card), "PD 채팅 2026-09-27 「승인 다음작업」: 현재 UI 후보 game6587ad94/검수1b79c154 채택·착륙 승인. 이후 main 변경은 STATE 기록뿐이고 제품 코드/검사 SHA가 같으므로 기존 단위53·관련12/732·창76 검증을 사용해 wt.py land --no-test로 착륙한다. 본진 임포트·부팅은 착륙 도구가 확인하며 push하지 않는다."]).decode("utf-8-sig"), end="", flush=True)
command = [sys.executable, "tools/wt.py", "land", "--no-test", "-m", "PD 승인 퀘스트 물건 창 밖 버림 차단·툴팁 정합성, 단위53/관련12·732/실제76 PASS"]
started = time.time()
path = report / f"{card}_land_{time.strftime('%H%M%S')}.log"
with path.open("wb") as out:
    p = subprocess.Popen(command, cwd=game, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for raw in iter(p.stdout.readline, b""):
        out.write(raw)
        out.flush()
        print(raw.decode("utf-8-sig", errors="replace"), end="", flush=True)
    rc = p.wait()
meta = {"command":command, "exit_code":rc, "started":started, "elapsed":time.time()-started, "raw_log":path.name, "raw_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
(report / "run_land.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
assert rc == 0
body = path.read_text(encoding="utf-8-sig")
assert "✅ 착륙" in body and "SCRIPT ERROR 0" in body and "본진 임포트" in body
ctx["game_landed"] = head(main)
assert ctx["game_landed"] == head(game)
paths = run(game, ["git", "diff", "--name-only", ctx["game_commit"], "HEAD"]).decode().splitlines()
assert paths == ["docs/STATE.md"], paths
for name, digest in json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))["files"].items():
    assert hashlib.sha256((main / name).read_bytes()).hexdigest() == digest
data["main_landed"] = True
data["landing"] = {"approval":"PD 2026-09-27 승인 다음작업", "game_main":ctx["game_landed"], "candidate":ctx["game_commit"], "same_runtime_after_doc_only_rebase":True, "protected105_main_sha_equal":True, "run":meta, "pushed":False}
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(report / "ACCEPTANCE.md").write_text(f"# #{card} 채택·착륙\n\nPD 2026-09-27 「승인 다음작업」으로 후보 game{ctx['game_commit']}·검수{ctx['assets_commit']} 승인. main의 STATE 기록만 rebase 후 game {ctx['game_landed']} 착륙, 제품 코드 동일·정의/PNG105 SHA 동일. 이전 단위53/관련E2E12·732/창70·76 PASS를 적용, 본진 임포트와 부팅오류0는 run_land.json과 원시 도구 stdout으로 확인. 미push. 검수 후보 QA의 미병합 표기는 제작 시점 기록이며 이 문서가 채택 결과다.\n", encoding="utf-8")
run(assets, ["git", "add", "--", f"reports/{card}"])
run(assets, ["git", "diff", "--cached", "--check", "--", ".", f":(exclude)reports/{card}/**/*.log"])
print(run(assets, ["git", "commit", "-m", f"test(#{card}): PD 채택·본진 착륙과 코드/자산 보존 기록"]).decode("utf-8"), end="", flush=True)
print(run(assets, ["git", "rebase", "main"]).decode("utf-8"), end="", flush=True)
ctx["assets_landed"] = head(assets)
print(run(assets_main, ["git", "merge", "--ff-only", ctx["assets_landed"]]).decode("utf-8"), end="", flush=True)
ctx["status"] = "complete"
ctx_path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"game_main":ctx["game_landed"], "assets_main":ctx["assets_landed"], "protected105":True, "main_boot_pass":True, "pushed":False}), flush=True)
