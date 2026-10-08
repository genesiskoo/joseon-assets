"""Keep the new contract in the spec and the inspection record in its log."""
from prepare_491 import GAME


def main():
    doc = GAME / 'docs/design/ui_v2.md'
    text = doc.read_text(encoding='utf-8')
    marker = '## #491 D1 T3 갑·포3 원화 후보 계약'
    start = text.index(marker)
    record_marker = '### #491 후보 검수 기록'
    record_start = text.index(record_marker, start)
    record = text[record_start:].strip()
    assert record.count('\n### ') == 0 and record.count('\n## ') == 0
    log_doc = GAME / 'docs/design/ui_v2_log.md'
    log_text = log_doc.read_text(encoding='utf-8') if log_doc.exists() else '# UI v2 검수·판정 기록\n'
    if record_marker not in log_text:
        log_doc.write_text(log_text.rstrip() + '\n\n' + record + '\n', encoding='utf-8', newline='\n')
    contract = '''## #491 D1 T3 갑·포3 원화 후보 계약 (2026-09-28)

엄심갑(eomsimgap)·수은갑(sueungap)·심의(geuksang_dopo)는 item_catalog_v2 §1.2·§1.3 / item_system_v2 §4.3의 예정T3/ARMOR/2×3/160×240 RGBA다. 엄심갑=심장만덮는호심경/빈지지끈, 수은갑=은빛철판/쪽빛안감/윤나는가공세계갑옷(실물고증주장없음), 심의=흰예복/검은가장자리/정돈주름. 내장imagegen→native/프롬프트/SHA보존→알파16/8%여백/Lanczos비율패킹→실제UiSkin40·48/30·48·60/검정/승인T2대조/무채색검수. #464 비교T2도미게임반입이다. 실제ItemDef는없고반입은#272뒤최종정의/점유재대조·별도카드. PNG42/H1PNG19·정의/UI·수치/세이브/3D보존, 채택전잔여31/전부채택시28. 세부사양=자산BRIEF.md, JPG6=docs/art/491_d1_t3_armor, 검수이력=ui_v2_log.md §491.

왜 이 구조인가: 사양원화와공용UiSkin검수로데이터작업을기다리며제작을진행한다. 임시정의/기존T2교체는비대상데이터와표시를바꾸므로기각한다.
'''
    doc.write_text(text[:start].rstrip() + '\n\n' + contract, encoding='utf-8', newline='\n')
    print('COMPACT #491: contract in ui_v2; final inspection in ui_v2_log; earlier content preserved')


if __name__ == '__main__':
    main()
