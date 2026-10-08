from pathlib import Path

root = Path(r'C:/workspace/joseon')
game = Path(r'C:/Users/FORYOUCOM/.codex/worktrees/293-monster-elite-ui/joseon')
spec = game / 'docs/design/ui_v2.md'
text = spec.read_text(encoding='utf-8')
assert '#450' not in text
spec.write_text(text + '\n\n' + (root / 'tmp/450_SPEC.md').read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
# 사양을 먼저 저장한 다음, 동일 구도 baseline을 만드는 실제 입력 대본을 확장한다.
p = game / 'tests/e2e/scenarios/icon_intake.gd'
text = p.read_text(encoding='utf-8')
assert 'func _t1_review()' in text and 'func _t2_review()' not in text
early = '''
\tif "--icon-intake-t2-only" in OS.get_cmdline_user_args():
\t\tvar was_dev: bool = DevMode.is_active
\t\tvar help_text: String = t.main.hud_label.text
\t\tDevMode.is_active = false
\t\tt.main.hud_label.text = ""
\t\tawait _t2_review()
\t\tDevMode.is_active = was_dev
\t\tt.main.hud_label.text = help_text
\t\tawait t.close_all()
\t\treturn
'''
text = text.replace('func run() -> void:\n', 'func run() -> void:\n' + early, 1)
text = text.replace('\tawait _t1_review()\n', '\tawait _t1_review()\n\tawait _t2_review()\n', 1)
text += '\n\n' + (root / 'tmp/450_t2_review.gd').read_text(encoding='utf-8')
p.write_text(text, encoding='utf-8', newline='\n')
print('PASS #450 spec first, existing icon_intake extended; no product/asset change before baseline.')
