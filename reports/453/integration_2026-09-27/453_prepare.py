from pathlib import Path
import json, subprocess
root = Path('C:/workspace/joseon')
game = Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
assets = root / '._tmp/assets_87'
report = assets / 'reports/453/integration_2026-09-27'
report.mkdir(parents=True, exist_ok=True)
(report / '.gitattributes').write_text('*.log -text\n*.txt -text\n', encoding='utf-8')
base = subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'], text=True).strip()
(report / 'game_base.json').write_text(json.dumps({'game_base':base,'source_commit':'f96e2931e8fed818b1952642b3fe685edfee1006','approval':'PD 2026-09-27: 승인 다음'}, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
p = game / 'docs/design/ui_v2.md'
old = p.read_text(encoding='utf-8')
assert '#453' not in old
p.write_text(old+'\n\n'+(root/'tmp/453_SPEC.md').read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
p = game / 'tests/e2e/scenarios/icon_intake.gd'
text = p.read_text(encoding='utf-8')
assert 'func _material_review()' not in text
early = '''
\tif "--icon-intake-material-only" in OS.get_cmdline_user_args():
\t\tvar was_dev: bool = DevMode.is_active
\t\tvar help_text: String = t.main.hud_label.text
\t\tDevMode.is_active = false
\t\tt.main.hud_label.text = ""
\t\tawait _material_review()
\t\tDevMode.is_active = was_dev
\t\tt.main.hud_label.text = help_text
\t\tawait t.close_all()
\t\treturn
'''
text = text.replace('func run() -> void:\n','func run() -> void:\n'+early,1)
text = text.replace('\tawait _t1_review()\n\tawait _t2_review()\n','\tawait _t1_review()\n\tawait _t2_review()\n\tawait _material_review()\n',1)
text += '\n\n' + (root/'tmp/453_material_review.gd').read_text(encoding='utf-8')
p.write_text(text,encoding='utf-8',newline='\n')
print('PASS #453 spec first; actual input fixture extended; PNG/ItemDef still unchanged.')
