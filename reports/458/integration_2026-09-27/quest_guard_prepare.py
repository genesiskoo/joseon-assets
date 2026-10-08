from pathlib import Path
import hashlib
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
ctx = json.loads((main / "tmp/quest_guard_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
report = main / f"._tmp/assets_87/reports/{card}/integration_2026-09-27"
spec = f"""## #{card} 퀘스트 물건 커서 버림·툴팁 정합성 — 사양

정본 item_system_v2 §14.4·14.5의 can_discard() 계약을 명시적인 창 밖 좌클릭에도 적용한다. 퀘스트 물건이면 기존 「퀘스트 물건은 버릴 수 없다」를 보이고 같은 ItemInstance를 커서에 유지한다. 되놓기·HUD 벨트 경로·일반 물건 버리기는 그대로이며, 창 닫기 때 가방이 꽉 차 자동 배치가 실패하면 발밑에 남겨 회수하게 하는 안전망은 유지한다. 가방 툴팁은 퀘스트에 「좌클릭: 들기」와 「퀘스트 물건 · 팔기·버리기 불가」를 표시하고, 좌판을 열어도 판매가/판매·버리기 동작을 안내하지 않는다. 일반 물건 가격·스택 판매 안내는 유지한다. 기존 정의67/PNG38 바이트를 보존하고 #169 봉밀굴 개방/#69 수하 보스는 다루지 않는다. 기존 unit/item_ui와 icon_intake에서 봉인3의 실제 입력·툴팁, 일반 물약 버림, 꽉 찬 가방 닫기→이름표 회수를 검수한다. 전후 같은 구도 JPG3쌍은 docs/art/{card}_quest_item_safety, 원본/raw는 자산 reports/{card}. 결과는 PD 확인 후 착륙한다.

왜 이 구조인가: can_discard를 명시적 버림 입력과 툴팁에 함께 적용하면 기존 거래/퀘스트 계약이 일치한다. _drop_held 전체를 금지하는 대안은 가방 가득 참·창 닫기 안전망까지 막으므로 기각한다. 입력 경계에서 거부하고 원본 물건·수량·커서와 회수 가능성을 실제 클릭으로 확인한다.
"""
p = game / "docs/design/ui_v2.md"
body = p.read_text(encoding="utf-8")
assert f"## #{card} " not in body
p.write_text(body + "\n\n" + spec, encoding="utf-8", newline="\n")
paths = sorted((game / "data/items").glob("*.tres")) + sorted((game / "assets/sprites/ui/icons_a/items").glob("*.png")) + sorted((game / "assets/sprites/ui/icons_a/skills").glob("*.png"))
snapshot = {p.relative_to(game).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert len(snapshot) == 105, len(snapshot)
(report / "before_snapshot.json").write_text(json.dumps({"base":ctx["game_base"], "files":snapshot}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
p = game / "tests/e2e/scenarios/icon_intake.gd"
body = p.read_text(encoding="utf-8")
assert "func _quest_cursor_guards(" not in body
head, seal = body.split("func _seal_review() -> void:", 1)
seal = seal.replace('\tvar before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()', '\tvar before: bool = "--icon-intake-before" in OS.get_cmdline_user_args()\n\tvar safety_before: bool = "--quest-safety-before" in OS.get_cmdline_user_args()', 1)
for shot, selling in [("seal_inventory", False), ("seal_vendor_refused", True), ("seal_drop_recovered", False)]:
    needle = f'\tawait t.shot("{shot}")'
    assert needle in seal
    seal = seal.replace(needle, f'\t_quest_tooltip_rules(tip, safety_before, {str(selling).lower()})\n' + needle, 1)
needle = '\tvar floor_before: int = t.tree.get_nodes_in_group("floor_item").size()'
assert needle in seal
seal = seal.replace(needle, '\tawait _quest_cursor_guards(specimens, safety_before)\n' + needle, 1)
assert seal.endswith('\tawait t.close_all()\n')
seal += '\tawait _quest_safety_fallbacks(specimens)\n'
body = head + "func _seal_review() -> void:" + seal + "\n\n" + (main / "tmp/quest_guard_fixture.gd").read_text(encoding="utf-8")
p.write_text(body, encoding="utf-8", newline="\n")
print(f"PASS #{card}: specification first, protected105 assets/definitions, real-input before/after fixture. Runtime still unchanged.")
