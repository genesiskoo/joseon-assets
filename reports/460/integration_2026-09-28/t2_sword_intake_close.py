from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path("C:/workspace/joseon")
ctx_file = root / "tmp/t2_sword_intake_context.json"
ctx = json.loads(ctx_file.read_text(encoding="utf-8"))
game, assets, report = [Path(ctx[k]) for k in ["game", "assets", "report"]]
assets_main = Path("C:/workspace/joseon-assets")
env = dict(os.environ, PYTHONIOENCODING="utf-8")

def run(tree, args):
    p = subprocess.run(args, cwd=tree, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode:
        print(p.stdout.decode("utf-8-sig", errors="replace"), end="", flush=True)
        raise SystemExit(p.returncode)
    return p.stdout

head = lambda tree: run(tree, ["git", "rev-parse", "HEAD"]).decode().strip()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
land = json.loads((report / "run_land.json").read_text(encoding="utf-8"))
assert land["exit_code"] == 0 and sha(report / land["raw_log"]) == land["raw_sha256"]
log = (report / land["raw_log"]).read_text(encoding="utf-8-sig")
assert "✅ 착륙" in log and "✓ 본진 임포트" in log and "✓ 부팅 검사 SCRIPT ERROR 0" in log and "오토로드 10/10" in log and "주 장면 OK" in log
assert head(root) == head(game) == ctx["game_candidate"]
assert not run(root, ["git", "status", "--porcelain"]).strip()
manifest = json.loads((root / "art/ui_intake_460/intake_manifest.json").read_text(encoding="utf-8"))
for item in manifest["files"]:
    assert sha(root / item["destination"]) == item["sha256"]
    assert (root / item["definition"]).read_text(encoding="utf-8") == (game / item["definition"]).read_text(encoding="utf-8")
for rel, digest in manifest["protected_files"].items():
    a, b = (root / rel).read_bytes(), (game / rel).read_bytes()
    assert sha(game / rel) == digest
    assert (a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n") if rel.endswith(".tres") else a == b), rel
for rel, digest in manifest["old_h1_icons_preserved"].items():
    assert sha(root / rel) == digest
game_head = head(root)
data_path = report / "verification.json"
data = json.loads(data_path.read_text(encoding="utf-8"))
data["landing"] = {"game_main": game_head, "run": land, "main_import_and_boot": "PASS: main import, SCRIPT ERROR0, autoload10/10, main sceneOK", "main_vs_tested_wt": "approved PNG4 exact bytes and definition4 exact normalized text; other63tres canonical line endings and previous38PNG exact bytes; H1PNG3 exact bytes"}
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
qa = root / "docs/art/460_d1_t2_sword_intake/QA.md"
body = qa.read_text(encoding="utf-8")
assert "## 최종 착륙 기록" not in body
body += f"\n## 최종 착륙 기록\n\n게임 main `{game_head}` 착륙 완료. 승인 PNG4와 그림 외 필드4를 작업 트리와 본진에서 다시 대조했다. 기존 PNG38/H1검3은 동일 바이트, 다른tres63은 Windows 줄끝을 정규화한 동일 내용이다. 본진 임포트·부팅 SCRIPT ERROR0·오토로드10/10·주 장면OK. 착륙 명령·시간·raw SHA는 자산 reports/460/integration_2026-09-28/run_land.json. #460 완료, #274 핵심잔여51. 미push.\n"
qa.write_text(body, encoding="utf-8", newline="\n")
shutil.copy2(qa, assets / "docs/art/460_d1_t2_sword_intake/QA.md")
shutil.copy2(qa, report / "QA.md")
for name in ["t2_sword_intake_commit.py", "t2_sword_intake_close.py"]:
    shutil.copy2(root / "tmp" / name, report / name)
for mode in ["import", "unit", "e2e", "gate", "land"]:
    meta = json.loads((report / f"run_{mode}.json").read_text(encoding="utf-8"))
    assert meta["exit_code"] == 0 and sha(report / meta["raw_log"]) == meta["raw_sha256"]
production = assets / "workbench/production/item_icons_459"
p = production / "ACCEPTANCE.md"
accepted = p.read_text(encoding="utf-8")
assert "## #460 게임 반입 완료" not in accepted
accepted += f"\n## #460 게임 반입 완료 — 2026-09-28\n\n위 문단의 ‘현재 게임은 옛 그림’은 #459 채택 당시 기록이다. 후속 #460에서 승인80×240 RGBA4를 바이트 그대로 복사하고 기존 Texture2D 경로만 연결했다. 게임 main `{game_head}`. 1×3/수치/양손/보조칸/가격/바닥 모델과 기존101파일/H1검3 보존, 실제 입력 전78/후86, 단위53/관련E2E11·{data['validation']['related_checks']}검사/빠른부팅·러너5/본진임포트·부팅 PASS. 전후3쌍 및 raw는 reports/460/integration_2026-09-28, 사진·검수는 docs/art/460_d1_t2_sword_intake. #274핵심잔여51. 미push.\n\n게임 반입 카드: https://github.com/genesiskoo/joseon-hunters/issues/460\n"
p.write_text(accepted, encoding="utf-8", newline="\n")
p = production / "README.md"
p.write_text(p.read_text(encoding="utf-8") + "\n후속 반입(2026-09-28): 승인 검4는 #460 게임 main에 적용 완료. 원본/패킹/최초 후보 기록을 보존하고 최종 반입 결과는 [ACCEPTANCE.md](ACCEPTANCE.md)에 추가했다.\n", encoding="utf-8", newline="\n")
assert not run(assets_main, ["git", "status", "--porcelain", "--untracked-files=no"]).strip()
run(assets, ["git", "add", "--", "reports/460", "docs/art/460_d1_t2_sword_intake", "workbench/production/item_icons_459/ACCEPTANCE.md", "workbench/production/item_icons_459/README.md"])
run(assets, ["git", "diff", "--cached", "--check", "--", ".", ":(exclude)reports/460/**/*.log"])
run(assets, ["git", "commit", "-m", "test(#460): 검4 반입 전후·실제 입력·보존·회귀·착륙 증거"])
run(assets, ["git", "rebase", "main"])
assets_head = head(assets)
run(assets_main, ["git", "merge", "--ff-only", assets_head])
for p in report.glob("*.log"):
    rel = p.relative_to(assets).as_posix()
    blob = run(assets, ["git", "show", f"HEAD:{rel}"])
    assert blob == p.read_bytes(), rel
assert not run(assets, ["git", "status", "--porcelain"]).strip()
state = root / "docs/STATE.md"
text = state.read_text(encoding="utf-8")
assert "#460 검4 게임" not in text
text = text.replace("## 이번 주 (2026-09-27 기준)", "## 이번 주 (2026-09-28 기준)", 1)
text = text.replace("실제 게임 반입은 별도 후속 카드·미push.", "실제 게임 반입 #460 완료·미push.", 1)
line = f"- 2026-09-28 Codex: #460 검4 게임{game_head[:8]}·검수{assets_head[:8]} 착륙. 승인SHA/그림외필드4·기존101파일/H1검3·기준픽셀3 보존. 실제착용/양손/거래/Alt회수 전78·후86/단위53/관련E2E11({data['validation']['related_checks']})/부팅·러너5 PASS·전후6JPG. 아이콘대기0·42PNG, 미push.\n"
text = text.replace("## 이번 주 (2026-09-28 기준)\n", "## 이번 주 (2026-09-28 기준)\n" + line, 1)
text = re.sub(r"^- Codex #160·#445~#450.*$", "- Codex #160·#445~#450·#452~#454·#457~#460 완료. #451 부적표적은 별도PD. #274핵심잔여51/현재ItemDef아이콘대기0, 검4 게임반입 완료. #273창3은 #265/#266/#267, #392는 #391 대기. 다음은 보드 선행·PD댓글 확인.", text, flags=re.M)
assert all(len(s) <= 300 for s in text.splitlines())
state.write_text(text, encoding="utf-8", newline="\n")
print(run(root, [sys.executable, "tools/doc_budget.py"]).decode("utf-8-sig"), end="", flush=True)
run(root, ["git", "add", "--", "docs/STATE.md", "docs/art/460_d1_t2_sword_intake/QA.md"])
run(root, ["git", "diff", "--cached", "--check"])
run(root, ["git", "commit", "-m", "docs(#460): 검4 반입 착륙과 다음 상태 저장"])
ctx.update(status="completed_and_landed", game_landed=game_head, assets_landed=assets_head, state_landed=head(root), core_remaining=51, actual_game_intake=True)
ctx_file.write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
message = f"#459 승인 검4의 #460 게임 반입 완료. main {game_head[:8]}, 검수 assets {assets_head[:8]}. 승인PNG4/기존Texture2D경로만·그림 외 필드4/기존101파일/H1검3/기준픽셀3 보존. 실제 입력 전78/후86, 단위53/관련E2E11·{data['validation']['related_checks']}검사/빠른부팅·러너5/본진임포트·부팅 PASS. 전후6JPG: docs/art/460_d1_t2_sword_intake. 원본/raw/초기fixture실패: reports/460/integration_2026-09-28. icons_a42(아이템36+스킬6), 현재아이콘대기0, #274핵심잔여51. 미push."
for card in [460, 459, 274]:
    print(run(root, [sys.executable, "tools/board.py", "note", str(card), message]).decode("utf-8-sig"), end="", flush=True)
assert not run(root, ["git", "status", "--porcelain"]).strip()
assert not run(assets_main, ["git", "status", "--porcelain", "--untracked-files=no"]).strip()
print("PASS #460: game+assets main landed; raw Git blobs byte-identical; main clean; unrelated untracked assets preserved; board/state complete.")
print(json.dumps({k: ctx[k] for k in ["game_landed", "assets_landed", "state_landed", "core_remaining"]}), flush=True)
