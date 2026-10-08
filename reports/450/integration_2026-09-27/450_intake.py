from pathlib import Path
import hashlib, json, re, shutil, subprocess
from PIL import Image

game = Path(r'C:/Users/FORYOUCOM/.codex/worktrees/293-monster-elite-ui/joseon')
assets = Path(r'C:/workspace/joseon-assets')
source = assets / 'workbench/production/item_icons_448'
base = subprocess.check_output(['git', '-C', str(game), 'rev-parse', 'HEAD'], text=True).strip()
production = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def semantic(text):
    return '\n'.join(line for line in text.splitlines() if line.strip()
        and not line.startswith('[gd_resource ') and not line.startswith('icon = ')
        and not ('[ext_resource type="Texture2D"' in line and 'id="art450"' in line))

old_files = []
for card in (439, 447):
    m = json.loads((game / f'art/ui_intake_{card}/intake_manifest.json').read_text(encoding='utf-8'))
    for item in m['files']:
        assert sha(game / item['destination']) == item['sha256']
        old_files.append({'destination': item['destination'], 'sha256': item['sha256']})
assert len(old_files) == 23
records = []
for item in production['items']:
    id = item['item_id']
    src = source / f'game/items/{id}.png'
    dest = f'assets/sprites/ui/icons_a/items/{id}.png'
    assert sha(src) == item['game_sha256'] and not (game / dest).exists(), id
    im = Image.open(src)
    assert im.mode == 'RGBA' and list(im.size) == item['game_size']
    assert im.getchannel('A').getextrema()[0] == 0 and im.getchannel('A').getextrema()[1] >= 250
    definition = f'data/items/{id}.tres'
    p = game / definition
    old = p.read_text(encoding='utf-8')
    baseline = subprocess.check_output(['git', '-C', str(game), 'show', f'{base}:{definition}']).decode('utf-8')
    assert old == baseline and 'icon = ' not in old and 'id="art450"' not in old
    new = re.sub(r'load_steps=(\d+)', lambda m: f'load_steps={int(m[1])+1}', old, count=1)
    new = new.replace('\n[resource]', f'\n[ext_resource type="Texture2D" path="res://{dest}" id="art450"]\n\n[resource]', 1)
    new = new.replace('script = ExtResource("1")\n', 'script = ExtResource("1")\nicon = ExtResource("art450")\n', 1)
    assert semantic(new) == semantic(old) and new != old
    shutil.copyfile(src, game / dest)
    p.write_text(new, encoding='utf-8', newline='\n')
    records.append({'data_id': id, 'display_name': item['display_name'], 'definition': definition,
        'source': f'workbench/production/item_icons_448/game/items/{id}.png', 'destination': dest,
        'sha256': item['game_sha256'], 'game_size': item['game_size'], 'footprint': [item['grid_w'],item['grid_h']],
        'previous_icon': None, 'definition_before_sha256': hashlib.sha256(old.encode()).hexdigest(),
        'non_icon_fields_sha256': hashlib.sha256(semantic(old).encode()).hexdigest(),
        'definition_after_sha256': sha(p), 'unchanged_except_icon': True})
p = game / 'tests/test_items.gd'
text = p.read_text(encoding='utf-8')
match = re.search(r'const ICON_PENDING := \[(.*?)\]', text, flags=re.S)
old_pending = re.findall(r'"([^\"]+)"', match[1])
accepted = [item['data_id'] for item in records]
assert len(old_pending) == 15 and all(id in old_pending for id in accepted)
remaining = [id for id in old_pending if id not in accepted]
assert len(remaining) == 9
text = text[:match.start()] + 'const ICON_PENDING := [' + ', '.join(json.dumps(id) for id in remaining) + ']' + text[match.end():]
text = text.replace('## + #304 벽력부(talisman_thunder) = 그림만 기다린다(바닥 모델은 부적 공용이라 MODEL_PENDING 밖).',
    '## #450: 정자관·첨주·윤도·부적 목판·청심환·벽력부 아이콘 반입 완료. 바닥 모델 대기 목록은 유지.')
p.write_text(text, encoding='utf-8', newline='\n')
intake = game / 'art/ui_intake_450'
intake.mkdir(parents=True, exist_ok=True)
(intake / 'intake_manifest.json').write_text(json.dumps({'issue':450,'production_issue':448,
    'source_repository':'joseon-assets','source_commit':'d6f4fd0bf21fc332a0cf5e5bde72e4566e4ebcd7',
    'game_base':base,'approval':'PD 2026-09-27: 채택하고 게임 반입 진행',
    'method':'Copy approved PNG bytes; wire ItemDef.icon only; existing UiSkin alpha-region drawing.',
    'files':records,'previous_assets_unchanged':old_files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
p = game / 'docs/TASK_CURRENT.md'
p.write_text(p.read_text(encoding='utf-8')+'\n- 2026-09-27 #450 `icons_a/items` ← `C:\\workspace\\joseon-assets\\workbench\\production\\item_icons_448\\game\\items` (승인 d6f4fd0) → 정자관·첨주·윤도·부적 목판·청심환·벽력부 6PNG·ItemDef.icon, 기존 23종/점유/수치/벨트 규칙 보존.\n',encoding='utf-8',newline='\n')
print('PASS #450 approved PNG6, non-icon fields6, previous assets23 unchanged, icon_pending15→9; model_pending unchanged.')
