from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
approved = json.loads((main / "tmp/t2_sword_context.json").read_text(encoding="utf-8"))
assert approved["status"] == "approved_and_landed"
context = main / "tmp/t2_sword_intake_context.json"
assert not context.exists(), "Resume existing intake card"
game,assets = Path(approved["game"]),Path(approved["assets"])
env = dict(os.environ,PYTHONIOENCODING="utf-8",GODOT_BIN="C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe")
def run(tree,args):
    p = subprocess.run(args,cwd=tree,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(p.stdout.decode("utf-8-sig",errors="replace"),end="",flush=True)
    p.check_returncode()
    return p.stdout
body = f"""## 승인 / 범위
PD 2026-09-28 「승인 다음」: #459 검4(본국검·제독검·쌍수도·사인검r2) 전부 채택하고 별도 카드로 게임 반입 진행 승인. 승인 자산main {approved['assets_landed']}, 제작 da2f36b, 사양 main{approved['game_landed']}. 원화 재생성 없이 승인80×240 RGBA4를 그대로 반입한다. 부모 #274 핵심잔여51.

## 사양 / 완료 기준
- docs/design/ui_v2.md에 한 단락 먼저. PowerShell Copy-Item으로 PNG4를 icons_a/items에 복사. ItemDef4는 기존Texture2D 바인딩의 경로만 변경, icon id/load_steps/수치/요구치/1×3/쌓기1/쌍수도two_handed=true/가격/바닥모델 모두 보존.
- 승인PNG4 SHA/크기/알파와 그림 외 필드4 보존. 다른tres63·기존PNG38=101파일 및 옛H1검3 보존. ICON_PENDING/MODEL_PENDING 변경 없음. art/ui_intake_<카드>/intake_manifest.json에 출처·승인·매핑·해시.
- 실제 입력 fixture로 가방4종/1×3 마지막칸 집기/되놓기,4무기 착용·교환·해제, 양손무기와보조칸계약,48px좌판호버/구매/판매/가격/같은물체이동, loot_dropped→Alt실제이름표클릭→가방회수 검증.
- 반입 전에 같은 표본·구도의 스샷3장, 반입후3장(가방·커서/장비·좌판). JPG1280폭/각300KB이하/총6장, 원본·raw로그·명령·검수도구는 자산reports. 만든 결과는 대화에서 전후 표시.
- test.ps1 -Unit 및영향관련UI/장비/거래/줍기 E2E, 빠른부팅·러너·문서예산 PASS 후 실행가능한커밋. 제품 동작 코드는 바꾸지 않음. 기존 승인바이트의 게임 반입까지 승인된 범위로 검수 후 wt.py land, 본진임포트/부팅을 확인. 추가 아트/새 UI 동작이 필요하면 별도PD판정.
- 단일 board.py로 추적·완료, push 없음. 기존 #451 후보는 그대로 보존.

## 소유 / 왜 이 구조인가
게임자리87: PNG4·ItemDef4경로·icon_intake 실제입력 대본·ui_v2 사양·TASK로그·반입manifest·사진/QA. 자산자리87: 이 카드 실게임검수 보고서 및 #459 승인/반입 연결 기록. 공통 UiSkin의 기존 알파 영역·비율보존을 사용하면 가방·무기칸·좌판·커서가 동일 그림을 사용한다. UI마다그림/배율을 따로 붙이는 대안은클릭영역과그림이 어긋날 수 있어 기각한다. 새1×3무기가 기존 착용·거래·줍기에 영향을주지 않는지 실제입력과해시로 확인한다.
"""
for tree in [main,game,assets]:
    assert not subprocess.check_output(["git","status","--porcelain"],cwd=tree).strip(),tree
raw = run(main,[sys.executable,"tools/board.py","new","[P2] 채택 D1 T2 검4 게임 반입 — 1×3·양손·거래·줍기 검수","-l","P2,UI,아트","-b",body,"--week","--who","codex"])
match = re.search(r"#(\d+) 생성",raw.decode("utf-8"))
assert match,"Inspect output; never repeat creation"
card = int(match.group(1))
ctx = {"card":card,"production_card":459,"parent":274,"main":main.as_posix(),"game":game.as_posix(),"assets":assets.as_posix(),"source":"C:/workspace/joseon-assets/workbench/production/item_icons_459","source_commit":approved["assets_landed"],"approval":"PD 2026-09-28 승인 다음; #459 4종채택 및 별도게임반입", "status":"created","body":body}
context.write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
run(main,[sys.executable,"tools/board.py","start",str(card)])
for tree,suffix in [(game,"t2-sword-intake"),(assets,"t2-sword-intake-review")]:
    run(tree,["git","switch","-c",f"codex/{card}-{suffix}","main"])
report = assets / f"reports/{card}/integration_2026-09-28"
report.mkdir(parents=True,exist_ok=True)
(report / ".gitattributes").write_text("*.log -text\n*.txt -text\n",encoding="utf-8",newline="\n")
(report / "board_new.log").write_bytes(raw)
p = subprocess.run([sys.executable,"tools/wt.py","setup","--card",str(card)],cwd=game,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(report / "wt_setup.log").write_bytes(p.stdout)
print(p.stdout.decode("utf-8-sig",errors="replace"),end="",flush=True)
p.check_returncode()
ctx.update(status="started",report=report.as_posix(),gallery=(game / f"docs/art/{card}_d1_t2_sword_intake").as_posix(),intake=(game / f"art/ui_intake_{card}").as_posix(),game_base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=game,text=True).strip(),assets_base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=assets,text=True).strip())
context.write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
run(main,[sys.executable,"tools/board.py","note","274",f"#{card} 승인 검4 실제게임반입 착수. #459 승인4 PNG를 바이트 그대로복사, ItemDef의그림경로만교체. 기존1×3/쌍수도양손/수치/모델/다른101파일보존과 실제가방·장비·거래·이름표회수·전후3쌍검수. 핵심잔여51유지, 미push."])
print(f"INTAKE_CARD={card}",flush=True)
