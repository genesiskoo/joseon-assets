from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops

game = Path(r'C:\Users\FORYOUCOM\.codex\worktrees\293-monster-elite-ui\joseon')
assets = Path(r'C:\Users\FORYOUCOM\.codex\worktrees\393-ui-icon-redesign\joseon-assets')
source = Path(r'C:\workspace\joseon-assets')
report = assets / 'reports/447/integration_2026-09-27'
manifest = json.loads((game / 'art/ui_intake_447/intake_manifest.json').read_text(encoding='utf-8'))
records = []
for item in manifest['files']:
    p = game / item['destination']
    approved = source / item['source']
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest == item['sha256'] == hashlib.sha256(approved.read_bytes()).hexdigest()
    im = Image.open(p)
    assert list(im.size) == item['game_size'] and im.mode == 'RGBA'
    alpha = im.getchannel('A')
    assert alpha.getextrema() == (0, 255) and alpha.getbbox() is not None
    text = (game / item['definition']).read_text(encoding='utf-8')
    semantic = '\n'.join(line for line in text.splitlines()
        if line.strip() and not line.startswith('[gd_resource ') and not line.startswith('icon = ')
        and not ('[ext_resource type="Texture2D"' in line and 'id="2"' in line))
    assert hashlib.sha256(semantic.encode('utf-8')).hexdigest() == item['non_icon_fields_sha256']
    assert f'path="res://{item["destination"]}" id="2"' in text and 'icon = ExtResource("2")' in text
    records.append({'item_id': item['data_id'], 'sha256': digest, 'size': list(im.size), 'alpha_bbox': alpha.getbbox(),
        'non_icon_fields_preserved': True})

anchors = {'paeraengi': (864,400,944,480), 'leather_shoes': (944,400,1024,480), 'cotton_belt': (1184,360,1264,400)}
baseline = Image.open(report / 't1_inventory_before.png').convert('RGB')
after = Image.open(report / 't1_inventory_after.png').convert('RGB')
anchor_records = []
for name, rect in anchors.items():
    equal = ImageChops.difference(baseline.crop(rect), after.crop(rect)).getbbox() is None
    assert equal, name
    anchor_records.append({'item_id': name, 'rect': list(rect), 'pixels_identical': equal})

old_assets = []
old_manifest = json.loads((game / 'art/ui_intake_439/intake_manifest.json').read_text(encoding='utf-8'))
for item in old_manifest['files']:
    digest = hashlib.sha256((game / item['destination']).read_bytes()).hexdigest()
    assert digest == item['sha256'], item['destination']
    old_assets.append({'destination': item['destination'], 'sha256': digest, 'unchanged': True})

jpegs = []
for p in sorted((game / 'docs/art/447_d1_icons_intake').glob('*.jpg')):
    im = Image.open(p)
    assert im.width == 1280 and p.stat().st_size <= 300_000
    jpegs.append({'file': p.name, 'bytes': p.stat().st_size, 'size': list(im.size)})
assert len(jpegs) == 6
verification = {'issue': 447, 'files': records, 'approved_anchor_pixels': anchor_records,
    'previous_439_assets_unchanged': old_assets, 'gallery': jpegs,
    'engine': 'Godot 4.7.2 stable Steam / Forward+ / Vulkan / RTX 4070',
    'screens': ['bag+9slots+rarity/unidentified', 'held sword', 'merchant+stock6+stamp tooltip'],
    'input': 'E2e genuine marked InputEvents; equipment swaps, held restore, merchant dialogue, buy/sell',
    'production_changes': '6 PNG + 6 ItemDef.icon; no non-icon field or renderer changes'}
(report / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(report / 'intake_manifest.json').write_bytes((game / 'art/ui_intake_447/intake_manifest.json').read_bytes())
print('Asset verification 6/6 PASS; approved anchors pixel-identical 3/3; JPG6 fit limits.')
print('Previous439 asset hashes unchanged:', len(old_assets))
