from pathlib import Path
import hashlib
import json
import re
import runpy
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/t2_sword_context.json").read_text(encoding="utf-8"))
assert ctx["status"] == "started"
card = ctx["card"]
game, assets, root, report = [Path(ctx[k]) for k in ["game", "assets", "production", "report"]]
root.mkdir(parents=True, exist_ok=True)
def put(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8", newline="\n")
def dump(path, value):
    put(path, json.dumps(value, ensure_ascii=False, indent=2)+"\n")
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

common = """Use case: stylized-concept.
Asset: ONE physical sword inventory icon for Joseon Hunters, a fictional Korean Joseon dark-fantasy ARPG. The item occupies a very narrow 1 by 3-cell vertical inventory footprint, displayed at only 40 by 120 pixels. Make a tall portrait composition with the pommel and grip at the TOP and blade point at the BOTTOM. The complete sword must be fully visible, almost vertical, centered, with clean transparent margins; no strongly diagonal pose. A slight three-quarter view may reveal blade thickness, but preserve the narrow upright silhouette.
Input images: image 1 is the accepted hwando sword, image 2 the accepted yedo sword. These are STYLE REFERENCES ONLY, not edit targets. Match their mature hand-painted inventory-object rendering, worn pale steel, quiet desaturated warm bronze fittings, dark cloth grip, warm upper-left light and controlled broad edge highlights. Do not copy the exact sword design, gray halo, dark backdrop, or cast shadow from a reference.
Style: a Diablo II Resurrected-like independent painted object with restrained, believable material and softly worn craftsmanship, adapted to a fictional Korean Joseon setting. Dark-fantasy value range, slightly weathered metal, substantial blade faces, small subdued cloth accents. The blade must stay visible on a nearly black brown inventory slot through broad pale metal planes, without an outline effect. No cartoon, flat vector symbol, pixel art, glossy product photography, chrome glare, exaggerated ornament or Western fantasy crossguard.
Background: genuinely TRANSPARENT with a real alpha channel. No scenery, ground plane, solid or checkerboard backdrop, gradient vignette, fog, or shadow outside the object. Exactly one complete sword, no scabbard, sheath, second blade, stand, hands or human figure. No UI border, badge, labels, lettering, readable inscriptions, watermark, magic aura, emissive glow, sparks, blood, or extra props. Design differences must be structural, not merely color swaps. Leave the steel edge readable at the real 40px-wide display size.
"""
subjects = [
    ("bongukgeom", "본국검", "균형 잡힌 곧은 날 · 짧은 손잡이", """Subject: Bongukgeom, the balanced practical T2 sword. One moderately broad, nearly straight steel blade with a clean gradual taper, a restrained central ridge and a strong point, slightly broader and more substantial than a fast saber. Compact flattened oval aged-bronze guard, short dark charcoal cloth-wrapped single-hand grip and a simple low bronze pommel. A small faded russet knot tightly attached to the pommel, with no long dangling tassel. The balanced blade occupies about three-quarters of the total length. Worn steel-gray planes and a pale edge form the main shape; simple warm fittings remain secondary. Calm sturdy Korean sword craft, no elaborate royal filigree or enormous guard. This is a fictional game design interpretation, not an archaeological reconstruction."""),
    ("jedokgeom", "제독검", "가늘고 살짝 휘는 빠른 날", """Subject: Jedokgeom, the faster and more agile T2 sword. ONE visibly slender single-edged steel blade with a gentle, restrained continuous curve and a fine tapering point. The blade should look narrow and light compared with a balanced straight sword. Short compact grip wrapped in very dark muted brown-red cloth, a small rounded dark bronze guard, and a discreet bronze end cap; one tightly folded faded vermilion tie no longer than the guard width. The narrow curved blade and its long pale sharpened edge are the dominant readable feature. Keep the guard and knot small so the sword retains nearly its full length in a 1 by 3 inventory footprint. Mature worn Korean dark-fantasy craft, no Japanese decorative motifs, Western crossguard, broad cleaver profile, large tassel or ornate ritual engraving. This is a fictional game design interpretation."""),
    ("ssangsudo", "쌍수도", "긴 양손 손잡이 · 넓고 묵직한 날", """Subject: Ssangsudo, a heavy TWO-HANDED T2 sword, represented by EXACTLY ONE sword, never a pair. A conspicuously long two-hand grip, about one-third of the complete object's length, wrapped in charcoal black cloth with a simple aged-bronze pommel and a small compact oval guard. The grip must visibly accommodate two hands, contrasting clearly with the other short-grip swords. One broad, heavy single-edged steel blade with a nearly straight spine, a very slight forward curve near the lower third and a stout tapered tip; blade width and long grip create the readable identity. Strong cool gray faces, pale broad worn cutting edge, darkened spine and a few quiet brown patina patches. Minimal fittings, no tassel or hanging cloth, no huge crossguard, no serrations, spikes or double weapons. Keep the complete long sword upright and fully contained in the narrow portrait composition. Fictional Korean Joseon sword craft, mature painted dark fantasy."""),
    ("saingeom", "사인검", "곧은 양날 · 절제된 의장 금속", """Subject: Saingeom, the base T2 ritual/ceremonial sword, distinct from the separate unique Sainchamsageom. One straight, slender double-edged steel blade with a clean symmetrical taper and central ridge. A compact flattened oval guard and rounded pommel of weathered warm brass/bronze, slightly richer than a practical sword but kept small and restrained; short single-hand grip wrapped in deeply muted reddish-black cloth. A discreet line of a few tiny non-letter constellation-like dots and faint incised connections on part of the blade can suggest ritual craft, never a readable inscription, luminous rune or bright magic effect. The broad pale steel planes carry readability; the aged brass fitting and dark red grip quietly identify the ritual version. One very short muted vermilion knot close to the pommel. No royal crown emblem, gem, Western crossguard, huge dragon carving, extravagant gold plating or trailing tassel. This is a fictional Korean dark-fantasy ceremonial sword interpretation, not a claim of historical accuracy."""),
]
catalog = json.loads((assets / "workbench/production/item_icons_446/catalog_274.json").read_text(encoding="utf-8"))
items = []
for id, name, shape, subject in subjects:
    e = dict(next(x for x in catalog["core_missing"] if x["item_id"] == id))
    e.update(definition_path=(game / f"data/items/{id}.tres").as_posix(), silhouette=shape, prompt=common+"\n"+subject, max_stack=1, quest_item=False, two_handed=id=="ssangsudo")
    text = Path(e["definition_path"]).read_text(encoding="utf-8")
    assert f'display_name = "{name}"' in text and "size = Vector2i(1, 3)" in text and "tier = 2" in text
    assert "icon = ExtResource" in text and e["output_width"] == 80 and e["output_height"] == 240
    assert ("two_handed = true" in text) == e["two_handed"]
    items.append(e)
inputs = {"card":card, "parent_card":274, "scope":"four implemented T2 sword bases inside core73", "core_remaining_before":55, "core_remaining_if_all_approved":51, "items":items}
dump(root / "inputs.json", inputs)
dump(main / "tmp/t2_sword_inputs.json", inputs)
dump(root / "manifest.json", {"card":card, "parent_card":274, "status":"before_generation", "items":items})
put(root / "PROMPTS.md", f"# #{card} 실제 생성 프롬프트\n\n내장 image_gen · 투명 배경 · 4개 독립 호출. 환도·예도는 화풍 참고이며 수정 대상이 아니다.\n\n"+"\n\n".join("## "+e["display_name"]+" / "+e["item_id"]+"\n\n"+e["prompt"] for e in items)+"\n")

builder = (assets / "workbench/production/item_icons_454/prepare_assets.py").read_text(encoding="utf-8").replace("454",str(card))
builder = builder.replace("originals3", "originals4").replace("edges3", "edges4").replace("PNG3", "PNG4").replace("footprints3", "footprints4").replace("SHA3", "SHA4").replace("items3/footprints4/names3/render3", "items4/footprints4/names4/render4")
start, end = builder.index("def contact("), builder.index("GDSCRIPT =")
contact = '''def contact(root: Path, manifest: dict) -> None:
    sheet = Image.new("RGB", (1280, 720), (25, 23, 21))
    draw = ImageDraw.Draw(sheet)
    draw.text((26, 17), "D1 T2 검 4종 · #CARD", font=font(26), fill=(228, 216, 192))
    draw.text((26, 55), "확대 원화 + 40×120px 파일 축소 · 1×3칸 · 후보 / 게임 미반입", font=font(17), fill=(160, 150, 130))
    for i, e in enumerate(manifest["items"]):
        x, y = 22 + i * 314, 96
        draw.rectangle((x, y, x + 299, y + 588), fill=(31, 28, 24), outline=(77, 67, 52))
        raw = Image.open(root / "source/items" / (e["item_id"] + ".png")).convert("RGBA").crop(tuple(e["source_bbox"]))
        raw.thumbnail((160, 410), Image.Resampling.LANCZOS)
        sheet.paste(raw, (x + 100 - raw.width // 2, y + 219 - raw.height // 2), raw)
        draw.text((x + 209, y + 95), "40×120", font=font(13), fill=(175, 162, 143))
        draw.rectangle((x + 222, y + 125, x + 261, y + 244), fill=(23, 21, 19), outline=(101, 84, 66))
        art = Image.open(root / "game/items" / (e["item_id"] + ".png")).convert("RGBA").resize((40, 120), Image.Resampling.LANCZOS)
        sheet.paste(art, (x + 222, y + 125), art)
        draw.text((x + 16, y + 441), e["display_name"], font=font(22), fill=(229, 215, 190))
        draw.text((x + 16, y + 478), e["silhouette"], font=font(14), fill=(175, 162, 143))
        draw.text((x + 16, y + 518), "손잡이 위 · 검 끝 아래", font=font(15), fill=(155, 147, 131))
        draw.text((x + 16, y + 554), e["item_id"] + " · 80×240 RGBA", font=font(14), fill=(155, 147, 131))
    path = root / "qa"
    path.mkdir(parents=True, exist_ok=True)
    sheet.save(path / "overview.png", optimize=True)
    sheet.save(path / "overview.jpg", quality=85, optimize=True)


'''.replace("CARD", str(card))
builder = builder[:start]+contact+builder[end:]
start, end = builder.index("\tfunc _draw() -> void:"), builder.index("var out_dir :=")
draw = '''\tfunc _draw() -> void:
\t\tdraw_rect(Rect2(Vector2.ZERO, dimensions), Color("211d19"))
\t\tvar title := "기존 그림" if mode == "before" else "후보 그림"
\t\tif mode == "sizes": title = "30·48·60px 칸 크기 검수"
\t\tlabel(Vector2(26, 36), "D1 T2 검4종 · " + title, 24, true)
\t\tlabel(Vector2(26, 65), "실제 공통 UiSkin · 현재 1×3칸/쌓기1 정의 · 후보는 검수 메모리에서만 사용", 15)
\t\tif mode == "sizes":
\t\t\tfor i in rows.size():
\t\t\t\tvar row: Dictionary = rows[i]
\t\t\t\tvar x := 28 + i * 310
\t\t\t\tlabel(Vector2(x, 104), row.spec.display_name, 20, true)
\t\t\t\tfor j in 3:
\t\t\t\t\tvar side: int = [30, 48, 60][j]
\t\t\t\t\tvar y: int = [132, 260, 438][j]
\t\t\t\t\tobject_at(Rect2(x + 130, y, side, side * 3), row, true)
\t\t\t\t\tobject_at(Rect2(x + 225, y, side, side * 3), row, true, true)
\t\t\t\t\tlabel(Vector2(x + 2, y + 25), "%dpx/칸" % side, 16)
\t\t\tlabel(Vector2(28, 682), "각 크기: 실제 슬롯 / 검정 · 30px의 문양·감김 세부는 판독 한계가 있음", 15)
\t\t\treturn
\t\tlabel(Vector2(28, 166), "현재40px/칸", 15)
\t\tlabel(Vector2(28, 342), "검정40px/칸", 15)
\t\tfor i in rows.size():
\t\t\tvar row: Dictionary = rows[i]
\t\t\tvar x := 110 + i * 290
\t\t\tlabel(Vector2(x, 112), row.spec.display_name, 21, true)
\t\t\tlabel(Vector2(x, 138), "1×3칸 · T2 검", 15)
\t\t\tobject_at(Rect2(x + 90, 180, 40, 120), row, mode != "before")
\t\t\tobject_at(Rect2(x + 90, 350, 40, 120), row, mode != "before", true)
\t\tlabel(Vector2(28, 505), "같은 화풍 기준 · 기존 채택 D1", 18, true)
\t\tfor i in references.size():
\t\t\tvar row: Dictionary = references[i]
\t\t\tvar w: float = row.spec.grid_w * 40
\t\t\tvar h: float = row.spec.grid_h * 40
\t\t\tvar x := 340 + i * 250
\t\t\tobject_at(Rect2(x, 530, w, h), row, false)
\t\t\tlabel(Vector2(x, 688), row.spec.display_name, 15)

'''
builder = builder[:start]+draw+builder[end:]
builder = builder.replace('assert(definition.icon == null, "candidate current icon must be unspecified")', 'assert(definition.icon != null, "existing H1 icon must be preserved")')
builder = builder.replace('assert(definition.quest_item and definition.max_stack == 1, "quest/stack mismatch")', 'assert(not definition.quest_item and definition.max_stack == 1, "quest/stack mismatch")\n\t\tassert(definition.tier == 2 and definition.slot == 0, "T2/weapon mismatch")\n\t\tassert(definition.two_handed == spec.two_handed, "two-handed contract mismatch")')
builder = builder.replace('["paeraengi", "leather_shoes", "cotton_belt"]','["hwando", "yedo", "leather_shoes"]')
assert "items4/footprints4/names4/render4" in builder
put(root / "prepare_assets.py", builder)
put(root / "qa_godot.gd", runpy.run_path(str(root / "prepare_assets.py"))["GDSCRIPT"])

files = sorted((game / "data/items").glob("*.tres")) + sorted((game / "assets/sprites/ui/icons_a/items").glob("*.png")) + sorted((game / "assets/sprites/ui/icons_a/skills").glob("*.png"))
snapshot = {}
for path in files:
    rel = path.relative_to(game).as_posix()
    a, b = path.read_bytes(), (main / rel).read_bytes()
    assert (a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n") if rel.endswith(".tres") else a == b), rel
    snapshot[rel] = sha(path)
assert len(snapshot) == 105
old_icons = {e["current_icon"].removeprefix("res://") for e in items}
dump(root / "current_game_snapshot.json", {"game_commit":ctx["game_base"], "files":snapshot, "old_h1_icons":{rel:sha(game / rel) for rel in sorted(old_icons)}})
refs = {
    "accepted_hwando.png":assets / "workbench/production/ui_icon_redesign_2026-09-23/individual/source/items/hwando.png",
    "accepted_yedo.png":assets / "workbench/production/item_icons_446/source/items/yedo.png",
}
reference_hashes = {}
for name, src in refs.items():
    dest = root / "references" / name
    dest.parent.mkdir(exist_ok=True)
    shutil.copy2(src, dest)
    assert sha(dest) == sha(src)
    reference_hashes[name] = sha(src)
dump(root / "reference_hashes.json", reference_hashes)
brief = f"""# D1 T2 검4종 (#{card} · 부모 #274)

## 1. 범위와 규격

정본 item_catalog_v2 §1.1·item_system_v2 §4.2·§17 및 현재 ItemDef4종. 본국검(bongukgeom)·제독검(jedokgeom)·쌍수도(ssangsudo)·사인검(saingeom)은 이미 구현된 T2 검이며 옛 H1 공용 그림을 재사용한다. 모두 논리1×3칸/40×120px, 후보80×240 RGBA. 기존 가격·스탯·점유·쌓기1·무기 슬롯·도호 조건·쌍수도의 two_handed=true를 보존한다. 현재 #274핵심잔여55 중4종; 후보일 때55, 전부 채택되면51이다. 사인검은 별도 유니크 사인참사검이 아니다.

## 2. 판독 형태

| id | 이름 | 제작 해석 |
|---|---|---|
| bongukgeom | 본국검 | 균형 잡힌 곧은 날·짧은 검은 손잡이·작은 둥근 코등이 |
| jedokgeom | 제독검 | 더 가늘고 살짝 휘는 빠른 날·작은 코등이·짧은 붉은 묶음 |
| ssangsudo | 쌍수도 | 검1자루·길게 드러난 양손 손잡이·넓고 묵직한 날 |
| saingeom | 사인검 | 곧은 양날·절제된 낡은 놋쇠 의장 금속·비문자 점각 |

세부 형태·재질·장식은 가공 조선의 아이콘 제작 해석이다. 별도의 고증·로어·수치 락을 만들지 않는다. 손잡이 위·검 끝 아래 세로 구도, 윗왼쪽 빛, 회색 철의 넓은 명암과 절제된 주홍·황동으로 채택 환도·예도 D1 독립 물체 화풍을 따른다. 장식이 커져 검이 가방 칸에서 줄어들지 않게 하고 단일 검·진짜 투명 알파·프레임/발광/문자 없음으로 제작한다.

## 3. 생산과 검수

내장 image_gen 물건별 독립4회, 환도·예도 원화2장은 화풍 참고이며 수정 대상이 아니다. 생성 결과는 즉시 대화에 표시하고 원본은 바이트 그대로 자산 source/items, 프롬프트·입력·참조·경로·SHA를 함께 보존한다. 기존 alpha16/8%여백/Lanczos 패킹으로80×240 후보를 만든다. 생성 전 현재 UiSkin 비교판을 저장한다. 실제 공통 UiSkin.item_slot/item_icon과 궁서 제목의40×120·검정·30/48/60px칸 렌더에서 판독·알파·여백을 확인한다. 현재 정의67·채택PNG38=105파일과 옛 H1검PNG3의 SHA, 승인 환도·예도·가죽신3영역 픽셀을 보존한다. main의 기존3정의 LF/CRLF 차이는 정규화 내용으로 대조하고 재작성하지 않는다. JPG4(1280폭·각300KB이하)는 게임 docs/art, 원본/전체 raw는 자산 reports/{card}이다. 실제 게임 설치와 플레이 검수는 원화 채택 뒤 별도 카드다.

## 4. 왜 이 구조인가

날 폭·곡률·손잡이 길이·의장 금속의 차이를 독립 원화로 만들면 작은 세로 가방 칸에서도 네 무기를 구분할 근거가 생긴다. 같은 공용 검을 색만 바꾸는 대안은 무기별 차이를 지우므로 기각한다. 후보를 실제 UiSkin 검수 프로세스 메모리에만 올려 현재 게임의 수치·그림을 보존하면서 비교 가능한 판정물을 만든다. 실행 코드가 같으므로 전체 플레이 회귀를 새로 반복하지 않고 자산·공통 렌더·현재 파일·문서 예산을 검증한다.
"""
put(root / "BRIEF.md", brief)
put(game / f"docs/design/item_icons_{card}.md", brief)
put(root / "README.md", f"# #{card} D1 T2 검4종 후보\n\n사양 BRIEF.md, 프롬프트 PROMPTS.md, 현재105파일 보존 current_game_snapshot.json. 내장 image_gen으로 독립 생성, 실제 게임 미반입.\n")
(root / "source/items").mkdir(parents=True, exist_ok=True)
(root / "qa").mkdir(exist_ok=True)
ctx["status"] = "prepared"
dump(main / "tmp/t2_sword_context.json", ctx)
print(f"#{card} spec/prompts prepared; protected105 current files +3 H1 icons; references2 copied unchanged")
