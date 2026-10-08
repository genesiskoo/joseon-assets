from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
from PIL import Image

GAME = Path(r'C:\Users\FORYOUCOM\.codex\worktrees\293-monster-elite-ui\joseon')
SOURCE = Path(r'C:\workspace\joseon-assets\workbench\production\item_icons_446')
BASE = 'ed0fd67d'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def semantics(text):
    return '\n'.join(line for line in text.splitlines()
        if line.strip() and not line.startswith('[gd_resource ') and not line.startswith('icon = ')
        and not ('[ext_resource type="Texture2D"' in line and 'id="2"' in line))

production = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
records = []
for item in production['items']:
    item_id = item['item_id']
    src = SOURCE / 'game/items' / f'{item_id}.png'
    dst_rel = f'assets/sprites/ui/icons_a/items/{item_id}.png'
    dst = GAME / dst_rel
    assert sha(src) == item['game_sha256'], item_id
    im = Image.open(src)
    assert list(im.size) == item['game_size'] and im.mode == 'RGBA' and im.getchannel('A').getextrema()[0] == 0
    assert dst.exists() is False, f'Existing target must be reviewed: {dst}'
    def_path = GAME / 'data/items' / f'{item_id}.tres'
    old = def_path.read_text(encoding='utf-8')
    base = subprocess.check_output(['git', '-C', str(GAME), 'show', f'{BASE}:data/items/{item_id}.tres']).decode('utf-8')
    assert old == base, f'Definition changed before intake: {item_id}'
    if 'icon = ExtResource("2")' in old:
        new = re.sub(r'\[ext_resource type="Texture2D" path="[^"]+" id="2"\]',
            f'[ext_resource type="Texture2D" path="res://{dst_rel}" id="2"]', old)
    else:
        new = old.replace('load_steps=2 ', 'load_steps=3 ', 1)
        new = new.replace('\n[resource]', f'\n[ext_resource type="Texture2D" path="res://{dst_rel}" id="2"]\n\n[resource]', 1)
        new = new.replace('script = ExtResource("1")\n', 'script = ExtResource("1")\nicon = ExtResource("2")\n', 1)
    assert new != old and semantics(new) == semantics(old), f'Non-icon change: {item_id}'
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    def_path.write_text(new, encoding='utf-8', newline='\n')
    assert sha(dst) == item['game_sha256']
    records.append({
        'data_id': item_id, 'display_name': item['display_name'], 'definition': f'data/items/{item_id}.tres',
        'source': f'workbench/production/item_icons_446/game/items/{item_id}.png',
        'destination': dst_rel, 'sha256': item['game_sha256'], 'game_size': item['game_size'],
        'footprint': [item['grid_w'], item['grid_h']], 'previous_icon': item['current_icon'],
        'definition_before_sha256': hashlib.sha256(base.encode('utf-8')).hexdigest(),
        'non_icon_fields_sha256': hashlib.sha256(semantics(base).encode('utf-8')).hexdigest(),
        'definition_after_sha256': sha(def_path), 'unchanged_except_icon': True,
    })

pending_path = GAME / 'tests/test_items.gd'
pending = pending_path.read_text(encoding='utf-8')
pending = pending.replace('const ICON_PENDING := ["satgat", "piju", "injang", ', 'const ICON_PENDING := [', 1)
pending_path.write_text(pending, encoding='utf-8', newline='\n')
intake = GAME / 'art/ui_intake_447'
intake.mkdir(parents=True, exist_ok=True)
(intake / 'intake_manifest.json').write_text(json.dumps({
    'issue': 447, 'production_issue': 446, 'source_repository': 'joseon-assets',
    'source_main': 'f7483c3556cb94c416454fc51bf8140b8655fe07', 'game_base': BASE,
    'method': 'Copy approved PNG bytes; wire ItemDef.icon only; reuse UiSkin alpha-region drawing.',
    'files': records,
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
task = GAME / 'docs/TASK_CURRENT.md'
task.write_text(task.read_text(encoding='utf-8') + '\n- 2026-09-27 #447 `icons_a/items` ← `C:\\workspace\\joseon-assets\\workbench\\production\\item_icons_446\\game\\items` (에셋 f7483c3, PD 승인 #446) → 삿갓·피주·인장·예도·미투리·전대 6PNG·ItemDef.icon, 승인 해시/점유/수치 보존.\n', encoding='utf-8', newline='\n')
print('Intake: 6/6 approved PNG hash/alpha/footprint and non-icon field preservation PASS.')
