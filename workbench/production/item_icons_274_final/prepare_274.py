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
def capture_root_baseline():
    """Run only after root confirms that all selected receipt collections are complete."""
    paths=list(ROOT.glob("generation_plan*.json"))+[ROOT/"README.md",REPO/"reports/274/pilot_dark_composite.png"]
    for directory in ["comfy_final_icons","comfy_grade4_textonly_v2"]:
        paths.extend(p for p in (REPO/"reports/274"/directory).rglob("*") if p.is_file() and p.name!=".gitattributes")
    before=json.loads((REPORT/"cloud_inputs_before.json").read_text(encoding="utf-8"))
    assert all(sha(REPO/p)==digest for p,digest in before["root_owned_files"].items())
    baseline={"card":274,"root_collection_complete":True,"root_owned_files":{p.relative_to(REPO).as_posix():sha(p) for p in sorted(paths)}}
    output=REPORT/"cloud_inputs_final.json"
    if output.exists():assert json.loads(output.read_text(encoding="utf-8"))==baseline,"root sources changed after final capture"
    else:write_json(output,baseline)
    print(json.dumps({"source_baseline_files":len(baseline["root_owned_files"]),"initial137_unchanged":True}))

def secret_scan():
    baseline=REPORT/"cloud_inputs_final.json"
    assert baseline.exists(),"capture the complete root source baseline after the final collection notice"
    source_paths=[REPO/p for p in json.loads(baseline.read_text(encoding="utf-8"))["root_owned_files"]]
    patterns=[("openai_key",re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
              ("bearer",re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}")),
              ("credential_field",re.compile(r'''(?i)["'](?:api_key|apikey|access_token|authorization)["']\s*:\s*["'][^"']{12,}'''))]
    findings=[];count=0;metadata=[]
    for p in source_paths:
        if p.suffix.lower() in [".png",".jpg",".jpeg"]:
            with Image.open(p) as image:
                info={"png_or_image_info":image.info,"exif":dict(image.getexif())}
                text=json.dumps(info,ensure_ascii=True,default=lambda value:repr(value),sort_keys=True)
                metadata.append({"path":p.relative_to(REPO).as_posix(),"image_sha256":sha(p),"metadata_keys":list(image.info),"exif_tags":len(image.getexif()),"metadata_serialization_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest()})
        elif p.suffix in [".json",".txt",".md",".log"]:
            text=p.read_text(encoding="utf-8-sig");count+=1
        else:continue
        for kind,rx in patterns:
            for match in rx.finditer(text):
                findings.append({"path":p.relative_to(REPO).as_posix(),"kind":kind,"line":text.count("\n",0,match.start())+1})
    result={"text_files_checked":count,"image_metadata_checked":len(metadata),"findings":findings,"result":"PASS" if not findings else "FAIL","matched_secret_values_not_recorded":True}
    write_json(REPORT/"secret_scan.json",result)
    packed_metadata={p.name:sorted(Image.open(p).info) for p in (ROOT/"game/items").glob("*.png")}
    assert all(not keys for keys in packed_metadata.values())
    write_json(REPORT/"png_metadata_scan.json",{"card":274,"result":result["result"],"metadata_sources":metadata,"packed_candidate_metadata_keys":packed_metadata,"findings":findings,"secret_values_not_printed_or_recorded":True})
    assert not findings,findings
    return result
def prepare(game):
    selection=json.loads((ROOT/"source_selection.json").read_text(encoding="utf-8"))
    assert selection["selected_count"]==21 and selection["revised_grade4_count"]==5 and selection["reference_images_uploaded"]==0
    plans={path:json.loads((REPO/path).read_text(encoding="utf-8-sig")) for path in {row["plan"] for row in selection["sources"].values()}}
    ids=[f"obang_jade_{color}_grade_{stage}" for color,_ in COLORS for stage in range(1,5)]+["horibyeong"]
    assert set(selection["sources"])==set(ids)
    rows=[]
    for uid in ids:
        chosen=selection["sources"][uid];key=chosen["source_key"];cloud=REPO/chosen["report"]
        job=next(row for row in plans[chosen["plan"]]["jobs"] if row["id"]==key);contract=job["contract"]
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
        label="호리병" if stage is None else dict(COLORS)[color]+" · "+{1:"깨진",2:"흠 있는",3:"온전한",4:"영롱한"}[stage]
        rows.append({"production_key":uid,"working_label":label,"color_token":color,"art_quality_stage":stage,
         "definition_state":"design_only","actual_item_id":None,"actual_gem_id":None,"final_display_name":None,
         "final_grade_name":None,"socket_count":None,"game_rarity":None,"game_tier":None,"efficacy":None,
         "intake_dependency":265,"provisional_output_px":size,"provisional_grid":[1,2] if uid=="horibyeong" else [1,1],
         "grid_source":"item_system_v2 §11.1 provisional" if uid=="horibyeong" else "art spec provisional, verify against265",
         "source_revision":key,"source_plan_path":chosen["plan"],"source_plan_sha256":sha(REPO/chosen["plan"]),
         "source_path":f"source/items/{key}.png","source_sha256":sha(clean),
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
                  "reference_images":receipt["reference_images"],"reference_images_uploaded":0,
                  "graph_node_classes":{k:v["class_type"] for k,v in graph.items()},"terminal_status":"success"}})
    failed=[]
    cloud=REPO/"reports/274/comfy_final_icons"
    for uid in ["obang_jade_red_grade_1","obang_jade_red_grade_4"]:
        history_path=cloud/(uid+".history.json");history=json.loads(history_path.read_text(encoding="utf-8-sig"))
        assert history["status"]=="error"
        failed.append({"source_key":uid,"selected":False,"status":"error","reason":"terminal RGBA4 sent to BiRefNet RGB3; retry inserts SplitImageWithAlpha",
         "history_path":history_path.relative_to(REPO).as_posix(),"history_sha256":sha(history_path),
         "history_preservation":"full original including execution error retained byte-for-byte",
         "api_path":f"reports/274/comfy_final_icons/{uid}.api.json","job_path":f"reports/274/comfy_final_icons/{uid}.job.json",
         "prompt_path":f"reports/274/comfy_final_icons/{uid}.prompt.txt","replacement_source":uid+"_v2"})
    all_submissions=[]
    selected_keys={r["source_revision"] for r in rows}
    for plan_path,plan in sorted(plans.items()):
        collection=REPO/plan["report"]
        for job in plan["jobs"]:
            key=job["id"];history_path=collection/(key+".history.json");receipt_path=collection/(key+".job.json")
            history=json.loads(history_path.read_text(encoding="utf-8-sig"));receipt=json.loads(receipt_path.read_text(encoding="utf-8-sig"))
            status=history["status"]["status_str"] if isinstance(history["status"],dict) else history["status"]
            assert status in ["success","error"] and receipt["reference_images"]==[]
            all_submissions.append({"source_key":key,"production_key":job["contract"]["production_key"],"plan_path":plan_path,
             "history_path":history_path.relative_to(REPO).as_posix(),"history_sha256":sha(history_path),
             "job_path":receipt_path.relative_to(REPO).as_posix(),"job_id":receipt["prompt_id"],"status":status,"selected":key in selected_keys,
             "generated_png_exists":(collection/(key+"_raw.png")).exists(),"clean_png_exists":(collection/(key+".png")).exists()})
    assert len(all_submissions)==28 and sum(r["status"]=="success" for r in all_submissions)==26
    before_snapshot=REPORT/"before_initial21/snapshot_manifest.json"
    assert before_snapshot.exists()
    scan=secret_scan()
    manifest={"schema":"joseon.item_art_candidate.v2","card":274,"date":"2026-10-01","status":"candidate_ready_not_approved_not_installed",
     "definition_state":"design_only","candidate_ready":21,"approved_remaining":25,"approved_remaining_closed":False,
     "pending_child":{"card":534,"count":4},"group_counts":{"obang_jade":20,"horibyeong":1},
     "approval_baseline":{"latest_accepted_card":496,"accepted_count":3,"evidence_commit":"0e2f7820","legacy_remaining28_unchanged":True},
     "production_source":"Comfy Cloud GPT Image2.5 Flare high -> SplitImageWithAlpha RGB -> BiRefNet general alpha",
     "paid_generation_by_worker":False,"source_collection_by":"root","submissions_total":len(all_submissions),"successful_collected":26,
     "successful_selected":21,"successful_superseded":5,"initial_failed":failed,"all_submissions":all_submissions,
     "revision":{"kind":selection["revision"],"source_selection_path":"source_selection.json","source_selection_sha256":sha(ROOT/"source_selection.json"),
       "before_snapshot_path":before_snapshot.relative_to(REPO).as_posix(),"before_snapshot_manifest_sha256":sha(before_snapshot),
       "revised_grade4_count":5,"working_stage4_name":"영롱한","working_name_source":"D-084 item_catalog_v2 status line6; final data binding remains null",
       "reference_images_uploaded":0,"blocked_reference_plan_path":"workbench/production/item_icons_274_final/generation_plan_grade4_shape_v2.json",
       "blocked_reference_plan_sha256":sha(ROOT/"generation_plan_grade4_shape_v2.json"),
       "approval_rejection_path":"reports/274/comfy_grade4_textonly_v2/automatic_approval_rejection.raw.txt",
       "approval_rejection_sha256":sha(REPO/"reports/274/comfy_grade4_textonly_v2/automatic_approval_rejection.raw.txt")},
     "manual_pixel_editing":False,"manual_alpha_editing":False,"production_alpha_thresholding":False,
     "new_runtime_definitions":0,"existing_png_changed":0,"save_changes":0,"items":rows,
     "actual_ui":{"source":"current UiSkin.item_slot/item_icon via distinct in-memory icons_a/qa274 paths",
       "bag_cell":[40,40],"bag_padding":8,"vendor_cell":[48,48],"vendor_padding":3,"source_review_width":80,
       "horibyeong_bag_provisional_cell":[40,80],"belt_role":False,"itemdefs_not_loaded_for_candidates":True},
     "unresolved":["265 ItemDef/GemDef IDs","265 final grid confirmation","265 socket count","265 final data names","PD adoption"],
     "source_docs":{p:sha(game/p) for p in ["docs/design/item_system_v2.md","docs/design/item_catalog_v2.md","ui/ui_skin.gd","ui/inventory_ui.gd","ui/vendor_ui.gd"]},
     "secret_scan":scan,"runtime_baseline_path":"reports/274/packing_final_2026-10-01/runtime_before.json",
     "cloud_inputs_baseline_path":"reports/274/packing_final_2026-10-01/cloud_inputs_final.json"}
    write_json(ROOT/"manifest.json",manifest)
    write_json(REPORT/"alpha_aspect_margin_audit.json",{"card":274,"result":"PASS","items":[{k:r[k] for k in ["production_key","source_revision","source_stats","generated_stats","packed_stats","source_content_aspect_ratio","resized_aspect_ratio","rgb_max_delta_raw_to_clean","alpha_pixels_changed","packing_padding_px"]} for r in rows]})
    print(json.dumps({"result":"PASS","packed":len(rows),"selected_source_copies":len(rows)*2,"all_source_png_copies":len(list((ROOT/"source/items").glob("*.png"))),"failed_preserved":len(failed),"secret_texts_checked":scan["text_files_checked"]},ensure_ascii=True))
    return manifest
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--game",type=Path,default=DEFAULT_GAME);parser.add_argument("--capture-source-baseline",action="store_true")
    args=parser.parse_args()
    capture_root_baseline() if args.capture_source_baseline else prepare(args.game)
