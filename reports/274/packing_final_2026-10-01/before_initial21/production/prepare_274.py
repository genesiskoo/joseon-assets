"""Card274: preserve completed Cloud sources and mechanically pack design-only art."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
REPORT=REPO/"reports/274/packing_final_2026-10-01"
DEFAULT_GAME=Path("C:/Users/FORYOUCOM/.codex/worktrees/274-obangjade-art/joseon")
COLORS=[("red","적옥"),("black","흑옥"),("blue","청옥"),("white","백옥"),("yellow","황옥")]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
def stats(path):
    image=Image.open(path)
    assert image.mode=="RGBA",str(path)
    a=np.asarray(image)[:,:,3]
    b=image.getchannel("A").getbbox()
    assert b
    w,h=image.size
    return {"size":list(image.size),"mode":image.mode,"alpha_extrema":[int(a.min()),int(a.max())],
            "bbox":list(b),"margins_ltrb":[b[0],b[1],w-b[2],h-b[3]],
            "nonzero":int(np.count_nonzero(a)),"partial":int(np.count_nonzero((a>0)&(a<255))),
            "opaque":int(np.count_nonzero(a==255)),"content_aspect_ratio":(b[2]-b[0])/(b[3]-b[1]),
            "corner_alpha":[int(a[y,x]) for x,y in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]}
def contain(image,size):
    bounds=image.getchannel("A").getbbox()
    assert bounds
    body=image.crop(bounds)
    pad=max(1,round(min(size)*.08))
    scale=min((size[0]-pad*2)/body.width,(size[1]-pad*2)/body.height)
    target=(max(1,round(body.width*scale)),max(1,round(body.height*scale)))
    resized=body.convert("RGBa").resize(target,Image.Resampling.LANCZOS).convert("RGBA")
    packed=Image.new("RGBA",tuple(size))
    packed.alpha_composite(resized,((size[0]-target[0])//2,(size[1]-target[1])//2))
    return packed,list(bounds),pad,list(target)
def secret_scan():
    source_paths=[REPO/p for p in json.loads((REPORT/"cloud_inputs_before.json").read_text(encoding="utf-8"))["root_owned_files"]]
    patterns=[("openai_key",re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
              ("bearer",re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}")),
              ("credential_field",re.compile(r'''(?i)["'](?:api_key|apikey|access_token|authorization)["']\s*:\s*["'][^"']{12,}'''))]
    findings=[];count=0
    for p in source_paths:
        if p.suffix not in [".json",".txt",".md",".log"]:continue
        text=p.read_text(encoding="utf-8-sig")
        count+=1
        for kind,rx in patterns:
            for match in rx.finditer(text):
                findings.append({"path":p.relative_to(REPO).as_posix(),"kind":kind,"line":text.count("\n",0,match.start())+1})
    result={"text_files_checked":count,"findings":findings,"result":"PASS" if not findings else "FAIL","matched_secret_values_not_recorded":True}
    write_json(REPORT/"secret_scan.json",result)
    assert not findings,findings
    return result
def prepare(game):
    plan=json.loads((ROOT/"generation_plan.json").read_text(encoding="utf-8-sig"))
    jobs={row["id"]:row for row in plan["jobs"]}
    assert len(jobs)==23
    ids=[f"obang_jade_{color}_grade_{stage}" for color,_ in COLORS for stage in range(1,5)]+["horibyeong"]
    rows=[]
    cloud=REPO/"reports/274/comfy_final_icons"
    for uid in ids:
        key=uid+"_v2" if uid in ["obang_jade_red_grade_1","obang_jade_red_grade_4"] else uid
        job=jobs[key];contract=job["contract"]
        assert contract["production_key"]==uid and contract["definition_state"]=="design_only" and contract["actual_item_id"] is None
        assert contract["intake_dependency"]==265
        clean=cloud/(key+".png");native=cloud/(key+"_raw.png")
        graph_path=cloud/(key+".api.json");job_path=cloud/(key+".job.json")
        history_path=cloud/(key+".history.json");prompt_path=cloud/(key+".prompt.txt")
        graph=json.loads(graph_path.read_text(encoding="utf-8-sig"))
        receipt=json.loads(job_path.read_text(encoding="utf-8-sig"))
        history=json.loads(history_path.read_text(encoding="utf-8-sig"))
        assert isinstance(history["status"],dict) and history["status"]["completed"] and history["status"]["status_str"]=="success"
        assert graph["8"]["class_type"]=="OpenAIGPTImageNodeV2"
        assert graph["10"]["class_type"]=="SplitImageWithAlpha" and graph["9"]["inputs"]["image"]==["10",0]
        assert graph["9"]["class_type"]=="BiRefNetRMBG"
        assert receipt["model"]=="gpt-image-2.5-flare" and receipt["reference_images"]==[]
        execution_prompt=graph["8"]["inputs"]["prompt"]
        assert hashlib.sha256(execution_prompt.encode("utf-8")).hexdigest()==receipt["prompt_sha256"]
        assert execution_prompt.rstrip("\r\n")==prompt_path.read_text(encoding="utf-8-sig").rstrip("\r\n")
        original=np.asarray(Image.open(native))
        cut=np.asarray(Image.open(clean))
        assert original.shape==cut.shape and np.array_equal(original[:,:,:3],cut[:,:,:3]),uid
        assert Image.open(clean).getchannel("A").getextrema()==(0,255)
        for source,destination in [(native,ROOT/f"source/items/{key}_generated.png"),(clean,ROOT/f"source/items/{key}.png")]:
            destination.parent.mkdir(parents=True,exist_ok=True)
            if destination.exists():assert sha(destination)==sha(source)
            else:shutil.copyfile(source,destination)
        size=[80,160] if uid=="horibyeong" else [80,80]
        canvas,bounds,pad,resized=contain(Image.open(clean),size)
        dest=ROOT/f"game/items/{uid}.png";dest.parent.mkdir(parents=True,exist_ok=True)
        canvas.save(dest)
        st=stats(dest);assert st["alpha_extrema"]==[0,255] and min(st["margins_ltrb"])>=pad
        stage=None if uid=="horibyeong" else int(contract["grade"])
        color=None if uid=="horibyeong" else uid.split("_")[2]
        label="호리병" if stage is None else dict(COLORS)[color]+" · "+{1:"깨진",2:"흠 있는",3:"온전한",4:"4단(명칭 미정)"}[stage]
        rows.append({"production_key":uid,"working_label":label,"color_token":color,"art_quality_stage":stage,
         "definition_state":"design_only","actual_item_id":None,"actual_gem_id":None,"final_display_name":None,
         "final_grade_name":None,"socket_count":None,"game_rarity":None,"game_tier":None,"efficacy":None,
         "intake_dependency":265,"provisional_output_px":size,"provisional_grid":[1,2] if uid=="horibyeong" else [1,1],
         "grid_source":"item_system_v2 §11.1 provisional" if uid=="horibyeong" else "art spec provisional, verify against265",
         "source_revision":key,"source_path":f"source/items/{key}.png","source_sha256":sha(clean),
         "generated_path":f"source/items/{key}_generated.png","generated_sha256":sha(native),
         "clean_receipt_path":clean.relative_to(REPO).as_posix(),"generated_receipt_path":native.relative_to(REPO).as_posix(),
         "source_stats":stats(clean),"generated_stats":stats(native),"game_path":f"game/items/{uid}.png",
         "game_sha256":sha(dest),"packed_stats":st,"source_crop_bbox":bounds,"resized_content_px":resized,
         "packing_padding_px":pad,"packing_method":"premultiplied Lanczos, uniform contain, center padding; alpha unthresholded",
         "source_content_aspect_ratio":(bounds[2]-bounds[0])/(bounds[3]-bounds[1]),"resized_aspect_ratio":resized[0]/resized[1],
         "rgb_max_delta_raw_to_clean":0,"alpha_pixels_changed":int(np.count_nonzero(original[:,:,3]!=cut[:,:,3])),
         "cloud":{"provider":"Comfy Cloud","model":receipt["model"],"job_id":receipt["prompt_id"],
                  "api_path":graph_path.relative_to(REPO).as_posix(),"api_sha256":sha(graph_path),
                  "job_path":job_path.relative_to(REPO).as_posix(),"job_sha256":sha(job_path),
                  "history_path":history_path.relative_to(REPO).as_posix(),"history_sha256":sha(history_path),
                  "prompt_path":prompt_path.relative_to(REPO).as_posix(),"prompt_file_sha256":sha(prompt_path),
                  "execution_prompt_sha256":receipt["prompt_sha256"],"prompt_text_file_trailing_newline_preserved":True,
                  "graph_node_classes":{k:v["class_type"] for k,v in graph.items()},"terminal_status":"success"}})
    failed=[]
    for uid in ["obang_jade_red_grade_1","obang_jade_red_grade_4"]:
        history_path=cloud/(uid+".history.json");history=json.loads(history_path.read_text(encoding="utf-8-sig"))
        assert history["status"]=="error"
        failed.append({"source_key":uid,"selected":False,"status":"error","reason":"terminal RGBA4 sent to BiRefNet RGB3; retry inserts SplitImageWithAlpha",
         "history_path":history_path.relative_to(REPO).as_posix(),"history_sha256":sha(history_path),
         "history_preservation":"full original including execution error retained byte-for-byte",
         "api_path":f"reports/274/comfy_final_icons/{uid}.api.json","job_path":f"reports/274/comfy_final_icons/{uid}.job.json",
         "prompt_path":f"reports/274/comfy_final_icons/{uid}.prompt.txt","replacement_source":uid+"_v2"})
    scan=secret_scan()
    manifest={"schema":"joseon.item_art_candidate.v2","card":274,"date":"2026-10-01","status":"candidate_ready_not_approved_not_installed",
     "definition_state":"design_only","candidate_ready":21,"approved_remaining":25,"approved_remaining_closed":False,
     "pending_child":{"card":534,"count":4},"group_counts":{"obang_jade":20,"horibyeong":1},
     "approval_baseline":{"latest_accepted_card":496,"accepted_count":3,"evidence_commit":"0e2f7820","legacy_remaining28_unchanged":True},
     "production_source":"Comfy Cloud GPT Image2.5 Flare high -> SplitImageWithAlpha RGB -> BiRefNet general alpha",
     "paid_generation_by_worker":False,"source_collection_by":"root","submissions_total":23,"successful_selected":21,"initial_failed":failed,
     "manual_pixel_editing":False,"manual_alpha_editing":False,"production_alpha_thresholding":False,
     "new_runtime_definitions":0,"existing_png_changed":0,"save_changes":0,"items":rows,
     "actual_ui":{"source":"current UiSkin.item_slot/item_icon via distinct in-memory icons_a/qa274 paths",
       "bag_cell":[40,40],"bag_padding":8,"vendor_cell":[48,48],"vendor_padding":3,"source_review_width":80,
       "horibyeong_bag_provisional_cell":[40,80],"belt_role":False,"itemdefs_not_loaded_for_candidates":True},
     "unresolved":["265 ItemDef/GemDef IDs","265 final grid confirmation","265 socket count","grade4 name: 맑은 vs 영롱한","PD adoption"],
     "source_docs":{p:sha(game/p) for p in ["docs/design/item_system_v2.md","ui/ui_skin.gd","ui/inventory_ui.gd","ui/vendor_ui.gd"]},
     "secret_scan":scan,"runtime_baseline_path":"reports/274/packing_final_2026-10-01/runtime_before.json",
     "cloud_inputs_baseline_path":"reports/274/packing_final_2026-10-01/cloud_inputs_before.json"}
    write_json(ROOT/"manifest.json",manifest)
    write_json(REPORT/"alpha_aspect_margin_audit.json",{"card":274,"result":"PASS","items":[{k:r[k] for k in ["production_key","source_revision","source_stats","generated_stats","packed_stats","source_content_aspect_ratio","resized_aspect_ratio","rgb_max_delta_raw_to_clean","alpha_pixels_changed","packing_padding_px"]} for r in rows]})
    print(json.dumps({"result":"PASS","packed":len(rows),"source_png_copies":len(rows)*2,"failed_preserved":len(failed),"secret_texts_checked":scan["text_files_checked"]},ensure_ascii=True))
    return manifest
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--game",type=Path,default=DEFAULT_GAME)
    prepare(parser.parse_args().game)
