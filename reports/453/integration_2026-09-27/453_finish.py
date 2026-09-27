from pathlib import Path
import hashlib, json, re, shutil, subprocess
root=Path('C:/workspace/joseon')
game=Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
assets=root/'._tmp/assets_87'
report=assets/'reports/453/integration_2026-09-27'
gallery=game/'docs/art/453_d1_material_intake'
def run_log(mode):
    meta=json.loads((report/f'run_{mode}.json').read_text(encoding='utf-8'))
    assert meta['exit_code']==0
    p=report/meta['raw_log']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['raw_sha256']
    return p.read_text(encoding='utf-8-sig',errors='replace'),meta
unit,unit_meta=run_log('unit')
e2e,e2e_meta=run_log('e2e')
assert '전부 PASS' in unit and '전부 PASS' in e2e and 'E2E SUMMARY: 11/11 PASS' in e2e
unit_rows=re.findall(r'^\s+PASS\s+(test_\S+\.gd)\s',unit,re.M)
assert len(unit_rows)==53, len(unit_rows)
checks={name:int(n) for name,n in re.findall(r'E2E (\w+) PASS \(검사 (\d+)\)',e2e)}
assert len(checks)==11 and checks['icon_intake']==153, checks
qa=f'''# #453 승인 재료6종 게임 반입 검수 — 2026-09-27

PD 「승인 다음」으로 #452 원화6종을 채택하고 게임 반입을 승인했다. 생산 자산 `f96e2931e8fed818b1952642b3fe685edfee1006`, 반입 전 게임 기준 `996fa75d`다. PNG를 PowerShell Copy-Item으로 그대로 복사했다.

| 재료 | 실제 점유/쌓기 | 원본 연결 |
|---|---|---|
| 괴황지 goehwangji | 1×1 /20 | 80×80 RGBA |
| 경면주사 gyeongmyeonjusa | 1×1 /20 | 80×80 RGBA |
| 흑랑 이빨 heukrang_tooth | 1×1 /20 | 80×80 RGBA |
| 장산범의 흰 털 jangsanbeom_fur | 1×1 /20 | 80×80 RGBA |
| 불가살이의 쇠비늘 bulgasari_scale | 1×1 /20 | 80×80 RGBA |
| 구미호 꼬리털 gumiho_tail | 1×1 /20 | 80×80 RGBA |

공통 UiSkin의 알파 영역 그리기를 재사용해 가방40px·좌판48px·커서가 같은 원본을 쓰게 했다. 개별 프레임이나 배율을 더하면 클릭 영역과 물체가 분리될 수 있어 기각했다. PNG/ItemDef.icon6만 반입하고 가격·점유·쌓기·가중·상점해금·보스전용 드랍·모델을 보존했다. 기존 승인29PNG(아이템23·스킬6), 다른 data/items .tres61파일(색인 포함), 삿갓/피주/인장 가방 기준 영역의 동일픽셀3종을 확인했다. 실제 원본 SHA6·그림외필드6·알파0~255·80×80이 전부 PASS다. 아이콘 대기는9→3(봉인조각), 바닥 모델 대기는 그대로다.

실제 입력: 종이18장을 집고 되놓은 뒤 다른3장과 합쳐20장+커서1장을 확인했다. 흑랑 처치 전 할매 진열 없음, 처치 뒤 일반재료2·보스재료4 미진열을 실제 npc_stock/대화/거래 선택으로 확인했다. 주사 구매=25엽전/스택+1, 종이 구매=10엽전/스택+1, 구미호 털 스택5 판매=기존가격500엽전이 확인됐다. 실제 loot_dropped로6종을 떨구고 Alt 이름표의 이빨만 클릭해 걸어가 회수, 가방의 기존 이빨3→4로 병합하고 다른5종이 바닥에 남음을 확인했다.

반입 전 실제32검사·후38검사 PASS·stderr0. 가방/할매좌판/드랍 회수 후3쌍은 같은 표본/구도/커서의 실제1280×720 캡처다. 실행 후 생성된 정확한 번호01/02/03 파일만 수집했고 SHA·시각·명령을 남겼다. 문서에는 JPG6장(각300KB 이하), PNG원본/raw는 자산 reports/453/integration_2026-09-27에 있다. 불꽃·배우 자세·도력 자연재생은 시간에 따라 변할 수 있다. 반입 전 플래그는 준비 중 PNG 경로 검사를 건너뛰는 용도이며 현재 설치된 그림을 옛 glyph로 바꾸지 않는다. before는 실제 PNG/정의 반입 전에 촬영했다.

직접 화면 검수: 검정 칸에서 종이·붉은 광석·굽은 이빨·냉백 털·회색 쇠비늘·온백 긴 털을 구별할 수 있다. 수량은 기존 칸 위치를 쓰고 tooltip은 원래 칸/상품 행을 가리지 않는다. 바닥의 임시3D 형태와 좌판의 무한재고99/20 표시는 기존 표현이며 이번 아이콘 반입으로 바꾸지 않았다.

최종 검증: 단위53종·러너/도구/문서층 PASS, 영향 관련 E2E11종 {sum(checks.values())}검사 PASS(일반 icon_intake153검사). 전체97 시나리오를 이번 카드에서 재실행했다고 주장하지 않는다. 제품 동작 코드는 그대로이고 자원6·검수 대본만 변경했으므로 전체 단위와 해당 UI/상점/드랍 경로를 재검했다. 같은 테스트 대상의 빠른 부팅/러너 검사를 거쳐 wt.py land --no-test로 착륙한다. 검증 뒤 제품/검수 코드 수정은 없다.

재현: `godot --path <자리> --windowed --resolution 1280x720 -- --e2e=icon_intake --e2e-shots --icon-intake-material-only`. 관련 검사: `tools/test.ps1 -E2e -Scenario 'icon_intake,item_ui,ui_tooltips,ui_docks,ui_windows,hover_target,vendor_quest,vendor_prices,shaman_heal,pickup_equip,loot_drop'`. 미push.
'''
(gallery/'QA.md').write_text(qa,encoding='utf-8',newline='\n')
(gallery/'README.md').write_text('# #453 전후 화면\n\nmaterial_inventory_before/after.jpg = 가방 재료6종·흑랑 이빨 호버. material_vendor_before/after.jpg = 무당 할매 좌판·경면주사 호버. material_drop_recovered_before/after.jpg = 바닥 이름표로 이빨을 회수한 뒤 가방 스택4·다른5종 바닥. 전부 실제 게임1280×720 전후3쌍이다. 검증/한계/재현은 QA.md.\n',encoding='utf-8',newline='\n')
(game/'art/ui_intake_453/README.md').write_text('# #453 승인 재료 아이콘 반입\n\n출처: joseon-assets #452 승인 f96e293, workbench/production/item_icons_452/game/items. 승인 PNG 그대로 복사·ItemDef.icon만 연결한다. intake_manifest.json에 원본/그림외필드6·이전 승인29PNG·다른tres61 해시를 보존했다. 가방/좌판/드랍 실제 전후는 docs/art/453_d1_material_intake/QA.md. 원화/프롬프트는 자산 저장소에 보존한다.\n',encoding='utf-8',newline='\n')
for name in ('453_prepare.py','453_SPEC.md','453_material_review.gd','453_intake.py','453_capture.py','453_verify.py','453_run.py','453_gate.py','453_finish.py'):
    shutil.copy2(root/'tmp'/name,report/name)
asset_gallery=assets/'docs/art/453_d1_material_intake'
asset_gallery.mkdir(parents=True,exist_ok=True)
for p in gallery.iterdir():
    if p.suffix in ('.jpg','.md'):
        shutil.copy2(p,asset_gallery/p.name)
shutil.copy2(gallery/'QA.md',report/'QA.md')
(report/'README.md').write_text('# #453 재료6종 실제 게임 반입\n\n승인6PNG/그림외필드6/이전29PNG/다른tres61/기준픽셀3 보존. 가방·할매좌판·드랍회수 전후3쌍 JPG/PNG, 새 촬영시간·명령·SHA, raw검증로그·manifest·반입/촬영/검증 도구를 보존한다. 원본 생성/패킹/프롬프트는 workbench/production/item_icons_452 승인 커밋 그대로다.\n',encoding='utf-8')
p=report/'verification.json'
data=json.loads(p.read_text(encoding='utf-8'))
data['validation']={'unit_gd':53,'related_e2e':checks,'related_checks':sum(checks.values()),
    'actual_windowed':{'before':32,'after':38,'stderr_errors':0},
    'scope':'runtime PNG/ItemDef.icon only; 53 unit+11 affected e2e+site gate; no claim of fresh full97 run',
    'runs':{'unit':unit_meta,'e2e':e2e_meta}}
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS #453 final evidence: unit53; related11/checks{sum(checks.values())}; captures32/38; JPG6; exact PNG/raw retained.')
