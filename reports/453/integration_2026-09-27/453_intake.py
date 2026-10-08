from pathlib import Path
from PIL import Image
import hashlib, json, re, subprocess
game = Path('C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon')
source_repo = Path('C:/workspace/joseon-assets')
source = source_repo/'workbench/production/item_icons_452'
production = json.loads((source/'manifest.json').read_text(encoding='utf-8'))
base = subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'],text=True).strip()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def semantic(text):
    return '\n'.join(line for line in text.splitlines() if line.strip()
        and not line.startswith('[gd_resource ') and not line.startswith('icon = ')
        and not ('[ext_resource type="Texture2D"' in line and 'id="art453"' in line))
previous = []
for card in (439,447,450):
    manifest = json.loads((game/f'art/ui_intake_{card}/intake_manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        assert sha(game/item['destination']) == item['sha256']
        previous.append({'destination':item['destination'],'sha256':item['sha256']})
assert len(previous) == 29
unchanged_defs=[]
accepted_ids=[it['item_id'] for it in production['items']]
for p in sorted((game/'data/items').glob('*.tres')):
    if p.stem not in accepted_ids:
        unchanged_defs.append({'path':p.relative_to(game).as_posix(),'sha256':sha(p)})
assert len(unchanged_defs)==61
records=[]
for item in production['items']:
    id=item['item_id']
    src=source/f'game/items/{id}.png'
    dest=f'assets/sprites/ui/icons_a/items/{id}.png'
    assert sha(src)==item['game_sha256']==sha(game/dest), id
    im=Image.open(game/dest)
    assert im.mode=='RGBA' and im.size==(80,80) and im.getchannel('A').getextrema()==(0,255)
    definition=f'data/items/{id}.tres'
    p=game/definition
    old=p.read_text(encoding='utf-8')
    baseline=subprocess.check_output(['git','-C',str(game),'show',f'{base}:{definition}']).decode('utf-8')
    assert old==baseline and 'icon = ' not in old
    new=re.sub(r'load_steps=(\d+)',lambda m:f'load_steps={int(m[1])+1}',old,count=1)
    new=new.replace('\n[resource]',f'\n[ext_resource type="Texture2D" path="res://{dest}" id="art453"]\n\n[resource]',1)
    new=new.replace('script = ExtResource("1")\n','script = ExtResource("1")\nicon = ExtResource("art453")\n',1)
    assert semantic(new)==semantic(old) and new!=old
    p.write_text(new,encoding='utf-8',newline='\n')
    records.append({'data_id':id,'display_name':item['display_name'],'definition':definition,
        'source':f'workbench/production/item_icons_452/game/items/{id}.png','destination':dest,
        'sha256':item['game_sha256'],'game_size':[80,80],'footprint':[1,1],
        'previous_icon':None,'definition_before_sha256':hashlib.sha256(old.encode()).hexdigest(),
        'non_icon_fields_sha256':hashlib.sha256(semantic(old).encode()).hexdigest(),
        'definition_after_sha256':sha(p),'unchanged_except_icon':True})
p=game/'tests/test_items.gd'
text=p.read_text(encoding='utf-8')
match=re.search(r'const ICON_PENDING := \[(.*?)\]',text,re.S)
pending=re.findall(r'"([^\"]+)"',match[1])
assert len(pending)==9 and all(id in pending for id in accepted_ids)
remaining=[id for id in pending if id not in accepted_ids]
assert len(remaining)==3
text=text[:match.start()]+'const ICON_PENDING := ['+', '.join(json.dumps(id) for id in remaining)+']'+text[match.end():]
text=text.replace('const ICON_PENDING :=', '## #453: 승인 재료6종 반입 완료. 아이콘 대기 = 봉인조각3, 모델 대기는 그대로.\nconst ICON_PENDING :=',1)
p.write_text(text,encoding='utf-8',newline='\n')
intake=game/'art/ui_intake_453'
intake.mkdir(parents=True,exist_ok=True)
(intake/'intake_manifest.json').write_text(json.dumps({'issue':453,'production_issue':452,
    'source_repository':'joseon-assets','source_commit':'f96e2931e8fed818b1952642b3fe685edfee1006',
    'game_base':base,'approval':'PD 2026-09-27: 승인 다음',
    'method':'PowerShell Copy-Item of approved PNG bytes; ItemDef.icon only; existing UiSkin alpha-region drawing.',
    'files':records,'previous_assets_unchanged':previous,'other_definitions_unchanged':unchanged_defs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
p=game/'docs/TASK_CURRENT.md'
p.write_text(p.read_text(encoding='utf-8')+'\n- 2026-09-27 #453 `icons_a/items` ← `C:\\workspace\\joseon-assets\\workbench\\production\\item_icons_452\\game\\items` (承認 f96e293) → 再料6PNG·ItemDef.icon; 기존29PNG/점유/가격/가중/상점해금/스택/보스드랍/모델 보존.\n'.replace('承認','승인').replace('再料','재료'),encoding='utf-8',newline='\n')
print('PASS #453 approved PNG6, non-icon fields6, previous PNG29 and other ItemDef61 preserved, icon_pending9→3; MODEL_PENDING unchanged.')
