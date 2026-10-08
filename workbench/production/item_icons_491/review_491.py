"""Verify alpha, native and T2 hashes, planned contracts, runtime and Godot plates."""
from pathlib import Path
import argparse
import json
import shutil
from PIL import Image
from prepare_491 import GAME, runtime_files, sha

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parents[2] / 'reports/491/2026-09-28'
GALLERY = GAME / 'docs/art/491_d1_t3_armor'
MODES = ['forty', 'sizes', 'black_sizes', 'base_compare', 'grayscale']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--defer-game-gallery', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT / 'generation_sources.json').read_text(encoding='utf-8'))
    before = json.loads((ROOT / 'runtime_before.json').read_text(encoding='utf-8'))
    assert len(manifest['items']) == len(sources['items']) == 3
    assert manifest['definition_state'] == 'design_only'
    for row, gen in zip(manifest['items'], sources['items']):
        assert row['item_id'] == gen['id']
        assert sha(ROOT / row['source_path']) == row['source_sha256'] == sha(Path(gen['native_path']))
        assert sha(ROOT / row['game_path']) == row['game_sha256']
        native = Image.open(ROOT / row['source_path'])
        assert native.mode == 'RGBA' and native.size == (1024, 1536)
        assert native.getchannel('A').getextrema() == (0, 254)
        assert native.getpixel((0, 0))[3] == 0
        image = Image.open(ROOT / row['game_path'])
        assert image.mode == 'RGBA' and image.size == (160, 240)
        assert list(image.getchannel('A').getextrema()) == row['game_alpha']
        assert image.getchannel('A').getextrema()[0] == 0 and image.getchannel('A').getextrema()[1] >= 250
        assert list(image.getchannel('A').getbbox()) == row['visible_bbox']
        assert row['grid_w'] == 2 and row['grid_h'] == 3
        assert not Path(row['planned_definition_path']).exists()
        assert sha(Path(row['reference_path'])) == row['reference_sha256']
        assert row['reference_status'] == 'PD_approved_T2_art_464_not_installed'
    for rel, expected in manifest['source_docs'].items():
        assert sha(GAME / rel) == expected
    harness = Image.open(ROOT / 'source/items/eomsimgap.png')
    hole_rgba = harness.getpixel((512, 150))
    assert hole_rgba[3] == 0
    after = {p.relative_to(GAME).as_posix(): sha(p) for p in runtime_files()}
    assert before == after, [k for k in before if before[k] != after.get(k)]
    current_png = sum(k.startswith('assets/sprites/ui/icons_a/') and k.endswith('.png') for k in after)
    legacy_png = sum(k.startswith('assets/sprites/ui/icons_h1/') and k.endswith('.png') for k in after)
    assert current_png == 42 and legacy_png == 19
    REPORT.mkdir(parents=True, exist_ok=True)
    if not args.defer_game_gallery:
        GALLERY.mkdir(parents=True, exist_ok=True)
    logs = []
    names = ['overview.jpg']
    for mode in MODES:
        stdout = REPORT / f'godot_{mode}_stdout.txt'
        stderr = REPORT / f'godot_{mode}_stderr.txt'
        raw = stdout.read_text(encoding='utf-8-sig') + '\n' + stderr.read_text(encoding='utf-8-sig')
        assert f'GODOT_D1_491_PASS mode={mode} items=3' in raw
        assert 'approvedT2references/resource_paths/render validated' in raw
        assert 'SCRIPT ERROR' not in raw and 'ERROR:' not in raw and stderr.stat().st_size == 0
        logs.append(dict(mode=mode, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
        png = ROOT / 'qa' / f'godot_{mode}.png'
        im = Image.open(png)
        assert im.size == (1280, 760)
        jpg = png.with_suffix('.jpg')
        im.convert('RGB').save(jpg, quality=86, optimize=True)
        names.append(jpg.name)
        shutil.copyfile(png, REPORT / png.name)
    assert len(names) == 6
    shutil.copyfile(ROOT / 'qa/overview.png', REPORT / 'overview.png')
    gallery = []
    for name in names:
        src = ROOT / 'qa' / name
        assert Image.open(src).width == 1280 and src.stat().st_size < 300000
        shutil.copyfile(src, REPORT / name)
        if not args.defer_game_gallery:
            shutil.copyfile(src, GALLERY / name)
        gallery.append(dict(filename=name, bytes=src.stat().st_size, sha256=sha(src)))
    assert (REPORT / 'packing_initial_stderr.txt').exists()
    assert (REPORT / 'initial_qa_parse/qa_godot.gd').exists()
    checks = dict(card=491, status='candidate_not_installed', definition_state='design_only',
                  intake_predecessor=272, items=3, planned_footprints='2x3 x3; no T3 runtime definitions',
                  existing_game_png=current_png, preserved_h1_png=legacy_png,
                  runtime_files_byte_match=len(after), original_hashes_preserved=True,
                  approved_T2_reference_hashes_preserved=True, fixture_resource_paths_validated=True,
                  native_alpha=[0, 254], native_opacity_not_normalized=True,
                  harness_hole_sample=dict(point=[512, 150], rgba=list(hole_rgba)),
                  manual_visual_checks=dict(method='manual inspection of native3 and actual UiSkin plates',
                    eomsimgap_heart_plate_without_full_coat=True, sueungap_metal_planes_navy_lining=True,
                    simui_white_black_pleats_white_sash=True, no_person_text_logo_or_external_aura=True,
                    no_assertion_of_historical_mercury_treatment=True),
                  initial_fixture_failures_preserved=True, godot_ui_skin_modes=logs, gallery=gallery)
    for target in [ROOT / 'verification.json', REPORT / 'verification.json']:
        target.write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'PASS #491: planned armor3 RGBA160x240/2x3; native3 alpha0..254/SHA preserved; T2 SHA3; runtime{len(after)}/PNG42+H1PNG19 byte-preserved; actual UiSkin5 modes/error0; JPG6')


if __name__ == '__main__':
    main()
