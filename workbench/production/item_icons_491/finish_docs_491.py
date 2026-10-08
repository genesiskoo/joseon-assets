"""Record review-only images and a conditional candidate ledger without intake."""
from pathlib import Path
import json
from collections import Counter
from prepare_491 import GAME

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    verified = json.loads((ROOT / 'verification.json').read_text(encoding='utf-8'))
    previous = json.loads((GAME / 'art/item_catalog_274/remaining_after_487_2026-09-28.json').read_text(encoding='utf-8'))
    assert previous['remaining_core'] == 31 and len(manifest['items']) == 3
    keys = {r['item_id'] for r in manifest['items']}
    pending = [r for r in previous['entries'] if r['production_key'] not in keys]
    assert len(pending) == 28 and Counter(r['definition_state'] for r in pending) == Counter(implemented=4, design_only=24)
    ledger = dict(card=491, parent_card=274, date='2026-09-28', status='candidate_pending_pd',
                  basis='approval_487_2026-09-28.json and remaining_after_487_2026-09-28.json',
                  approved_core_remaining=31, approved_existing_definitions=4, approved_design_only=27,
                  conditional_remaining_if_all_accepted=28, conditional_existing_definitions=4,
                  conditional_design_only=24, intake_predecessor=272, runtime_installed=False,
                  candidates=[{k: r[k] for k in ['item_id', 'display_name', 'definition_state', 'game_path',
                               'game_sha256', 'source_sha256', 'reference_id', 'reference_status']} |
                               {'planned_footprint': [2, 3]} for r in manifest['items']])
    target = GAME / 'art/item_catalog_274/candidate_491_2026-09-28.json'
    target.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    readme = '''# #491 T3 갑·포3 검토판

엄심갑 / 수은갑 / 심의. 사양기반 신규원화 후보이며 아직미채택·미게임반입이다. 모두예정T3/ARMOR/2×3/160×240 RGBA이며 실제ItemDef는없다. 게임반입은 #272 뒤 최종정의/점유를다시대조한다. 현재승인잔여31 유지, 이번3 전부채택시28/현정의4·설계24.

- overview.jpg: native3 / #464 채택 T2 비교 / 40px / 무채색.
- godot_forty.jpg: 실제UiSkin 가방40px·검정40px·좌판48px칸.
- godot_sizes.jpg: 실제UiSkin 30/48/60px칸.
- godot_black_sizes.jpg: 실제검정 30/48/60px칸.
- godot_base_compare.jpg: 같은UiSkin에서 #464 승인 경번갑·두정갑·학창의와비교. 이 T2 비교그림도 아직미게임반입이다.
- godot_grayscale.jpg: 실제UiSkin 무채색30/48/60px칸. 색보다형태와명암으로구별하는지본다.

5모드 PASS/오류0·후보/참조경로 검사·JPG6/폭1280/각300KB미만. 엄심갑은호심경과빈끈만으로전신갑옷이아니며중앙위빈공간알파0, 수은갑은가공세계의명칭으로수은처리실물고증을주장하지않는다. 심의는흰비단·검은가장자리·흰허리끈·정돈주름으로검수했다. native3는1024×1536 RGBA/알파0~254이며원본불변, 최고알파를255로강제보정하지않았다. 30px에서는미세새김/직물문양이약해지고40px에서주요재질/형태를읽는다.

최초알파검사조건과GDScript자료형검수실패의raw를자산reports/491에보존했다. 최종5모드는수정한검수도구의재실행결과이며그림/게임UiSkin은이문제로변경하지않았다. 기존PNG42/H1PNG19·정의/관련UI154파일SHA동일. 원본/정확프롬프트/manifest/QA/verification은자산codex/491-d1-t3-armor의workbench/production/item_icons_491, raw/PNG는reports/491/2026-09-28. 왜이구조인지는ui_v2.md와BRIEF.md에기록했다.
'''
    (GAME / 'docs/art/491_d1_t3_armor/README.md').write_text(readme, encoding='utf-8', newline='\n')
    doc = GAME / 'docs/design/ui_v2.md'
    text = doc.read_text(encoding='utf-8')
    final = '''
### #491 후보 검수 기록 (2026-09-28)

신규native3는1024×1536 RGBA/알파0~254이며원본/정확프롬프트/SHA를그대로보존했다. 예정160×240/2×3로공통패킹하고실제UiSkin5모드(가방/검정40·좌판48,30·48·60,검정크기,T2대조,무채색)오류0·후보/참조resource_path·승인T2 SHA3·기존PNG42/H1PNG19·정의/UI154파일불변을확인했다. 엄심갑빈끈공간의알파0·수은갑은빛철판/쪽빛안감·심의흰비단/검은가장자리/흰허리끈/정돈주름을직접검수했다. 최초알파검사조건/검수스크립트자료형실패raw는자산reports491에기각본으로보존하고최종5모드를재실행했다. 30px에서미세문양이약해지는한계는QA에기록한다. 후보원장candidate_491_2026-09-28.json은조건부31→28이며아직실제게임반입/정의생성/승인차감은없다. JPG6장은docs/art/491_d1_t3_armor, 원본/raw는자산workbench/production/item_icons_491·reports/491/2026-09-28이다.
'''
    log_doc = GAME / 'docs/design/ui_v2_log.md'
    log_text = log_doc.read_text(encoding='utf-8') if log_doc.exists() else '# UI v2 검수·판정 기록\n'
    if '### #491 후보 검수 기록' not in log_text:
        log_doc.write_text(log_text.rstrip() + '\n' + final, encoding='utf-8', newline='\n')
    assert verified['runtime_files_byte_match'] == 154
    print('DOCS #491 planned armor3/JPG6/conditional31 -> 28 ledger; approved remaining31 unchanged; no runtime intake')


if __name__ == '__main__':
    main()
