"""Write candidate spec and review ledger without introducing T3 data."""
import json
from pathlib import Path
from prepare_487 import GAME

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    verification = json.loads((ROOT / 'verification.json').read_text(encoding='utf-8'))
    assert verification['items'] == 4 and verification['runtime_files_byte_match'] == 154
    assert len(verification['godot_ui_skin_modes']) == 5
    doc = GAME / 'docs/design/ui_v2.md'
    text = doc.read_text(encoding='utf-8')
    section = '''
## #487 D1 T3 칼3·운룡검 원화 후보 계약 (2026-09-28)

#274 승인핵심잔여35의 운검(ungeom)·환두대도(keun_kal)·칠성검(chilseonggeom)·운룡검(u_yongcheon)을 사양기반1×3/80×240 RGBA로 제작한다. 정본 item_catalog_v2 §1.1/§2·item_system_v2 §4.2/§8.2, 현재ItemDef/UniqueDef는없고 실제반입은 #272 선행과최종정의 대조 뒤다. 궁중호위칼/빈고리꼭지의무거운칼/칠성7점 금속새김/운검계열끝칼을 쪽빛·가죽·정교한쇠·유백실/옥/금 마감으로 구별한다. 좋은칼일수록 물체의재질/날/마감이좋아보이게 하는신규T3방향이며 기존그림은폴리싱하지않는다. 내장imagegen 신규원본4+칠성정밀편집1(모두724×2172RGBA), 정확한프롬프트·native/sourceSHA·원안8점/v1패킹/검토판을 자산 codex/487-d1-t3-swords의 workbench/production/item_icons_487에 보존했다. 최종칠성v2는 손잡이3점+그릇4점=7점, 환두대도 고리안은실제알파0다. 알파16·8%여백·Lanczos비율보존 뒤 실제UiSkin5모드(40/검정/30·48·60/앞선단대조/칠성전후) PASS·오류0. 비교=기존T2 본국검/쌍수도/사인검, 운룡검=이번운검후보이며 실제새아이템 검증과구별한다. JPG6(1280폭/각300KB미만)=docs/art/487_d1_t3_swords, raw/PNG=자산reports/487/2026-09-28. 기존PNG42/H1PNG19·정의/UI154파일은바이트동일이며 신규데이터/수치/세이브/3D모델은그대로다. 현재미채택·미게임반입, 승인잔여35 유지; 전부채택시31(현재정의4/설계27)이며 근거art/item_catalog_274/candidate_487_2026-09-28.json에기록한다.

왜 이 구조인가: 확정된 이름/점유 사양을 먼저 원화로 만들고 #272 뒤 실제정의를 대조하면 데이터 작업과 아트 제작을 각각 추적할 수 있다. 임시 ItemDef/UniqueDef로 2회차 기능까지 들이거나 기존T2 PNG를 덮는 대안은 새기능/비대상 표시를바꾸므로 기각한다.
'''
    if '## #487 D1 T3 칼3·운룡검 원화 후보 계약' not in text:
        doc.write_text(text.rstrip() + '\n' + section, encoding='utf-8', newline='\n')
    gallery = GAME / 'docs/art/487_d1_t3_swords'
    gallery.mkdir(parents=True, exist_ok=True)
    readme = '''# #487 T3 칼3·운룡검 검토판

운검 / 환두대도 / 칠성검v2 / 운룡검. 사양기반 신규원화 후보이며 아직미채택·미게임반입이다. 모두예정1×3/80×240RGBA, 실제새ItemDef/UniqueDef는없다. 데이터연결은 #272 선행뒤 최종정의와다시대조한다.

- overview.jpg: 원화4 / T2·운검후보 비교 / 40px / 무채색.
- godot_forty.jpg: 실제UiSkin 가방40px/검정40px/좌판48px칸.
- godot_sizes.jpg: 실제UiSkin 30/48/60px칸.
- godot_black_sizes.jpg: 실제검정칸 30/48/60px칸.
- godot_base_compare.jpg: 같은UiSkin에서 T2 본국검/쌍수도/사인검, 운룡검은이번운검후보와비교.
- godot_constellation_pair.jpg: 원안8점→v2 7점. 같은원화부분/배율과40·60px UiSkin의전후.

5모드 PASS/오류0, 원본4+칠성정밀편집1/정확한프롬프트·v1원안 보존. 칠성점수는원화직접검수3+4=7이며 자동인식검사를주장하지않는다. 빈고리꼭지의내부알파0, 기존PNG42/H1PNG19·정의/UI154바이트동일을확인했다. JPG6/각300KB미만. 30px에서미세문양은약해지며40px에서주요재질/형태를본다.

원본/manifest/PROMPTS/verification/QA는자산 codex/487-d1-t3-swords의 workbench/production/item_icons_487, raw/PNG는 reports/487/2026-09-28. 현재승인잔여35 유지, 4종전부채택시31/현재정의4·설계27.
'''
    (gallery / 'README.md').write_text(readme, encoding='utf-8', newline='\n')
    ledger = dict(card=487, parent_card=274, date='2026-09-28', status='candidate_pending_pd',
                  basis='approval_485_2026-09-28.json and remaining_after_485_2026-09-28.json',
                  approved_core_remaining=35, approved_existing_definitions=4, approved_design_only=31,
                  conditional_remaining_if_all_accepted=31, conditional_existing_definitions=4,
                  conditional_design_only=27, intake_predecessor=272, runtime_installed=False,
                  selected_constellation_version='v2', candidates=[dict(item_id=r['item_id'], display_name=r['display_name'],
                           definition_state=r['definition_state'], planned_footprint=[1, 3],
                           game_path=r['game_path'], game_sha256=r['game_sha256'], source_sha256=r['source_sha256'])
                           for r in manifest['items']])
    (GAME / 'art/item_catalog_274/candidate_487_2026-09-28.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('DOCS #487 planned art4/JPG6/conditional ledger; approved remaining35 unchanged; no runtime definitions')


if __name__ == '__main__':
    main()
