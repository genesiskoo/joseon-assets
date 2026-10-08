from pathlib import Path
import json
p=Path(r'C:\Users\FORYOUCOM\.codex\worktrees\393-ui-icon-redesign\joseon-assets\reports\447\integration_2026-09-27')
r=json.loads((p/'captures_before.json').read_text(encoding='utf-8'))
assert r[0]['source'].endswith('icon_intake_06_t1_inventory.png')
r[0]['requested_state']='inventory'
r[0]['state']='t1_inventory_duplicate'
r[0]['note']='Suffix glob selected T1 inventory; first439 inventory-before raw was not retained. Primary T1 before/after three pairs remain exact.'
(p/'captures_before.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'inventory_before.png').rename(p/'t1_inventory_before_duplicate.png')
q=(p/'README.md').read_text(encoding='utf-8').replace('8상태×전후 PNG16:','전후 PNG16(반입전 기존 inventory는 T1 중복 보관, 아래 메모):')
(p/'README.md').write_text(q+'\n보관 메모: 첫 사진 수집의 inventory 접미사가 t1_inventory와 겹쳤다. 반입전 inventory_before 사본은 T1 중복이므로 t1_inventory_before_duplicate로 명시하고 captures_before에도 기록했다. 반입후 기존 inventory는 정확한01번 파일로 재보관했고 수집 도구는 정확한 번호/상태 경로로 수정했다. 판정에 쓴 T1 전후3쌍·해시6/6·기준물체3/3은 처음부터 정확하다.\n',encoding='utf-8')