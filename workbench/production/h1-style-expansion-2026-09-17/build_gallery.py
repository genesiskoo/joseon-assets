import json, html, pathlib, hashlib
ROOT = pathlib.Path(r"C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17")
def esc(v): return html.escape(str(v), quote=True)
manifest = json.loads((ROOT/"manifest.json").read_text(encoding="utf-8-sig"))
active = [r for r in manifest["records"] if r["status"] != "superseded"]
old = [r for r in manifest["records"] if r["status"] == "superseded"]
style = """*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#141719;color:#e7e0d5;font:16px/1.65 system-ui,'Malgun Gothic',sans-serif}a{color:#b4cfda;text-underline-offset:4px}header,main,footer{max-width:1280px;margin:auto;padding:32px}header{padding-top:52px}.eyebrow{font-size:12px;letter-spacing:.16em;color:#b39b74}h1{font-size:44px;line-height:1.25;margin:12px 0}h2{font-size:27px;margin:0 0 10px}h3{font-size:18px;margin:10px 0}.muted{color:#aeb9bb}.summary{max-width:950px}nav{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}nav a,.button{display:inline-block;border:1px solid #44484b;border-radius:5px;padding:8px 13px;text-decoration:none;color:#d4ddd9}.hero{width:100%;display:block;border-radius:8px}.hero-caption{display:flex;justify-content:space-between;gap:16px;color:#bec7c6;font-size:14px;margin:12px 0}.note{background:#202527;border-left:3px solid #ab9069;padding:16px 20px;border-radius:3px}.section{margin:42px 0;scroll-margin-top:20px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.card{background:#202527;border:1px solid #373e41;border-radius:7px;overflow:hidden}.card img{width:100%;height:350px;object-fit:contain;background:#101315;display:block}.card .body{padding:14px 20px}.tag{font-size:12px;color:#acbdc2}.qa{font-size:14px;color:#bac4c6}details{margin:10px 0}summary{cursor:pointer}.portrait-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px;margin-top:24px}.portrait{background:#24292d;padding:20px;text-align:center;border:1px solid #3d4548;border-radius:7px}.portrait svg{width:128px;height:128px;display:block;margin:0 auto;background:#303333}.portrait p{font-size:14px;margin:10px 0 0}.small{font-size:14px}.old .grid img{height:200px}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #394144;text-align:left;padding:12px}footer{font-size:13px;color:#aeb8ba;border-top:1px solid #373e41}@media(max-width:740px){header,main,footer{padding:22px}h1{font-size:32px}.grid{grid-template-columns:1fr}.card img{height:auto}.portrait-row{grid-template-columns:repeat(2,minmax(0,1fr))}.portrait{padding:12px}.hero-caption{display:block}}"""
def page(title, body):
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+style+'</style></head><body>'+body+'</body></html>'
def card(r):
    label = "재질 적용 시험 후보" if r["id"] == "H1-TEX01" else ("중립 3D 입력 / 원화 검수" if "input_" in r["status"] else "목표 원화 / 시각 검수")
    return '<article class="card"><a href="'+esc(r["file"])+'"><img loading="lazy" src="'+esc(r["file"])+'" alt="'+esc(r["title"])+'"></a><div class="body"><span class="tag">'+esc(r["id"])+' · '+label+'</span><h3>'+esc(r["title"])+'</h3><details><summary class="small">검수 기록</summary><p class="qa">'+esc(r["qa"])+'</p><p class="small">'+str(r["width"])+' × '+str(r["height"])+' px</p></details></div></article>'
def section(sid,title,intro,items):
    return '<section class="section" id="'+sid+'"><h2>'+title+'</h2><p class="muted">'+intro+'</p><div class="grid">'+''.join(card(r) for r in items)+'</div></section>'
groups = [
("cast","PC · NPC · 구미호","각 인물의 복장·성격·연령을 유지하며 H1의 선과 무광 명암으로 연결했습니다.",[r for r in active if r["stage"] in (3,4) or r["id"]=="H1-X01r1"]),
("environment","못골 · 석실","통합 장면은 목표 원화입니다. 아래의 실제 3D 렌더와 구분해 비교할 수 있습니다.",[r for r in active if r["id"] in ("H1-X02r1","H1-X03r1","H1-BG01","H1-BG02","H1-TEX01")]),
("enemy","적 · 분리 소품","슬라이스 적 4종과 검·검집·곤봉·부적을 제작했습니다. 적 4종의 Meshy 전송은 명시 승인 대기입니다.",[r for r in active if r["id"].startswith("H1-E") or r["id"]=="H1-P01"]),
("story","컷씬 · 초상","봉인 벽은 기존 스토리 컷4입니다. 초상 8종은 얼굴 중심 크롭으로 별도 128px 표시 시험을 제공합니다.",[r for r in active if r["id"] in ("H1-CS04","H1-UI01")])]
body='<header><div class="eyebrow">JOSEON HUNTERS · H1 ART EXPANSION · 2026.09.17</div><h1>H1에서 한 세계로</h1><p class="summary">최신 원화 <strong>'+str(len(active))+'장</strong> · PC 3인 · NPC 3인 · 구미호 전후 · 마을·던전 · 적 4종 · 키아트·컷씬·초상</p><nav><a href="00_style_anchor.html">H1 기준표</a><a href="#cast">캐릭터</a><a href="#environment">배경</a><a href="#enemy">적·소품</a><a href="#story">컷씬·초상</a><a href="#runtime">실제 3D</a><a href="portraits_128.html">초상 128px</a></nav><a href="20_keyart.png"><img class="hero" src="20_keyart.png" alt="H1 도호가 중심에 선 귀새·청연 3인방 키아트"></a><div class="hero-caption"><span>H1-K01r1 · 도호 중심 키아트 / 원화 검수 통과</span><span>게임 화면 · 클래스 선택 화면과 구분</span></div><div class="note">H1 공통 화풍은 고정했습니다. 이 묶음은 제작 후보이며 원화 검수와 실제 3D 합격을 구분합니다. 공식 게임 자산은 교체하지 않았습니다.</div></header><main>'
for args in groups: body+=section(*args)
body+='<section class="section" id="runtime"><h2>실제 3D 시험</h2><p class="muted">독립 Godot 씬에서 실제 모델·카메라·조명을 캡처했습니다.</p><div class="note">도호·상인: 24본과 대기·이동·공격 재생 확인. 도호의 주먹과 검 연결을 교정했습니다. 손끝 조형·의복 겹침·상인 외형과 폴리곤/텍스처 예산은 추가 보완이 필요합니다. 환경·소품도 게임 반입 전의 제작 후보입니다.</div><nav><a href="3d_trial/review.html">인물 3D 상세 비교</a><a href="3d_trial/README.md">인물 검사·한계·비용</a>'
if (ROOT/"3d_modules/README.md").exists(): body+='<a href="3d_modules/README.md">환경·소품 3D 명세</a>'
body+='<a href="3d_enemies/README.md">적 3D 전송 승인 대기</a></nav><div class="grid">'
runtime=[("3d_trial/captures/fist_final_baseline/h1_trial_idle_01.png","인물 / 실제 카메라·기본광","1280×720 · 직교11 · 독립 씬, 주먹 교정과 원본 3클립 보존"),
("3d_trial/captures/fist_final_neutral/h1_trial_idle_01.png","인물 / 근접 중립 검사","얼굴·옷·손·재질 결함 확인용 조명. 게임광 판정과 별도"),
("3d_modules/captures/02_town_assembly.png","마을 / 모듈 조합","H1 목재·기와·한지 재질의 실제 UV 적용 시험"),
("3d_modules/captures/01b_town_catalog.png","마을 / 중립 재질 검사","목재·기와·회벽·한지 구분. 옹기는 무광 단색 후보 유지"),
("3d_modules/captures/03_dungeon_assembly.png","던전 / 모듈 조합","기존 돌 재질을 재사용한 독립 3D 장면"),
("3d_modules/captures/07_props_catalog.png","검·검집·곤봉·부적 / 분리 모델","개별 부착용 원점·축과 소품별 형상을 확인한 후보"),
("3d_modules/captures/11_h1_socket_attack_01.png","도호 / 공격 중 검 연결","교정한 H1 주먹에 제작 검을 연결한 실제 동작 캡처"),
("3d_trial/captures/fist_final_grip/h1_trial_attack_01.png","검 그립 / 확대 검사","주먹과 손잡이 접촉 확인. 손끝 모양은 후속 보완 항목")]
for file,title,qa in runtime:
 if (ROOT/file).exists(): body+='<article class="card"><a href="'+file+'"><img loading="lazy" src="'+file+'" alt="'+title+'"></a><div class="body"><span class="tag">실제 3D 렌더</span><h3>'+title+'</h3><p class="qa">'+qa+'</p></div></article>'
body+='</div></section><details class="section old"><summary>이전 시안·수정 이력 '+str(len(old))+'장</summary><p class="muted">현재 제작 기준은 위의 수정본입니다. 초기 파일은 검수 이력으로 보존했습니다.</p><div class="grid">'+''.join(card(r) for r in old)+'</div></details></main><footer><a href="PROMPTS.md">정확한 프롬프트·참조 순서·QA</a> · <a href="manifest.json">파일·해시 명세</a> · <a href="generations.csv">생성 기록</a><p>원화: built-in image_gen, 참조 기반 생성 및 부분 수정. 실제 모델 ID는 노출되지 않습니다. H1 승인 원본은 수정하지 않았습니다.</p></footer>'
(ROOT/"index.html").write_text(page("H1 아트 확장 · 조선헌터스",body),encoding="utf-8")
portraits=[("도호",22,16),("귀새",434,16),("청연",845,16),("구미호 F01",1256,16),("김 영감",22,471),("무당 할매",434,471),("촌장",845,471),("구미호 F03",1256,471)]
pbody='<header><div class="eyebrow">PORTRAIT READABILITY / H1</div><h1>초상 128px 표시</h1><p>같은 원화를 실제 CSS 128×128px로 표시합니다. 얼굴·나이·대표 소품의 식별을 확인하는 페이지입니다.</p><nav><a href="index.html">전체 갤러리</a><a href="22_portraits.png">원본 8칸 시트</a></nav></header><main><div class="portrait-row">'
for name,x,y in portraits:
 pbody+='<article class="portrait"><svg role="img" aria-label="'+name+'" viewBox="'+str(x)+' '+str(y)+' 395 395" xmlns="http://www.w3.org/2000/svg"><image href="22_portraits.png" width="1672" height="941"/></svg><p>'+name+'</p></article>'
pbody+='</div><p class="note">얼굴 우선 크롭: 갓 끝·모자 윗부분은 일부 잘립니다. 별도 UI 프레임, 투명 배경 파일, 표정 애니메이션이나 게임 적용까지 완료한 상태는 아닙니다.</p></main><footer>원본 PNG의 재생성·보정 없이 표시 영역만 사용했습니다.</footer>'
(ROOT/"portraits_128.html").write_text(page("H1 초상 128px 검수",pbody),encoding="utf-8")
checks=[]
for r in manifest["records"]:
 path=ROOT/r["file"]
 checks.append({"id":r["id"],"exists":path.exists(),"sha256_matches":hashlib.sha256(path.read_bytes()).hexdigest().upper()==r["sha256"].upper()})
(ROOT/"delivery_check.json").write_text(json.dumps({"active_images":len(active),"superseded_images":len(old),"image_checks":checks,"generated_png_edited_locally":False},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"active":len(active),"iterations":len(old),"hash_pass":all(c["sha256_matches"] for c in checks)},ensure_ascii=False))
