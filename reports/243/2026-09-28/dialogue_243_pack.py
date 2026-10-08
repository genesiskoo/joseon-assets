from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
import numpy as np
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path("C:/workspace/joseon")
ctx = json.loads((root / "tmp/dialogue_243_context.json").read_text(encoding="utf-8"))
prod, report, gallery = [Path(ctx[k]) for k in ["production", "report", "gallery"]]
plans = {"doho": {"base": "doho_neutral_r2", "expressions": ["neutral", "smug", "serious"], "face": [485,270,675,490], "gaze": "screen_right"}, "merchant": {"base": "merchant_neutral", "expressions": ["neutral", "smile"], "face": None, "gaze": "screen_left"}}
records = []
comparisons = []
for actor, plan in plans.items():
    source = prod / "source" / (plan["base"]+".png")
    if not source.exists():
        continue
    base = Image.open(source).convert("RGBA")
    bbox = base.getchannel("A").point(lambda a: 255 if a >= 16 else 0).getbbox()
    left, top, right, bottom = bbox
    scale = min(954/(right-left), 1413/(bottom-top))
    crop = (max(0,left-4),max(0,top-4),min(1024,right+4),min(1536,bottom+4))
    size = (round((crop[2]-crop[0])*scale),round((crop[3]-crop[1])*scale))
    position = (round((1024-(right-left)*scale)/2-(left-crop[0])*scale),round(123-(top-crop[1])*scale))
    if actor == "merchant" and plan["face"] is None:
        plan["face"] = [395,205,615,445]
    target = prod / "game" / actor
    target.mkdir(parents=True,exist_ok=True)
    for expression in plan["expressions"]:
        variant = "merchant_smile_r2" if actor == "merchant" and expression == "smile" else f"{actor}_{expression}"
        src = source if expression == "neutral" else prod / "source" / (variant+".png")
        if not src.exists():
            continue
        im = Image.open(src)
        assert im.mode == "RGBA" and im.size == (1024,1536)
        # Standard intake packing only: one common uniform resample and canvas placement per character.
        # No face edits/compositing, alpha amplification, background removal or content repainting.
        packed = Image.new("RGBA",(1024,1536),(0,0,0,0))
        packed.paste(im.crop(crop).resize(size,Image.Resampling.LANCZOS),position)
        out = target / (expression+".png")
        packed.save(out)
        a = packed.getchannel("A")
        bound = a.point(lambda v:255 if v>=16 else 0).getbbox()
        assert a.getextrema()[0] == 0 and a.getextrema()[1] >= 250
        assert abs(bound[1]-123)<=2 and bound[0]>=32 and bound[2]<=992, bound
        entry={"actor":actor,"expression":expression,"source":src.relative_to(prod).as_posix(),"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"destination":out.relative_to(prod).as_posix(),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"size":[1024,1536],"alpha":list(a.getextrema()),"alpha16_bbox":list(bound),"gaze":plan["gaze"],"common_geometry":{"base":plan["base"],"bbox":list(bbox),"crop":list(crop),"scale":scale,"resampled_size":list(size),"position":list(position)},"postprocess":"standard common uniform alpha-preserving intake packing; no facial compositing"}
        records.append(entry)
        if expression != "neutral":
            ref = np.array(base).astype(np.int16)
            candidate = np.array(im).astype(np.int16)
            am, bm = ref[:,:,3]>=16,candidate[:,:,3]>=16
            diff = np.abs(ref-candidate).max(axis=2)
            union = am|bm
            fx0,fy0,fx1,fy1=plan["face"]
            body=union.copy();body[fy0:fy1,fx0:fx1]=False
            face=union.copy();face[:]=False;face[fy0:fy1,fx0:fx1]=union[fy0:fy1,fx0:fx1]
            iou=float((am&bm).sum()/union.sum())
            assert iou>=0.990, (actor,expression,iou)
            comparisons.append({"actor":actor,"expression":expression,"source_face_rect":plan["face"],"alpha16_silhouette_iou":iou,"body_visible_pixels":int(body.sum()),"body_changed_pixels":int(((diff>0)&body).sum()),"body_mean_max_channel_difference":float(diff[body].mean()),"face_changed_pixels":int(((diff>0)&face).sum()),"exact_body_pixels":bool(not ((diff>0)&body).any()),"interpretation":"same pose/props/common frame; native re-rasterization causes body color/edge variation, not pixel-identical face-only patch"})
manifest={"card":243,"status":"candidate_not_installed","method":"native image_gen generation/expression-only edits; common alpha-preserving intake packing per character","approval":ctx["approval"],"references":ctx["references"],"items":records,"expression_comparisons":comparisons,"original_game_images_modified":False,"runtime_intake":"after pilot PD decision, separate claude card; intake_portrait.ps1 is currently absent; static mid-thigh anchor must be adapted"}
(prod / "manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
(report / "packing_verification.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
font_path="C:/Windows/Fonts/malgun.ttf"
font=ImageFont.truetype(font_path,24)
small=ImageFont.truetype(font_path,19)
for actor,title in [("doho","도호 — 중립 · 능청 · 진지"),("merchant","김 영감 — 중립 · 미소")]:
    group=[e for e in records if e["actor"]==actor]
    if not group:
        continue
    plate=Image.new("RGB",(1280,760),(24,22,21))
    draw=ImageDraw.Draw(plate);draw.text((24,12),title,font=font,fill=(225,208,178))
    width=1280//len(group)
    names={"neutral":"중립","smug":"능청","serious":"진지","smile":"미소"}
    for i,e in enumerate(group):
        thumb=Image.open(prod/e["destination"]);thumb.thumbnail((width-25,640),Image.Resampling.LANCZOS)
        plate.paste(thumb,(i*width+(width-thumb.width)//2,55),thumb)
        draw.text((i*width+30,707),names[e["expression"]],font=small,fill=(221,214,200))
    p=gallery/f"{actor}_expressions.jpg";plate.save(p,quality=85,optimize=True)
    assert p.stat().st_size<=300_000
    (report/p.name).write_bytes(p.read_bytes())
print("PACKED",len(records),"portraits",[(c["actor"],c["expression"],round(c["alpha16_silhouette_iou"],6),c["exact_body_pixels"]) for c in comparisons])
