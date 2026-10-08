from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
from PIL import Image, ImageChops

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/t2_sword_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
game, assets, root, report = [Path(ctx[k]) for k in ["game","assets","production","report"]]
gallery = game / f"docs/art/{card}_d1_t2_swords"
gallery.mkdir(parents=True, exist_ok=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body,encoding="utf-8",newline="\n")
def dump(path, value):
    put(path,json.dumps(value,ensure_ascii=False,indent=2)+"\n")

manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
snapshot = json.loads((root / "current_game_snapshot.json").read_text(encoding="utf-8"))
sources = json.loads((root / "generation_sources.json").read_text(encoding="utf-8"))
commands = json.loads((report / "render_commands.json").read_text(encoding="utf-8"))
assert len(manifest["items"]) == 4 and manifest["status"] == "candidate_not_installed"
assert len(snapshot["files"]) == 105
main_raw_same, main_eol_only = [], []
for rel,digest in snapshot["files"].items():
    assert sha(game / rel) == digest, rel
    a,b = (game / rel).read_bytes(),(main / rel).read_bytes()
    if a == b:
        main_raw_same.append(rel)
    else:
        assert rel.endswith(".tres") and a.replace(b"\r\n",b"\n") == b.replace(b"\r\n",b"\n"), rel
        main_eol_only.append(rel)
for rel,digest in snapshot["old_h1_icons"].items():
    assert sha(game / rel) == sha(main / rel) == digest
for name,digest in json.loads((root / "reference_hashes.json").read_text(encoding="utf-8")).items():
    assert sha(root / "references" / name) == digest
definitions = [r for r in snapshot["files"] if r.endswith(".tres")]
pngs = [r for r in snapshot["files"] if r.endswith(".png")]
current_items = [r for r in definitions if 'script_class="ItemDef"' in (game / r).read_text(encoding="utf-8")]
pending = [Path(r).stem for r in current_items if "icon =" not in (game / r).read_text(encoding="utf-8")]
assert len(definitions) == 67 and len(pngs) == 38 and len(current_items) == 66 and not pending
before_cmd = next(e for e in commands if e["mode"] == "before")
for e in manifest["items"]:
    assert e["game_size"] == [80,240] and e["source_size"] == [724,2172]
    assert e["source_alpha"] == [0,255] and e["packed_alpha"] == [0,255]
    id = e["item_id"]
    src = next(x for x in sources["items"] if x["item_id"] == id)
    assert sha(root / "source/items" / f"{id}.png") == e["source_sha256"] == src["original_sha256"]
    assert sha(root / "game/items" / f"{id}.png") == e["game_sha256"]
    prompt = e.get("edit_prompt",e["prompt"])
    assert hashlib.sha256(prompt.encode("utf-8")).hexdigest() == src["prompt_sha256"]
    assert sha(Path(src["generated_path"])) == src["original_sha256"]
    assert Path(src["generated_path"]).stat().st_mtime > before_cmd["started_epoch"]
    assert not (game / "assets/sprites/ui/icons_a/items" / f"{id}.png").exists()
    assert not (main / "assets/sprites/ui/icons_a/items" / f"{id}.png").exists()
edited = next(x for x in sources["items"] if x["item_id"] == "saingeom")
assert edited["revision"] == 2 and sha(Path(edited["preserved_edit_target"])) == edited["edit_target_sha256"]
assert sha(Path(edited["initial_generation"]["generated_path"])) == edited["edit_target_sha256"]
assert Path(edited["initial_generation"]["generated_path"]).stat().st_mtime > before_cmd["started_epoch"]

before = Image.open(root / "qa/godot_before.png").convert("RGB")
after = Image.open(root / "qa/r2/godot_after.png").convert("RGB")
anchors = {"hwando":(340,530,380,650),"yedo":(590,530,630,650),"leather_shoes":(840,530,920,610)}
for id,box in anchors.items():
    assert ImageChops.difference(before.crop(box),after.crop(box)).getbbox() is None,id
# Only the revised sword may differ from the first candidate render.
first = Image.open(root / "qa/godot_after.png").convert("RGB")
unchanged_candidates = {}
for i,id in enumerate(["bongukgeom","jedokgeom","ssangsudo"]):
    x = 200+i*290
    for y in [180,350]:
        box = (x,y,x+40,y+120)
        assert ImageChops.difference(first.crop(box),after.crop(box)).getbbox() is None,id
    unchanged_candidates[id] = "both real and black slot pixels identical after saingeom edit"
for mode, suffix in [("before",""),("after","_r2"),("sizes","_r2")]:
    raw = (report / f"{card}_godot_{mode}{suffix}.log").read_bytes()
    body = raw.decode("utf-8")
    assert f"GODOT_D1_{card} PASS" in body and "ERROR:" not in body and "SCRIPT ERROR" not in body
    command = next(e for e in commands if e["mode"] == mode and e.get("revision","") == suffix.removeprefix("_"))
    assert hashlib.sha256(raw).hexdigest() == command["raw_sha256"]

review = []
mapping = {"overview.jpg":"overview.png","ui_before.jpg":"godot_before.png","ui_after.jpg":"r2/godot_after.png","ui_sizes.jpg":"r2/godot_sizes.png"}
for dest,src in mapping.items():
    im = Image.open(root / "qa" / src).convert("RGB")
    assert im.size == (1280,720)
    target = gallery / dest
    im.save(target,quality=85,optimize=True)
    assert target.stat().st_size <= 300000
    shutil.copy2(target,root / "qa" / dest)
    shutil.copy2(root / "qa" / src,report / src.split("/")[-1])
    review.append({"file":dest,"dimensions":[1280,720],"bytes":target.stat().st_size,"sha256":sha(target)})

qa = f"""# #{card} D1 T2 검4종 검수

기준 게임 `{ctx['game_base']}`·자산 `{ctx['assets_base']}`. 내장 image_gen으로 독립 생성4회와 사인검 판독 보정1회(총5호출)를 진행했다. 최종 원본4장은724×2172 RGBA·실제 알파0~255, 생성 파일과바이트 동일하다. 원본을 그대로 source/items에 보존하고 기존 alpha16/8%여백/Lanczos 패킹으로80×240 RGBA 후보4장을 만들었다. 실제 프롬프트는 PROMPTS.md·EDIT_SAINGEOM.txt, 경로/역할/해시는 generation_sources.json·manifest.json이다. 환도·예도는 화풍 참고이며 수정 대상이 아니고, 마지막 호출의 첫 입력만 사인검 편집 대상이다.

| 물건 | 직접 시각 검수 |
|---|---|
| 본국검 | 곧은 날·짧은 검은 손잡이·작은 타원 코등이. 실용적인 좁은 철 면 |
| 제독검 | 완만하게 휘는 긴 날·짧은 붉은 손잡이. 곡률이 실제40px칸에서도 보임 |
| 쌍수도 | 검1자루·길게 드러난 양손 손잡이·묵직한 날. 손잡이 길이가 짧은 검과 구별됨 |
| 사인검 r2 | 더 넓은 양날·중앙 능선·낮은 사각 놋쇠 코등이. 최초 r1은 본국검과 비슷해 실제 슬롯 판독 보정 |

40×120 슬롯에서 날·손잡이·주요 명암이 남고 어두운 슬롯과 검정에서 칼날이 보인다. 사인검의 넓은 면은 보정 전보다 본국검과 차이가 커졌다. 다만30px칸에서는 감김/문양/별자리 점각의 세부가 거의 사라지고, 본국검·사인검의 작은 장식만으로 즉시 구분하기에는 한계가 있다. 아이콘만으로 이름을 완전히 식별한다는 보장은 하지 않는다. 사인검 장식은 확대 원화에서 의미가 있고 실제칸에서는 날폭·넓은 명암이 주 정보다. 생성 보정은 요청보다 하단 테이퍼가 완만하며 게임 아이콘용 제작 해석으로 판정한다. 고증 사실을 새로 정하지 않는다.

overview.jpg는 원화 확대와40×120 **파일 축소**다. ui_before.jpg/ui_after.jpg는 같은 구도의 **실제 Godot UiSkin.item_slot/item_icon 렌더**이며 현재 가방과 같은 padding8,40px칸/검정칸을 비교한다. ui_sizes.jpg는30/48/60px칸(각1×3) 실제 렌더다. 처음 before를 원화 생성 전에 저장했다. 후보는 ImageTexture.take_over_path로 짧은 검수 프로세스 메모리에만 올리고 실제 게임 PNG나ItemDef를 설치하지 않았다. 가방 전체를 플레이한 결과로 보아서는 안 된다.

검증: 원본/패킹4 알파·여백·크기·SHA PASS, 현재 정의67(ItemDef66+인덱스)/채택PNG38=105파일 WT rawSHA 동일. 본진은{len(main_raw_same)}raw동일+{len(main_eol_only)}기존LF/CRLF차이뿐이며 정의 정규화 내용은105파일 모두동일; 해당3파일을 재작성하지 않았다. 옛 H1공용검PNG3·화풍참조2 원본도SHA 동일. 기준 환도·예도·가죽신3영역 전후픽셀 동일, 사인검 보정 전후 다른3후보의 일반/검정6영역 픽셀 동일. Godot before/final-after/final-sizes 모두PASS·SCRIPT ERROR/ERROR0. 원화 독립4+보정1의경로·해시, 실행5회(최초3+보정후2) 명령/raw/캡처·r1원본은 자산 reports/{card}/2026-09-27에보존했다. 문서예산 PASS, JPG4모두1280×720·각300KB이하·합{sum(x['bytes'] for x in review)}B.

실제 게임·수치·점유·쌓기·가격·모델·애니·퀘스트 규칙 변경 없음. 쌍수도는 기존two_handed=true를 유지했다. 실행 코드가 동일하므로 전체 플레이 회귀검사는 새로 반복하지 않았으며, 자산·현재파일·공유렌더·문서검사 결과만 기록한다. 원화 채택 뒤 별도 카드로 실제가방/착용/좌판/드랍 게임반입을 검수한다. 현재는미채택후보/미착륙/미push. #274핵심잔여55 유지,4종전부채택시51이다.

왜 이 구조인가: 날폭·곡률·손잡이길이·코등이형태를 각각 나눠 작은 세로 가방 칸에 무기별 차이를 남긴다. 공용검을 색만바꾸는 대안은 형태를 공유해 판독차이가 줄어들므로 기각했다. 실제UiSkin 메모리렌더와현재파일보존 검증으로 데이터를 바꾸지않고 채택할 수 있는 후보를 만든다. 사양 docs/design/item_icons_{card}.md, 자산 BRIEF.md다.
"""
put(gallery / "QA.md",qa)
put(root / "QA.md",qa)
put(gallery / "README.md",f"# #{card} D1 T2 검4종 후보\n\n본국검·제독검·쌍수도·사인검(r2). overview.jpg는 원화 확대/40×120파일축소, ui_before.jpg·ui_after.jpg는 같은 구도 실제공통UiSkin, ui_sizes.jpg는30/48/60px칸. 검증·한계는QA.md. 실제게임미반입·PD판정대기.\n")
put(root / "README.md",f"# #{card} D1 T2 검4종 후보\n\n내장image_gen독립4+사인검편집1. 원본 source/items(724×2172RGBA)·game/items(80×240RGBA), PROMPTS.md·EDIT_SAINGEOM.txt·generation_sources.json·manifest.json에 호출/참조/해시. 최종qa/overview.jpg·ui_before.jpg·ui_after.jpg·ui_sizes.jpg, QA.md에 검증·한계. 첫사인검과첫검수판은 reports/{card}/2026-09-27/iterations/r1 보존. 실제게임미반입·핵심잔여55·미push.\n\n재현: python prepare_assets.py로패킹/확대판, Godot --path=<게임> -s=<qa_godot.gd> -- --root=<이폴더> --mode=<before|after|sizes> --out=<출력폴더>. 현재 정의·공통UiSkin만 읽고 후보는검수메모리에서만사용. 독립4프롬프트·사인검수정문을도구의실제호출과같이보존했다.\n")
env = dict(os.environ)
env["PYTHONIOENCODING"] = "utf-8"
p = subprocess.run([sys.executable,"tools/doc_budget.py"],cwd=game,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(report / f"{card}_doc_budget.log").write_bytes(p.stdout)
print(p.stdout.decode("utf-8",errors="replace"))
p.check_returncode()
verification = {"card":card,"parent":274,"status":"candidate_not_installed","core_remaining":55,"if_all_four_approved":51,"built_in_generations":4,"built_in_edits":1,"selected_saingeom_revision":2,"current_definition_files_preserved":67,"current_ItemDefs_preserved":66,"current_png_files_preserved":38,"current_game_files_raw_preserved":105,"main_files_raw_equal":len(main_raw_same),"main_preexisting_eol_only":main_eol_only,"main_content_equal":105,"old_h1_icons_preserved":3,"style_references_preserved":2,"current_icon_pending":pending,"approved_anchor_regions_preserved":list(anchors),"unchanged_candidates_after_edit":unchanged_candidates,"godot_final_modes_passed":["before","after_r2","sizes_r2"],"godot_total_runs":len(commands),"final_script_engine_errors":0,"doc_budget_exit":0,"gallery":review,"gallery_bytes":sum(x["bytes"] for x in review),"main_landed":False,"pushed":False}
dump(root / "verification.json",verification)
dump(report / "verification.json",verification)
dump(report / "raw_hashes.json",{path.relative_to(report).as_posix():sha(path) for path in sorted(report.rglob("*.log"))})
for filename in ["t2_sword_start.py","t2_sword_prepare.py","t2_sword_render.py","t2_sword_record_image.py","t2_sword_record_revision.py","t2_sword_finish.py"]:
    dest = report / "tools" / filename
    dest.parent.mkdir(exist_ok=True)
    shutil.copy2(main / "tmp" / filename,dest)
ctx.update(status="verified_candidate",gallery=gallery.as_posix())
dump(main / "tmp/t2_sword_context.json",ctx)
print(json.dumps(verification,ensure_ascii=False))
