from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
ctx = json.loads((main / "tmp/seal_intake_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
report = assets / f"reports/{card}/integration_2026-09-27"
gallery = game / f"docs/art/{card}_d1_quest_seal_intake"

def run_log(mode):
    meta = json.loads((report / f"run_{mode}.json").read_text(encoding="utf-8"))
    assert meta["exit_code"] == 0
    p = report / meta["raw_log"]
    assert hashlib.sha256(p.read_bytes()).hexdigest() == meta["raw_sha256"]
    return p.read_text(encoding="utf-8-sig", errors="replace"), meta

unit, unit_meta = run_log("unit")
e2e, e2e_meta = run_log("e2e")
gate, gate_meta = run_log("gate")
assert "전부 PASS" in unit and "전부 PASS" in e2e and "E2E SUMMARY: 12/12 PASS" in e2e
assert "SCRIPT ERROR 0" in gate and "러너 자기검사 PASS 5/5" in gate
unit_rows = re.findall(r"^\s+PASS\s+(test_\S+\.gd)\s", unit, re.M)
assert len(unit_rows) == len(list((game / "tests").glob("test_*.gd"))) == 53
checks = {name:int(n) for name,n in re.findall(r"E2E (\w+) PASS \(검사 (\d+)\)", e2e)}
assert len(checks) == 12 and checks["icon_intake"] == 196, checks
qa = f"""# #{card} 승인 봉인물3종 게임 반입 — 2026-09-27

PD 「승인 다음」으로 #454 봉인패·봉인고리·사슬 조각3종을 전부 채택하고 반입했다. 원화/80px 후보 최초9747c2a, 동시 #455·#456 자산을 보존해 rebase한 채택 자산 `{ctx['source_commit']}`. 원화·공유UiSkin 검수 문서 main5e23e8eb 착륙 후 이 기준에서 실제 반입했다. PNG는 PowerShell Copy-Item으로 승인 바이트 그대로 복사했다.

| 물건 | 실제 정의/반입 |
|---|---|
| 흑랑의 봉인패 seal_heukrang | 1×1/쌓기1/quest_item · 80×80 RGBA |
| 장산범의 봉인고리 seal_jangsanbeom | 1×1/쌓기1/quest_item · 80×80 RGBA |
| 불가살이의 사슬 조각 seal_bulgasari | 1×1/쌓기1/quest_item · 80×80 RGBA |

기존 UiSkin 알파 영역 그리기를 재사용한다. PNG와 ItemDef.icon3만 반입하고 수치·점유·쌓기·퀘스트 여부·가격·드랍·모델을 보존했다. 승인 SHA3/그림외필드3/다른 정의64(색인 포함)/기존 PNG35(아이템29·스킬6) 동일. 가방의 삿갓·피주·인장 영역3곳 전후 픽셀 동일. 아이콘 없는 현재 ItemDef는3→0, 현재 ItemDef66 전부 icon 참조를 갖는다. 바닥 모델 대기는 그대로이며 #274 핵심73 밖 추가3이므로 핵심잔여55는 유지한다.

실제 입력: 세 물건을1×1로 배치하고 봉인패를 집어 같은 칸에 되놓았다. 각각 Ctrl클릭 버림 거부, 바닥 물건 추가 없음. 실제 김 영감 대화/거래 선택 후 세 물건 우클릭 판매 거부, 같은 물건/엽전3750/재고 유지. 실제 loot_dropped로 세 물건을 바닥에 놓고 각각 Alt 이름표를 클릭해 걸어가 회수했다. 세 물건은 병합 없이 쌓기1/같은 인스턴스/원자리로 돌아왔다.

반입 전40검사/후43검사 PASS, stderr0. 가방·좌판 판매 거부·드랍 회수 후3쌍 모두 실제1280×720 캡처다. 같은 표본/구도/커서를 사용했고 정확한01/02/03 파일의 새 시각·SHA·명령을 기록했다. JPG6장 각300KB이하, 원본PNG/raw는 reports/{card}/integration_2026-09-27. 배우 자세·불꽃·도력 자연재생은 시간에 따라 변할 수 있다. before는 실제 PNG/정의 반입 전에 촬영했으며 before 플래그는 승인 이미지 경로 검사만 건너뛴다.

직접 시각 검수: 어두운 가방에서 넓은 주홍 패·열린 회색 고리·대각선 사슬을 구별할 수 있다. 툴팁은 원래 점유 칸을 가리지 않는다. 기존 퀘스트 물건 툴팁이 판매 불가인데 판매가1엽전을 보이고 「들고 창 밖 클릭: 버림」을 안내하는 불일치, 커서로 든 채 창 밖에 명시적으로 버리는 경로는 후속 UI 카드로 분리한다. 이 카드에서는 판매와 Ctrl 버림 금지만 검수했으며 모든 버림 경로가 막혔다고 주장하지 않는다. 창 닫기/가방 가득 참의 발밑 보존 안전망은 정본 §14.5의 허용 예외다.

봉밀굴 봉인3 소비/개방은 #169 대기이고 현재 입구는 sealed_message 고정이다. 장산범·불가살이 보스 연결은 #69 대기다. 이번 반입이 두 미구현 기능을 완성하거나 테스트했다고 보아서는 안 된다.

최종 검증: 단위53종·도구/러너/문서층 PASS, 관련E2E12종{sum(checks.values())}검사 PASS(일반 icon_intake196). 빠른부팅 SCRIPT ERROR0/오토로드10/10/주장면OK·러너자기검사5/5. 새 전체98 시나리오 실행 결과로 보아서는 안 된다. 제품 동작 코드가 같고 자원3/아이콘 대기목록/검수 대본만 바뀌어 전체 단위와 해당UI·줍기·물약/퀘스트·보스 경로를 재검했다. 이 검증 후 코드 변경 없이 wt.py land --no-test로 착륙한다.

왜 이 구조인가: 채택 PNG를 기존 아이콘 경로에 연결하면 슬롯/툴팁/퀘스트 입력을 그대로 사용한다. 새 렌더러나 문 개방 규칙을 추가하는 대안은 반입 범위를 넘어 위험을 늘리므로 기각했다. 승인 바이트/나머지 필드 보존과 실제 입력을 함께 검수했다.

재현: godot --path <자리> --windowed --resolution1280x720 -- --e2e=icon_intake --e2e-shots --icon-intake-seal-only. 관련 검사는 tools/test.ps1 -E2e -Scenario 'icon_intake,item_ui,ui_tooltips,ui_docks,ui_windows,hover_target,vendor_quest,pickup_equip,loot_drop,potion_tiers,quest_journal,boss_floor'. 미push.
"""
(gallery / "QA.md").write_text(qa, encoding="utf-8", newline="\n")
(gallery / "README.md").write_text(f"# #{card} 봉인물3 실제 전후\n\nseal_inventory_before/after.jpg = 가방3물건/봉인패 호버. seal_vendor_refused_before/after.jpg = 실제 김 영감 좌판/판매거부/봉인고리 호버. seal_drop_recovered_before/after.jpg = 각 이름표 클릭으로 세 물건을 회수한 뒤 사슬 호버. 검증/현재 미구현/후속UI 문제는 QA.md.\n", encoding="utf-8", newline="\n")
(game / f"art/ui_intake_{card}/README.md").write_text(f"# #{card} 승인 봉인물3 반입\n\n출처 joseon-assets #454 채택 {ctx['source_commit'][:8]}, workbench/production/item_icons_454/game/items. PNG 그대로 복사/ItemDef.icon만 연결. intake_manifest.json에 승인 SHA3/그림외필드3/이전PNG35/다른정의64를 보존했다. 실제 전후 검수 docs/art/{card}_d1_quest_seal_intake/QA.md. 원화·프롬프트는 자산 본진에 보존한다.\n", encoding="utf-8", newline="\n")
for name in ["seal_review.gd", "seal_intake_begin.py", "seal_intake_prepare.py", "seal_intake_apply.py", "seal_copy.ps1", "seal_capture.py", "seal_verify.py", "seal_run.py", "seal_finish.py"]:
    shutil.copy2(main / "tmp" / name, report / name)
asset_gallery = assets / f"docs/art/{card}_d1_quest_seal_intake"
asset_gallery.mkdir(parents=True, exist_ok=True)
for p in gallery.iterdir():
    if p.suffix in [".jpg", ".md"]:
        shutil.copy2(p, asset_gallery / p.name)
shutil.copy2(gallery / "QA.md", report / "QA.md")
(report / "README.md").write_text(f"# #{card} 봉인물3 실제 게임 반입\n\n승인 SHA3/그림외필드3/이전PNG35/다른정의64/기준픽셀3 보존. 전후3쌍 JPG/PNG, 촬영시각/명령/해시/원시 로그/반입 및 검수 도구. 원본생성·패킹·프롬프트는 승인 workbench/production/item_icons_454 그대로. 결과의 범위와 기존 퀘스트 UI/문개방 미구현은 QA.md.\n", encoding="utf-8")
p = report / "verification.json"
data = json.loads(p.read_text(encoding="utf-8"))
data["validation"] = {"unit_gd":53, "related_e2e":checks, "related_checks":sum(checks.values()), "actual_windowed":{"before":40, "after":43, "stderr_errors":0}, "scope":"PNG/ItemDef.icon3 only; all53 unit +12 affected e2e +site gate; no fresh full-suite claim", "runs":{"unit":unit_meta, "e2e":e2e_meta, "gate":gate_meta}}
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PASS #{card} final evidence: unit53; related12/checks{sum(checks.values())}; capture40/43; JPG6; raw retained.")
