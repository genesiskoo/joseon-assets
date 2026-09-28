"""Verify native/v1 hashes, planned contracts, runtime preservation and UiSkin logs."""
from pathlib import Path
import argparse
import json
import shutil
from PIL import Image
from prepare_487 import GAME, runtime_files, sha

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parents[2] / 'reports/487/2026-09-28'
GALLERY = GAME / 'docs/art/487_d1_t3_swords'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--defer-game-gallery', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT / 'generation_sources.json').read_text(encoding='utf-8'))
    before = json.loads((ROOT / 'runtime_before.json').read_text(encoding='utf-8'))
    assert len(manifest['items']) == len(sources['items']) == 4
    assert manifest['definition_state'] == 'design_only'
    for row, gen in zip(manifest['items'], sources['items']):
        assert row['item_id'] == gen['id']
        assert sha(ROOT / row['source_path']) == row['source_sha256'] == sha(Path(gen['native_path']))
        assert sha(ROOT / row['game_path']) == row['game_sha256']
        image = Image.open(ROOT / row['game_path'])
        assert image.mode == 'RGBA' and image.size == (80, 240)
        assert list(image.getchannel('A').getextrema()) == row['game_alpha']
        assert list(image.getchannel('A').getbbox()) == row['visible_bbox']
        assert row['grid_w'] == 1 and row['grid_h'] == 3
        assert not Path(row['planned_definition_path']).exists()
        assert sha(Path(row['reference_path'])) == row['reference_sha256']
    for rel, expected in manifest['source_docs'].items():
        assert sha(GAME / rel) == expected
    old_manifest = json.loads((ROOT / 'variants/v1/manifest.json').read_text(encoding='utf-8'))
    old_sources = json.loads((ROOT / 'variants/v1/generation_sources.json').read_text(encoding='utf-8'))
    old_row = old_manifest['items'][2]
    old_gen = old_sources['items'][2]
    assert old_row['item_id'] == old_gen['id'] == 'chilseonggeom'
    assert sha(ROOT / old_row['source_path']) == old_row['source_sha256'] == sha(Path(old_gen['native_path']))
    assert sha(ROOT / 'variants/v1/game/items/chilseonggeom.png') == old_row['game_sha256']
    assert manifest['items'][2]['source_path'].endswith('_v2.png')
    ring = Image.open(ROOT / manifest['items'][1]['source_path'])
    hole_point = (360, 105)
    hole_rgba = ring.getpixel(hole_point)
    assert hole_rgba[3] == 0
    manual = json.loads((ROOT / 'visual_checks.json').read_text(encoding='utf-8'))
    assert manual['chilseonggeom_v1_blade_gold_dots'] == 8
    assert manual['chilseonggeom_v2_blade_gold_dots'] == 7
    assert manual['v2_dots_handle'] == 3 and manual['v2_dots_bowl'] == 4
    after = {p.relative_to(GAME).as_posix(): sha(p) for p in runtime_files()}
    assert before == after, [k for k in before if before[k] != after.get(k)]
    current_png = sum(k.startswith('assets/sprites/ui/icons_a/') and k.endswith('.png') for k in after)
    legacy_png = sum(k.startswith('assets/sprites/ui/icons_h1/') and k.endswith('.png') for k in after)
    assert current_png == 42 and legacy_png == 19 and len(after) == 154
    REPORT.mkdir(parents=True, exist_ok=True)
    if not args.defer_game_gallery:
        GALLERY.mkdir(parents=True, exist_ok=True)
    names = ['overview.jpg']
    logs = []
    for mode in ['forty', 'sizes', 'black_sizes', 'base_compare', 'constellation_pair']:
        stdout = REPORT / f'godot_{mode}_stdout.txt'
        stderr = REPORT / f'godot_{mode}_stderr.txt'
        raw = stdout.read_text(encoding='utf-8-sig') + '\n' + stderr.read_text(encoding='utf-8-sig')
        assert f'GODOT_D1_487_PASS mode={mode} items=4' in raw
        assert 'currentT2references/resource_paths/render validated' in raw
        assert 'SCRIPT ERROR' not in raw and 'ERROR:' not in raw
        logs.append(dict(mode=mode, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
        p = ROOT / 'qa' / f'godot_{mode}.png'
        im = Image.open(p)
        assert im.size == (1280, 760)
        jpg = p.with_suffix('.jpg')
        im.convert('RGB').save(jpg, quality=86, optimize=True)
        names.append(jpg.name)
        shutil.copyfile(p, REPORT / p.name)
    assert len(names) == 6
    shutil.copyfile(ROOT / 'qa/overview.png', REPORT / 'overview.png')
    gallery = []
    for name in names:
        src = ROOT / 'qa' / name
        assert src.stat().st_size < 300000
        shutil.copyfile(src, REPORT / name)
        if not args.defer_game_gallery:
            shutil.copyfile(src, GALLERY / name)
        gallery.append(dict(filename=name, bytes=src.stat().st_size, sha256=sha(src)))
    result = dict(card=487, status='candidate_not_installed', definition_state='design_only', intake_predecessor=272,
                  items=4, planned_footprints='1x3 x4; no T3 runtime definitions',
                  existing_game_png=current_png, preserved_h1_png=legacy_png, runtime_files_byte_match=len(after),
                  original_hashes_preserved=True, v1_source_prompt_packing_preserved=True,
                  fixture_resource_paths_validated=True, rejected_path_collision_fixture_preserved=True,
                  selected_constellation_version='v2', manual_visual_checks=manual,
                  ring_hole_sample=dict(point=list(hole_point), rgba=list(hole_rgba)),
                  godot_ui_skin_modes=logs, gallery=gallery)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    (ROOT / 'verification.json').write_text(text, encoding='utf-8', newline='\n')
    (REPORT / 'verification.json').write_text(text, encoding='utf-8', newline='\n')
    print('PASS #487: planned swords4 RGBA80x240/1x3, native4+edit1/v1 SHA preserved, seven dots manual3+4/ring hole alpha0, runtime154/PNG42+H1PNG19 byte-preserved, actual UiSkin5modes/error0, JPG6')


if __name__ == '__main__':
    main()
