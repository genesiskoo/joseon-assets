from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
root=Path("C:/workspace/joseon")
ctx=json.loads((root/"tmp/dialogue_243_context.json").read_text(encoding="utf-8"))
game,assets,prod,report,gallery=[Path(ctx[k]) for k in ["game","assets","production","report","gallery"]]
manifest=json.loads((prod/"manifest.json").read_text(encoding="utf-8"))
assert len(manifest["items"])==5
font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",22)
face=Image.new("RGB",(1280,760),(24,22,21));d=ImageDraw.Draw(face)
d.text((24,12),"#243 얼굴 표정 대조 — 위 도호 / 아래 김 영감",font=font,fill=(225,208,178))
labels={"neutral":"중립","smug":"능청","serious":"진지","smile":"미소"}
for actor,row,rect in [("doho",0,(425,190,780,565)),("merchant",1,(355,220,665,520))]:
    group=[e for e in manifest["items"] if e["actor"]==actor]
    for i,e in enumerate(group):
        im=Image.open(prod/e["source"]).crop(rect)
        im.thumbnail((340,260),Image.Resampling.LANCZOS)
        x=60+i*410; y=60+row*345
        face.paste(im,(x,y),im)
        d.text((x,y+265),labels[e["expression"]],font=font,fill=(221,214,200))
p=gallery/"face_expressions.jpg";face.save(p,quality=88,optimize=True)
assert p.stat().st_size<=300_000
shutil.copyfile(p,report/p.name)
shots=json.loads((report/"preview_capture.json").read_text(encoding="utf-8"))
for actor in ["doho_smug","merchant_smile","doho_serious"]:
    source=report/f"preview_{actor}.png"
    im=Image.open(source).convert("RGB");im.thumbnail((1280,720),Image.Resampling.LANCZOS)
    dest=gallery/f"preview_{actor}.jpg";im.save(dest,quality=86,optimize=True)
    assert dest.stat().st_size<=300_000
    shutil.copyfile(dest,report/dest.name)
gallery_files=list(gallery.glob("*.jpg"))
assert len(gallery_files)<=6 and sum(p.stat().st_size for p in gallery_files)<=2_000_000
changed=subprocess.run(["git","diff",ctx["game_base"],"--name-only","--","assets","data","core","ui","world","items"],cwd=game,capture_output=True,check=True).stdout.decode().strip()
assert not changed, changed
protected=[]
for directory in ["assets/sprites/ui/icons_a","assets/portraits","data/portraits"]:
    for p in sorted((game/directory).rglob("*")):
        if p.is_file() and not p.name.endswith(".import"):
            protected.append({"path":p.relative_to(game).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
for ref in ctx["references"].values():
    saved=assets/ref["saved"]
    assert hashlib.sha256(saved.read_bytes()).hexdigest()==ref["sha256"]
    assert saved.read_bytes()==Path(ref["original"]).read_bytes()
report_manifest={"card":243,"checks":{"portraits":5,"rgba1024x1536":True,"top8percent_common_placement":True,"common_pose_per_character":True,"expressions_differ":True,"transparent_alpha_preserved":True,"original_references_exact":True,"runtime_diff_empty":True,"dialogue_render_captures":5,"script_engine_errors":0},"protected_runtime_files":protected,"gallery":[{"path":p.name,"bytes":p.stat().st_size} for p in gallery_files],"expression_metrics":manifest["expression_comparisons"],"preview_limit":"Existing dialogue renderer used with static image anchors adapted ONLY in separate QA process; legacy idle shadow hidden. Does not prove unchanged renderer can intake these crops without an anchor update.","adoption":"pilot pending PD; no runtime intake or full-cast expansion"}
(report/"QA.json").write_text(json.dumps(report_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
readme="""# #243 대화 초상 파일럿 — PD 확인 후보

도호3(neutral·smug·serious), 김 영감2(neutral·smile). 각 1024×1536 투명 RGBA, 머리 위 8% 여백, 같은 인물끼리 공통 배율/위치, 도호 우측·김 영감 좌측 시선. 기존 H1/B1 전신 원본을 정체성/복장/화풍 기준으로 사용했다. 새 중립 초상에서 native image_gen 표정 편집으로 파생했고 중립 프레이밍 초안·구분이 약한 첫 미소는 source에 따로 보존했다. 최종은 game/<id>/<expression>.png다.

검수: 원본 알파0~254·1024×1536 보존, 공통 배치 후 상단123px, 모자/손/검/장부/허리 장식과 좌우 시선 직접 대조. 표정 간 실루엣 IoU는 manifest에 실측했다. native 재채색으로 얼굴 밖의 미세한 색/가장자리 차이가 있으며 완전 동일 픽셀은 아니다. 자세/소품 기하는 유지한다. 이 차이를 숨기거나 코드로 얼굴만 합성하지 않았다.

실제 Godot 대화 띠에 ImageTexture를 메모리로 주입해 5장 촬영했다. 새 허벅지 절단 초상은 기존 전신 idle 발 기준 앵커와 맞지 않아 외부 QA 프로세스에서만 가상 발 앵커를 조정하고 옛 idle 그늘을 숨겼다. 게임 파일·PortraitDef·현재 icons_a42PNG는 바뀌지 않았다. 실게임 반입은 채택 후 별도 claude 카드에서 static 앵커·그늘·intake_portrait 도구를 먼저 마련해야 한다. tools/intake_portrait.ps1은 현재 없다. 전원 확장은 파일럿 판정 뒤 진행한다.

왜 이 구조인가: 인물별 중립을 하나의 자세 기준으로 쓰면 표정마다 모자·손·검이 다른 자리에 생기는 문제를 줄인다. 표정별 인물 전체 독립 재생성은 비율과 소품 이동 위험이 커서 기각했다. 파생 PNG와 원본·프롬프트·해시를 분리 보존해 게임 반입 시 승인 파일을 정확히 재현한다.

프롬프트/네이티브 생성 경로와 원본 SHA: PROMPTS.md·generation_sources.json. 최종 PNG/패킹/실루엣 측정: manifest.json. raw 로그·전환5장·검수판: reports/243/2026-09-28. 대화 검토판6JPG: 게임 docs/art/243_dialogue_portraits. 코드 시험/전체 E2E는 실행하지 않았다(런타임 수정 없음); 외부 미리보기 부팅·5표정 렌더·SCRIPT ERROR/ERROR 0·문서 예산 검사를 사용했다.
"""
(prod/"README.md").write_text(readme,encoding="utf-8",newline="\n")
for name in ["dialogue_243_collect.py","dialogue_243_pack.py","dialogue_243_finish.py"]:
    shutil.copyfile(root/"tmp"/name,report/name)
(gallery/"README.md").write_text("# #243 대화 초상 파일럿\n\n신규 후보 검토판6JPG. 원본/최종5PNG/프롬프트/해시는 joseon-assets workbench/production/dialogue-portraits-235, raw와5표정 전환은 reports/243/2026-09-28. 기존 그림은 그대로이며 게임 반입 전 후보이다. preview_*.jpg는 실제 대화 띠의 외부 QA 프로세스에서만 static 앵커를 조정하고 옛 idle 그늘을 숨긴 검토 사진이다.\n",encoding="utf-8",newline="\n")
print("PASS #243 portraits5; originals exact; protected runtime",len(protected),"files; gallery",len(gallery_files),"JPG",sum(p.stat().st_size for p in gallery_files),"bytes; candidate only")
