from pathlib import Path
from PIL import Image, ImageChops
import hashlib, json, shutil

game = Path(r'C:/Users/FORYOUCOM/.codex/worktrees/293-monster-elite-ui/joseon')
assets = Path(r'C:/Users/FORYOUCOM/.codex/worktrees/393-ui-icon-redesign/joseon-assets')
source = Path(r'C:/workspace/joseon-assets')
report = assets / 'reports/450/integration_2026-09-27'
manifest = json.loads((game / 'art/ui_intake_450/intake_manifest.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = []
for item in manifest['files']:
    p = game / item['destination']
    assert sha(p) == item['sha256'] == sha(source/item['source'])
    im = Image.open(p)
    assert im.mode == 'RGBA' and list(im.size) == item['game_size']
    alpha = im.getchannel('A')
    assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 250
    text = (game / item['definition']).read_text(encoding='utf-8')
    semantic = '\n'.join(line for line in text.splitlines() if line.strip()
        and not line.startswith('[gd_resource ') and not line.startswith('icon = ')
        and not ('[ext_resource type="Texture2D"' in line and 'id="art450"' in line))
    assert hashlib.sha256(semantic.encode()).hexdigest() == item['non_icon_fields_sha256']
    assert sha(game/item['definition']) == item['definition_after_sha256']
    assert 'icon = ExtResource("art450")' in text
    records.append({'item_id':item['data_id'],'sha256':sha(p),'size':list(im.size),
        'alpha':alpha.getextrema(),'alpha_bbox':alpha.getbbox(),'non_icon_fields_preserved':True})
for item in manifest['previous_assets_unchanged']:
    assert sha(game/item['destination']) == item['sha256'], item['destination']
before = Image.open(report/'t2_inventory_before.png').convert('RGB')
after = Image.open(report/'t2_inventory_after.png').convert('RGB')
anchors = {'satgat':(864,400,944,480),'piju':(944,400,1024,480),'injang':(1024,400,1064,440)}
anchor_records = []
for name, rect in anchors.items():
    identical = ImageChops.difference(before.crop(rect),after.crop(rect)).getbbox() is None
    assert identical, name
    anchor_records.append({'id':name,'rect':rect,'pixels_identical':identical})
gallery = []
for p in sorted((game/'docs/art/450_d1_t2_intake').glob('*.jpg')):
    im = Image.open(p)
    assert im.width == 1280 and p.stat().st_size <= 300_000
    gallery.append({'file':p.name,'bytes':p.stat().st_size,'size':list(im.size)})
assert len(gallery) == 6
(report/'intake_manifest.json').write_bytes((game/'art/ui_intake_450/intake_manifest.json').read_bytes())
(report/'verification.json').write_text(json.dumps({'issue':450,'approval':manifest['approval'],'files':records,
    'previous_assets_unchanged':manifest['previous_assets_unchanged'],'approved_anchor_pixels':anchor_records,
    'gallery':gallery,'engine':'Godot 4.7.2 stable Steam / Forward+ / Vulkan / RTX4070',
    'input':'E2e marked real InputEvents; held last cell, equipment swap, vendor dialogue/buy/sell, rejuv use/rejected belt, thunder belt/town gate/dungeon cast',
    'production_changes':'6 PNG + 6 ItemDef.icon only; no renderer, balance, stack, belt-rule or model changes'},
    ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS #450 source hashes6, non-icon fields6, previous hashes23, approved anchor pixels3, gallery limits6.')
