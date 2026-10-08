from pathlib import Path
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
env = dict(os.environ, PYTHONIOENCODING="utf-8", GODOT_BIN="C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe")

def run(cwd, args, log=None):
    p = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_bytes(p.stdout)
    print(p.stdout.decode("utf-8", errors="replace"), end="", flush=True)
    assert p.returncode == 0, args
    return p.stdout.decode("utf-8", errors="replace")

acceptance = assets / "workbench/production/item_icons_454/ACCEPTANCE.md"
if not acceptance.exists():
    run(main, [sys.executable, "tools/board.py", "who", "454", "codex"])
    run(main, [sys.executable, "tools/board.py", "note", "454", "PD 2026-09-27 대화 승인 다음 = 봉인패·봉인고리·사슬 조각3종 전부 채택. 원화 자산9747c2a·게임 검수b405aab2를 승인 착륙하고 실제 반입은 별도 후속 카드. #274 핵심잔여55 유지, #451은 별도 PD 확인."])
    acceptance.write_text("# #454 봉인물3종 채택\n\nPD 2026-09-27 대화 **승인 다음**으로 봉인패·봉인고리·사슬 조각3종을 전부 채택했다. 원화/80px 후보/프롬프트/검수는9747c2a, 게임 검수 문서는b405aab2. 핵심73 밖의 추가 퀘스트 물건이므로 #274 핵심잔여55는 그대로다. 실제 게임 반입은 후속 카드로 진행한다. #451 승인으로 해석하지 않는다.\n", encoding="utf-8", newline="\n")
    run(assets, ["git", "add", "--", "workbench/production/item_icons_454/ACCEPTANCE.md"])
    run(assets, ["git", "diff", "--cached", "--check"])
    run(assets, ["git", "commit", "-m", "docs(#454): 봉인물3종 PD 채택 기록"])
else:
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=assets).strip()
    run(assets, ["git", "rebase", "main"], main / "tmp/454_assets_approval_rebase.log")
    import hashlib
    production = assets / "workbench/production/item_icons_454"
    manifest = json.loads((production / "manifest.json").read_text(encoding="utf-8"))
    for item in manifest["items"]:
        assert hashlib.sha256((production / "game/items" / (item["item_id"] + ".png")).read_bytes()).hexdigest() == item["game_sha256"]
approved = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=assets, text=True).strip()
run(Path("C:/workspace/joseon-assets"), ["git", "merge", "--ff-only", approved])
run(game, [sys.executable, "tools/wt.py", "land", "-m", "PD 승인 봉인물3 원화 사양과 공통 UI 검수 착륙"], main / "tmp/454_approval_land.log")
body = """## 범위
PD 승인 #454 봉인패·봉인고리·사슬 조각3종의80×80 RGBA PNG를 현재 게임에 반입한다. 원화 자산9747c2a(채택 커밋은 진행 메모), 정본 item_catalog_v2 §6.4·item_system_v2 §14.4·14.5·17. #274 핵심73 밖 추가3으로 핵심잔여55 유지.

## 수용 기준
- 실제 icons_a/items PNG3을 승인 바이트 그대로 PowerShell Copy-Item, ItemDef.icon만 연결. 1×1/쌓기1/quest_item/이름·수치·가격·드랍·모델 유지.
- 현재 정의67파일과 채택 PNG35 기준 보존. 대상3은 icon 이외 필드 동일; 다른 정의64와 PNG35 해시 동일.
- 실제 입력으로 가방/툴팁/커서 되놓기·판매 거부·Ctrl 버림 거부·바닥 이름표 줍기를 검수. 전후 같은 표본3쌍 JPG1280폭≤300KB≤6장, 원본/raw는 자산 reports에 저장.
- 이미 있는 test_items ICON_PENDING3을 빈 목록으로 갱신. 적절한 단위·관련 E2E·부팅/러너/문서 예산 검증. 기존 코드는 바꾸지 않는다.
- 봉밀굴 봉인 소비/개방은 #169 대기이며 이번 UI 반입에서 새 규칙을 구현하지 않는다. 장산범/불가살이 보스 연결도 #69 대기.
- WT87/자산87 재사용. 스펙 먼저, 검증된 실행 가능 상태 커밋·승인 범위 착륙·카드 완료. push 없음.

## 왜 이 구조인가
이미 채택된 독립 PNG를 기존 UiSkin 경로에 연결하면 기존 슬롯/툴팁/희귀도/퀘스트 입력을 그대로 사용할 수 있다. 새 렌더러나 게임 규칙을 추가하는 대안은 아트 교체 범위를 넘어 위험을 늘리므로 기각한다. 실제 입력과 승인 바이트/기존 파일 보존을 함께 검수한다.
"""
out = run(main, [sys.executable, "tools/board.py", "new", "[P2] 승인 봉인물3종 게임 반입·실제 가방과 줍기 검수 (#454)", "--who", "codex", "-l", "P2,UI,아트", "-b", body, "--week"])
match = re.search(r"(?:issues/|#)(\d+)", out)
assert match
card = int(match.group(1))
context = {"card":card, "source_commit":approved, "production_commit":"9747c2a226079887929af0951bb69b7f75c9e851", "game_preview_landed":subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=game, text=True).strip(), "approval":"PD 2026-09-27: 승인 다음", "body":body}
(main / "tmp/seal_intake_context.json").write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
run(main, [sys.executable, "tools/board.py", "start", str(card)])
for tree, branch in [(game, f"codex/{card}-quest-seal-intake"), (assets, f"codex/{card}-quest-seal-review")]:
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=tree).strip(), tree
    run(tree, ["git", "switch", "-c", branch, "main"])
report = assets / f"reports/{card}/integration_2026-09-27"
report.mkdir(parents=True, exist_ok=True)
(report / ".gitattributes").write_text("*.log -text\n*.txt -text\n", encoding="utf-8")
run(game, [sys.executable, "tools/wt.py", "setup", "--card", str(card)], report / "wt_setup.log")
context["game_base"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=game, text=True).strip()
(main / "tmp/seal_intake_context.json").write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(report / "game_base.json").write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"READY seal intake #{card}", flush=True)
