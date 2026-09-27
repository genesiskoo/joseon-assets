from pathlib import Path
from PIL import Image
import hashlib
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
ctx = json.loads((main / "tmp/seal_intake_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
source_repo = Path("C:/workspace/joseon-assets")
source = source_repo / "workbench/production/item_icons_454"
production = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
report = assets / f"reports/{card}/integration_2026-09-27"
snapshot = json.loads((report / "before_snapshot.json").read_text(encoding="utf-8"))
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target_ids = {e["item_id"] for e in production["items"]}
assert target_ids == {"seal_heukrang", "seal_jangsanbeom", "seal_bulgasari"}
for rel, digest in snapshot["files"].items():
    assert sha(game / rel) == digest, rel
commands = []
for item in production["items"]:
    id = item["item_id"]
    assert re.fullmatch("[a-z_]+", id)
    src, dest = source / f"game/items/{id}.png", game / f"assets/sprites/ui/icons_a/items/{id}.png"
    assert sha(src) == item["game_sha256"] and not dest.exists()
    commands.append(f"Copy-Item -LiteralPath '{src}' -Destination '{dest}'")
copy_script = main / "tmp/seal_copy.ps1"
copy_script.write_text("$ErrorActionPreference = 'Stop'\n" + "\n".join(commands) + "\n", encoding="utf-8-sig")
p = subprocess.run(["powershell.exe", "-NoProfile", "-File", str(copy_script)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(report / "copy_raw.log").write_bytes(p.stdout)
assert p.returncode == 0, p.stdout

def semantic(text):
    return "\n".join(line for line in text.splitlines() if line.strip() and not line.startswith("[gd_resource ") and not line.startswith("icon = ") and not ('[ext_resource type="Texture2D"' in line and f'id="art{card}"' in line))

records = []
for item in production["items"]:
    id = item["item_id"]
    dest = f"assets/sprites/ui/icons_a/items/{id}.png"
    assert sha(game / dest) == item["game_sha256"]
    im = Image.open(game / dest)
    assert im.mode == "RGBA" and im.size == (80, 80) and im.getchannel("A").getextrema() == (0, 255)
    definition = f"data/items/{id}.tres"
    p = game / definition
    old = p.read_text(encoding="utf-8")
    base = subprocess.check_output(["git", "show", f"{ctx['game_base']}:{definition}"], cwd=game).decode("utf-8")
    assert old == base and "icon = " not in old
    new = re.sub(r"load_steps=(\d+)", lambda m:f"load_steps={int(m[1]) + 1}", old, count=1)
    new = new.replace("\n[resource]", f'\n[ext_resource type="Texture2D" path="res://{dest}" id="art{card}"]\n\n[resource]', 1)
    new = new.replace('script = ExtResource("1")\n', f'script = ExtResource("1")\nicon = ExtResource("art{card}")\n', 1)
    assert semantic(old) == semantic(new) and new != old
    p.write_text(new, encoding="utf-8", newline="\n")
    records.append({"data_id":id, "display_name":item["display_name"], "definition":definition, "source":f"workbench/production/item_icons_454/game/items/{id}.png", "destination":dest, "sha256":item["game_sha256"], "game_size":[80,80], "footprint":[1,1], "max_stack":1, "quest_item":True, "previous_icon":None, "definition_before_sha256":hashlib.sha256(old.encode()).hexdigest(), "non_icon_fields_sha256":hashlib.sha256(semantic(old).encode()).hexdigest(), "definition_after_sha256":sha(p), "unchanged_except_icon":True})
p = game / "tests/test_items.gd"
body = p.read_text(encoding="utf-8")
match = re.search(r"const ICON_PENDING := \[(.*?)\]", body, re.S)
assert match and set(re.findall(r'"([^"]+)"', match[1])) == target_ids
body = body[:match.start()] + "const ICON_PENDING := []" + body[match.end():]
body = body.replace("## #453: 승인 재료6종 반입 완료. 아이콘 대기 = 봉인조각3, 모델 대기는 그대로.", f"## #{card}: 승인 봉인물3 반입으로 모든 현재 ItemDef에 아이콘이 있다. 모델 대기는 그대로.")
p.write_text(body, encoding="utf-8", newline="\n")
other_defs = [{"path":r, "sha256":digest} for r, digest in snapshot["files"].items() if r.endswith(".tres") and Path(r).stem not in target_ids]
prior_png = [{"destination":r, "sha256":digest} for r, digest in snapshot["files"].items() if r.endswith(".png")]
assert len(other_defs) == 64 and len(prior_png) == 35
intake = game / f"art/ui_intake_{card}"
intake.mkdir(parents=True, exist_ok=True)
(intake / "intake_manifest.json").write_text(json.dumps({"issue":card, "production_issue":454, "source_repository":"joseon-assets", "source_commit":ctx["source_commit"], "game_base":ctx["game_base"], "approval":ctx["approval"], "method":"PowerShell Copy-Item of approved PNG bytes; ItemDef.icon only; existing UiSkin alpha-region drawing", "files":records, "previous_assets_unchanged":prior_png, "other_definitions_unchanged":other_defs}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
p = game / "docs/TASK_CURRENT.md"
p.write_text(p.read_text(encoding="utf-8") + f"\n- 2026-09-27 #{card} `icons_a/items` ← `C:\\workspace\\joseon-assets\\workbench\\production\\item_icons_454\\game\\items` (승인 {ctx['source_commit'][:8]}) → 봉인물3PNG·ItemDef.icon. 퀘스트/쌓기1/점유/가격/드랍/모델·기존35PNG·다른정의64 보존.\n", encoding="utf-8", newline="\n")
print(f"PASS #{card}: approved PNG3/non-icon fields3/other .tres64/previousPNG35; icon pending3→0; model pending unchanged.")
