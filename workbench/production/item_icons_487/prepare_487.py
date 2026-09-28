"""Capture planned sword contracts and preserve existing runtime before art."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon')
PLAN = [
    ('ungeom', '운검', 'bongukgeom', '본국검', '궁중호위·쪽빛/담청옥/정제된쇠'),
    ('keun_kal', '환두대도', 'ssangsudo', '쌍수도', '빈고리꼭지·넓은날·갈색가죽'),
    ('chilseonggeom', '칠성검', 'saingeom', '사인검', '칠성7점의 금속새김·밝은쇠'),
    ('u_yongcheon', '운룡검', 'ungeom', '운검', '운검끝칼·유백실/옥금/구름새김'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def runtime_files():
    files = list((GAME / 'assets/sprites/ui/icons_a').rglob('*.png'))
    files += list((GAME / 'assets/sprites/ui/icons_h1').glob('*.png'))
    files += list((GAME / 'data/items').glob('*.tres')) + list((GAME / 'data/uniques').glob('*.tres'))
    files += [GAME / p for p in ['items/unique_def.gd', 'items/item_instance.gd', 'ui/ui_skin.gd', 'ui/inventory_ui.gd', 'ui/vendor_ui.gd', 'ui/hover_tip.gd', 'ui/hud.gd']]
    return sorted(files)


def main():
    catalog = GAME / 'docs/design/item_catalog_v2.md'
    system = GAME / 'docs/design/item_system_v2.md'
    catalog_text = catalog.read_text(encoding='utf-8')
    system_text = system.read_text(encoding='utf-8')
    assert '### 4.2 도호 칼 (`item_type = sword`, 1×3)' in system_text
    assert '| u_yongcheon |' in system_text and '| T3 | ungeom | 운검 |' in system_text
    remaining = json.loads((GAME / 'art/item_catalog_274/remaining_after_485_2026-09-28.json').read_text(encoding='utf-8'))
    pending = {r['production_key']: r for r in remaining['entries']}
    assert remaining['remaining_core'] == 35
    rows = []
    for uid, name, ref, ref_name, note in PLAN:
        row = pending[uid]
        assert row['display_name'] == name and row['definition_state'] == 'design_only'
        assert (row['grid_w'], row['grid_h']) == (1, 3)
        target = GAME / ('data/uniques' if uid.startswith('u_') else 'data/items') / f'{uid}.tres'
        assert not target.exists(), f'Planned definition now exists, revalidate before art: {target}'
        if uid.startswith('u_'):
            reference = ROOT / 'game/items/ungeom.png'
            reference_status = 'same_batch_planned_T3_base_candidate'
            reference_sha = None
        else:
            assert f'| {uid} | {name}' in catalog_text
            reference = GAME / 'assets/sprites/ui/icons_a/items' / f'{ref}.png'
            assert reference.exists()
            reference_status = 'current_approved_T2_game_icon'
            reference_sha = sha(reference)
        rows.append(dict(item_id=uid, display_name=name, grid_w=1, grid_h=3, output_width=80, output_height=240,
                         definition_state='design_only', planned_definition_path=target.as_posix(),
                         planned_tier=3, planned_slot=0, base_id='ungeom' if uid.startswith('u_') else None,
                         reference_id=ref, reference_display_name=ref_name, reference_path=reference.as_posix(),
                         reference_status=reference_status, reference_sha256=reference_sha, note=note,
                         intake_predecessor=272))
    docs = {p.relative_to(GAME).as_posix(): sha(p) for p in [catalog, system]}
    inputs = dict(card=487, parent_card=274, approved_remaining=35, source_docs=docs, items=rows)
    before = {p.relative_to(GAME).as_posix(): sha(p) for p in runtime_files()}
    assert len(before) == 154
    assert sum(k.startswith('assets/sprites/ui/icons_a/') and k.endswith('.png') for k in before) == 42
    (ROOT / 'inputs.json').write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    (ROOT / 'runtime_before.json').write_text(json.dumps(before, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PREPARED #487 planned swords4/no runtime definitions; docs contracts1x3; runtime154/PNG42+H1PNG19 preserved')


if __name__ == '__main__':
    main()
