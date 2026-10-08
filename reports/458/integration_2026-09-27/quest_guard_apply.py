from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
p = game / "ui/inventory_ui.gd"
body = p.read_text(encoding="utf-8")
old = '\tif i >= 0:\n\t\tbar.belt_click(i, MOUSE_BUTTON_LEFT)\n\telse:\n\t\t_drop_held()'
new = '\tif i >= 0:\n\t\tbar.belt_click(i, MOUSE_BUTTON_LEFT)\n\telse:\n\t\tif held != null and not held.def.can_discard():\n\t\t\tshow_msg("퀘스트 물건은 버릴 수 없다")\n\t\t\treturn\n\t\t_drop_held()'
assert body.count(old) == 1
body = body.replace(old, new, 1)
body = body.replace('아니면 바닥에 버린다.', '아니면 버릴 수 있는 일반 물건만 바닥에 버린다.', 1)
body = body.replace('아니면 예전처럼 바닥에.', '아니면 일반 물건만 바닥에. 퀘스트는 커서에 유지한다.', 1)
p.write_text(body, encoding="utf-8", newline="\n")
p = game / "ui/tooltip_content.gd"
body = p.read_text(encoding="utf-8")
assert body.count('\telif selling:\n') == 1
body = body.replace('\telif selling:\n', '\telif selling and it.def.can_discard():\n', 1)
old = '\t\t\thints.append("좌클릭: 들기 · 들고 창 밖 클릭: 버림")'
new = '\t\t\tif it.def.can_discard():\n\t\t\t\thints.append("좌클릭: 들기 · 들고 창 밖 클릭: 버림")\n\t\t\telse:\n\t\t\t\thints.append("좌클릭: 들기")\n\t\t\t\thints.append("퀘스트 물건 · 팔기·버리기 불가")'
assert body.count(old) == 1
body = body.replace(old, new, 1)
p.write_text(body, encoding="utf-8", newline="\n")
p = game / "tests/test_item_ui.gd"
body = p.read_text(encoding="utf-8")
assert '\t_quest_tooltips()\n' not in body
body = body.replace('\t_tooltip()\n', '\t_tooltip()\n\t_quest_tooltips()\n', 1)
body += '''

## #458: 퀘스트/일반 물건의 가방·판매 문맥을 구별하며 정의·수량을 바꾸지 않는다.
func _quest_tooltips() -> void:
	var tips: GDScript = load("res://ui/tooltip_content.gd")
	for id in ["seal_heukrang", "seal_jangsanbeom", "seal_bulgasari"]:
		var it := ItemInstance.create(ItemDb.get_def(id))
		var snapshot := it.to_dict()
		var price: int = it.def.price
		for selling in [false, true]:
			var rows: Array[Dictionary] = tips.item(it, {"surface": "bag", "selling": selling})
			_check(rows.all(func(row: Dictionary) -> bool: return row.role != "price"), "%s 판매 문맥 %s: 퀘스트 판매가 없음" % [id, selling])
			var hints := ""
			for row in rows:
				if row.role == "hint":
					hints += String(row.text) + "\\n"
			_check(hints.contains("좌클릭: 들기") and hints.contains("퀘스트 물건 · 팔기·버리기 불가"), "%s 들기·판매/버림 불가 안내" % id)
			_check(not hints.contains("클릭: 버림") and not hints.contains("클릭: 판매") and not hints.contains("모두 판매"), "%s 불가능한 조작 안내 없음" % id)
		_check(it.to_dict() == snapshot and it.def.price == price and it.def.quest_item, "%s 툴팁이 물건·가격·퀘스트 정의를 바꾸지 않음" % id)
	var normal := ItemInstance.create(ItemDb.get_def("hp_potion"), 3)
	var rows: Array[Dictionary] = tips.item(normal, {"surface": "bag", "selling": true})
	_check(rows.any(func(row: Dictionary) -> bool: return row.role == "price" and row.text == "판매가 %d 엽전 (3개 전부)" % Vendor.sell_price(normal)), "일반 물약3 판매가·전체 수량 표시 유지")
	_check(rows.any(func(row: Dictionary) -> bool: return row.role == "hint" and String(row.text).contains("모두 판매")) and rows.any(func(row: Dictionary) -> bool: return row.role == "hint" and String(row.text).contains("들고 창 밖 클릭: 버림")), "일반 물건 판매·창 밖 버림 안내 유지")
	_check(normal.stack == 3 and normal.def.can_discard(), "일반 물건 툴팁 뒤 수량·버릴 수 있음 보존")
'''
p.write_text(body, encoding="utf-8", newline="\n")
p = game / "docs/design/item_system_v2.md"
body = p.read_text(encoding="utf-8")
old = '`InventoryUi._sell`·Ctrl+클릭 버림 두 곳만 막는다 —'
new = '`InventoryUi._sell`·Ctrl+클릭 버림·커서에 든 채 창 밖 좌클릭 버림을 막는다(#458). 툴팁도 팔기·버리기 불가를 안내하고 판매가는 숨긴다 —'
assert body.count(old) == 1
p.write_text(body.replace(old, new, 1), encoding="utf-8", newline="\n")
print("Applied explicit quest discard guard, truthful tooltip and existing unit regressions; closing/full-bag fallback unchanged.")
