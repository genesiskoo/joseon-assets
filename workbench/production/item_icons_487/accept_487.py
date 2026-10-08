"""Freeze the approved art hashes without inventing T3 item definitions."""
from pathlib import Path
import json
from prepare_487 import sha

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    verification = json.loads((ROOT / 'verification.json').read_text(encoding='utf-8'))
    assert manifest['card'] == 487 and len(manifest['items']) == 4
    assert verification['runtime_files_byte_match'] == 154
    assert verification['selected_constellation_version'] == 'v2'
    assert verification['fixture_resource_paths_validated']
    assert verification['manual_visual_checks']['chilseonggeom_v2_blade_gold_dots'] == 7
    rows = []
    for row in manifest['items']:
        assert sha(ROOT / row['game_path']) == row['game_sha256']
        assert sha(ROOT / row['source_path']) == row['source_sha256']
        rows.append('| ' + row['display_name'] + ' | ' + row['game_path'] + ' | ' + row['game_sha256'] + ' |')
    text = '''# #487 PD 채택 기록 (2026-09-28)

PD 「승인 다음」으로 운검·환두대도·칠성검v2·운룡검 원화4종을 모두 채택했다. 최초 후보 자산6ec8e254·게임사양/검토판c97e7fdb. 원본4+칠성정밀편집1/정확한프롬프트/공통패킹/실제UiSkin5모드/raw/해시를 보존한다. manifest·verification·candidate 목록의 미채택 표시는 제작 당시 이력이며 채택 판정은 이 기록과 게임 approval_487 원장에 둔다.

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
''' + '\n'.join(rows) + '''

모두 예정1×3/80×240 RGBA이며 실제 T3 ItemDef/UniqueDef는 아직 없다. 칠성검은 선택된 v2의 3+4=7점이고 원안8점/프롬프트/패킹을 보존했다. 실제UiSkin5모드/오류0·후보/참조 resource_path 확인·JPG6/각300KB미만, 원본/후보SHA·고리 내부 알파0·기존PNG42/H1PNG19·정의/UI154파일 보존을 검사했다. 검수 도구의 첫 경로 충돌 렌더도 variants/qa_path_collision에 기각본으로 남겨 원화 변경과 구별한다.

#274 최초핵심73 중 승인핵심42, 잔여31=T3베이스6·상위물약4·호리병1·오방옥20(현정의4/설계27). 핵심밖 추가승인6·퀘스트봉인3은 별도 집계다. 게임반입은 #272 데이터와 #484 유니크 전용그림 해석 경로 뒤 최종정의/점유를 재대조하는 별도카드다. 승인원화 병합은 실제 게임설치 완료가 아니다. 기존 칼·물약 폴리싱과 새로운 데이터/2회차 기능은 이번에 변경하지 않았다.
'''
    (ROOT / 'ACCEPTANCE.md').write_text(text, encoding='utf-8', newline='\n')
    print('ACCEPT #487 planned sword4/final v2 SHA preserved; core35 -> 31; no runtime intake')


if __name__ == '__main__':
    main()
