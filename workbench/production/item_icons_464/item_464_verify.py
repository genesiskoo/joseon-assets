from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,os,shutil,subprocess,sys
sys.stdout.reconfigure(encoding="utf-8")
root=Path("C:/workspace/joseon");ctx=json.loads((root/"tmp/item_464_context.json").read_text(encoding="utf-8"))
game,assets,prod,report,gallery=[Path(ctx[k]) for k in ["game","assets","production","report","gallery"]]
manifest=json.loads((prod/"manifest.json").read_text(encoding="utf-8"));assert len(manifest["items"])==6
shutil.copyfile(root/"tmp/item_464_qa.gd",prod/"qa_godot.gd")
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
results=[]
for mode in ["after","sizes","black_sizes"]:
    log=report/f"godot_{mode}.raw.log"
    cmd=["C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe","--path",str(game),"--script",str(prod/"qa_godot.gd"),"--windowed","--resolution","1280x760","--position","0,0","--",f"--root={prod.as_posix()}",f"--out={report.as_posix()}",f"--mode={mode}"]
    with log.open("wb") as stream:
        process=subprocess.Popen(cmd,cwd=game,stdout=stream,stderr=subprocess.STDOUT,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
        try:code=process.wait(timeout=50)
        except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10);code=124
    raw=log.read_text(encoding="utf-8-sig",errors="replace");print(raw,end="",flush=True)
    assert code==0 and "GODOT_D1_464_PASS" in raw,(mode,code)
    assert "SCRIPT ERROR" not in raw and "ERROR:" not in raw
    im=Image.open(report/f"godot_{mode}.png");assert im.size==(1280,760)
    dest=gallery/f"godot_{mode}.jpg";im.convert("RGB").save(dest,quality=87,optimize=True)
    assert dest.stat().st_size<=300_000
    shutil.copyfile(dest,report/dest.name)
    results.append({"mode":mode,"status":"PASS","script_engine_errors":0,"capture_size":[1280,760],"real_shared_renderer":"UiSkin.item_slot/item_icon","virtual_resource_paths_only":True})
# Read-only QA colour conversion. Native source/packed item PNGs remain untouched.
sheet=Image.new("RGB",(1280,360),(15,14,13));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",20)
d.text((24,16),"#464 80×120px 무채색 가독성 대조 — 원본 PNG 변경 없음",font=font,fill=(222,207,181))
for i,e in enumerate(manifest["items"]):
    x=30+i*208;rgba=Image.open(prod/"game/items"/(e["item_id"]+".png")).resize((80,120),Image.Resampling.LANCZOS)
    gray=rgba.convert("L").convert("RGBA");gray.putalpha(rgba.getchannel("A"))
    sheet.paste(rgba,(x+10,76),rgba);sheet.paste(gray,(x+112,76),gray)
    d.text((x,232),e["display_name"],font=font,fill=(222,207,181))
    d.text((x,272),"색 / 무채색",font=font,fill=(171,158,137))
sheet.save(gallery/"material_readability.jpg",quality=86,optimize=True)
shutil.copyfile(gallery/"material_readability.jpg",report/"material_readability.jpg")
snapshot=json.loads((prod/"current_game_snapshot.json").read_text(encoding="utf-8"))
for p in snapshot:assert hashlib.sha256((game/p["path"]).read_bytes()).hexdigest()==p["sha256"],p["path"]
runtime_diff=subprocess.run(["git","diff",ctx["game_base"],"--name-only","--","assets","data","core","ui","world","items"],cwd=game,capture_output=True,check=True).stdout.decode().strip();assert not runtime_diff,runtime_diff
assert hashlib.sha256((prod/"references/approved_d1_cotton_dopo.png").read_bytes()).hexdigest()==ctx["approved_reference_sha256"]
jpg=list(gallery.glob("*.jpg"));assert len(jpg)<=6 and sum(p.stat().st_size for p in jpg)<=2_000_000
qa={"card":464,"parent_card":274,"status":"candidate_not_installed","originals":6,"packed_png":6,"dimensions":[160,240],"footprint":[2,3],"renderer_runs":results,"protected_runtime_files":len(snapshot),"protected_icon_png":42,"runtime_diff_empty":True,"gallery":[{"name":p.name,"bytes":p.stat().st_size} for p in jpg],"limits":"No item has been adopted/installed. Small chainmail rings and individual studs are not individually readable at30px per cell; broader materials and silhouette are the acceptance target. Full suite not run because runtime code/data unchanged.","parent_remaining":57,"if_all_six_adopted_remaining":51}
(prod/"verification.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
(report/"verification.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
(prod/"README.md").write_text("# #464 D1 T2 갑·포6 — PD 확인 후보\n\n지갑·쇄자갑·경번갑·두정갑·비단 도포·학창의. item_catalog_v2 §1.2/1.3의 소재, 현 ItemDef2×3칸을 따르는 독립 물체 그림이다. 원화6은 native image_gen으로 생성했고 기존 #393의 알파16/8%여백/Lanczos 공통 패킹만 거쳐160×240 RGBA로 정리했다. source/items 원본·game/items 최종·PROMPTS.md·generation_sources.json·manifest.json에 경로/해시/규격을 보존한다. 기존 H1 공용그림/현재D1 PNG42/정의67은 바뀌지 않았다.\n\n실제 Godot UiSkin.item_slot/item_icon을 검수 프로세스에서만 호출해40px 논리셀의80×120 표시와검정칸,30/48/60px셀을 검수했다. 후보Texture의 가상ResourcePath를 연결해 실제알파영역 경로를 사용하되 게임파일은 쓰지 않았다. 무채색대조는 검토판의 색 변환만 수행한다. 원본/최종PNG는그대로다. 30px에서 사슬고리·못머리 하나하나를읽는 것은 제한되므로 큰재질면·깃·구획으로구별한다. 코드/데이터변경없어전체단위/E2E는안돌렸고, 실제공통UI3렌더/오류0·원본/정의/PNG해시보존·문서예산으로 검증했다.\n\n왜 이 구조인가: 정본재질과공통점유/렌더를함께쓰면 작은가방에서물체의종류를판정할수있다. H1공용원본덮어쓰기는다른장비도바꾸므로기각했다. 게임반입은PD채택후별도카드, 상위#274잔여57은미채택상태에서유지하며6종전부채택시51이된다. 기존그림즉시폴리싱은하지않았고좋은검/물약의품질사다리지시는후속기조로만기록했다.\n",encoding="utf-8",newline="\n")
(gallery/"README.md").write_text("# #464 갑·포6 신규 원화 검토\n\n미제작전용후보6. overview=원화/가방크기, godot_after=실제UiSkin40px와검정칸, godot_sizes/black_sizes=30·48·60px, material_readability=색/무채색대조. 기존게임그림은그대로이며미반입이다. 자산workbench/production/item_icons_464와reports/464/2026-09-28에원본/PNG/프롬프트/해시/raw보존.\n",encoding="utf-8",newline="\n")
shutil.copyfile(root/"tmp/item_464_README.md",prod/"README.md")
for name in ["item_464_pack.py","item_464_verify.py","item_464_prepare.py"]:shutil.copyfile(root/"tmp"/name,prod/name)
shutil.copyfile(root/"tmp/item_464_context.json",report/"context.json")
(report/".gitattributes").write_text("*.log -text\n",encoding="utf-8",newline="\n")
print("PASS #464 real UiSkin3 modes; PNG6/definitions6; protected",len(snapshot),"runtime files/PNG42; gallery",len(jpg),"JPG",sum(p.stat().st_size for p in jpg),"bytes")
