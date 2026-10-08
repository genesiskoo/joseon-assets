"""Capture unchanged live ItemDefs and PNGs before #469 candidate generation."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon')
PLAN = [
    ('gwangdahoe', '광다회', 2, 1, 4, 2, 1, '관복의 넓은 짠띠·절제된 홍/남색 직조'),
    ('mokhwa', '목화', 2, 2, 5, 2, 1, '검은 장화·회색 천 반사·밝은 밑창 경계'),
    ('ident_tome', '식별부첩', 1, 2, 6, 1, 20, '황토빛 종이 묶음·적색 실 바느질'),
    ('portal_tome', '귀환부첩', 1, 2, 6, 1, 20, '남색 천 덮개·밝은 종이 모서리'),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def val(text, name, default=None):
    m = re.search(r'^' + re.escape(name) + r' = (.+)$', text, re.M)
    return m.group(1).strip('"') if m else default

items = []
for item_id, name, w, h, slot, tier, stack, note in PLAN:
    p = GAME / 'data/items' / (item_id + '.tres')
    t = p.read_text(encoding='utf-8')
    assert val(t,'id') == item_id and val(t,'display_name') == name
    assert val(t,'size') == f'Vector2i({w}, {h})'
    assert int(val(t,'slot')) == slot
    assert int(val(t,'tier','1')) == tier
    assert int(val(t,'max_stack','1')) == stack
    items.append(dict(item_id=item_id, display_name=name, grid_w=w, grid_h=h,
                      output_width=w*80, output_height=h*80, slot=slot, tier=tier,
                      max_stack=stack, note=note, definition_path=p.as_posix(), definition_sha256=sha(p)))
files = sorted((GAME/'assets/sprites/ui/icons_a').rglob('*.png')) + sorted((GAME/'data/items').glob('*.tres'))
snapshot = {p.relative_to(GAME).as_posix(): sha(p) for p in files}
assert sum(k.endswith('.png') for k in snapshot) == 42
(ROOT/'inputs.json').write_text(json.dumps(dict(card=469, parent_card=274, items=items), ensure_ascii=False, indent=2)+'\n',encoding='utf-8',newline='\n')
(ROOT/'runtime_before.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('PREPARED 4 definitions, snapshot',len(snapshot),'files, 42 PNG')
