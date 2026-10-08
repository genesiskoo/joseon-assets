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
context = main / "tmp/t2_sword_context.json"
assert not context.exists(), "Resume existing card instead of making a duplicate"
body = """## 문제 / 부모 #274
본국검·제독검·쌍수도·사인검은 현재 T2 ItemDef가 있지만 예전 H1 공용 검 그림을 재사용한다. 채택된 D1 독립 물체 채색으로 전용 원화4종을 제작한다. 핵심잔여55 중4종이며 채택 뒤51, 후보 단계에서는55 유지.

## 사양 / 완료 기준
- item_catalog_v2 §1.1, item_system_v2 §4.2·§17, 현재4개 ItemDef를 읽고 docs/design/item_icons_<카드>.md에 사양 먼저 기록.
- 기존 채택 환도·예도는 화풍 참고. 내장 image_gen 물건별 독립4회, 실제 투명 알파·단일 검·손잡이 위/날 아래·짙은 가방에서도 날이 읽히도록 생성.
- 본국검=균형, 제독검=가는 빠른 날, 쌍수도=긴 양손 손잡이와 넓은 날(검1자루), 사인검=절제된 의장 장식. 세부 형태는 가공 조선 제작 해석이며 새 고증/로어/수치 락을 만들지 않음. 사인참사검 유니크와 혼동 금지.
- 현재1×3칸/쌓기1/무기/클래스·쌍수도 two_handed 등 정의 보존. alpha16/8%여백/Lanczos 기존 패킹으로80×240 RGBA. 실제 UiSkin의40×120 및30/48/60px칸 검수.
- 현재 정의67·승인PNG38=105파일 SHA 보존. 같은 구도 before/after, 승인 환도·예도·가죽신 기준 영역 픽셀 보존. 게임 아이콘 설치/실행 코드 변경 없음.
- 원화/프롬프트/참조/생성 경로/해시/raw는 joseon-assets 생산폴더·reports, JPG4(1280폭·각300KB이하)는 게임 docs/art. 생성물은 즉시 대화에 표시. 문서예산 및 알파/점유/공통 렌더 검증 후 실행 가능한 후보 커밋.
- 완성 후보는 PD 확인으로 옮기고 멈춤. 채택 후 별도 게임 반입 카드. push 없음.

## 소유 / 왜 이 구조인가
Codex 게임자리87은 이 카드 사양·검수 사진만, 자산자리87은 독립 원화4종·패킹·검수 보고서. 작은 세로 칸에서 날 폭·손잡이 길이·의장 금속의 차이를 읽도록 실루엣을 먼저 나눈다. 공용 검을 단순 색칠하는 대안은 실제 무기별 차이를 지우므로 기각. 실제 공유 렌더에 후보를 메모리로만 올려 채택 전에 비교한다.
"""
def run(args, cwd=main, env=None):
    p = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout.decode("utf-8", errors="replace"), end="")
    p.check_returncode()
    return p.stdout
for tree in [main, game, assets]:
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=tree).strip(), str(tree)
raw = run([sys.executable, "tools/board.py", "new", "[P2] D1 T2 검 아이콘4 — 본국검·제독검·쌍수도·사인검", "-l", "P2,UI,아트", "-b", body, "--week", "--who", "codex"])
match = re.search(r"#(\d+) 생성", raw.decode("utf-8"))
assert match, "Inspect board output; do not retry card creation"
card = int(match.group(1))
ctx = {"card":card, "parent":274, "main":main.as_posix(), "game":game.as_posix(), "assets":assets.as_posix(), "status":"created", "body":body}
context.write_text(json.dumps(ctx, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
run([sys.executable, "tools/board.py", "start", str(card)])
for tree, suffix in [(game,"t2-sword-preview"), (assets,"t2-sword-icons")]:
    run(["git", "switch", "-c", f"codex/{card}-{suffix}", "main"], tree)
report = assets / f"reports/{card}/2026-09-27"
report.mkdir(parents=True, exist_ok=True)
(report / ".gitattributes").write_text("*.log -text\n*.txt -text\n", encoding="utf-8", newline="\n")
(report / f"{card}_board_new.log").write_bytes(raw)
env = dict(os.environ)
env["GODOT_BIN"] = "C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe"
p = subprocess.run([sys.executable, "tools/wt.py", "setup", "--card", str(card)], cwd=game, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(report / f"{card}_wt_setup.log").write_bytes(p.stdout)
print(p.stdout.decode("utf-8", errors="replace"))
p.check_returncode()
ctx.update(status="started", production=(assets / f"workbench/production/item_icons_{card}").as_posix(), report=report.as_posix(), game_base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=game,text=True).strip(), assets_base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=assets,text=True).strip())
context.write_text(json.dumps(ctx, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
run([sys.executable,"tools/board.py","note","274",f"후속 #{card} 착수: 현 T2 검4(bongukgeom/jedokgeom/ssangsudo/saingeom) 전용 D1 원화·80×240 후보를 독립 생성. 기존 환도·예도 화풍과 실제 UiSkin40×120 검수, 현재105파일 보존. 현재핵심잔여55 유지·4종채택시51. 원화 판정 뒤 게임 반입은 별도 카드."])
print(f"CARD={card}")
