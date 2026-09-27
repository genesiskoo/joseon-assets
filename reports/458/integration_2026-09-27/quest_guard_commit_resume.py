from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
ctx = json.loads((main / "tmp/quest_guard_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
report = assets / f"reports/{card}/integration_2026-09-27"
data = json.loads((report / "verification.json").read_text(encoding="utf-8"))
ctx["game_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=game, text=True).strip()
assert ctx["game_commit"] == data["game_commit"]
assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=game).strip()
old = subprocess.run(["git", "diff", "--cached", "--check", "--", ".", f":(exclude)reports/{card}/**/*.log"], cwd=assets, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
assert old.returncode != 0
(report / "evidence_whitespace_before.log").write_bytes(old.stdout)
# A diff is a recorded structured Git output; its leading context spaces are data.
(report / ".gitattributes").write_text("*.log -text\n*.txt -text\n*.diff binary\n", encoding="utf-8")
for folder in [main / "tmp", report]:
    p = folder / "quest_guard_fixture.gd"
    p.write_text(p.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8", newline="\n")
for name in ["quest_guard_commit_resume.py"]:
    shutil.copy2(main / "tmp" / name, report / name)
data["source_diff_sha256"] = hashlib.sha256((report / "game_patch.diff").read_bytes()).hexdigest()
(report / "verification.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def run(command):
    proc = subprocess.run(command, cwd=assets, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode:
        print(proc.stdout.decode("utf-8", errors="replace"), end="")
        raise SystemExit(proc.returncode)
    return proc.stdout

run(["git", "add", "--", f"reports/{card}", f"docs/art/{card}_quest_item_safety"])
run(["git", "diff", "--cached", "--check", "--", ".", f":(exclude)reports/{card}/**/*.log"])
staged = run(["git", "diff", "--cached", "--name-only"]).decode("utf-8").splitlines()
assert all(p.startswith(f"reports/{card}/") or p.startswith(f"docs/art/{card}_quest_item_safety/") for p in staged)
print(run(["git", "commit", "-m", f"test(#{card}): 실제 퀘스트 입력·툴팁 전후와 회귀검수 증거"]).decode("utf-8"), end="")
ctx["assets_commit"] = run(["git", "rev-parse", "HEAD"]).decode().strip()
for p in report.glob("*.log"):
    assert run(["git", "show", f"HEAD:{p.relative_to(assets).as_posix()}"]) == p.read_bytes(), p
assert run(["git", "show", f"HEAD:{(report / 'game_patch.diff').relative_to(assets).as_posix()}"]) == (report / "game_patch.diff").read_bytes()
assert not run(["git", "status", "--porcelain"]).strip()
ctx["status"] = "PD confirmation"
(main / "tmp/quest_guard_context.json").write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"game":ctx["game_commit"], "assets":ctx["assets_commit"], "raw_log_and_diff_git_bytes_exact":True, "main_landed":False}))
