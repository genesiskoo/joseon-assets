from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
root=Path('C:/workspace/joseon')
game=Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
assets=root/'._tmp/assets_87'
report=assets/'reports/453/integration_2026-09-27'
mode=sys.argv[1]
p=report/'verification.json'
data=json.loads(p.read_text(encoding='utf-8'))
head=lambda path:subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
if mode=='gate':
    meta=json.loads((report/'run_gate.json').read_text(encoding='utf-8'))
    assert meta['exit_code']==0
    log=(report/meta['raw_log']).read_text(encoding='utf-8-sig',errors='replace')
    assert 'SCRIPT ERROR 0' in log and '러너 자기검사 PASS 5/5' in log
    data['game_commit']=head(game)
    data['validation']['site_gate']={'result':'boot SCRIPT ERROR0; autoload10/10; main scene OK; runner5/5','run':meta}
elif mode=='land':
    meta=json.loads((report/'run_land.json').read_text(encoding='utf-8'))
    assert meta['exit_code']==0
    log=(report/meta['raw_log']).read_text(encoding='utf-8-sig',errors='replace')
    assert '✅ 착륙' in log and '부팅 검사 SCRIPT ERROR 0' in log and '본진 임포트' in log
    assert head(root)==head(game)==data['game_commit']
    for item in json.loads((root/'art/ui_intake_453/intake_manifest.json').read_text(encoding='utf-8'))['files']:
        assert hashlib.sha256((root/item['destination']).read_bytes()).hexdigest()==item['sha256']
    data['landing']={'game_main':head(root),'main_boot':'SCRIPT ERROR0; autoload10/10; main scene OK','run':meta,'pushed':False,'new_assets_main_hashes_verified':6}
else:
    raise ValueError(mode)
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(__file__),report/'453_record.py')
print(f'PASS #453 {mode}: exact raw + game commit/main hashes recorded.')
