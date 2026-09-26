from pathlib import Path
import hashlib, json, re, shutil, subprocess

root=Path(r'C:/workspace/joseon')
game=Path(r'C:/Users/FORYOUCOM/.codex/worktrees/293-monster-elite-ui/joseon')
assets=Path(r'C:/Users/FORYOUCOM/.codex/worktrees/393-ui-icon-redesign/joseon-assets')
report=assets/'reports/450/integration_2026-09-27'
gallery=game/'docs/art/450_d1_t2_intake'
unit=(game/'tmp/450_unit.log').read_text(encoding='utf-8-sig',errors='replace')
e2e=(game/'tmp/450_e2e.log').read_text(encoding='utf-8-sig',errors='replace')
assert '전부 PASS' in unit and '실패 1' not in unit
unit_rows=re.findall(r'^\s+PASS\s+(test_\S+\.gd)\s',unit,re.M)
assert len(unit_rows)==53, len(unit_rows)
assert 'E2E SUMMARY: 12/12 PASS' in e2e and '전부 PASS' in e2e
checks={name:int(n) for name,n in re.findall(r'E2E (\w+) PASS \(검사 (\d+)\)',e2e)}
assert len(checks)==12
validation=f'전체 단위53종·러너/도구/문서층 PASS, 관련 E2E12종{sum(checks.values())}검사 PASS(일반 icon_intake {checks["icon_intake"]}). 같은 자리의 선행 #449 전체97/97 회귀 PASS 위에, 반입 뒤 전체 단위와 변경 영향 UI/소모품12종을 재검했다. #450 자체에서 전체97을 새로 실행했다고 주장하지 않는다. 최근 검증 후 빠른 부팅/러너 검사와 wt.py land --no-test로 착륙한다.'
qa=(root/'tmp/450_QA_TEMPLATE.md').read_text(encoding='utf-8').replace('{{VALIDATION}}',validation)
(gallery/'QA.md').write_text(qa,encoding='utf-8',newline='\n')
(gallery/'README.md').write_text('# #450 전후 화면\n\n가방+장비: t2_inventory_before/after.jpg · 윤도 커서: t2_held_before/after.jpg · 좌판+윤도 툴팁: t2_vendor_tooltip_before/after.jpg. 모두 실제 게임1280×720이며 확대 합성 화면이 아니다. PNG/raw/검증 보존 위치는 QA.md에 있다.\n',encoding='utf-8',newline='\n')
intake=game/'art/ui_intake_450'
(intake/'README.md').write_text('# #450 승인 아이콘 게임 반입\n\n출처 = joseon-assets #448 승인 d6f4fd0, workbench/production/item_icons_448/game/items. ItemDef.icon만 연결하고 공통 UiSkin 렌더를 사용한다. intake_manifest.json은 원본 해시·점유·그림 외 필드 해시·기존23종 보존 목록을 기록한다. 실게임 전후와 최종 검사 결과는 docs/art/450_d1_t2_intake/QA.md. 원본 생성 프롬프트/원화는 자산 저장소에 보존한다.\n',encoding='utf-8',newline='\n')
for name in ('450_unit.log','450_e2e.log','450_import.log'):
    shutil.copy2(game/'tmp'/name,report/name)
for name in ('450_prepare.py','450_t2_review.gd','450_intake.py','450_capture.py','450_verify.py','450_finish.py'):
    shutil.copy2(root/'tmp'/name,report/name)
asset_gallery=assets/'docs/art/450_d1_t2_intake'
asset_gallery.mkdir(parents=True,exist_ok=True)
for p in gallery.iterdir():
    if p.suffix in ('.jpg','.md'):
        shutil.copy2(p,asset_gallery/p.name)
shutil.copy2(gallery/'QA.md',report/'QA.md')
(report/'README.md').write_text('# #450 승인6종 실제 게임 반입\n\n승인PNG6/그림외필드6/기존23/기준물체3픽셀 보존. 전후3쌍 JPG와PNG 원본, fresh exact-index 촬영 기록, 입력/전체단위/관련e2e raw로그·manifest·재현 도구를 보존한다. 게임 전후 구도와 수치는 QA.md, 해시는 verification.json을 읽는다. 생성 원화·프롬프트는 workbench/production/item_icons_448에서 승인 버전을 그대로 보존한다.\n',encoding='utf-8')
(report/'450_before_attempt1_capture_error.txt').write_text('Traceback (most recent call last):\n  File "C:\\workspace\\joseon\\tmp\\450_capture.py", line 30, in <module>\n    print(log, end=\'\')\nUnicodeEncodeError: \'cp949\' codec can\'t encode character \'\\u2014\' in position 864: illegal multibyte sequence\n',encoding='utf-8')
verify=json.loads((report/'verification.json').read_text(encoding='utf-8'))
verify['validation']={'unit_gd':53,'related_e2e':checks,'related_checks':sum(checks.values()),
    'whole_regression_base':'#449 main30af0bd2:53 unit/97 e2e PASS in same checkout; final #450 unit53 + changed-areas12 rerun',
    'raw_logs':{name:{'bytes':(report/name).stat().st_size,'sha256':hashlib.sha256((report/name).read_bytes()).hexdigest()} for name in ('450_unit.log','450_e2e.log','450_import.log')}}
(report/'verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS #450 final evidence: unit53; related12/checks{sum(checks.values())}; gameplay captures45/51; gallery6; raw/pipeline retained.')
