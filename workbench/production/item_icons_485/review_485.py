"""Validate original/contract hashes, unchanged runtime and actual UiSkin logs."""
from pathlib import Path
import json
import shutil
from PIL import Image
from prepare_485 import GAME, runtime_files, sha

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parents[2] / 'reports/485/2026-09-28'
GALLERY = GAME / 'docs/art/485_d1_unique_equipment'


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT / 'generation_sources.json').read_text(encoding='utf-8'))
    before = json.loads((ROOT / 'runtime_before.json').read_text(encoding='utf-8'))
    assert len(manifest['items']) == len(sources['items']) == 4
    for row, gen in zip(manifest['items'], sources['items']):
        assert row['item_id'] == gen['id']
        assert sha(ROOT / row['source_path']) == row['source_sha256'] == sha(Path(gen['native_path']))
        assert sha(ROOT / row['game_path']) == row['game_sha256']
        image = Image.open(ROOT / row['game_path'])
        assert image.mode == 'RGBA' and image.size == (row['grid_w'] * 80, row['grid_h'] * 80)
        alpha = image.getchannel('A').getextrema()
        assert list(alpha) == row['game_alpha'] and alpha[0] == 0 and alpha[1] >= 250
        assert list(image.getchannel('A').getbbox()) == row['visible_bbox']
        for field in ['definition', 'base_definition', 'base_reference']:
            assert sha(Path(row[field + '_path'])) == row[field + '_sha256']
    robe_probe = json.loads((ROOT / 'robe_alpha_probe.json').read_text(encoding='utf-8'))
    assert all(sample['rgba'][3] == 0 for sample in robe_probe[:8])
    assert robe_probe[-1]['rgba'][3] >= 250
    after = {p.relative_to(GAME).as_posix(): sha(p) for p in runtime_files()}
    assert before == after, [k for k in before if before[k] != after.get(k)]
    current_png = sum(k.startswith('assets/sprites/ui/icons_a/') and k.endswith('.png') for k in after)
    legacy_png = sum(k.startswith('assets/sprites/ui/icons_h1/') and k.endswith('.png') for k in after)
    assert current_png == 42 and legacy_png == 19 and len(before) == 154
    REPORT.mkdir(parents=True, exist_ok=True)
    GALLERY.mkdir(parents=True, exist_ok=True)
    names = ['overview.jpg']
    logs = []
    for mode in ['forty', 'sizes', 'black_sizes', 'base_compare']:
        stdout = REPORT / f'godot_{mode}_stdout.txt'
        stderr = REPORT / f'godot_{mode}_stderr.txt'
        raw = stdout.read_text(encoding='utf-8-sig') + '\n' + stderr.read_text(encoding='utf-8-sig')
        assert f'GODOT_D1_485_PASS mode={mode} items=4' in raw
        assert 'SCRIPT ERROR' not in raw and 'ERROR:' not in raw
        logs.append(dict(mode=mode, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
        p = ROOT / 'qa' / f'godot_{mode}.png'
        im = Image.open(p)
        assert im.size == (1280, 760)
        shutil.copyfile(p, REPORT / p.name)
        jpg = p.with_suffix('.jpg')
        im.convert('RGB').save(jpg, quality=86, optimize=True)
        names.append(jpg.name)
    assert len(names) <= 6
    shutil.copyfile(ROOT / 'qa/overview.png', REPORT / 'overview.png')
    gallery = []
    for name in names:
        src = ROOT / 'qa' / name
        assert src.stat().st_size < 300000
        shutil.copyfile(src, REPORT / name)
        shutil.copyfile(src, GALLERY / name)
        gallery.append(dict(filename=name, bytes=src.stat().st_size, sha256=sha(src)))
    result = dict(card=485, status='candidate_not_installed', binding_status='unique_icon_path_not_implemented',
                  items=4, existing_game_png=current_png, preserved_h1_png=legacy_png,
                  runtime_files_byte_match=len(before), unique_and_base_definition_hashes_match=True,
                  original_hashes_preserved=True, robe_outer_rgb_matte_alpha_zero=True,
                  godot_ui_skin_modes=logs, gallery=gallery)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    (ROOT / 'verification.json').write_text(text, encoding='utf-8', newline='\n')
    (REPORT / 'verification.json').write_text(text, encoding='utf-8', newline='\n')
    print('PASS #485: unique4 RGBA footprints1x3/2x2/2x3/1x3, native SHA preserved, runtime154+PNG42/H1PNG19 byte-preserved, actual UiSkin4modes/error0, JPG5')


if __name__ == '__main__':
    main()
