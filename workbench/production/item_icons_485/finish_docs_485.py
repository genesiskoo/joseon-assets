"""Save candidate documentation/ledger in the game worktree, no runtime edits."""
from pathlib import Path
import json
from prepare_485 import GAME

ROOT = Path(__file__).resolve().parent

SPEC = '''
## #485 D1 대표유니크 검·신·도포4 원화 후보 계약 (2026-09-28)

#274 승인핵심잔여39 중 실제정의 쇠 먹는 이빨(u_soe_eater)·축지 짚신(u_chukji_shoes)·선녀 날개옷(u_seonnyeo_robe)·사인참사검(u_sain_sword)을 신규 제작한다. 정본 item_catalog_v2 §2·item_system_v2 §8/§17 및 실제 UniqueDef/베이스ItemDef를 확인했다. 순서대로 장검1×3/80×240·짚신2×2/160×160·비단도포2×3/160×240·사인검1×3/80×240의 점유·장착·tier·stack을 따른다. 짙은 쇠와 밝은 날/송곳니 꼭지, 촘촘한 짚과 쪽빛 매듭, 교차 깃·넓은 소매의 유백 비단, 정교한 금속 마감의 곧은 양날을 실물로 표현한다. 원화마다 내장 imagegen을 사용해 native4(검724×2172/신1254×1254/포1024×1536)·정확한 프롬프트·해시를 자산 브랜치 codex/485-d1-unique-equipment의 workbench/production/item_icons_485에 보존했다. 알파16·8%여백·Lanczos 비율패킹 뒤 실제 UiSkin4모드(40px/검정/30·48·60px/베이스대조) PASS·오류0. 날개옷 주변 RGB는알파0이며 실제 검정칸에서 후광이없다. 비단 베이스 비교는#464 채택 원화이며 미반입 상태를 명시했다. 원화/UiSkin JPG5장은 docs/art/485_d1_unique_equipment, PNG와raw는자산 reports/485/2026-09-28에 있다. 기존PNG42/H1 PNG19·정의/UI154파일 바이트동일을 확인했다. 현재UniqueDef 전용그림 선택은#484 선행이며 후보는메모리검수·미채택·미게임반입이다. 승인잔여39 유지, 전부채택시35(실제4/설계31); 근거는art/item_catalog_274/candidate_485_2026-09-28.json. 기존검/물약폴리싱·수치/세이브/3D외형은 이번에 바꾸지 않는다.

왜 이 구조인가: 베이스의 실제 종류와 점유 계약을 유지하면서 설화·재질·마감으로 고유품을 구별하면 추가 아이템 기능 없이도 시각적 가치를 드러낼 수 있다. 이름만 보고 장검을 재료 이빨로 바꾸거나 베이스 공용 PNG를 덮어쓰는 대안은 종류/비대상 표시까지 바꾸므로 기각한다.
'''


def main():
    verification = json.loads((ROOT / 'verification.json').read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    assert verification['items'] == 4 and verification['runtime_files_byte_match'] == 154
    doc = GAME / 'docs/design/ui_v2.md'
    current = doc.read_text(encoding='utf-8')
    marker = '## #485 D1 대표유니크 검·신·도포4 원화 후보 계약'
    if marker not in current:
        doc.write_text(current.rstrip() + '\n' + SPEC, encoding='utf-8', newline='\n')
    gallery = GAME / 'docs/art/485_d1_unique_equipment'
    gallery.mkdir(parents=True, exist_ok=True)
    text = '''# #485 대표유니크 장비4 검토판

쇠 먹는 이빨 / 축지 짚신 / 선녀 날개옷 / 사인참사검. 신규 원화 후보이며 미채택·미게임반입이다.

- overview.jpg: 원화4/기본베이스/40px칸/무채색.
- godot_forty.jpg: 실제UiSkin 가방40px/검정40px/좌판48px칸.
- godot_sizes.jpg: 실제UiSkin 30/48/60px칸.
- godot_black_sizes.jpg: 실제검정칸 30/48/60px칸.
- godot_base_compare.jpg: 같은UiSkin에서 기본과후보 30/40/60px칸. 비단도포는 #464 채택 자산·#466 미반입.

4모드 PASS/오류0, RGBA4/실제베이스 점유·이름·장착·tier·stack확인. 원본/후보SHA일치 및기존PNG42/H1 PNG19·정의/UI154파일바이트동일. 날개옷외부회색RGB는알파0이며실제칸에서후광없음. JPG5/각300KB미만. 30px에서미세문양은약해지며40px에서주요재질차를확인했다.

원본/프롬프트/manifest/verification/QA는자산브랜치 codex/485-d1-unique-equipment의 workbench/production/item_icons_485, raw/렌더PNG는 reports/485/2026-09-28. UniqueDef 전용그림 선택 #484 뒤 실제연결한다. 승인잔여39유지, 4종전부채택시35.
'''
    (gallery / 'README.md').write_text(text, encoding='utf-8', newline='\n')
    ledger = dict(card=485, parent_card=274, date='2026-09-28', status='candidate_pending_pd',
                  approved_core_remaining=39, approved_existing_definitions=8, approved_design_only=31,
                  conditional_remaining_if_all_accepted=35, conditional_existing_definitions=4,
                  basis='approval_483_2026-09-28.json and remaining_after_483_2026-09-28.json',
                  candidates=[dict(item_id=r['item_id'], display_name=r['display_name'], base_id=r['base_id'],
                                   footprint=[r['grid_w'], r['grid_h']], game_path=r['game_path'],
                                   game_sha256=r['game_sha256'], source_sha256=r['source_sha256'])
                              for r in manifest['items']],
                  runtime_installed=False, intake_predecessor=484)
    dest = GAME / 'art/item_catalog_274/candidate_485_2026-09-28.json'
    dest.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('DOCS #485 candidate spec + JPG5 README + conditional ledger; approved remaining39 unchanged')


if __name__ == '__main__':
    main()
