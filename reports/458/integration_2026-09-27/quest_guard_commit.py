from pathlib import Path
import hashlib
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
ctx = json.loads((main / "tmp/quest_guard_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
report = assets / f"reports/{card}/integration_2026-09-27"

def run(tree, command):
    proc = subprocess.run(command, cwd=tree, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode:
        print(proc.stdout.decode("utf-8", errors="replace"), end="", flush=True)
        raise SystemExit(proc.returncode)
    return proc.stdout

head = lambda tree:run(tree, ["git", "rev-parse", "HEAD"]).decode().strip()
verification = json.loads((report / "verification.json").read_text(encoding="utf-8"))
assert "validation" in verification and not verification["main_landed"]
for name, digest in json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))["files"].items():
    assert hashlib.sha256((game / name).read_bytes()).hexdigest() == digest, name
assert not run(game, ["git", "diff", "--cached", "--name-only"]).strip(), "Unexpected staged work"
paths = ["ui/inventory_ui.gd", "ui/tooltip_content.gd", "tests/test_item_ui.gd", "tests/e2e/scenarios/icon_intake.gd", "docs/design/ui_v2.md", "docs/design/item_system_v2.md", f"docs/art/{card}_quest_item_safety"]
run(game, ["git", "add", "--"] + paths)
run(game, ["git", "diff", "--cached", "--check"])
staged = run(game, ["git", "diff", "--cached", "--name-only"]).decode("utf-8").splitlines()
assert len(staged) == 14 and all(p in paths[:6] or p.startswith(paths[-1] + "/") for p in staged), staged
print(run(game, ["git", "diff", "--cached", "--stat"]).decode("utf-8"), end="")
print(run(game, ["git", "commit", "-m", f"fix(#{card}): 퀘스트 물건 커서 버림 차단과 툴팁 정합성"]).decode("utf-8"), end="")
ctx["game_commit"] = head(game)
verification["game_commit"] = ctx["game_commit"]
verification["tested_base"] = ctx["game_base"]
verification["main_landed"] = False
(report / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(report / "game_patch.diff").write_bytes(run(game, ["git", "diff", f"{ctx['game_base']}..HEAD"]))
assert not run(assets, ["git", "diff", "--cached", "--name-only"]).strip(), "Unexpected staged asset work"
run(assets, ["git", "add", "--", f"reports/{card}", f"docs/art/{card}_quest_item_safety"])
run(assets, ["git", "diff", "--cached", "--check", "--", ".", f":(exclude)reports/{card}/**/*.log"])
print(run(assets, ["git", "commit", "-m", f"test(#{card}): 퀘스트 입력·툴팁 전후와 회귀검수 증거"]).decode("utf-8"), end="")
ctx["assets_commit"] = head(assets)
for path in report.glob("*.log"):
    assert run(assets, ["git", "show", f"HEAD:{path.relative_to(assets).as_posix()}"]) == path.read_bytes(), path
assert not run(game, ["git", "status", "--porcelain"]).strip()
assert not run(assets, ["git", "status", "--porcelain"]).strip()
ctx["status"] = "PD confirmation"
(main / "tmp/quest_guard_context.json").write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"card":card, "game_commit":ctx["game_commit"], "assets_commit":ctx["assets_commit"], "main_landed":False, "raw_git_bytes_preserved":True}))
