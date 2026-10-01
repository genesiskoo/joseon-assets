"""Verify preserved Comfy sources, real definitions, runtime bytes and rendered plates."""
from pathlib import Path
import argparse
import json
import shutil

import numpy as np
from PIL import Image

from prepare_534 import DEFAULT_GAME, REPORT, REPO, ROOT, sha, snapshot, write_json

MODES = ['overview', 'actual', 'belt_stress', 'black', 'grayscale']


def jpeg(source, destination):
    image = Image.open(source).convert('RGB')
    assert image.width == 1280
    for quality in [86, 82, 78, 74, 70]:
        image.save(destination, quality=quality, optimize=True)
        if destination.stat().st_size <= 300000:
            return
    raise AssertionError(f'Gallery JPEG exceeds 300 KB: {destination}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=Path, default=DEFAULT_GAME)
    parser.add_argument('--defer-game-gallery', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    before = json.loads((ROOT / 'runtime_before.json').read_text(encoding='utf-8'))
    assert manifest['card'] == 534 and len(manifest['items']) == 4 and len(manifest['references']) == 2
    assert manifest['definition_state'] == 'existing' and manifest['status'] == 'candidate_not_installed'
    assert not manifest['manual_pixel_editing'] and not manifest['manual_alpha_editing']
    assert not manifest['production_alpha_thresholding']
    alpha = []
    for row in manifest['items']:
        native_path, clean_path, game_path = [ROOT / row[key] for key in ['generated_path', 'source_path', 'game_path']]
        assert sha(native_path) == row['generated_sha256'] and sha(clean_path) == row['source_sha256']
        if 'generated_receipt_path' in row:
            assert sha(REPO / row['generated_receipt_path']) == row['generated_sha256']
            assert sha(REPO / row['clean_receipt_path']) == row['source_sha256']
        assert sha(game_path) == row['game_sha256']
        native, clean, packed = [Image.open(path) for path in [native_path, clean_path, game_path]]
        assert native.mode == clean.mode == packed.mode == 'RGBA'
        assert native.size == clean.size == (1024, 1024) and packed.size == (80, 80)
        a, b = np.asarray(native), np.asarray(clean)
        assert np.array_equal(a[:, :, :3], b[:, :, :3]), 'BiRefNet must not redraw the bottle'
        assert np.count_nonzero(a[:, :, 3] != b[:, :, 3]) > 0
        assert clean.getchannel('A').getextrema() == packed.getchannel('A').getextrema() == (0, 255)
        assert list(packed.getchannel('A').getbbox()) == row['visible_bbox']
        assert row['packing_padding_px'] == 6
        assert min(row['visible_bbox'][:2]) >= 6 and max(row['visible_bbox'][2:]) <= 74
        assert row['tier'] == 1 and row['slot'] == 6 and row['max_stack'] == 10
        assert row['grid_w'] == row['grid_h'] == 1 and row['efficacy_stage'] in [2, 3]
        definition = args.game / f"data/items/{row['item_id']}.tres"
        assert sha(definition) == row['definition_sha256']
        alpha.append(dict(id=row['item_id'], rgb_max_delta=0, rgb_pixels_changed=0,
                          alpha_pixels_changed=int(np.count_nonzero(a[:, :, 3] != b[:, :, 3])),
                          source_sha256=sha(clean_path), generated_sha256=sha(native_path),
                          game_sha256=sha(game_path), clean_alpha=[0, 255], packed_alpha=[0, 255],
                          source_bbox=row['source_stats']['bbox'], game_bbox=row['visible_bbox']))
    for ref in manifest['references']:
        assert sha(ROOT / ref['source_path']) == ref['source_sha256']
        current = args.game / f"assets/sprites/ui/icons_a/items/{ref['resource']}_potion.png"
        assert sha(current) == sha(ROOT / ref['runtime_snapshot_path']) == ref['runtime_sha256']
        assert sha(args.game / f"data/items/{ref['item_id']}.tres") == ref['definition_sha256']
    for rel, expected in manifest['source_docs'].items():
        assert sha(args.game / rel) == expected
    after = snapshot(args.game)
    changed = [path for path in sorted(set(before) | set(after)) if before.get(path) != after.get(path)]
    assert not changed, f'Runtime changed: {changed}'
    gallery_dir = args.game / 'docs/art/534_potion_grade'
    if not args.defer_game_gallery:
        gallery_dir.mkdir(parents=True, exist_ok=True)
    initial_dir = REPO / 'reports/534/packing_initial'
    revised = any(row.get('source_revision', row['item_id']) != row['item_id'] for row in manifest['items'])
    initial_sources, same_frame = [], []
    if revised:
        initial_manifest = json.loads((initial_dir / 'manifest.json').read_text(encoding='utf-8'))
        for row in initial_manifest['items']:
            for path_key, sha_key in [('source_path', 'source_sha256'), ('generated_path', 'generated_sha256'), ('game_path', 'game_sha256')]:
                assert sha(initial_dir / row[path_key]) == row[sha_key]
                if path_key != 'game_path':
                    assert sha(ROOT / row[path_key]) == row[sha_key], 'Initial source must remain immutable'
            initial_sources.append(dict(id=row['item_id'], source_sha256=row['source_sha256'],
                                        generated_sha256=row['generated_sha256'], game_sha256=row['game_sha256']))
        for mode in ['overview', 'actual']:
            old = np.asarray(Image.open(initial_dir / f'qa/godot_{mode}.png').convert('RGB'))
            new = np.asarray(Image.open(ROOT / f'qa/godot_{mode}.png').convert('RGB'))
            anchors = [(0, 0, 1280, 80), (0, 80, 431, 905), (860, 80, 1280, 495)]
            changed_pixels = sum(int(np.count_nonzero(np.any(old[y0:y1, x0:x1] != new[y0:y1, x0:x1], axis=2)))
                                 for x0, y0, x1, y1 in anchors)
            assert changed_pixels == 0, f'Unchanged title/basic2/HP3 anchors shifted in {mode}'
            same_frame.append(dict(mode=mode, title_basic2_hp3_pixels_changed=changed_pixels, regions=anchors))
    gallery, logs = [], []
    for mode in MODES:
        stdout, stderr = [REPORT / f'godot_{mode}_{channel}.txt' for channel in ['stdout', 'stderr']]
        raw = stdout.read_text(encoding='utf-8-sig') + '\n' + stderr.read_text(encoding='utf-8-sig')
        assert f'GODOT_534_PASS mode={mode} items=6' in raw
        assert 'resource_paths/render validated; definitions unchanged' in raw
        assert 'SCRIPT ERROR' not in raw and 'ERROR:' not in raw and stderr.stat().st_size == 0
        png = ROOT / f'qa/godot_{mode}.png'
        assert Image.open(png).size == (1280, 960)
        jpg = ROOT / f'qa/{mode}.jpg'
        jpeg(png, jpg)
        shutil.copyfile(png, REPORT / png.name)
        shutil.copyfile(jpg, REPORT / jpg.name)
        present = not revised or mode in ['overview', 'actual', 'belt_stress']
        if not args.defer_game_gallery and present:
            shutil.copyfile(jpg, gallery_dir / jpg.name)
        logs.append(dict(mode=mode, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr), errors=0))
        if present:
            gallery.append(dict(filename=jpg.name, bytes=jpg.stat().st_size, sha256=sha(jpg), round='after' if revised else 'initial'))
    diagnostic = json.loads((REPORT / 'alpha_comparison.json').read_text(encoding='utf-8'))
    assert diagnostic['ready'] == 4 and all(r['rgb_max_delta'] == 0 for r in diagnostic['items'])
    diagnostic_jpg = ROOT / 'qa/alpha_comparison.jpg'
    jpeg(REPORT / 'alpha_comparison.png', diagnostic_jpg)
    if not args.defer_game_gallery:
        shutil.copyfile(diagnostic_jpg, gallery_dir / diagnostic_jpg.name)
    gallery.append(dict(filename=diagnostic_jpg.name, bytes=diagnostic_jpg.stat().st_size, sha256=sha(diagnostic_jpg)))
    if revised:
        for mode in ['overview', 'actual']:
            before = initial_dir / f'qa/{mode}.jpg'
            target = ROOT / f'qa/before_{mode}.jpg'
            shutil.copyfile(before, target)
            if not args.defer_game_gallery:
                shutil.copyfile(target, gallery_dir / target.name)
            gallery.append(dict(filename=target.name, bytes=target.stat().st_size, sha256=sha(target), round='before'))
        if not args.defer_game_gallery:
            # Only our untracked initial-gallery outputs may be removed; full PNG/JPG proof stays in reports.
            for mode in ['black', 'grayscale']:
                unused = gallery_dir / f'{mode}.jpg'
                if unused.exists():
                    assert sha(unused) == sha(initial_dir / f'qa/{mode}.jpg')
                    assert unused.resolve().is_relative_to(gallery_dir.resolve())
                    unused.unlink()
    assert len(gallery) == 6 and sum(item['bytes'] for item in gallery) < 2000000
    checks = dict(card=534, status='candidate_not_installed', definition_state='existing',
                  definitions='HP40/80/140 and MP25/50/90; CONSUMABLE/tier1/max_stack10/1x1',
                  original_and_clean_sha_preserved=True, approved_basic_source_sha_preserved=True,
                  runtime_files_byte_match=len(after),
                  icons_a_png=sum(p.startswith('assets/sprites/ui/icons_a/') and p.endswith('.png') for p in after),
                  icons_h1_png=sum(p.startswith('assets/sprites/ui/icons_h1/') and p.endswith('.png') for p in after),
                  manual_alpha_editing=False, manual_pixel_editing=False, alpha_thresholding=False,
                  initial_sources_preserved=initial_sources, same_frame=same_frame,
                  comparison='Initial vs corrected' if revised else 'Initial candidate',
                  alpha=alpha, actual_ui=manifest['actual_ui'], godot_ui_skin_modes=logs,
                  fixture_resource_paths='Unique qa534 paths with icons_a prefix; no loaded ItemDef icon replaced',
                  qa_script_sha256=sha(ROOT / 'qa_godot.gd'),
                  visual_review=dict(method='All five Godot plates plus alpha-composited diagnostic inspected',
                                     clean_on_black_and_gray='No visible background halo; clean RGB matches original',
                                     hp_stage3='Neck metal and taller bottle remain different from paper-covered stage1/2',
                                     hp_stage1_2='Corrected stage2 has flat wood cap and broad bronze shoulder instead of folded paper cap; shape remains visible at40/42' if revised else 'Same paper cap family; separation mainly proportion and glaze',
                                     mp_stage2_3='Corrected stage2 single rounded body and broad neck vs stage3 two bulbs/broad brass cap-band remain different at40/42; fine carving and small knots weaken at30/36' if revised else 'Metal cap and cloud engraving are visible at source/80; silhouettes nearly equal at40/42; weak separation at30/36',
                                     smallest_size_limit='30px belt has only14px art height after padding8; do not expect cloud carving/cord/bead detail to carry grade by itself',
                                     approval='PD visual decision required; no automatic adoption or runtime intake'),
                  packing_failure_raw='reports/534/packing/packing_failed_relative_selection.txt' if revised else None,
                  gallery=gallery)
    write_json(ROOT / 'verification.json', checks)
    write_json(REPORT / 'verification.json', checks)
    print(f"PASS #534: RGBA80x80 x4; raw/clean RGB delta0/SHA preserved; runtime{len(after)} byte-preserved; actual UiSkin5 modes/error0; JPG6 <=300KB each; candidate not installed")


if __name__ == '__main__':
    main()
