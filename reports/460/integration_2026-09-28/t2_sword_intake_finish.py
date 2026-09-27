from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path("C:/workspace/joseon")
ctx = json.loads((root / "tmp/t2_sword_intake_context.json").read_text(encoding="utf-8"))
game, assets, report, gallery, intake = [Path(ctx[k]) for k in ["game", "assets", "report", "gallery", "intake"]]

def run_log(mode):
    meta = json.loads((report / f"run_{mode}.json").read_text(encoding="utf-8"))
    assert meta["exit_code"] == 0
    p = report / meta["raw_log"]
    assert hashlib.sha256(p.read_bytes()).hexdigest() == meta["raw_sha256"]
    return p.read_text(encoding="utf-8-sig", errors="replace"), meta

unit, unit_meta = run_log("unit")
e2e, e2e_meta = run_log("e2e")
gate, gate_meta = run_log("gate")
assert "전부 PASS" in unit and "전부 PASS" in e2e and "E2E SUMMARY: 11/11 PASS" in e2e
unit_rows = re.findall(r"^\s+PASS\s+(test_\S+\.gd)\s", unit, re.M)
assert len(unit_rows) == 53, len(unit_rows)
checks = {name: int(n) for name, n in re.findall(r"E2E (\w+) PASS \(검사 (\d+)\)", e2e)}
assert len(checks) == 11 and checks["icon_intake"] == 315, checks
assert "✓ 부팅 검사 SCRIPT ERROR 0" in gate and "오토로드 10/10" in gate and "주 장면 OK" in gate
assert "✓ 러너 자기검사 PASS 5/5" in gate and "SCRIPT ERROR:" not in gate and "\nERROR:" not in gate
qa = f'''# #460 승인 T2 검 4종 게임 반입 검수 — 2026-09-28

PD 「승인 다음」으로 #459 본국검·제독검·쌍수도·사인검 r2를 채택하고 별도 게임 반입을 승인했다. 승인 자산 main `{ctx['source_commit']}`, 반입 전 게임 기준 `{ctx['game_base']}`. 승인된 80×240 RGBA PNG 네 장을 PowerShell Copy-Item으로 그대로 복사하고 기존 Texture2D 경로만 연결했다.

| 검 | 점유 / 쌓기 | 구매 / 판매 | 현재 계약 |
|---|---|---|---|
| 본국검 bongukgeom | 1×3 / 1 | 250 / 62 엽전 | 한손, 기존 피해·요구치 유지 |
| 제독검 jedokgeom | 1×3 / 1 | 250 / 62 엽전 | 한손, 기존 피해·요구치 유지 |
| 쌍수도 ssangsudo | 1×3 / 1 | 300 / 75 엽전 | 양손, 보조칸 차단 유지 |
| 사인검 saingeom r2 | 1×3 / 1 | 280 / 70 엽전 | 한손, 기존 부적 피해 보정 유지 |

왜 이 구조인가: 공통 UiSkin의 알파 영역·비율 보존을 재사용하면 가방 40×120, 무기칸, 좌판 48px, 커서가 동일한 승인 그림을 사용한다. UI마다 그림과 배율을 따로 붙이는 대안은 점유·호버 영역과 물체를 분리할 수 있어 기각했다. 제품 변경은 PNG 4장과 ItemDef 4개의 기존 Texture2D 경로뿐이다. 같은 resource id 2/load_steps 3, 수치·가격·요구치·1×3·쌓기·양손/보조칸·바닥 모델은 그대로다.

원본 SHA 4개, RGBA/80×240/알파 0~255, 그림 외 필드 4종이 PASS다. 다른 data/items .tres 63개(색인 포함), 기존 icons_a PNG 38장(아이템 32·스킬 6), 옛 H1 검 그림 3장이 바이트 그대로다. tests/test_items.gd의 ICON_PENDING/MODEL_PENDING과 공통 UI 렌더도 보존했다. 가방의 환도·예도·가죽신 세 영역은 원본 PNG 전후 픽셀이 동일하다. 현재 ItemDef 아이콘 대기는 0, icons_a는 아이템 36·스킬 6 = 42장이다. #274 핵심 원화 잔여는 51종으로 유지한다.

실제 입력 검수: 네 검의 마지막 점유 칸에서 사인검을 집고 되놓았으며, 네 무기의 착용·교환·해제를 같은 인스턴스로 확인했다. 쌍수도 착용 시 보조 장비가 가방으로 돌아가고 보조칸 입력이 차단되며, 사인검으로 교환하면 보조칸이 복원되고 다시 착용할 수 있다. 고정 좌판 네 검을 실제 호버·클릭해 구매/판매했고 총 구매 1080·판매 269·순지출 811엽전이 유지됐다. loot_dropped로 네 검을 떨군 뒤 Alt 이름표를 실제 클릭해 걸어가 회수했고 각각 원래 인스턴스·1×3으로 가방에 들어갔다.

최초 반입 전 대본은 보조 장비가 먼저 차지한 칸으로 교환 무기도 돌아올 것이라는 기대와 존재하지 않는 메시지 필드 접근으로 실패했다. 제품은 수정하지 않았고, 대본을 실제 자동 배치 (4,0) 및 bag.get('_msg') 계약에 맞췄다. 최초 실패 stdout/stderr 전문과 첫 화면은 자산 reports에 보존했다. 최종 반입 전 78개·후 86개 검사 PASS, stderr 0. 후의 추가 8개는 새 PNG 경로/크기 검사다.

사진: 가방/커서와 양손 장비/좌판을 같은 표본·구도·커서로 촬영한 전후 3쌍이다. 실행 후 새로 생성된 정확한 번호 01/02/03 파일만 수집하고 시각·명령·SHA를 남겼다. 문서에는 1280×720 JPG 6장(각 300KB 이하), 원본 PNG/raw 로그는 `joseon-assets/reports/460/integration_2026-09-28`에 있다. 마을 불꽃·배우 자세·도력 자연 재생은 시간에 따라 변할 수 있다. before 플래그는 아직 반입하지 않은 PNG 경로/크기 검사를 생략하며 기존 그림을 가짜로 교체하지 않는다. before는 실제 PNG/정의 변경 전에 촬영했다.

직접 화면 검수: 검정 칸에서 본국검의 곧은 짧은 자루, 제독검의 굽은 날, 쌍수도의 긴 두손 자루, 사인검의 넓은 양날과 금속 장식을 확인했다. 가방에서 네 검이 1×3 칸 안에 놓이고, 커서 사인검과 착용 쌍수도는 같은 원본을 사용한다. 좌판 48px에서는 날과 자루의 형태는 보이지만 각인·작은 장식만으로 즉시 이름을 구별하기 어렵다. 좌판의 기존 텍스트 이름·가격을 함께 사용한다. 가방 수치 툴팁과 좌판 툴팁이 검사 대상 칸/상품 행을 가리지 않는다. 바닥 임시 3D 모델은 이번 반입에서 교체하지 않았다.

최종 검증: 단위 53종 및 러너/도구/문서층 PASS, 영향 관련 E2E 11종 {sum(checks.values())}검사 PASS(일반 icon_intake 315검사), 빠른 부팅·러너 자기검사 PASS. 전체 98 시나리오나 내보낸 빌드를 이번 카드에서 새로 검사했다고 주장하지 않는다. 검증한 동일한 코드와 자산을 wt.py land --no-test로 착륙하고 본진 임포트·부팅을 확인한다. 검증 뒤 제품/검수 코드는 수정하지 않는다. 미push.

재현: `godot --path <자리> --windowed --resolution 1280x720 -- --e2e=icon_intake --e2e-shots --icon-intake-sword-only`. 관련 검사: `tools/test.ps1 -E2e -Scenario 'icon_intake,item_ui,equipment_ui,ui_tooltips,ui_docks,ui_windows,hover_target,vendor_quest,vendor_prices,pickup_equip,loot_drop'`. 출처·매핑·보존 해시는 `art/ui_intake_460/intake_manifest.json`, 실행 증거는 자산 `verification.json`과 `run_*.json`.
'''
(gallery / "QA.md").write_text(qa, encoding="utf-8", newline="\n")
readme = "# #460 T2 검 반입 전후 화면\n\n실제 게임 입력으로 촬영한 전후 세 쌍. 검증·한계·재현은 [QA.md](QA.md).\n"
for state, title in [("sword_inventory", "가방 — 네 검과 사인검 호버"), ("sword_held_twohand", "커서 사인검·착용 쌍수도·보조칸 차단"), ("sword_vendor", "좌판 — 네 검 진열·사인검 호버")]:
    readme += f"\n## {title}\n\n전\n\n![전]({state}_before.jpg)\n\n후\n\n![후]({state}_after.jpg)\n"
(gallery / "README.md").write_text(readme, encoding="utf-8", newline="\n")
(intake / "README.md").write_text("# #460 승인 T2 검 아이콘 반입\n\n출처: joseon-assets #459 승인 87d0c4fa, workbench/production/item_icons_459/game/items. 본국검·제독검·쌍수도·사인검r2 PNG80×240 네 장을 바이트 그대로 복사하고 기존 Texture2D 경로만 연결했다. intake_manifest.json에 출처·승인·원본/그림 외 필드·이전101파일 및 H1검3 보존 해시를 기록했다. 실게임 전후·실제 착용/거래/회수 검수는 docs/art/460_d1_t2_sword_intake/QA.md. 원화와 프롬프트는 자산 저장소에 보존한다.\n", encoding="utf-8", newline="\n")
for name in ["t2_sword_intake_start.py", "t2_sword_intake_prepare.py", "460_sword_review.gd", "t2_sword_fix_fixture.py", "t2_sword_intake_apply.py", "t2_sword_intake_capture.py", "t2_sword_intake_verify.py", "t2_sword_intake_run.py", "t2_sword_intake_gate.py", "t2_sword_intake_finish.py"]:
    shutil.copy2(root / "tmp" / name, report / name)
asset_gallery = assets / "docs/art/460_d1_t2_sword_intake"
asset_gallery.mkdir(parents=True, exist_ok=True)
for p in gallery.iterdir():
    if p.suffix in [".jpg", ".md"]:
        shutil.copy2(p, asset_gallery / p.name)
shutil.copy2(gallery / "QA.md", report / "QA.md")
(report / "README.md").write_text("# #460 T2 검4 실제 게임 반입\n\n승인 PNG/그림 외 필드4, 기존101파일+H1검3, 기준 픽셀3 보존. 가방·커서/양손 장비·좌판 전후3쌍 JPG/PNG, 실제 착용·거래·Alt회수, 최초 fixture 실패를 포함한 raw전문, 명령·시각·해시·manifest·재현 도구를 보존한다. 원화 생성·편집·패킹·프롬프트는 workbench/production/item_icons_459에 그대로 있다.\n", encoding="utf-8", newline="\n")
p = report / "verification.json"
data = json.loads(p.read_text(encoding="utf-8"))
data["validation"] = {"unit_gd": 53, "related_e2e": checks, "related_checks": sum(checks.values()), "actual_windowed": {"before": 78, "after": 86, "stderr_errors": 0}, "scope": "PNG4/Texture2D-path4 and actual-input fixture; unit53+11 affected E2E+site gate; no fresh full98/export claim", "runs": {"unit": unit_meta, "e2e": e2e_meta, "gate": gate_meta}}
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(f"PASS #460 final evidence: unit53; related11/checks{sum(checks.values())}; captures78/86; six JPG; exact PNG/raw retained.")
