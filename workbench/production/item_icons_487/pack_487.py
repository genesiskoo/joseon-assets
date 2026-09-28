"""Deterministic alpha16/8percent/Lanczos packaging, no creative edits."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
from prepare_487 import GAME, sha

ROOT = Path(__file__).resolve().parent


def contain(raw, size):
    alpha = raw.getchannel('A').point(lambda a: a if a >= 16 else 0)
    bounds = alpha.getbbox()
    assert bounds
    art = raw.copy()
    art.putalpha(alpha)
    art = art.crop(bounds)
    pad = max(5, round(min(size) * .08))
    scale = min((size[0] - 2 * pad) / art.width, (size[1] - 2 * pad) / art.height)
    shown = art.resize((round(art.width * scale), round(art.height * scale)), Image.Resampling.LANCZOS)
    result = Image.new('RGBA', size)
    result.alpha_composite(shown, ((size[0] - shown.width) // 2, (size[1] - shown.height) // 2))
    return result, bounds


def main():
    inputs = json.loads((ROOT / 'inputs.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT / 'generation_sources.json').read_text(encoding='utf-8'))
    assert len(inputs['items']) == len(sources['items']) == 4
    for folder in ['source/items', 'game/items', 'qa']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    rows = []
    for spec, gen in zip(inputs['items'], sources['items']):
        uid = spec['item_id']
        assert uid == gen['id'] and spec['definition_state'] == 'design_only'
        assert not Path(spec['planned_definition_path']).exists()
        suffix = '_' + gen['version'] if gen.get('version') else ''
        source = ROOT / 'source/items' / f'{uid}{suffix}.png'
        native = Path(gen['native_path'])
        if source.exists():
            assert sha(source) == sha(native)
        else:
            shutil.copyfile(native, source)
        raw = Image.open(source)
        assert raw.mode == 'RGBA'
        alpha = raw.getchannel('A').getextrema()
        assert alpha[0] == 0 and alpha[1] >= 250
        packed, bbox = contain(raw, (80, 240))
        assert 0 < bbox[0] < bbox[2] < raw.width and 0 < bbox[1] < bbox[3] < raw.height
        path = ROOT / 'game/items' / f'{uid}.png'
        packed.save(path, optimize=True)
        bounds = packed.getchannel('A').getbbox()
        assert bounds and bounds[0] >= 2 and bounds[1] >= 2 and bounds[2] <= 78 and bounds[3] <= 238
        assert packed.getchannel('A').getextrema()[0] == 0 and packed.getchannel('A').getextrema()[1] >= 250
        rows.append(dict(spec, source_path=source.relative_to(ROOT).as_posix(), source_size=list(raw.size),
                         source_sha256=sha(source), source_alpha=list(alpha), source_bbox=list(bbox),
                         game_path=path.relative_to(ROOT).as_posix(), game_sha256=sha(path),
                         game_size=[80, 240], game_alpha=list(packed.getchannel('A').getextrema()), visible_bbox=list(bounds)))
    for row in rows:
        reference = Path(row['reference_path'])
        if row['reference_sha256']:
            assert sha(reference) == row['reference_sha256']
        else:
            row['reference_sha256'] = sha(reference)
    for rel, expected in inputs['source_docs'].items():
        assert sha(GAME / rel) == expected
    manifest = dict(card=487, parent_card=274, status='candidate_not_installed',
                    definition_state='design_only', intake_predecessor=272,
                    method='native image_gen; common alpha16/8percent/Lanczos ratio packing',
                    logical_cell_px=40, output_scale=2, source_docs=inputs['source_docs'], items=rows)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    prompts = '# #487 Native image_gen prompts\n\n' + '\n\n'.join(
        '## ' + r['id'] + (' ' + r['version'] if r.get('version') else '') + '\n\n' + r['prompt']
        + '\n\nNative original: ' + r['native_path']
        + ('\n\nReferenced image: ' + r['referenced_image_path'] if r.get('referenced_image_path') else '')
        for r in sources['items']) + '\n'
    (ROOT / 'PROMPTS.md').write_text(prompts, encoding='utf-8', newline='\n')
    title = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 23)
    head = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 14)
    sheet = Image.new('RGB', (1280, 850), (26, 23, 21))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 15), '#487 D1 T3 칼3·운룡검 — 원화 / 앞선 단 비교 / 40px칸', font=title, fill=(235, 216, 187))
    for i, row in enumerate(rows):
        x = 15 + i * 315
        draw.rectangle((x, 59, x + 302, 816), fill=(34, 30, 27), outline=(88, 72, 52))
        draw.text((x + 14, 70), row['display_name'], font=head, fill=(232, 216, 190))
        art = Image.open(ROOT / row['source_path']).crop(tuple(row['source_bbox']))
        art.thumbnail((270, 410), Image.Resampling.LANCZOS)
        sheet.paste(art, (x + 16 + (270 - art.width) // 2, 107 + (410 - art.height) // 2), art)
        draw.text((x + 14, 536), row['note'], font=small, fill=(185, 168, 144))
        draw.text((x + 14, 565), row['reference_display_name'] + ' / 후보 / 무채색', font=small, fill=(177, 162, 140))
        icon = Image.open(ROOT / row['game_path']).resize((40, 120), Image.Resampling.LANCZOS)
        reference, _ = contain(Image.open(row['reference_path']).convert('RGBA'), (40, 120))
        gray = Image.merge('RGBA', (*([icon.convert('L')] * 3), icon.getchannel('A')))
        for j, img in enumerate([reference, icon, gray]):
            px = x + 29 + j * 96
            py = 598
            draw.rectangle((px, py, px + 40, py + 120), fill=(0, 0, 0), outline=(100, 82, 58))
            sheet.paste(img, (px, py), img)
        draw.text((x + 14, 733), '예정1×3 / 80×240 RGBA', font=small, fill=(177, 162, 140))
        draw.text((x + 14, 762), row['item_id'], font=small, fill=(153, 143, 127))
        draw.text((x + 14, 790), '사양기반 원화 · #272 반입 선행', font=small, fill=(153, 143, 127))
    draw.text((24, 828), 'T2 본국검·쌍수도·사인검 / 운룡검은 이번 운검 후보와 비교 · 실제 T3 데이터는 아직 없음', font=small, fill=(177, 162, 140))
    sheet.save(ROOT / 'qa/overview.png', optimize=True)
    sheet.save(ROOT / 'qa/overview.jpg', quality=85, optimize=True)
    print('PACKED #487', [(r['item_id'], r['source_size'], r['visible_bbox'], r['reference_status']) for r in rows])


if __name__ == '__main__':
    main()
