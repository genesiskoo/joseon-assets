"""Capture unique/base footprints and all relevant runtime bytes before art."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent
GAME=Path('C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon')
ASSETS=Path('C:/workspace/joseon-assets')
PLAN=[
    ('u_soe_eater','쇠 먹는 이빨','long_sword',1,3,0,1,'불가살이 장검·짙은 쇠/밝은 날'),
    ('u_chukji_shoes','축지 짚신','straw_shoes',2,2,5,1,'촘촘한 짚 엮임·쪽빛 축지 매듭'),
    ('u_seonnyeo_robe','선녀 날개옷','silk_dopo',2,3,1,2,'교차 깃·넓은 소매·유백 비단'),
    ('u_sain_sword','사인참사검','saingeom',1,3,0,2,'곧은 양날·절제된 금빛 새김'),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def val(t,key,default=None):
    m=re.search(r'^'+re.escape(key)+r' = (.+)$',t,re.M)
    return m.group(1).strip('"') if m else default

def runtime_files():
    files=list((GAME/'assets/sprites/ui/icons_a').rglob('*.png'))
    files+=list((GAME/'data/items').glob('*.tres'))+list((GAME/'data/uniques').glob('*.tres'))
    files+=[GAME/p for p in ['items/unique_def.gd','items/item_instance.gd','ui/ui_skin.gd','ui/inventory_ui.gd','ui/vendor_ui.gd','ui/hover_tip.gd','ui/hud.gd']]
    files+=list((GAME/'assets/sprites/ui/icons_h1').glob('*.png'))
    return sorted(files)

def main():
    items=[]
    for uid,name,base,w,h,slot,tier,note in PLAN:
        u_path=GAME/'data/uniques'/f'{uid}.tres'
        b_path=GAME/'data/items'/f'{base}.tres'
        u=u_path.read_text(encoding='utf-8');b=b_path.read_text(encoding='utf-8')
        assert val(u,'id')==uid and val(u,'display_name')==name and val(u,'base_id')==base
        assert val(b,'size')==f'Vector2i({w}, {h})' and int(val(b,'slot'))==slot and int(val(b,'tier','1'))==tier
        icon=re.search(r'\[ext_resource type="Texture2D" path="([^"]+)"',b).group(1)
        reference=ASSETS/'workbench/production/item_icons_464/game/items/silk_dopo.png' if base=='silk_dopo' else GAME/icon.removeprefix('res://')
        assert reference.exists()
        items.append(dict(item_id=uid,display_name=name,base_id=base,base_display_name=val(b,'display_name'),grid_w=w,grid_h=h,output_width=w*80,output_height=h*80,slot=slot,tier=tier,max_stack=int(val(b,'max_stack','1')),note=note,definition_path=u_path.as_posix(),definition_sha256=sha(u_path),base_definition_path=b_path.as_posix(),base_definition_sha256=sha(b_path),base_reference_path=reference.as_posix(),base_reference_sha256=sha(reference),base_reference_status='approved_asset_awaiting_intake_466' if base=='silk_dopo' else 'current_game_base_icon',binding_status='unique_icon_path_not_implemented'))
    assert '@export var icon' not in (GAME/'items/unique_def.gd').read_text(encoding='utf-8')
    snapshot={p.relative_to(GAME).as_posix():sha(p) for p in runtime_files()}
    assert sum(k.startswith('assets/sprites/ui/icons_a/') and k.endswith('.png') for k in snapshot)==42
    (ROOT/'inputs.json').write_text(json.dumps(dict(card=485,parent_card=274,items=items),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (ROOT/'runtime_before.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PREPARED unique/base4, snapshot',len(snapshot),'files; existing icons_a PNG42; no unique icon binding')

if __name__=='__main__':
    main()
