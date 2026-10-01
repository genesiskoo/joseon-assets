import json
from pathlib import Path
import render_potion_rank_v3_534 as renderer

source = (renderer.HERE / 'qa_godot.gd').read_text(encoding='utf-8')
source = source.replace('"grayscale"]', '"grayscale", "blind"]')
source = source.replace('func label(at: Vector2, value: String, px: int = 15, strong: bool = false) -> void:\n',
    'func label(at: Vector2, value: String, px: int = 15, strong: bool = false) -> void:\n\t\tif mode == "blind": return\n')
source = source.replace('assert(specs.size() == 6)',
    'assert(specs.size() == 6)\n\tif mode == "blind":\n\t\tvar shuffled: Array = []\n\t\tfor index in [0, 5, 1, 4, 2, 3]: shuffled.append(specs[index])\n\t\tspecs = shuffled')
path = renderer.HERE / 'qa_godot_blind.gd'
if path.exists():
    raise SystemExit('Preserve existing blind renderer instead of overwriting it.')
path.write_text(source, encoding='utf-8', newline='\n')
(renderer.REPORT / 'blind_layout_key.json').write_text(json.dumps({'order_row_major': ['hp_potion', 'mp_potion_3', 'hp_potion_2', 'mp_potion_2', 'hp_potion_3', 'mp_potion'],
    'surfaces': ['bag40', 'vendor48', 'belt42', '80px_enlargement'], 'names_and_numbers_drawn': False,
    'purpose': 'Unlabelled mixed preview; not a user-study accuracy claim.'}, indent=2) + '\n', encoding='utf-8')
renderer.run('blind', ['-s', str(path), '--', '--root=' + str(renderer.HERE), '--out=' + str(renderer.HERE / 'qa'), '--mode=blind'])
