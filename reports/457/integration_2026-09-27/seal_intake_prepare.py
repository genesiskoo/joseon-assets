from pathlib import Path
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
ctx = json.loads((main / "tmp/seal_intake_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
report = assets / f"reports/{card}/integration_2026-09-27"
spec = f"""## #{card} 승인 봉인물3 반입 — 사양

PD 승인 #454 봉인패·봉인고리·사슬 조각3종(1×1/쌓기1/quest_item=true)의80×80 RGBA PNG를 승인 바이트 그대로 icons_a/items에 복사하고 ItemDef.icon만 연결한다. 정본 item_catalog_v2 §6.4·item_system_v2 §14.4·14.5·17. 퀘스트/소비/판매·드랍/가격·모델 규칙은 그대로다. 현재 definition67/채택PNG35를 기준으로 대상3의 icon 이외 필드, 다른 정의64, 기존 PNG35를 보존한다. test_items ICON_PENDING3만0으로 갱신한다. 실제 입력으로 가방/툴팁/커서 되놓기·Ctrl버림과 판매 거부·이름표 줍기를 전후 동일 표본으로 촬영한다. JPG3쌍(1280폭/각300KB이하), 원본/raw는 자산 reports/{card}. 새 프레임/렌더러/효과를 추가하지 않는다. 봉밀굴 봉인3 소비/개방은 현재 sealed_message 고정인 #169 대기, 장산범/불가살이 보스 연결은 #69 대기다. 이번 결과는 그 미구현 기능의 합격 판정이 아니다. 기존 단위와 관련UI·줍기·퀘스트·보스 E2E/빠른 부팅·러너·문서 예산을 검증한다.

왜 이 구조인가: 채택된 PNG를 기존 아이콘 경로에 연결하면 슬롯/툴팁/퀘스트 입력을 그대로 사용한다. 새 렌더러나 문 개방 규칙을 추가하는 대안은 아트 반입 범위를 넘어 위험을 늘리므로 기각했다. 승인 바이트·나머지 필드 보존과 실제 입력을 함께 검수한다. 핵심73 밖 추가3으로 #274 핵심잔여55는 유지한다.
"""
p = game / "docs/design/ui_v2.md"
body = p.read_text(encoding="utf-8")
assert f"## #{card} " not in body
p.write_text(body + "\n\n" + spec, encoding="utf-8", newline="\n")
paths = sorted((game / "data/items").glob("*.tres")) + sorted((game / "assets/sprites/ui/icons_a/items").glob("*.png")) + sorted((game / "assets/sprites/ui/icons_a/skills").glob("*.png"))
snapshot = {p.relative_to(game).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert len(snapshot) == 102
(report / "before_snapshot.json").write_text(json.dumps({"base":ctx["game_base"], "files":snapshot}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
p = game / "tests/e2e/scenarios/icon_intake.gd"
body = p.read_text(encoding="utf-8")
assert "func _seal_review()" not in body
early = '''
\tif "--icon-intake-seal-only" in OS.get_cmdline_user_args():
\t\tvar was_dev: bool = DevMode.is_active
\t\tvar help_text: String = t.main.hud_label.text
\t\tDevMode.is_active = false
\t\tt.main.hud_label.text = ""
\t\tawait _seal_review()
\t\tDevMode.is_active = was_dev
\t\tt.main.hud_label.text = help_text
\t\tawait t.close_all()
\t\treturn
'''
body = body.replace("func run() -> void:\n", "func run() -> void:\n" + early, 1)
needle = "\tawait _t1_review()\n\tawait _t2_review()\n\tawait _material_review()\n"
assert needle in body
body = body.replace(needle, needle + "\tawait _seal_review()\n", 1)
body += "\n\n" + (main / "tmp/seal_review.gd").read_text(encoding="utf-8")
p.write_text(body, encoding="utf-8", newline="\n")
p = game / "tests/e2e/scenarios/potion_tiers.gd"
body = p.read_text(encoding="utf-8")
body = body.replace("아이콘 없는 다섯(청심환·괴황지·경면주사·흑랑 이빨·흑랑의 봉인패 — 글자 폴백이 어떻게 보이는지)", "현재 아이콘 물건 다섯(청심환·괴황지·경면주사·흑랑 이빨·흑랑의 봉인패)")
body = body.replace("가방에 아이콘 없는 다섯(글자 폴백)", "가방에 현재 아이콘 물건 다섯")
body = body.replace("새 물건 다섯 자리 (아이콘 없음 — 글자 폴백)", "새 물건 다섯 자리 (현재 정의 아이콘)")
p.write_text(body, encoding="utf-8", newline="\n")
print(f"PASS #{card}: spec first; protected102; actual input fixture added; PNG/ItemDefs still before.")
