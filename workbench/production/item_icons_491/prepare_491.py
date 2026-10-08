"""Capture planned armor contracts and approved T2 art without changing runtime."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/464-t2-armor-art/joseon')
REF = Path('C:/workspace/joseon-assets/workbench/production/item_icons_464')
PLAN = [
    ('eomsimgap', '엄심갑', 'gyeongbeongap', '경번갑', '심장만 덮는 호심경과 빈 지지 끈'),
    ('sueungap', '수은갑', 'dujeonggap', '두정갑', '정교한 은빛 철판·쪽빛 안감·윤나는 마감'),
    ('geuksang_dopo', '심의', 'hakchangui', '학창의', '흰 예복·검은 가장자리·정돈된 긴 주름'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_files():
    files = list((GAME / 'assets/sprites/ui/icons_a').rglob('*.png'))
    files += list((GAME / 'assets/sprites/ui/icons_h1').glob('*.png'))
    files += list((GAME / 'data/items').glob('*.tres')) + list((GAME / 'data/uniques').glob('*.tres'))
    files += [GAME / p for p in ['items/unique_def.gd', 'items/item_instance.gd', 'ui/ui_skin.gd',
              'ui/inventory_ui.gd', 'ui/vendor_ui.gd', 'ui/hover_tip.gd', 'ui/hud.gd']]
    return sorted(files)


def main():
    catalog = GAME / 'docs/design/item_catalog_v2.md'
    system = GAME / 'docs/design/item_system_v2.md'
    cat_text, sys_text = catalog.read_text(encoding='utf-8'), system.read_text(encoding='utf-8')
    assert '### 4.3 갑옷' in sys_text and '2×3' in sys_text
    pending = json.loads((GAME / 'art/item_catalog_274/remaining_after_487_2026-09-28.json').read_text(encoding='utf-8'))
    assert pending['remaining_core'] == 31
    keys = {r['production_key']: r for r in pending['entries']}
    reference = json.loads((REF / 'manifest.json').read_text(encoding='utf-8'))
    refs = {r['item_id']: r for r in reference['items']}
    rows = []
    for uid, name, rid, rname, note in PLAN:
        entry = keys[uid]
        assert entry['definition_state'] == 'design_only' and (entry['grid_w'], entry['grid_h']) == (2, 3)
        assert f'| {uid} |' in cat_text and f'| T3 | {uid} |' in sys_text
        definition = GAME / 'data/items' / f'{uid}.tres'
        assert not definition.exists(), f'Revalidate new T3 definition before art: {definition}'
        ref_path = REF / 'game/items' / f'{rid}.png'
        assert ref_path.exists() and sha(ref_path) == refs[rid]['game_sha256']
        rows.append(dict(item_id=uid, display_name=name, grid_w=2, grid_h=3,
                         output_width=160, output_height=240, definition_state='design_only',
                         planned_definition_path=definition.as_posix(), planned_tier=3, planned_slot=1,
                         reference_id=rid, reference_display_name=rname, reference_path=ref_path.as_posix(),
                         reference_status='PD_approved_T2_art_464_not_installed', reference_sha256=sha(ref_path),
                         note=note, intake_predecessor=272))
    docs = {p.relative_to(GAME).as_posix(): sha(p) for p in [catalog, system]}
    inputs = dict(card=491, parent_card=274, approved_remaining=31, source_docs=docs, items=rows)
    before = {p.relative_to(GAME).as_posix(): sha(p) for p in runtime_files()}
    assert sum(k.startswith('assets/sprites/ui/icons_a/') and k.endswith('.png') for k in before) == 42
    assert sum(k.startswith('assets/sprites/ui/icons_h1/') and k.endswith('.png') for k in before) == 19
    for name, value in [('inputs.json', inputs), ('runtime_before.json', before)]:
        (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    spec = GAME / 'docs/design/ui_v2.md'
    text = spec.read_text(encoding='utf-8')
    section = '''
## #491 D1 T3 갑·포3 원화 후보 계약 (2026-09-28)

엄심갑(eomsimgap)·수은갑(sueungap)·심의(geuksang_dopo) 신규3를 item_catalog_v2 §1.2·§1.3 / item_system_v2 §4.3의 예정T3/ARMOR/2×3/160×240 RGBA로 제작한다. 실제ItemDef는없으며 게임반입은 #272 데이터뒤 최종정의/점유와재대조하는별도카드다. 엄심갑=심장만덮는호심경류금속판/빈지지끈, 수은갑=정교한은빛철판/쪽빛안감/윤나는가공세계최상급갑옷(실물고증주장없음), 심의=흰예복/검은가장자리/상하가이어진긴정돈주름. 내장imagegen/native/정확프롬프트/SHA보존→알파16/8%여백/Lanczos비율패킹→실제UiSkin 가방/검정40·좌판48/30·48·60/승인T2 경번갑·두정갑·학창의/무채색을검수한다. 비교#464도아직게임반입전임을명시한다. JPG≤6/폭1280/각300KB=docs/art/491_d1_t3_armor, native/raw=자산workbench/production/item_icons_491·reports/491. 기존PNG42/H1PNG19·정의/UI·수치/세이브/3D는보존, 승인잔여31유지/이번3전부채택시28·현정의4/설계24. 좋은장비일수록재질/마감/실루엣이좋게보이도록하며기존검/물약폴리싱은후속이다.

왜 이 구조인가: 사양이 고정된 물체를 먼저 만들고 승인 T2 원화 및 공용 UiSkin에서 대조하면 데이터 작업을 기다리며 원화를 진행할 수 있다. 임시 정의나 기존 T2 그림 교체는 데이터와 비대상 표시를 바꾸므로 기각한다.
'''
    if '## #491 D1 T3 갑·포3 원화 후보 계약' not in text:
        spec.write_text(text.rstrip() + '\n' + section, encoding='utf-8', newline='\n')
    print(f'PREPARED #491 planned armor3/2x3/no definitions; approved T2 SHA3; runtime{len(before)}/PNG42+H1PNG19')


if __name__ == '__main__':
    main()
