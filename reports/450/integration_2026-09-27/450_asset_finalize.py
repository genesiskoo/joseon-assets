from pathlib import Path
import hashlib, json, shutil, subprocess

game=Path(r'C:/Users/FORYOUCOM/.codex/worktrees/293-monster-elite-ui/joseon')
assets=Path(r'C:/Users/FORYOUCOM/.codex/worktrees/393-ui-icon-redesign/joseon-assets')
report=assets/'reports/450/integration_2026-09-27'
p=report/'verification.json'
data=json.loads(p.read_text(encoding='utf-8'))
data['game_commit']=subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'],text=True).strip()
gate=(game/'tmp/450_site_gate.log').read_text(encoding='utf-8-sig',errors='replace')
assert 'SCRIPT ERROR 0' in gate and '러너 자기검사 PASS 5/5' in gate
shutil.copy2(game/'tmp/450_site_gate.log',report/'450_site_gate.log')
data['validation']['site_gate']='boot SCRIPT ERROR0; autoload10/10; main scene OK; runner5/5'
data['validation']['raw_logs']['450_site_gate.log']={'bytes':(report/'450_site_gate.log').stat().st_size,
    'sha256':hashlib.sha256((report/'450_site_gate.log').read_bytes()).hexdigest()}
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(r'C:/workspace/joseon/tmp/450_asset_finalize.py'),report/'450_asset_finalize.py')
print('PASS #450 final game commit and gate evidence recorded; review ready to merge.')
