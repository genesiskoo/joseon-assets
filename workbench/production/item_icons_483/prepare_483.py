"""Capture unique/base contracts and preserve every relevant runtime byte."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon')
ASSETS = Path('C:/workspace/joseon-assets')
PLAN = [
    ('u_heukrang_fang', '흑랑 송곳니', 'jade_charm', 1, '옥 마감·짧은 매듭의 송곳니 호신부'),
    ('u_jangsanbeom_eye', '장산범의 눈', 'myeongdu', 2, '놋거울에 깃든 짐승 눈빛'),
    ('u_fox_bead', '여우구슬', 'yagwangju', 3, '유백 구슬·붉은 속빛·짧은 홍색 매듭'),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def val(t, name, default=None):
    match = re.search(r'^'+re.escape(name)+r' = (.+)$', t, re.M)
    return match.group(1).strip('"') if match else default

def runtime_files():
    files = list((GAME/'assets/sprites/ui/icons_a').rglob('*.png'))
    files += list((GAME/'data/items').glob('*.tres')) + list((GAME/'data/uniques').glob('*.tres'))
    files += [GAME/p for p in ['items/unique_def.gd','items/item_instance.gd','ui/ui_skin.gd','ui/inventory_ui.gd','ui/vendor_ui.gd','ui/hover_tip.gd','ui/hud.gd']]
    return sorted(files)

def main():
    items=[]
    for uid,name,base,tier,note in PLAN:
        definition=GAME/'data/uniques'/f'{uid}.tres'
        base_def=GAME/'data/items'/f'{base}.tres'
        u=definition.read_text(encoding='utf-8');b=base_def.read_text(encoding='utf-8')
        assert val(u,'id')==uid and val(u,'display_name')==name and val(u,'base_id')==base
        assert val(b,'size')=='Vector2i(1, 1)' and val(b,'slot')=='2'
        assert int(val(b,'tier','1'))==tier
        reference=GAME/'assets/sprites/ui/icons_a/items/jade_charm.png' if base=='jade_charm' else ASSETS/'workbench/production/item_icons_467/game/items'/f'{base}.png'
        assert reference.exists()
        items.append(dict(item_id=uid,display_name=name,base_id=base,base_display_name=val(b,'display_name'),grid_w=1,grid_h=1,output_width=80,output_height=80,slot=2,tier=tier,max_stack=1,note=note,definition_path=definition.as_posix(),definition_sha256=sha(definition),base_definition_path=base_def.as_posix(),base_definition_sha256=sha(base_def),base_reference_path=reference.as_posix(),base_reference_sha256=sha(reference),binding_status='unique_icon_path_not_implemented'))
    assert '@export var icon' not in (GAME/'items/unique_def.gd').read_text(encoding='utf-8')
    snapshot={p.relative_to(GAME).as_posix():sha(p) for p in runtime_files()}
    assert sum(k.endswith('.png') for k in snapshot)==42
    (ROOT/'inputs.json').write_text(json.dumps(dict(card=483,parent_card=274,items=items),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (ROOT/'runtime_before.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PREPARED unique/base3; snapshot',len(snapshot),'files; existing PNG42; no unique icon binding')

if __name__=='__main__':
    main()
