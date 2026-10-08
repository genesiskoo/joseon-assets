from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,sys
sys.stdout.reconfigure(encoding="utf-8")
root=Path("C:/workspace/joseon")
ctx=json.loads((root/"tmp/item_464_context.json").read_text(encoding="utf-8"))
prod,report,gallery=[Path(ctx[k]) for k in ["production","report","gallery"]]
inputs=json.loads((prod/"inputs.json").read_text(encoding="utf-8"))
generated=json.loads((root/"tmp/item_464_generated.json").read_text(encoding="utf-8"))
records=[]
for row in generated:
    native=Path(row["native_path"])
    out=prod/"source/items"/(row["id"]+".png")
    if not out.exists():shutil.copyfile(native,out)
    assert native.read_bytes()==out.read_bytes()
    row["source_sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
for e in inputs["items"]:
    matches=[r for r in generated if r["id"]==e["item_id"] and r.get("selected",True)]
    if not matches:continue
    src=prod/"source/items"/(matches[-1]["id"]+".png")
    raw=Image.open(src)
    assert raw.mode=="RGBA",(e["item_id"],raw.mode)
    assert raw.getchannel("A").getextrema()[0]==0 and raw.getchannel("A").getextrema()[1]>=250
    alpha=raw.getchannel("A").point(lambda a:a if a>=16 else 0)
    bbox=alpha.getbbox();assert bbox and 0<bbox[0]<bbox[2]<raw.width and 0<bbox[1]<bbox[3]<raw.height,(e["item_id"],bbox,raw.size)
    art=raw.copy();art.putalpha(alpha);art=art.crop(bbox)
    size=(e["output_width"],e["output_height"])
    pad=max(5,round(min(size)*.08))
    scale=min((size[0]-2*pad)/art.width,(size[1]-2*pad)/art.height)
    shown=art.resize((max(1,round(art.width*scale)),max(1,round(art.height*scale))),Image.Resampling.LANCZOS)
    packed=Image.new("RGBA",size)
    packed.alpha_composite(shown,((size[0]-shown.width)//2,(size[1]-shown.height)//2))
    dst=prod/"game/items"/(e["item_id"]+".png");packed.save(dst,optimize=True)
    bound=packed.getchannel("A").getbbox()
    assert bound and bound[0]>=2 and bound[1]>=2 and bound[2]<=size[0]-2 and bound[3]<=size[1]-2
    assert packed.getchannel("A").getextrema()[0]==0 and packed.getchannel("A").getextrema()[1]>=250
    assert hashlib.sha256(Path(e["definition_path"]).read_bytes()).hexdigest()==e["definition_sha256"]
    records.append(dict(e,source_path=src.relative_to(prod).as_posix(),source_size=list(raw.size),source_bbox=list(bbox),source_alpha=list(raw.getchannel("A").getextrema()),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),game_size=list(size),game_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),visible_bbox=list(bound),packed_alpha=list(packed.getchannel("A").getextrema())))
manifest={"card":464,"parent_card":274,"status":"candidate_not_installed","method":"native image_gen originals; approved #393 alpha16/8percent/Lanczos standard packing","logical_cell_px":40,"output_scale":2,"items":records}
(prod/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
(prod/"generation_sources.json").write_text(json.dumps({"card":464,"items":generated},ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
(prod/"PROMPTS.md").write_text("# #464 Native generation prompts\n\n"+"\n\n".join("## "+r["id"]+"\n\n"+r["prompt"]+"\n\nNative original: "+r["native_path"] for r in generated)+"\n",encoding="utf-8",newline="\n")
if len(records)==6:
    font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",21);small=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",14)
    plate=Image.new("RGB",(1280,900),(25,23,21));draw=ImageDraw.Draw(plate)
    draw.text((24,15),"#464 D1 T2 갑·포 6종 — 원화 / 80×120px 가방 크기",font=font,fill=(230,214,184))
    for i,e in enumerate(records):
        x=18+(i%3)*424;y=65+(i//3)*410
        draw.rectangle((x,y,x+407,y+389),fill=(31,28,24),outline=(83,69,50))
        art=Image.open(prod/e["source_path"]).crop(tuple(e["source_bbox"]));art.thumbnail((220,280),Image.Resampling.LANCZOS)
        plate.paste(art,(x+15+(220-art.width)//2,y+18),art)
        smallart=Image.open(prod/"game/items"/(e["item_id"]+".png")).resize((80,120),Image.Resampling.LANCZOS)
        draw.rectangle((x+290,y+55,x+370,y+175),fill=(17,16,15),outline=(87,74,57))
        plate.paste(smallart,(x+290,y+55),smallart)
        draw.text((x+265,y+199),"40px × 2×3칸",font=small,fill=(181,166,142))
        draw.text((x+17,y+308),e["display_name"],font=font,fill=(229,216,190))
        draw.text((x+17,y+344),e["silhouette"],font=small,fill=(182,167,144))
        draw.text((x+17,y+368),e["item_id"]+" · 160×240 RGBA",font=small,fill=(152,143,125))
    plate.save(prod/"qa/overview.png",optimize=True)
    plate.save(prod/"qa/overview.jpg",quality=86,optimize=True)
    shutil.copyfile(prod/"qa/overview.jpg",gallery/"overview.jpg")
    shutil.copyfile(prod/"qa/overview.jpg",report/"overview.jpg")
print("PACKED",len(records),[(r["item_id"],r["source_size"],r["game_size"],r["visible_bbox"]) for r in records])
