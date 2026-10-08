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
    proc = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log:
        log.write_bytes(proc.stdout)
    output = proc.stdout.decode("utf-8-sig", errors="replace")
    print(output, end="", flush=True)
    if proc.returncode:
        raise SystemExit(proc.returncode)
    return output

for tree in [main, game, assets]:
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=tree).strip(), tree
body = """## 문제와 범위
#457 실제 봉인물 검수에서 확인: can_discard=false인 봉인3도 커서에 든 채 창 밖을 좌클릭하면 바닥에 버려진다. 툴팁은 불가능한 버리기를 안내하고, 좌판이 열리면 판매가 1엽전도 보여 준다. item_system_v2 §14.4의 팔기·버리기 불가 계약에 맞춘다.

## 완료 기준
- InventoryUi의 명시적 창 밖 버림만 can_discard()로 거부. 같은 ItemInstance를 커서에 유지하고 기존 거부 문구 표시.
- TooltipContent: 퀘스트 가방 물건은 들기 + 팔기·버리기 불가 안내. 좌판 열린 가방에서도 판매가/판매 동작/버림 동작 없음.
- 일반 물건의 창 밖 버림/판매가·힌트와 HUD 벨트 입력 유지. 가방 꽉 찬 상태에서 창 닫을 때 발밑으로 흘리는 안전망은 §14.5대로 유지하고 실제 이름표로 회수 검증.
- 아이템 정의67/채택PNG38의 바이트 보존. 봉밀굴 개방#169/수하 보스#69는 이번 범위 아님.
- 스펙 먼저 ui_v2.md, 기존 test_item_ui + icon_intake 봉인 표본에서 실제 입력/툴팁 회귀 검수. 변경 전후 같은 구도 JPG3쌍, 원본/raw는 joseon-assets reports/해당카드.
- 단위+관련 UI·줍기·퀘스트 E2E·부팅/러너·문서 예산 합격 후 실행 가능한 커밋. 결과는 PD 확인, 신규 UI 후보를 임의로 main에 병합하지 않음. push 없음.

## 소유 파일 / 자리
codex WT87 재사용: ui/inventory_ui.gd, ui/tooltip_content.gd, tests/test_item_ui.gd, tests/e2e/scenarios/icon_intake.gd, docs/design/ui_v2.md 및 이 카드 검수 문서·사진. 자산87은 검수 보고서만. 다른 자리/카드 편집 없음.

## 왜 이 구조인가
입력의 명시적 버림 지점에서만 차단하면, 동일 can_discard 계약으로 툴팁과 거래를 맞추면서 창 닫기 회수 안전망은 유지된다. 공통 _drop_held 전체를 금지하는 대안은 꽉 찬 가방의 자동 회수 실패 때 물건을 잃거나 커서를 남길 수 있으므로 기각한다.
"""
out = run(main, [sys.executable, "tools/board.py", "new", "[P1] 퀘스트 물건 창 밖 버림 차단·툴팁 판매/버리기 안내 정합성 (#457)", "--who", "codex", "-l", "P1,UI,버그", "-b", body, "--week"])
match = re.search(r"(?:issues/|#)(\d+)", out)
assert match, out
card = int(match.group(1))
ctx = {"card":card, "body":body, "game_base":subprocess.check_output(["git", "rev-parse", "main"], cwd=main, text=True).strip(), "assets_base":subprocess.check_output(["git", "rev-parse", "main"], cwd=assets, text=True).strip(), "status":"in progress"}
(main / "tmp/quest_guard_context.json").write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
run(main, [sys.executable, "tools/board.py", "start", str(card)])
for tree, branch in [(game, f"codex/{card}-quest-item-safety"), (assets, f"codex/{card}-quest-item-safety-review")]:
    run(tree, ["git", "switch", "-c", branch, "main"])
report = assets / f"reports/{card}/integration_2026-09-27"
report.mkdir(parents=True, exist_ok=True)
(report / ".gitattributes").write_text("*.log -text\n*.txt -text\n", encoding="utf-8")
(report / "context.json").write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
run(game, [sys.executable, "tools/wt.py", "setup", "--card", str(card)], report / "wt_setup.log")
print(f"READY #{card} quest item safety", flush=True)
