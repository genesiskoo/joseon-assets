"""Preserve the real potion contracts and pack Comfy cutouts without creative edits."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
REPORT = REPO / 'reports/534/packing'
DEFAULT_GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/534-potion-grade-art/joseon')
PLAN = [('hp_potion_2', '십전대보탕', 'hp', 2, 80, 6),
        ('hp_potion_3', '경옥고', 'hp', 3, 140, 13),
        ('mp_potion_2', '총명탕', 'mp', 2, 50, 6),
        ('mp_potion_3', '공진단', 'mp', 3, 90, 13)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def runtime_files(game):
    files = list((game / 'assets/sprites/ui/icons_a').rglob('*.png'))
    files += list((game / 'assets/sprites/ui/icons_h1').rglob('*.png'))
    files += list((game / 'data/items').glob('*.tres')) + list((game / 'data/uniques').glob('*.tres'))
    files += list((game / 'ui').rglob('*.gd')) + list((game / 'items').rglob('*.gd'))
    return sorted(set(files))


def snapshot(game):
    return {p.relative_to(game).as_posix(): sha(p) for p in runtime_files(game)}


def scalar(text, name, default=None):
    match = re.search(r'^' + re.escape(name) + r' = (.+)$', text, re.M)
    return match.group(1).strip() if match else default


def image_stats(path):
    image = Image.open(path).convert('RGBA')
    a = np.asarray(image)[:, :, 3]
    return dict(size=list(image.size), mode=Image.open(path).mode, alpha=[int(a.min()), int(a.max())],
                bbox=list(image.getchannel('A').getbbox()), nonzero=int(np.count_nonzero(a)),
                partial=int(np.count_nonzero((a > 0) & (a < 255))), opaque=int(np.count_nonzero(a == 255)))


def contain(raw, size):
    """Use the supplied alpha unchanged; only crop, premultiplied resize and pad."""
    raw = raw.convert('RGBA')
    bounds = raw.getchannel('A').getbbox()
    assert bounds
    art = raw.crop(bounds)
    pad = max(1, round(min(size) * .08))
    scale = min((size[0] - 2 * pad) / art.width, (size[1] - 2 * pad) / art.height)
    shown = art.convert('RGBa').resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.Resampling.LANCZOS).convert('RGBA')
    result = Image.new('RGBA', size)
    result.alpha_composite(shown, ((size[0] - shown.width) // 2, (size[1] - shown.height) // 2))
    return result, list(bounds), pad


def alpha_diagnostic():
    """Never confuse RGB hidden behind alpha zero with a visible background halo."""
    REPORT.mkdir(parents=True, exist_ok=True)
    ready = [uid for uid, *_ in PLAN if (REPO / f'reports/534/comfy_birefnet/{uid}_clean.png').exists()]
    assert ready
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 15)
    sheet = Image.new('RGB', (1280, 70 + len(ready) * 300), '#252622')
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 12), '#534 원본/clean 실제 alpha 합성 · 검정/회색 · 마스크', font=font, fill='#e5d5bd')
    checks = []
    for i, uid in enumerate(ready):
        original_path = REPO / f'reports/534/comfy_gpt25/{uid}.png'
        clean_path = REPO / f'reports/534/comfy_birefnet/{uid}_clean.png'
        original, clean = Image.open(original_path).convert('RGBA'), Image.open(clean_path).convert('RGBA')
        a, b = np.asarray(original), np.asarray(clean)
        assert a.shape == b.shape
        delta = np.abs(a[:, :, :3].astype(np.int16) - b[:, :, :3].astype(np.int16))
        checks.append(dict(id=uid, generated_sha256=sha(original_path), clean_sha256=sha(clean_path),
                           generated=image_stats(original_path), clean=image_stats(clean_path),
                           rgb_max_delta=int(delta.max()), rgb_pixels_changed=int(np.count_nonzero(np.any(delta, axis=2))),
                           alpha_pixels_changed=int(np.count_nonzero(a[:, :, 3] != b[:, :, 3])),
                           samples={str(point): dict(generated_alpha=int(a[point[1], point[0], 3]),
                                                   clean_alpha=int(b[point[1], point[0], 3]))
                                    for point in [(512, 20), (100, 512), (512, 1023)]}))
        y = 70 + i * 300
        for j, (image, background, title) in enumerate([(original, '#000000', '원본 / 검정'), (clean, '#000000', 'clean / 검정'),
                                                       (original, '#7a7a7a', '원본 / 회색'), (clean, '#7a7a7a', 'clean / 회색')]):
            x = 16 + j * 254
            shown = image.resize((236, 236), Image.Resampling.LANCZOS)
            composed = Image.alpha_composite(Image.new('RGBA', shown.size, background), shown)
            sheet.paste(composed.convert('RGB'), (x, y + 35))
            draw.text((x, y), uid + ' ' + title, font=font, fill='#e5d5bd')
        mask = clean.getchannel('A').resize((236, 236), Image.Resampling.NEAREST).convert('RGB')
        sheet.paste(mask, (1032, y + 35))
        draw.text((1032, y), 'clean alpha', font=font, fill='#e5d5bd')
    sheet.save(REPORT / 'alpha_comparison.png')
    sheet.save(REPORT / 'alpha_comparison.jpg', quality=85, optimize=True)
    write_json(REPORT / 'alpha_comparison.json', dict(card=534, ready=len(ready), items=checks,
               production_alpha_thresholding=False, manual_alpha_editing=False))
    print(json.dumps(checks, ensure_ascii=False, indent=2))


def prepare(game):
    plan = json.loads((ROOT / 'generation_plan.json').read_text(encoding='utf-8'))
    jobs = {row['id']: row for row in plan['jobs']}
    assert len(jobs) == 4
    rows = []
    for uid, name, family, stage, power, level in PLAN:
        path = game / f'data/items/{uid}.tres'
        text = path.read_text(encoding='utf-8')
        assert scalar(text, 'id') == f'"{uid}"' and name in scalar(text, 'display_name')
        assert scalar(text, 'slot') == '6' and scalar(text, 'size') == 'Vector2i(1, 1)'
        assert int(scalar(text, 'tier', '1')) == 1 and int(scalar(text, 'max_stack')) == 10
        assert int(scalar(text, 'min_ilvl')) == level and float(scalar(text, 'power')) == power
        assert int(scalar(text, 'consumable')) == (1 if family == 'hp' else 2)
        assert f'path="res://assets/sprites/ui/icons_a/items/{family}_potion.png"' in text
        contract = jobs[uid]['contract']
        assert contract['tier'] == 1 and contract['runtime_px'] == [80, 80]
        assert contract['restores'] == power and contract['item_level'] == level and contract['max_stack'] == 10
        rows.append(dict(item_id=uid, display_name=name, resource=family, efficacy_stage=stage,
                         tier=1, slot=6, consumable_kind=1 if family == 'hp' else 2,
                         grid_w=1, grid_h=1, max_stack=10, power=power, min_ilvl=level,
                         definition_path=path.as_posix(), definition_sha256=sha(path),
                         current_shared_icon=f'assets/sprites/ui/icons_a/items/{family}_potion.png'))
    refs = []
    for family in ['hp', 'mp']:
        source = ROOT / f'refs/{family}_potion_basic.png'
        current = game / f'assets/sprites/ui/icons_a/items/{family}_potion.png'
        definition = game / f'data/items/{family}_potion.tres'
        basic_text = definition.read_text(encoding='utf-8')
        runtime_copy = ROOT / f'source/reference_runtime/{family}_potion.png'
        runtime_copy.parent.mkdir(parents=True, exist_ok=True)
        if runtime_copy.exists():
            assert sha(runtime_copy) == sha(current)
        else:
            shutil.copyfile(current, runtime_copy)
        declared = jobs[f'{family}_potion_2']['references'][0]
        assert sha(source) == declared['sha256']
        refs.append(dict(item_id=f'{family}_potion', resource=family, efficacy_stage=1,
                         display_name=scalar(basic_text, 'display_name').strip('"').split(' — ')[-1],
                         tier=1, power=float(scalar(basic_text, 'power')), min_ilvl=int(scalar(basic_text, 'min_ilvl')),
                         definition_path=definition.as_posix(), definition_sha256=sha(definition),
                         source_path=source.relative_to(ROOT).as_posix(), source_sha256=sha(source),
                         runtime_path=current.as_posix(), runtime_sha256=sha(current),
                         runtime_snapshot_path=runtime_copy.relative_to(ROOT).as_posix(),
                         runtime_size=list(Image.open(current).size)))
    baseline = snapshot(game)
    before_path = ROOT / 'runtime_before.json'
    if before_path.exists():
        assert json.loads(before_path.read_text(encoding='utf-8')) == baseline, 'Runtime changed since baseline'
    else:
        write_json(before_path, baseline)
    source_docs = {rel: sha(game / rel) for rel in ['docs/design/item_catalog_v2.md', 'docs/design/item_system_v2.md']}
    inputs = dict(card=534, parent_card=274, game_repository=game.as_posix(), definition_state='existing',
                  status='candidate_not_installed', source_docs=source_docs, items=rows, references=refs,
                  actual_ui=dict(bag=[40, 8], vendor=[48, 3], belt=[42, 8], belt_stress=[[30, 8], [36, 8]]))
    write_json(ROOT / 'inputs.json', inputs)
    print(f'PREPARED #534 real definitions4/tier1/1x1/max_stack10; runtime SHA {len(baseline)} preserved')
    return inputs


def pack(game, inputs):
    for directory in ['source/items', 'game/items', 'qa']:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    rows = []
    for row in inputs['items']:
        uid = row['item_id']
        native = REPO / f'reports/534/comfy_gpt25/{uid}.png'
        clean = REPO / f'reports/534/comfy_birefnet/{uid}_clean.png'
        assert native.exists() and clean.exists(), f'Wait for final Comfy result: {uid}'
        for origin, destination in [(native, ROOT / f'source/items/{uid}_generated.png'), (clean, ROOT / f'source/items/{uid}.png')]:
            if destination.exists():
                assert sha(origin) == sha(destination), f'Never replace a preserved source: {destination}'
            else:
                shutil.copyfile(origin, destination)
        raw = Image.open(clean)
        assert raw.mode == 'RGBA' and raw.size == (1024, 1024)
        assert raw.getchannel('A').getextrema() == (0, 255)
        result, bounds, pad = contain(raw, (80, 80))
        assert 0 < bounds[0] < bounds[2] < 1024 and 0 < bounds[1] < bounds[3] < 1024
        path = ROOT / f'game/items/{uid}.png'
        result.save(path, optimize=True)
        bbox = result.getchannel('A').getbbox()
        assert bbox and min(bbox[:2]) >= pad and max(bbox[2:]) <= 80 - pad
        assert result.getchannel('A').getextrema() == (0, 255)
        rows.append(dict(row, generated_path=f'source/items/{uid}_generated.png', generated_sha256=sha(native),
                         source_path=f'source/items/{uid}.png', source_sha256=sha(clean), source_stats=image_stats(clean),
                         source_crop=bounds, packing_padding_px=pad, game_path=f'game/items/{uid}.png',
                         game_sha256=sha(path), game_size=[80, 80], game_alpha=[0, 255], visible_bbox=list(bbox)))
    assert snapshot(game) == json.loads((ROOT / 'runtime_before.json').read_text(encoding='utf-8'))
    manifest = dict(inputs, method='Comfy GPT25 -> Comfy BiRefNet alpha -> premultiplied Lanczos ratio packing; no alpha threshold',
                    output_scale=2, logical_cell_px=40, manual_pixel_editing=False, manual_alpha_editing=False,
                    production_alpha_thresholding=False)
    manifest['items'] = rows
    write_json(ROOT / 'manifest.json', manifest)
    print('PACKED #534 four RGBA80x80; raw/clean SHA preserved; alpha unchanged before resize; runtime byte-preserved')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=Path, default=DEFAULT_GAME)
    parser.add_argument('--pack', action='store_true')
    parser.add_argument('--diagnostic', action='store_true')
    args = parser.parse_args()
    if args.diagnostic:
        alpha_diagnostic()
    else:
        inputs = prepare(args.game)
        if args.pack:
            pack(args.game, inputs)


if __name__ == '__main__':
    main()
