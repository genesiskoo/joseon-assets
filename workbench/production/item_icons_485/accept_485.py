"""Freeze PD-approved artwork hashes without installing runtime icons."""
from pathlib import Path
import json
from prepare_485 import sha

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    verification = json.loads((ROOT / 'verification.json').read_text(encoding='utf-8'))
    assert manifest['card'] == 485 and len(manifest['items']) == 4
    assert verification['runtime_files_byte_match'] == 154
    rows = []
    for row in manifest['items']:
        assert sha(ROOT / row['game_path']) == row['game_sha256']
        assert sha(ROOT / row['source_path']) == row['source_sha256']
        rows.append('| ' + row['display_name'] + ' | ' + row['game_path'] + ' | ' + row['game_sha256'] + ' |')
    text = '''# #485 PD 채택 기록 (2026-09-28)

PD의 「승인 다음」으로 쇠 먹는 이빨·축지 짚신·선녀 날개옷·사인참사검 원화4종을 모두 채택했다. 최초 후보 자산 커밋은378b579, 게임 사양/검토판은278d7ceb이다. 원본4/정확한 프롬프트/공통 패킹/실제 UiSkin4모드/raw/해시를 보존한다. 현재 후보 manifest의 candidate_not_installed는 제작 당시의 상태이며 채택 판정은 이 문서가 기록한다.

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
''' + '\n'.join(rows) + '''

검수: 장검1×3/80×240·짚신2×2/160×160·비단도포2×3/160×240·사인검1×3/80×240 RGBA. 실제Godot4.7.2 UiSkin4모드/오류0·JPG5/각300KB미만, UniqueDef/베이스 계약·원본/후보/참조SHA 확인. 날개옷 주변 RGB는알파0이며 실제검정칸 후광없음. 기존게임PNG42/H1PNG19·정의/UI154파일을 보존했다. 30px에서 미세문양은 약해지는 한계를 QA.md에 기록했다.

#274 최초핵심73에서 승인핵심38을 빼면 잔여35. T3베이스9·상위물약4·호리병1·대표유니크1·오방옥20이며 현재정의4/설계31이다. 추가 승인6·퀘스트봉인3은 원핵심 밖 별도 집계다. 실제 게임 반입은 #484 전용유니크그림 선택 선행 뒤 별도카드이며 이 원화 채택은 게임 설치 완료가 아니다. 기존 검·물약 후속 폴리싱은 지금 진행하지 않는다.
'''
    (ROOT / 'ACCEPTANCE.md').write_text(text, encoding='utf-8', newline='\n')
    print('ACCEPT #485 unique4 SHA preserved; original core remaining39 -> 35; runtime not installed')


if __name__ == '__main__':
    main()
