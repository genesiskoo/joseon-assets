from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path('C:/workspace/joseon')
assets=root/'._tmp/assets_87'
report=assets/'reports/453/integration_2026-09-27'
data=json.loads((report/'verification.json').read_text(encoding='utf-8'))
head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
assert head==data['landing']['game_main']
p=root/'docs/art/453_d1_material_intake/QA.md'
text=p.read_text(encoding='utf-8')
assert '최종 착륙 기록' not in text
text+='\n## 최종 착륙 기록\n\n게임 main `'+head+'` 착륙 완료, 본진 임포트21초·부팅 SCRIPT ERROR0·오토로드10/10·주 장면OK. #453 완료, #274 핵심 잔여55. 자산 reports/453/integration_2026-09-27의 run_land.json과 raw로그에 재현 명령·실행시간·SHA가 있다. 최초 자산 Git 공백검사는 원문 Windows 로그의 CR 줄끝을 공백으로 판정해 종료2로 멈췄다. 전문은453_initial_diff_check.log로 보존했다. raw바이트를 고치지 않고 로그만 공백검사에서 제외했으며 소스·문서 공백검사와 Git blob/raw 동등성은 PASS다. 게임 시험 실패나 자동승인 거절은 없었다.\n'
p.write_text(text,encoding='utf-8',newline='\n')
shutil.copy2(p,assets/'docs/art/453_d1_material_intake/QA.md')
shutil.copy2(p,report/'QA.md')
for name in ('453_commit_game.py','453_commit_assets.py','453_acceptance.py','453_close_records.py','453_state.py'):
    shutil.copy2(root/'tmp'/name,report/name)
# Report contains the runner's main-import summary, and byte-identical per-step engine logs referenced by wt.py.
unit_meta=json.loads((report/'run_unit.json').read_text(encoding='utf-8'))
for mode in ('import','unit','e2e','gate','land'):
    meta=json.loads((report/f'run_{mode}.json').read_text(encoding='utf-8'))
    assert meta['exit_code']==0
    log=report/meta['raw_log']
    assert hashlib.sha256(log.read_bytes()).hexdigest()==meta['raw_sha256']
print('PASS #453 final landing docs/raw hashes; metadata-only changes after validated runtime.')
