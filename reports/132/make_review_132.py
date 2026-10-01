"""#132 read-only GLB audit and mechanical review composition. No generation or model writes."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, math, re, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[2]
INPUT = ASSETS / "workbench/production/dungeon_props_132"
REPORT = ASSETS / "reports/132"
CLOUD = REPORT / "comfy_h31"
OUT = REPORT / "review_v2"
IDS = ["bone_heap", "roots", "nest", "palisade", "seal_stone", "pillar", "broken_statue"]
NAMES = {"bone_heap": "유골 더미", "roots": "뿌리", "nest": "둥지", "palisade": "목책",
         "seal_stone": "봉인돌", "pillar": "기둥", "broken_statue": "파손 석상"}
# Historical reference plans are W x D x H. They are NEVER used as measured bounds.
PLANS = {"bone_heap": [1.5, 1.0, .5], "roots": [1.3, .3, 1.6], "nest": [1.4, 1.2, .4],
         "palisade": [1.8, .3, 1.7], "seal_stone": [1.8, 1.8, .25],
         "pillar": [.7, .7, 2.0], "broken_statue": [.9, .9, 1.3]}
CHECKS = 0
def require(condition, label):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise RuntimeError(label)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def rel(path):
    return path.relative_to(ASSETS).as_posix()
def evidence(path):
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size}
def font(size):
    return ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", size)
def dims_label(v):
    return " × ".join(f"{x:.3f}" for x in v)
def content(source):
    image = Image.open(source).convert("RGBA")
    if image.getextrema()[3][0] < 255:
        box = image.getbbox()
    else:
        rgb = image.convert("RGB")
        box = ImageChops.difference(rgb, Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))).getbbox()
    return image.crop(box) if box else image
def fitted(canvas, image, box, bg=(38, 38, 36)):
    x, y, w, h = box
    canvas.paste(bg, (x, y, x+w, y+h))
    image = image.copy()
    image.thumbnail((w-16, h-12), Image.Resampling.LANCZOS)
    canvas.paste(image, (x+(w-image.width)//2, y+(h-image.height)//2), image if image.mode == "RGBA" else None)
def jpg(canvas, target):
    for quality in [88, 84, 80, 76, 72, 68, 64, 60, 56, 52, 48, 44, 40]:
        canvas.save(target, "JPEG", quality=quality, optimize=True, subsampling=2)
        if target.stat().st_size <= 300000:
            break
    require(target.stat().st_size <= 300000, f"JPEG >300KB: {target}")
    require(canvas.width == 1280, f"JPEG width: {target}")
    return {"path": rel(target), "sha256": sha(target), "bytes": target.stat().st_size,
            "width": canvas.width, "height": canvas.height, "jpeg_quality": quality}
def glb_audit(ops, asset, approved):
    ref = INPUT / "refs" / f"{asset}.png"
    runtime = CLOUD / f"{asset}_runtime_v2.json"
    item = load(runtime)
    model = INPUT / "models" / f"{asset}.glb"
    raw = CLOUD / item["source"]
    require(sha(ref) == approved[asset], f"Approved reference changed: {asset}")
    require(sha(model) == item["output_sha256"], f"Prepared GLB SHA: {asset}")
    require(sha(raw) == item["source_sha256"], f"Cloud GLB SHA: {asset}")
    js, blob = ops.read_glb(str(model))
    require(not js.get("skins") and not js.get("animations"), f"Non-static prop: {asset}")
    worlds = ops._node_worlds(js)
    positions = []
    for ni, node in enumerate(js.get("nodes", [])):
        if "mesh" not in node:
            continue
        for primitive in js["meshes"][node["mesh"]]["primitives"]:
            require(primitive.get("mode", 4) == 4, f"Not triangle mode: {asset}")
            p = ops.accessor(js, blob, primitive["attributes"]["POSITION"])
            m = worlds[ni]
            positions.append(p @ m[:3,:3].T + m[:3,3])
    vertices = np.concatenate(positions)
    lo, hi = vertices.min(0), vertices.max(0)
    dims = hi-lo
    triangles = sum(js["accessors"][p.get("indices", p["attributes"]["POSITION"])]["count"] // 3
                    for mesh in js["meshes"] for p in mesh["primitives"])
    check = REPORT / "godot_v2" / f"{asset}_check.log"
    raw_check = check.read_text(encoding="utf-8-sig")
    engine_triangles = int(re.search(r"삼각형 (\d+)", raw_check)[1])
    require(triangles == item["triangles"] == engine_triangles, f"Canonical triangles: {asset}")
    require("RESULT PASS" in raw_check and "SCRIPT ERROR:" not in raw_check and not re.search(r"^ERROR:", raw_check, re.M), f"Model check failed: {asset}")
    require(np.allclose(dims, item["dimensions_xyz"], atol=1e-6), f"Measured dimensions: {asset}")
    require(np.allclose(lo, item["bounds_min"], atol=1e-6) and np.allclose(hi, item["bounds_max"], atol=1e-6), f"Measured bounds: {asset}")
    require(abs(float(lo[1])) < 1e-6, f"Foot not grounded: {asset}")
    require(np.max(np.abs(((lo+hi)/2)[[0,2]])) < 1e-6, f"XZ pivot not centered: {asset}")
    root = js["nodes"][js["scenes"][js.get("scene", 0)]["nodes"][0]]
    matrix = np.array(root["matrix"]).reshape(4,4).T
    rotation = np.array([[0,0,-1],[0,1,0],[1,0,0]], float)
    require(np.allclose(matrix[:3,:3], rotation*item["scale"], atol=1e-7), f"Uniform scale/-90Y: {asset}")
    require(item["preparation_revision"] == 2 and item["yaw_rotation_degrees"] == -90, f"Revision/direction metadata: {asset}")
    textures = []
    for i in range(len(js.get("images", []))):
        picture, _ = ops.load_image(js, blob, i)
        textures.append(list(picture.size))
    require(textures == [[1024,1024]], f"Texture not one embedded 1K: {asset}")
    materials = []
    for material in js.get("materials", []):
        pbr = material.get("pbrMetallicRoughness", {})
        values = {"metallic": pbr.get("metallicFactor", 1), "roughness": pbr.get("roughnessFactor", 1),
                  "emissive_factor": material.get("emissiveFactor", [0,0,0]),
                  "emissive_texture": "emissiveTexture" in material}
        require(values["metallic"] == 0 and values["roughness"] == 1
                and values["emissive_factor"] == [0,0,0] and not values["emissive_texture"],
                f"Matte/emission metadata: {asset}")
        materials.append(values)
    require(len(materials) == 1, f"Unexpected material count: {asset}")
    preview = CLOUD / f"{asset}_runtime_preview.png"
    shot = REPORT / "godot_v2" / asset / "idle_00.png"
    viewer = REPORT / "godot_v2" / f"{asset}_viewer.log"
    viewtext = viewer.read_text(encoding="utf-8-sig")
    require("loaded=true" in viewtext and "SCRIPT ERROR:" not in viewtext and not re.search(r"^ERROR:", viewtext, re.M), f"Viewer failed: {asset}")
    viewer_triangles = int(re.search(r"tris=(\d+)", viewtext)[1])
    require(viewer_triangles == 2*triangles, f"Viewer outline duplicate count: {asset}")
    return {"id": asset, "name_ko": NAMES[asset], "region_ko": "흑랑 굴" if asset in IDS[:4] else "봉밀굴",
            "reference": evidence(ref), "cloud_glb": evidence(raw), "prepared_glb_v2": evidence(model),
            "runtime_v2_record": evidence(runtime), "canonical_model_check": evidence(check),
            "canonical_triangle_count": triangles, "bounds_min_xyz_units": lo.tolist(),
            "bounds_max_xyz_units": hi.tolist(), "measured_dimensions_xyz_units": dims.tolist(),
            "foot_y_units": float(lo[1]), "center_xz_units": ((lo+hi)/2)[[0,2]].tolist(),
            "measured_footprint_xz_units": [float(dims[0]), float(dims[2])],
            "measured_aabb_footprint_area_units_squared": float(dims[0]*dims[2]),
            "reference_plan_wdh_units_not_measurement": PLANS[asset],
            "uniform_scale": item["scale"], "yaw_rotation_y_degrees": -90,
            "embedded_texture_dimensions": textures, "materials": materials,
            "software_preview": evidence(preview), "godot_viewer_render": evidence(shot),
            "godot_viewer_log": evidence(viewer), "godot_viewer_triangle_label_not_canonical": viewer_triangles}

def compare(names, title, target, data):
    header, row, footer = 100, 284, 64
    canvas = Image.new("RGB", (1280, header+row*len(names)+footer), (20,23,29))
    d = ImageDraw.Draw(canvas)
    d.text((20,12), f"#132  {title} · 채택 원화 → 실제 GLB v2", font=font(26), fill=(238,226,204))
    d.text((20,48), "동일 패널 크기 / 여백 제거 후 fit · 각 패널은 형태 비교용 (물리 크기 비교 아님)", font=font(16), fill=(176,187,197))
    for col, label in enumerate(["채택 원화", "GLB 정면", "GLB 후면", "GLB 아이소"]):
        d.text((col*320+24,76), label, font=font(17), fill=(226,219,202))
    for n, asset in enumerate(names):
        y = header+n*row
        a = data[asset]
        d.text((20,y+5), f"{NAMES[asset]} / {asset}", font=font(18), fill=(225,216,201))
        fitted(canvas, content(INPUT/"refs"/f"{asset}.png"), (12,y+34,304,206))
        image = Image.open(CLOUD/f"{asset}_runtime_preview.png").convert("RGB")
        require(image.size == (900,560), f"Unexpected preview dimensions: {asset}")
        for col in range(3):
            panel = image.crop((300*col,0,300*(col+1),560))
            box = ImageChops.difference(panel, Image.new("RGB", panel.size, panel.getpixel((0,0)))).getbbox()
            if box:
                panel = panel.crop(box)
            fitted(canvas, panel, (332+col*316,y+34,304,206))
        d.text((20,y+247), f"{a['canonical_triangle_count']:,} tris  |  실측 X×Y×Z = {dims_label(a['measured_dimensions_xyz_units'])} u  |  발 Y=0 · 1K · 금속0 / 거칠기1 / 발광0",
               font=font(16), fill=(194,204,211))
        d.line((12,y+row-4,1268,y+row-4), fill=(63,70,79), width=1)
    note = "원화와 GLB/알베도 차이는 그대로 표시. 준비본 v1·계획 치수를 최종 후보로 혼용하지 않음."
    if names == IDS[4:]:
        note = "푸른 문양은 알베도 색(emission 0). 파손 석상의 끊긴 팔 실루엣을 실제 GLB에서 확인."
    d.text((20,canvas.height-49), note, font=font(16), fill=(196,187,168))
    d.text((20,canvas.height-25), "소프트웨어 GLB 검수 이미지 · 실제 던전 배치/게임 반입 사진 아님", font=font(15), fill=(154,165,177))
    return jpg(canvas, target)

def godot_sheet(names, title, target, data):
    cols = 2 if len(names) == 4 else 3
    rows = math.ceil(len(names)/cols)
    cw = (1280-32)//cols
    ch = 500 if cols == 2 else 370
    canvas = Image.new("RGB", (1280, 106+ch*rows+78), (20,23,29))
    d = ImageDraw.Draw(canvas)
    d.text((20,13), f"#132  {title} · 실제 Godot 모델 뷰어", font=font(26), fill=(238,226,204))
    d.text((20,52), "Godot 4.7.2 / 준비본 v2 · 7종 모두 같은 idle_00 화면 영역(280,120)-(1000,600)", font=font(16), fill=(181,191,203))
    d.text((20,78), "원본 스크린샷의 동일 영역만 확대 · 모델/텍스처/조명 재작성 없음", font=font(15), fill=(169,179,191))
    for n, asset in enumerate(names):
        x = 16+(n%cols)*cw
        y = 106+(n//cols)*ch
        a = data[asset]
        image = Image.open(REPORT/"godot_v2"/asset/"idle_00.png").convert("RGB")
        require(image.size == (1280,720), f"Unexpected Godot frame dimensions: {asset}")
        image = image.crop((280,120,1000,600))
        d.text((x+9,y+4), f"{NAMES[asset]} / {asset}", font=font(18), fill=(225,216,201))
        fitted(canvas, image, (x+4,y+34,cw-8, int((cw-24)*2/3)), bg=(20,23,29))
        py = y+ch-56
        d.text((x+10,py), f"{a['canonical_triangle_count']:,} tris · 발Y=0 · 1024²", font=font(16), fill=(194,204,211))
        d.text((x+10,py+25), f"실측 XYZ {dims_label(a['measured_dimensions_xyz_units'])}", font=font(14), fill=(177,188,200))
    d.text((20,canvas.height-59), "삼각형 수 = canonical model_check / GLB primitive. 뷰어의 외곽선 포함 2배 표시는 제외.", font=font(16), fill=(198,189,171))
    d.text((20,canvas.height-30), "새 3D 납품 후보 검수판 · 실제 인게임 던전 배치 검증은 후속 작업", font=font(16), fill=(169,181,194))
    return jpg(canvas, target)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-tools", type=Path, required=True)
    parser.add_argument("--game-review", type=Path, required=True)
    args = parser.parse_args()
    require(args.game_review.resolve().parts[-3:] == ("docs","art","132_dungeon_props_review"), "Wrong game output scope")
    protected = list((INPUT/"models").glob("*.glb")) + list((INPUT/"refs").glob("*.png"))
    protected += [p for p in CLOUD.rglob("*") if p.is_file()]
    protected += [p for p in (REPORT/"godot_v2").rglob("*") if p.is_file()]
    protected += [INPUT/"prepare_h31.py", INPUT/"make_contact.py", INPUT/"pd_adoption_2026_10_01.json"]
    baseline = {rel(p): sha(p) for p in protected}
    spec = importlib.util.spec_from_file_location("albedo_ops_audit_readonly", args.game_tools/"albedo_ops.py")
    ops = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ops)
    approval = load(INPUT/"pd_adoption_2026_10_01.json")
    approved = {v["id"]: v["sha256"] for v in approval["selected_inputs"]}
    require(set(approved) == set(IDS), "Approved reference set")
    data = {asset: glb_audit(ops,asset,approved) for asset in IDS}
    jobs = []
    for path in sorted(CLOUD.glob("*.job.json")):
        job = load(path)
        api = path.with_name(path.name.replace(".job.json",".api.json"))
        row = {"asset": job["asset"], "attempt": int(job.get("attempt", 2 if "_v2." in path.name else 1)),
               "state": job["state"], "prompt_id": job["prompt_id"], "model": job["model"],
               "submitted_at": job["submitted_at"], "status": job["status_response"]["status"],
               "terminal_at": job["status_response"]["last_state_update"], "job_record": evidence(path),
               "workflow_api_record": evidence(api), "requested_face_limit": job["face_limit"]}
        require(job["source_sha256"] == approved[job["asset"]], f"Submission ref SHA: {path.name}")
        if row["state"] == "downloaded":
            history = path.with_name(path.name.replace(".job.json",".history.json"))
            row["history_record"] = evidence(history)
            row["output_glb"] = evidence(CLOUD/job["output"])
            require(row["output_glb"]["sha256"] == job["output_sha256"], f"Submission output SHA: {path.name}")
        else:
            require(job["asset"] == "nest" and "429" in job["status_response"]["error_message"], "Unexpected failure")
            row["failure_json"] = evidence(CLOUD/"nest_v1.failure.json")
            row["failure_raw"] = evidence(CLOUD/"nest_v1.failure.raw.txt")
        jobs.append(row)
    raw_glbs = sorted(CLOUD.glob("*_h31_raw_v*.glb"))
    require(len(jobs) == 8 and len(raw_glbs) == 7, "Submitted/successful raw counts")
    require(sum(j["state"] == "downloaded" for j in jobs) == 7, "Success count")
    failed = next(j for j in jobs if j["state"] == "failed_recorded")
    recovered = next(j for j in jobs if j["asset"] == "nest" and j["state"] == "downloaded")
    require(datetime.datetime.fromisoformat(recovered["submitted_at"]) > datetime.datetime.fromisoformat(failed["terminal_at"].replace("Z","+00:00")), "Retry before terminal failure")
    OUT.mkdir(parents=True, exist_ok=True)
    sheets = [
        compare(IDS[:4], "흑랑 굴 4종", OUT/"01_den_source_glb.jpg", data),
        compare(IDS[4:], "봉밀굴 3종", OUT/"02_bongmil_source_glb.jpg", data),
        godot_sheet(IDS[:4], "흑랑 굴 4종", OUT/"03_den_godot.jpg", data),
        godot_sheet(IDS[4:], "봉밀굴 3종", OUT/"04_bongmil_godot.jpg", data)]
    require(len(sheets) == 4, "Review sheet count")
    for p in protected:
        require(sha(p) == baseline[rel(p)], f"Protected input changed: {rel(p)}")
    args.game_review.mkdir(parents=True,exist_ok=True)
    for item in sheets:
        shutil.copyfile(ASSETS/item["path"], args.game_review/Path(item["path"]).name)
    require(len(list(args.game_review.glob("*.jpg"))) == 4,"Game JPG count")
    for s in sheets:
        require(sha(ASSETS/s["path"]) == sha(args.game_review/Path(s["path"]).name), "Game review copy differs")
    manifest = {"schema_version":1, "card":132, "review_date":"2026-10-01", "candidate_revision":2,
                "provider":"Comfy Cloud", "model":"Tripo H3.1 / v3.1-20260211",
                "status":"3d_candidates_ready_for_pd_review", "shape_reference_pd_approved": True,
                "new_3d_result_pd_approved": False, "game_intake":False, "in_game_dungeon_review":False,
                "candidate_count":7, "approved_reference_count":7, "successful_cloud_raw_glb_count":7,
                "submitted_job_count":8, "successful_job_count":7, "failed_job_count":1,
                "prepared_v1_archived_count":len(list((CLOUD/"runtime_prior_v1").glob("*.glb"))),
                "triangle_range":[min(a["canonical_triangle_count"] for a in data.values()),max(a["canonical_triangle_count"] for a in data.values())],
                "canonical_triangle_rule":"GLB primitive accessors + godot_v2/*_check.log; viewer outline duplicates excluded",
                "dimensions_rule":"Actual transformed GLB bounds, validated against *_runtime_v2.json; X width, Y height, Z depth",
                "footprint_rule":"XZ AABB extents and their rectangle area, not collision mesh or placement occupancy",
                "display_rules":{"comparison":"same maximum panel, mechanically trimmed/fit; not relative physical scale",
                                 "godot":"idle_00.png same source crop (280,120)-(1000,600), then resize",
                                 "max_width_pixels":1280,"max_jpg_bytes":300000,"sheet_count":4,
                                 "blue_marks":"existing baked albedo, emission metadata 0; no new effect"},
                "submission_attempts":jobs, "assets":list(data.values()), "review_sheets":sheets,
                "protected_input_files_sha256":baseline, "validation":{"checks":CHECKS,"fails":0,"protected_files":len(protected)}}
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines = ["# #132 던전 소품 v2 검수판", "", "Comfy Cloud Tripo H3.1 성공 모델7종, 제출8회(둥지 v1 429 실패 후 v2 성공). 승인 원화7종 SHA 일치. 새로운 3D 결과는 본진 PD 검토 후보다.", "",
             "삼각형은 실제 GLB와 Godot model_check 정본이다. 뷰어 표시에는 외곽선이 중복돼2배가 나온다. 실측 XYZ는 폭/높이/깊이, footprint는 XZ AABB 사각형이며 충돌체/던전 통행 검증값이 아니다.", "",
             "| 소품 | 지역 | 삼각형 | 실측 X×Y×Z (u) | 실측 X×Z footprint / 면적 | 발Y |", "|---|---|---:|---|---|---:|"]
    for a in data.values():
        lines.append(f"| {a['name_ko']} ({a['id']}) | {a['region_ko']} | {a['canonical_triangle_count']:,} | {dims_label(a['measured_dimensions_xyz_units'])} | {dims_label(a['measured_footprint_xz_units'])} / {a['measured_aabb_footprint_area_units_squared']:.3f}u² | {a['foot_y_units']:.0f} |")
    lines += ["", "7종 모두 GLB 내장 텍스처1장1024², 정적 메시, 금속0·거칠기1·emission0·Y축−90°·균일 배율·XZ 중앙 pivot. 원화 단계의 계획 치수는 README/manifest의 별도 칸으로만 남긴다. 목책 실측 높이는1.308u이며 계획1.7u와 같다고 표시하지 않는다.", "",
              "검수 관찰: 유골 더미·뿌리·둥지·목책의 실루엣은 정면/후면/아이소에서 비교한다. 봉인돌의 푸른 원과 석재의 푸른 기는 알베도에 남아 있어 emission0이라도 색 자체는 보인다. 파손 석상의 팔 단면이 끊긴 형태는 GLB 정면과 아이소에서 읽힌다. 실제 어두운 던전 조명·전투 바닥·클릭면·통행 여유는 이 뷰어 사진으로 판정하지 않는다.", "",
              "검수판4장: 01/02는 채택 원화→실제 GLB 소프트웨어3뷰, 03/04는 실제 Godot7렌더의 공통 영역 확대다. 모두1280폭·300KB 이하. 원본 사진은 reports/132/godot_v2, 원문은 reports/132/comfy_h31, 최종 실제 측정과 전체 SHA는 review_v2/manifest.json.", "",
              "PD 판정·게임 반입·배치·main 착륙은 본진 후속 작업이다. 모델/원화/raw 변경이나 신규 유료 생성은 없고 검수판의 기계 합성/리사이즈/레이블만 추가했다.", "",
              f"검증: {CHECKS} checks / fails0, 보호 입력{len(protected)}개 SHA 불변. model_check7/7 PASS와 실제 GLB 삼각형·치수·재질 대조 PASS.", "",
              "둥지 실패 원문: reports/132/comfy_h31/nest_v1.failure.raw.txt (429). 성공 재시도: nest_v2.job.json·nest_v2.history.json. v1 GLB는 생성되지 않았고 runtime_prior_v1은 별도 변환 이력이다.", ""]
    (OUT/"README.md").write_text("\n".join(lines),encoding="utf-8")
    shutil.copyfile(OUT/"manifest.json",args.game_review/"manifest.json")
    shutil.copyfile(OUT/"README.md",args.game_review/"QA.md")
    print(json.dumps({"status":"PASS","checks":CHECKS,"fails":0,"protected_files":len(protected),
                      "raw_glb":len(raw_glbs),"submitted":len(jobs),"candidate_count":len(data),
                      "triangles":manifest["triangle_range"],
                      "sheets":[{"name":Path(s["path"]).name,"bytes":s["bytes"]} for s in sheets]},ensure_ascii=False))
    for a in data.values():
        print(f"{a['id']}: {a['canonical_triangle_count']} tris, XYZ={dims_label(a['measured_dimensions_xyz_units'])}, footprint area={a['measured_aabb_footprint_area_units_squared']:.6f}, foot={a['foot_y_units']:.6f}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
