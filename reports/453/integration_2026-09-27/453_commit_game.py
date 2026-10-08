from pathlib import Path
import json,subprocess
game=Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
manifest=json.loads((game/'art/ui_intake_453/intake_manifest.json').read_text(encoding='utf-8'))
files=[]
for item in manifest['files']:
    files.extend([item['definition'],item['destination']])
files.extend(['tests/test_items.gd','tests/e2e/scenarios/icon_intake.gd','docs/design/ui_v2.md','docs/TASK_CURRENT.md','art/ui_intake_453','docs/art/453_d1_material_intake'])
subprocess.run(['git','-C',str(game),'add','--',*files],check=True)
subprocess.run(['git','-C',str(game),'diff','--cached','--check'],check=True)
subprocess.run(['git','-C',str(game),'commit','-m','feat(#453): 승인 재료6종 아이콘 반입과 실제 가방·좌판·드랍 검수'],check=True)
print('GAME_COMMIT',subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'],text=True).strip())
