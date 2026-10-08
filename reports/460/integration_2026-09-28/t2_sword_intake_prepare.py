from pathlib import Path
import hashlib
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
context = main / "tmp/t2_sword_intake_context.json"
ctx = json.loads(context.read_text(encoding="utf-8"))
assert ctx["status"] == "started"
card = ctx["card"]
game,report,source = [Path(ctx[k]) for k in ["game","report","source"]]
production = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
ids = [e["item_id"] for e in production["items"]]
files = sorted((game / "data/items").glob("*.tres")) + sorted((game / "assets/sprites/ui/icons_a/items").glob("*.png")) + sorted((game / "assets/sprites/ui/icons_a/skills").glob("*.png"))
protected = {}
baseline_definitions = {}
for path in files:
    rel = path.relative_to(game).as_posix()
    if path.suffix == ".tres" and path.stem in ids:
        baseline_definitions[rel] = path.read_text(encoding="utf-8")
    else:
        protected[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
assert len(protected) == 101 and len(baseline_definitions) == 4
snapshot = {"game_base":ctx["game_base"],"source_commit":ctx["source_commit"],"protected_files":protected,"before_definitions":baseline_definitions,"old_h1_icons":{e["current_icon"].removeprefix("res://"):hashlib.sha256((game / e["current_icon"].removeprefix("res://")).read_bytes()).hexdigest() for e in production["items"]}}
(report / "before_snapshot.json").write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
spec = f"""\n\n## #{card} 承認 T2 검4 게임 반입 — 사양

PD 2026-09-28 「승인 다음」으로 #459 본국검·제독검·쌍수도·사인검r2를 채택하고 후속 게임 반입을 승인했다. 자산main {ctx['source_commit'][:8]}의80×240 RGBA4를 PowerShell Copy-Item으로 바이트 그대로 `icons_a/items`에 복사하고 기존ItemDef의Texture2D 경로만 바꾼다. 현재1×3칸·쌓기1·가격·요구치·보조칸·쌍수도two_handed=true·바닥모델을 보존하며 ICON_PENDING/MODEL_PENDING도 그대로다. 공통UiSkin의 알파 영역·비율보존을 재사용한다. 가방40×120/무기칸/48px좌판/커서에서 같은 그림을 확인하고 실제 마지막칸 집기·되놓기·검4착용/교환/해제·양손보조칸 차단/복원·가격/구매/판매·Alt이름표회수를 검수한다. 같은 표본·구도의 가방/커서와양손장비/좌판 전후3쌍과 원본SHA4·그림외필드4·기존101파일/H1검3 보존, 단위/관련UI·장비·거래·줍기E2E와 부팅을 남긴다. 현재 #274핵심잔여51, 이 반입은 바닥3D모델 교체가 아니다. 출처·해시·매핑은 `art/ui_intake_{card}/intake_manifest.json`, 실게임 사진은 `docs/art/{card}_d1_t2_sword_intake`다.

왜 이 구조인가: 승인 PNG와 ItemDef 연결만 바꾸면 각 UI가 기존 알파 렌더를 통해 같은 물체를 쓰며 수치·클릭영역·착용을 건드리지 않는다. UI별 그림/배율을 따로 붙이는 대안은 점유·호버 영역과 그림을 분리할 수 있어 기각했다. 실제 긴 검의 집기·교환·양손·거래·회수와 파일 보존을 함께 확인해 아트 반입을 재현한다.
""".replace("承認","승인")
doc = game / "docs/design/ui_v2.md"
old = doc.read_text(encoding="utf-8")
assert f"## #{card} 승인 T2 검4" not in old
doc.write_text(old+spec,encoding="utf-8",newline="\n")
(report / "SPEC.md").write_text(spec.strip()+"\n",encoding="utf-8",newline="\n")
fixture = game / "tests/e2e/scenarios/icon_intake.gd"
text = fixture.read_text(encoding="utf-8")
assert "func _sword_review()" not in text
early = '''
\tif "--icon-intake-sword-only" in OS.get_cmdline_user_args():
\t\tvar was_dev: bool = DevMode.is_active
\t\tvar help_text: String = t.main.hud_label.text
\t\tDevMode.is_active = false
\t\tt.main.hud_label.text = ""
\t\tawait _sword_review()
\t\tDevMode.is_active = was_dev
\t\tt.main.hud_label.text = help_text
\t\tawait t.close_all()
\t\treturn
'''
text = text.replace("func run() -> void:\n","func run() -> void:\n"+early,1)
needle = "\tawait _material_review()\n\tawait _seal_review()\n"
assert needle in text
text = text.replace(needle,needle+"\tawait _sword_review()\n",1)
text += "\n\n"+(main / "tmp/460_sword_review.gd").read_text(encoding="utf-8")
fixture.write_text(text,encoding="utf-8",newline="\n")
ctx["status"] = "prepared_before_intake"
context.write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"#{card}: spec first, actual input fixture prepared; old PNG/ItemDef unchanged; protected101 +4 definitions recorded")
