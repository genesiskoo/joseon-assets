from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
sys.stdout.reconfigure(encoding="utf-8")
root=Path("C:/workspace/joseon")
game=Path("C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon")
assets=root/"._tmp/assets_464"
prod=assets/"workbench/production/item_icons_464"
report=assets/"reports/464/2026-09-28"
gallery=game/"docs/art/464_d1_t2_armor"
assert not (root/"tmp/item_464_context.json").exists()
env=dict(os.environ,PYTHONIOENCODING="utf-8",GODOT_BIN="C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe")
def run(tree,args):
    p=subprocess.run(args,cwd=tree,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(p.stdout.decode("utf-8-sig",errors="replace"),end="",flush=True);p.check_returncode();return p.stdout.decode().strip()
for tree in [game,assets]:assert not run(tree,["git","status","--porcelain"]).strip()
run(game,["git","switch","-c","codex/464-t2-armor-icons"])
for path in [prod/"source/items",prod/"game/items",prod/"references",prod/"qa",report,gallery]:path.mkdir(parents=True,exist_ok=True)
materials={"jigap":("지갑","겹친 종이의 두께·누빈 큰 구획·밝은 무명 표면"),"swaejagap":("쇄자갑","쇠고리가 연결된 사슬 표면·회색 금속"),"gyeongbeongap":("경번갑","남색 천에 누빈 작은 쇠札·사각 구획"),"dujeonggap":("두정갑","적갈색 천 갑옷·촘촘한 쇠못 머리"),"silk_dopo":("비단 도포","짙은 청록 비단의 면과 부드러운 광택·흰 깃"),"hakchangui":("학창의","흰 바탕·검은 깃/테두리·넓은 소매")}
rows=[]
for id,(name,shape) in materials.items():
    p=game/f"data/items/{id}.tres";text=p.read_text(encoding="utf-8")
    assert f'id = "{id}"' in text and f'display_name = "{name}"' in text
    assert "size = Vector2i(2, 3)" in text and "tier = 2" in text and "slot = 1" in text
    rows.append({"item_id":id,"display_name":name,"grid_w":2,"grid_h":3,"output_width":160,"output_height":240,"silhouette":shape,"definition_path":p.as_posix(),"definition_sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
(prod/"inputs.json").write_text(json.dumps({"card":464,"parent_card":274,"items":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
ref=root.parent/"joseon-assets/workbench/production/ui_icon_redesign_2026-09-23/individual/source/items/cotton_dopo.png"
shutil.copyfile(ref,prod/"references/approved_d1_cotton_dopo.png")
protected=[]
for folder in ["data/items","assets/sprites/ui/icons_a"]:
    for p in sorted((game/folder).rglob("*")):
        if p.is_file() and not p.name.endswith(".import"):protected.append({"path":p.relative_to(game).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
(prod/"current_game_snapshot.json").write_text(json.dumps(protected,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
brief="""# #464 D1 T2 갑·포6 제작 계약

상위 #274 핵심 잔여57 중 미제작 실제 정의6: 지갑·쇄자갑·경번갑·두정갑·비단 도포·학창의. 사양 item_catalog_v2 §1.2/§1.3·각 ItemDef, 모두 2×3칸/160×240 RGBA. native image_gen으로 독립 원화를 생산하고 기존 #393과 같은 알파16/여백8%/Lanczos 규격으로만 패킹한다. 얼굴/인물/몸/마네킹 없이 장비 물체 하나, 조선풍 재질·치마/깃/소매. 완전한 실루엣/최소8% 원화여백/진짜 투명배경·문자/테두리/후광 금지. 승인 D1 비단 이전 무명도포 원본은 읽기 기준이며 덮어쓰지 않는다.

겹친 종이·사슬 고리·천에 누빈 작은 쇠札·쇠못 머리·비단면·흰바탕 검은선의 차이를 실제 UiSkin 논리40px(80×120)·검정칸/48px(96×144)/30/60에서 대조한다. 좋은 검/물약은 후속 폴리싱 기조로만 기록했으며 이번은 기존 아이콘 수정이 아니라 미제작 전용그림 생산이다. 현재 ItemDef와 채택 PNG42/그림외필드/3D드랍은 보존한다. 후보 채택 전 게임 반입 없음; #274 잔여57은 판정 전 그대로다.

왜 이 구조인가: 각 아이템 정본의 소재와 기존2×3 점유·공통 UiSkin을 함께 쓰면 작은 가방에서도 장비 종류의 차이를 판정할 수 있다. 기존 공용 H1 그림을 덮어쓰면 다른 장비까지 바뀌므로 기각한다. 원본·프롬프트·해시와 최종파일을 별도로 보존하고 채택 파일만 후속 카드에서 연결한다.
"""
(prod/"BRIEF.md").write_text(brief,encoding="utf-8",newline="\n")
p=game/"docs/design/ui_v2.md";text=p.read_text(encoding="utf-8")
text+="\n\n## D1 T2 갑·포6 원화 후보 계약 (#464, 2026-09-28)\n\n#274 미제작 실제 정의의 지갑·쇄자갑·경번갑·두정갑·비단 도포·학창의를 item_catalog_v2 §1.2/§1.3 소재에 맞는 독립 물체로 제작한다. 전부2×3칸/160×240 RGBA이며 원본/프롬프트/해시는 자산 workbench/production/item_icons_464, 검수는 reports/464/2026-09-28와 docs/art/464_d1_t2_armor에 남긴다. 알파16/8%여백/Lanczos 공통 패킹과 실제 UiSkin40px/검정칸/30·48·60 검수로 종이겹·사슬·누빈 쇠札·못 머리·비단·흰바탕 검은선을 비교한다. 현재42PNG/정의/수치/모델은 유지하고, 후보 채택 뒤 게임 반입은 별도 카드에서 한다. 왜 이 구조인가: 물건 소재와 기존 점유·공통 렌더를 함께 쓰면 작은 가방에서 종류 차이를 판정할 수 있다. 기존 H1 공용그림 덮어쓰기는 다른 장비까지 바꾸므로 기각한다.\n"
p.write_text(text,encoding="utf-8",newline="\n")
ctx={"card":464,"parent_card":274,"status":"prepared","game":game.as_posix(),"assets":assets.as_posix(),"production":prod.as_posix(),"report":report.as_posix(),"gallery":gallery.as_posix(),"game_base":run(game,["git","rev-parse","HEAD"]),"asset_base":run(assets,["git","rev-parse","HEAD"]),"approved_reference_sha256":hashlib.sha256(ref.read_bytes()).hexdigest()}
(root/"tmp/item_464_context.json").write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
run(game,[sys.executable,"tools/wt.py","setup","--card","464","--slug","t2-armor-icons"])
print("PASS #464 spec-first; definitions6 and existing PNG42 protected; isolated native art production ready")
