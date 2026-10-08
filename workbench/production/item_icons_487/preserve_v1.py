"""Keep pre-edit constellation source/packing/contact evidence unchanged."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent


def main():
    dest = ROOT / 'variants/v1'
    assert not (dest / 'manifest.json').exists(), 'Do not overwrite initial evidence'
    for rel in ['manifest.json', 'generation_sources.json', 'PROMPTS.md',
                'game/items/chilseonggeom.png', 'qa/overview.png', 'qa/overview.jpg']:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    (dest / 'NOTE.md').write_text('# #487 최초 생성 칠성검\n\n원화의 금속점8개를 확인해 7점 보강 전 원본/정확한프롬프트/패킹/검토판을 보존했다. 최종선택이 아니다. native/source/items/chilseonggeom.png는 변경하지 않는다.\n', encoding='utf-8', newline='\n')
    print('PRESERVED #487 v1 constellation8 source/prompt/packing/contact; not selected')


if __name__ == '__main__':
    main()
