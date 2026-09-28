"""Archive the first fixture render rejected by visual inspection."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parents[2] / 'reports/487/2026-09-28'


def main():
    dest = ROOT / 'variants/qa_path_collision'
    assert not dest.exists(), 'Do not overwrite rejected fixture evidence'
    for rel in ['verification.json', 'qa_godot.gd']:
        path = dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, path)
    for mode in ['forty', 'sizes', 'black_sizes', 'base_compare', 'constellation_pair']:
        for suffix in ['png', 'jpg']:
            path = dest / 'qa' / f'godot_{mode}.{suffix}'
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / 'qa' / path.name, path)
        for stream in ['stdout', 'stderr']:
            path = dest / 'logs' / f'godot_{mode}_{stream}.txt'
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPORT / path.name, path)
    text = '''# #487 검수도구 첫 렌더: 최종 결과 아님

자동 렌더/계약 검사는 PASS였으나 직접 검수에서 첫 운검이 짧게 찌그러지는 문제를 발견했다. 같은 배치 운검을 운룡검 비교로 다시 ImageTexture.take_over_path 호출하며 기존 운검 후보의 resource_path가 지워졌다. UiSkin이 작은 공용그림 fallback을 사용한 검수도구 문제다. 원화나 게임런타임을 수정하지 않고 같은 배치 비교는 기존후보 Texture2D를 공유한다. 재렌더 전 모든 후보/참조의 art resource_path를 검사한다. 첫 검수의 PNG/JPG/raw/script/verification를 여기 보존하고 현재 qa/verification를 최종 결과로 재작성한다.
'''
    (dest / 'REJECTED.md').write_text(text, encoding='utf-8', newline='\n')
    print('ARCHIVED #487 visual-rejected path-collision fixture; artwork/native bytes unchanged')


if __name__ == '__main__':
    main()
