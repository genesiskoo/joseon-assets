"""Freeze PD-approved armor hashes while retaining the candidate history."""
from pathlib import Path
import json
from prepare_491 import sha

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    verification = json.loads((ROOT / 'verification.json').read_text(encoding='utf-8'))
    assert manifest['card'] == 491 and len(manifest['items']) == 3
    assert verification['runtime_files_byte_match'] == 154
    assert verification['fixture_resource_paths_validated']
    assert verification['original_hashes_preserved']
    assert verification['approved_T2_reference_hashes_preserved']
    assert len(verification['godot_ui_skin_modes']) == 5
    rows = []
    for row in manifest['items']:
        assert sha(ROOT / row['game_path']) == row['game_sha256']
        assert sha(ROOT / row['source_path']) == row['source_sha256']
        rows.append('| ' + row['display_name'] + ' | ' + row['game_path'] + ' | ' + row['game_sha256'] + ' |')
    text = '''# #491 PD 채택 기록 (2026-09-29)

PD 「승인 다음」으로 엄심갑·수은갑·심의 원화3종을 모두 채택했다. 최초 후보 자산4e55cc6b·게임사양/검토판1b374645. native3/정확한프롬프트/공통패킹/실제UiSkin5모드/raw/해시를 보존한다. manifest·verification·candidate 목록의 미채택 표시는 제작 당시 이력이며 현재 판정은 이 기록과 게임 approval_491 원장에 둔다.

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
''' + '\n'.join(rows) + '''

모두 예정T3/ARMOR/2×3/160×240 RGBA이며 실제 ItemDef는 아직 없다. native3는1024×1536 RGBA/알파0~254이고 최고알파를 강제보정하지 않았다. 엄심갑은 호심경과 빈 끈, 수은갑은 은빛 철판과 쪽빛 안감, 심의는 흰 비단·검은 가장자리·흰 허리끈·정돈 주름으로 검수했다. 수은 처리 실물 고증을 주장하지 않는다. 30px에서 미세 문양이 약해지는 한계와 최초 알파 조건/검수 도구 자료형 실패 raw를 보존했다. 최종5모드 오류0·후보/참조 resource_path·원본/후보/승인T2 SHA·JPG6/각300KB미만·기존PNG42/H1PNG19·정의/UI154파일 불변을 확인했다.

#274 최초핵심73 중 승인핵심45, 잔여28=T3장신구3·상위물약4·호리병1·오방옥20(현정의4/설계24). 핵심밖 추가승인6·퀘스트봉인3은 별도다. 실제 게임반입은 #272 데이터 뒤 최종정의/점유 재대조를 거치는 별도카드이며, 이 원화 병합으로 게임설치나 2회차 구현 완료를 세지 않는다. 기존 검·물약 폴리싱은 후속기조를 유지한다.
'''
    (ROOT / 'ACCEPTANCE.md').write_text(text, encoding='utf-8', newline='\n')
    print('ACCEPT #491 planned armor3 SHA preserved; core31 -> 28; no runtime intake')


if __name__ == '__main__':
    main()
