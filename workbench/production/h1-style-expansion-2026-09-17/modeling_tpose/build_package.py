"""Rebuild delivery ZIPs and HTML without changing any PNG pixels."""
import hashlib, html, json, struct, sys, zipfile
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
data=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
rows=data["records"]
active=[r for r in rows if r.get("status")!="superseded"]
CHARS=[("doho","도호","PC",1.7),("merchant","김 영감","NPC",1.5),("shaman","무당 할매","NPC",1.5),("elder","촌장","NPC",1.6),("bandit","산적","적",1.5),("talisman_master","부적술사","적",1.6)]
VIEWS=[("front","01","정면"),("left","02","좌측"),("back","03","후면"),("right","04","우측")]
lookup={(r["character"],r["view"]):r for r in active}
assert len(active)==len(lookup)==24
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,text):
 p=(ROOT/name).resolve()
 assert p.is_relative_to(ROOT)
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(text,encoding="utf-8")
stable={r["source_path"]:str((ROOT/r["file"]).resolve()) for r in rows}
origin={r["id"]:r for r in json.loads((ROOT.parent/"manifest.json").read_text(encoding="utf-8"))["records"]}
for r in active:
 if r.get("source_record"):
  old=origin[r["source_record"]]
  r["prompt"]=old["prompt"]
  r.setdefault("reference_paths_at_generation",old.get("reference_paths_at_generation",old["references"]))
  r["original_tool_source_path"]=old["source_path"]
  stable[old["source_path"]]=str((ROOT/r["file"]).resolve())
for r in rows:
 r.setdefault("reference_paths_at_generation",r["references"])
 r["references"]=[stable.get(p,p) for p in r["reference_paths_at_generation"]]
 for p in r["references"]: assert Path(p).is_file(),p
 path=(ROOT/r["file"]).resolve()
 assert path.is_relative_to(ROOT) and path.is_file()
 assert sha(path)==r["sha256"]
 assert struct.unpack(">II",path.read_bytes()[16:24])==(r["width"],r["height"])
for cid,*_ in CHARS:
 assert len({(lookup[cid,v]["width"],lookup[cid,v]["height"]) for v,_,_ in VIEWS})==1
data.update(active_image_count=24,archived_rejected_image_count=3,view_order=["front","left","back","right"],side_convention="Anatomical left: nose points image right; anatomical right: nose points image left",qa_scope="Illustration/input QA only; no model or rigging verification",local_raster_edits=False,external_model_uploads_this_package=0,external_model_generation_jobs_this_package=0)
write("manifest.json",json.dumps(data,ensure_ascii=False,indent=2)+"\n")
guide="""# H1 인게임 캐릭터 T포즈 — Meshy / Tripo 입력

2026-09-17 · D-071 도호 / D-072 공통 H1 화풍. **현행 인게임 인간형 6종 × 4뷰 = PNG 24장**.
기존 도호·상인 정면/후면 4장은 바이트 그대로 재사용했다. 최종 입력 시안 20장을 새로 생성했으며 수정 전 3장은 archive/rejected/에 분리했다.

## 사용하는 파일

각 캐릭터 폴더: 01_front.png → 02_left.png → 03_back.png → 04_right.png.
left는 **인물의 왼쪽**을 보는 측면(코가 화면 오른쪽), right는 인물의 오른쪽(코가 화면 왼쪽)이다.
인물 한 명·한 방향·빈 주먹 T포즈. 무기·지팡이·부채·방울은 별도 소품이다. 정체성에 포함되는 허리 패·주머니·손목 부적은 유지했다.

| 폴더 / 게임 id | 캐릭터 | 목표 키(유닛) | 실제 PNG |
|---|---|---:|---|
"""
for cid,name,role,height in CHARS:
 r=lookup[cid,"front"]
 guide+=f"| {cid} | {name} ({role}) | {height} | {r['width']} × {r['height']} |\n"
guide+="""
캐릭터별 4뷰의 캔버스 크기는 같다. 위 해상도는 PNG 실측값이다. 인물마다 프레임에 맞춘 그림이므로 서로 다른 캐릭터의 이미지상 키를 게임 키로 해석하지 않는다.

## 업로드

- **Meshy:** 같은 인물의 4장을 넣고 01_front.png를 첫 이미지로 둔다. Meshy 7 API는 1~4장이며 첫 장이 정면 기준이다. [공식 Multi-Image API](https://docs.meshy.ai/en/api/multi-image-to-3d)
- **Tripo:** 정면·좌측·후면·우측 슬롯에 같은 이름의 파일을 각각 넣는다. 공식 API의 순서는 [front, left, back, right]다. [공식 Generation API](https://platform.tripo3d.ai/docs/generation)
- 단일 이미지 경로에서는 01_front.png만 사용한다. 갤러리 화면이나 4뷰 합본은 업로드하지 않는다.
- ZIP은 전달용이다. 압축을 풀고 PNG를 업로드한다. 서비스 UI의 슬롯 예시와 실제 방향도 대조한다.
- 이번 작업에서는 Meshy/Tripo로 이미지를 전송하거나 모델을 생성하지 않았다.

## 검수

전신 프레임, 수평 T팔, 빈 주먹, 얼굴·나이·체형, 앞뒤 의상, 90도 측면과 좌우 장식을 직접 대조하고 독립 시각 QA를 수행했다. 도호의 파란 패·상인 주머니의 오른쪽 측면 노출과 무당 왼쪽 비녀 큰 머리 중복을 수정했다. 수정 전 3장은 업로드 ZIP에서 제외했다.

H1의 어두운 고유색은 유지하며 형태를 읽는 중립 조명을 사용한다. 장면의 어둠·림라이트·안개를 텍스처에 미리 굽지 않는다. [Meshy 입력 가이드](https://help.meshy.ai/en/articles/9996860-how-to-use-meshy-image-to-3d)

**입력 그림 검수와 메시·리깅 검수는 별도다.** 모델 생성 후 소매와 겨드랑이, 치마 속 두 다리, 가려진 반대 팔다리, 얇은 갓끈·탈·부적, 주먹/손목, 옷자락 관통을 확인한다. 도호 머리끝 길이·촌장 소매 안감·산적의 작은 패치·술사 옷자락은 뷰마다 작은 해석 차이가 남아 있어 모델에서 연결을 다듬는다. 주먹 입력만으로 서비스가 닫힌 손을 보장하지 않으며 기존 그립 보정·무기 소켓 검수를 이어간다. [Tripo 리깅 가이드](https://www.tripo3d.ai/blog/how-to-rig-an-ai-generated-character)

박쥐·흑랑은 인간 T포즈 대상이 아니므로 기존 날개 펼침/네 발 입력을 유지한다. 귀새·청연·구미호의 H1 외형 카탈로그는 유지하며 이번 현행 인게임 6종 묶음과 별도다.

## 추적

Built-in image_gen 사용, 실제 모델 ID는 도구에서 미노출. PROMPTS.md에 정확한 프롬프트·생성 당시 참조·현재 영구 참조를 기록했다. manifest.json에는 원본 위치·최종 경로·SHA-256·실측 크기가 있다. validation.json은 파일·방향 슬롯·ZIP·링크 검사다.
build_package.py를 실행하면 PNG를 편집하지 않고 ZIP과 갤러리를 재생성한다. downloads/의 ZIP은 배포용 복제물이므로 Git에는 중복 저장하지 않는다.

이 구조는 모델이 인물·뷰·무기를 혼동하지 않도록 단일 뷰 PNG를 원본 단위로 유지하기 위해 채택했다. 여러 몸이 합쳐질 수 있는 카탈로그 합본 입력은 검토 화면으로만 사용한다.
"""
write("README.md",guide)
lines=["# H1 T-pose exact prompts","Built-in image_gen. Actual model ID not exposed.",""]
for r in rows:
 lines += [f"## {r['id']} — {r['file']}",f"Status: {r['status']}",f"Mode: {r['mode']}",f"SHA256: {r['sha256']}","","References at generation:"]
 lines += [f"{i+1}. {p}" for i,p in enumerate(r["reference_paths_at_generation"])]
 lines += ["","Persistent project references:"]
 lines += [f"{i+1}. {p}" for i,p in enumerate(r["references"])]
 lines += ["","Prompt:","",r["prompt"],""]
write("PROMPTS.md","\n".join(lines)+"\n")
orders={cid:{"game_id":cid,"target_height":height,"meshy_images":[lookup[cid,v]["file"] for v,_,_ in VIEWS],"tripo_slots":{v:lookup[cid,v]["file"] for v,_,_ in VIEWS}} for cid,_,_,height in CHARS}
write("upload_order.json",json.dumps(orders,ensure_ascii=False,indent=2)+"\n")
write(".gitignore","downloads/\n__pycache__/\n")
write("archive/README.md","# 수정 전 시안 3장\n\n오른쪽에 왼쪽 장식이 보이던 도호·상인 2장, 왼쪽 비녀 큰 머리가 중복된 무당 1장. rejected/에 보존하며 업로드 ZIP·갤러리에서 제외한다.\n")
downloads=ROOT/"downloads"
downloads.mkdir(exist_ok=True)
zip_reports=[]
def makezip(path,entries):
 with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for src,name in entries:z.write(src,name)
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for src,name in entries:assert hashlib.sha256(z.read(name)).hexdigest()==sha(src)
 zip_reports.append({"file":path.relative_to(ROOT).as_posix(),"entries":len(entries),"sha256":sha(path),"crc_and_content_hashes":True})
for cid,name,_,height in CHARS:
 note=f"{name} / {cid}\n01_front -> 02_left -> 03_back -> 04_right\nLeft = anatomical left (nose points image right); right = anatomical right (nose points image left).\nMeshy: front must be first. Tripo: use front/left/back/right slots.\nGame target height: {height} units. Neutral light, empty fists, weapons separate.\nInput artwork QA only; inspect generated limbs, cloth, thin details and hands before rigging.\n"
 write(f"{cid}/UPLOAD.txt",note)
 entries=[(ROOT/lookup[cid,v]["file"],Path(lookup[cid,v]["file"]).name) for v,_,_ in VIEWS]+[(ROOT/cid/"UPLOAD.txt","UPLOAD.txt")]
 makezip(downloads/f"{cid}_4views.zip",entries)
entries=[(ROOT/lookup[cid,v]["file"],lookup[cid,v]["file"]) for cid,*_ in CHARS for v,_,_ in VIEWS]
entries += [(ROOT/n,n) for n in ["README.md","upload_order.json"]]
makezip(downloads/"H1_TPOSE_6_CHARACTERS.zip",entries)
css="""*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#15191c;color:#e9e3d9;font:16px/1.65 system-ui,'Malgun Gothic',sans-serif}a{color:#b5cdd3;text-underline-offset:4px}header,main,footer{max-width:1360px;margin:auto;padding:30px}header{padding-top:46px}.eyebrow{font-size:12px;letter-spacing:.14em;color:#bda17b}h1{font-size:42px;line-height:1.25;margin:12px 0}h2{font-size:25px;margin:0}p{margin:10px 0}.muted{color:#aebbc0}.row,nav{display:flex;align-items:center;flex-wrap:wrap;gap:10px}.row{justify-content:space-between}.button,nav a{display:inline-block;padding:8px 14px;border:1px solid #596365;border-radius:5px;text-decoration:none}.primary{background:#b8cfd2;color:#142127;border:0;font-weight:650}.note{border-left:3px solid #bda17b;background:#21292e;padding:15px 20px;margin:22px 0}.section{padding-top:24px;margin:25px 0 52px;scroll-margin-top:20px}.tag{font-size:12px;color:#c2ad8d;letter-spacing:.08em}.views{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:20px}.view{margin:0;overflow:hidden;background:#22282d;border:1px solid #41494e;border-radius:6px}.view img{display:block;width:100%;height:auto}.view figcaption{padding:10px 14px;font-size:14px}.view small{display:block;color:#b3bdc2;font-size:12px}.small{font-size:14px}details{background:#1c2429;padding:14px 18px;border:1px solid #41494e;border-radius:5px}summary{cursor:pointer}.spec{max-width:950px}footer{border-top:1px solid #41494e;color:#aebbc0;font-size:13px}@media(max-width:850px){.views{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:520px){header,main,footer{padding:20px}h1{font-size:30px}.views{gap:8px}.view figcaption{padding:8px;font-size:13px}}"""
page=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>H1 캐릭터 T포즈 · Meshy / Tripo</title><style>{css}</style></head><body>'
page+='''<header><div class="eyebrow">JOSEON HUNTERS / H1 / MODEL INPUT</div><h1>인게임 캐릭터 T포즈</h1><p class="muted">현행 인간형 6종 · 정면 / 좌측 / 후면 / 우측 · 개별 PNG 24장</p><div class="row"><a class="button primary" href="downloads/H1_TPOSE_6_CHARACTERS.zip" download>24장 전체 ZIP</a><a href="../index.html">H1 아트 전체 보기</a></div><div class="note"><strong>같은 인물의 네 장을 사용하세요.</strong><br>Meshy: 01 정면을 첫 이미지로. Tripo: 정면·좌측·후면·우측 슬롯에 각각 배치.<br><span class="small">좌측/우측은 인물 기준입니다. 좌측은 코가 화면 오른쪽, 우측은 코가 화면 왼쪽을 향합니다.</span></div><nav>'''
for cid,name,*_ in CHARS:page+=f'<a href="#{cid}">{name}</a>'
page+='</nav></header><main>'
for cid,name,role,height in CHARS:
 page+=f'<section id="{cid}" class="section"><div class="row"><div><div class="tag">{role} / {cid.upper()} / {height}u</div><h2>{name}</h2></div><a class="button" href="downloads/{cid}_4views.zip" download>이 캐릭터 4장 ZIP</a></div><div class="views">'
 for v,num,label in VIEWS:
  r=lookup[cid,v];f=html.escape(r["file"])
  page+=f'<figure class="view"><a href="{f}"><img src="{f}" alt="{name} {label} T포즈"></a><figcaption>{num} · {label}<small>{r["width"]} × {r["height"]} PNG</small><a href="{f}" download>원본 저장</a></figcaption></figure>'
 page+='</div></section>'
page+='''<details open><summary>검수와 모델링 시 확인할 점</summary><div class="spec"><p>전신 잘림, T팔, 빈 주먹, 나이·복식, 앞뒤·좌우 장식을 대조했습니다. 도호의 패, 상인의 주머니, 무당의 비녀 중복을 수정했습니다.</p><p>어두운 복색은 유지하고 모델링용 중립광을 사용했습니다. 무기는 별도 소품입니다.</p><p>모델 생성 후 긴 소매와 겨드랑이, 치마 속 두 다리, 가려진 팔다리, 갓끈·탈·부적의 두께와 접합을 확인하세요. 이 묶음은 입력 이미지 검수까지 완료한 상태입니다.</p><p>박쥐·흑랑은 기존 <a href="../16_bat_input.png">날개 펼침</a> · <a href="../18_heukrang_input.png">네 발 입력</a>을 사용합니다.</p><p class="small"><a href="https://docs.meshy.ai/en/api/multi-image-to-3d">Meshy 공식 안내</a> · <a href="https://platform.tripo3d.ai/docs/generation">Tripo 공식 안내</a></p></div></details></main><footer><a href="README.md">제작·업로드 안내</a> · <a href="PROMPTS.md">프롬프트·참조</a> · <a href="manifest.json">파일·해시</a> · <a href="validation.json">검증 결과</a><p>Built-in image_gen / H1 입력 파생본 / 2026.09.17 · 이미지 24장 / 수정 전 3장 별도 보존 · Meshy·Tripo 업로드·모델 생성 없음.</p></footer></body></html>'''
write("index.html",page)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ("src","href"):self.refs.append(value)
parser=Links();parser.feed(page)
links=[]
for url in parser.refs:
 bits=urlsplit(url)
 if bits.scheme or not bits.path:continue
 exists=(ROOT/unquote(bits.path)).resolve().exists() or bits.path=="validation.json"
 links.append({"url":url,"exists":exists})
assert all(x["exists"] for x in links)
checks=[{"file":r["file"],"sha256":r["sha256"],"copy_hash_matches":True,"width":r["width"],"height":r["height"]} for r in rows]
validation={"active_images":24,"archived_rejected_images":3,"generated_final_images":20,"reused_images":4,"pixel_edits_local":False,"unique_character_view_pairs":24,"per_character_view_dimensions_equal":True,"visual_qa":"root + independent agent inspection passed; 3D untested","checks":checks,"archives":zip_reports,"local_links":links,"pending_3d":["Occluded limbs","Skirt legs and sleeve armpits","Thin cords, mask and talismans","Hands and weapon grip","Cloth and hair continuity between views"]}
write("validation.json",json.dumps(validation,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"final_png":24,"archive_png":3,"zip_files":len(zip_reports),"local_links":len(links),"all_hashes_and_zip_contents_pass":True,"output":str(ROOT)},ensure_ascii=False))

