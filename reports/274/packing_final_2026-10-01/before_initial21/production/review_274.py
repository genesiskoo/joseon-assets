"""Mechanical QA variants and final delivery validation for design-only card274."""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from prepare_274 import ROOT,REPO,REPORT,DEFAULT_GAME,COLORS,sha,stats,write_json
sys.dont_write_bytecode=True
MODES=["actual","grayscale","black","horibyeong"]
def gray(image):
    data=np.asarray(image.convert("RGBA")).copy()
    lum=np.rint(data[:,:,:3].astype(float)@np.array([.2126,.7152,.0722])).astype(np.uint8)
    data[:,:,:3]=lum[:,:,None]
    return Image.fromarray(data,"RGBA")
def jpeg(image,path):
    image=image.convert("RGB")
    assert image.width==1280
    for quality in [86,82,78,74,70,66]:
        image.save(path,quality=quality,optimize=True)
        if Path(path).stat().st_size<=300000:return
    raise AssertionError(f"JPG >300KB: {path}")
def prepare_qa():
    m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    for directory in ["qa/grayscale","qa/source80","qa/source80_gray"]: (ROOT/directory).mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",17)
    atlas=Image.new("RGB",(1280,1080),"#211d19");d=ImageDraw.Draw(atlas)
    d.text((24,16),"#274 원화 컷아웃 비교 · 가방 UI 검수 전의 기계 축소 · 후보21/승인잔여25",font=font,fill="#e5d5bd")
    for i,row in enumerate(m["items"]):
        uid=row["production_key"];packed=Image.open(ROOT/row["game_path"]).convert("RGBA")
        source=Image.open(ROOT/row["source_path"]).convert("RGBA")
        gray(packed).save(ROOT/f"qa/grayscale/{uid}.png")
        source_sz=(80,round(source.height*80/source.width))
        mini=source.convert("RGBa").resize(source_sz,Image.Resampling.LANCZOS).convert("RGBA")
        mini.save(ROOT/f"qa/source80/{uid}.png");gray(mini).save(ROOT/f"qa/source80_gray/{uid}.png")
        if uid=="horibyeong":continue
        x=20+(i%4)*314;y=68+(i//4)*197
        d.rectangle((x,y,x+301,y+181),fill="#29231e")
        d.text((x+10,y+8),row["working_label"],font=font,fill="#e5d5bd")
        large=source.crop(source.getchannel("A").getbbox())
        large.thumbnail((126,128),Image.Resampling.LANCZOS)
        tile=Image.new("RGBA",(126,128),"#1b1e22")
        tile.alpha_composite(large,((126-large.width)//2,(128-large.height)//2))
        atlas.paste(tile.convert("RGB"),(x+12,y+37))
        for xx,bg,title in [(x+158,"#1b1e22","출력80"),(x+158,"#000000","black40")]:
            side=80 if title=="출력80" else 40
            yy=y+39 if side==80 else y+132
            icon=packed if side==80 else packed.convert("RGBa").resize((40,40),Image.Resampling.LANCZOS).convert("RGBA")
            comp=Image.alpha_composite(Image.new("RGBA",(side,side),bg),icon)
            atlas.paste(comp.convert("RGB"),(xx,yy))
            d.text((xx+side+4,yy+6),title,font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",12),fill="#b9ad99")
    atlas.save(REPORT/"software_source_overview.png")
    jpeg(atlas,REPORT/"software_source_overview.jpg")
    print("QA variants prepared21; source RGB/alpha unchanged; grayscale diagnostics only")
def review(game):
    m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert len(m["items"])==21 and m["status"]=="candidate_ready_not_approved_not_installed"
    assert m["approved_remaining"]==25 and m["pending_child"]=={"card":534,"count":4}
    before=json.loads((REPORT/"runtime_before.json").read_text(encoding="utf-8"))
    changed=[p for p,v in before["files"].items() if sha(game/p)!=v]
    assert not changed,changed
    cloud=json.loads((REPORT/"cloud_inputs_before.json").read_text(encoding="utf-8"))
    cloud_changed=[p for p,v in cloud["root_owned_files"].items() if sha(REPO/p)!=v]
    assert not cloud_changed,cloud_changed
    legacy=json.loads((REPORT/"legacy_ledger_before.json").read_text(encoding="utf-8"))
    assert all(sha(game/"art/item_catalog_274"/p)==v["sha256"] for p,v in legacy.items())
    items=[]
    for row in m["items"]:
        assert all(row[k] is None for k in ["actual_item_id","actual_gem_id","final_display_name","final_grade_name","socket_count","game_rarity","game_tier","efficacy"])
        for p,v in [(row["source_path"],row["source_sha256"]),(row["generated_path"],row["generated_sha256"]),(row["game_path"],row["game_sha256"])]:
            assert sha(ROOT/p)==v
        assert sha(REPO/row["clean_receipt_path"])==row["source_sha256"] and sha(REPO/row["generated_receipt_path"])==row["generated_sha256"]
        data=stats(ROOT/row["game_path"])
        assert data["size"]==row["provisional_output_px"] and data["alpha_extrema"]==[0,255]
        assert data["bbox"]==row["packed_stats"]["bbox"] and min(data["margins_ltrb"])>=6
        assert data["corner_alpha"]==[0,0,0,0]
        assert abs(row["resized_aspect_ratio"]/row["source_content_aspect_ratio"]-1)<.02
        a=np.asarray(Image.open(ROOT/row["generated_path"]));b=np.asarray(Image.open(ROOT/row["source_path"]))
        assert np.array_equal(a[:,:,:3],b[:,:,:3])
        qa_gray=np.asarray(Image.open(ROOT/f'qa/grayscale/{row["production_key"]}.png'))
        assert np.array_equal(qa_gray[:,:,3],np.asarray(Image.open(ROOT/row["game_path"]))[:,:,3])
        items.append({"production_key":row["production_key"],"result":"PASS","alpha":data["alpha_extrema"],"margins":data["margins_ltrb"],"aspect_relative_error":abs(row["resized_aspect_ratio"]/row["source_content_aspect_ratio"]-1),"raw_clean_rgb_max_delta":0})
    gallery=game/"docs/art/274_final_item_art";gallery.mkdir(parents=True,exist_ok=True)
    photos=[]
    for mode in MODES:
        raw=REPORT/f"godot_{mode}.png";trace=REPORT/f"godot_{mode}.raw.log";audit=REPORT/f"godot_{mode}.json"
        assert raw.exists() and trace.exists() and audit.exists()
        log=trace.read_text(encoding="utf-8-sig")
        assert f"GODOT_274_PASS mode={mode}" in log and "SCRIPT ERROR" not in log and not any(s.startswith("ERROR:") for s in log.splitlines())
        r=json.loads(audit.read_text(encoding="utf-8"))
        assert r["card"]==274 and r["candidate_count"]==21 and r["runtime_itemdefs_modified"]==0
        destination=gallery/f"godot_{mode}.jpg"
        jpeg(Image.open(raw),destination)
        shutil.copyfile(destination,REPORT/destination.name)
        photos.append({"file":destination.name,"sha256":sha(destination),"bytes":destination.stat().st_size,"width":1280})
    assert len(photos)<=6
    write_json(REPORT/"review.json",{"card":274,"result":"PASS","item_checks":items,"runtime_files_unchanged":len(before["files"]),"runtime_changed":changed,"root_cloud_inputs_unchanged":len(cloud["root_owned_files"]),"cloud_changed":cloud_changed,"legacy_ledgers_unchanged":len(legacy),"actual_ui_modes":MODES,"game_gallery":photos,"candidate_ready21":True,"approved_remaining25":True,"pd_adoption":"pending","definition_binding":"blocked_on265_not_created","manual_quality_evaluation":"see visual_findings.json; automated pass does not assert artistic preference"})
    print(json.dumps({"result":"PASS","items":len(items),"runtime_unchanged":len(before["files"]),"cloud_inputs_unchanged":len(cloud["root_owned_files"]),"game_jpg":len(photos),"max_jpg_bytes":max(p["bytes"] for p in photos)},ensure_ascii=True))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--game",type=Path,default=DEFAULT_GAME);p.add_argument("--prepare-qa",action="store_true")
    a=p.parse_args()
    prepare_qa() if a.prepare_qa else review(a.game)
