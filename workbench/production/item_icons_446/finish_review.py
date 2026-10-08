"""Record #446's real image and Godot QA evidence. Never alters game art."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def put(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


def finish(root: Path) -> None:
    assets = root.parents[2]
    report = assets / "reports/446/integration_2026-09-27"
    gallery = assets / "docs/art/446_d1_items_t1"
    gallery.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    generation = json.loads((root / "generation_sources.json").read_text(encoding="utf-8"))
    assert generation["count"] == len(generation["items"]) == len(manifest["items"]) == 6
    generated = {r["id"]: r for r in generation["items"]}
    for item in manifest["items"]:
        id = item["item_id"]
        src = root / "source/items" / (id + ".png")
        dst = root / "game/items" / (id + ".png")
        assert sha(src) == item["source_sha256"] == sha(Path(generated[id]["generated_path"]))
        assert sha(dst) == item["game_sha256"]
        assert sha(Path(item["definition_path"])) == item["definition_sha256"]
        with Image.open(dst) as im:
            im.verify()
        im = Image.open(dst)
        assert im.size == (80 * item["grid_w"], 80 * item["grid_h"])
        assert im.getchannel("A").getextrema() == (0, 255)
    frames = {}
    for mode, height in [("before", 720), ("after", 720), ("sizes", 790)]:
        log = report / f"godot_{mode}.log"
        err = report / f"godot_{mode}_errors.log"
        text = log.read_text(encoding="utf-8", errors="replace")
        assert "GODOT_D1_446 PASS" in text and "Godot Engine v4.7.2" in text
        assert not err.read_text(encoding="utf-8", errors="replace").strip()
        assert "ERROR" not in text
        p = root / "qa" / f"godot_{mode}.png"
        assert Image.open(p).size == (1280, height)
        frames[mode] = {"sha256": sha(p), "size": [1280, height], "stderr_bytes": err.stat().st_size}
    before = Image.open(root / "qa/godot_before.png").convert("RGB")
    after = Image.open(root / "qa/godot_after.png").convert("RGB")
    same_refs = ImageChops.difference(before.crop((20, 535, 1260, 718)), after.crop((20, 535, 1260, 718))).getbbox() is None
    assert same_refs, "approved reference plate changed between before/after"
    sheets = {"overview": root / "qa/overview.png", "before": root / "qa/godot_before.png",
              "after": root / "qa/godot_after.png", "sizes": root / "qa/godot_sizes.png"}
    pictures = []
    for name, source in sheets.items():
        target = gallery / f"{name}.jpg"
        Image.open(source).convert("RGB").save(target, quality=85, optimize=True)
        assert target.stat().st_size <= 300 * 1024
        assert Image.open(target).width == 1280
        shutil.copy2(source, report / source.name)
        shutil.copy2(target, report / target.name)
        pictures.append({"name": name, "bytes": target.stat().st_size, "sha256": sha(target)})
    verification = {"card": 446, "parent": 274, "game_baseline": "ec50b082",
                    "assets_baseline": "82558ef", "generated_assets": 6,
                    "original_copy_hashes": "6/6", "immutable_game_definition_hashes": "6/6",
                    "packed_alpha_and_footprints": "6/6", "actual_godot_renderer": "4.7.2 Compatibility",
                    "render_cases": frames, "same_before_after_approved_refs": same_refs,
                    "gallery": pictures, "game_installation": False,
                    "source_manifest_sha256": sha(root / "generation_sources.json"),
                    "item_manifest_sha256": sha(root / "manifest.json")}
    put(report / "verification.json", json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
    put(gallery / "README.md", """# #446 D1 소지품 확장 1차\n\n현재 T1 6종의 후보: 삿갓·피주·인장·예도·미투리·전대. 확대 원화는 overview.jpg, 기존/후보 같은 구도는 before.jpg / after.jpg, 작은 크기 검수는 sizes.jpg. 4장 모두1280폭·300KB 이하. 게임 장면 사진이 아니라 현재 게임의 실제 ItemDef/공통 UiSkin을 사용한 Godot4.7.2 렌더 판이다. 새 PNG는 메모리에만 넣었으며 데이터나 게임 에셋을 바꾸지 않았다.\n\n위 줄은 논리40px 점유, 아래 줄은 같은 물체의 검정 바탕, 하단은 기존 채택 D1 패랭이·가죽신·무명띠다. before/after 하단 원본 픽셀은 동일하다. sizes.jpg는 각 점유칸30/48/60px이다.\n\n원본·프롬프트·최종PNG·manifest·미제작 목록 = workbench/production/item_icons_446/. 전체로그/PNG/verification = reports/446/integration_2026-09-27/. 후보 판정 전, 상위#274는 계속 남는다.\n""")
    put(root / "QA.md", """# #446 이미지 검수\n\n- 내장 image_gen 6회, 각 물건1장. 원본6/6 실제알파·이미지 가장자리 여백·보존해시 통과.\n- 최종 PNG6/6 점유와 2배해상도 일치, 실제 ItemDef의 이름/점유는 Godot에서6/6 확인. 데이터 원본해시6/6 불변.\n- Godot4.7.2 Compatibility로 기존/후보40px·검정 바탕·승인D1 기준3종 및30/48/60px 점유를 캡처. 세 실행 PASS, stderr0.\n- before/after의 하단 기존 승인물체 픽셀 동일, 그림 교체만 위 표본에 적용.\n- 원본과 최종6종을 직접 보았다. 삿갓 원뿔/피주 가죽 돔, 예도 직선/기존 환도 곡선, 미투리 밝은 삼끈/가죽신 어두운 가죽, 전대 돈주머니/무명띠 단순 매듭을 구별했다. 새 인장은 묵함 상자와 다른 손잡이+받침이다.\n- 인장의40px 표시는 손잡이/받침 실루엣 위주이며30px에서는 세부 구름 문양이 사라진다. 예도는 실제1×3칸에서 얇은 곧은 날로 읽힌다. 원본에 글자를 넣지 않았으므로 작은 칸에서 문자를 읽게 하지 않는다.\n- 게임 반입 뒤 실제 가방·장비·상점·커서의 호버/비활성/금테 검수는 반입 카드에 남긴다. 유니크 전용그림은 UniqueDef/UI 해석 선행이 필요하므로 현재6종과 분리한다.\n""")
    put(root / "README.md", """# D1 T1 소지품 6종 납품 후보 (#446, 상위 #274)\n\n채택한 #393/#439 화풍의 현재 T1 미제작6종. 게임 반입은 아직 하지 않았다.\n\n| id | 이름 | 점유 | 최종 PNG |\n|---|---|---:|---:|\n|satgat|삿갓|2×2|160×160|\n|piju|피주|2×2|160×160|\n|injang|인장|1×1|80×80|\n|yedo|예도|1×3|80×240|\n|mituri|미투리|2×2|160×160|\n|jeondae|전대|2×1|160×80|\n\nsource/items = 내장 image_gen 투명 원본6장, game/items = 점유×80px 투명PNG6장. generation_sources.json/PROMPTS.md = 실제 프롬프트6개·원본출처, manifest.json = 원본/산출물/현재ItemDef해시 및알파/크기. prepare_assets.py = 승인#393 alpha16·8%여백·LANCZOS 패킹/검수판. qa_godot.gd = 현재게임공통 UiSkin을 사용한 외부 검수대본. qa = 실제GPU캡처와Pillow확대판. 재실행은 python prepare_assets.py, 이후 현재게임경로로 Godot --script <절대qa_godot.gd> -- --root=<이폴더> --out=<이폴더/qa> --mode=before|after|sizes. finish_review.py가 세 실행 raw로그 및 원본/가공본을 검증하고4장jpg+verification을 기록한다. qa_godot의 가상리소스명은 이짧은프로세스에만 있고게임파일을 쓰지 않는다.\n\n## 전체 카탈로그\n\ncatalog_274.json = 읽기 조사 결과. 핵심미제작73장(현재정의42/설계만31), 현재모든장비를 D1로 바꾸려면 핵심밖 추가10. 이번6장이 채택되면 핵심잔여67. 승인D1 소지품11+스킬6은 원본·가공본·반입본해시17/17 일치, 소지품별칭5는 그대로 재사용한다. 옥20·호리병·운룡검은 아직ItemDef가 없으며 대표유니크전용PNG 반입은 UniqueDef가아이콘을 읽는경로부터 필요하다. 미구현품목이나 이름제안을 실제 확정데이터처럼 만들지 않았다.\n\n## 구조 선택\n\n물체를 칸배경과 분리하면 칼/띠/갓의 실제점유와비율을 가방·장비·상점에 공유할 수 있다. 정사각 액자에 통일하는 대안은 긴칼과넓은띠의형태를 잃어 기각했다. 원본을 남기고 패킹만 결정적으로 수행해 후속교체를 재현한다.\n""")
    put(report / "README.md", """# #446 D1 T1 6종 실제 UI 렌더 검수\n\n기준 = game main ec50b082 / assets main82558ef. source는내장image_gen6장, 실제Godot4.7.2GPU Compatibility 렌더3회(기존/후보/작은칸). Godot로그/빈stderr·원본PNG4·jpg4·verification을 보존한다. 현재게임의 공통UiSkin과실제ItemDef를 읽었으나 파일반입은하지 않았다. 승인D1 하단표본은before/after 동일픽셀. 데이터원본해시불변6/6, 원본/산출PNG알파·점유해시6/6. 확대판overview는Pillow, 나머지세PNG는실제GPU캡처.\n""")
    print("PASS #446 image alpha/size/immutable source and definitions6, Godot3(stderr0), refs pixel-identical, JPG4<=300KB")
    for p in pictures:
        print(f'  {p["name"]}.jpg: {p["bytes"]} bytes')


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    finish(ap.parse_args().root)
