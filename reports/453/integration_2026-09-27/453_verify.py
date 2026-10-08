from pathlib import Path
from PIL import Image, ImageChops
import hashlib, json
game=Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
source=Path('C:/workspace/joseon-assets')
report=Path('C:/workspace/joseon/._tmp/assets_87/reports/453/integration_2026-09-27')
manifest=json.loads((game/'art/ui_intake_453/intake_manifest.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for item in manifest['files']:
    p=game/item['destination']
    assert sha(p)==item['sha256']==sha(source/item['source'])
    im=Image.open(p)
    assert im.mode=='RGBA' and list(im.size)==[80,80] and im.getchannel('A').getextrema()==(0,255)
    text=(game/item['definition']).read_text(encoding='utf-8')
    semantic='\n'.join(line for line in text.splitlines() if line.strip()
        and not line.startswith('[gd_resource ') and not line.startswith('icon = ')
        and not ('[ext_resource type="Texture2D"' in line and 'id="art453"' in line))
    assert hashlib.sha256(semantic.encode()).hexdigest()==item['non_icon_fields_sha256']
    assert sha(game/item['definition'])==item['definition_after_sha256']
    assert 'icon = ExtResource("art453")' in text
    records.append({'id':item['data_id'],'sha256':sha(p),'size':list(im.size),'alpha':im.getchannel('A').getextrema(),'alpha_bbox':im.getchannel('A').getbbox(),'non_icon_fields_preserved':True})
for item in manifest['previous_assets_unchanged']:
    assert sha(game/item['destination'])==item['sha256'], item['destination']
for item in manifest['other_definitions_unchanged']:
    assert sha(game/item['path'])==item['sha256'], item['path']
before=Image.open(report/'material_inventory_before.png').convert('RGB')
after=Image.open(report/'material_inventory_after.png').convert('RGB')
anchors={'satgat':(864,400,944,480),'piju':(944,400,1024,480),'injang':(1024,400,1064,440)}
anchor_records=[]
for name,rect in anchors.items():
    identical=ImageChops.difference(before.crop(rect),after.crop(rect)).getbbox() is None
    assert identical, name
    anchor_records.append({'id':name,'rect':rect,'pixels_identical':identical})
gallery=[]
for p in sorted((game/'docs/art/453_d1_material_intake').glob('*.jpg')):
    im=Image.open(p)
    assert im.size==(1280,720) and p.stat().st_size <= 300_000
    gallery.append({'file':p.name,'bytes':p.stat().st_size,'size':list(im.size)})
assert len(gallery)==6
(report/'intake_manifest.json').write_bytes((game/'art/ui_intake_453/intake_manifest.json').read_bytes())
(report/'verification.json').write_text(json.dumps({'issue':453,'approval':manifest['approval'],
    'files':records,'previous_assets_unchanged':manifest['previous_assets_unchanged'],
    'other_definitions_unchanged':manifest['other_definitions_unchanged'],'approved_anchor_pixels':anchor_records,
    'gallery':gallery,'engine':'Godot4.7.2 stable Steam / Forward+ / Vulkan / RTX4070',
    'input':'actual marked InputEvents: bag pick/place/stack20 merge; real shaman dialogue/shop unlock/buy/sell; loot_dropped six and floor-name click to merge picked tooth3→4',
    'production_changes':'6 approved PNG +6 ItemDef.icon only; icon_pending9→3; no UI renderer, balance, models or drop/shop rules changed'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS #453 hashes6, non-icon fields6, old PNG29, other .tres61, exact anchor pixels3, gallery limits6.')
