"""Deterministic alpha/ratio packaging and review plate; no creative edits."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
from prepare_485 import sha

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
    shown = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.Resampling.LANCZOS)
    packed = Image.new('RGBA', size)
    packed.alpha_composite(shown, ((size[0] - shown.width) // 2, (size[1] - shown.height) // 2))
    return packed, bounds


def main():
    inputs = json.loads((ROOT / 'inputs.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT / 'generation_sources.json').read_text(encoding='utf-8'))
    assert len(inputs['items']) == len(sources['items']) == 4
    for directory in ['game/items', 'qa']:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    rows = []
    for spec, gen in zip(inputs['items'], sources['items']):
        uid = spec['item_id']
        assert uid == gen['id']
        original = ROOT / 'source/items' / f'{uid}.png'
        assert sha(original) == sha(Path(gen['native_path']))
        raw = Image.open(original)
        assert raw.mode == 'RGBA'
        alpha_range = raw.getchannel('A').getextrema()
        assert alpha_range[0] == 0 and alpha_range[1] >= 250
        size = (spec['output_width'], spec['output_height'])
        packed, bbox = contain(raw, size)
        assert 0 < bbox[0] < bbox[2] < raw.width and 0 < bbox[1] < bbox[3] < raw.height
        dest = ROOT / 'game/items' / f'{uid}.png'
        packed.save(dest, optimize=True)
        bounds = packed.getchannel('A').getbbox()
        assert bounds and bounds[0] >= 2 and bounds[1] >= 2
        assert bounds[2] <= size[0] - 2 and bounds[3] <= size[1] - 2
        game_alpha = packed.getchannel('A').getextrema()
        assert game_alpha[0] == 0 and game_alpha[1] >= 250
        for field in ['definition', 'base_definition', 'base_reference']:
            assert sha(Path(spec[field + '_path'])) == spec[field + '_sha256']
        rows.append(dict(spec, source_path=original.relative_to(ROOT).as_posix(), source_sha256=sha(original),
                         source_size=list(raw.size), source_bbox=list(bbox), source_alpha=list(alpha_range),
                         game_path=dest.relative_to(ROOT).as_posix(), game_sha256=sha(dest), game_size=list(size),
                         game_alpha=list(game_alpha), visible_bbox=list(bounds)))
    manifest = dict(card=485, parent_card=274, status='candidate_not_installed',
                    method='native image_gen originals; common alpha16/8percent/Lanczos ratio packing',
                    logical_cell_px=40, output_scale=2, items=rows)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    prompts = '# #485 Native image_gen prompts\n\n' + '\n\n'.join(
        '## ' + r['id'] + '\n\n' + r['prompt'] + '\n\nNative original: ' + r['native_path']
        for r in sources['items']) + '\n'
    (ROOT / 'PROMPTS.md').write_text(prompts, encoding='utf-8', newline='\n')
    head = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 14)
    title = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 24)
    sheet = Image.new('RGB', (1280, 850), (26, 23, 21))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 15), '#485 D1 대표유니크 장비4 — 원화 / 베이스 대조 / 40px칸', font=title, fill=(235, 216, 187))
    for i, row in enumerate(rows):
        x = 15 + i * 315
        draw.rectangle((x, 59, x + 302, 816), fill=(34, 30, 27), outline=(88, 72, 52))
        draw.text((x + 14, 70), row['display_name'], font=head, fill=(232, 216, 190))
        raw = Image.open(ROOT / row['source_path'])
        art = raw.crop(tuple(row['source_bbox']))
        art.thumbnail((270, 410), Image.Resampling.LANCZOS)
        sheet.paste(art, (x + 16 + (270 - art.width) // 2, 107 + (410 - art.height) // 2), art)
        draw.text((x + 14, 536), row['note'], font=small, fill=(185, 168, 144))
        draw.text((x + 14, 565), '베이스 / 유니크 후보 / 무채색', font=small, fill=(177, 162, 140))
        slot = (row['grid_w'] * 40, row['grid_h'] * 40)
        icon = Image.open(ROOT / row['game_path']).resize(slot, Image.Resampling.LANCZOS)
        base, _ = contain(Image.open(row['base_reference_path']).convert('RGBA'), slot)
        gray = Image.merge('RGBA', (*([icon.convert('L')] * 3), icon.getchannel('A')))
        for j, img in enumerate([base, icon, gray]):
            px = x + 11 + j * 96 + (80 - slot[0]) // 2
            py = 598
            draw.rectangle((px, py, px + slot[0], py + slot[1]), fill=(0, 0, 0), outline=(100, 82, 58))
            sheet.paste(img, (px, py), img)
        draw.text((x + 14, 733), f"{row['grid_w']}×{row['grid_h']} / {row['output_width']}×{row['output_height']} RGBA", font=small, fill=(177, 162, 140))
        draw.text((x + 14, 762), row['item_id'], font=small, fill=(153, 143, 127))
        draw.text((x + 14, 790), '후보 · 게임 미반입', font=small, fill=(153, 143, 127))
    draw.text((24, 828), '비단 도포 베이스는 채택 원화(#464) · 아래 비교는 실제 Godot UiSkin 스크린샷에서 재검수', font=small, fill=(177, 162, 140))
    sheet.save(ROOT / 'qa/overview.png', optimize=True)
    sheet.save(ROOT / 'qa/overview.jpg', quality=85, optimize=True)
    print('PACKED #485', [(r['item_id'], r['source_size'], r['game_size'], r['game_alpha'], r['visible_bbox']) for r in rows])


if __name__ == '__main__':
    main()
