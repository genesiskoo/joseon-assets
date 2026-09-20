"""Deterministic alpha-preserving H1 item icon packaging; never keys backgrounds."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


EXPECTED = {
    'coin', 'cotton_belt', 'cotton_robe', 'hp_potion', 'hwando',
    'ident_scroll', 'iron_sword', 'jade_charm', 'leather_armor',
    'leather_shoes', 'long_sword', 'mp_potion', 'quilted_robe',
    'silver_ring', 'straw_shoes', 'town_portal', 'wooden_sword',
}
SIZE, ART_SIZE = 128, 103


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alpha_info(im):
    alpha = im.getchannel('A')
    histogram = alpha.histogram()
    bbox = alpha.getbbox()
    return {
        'dimensions': list(im.size), 'alpha_extrema': list(alpha.getextrema()),
        'alpha_counts': {'transparent': histogram[0], 'opaque': histogram[255],
                         'partial': sum(histogram[1:255])},
        'alpha_bbox': list(bbox) if bbox else None,
    }


def read_art(path):
    with Image.open(path) as original:
        if 'A' not in original.getbands() and 'transparency' not in original.info:
            raise ValueError('NO_REAL_TRANSPARENCY: source has no alpha channel')
        im = original.convert('RGBA')
    info = alpha_info(im)
    if info['alpha_extrema'] != [0, 255]:
        raise ValueError('NO_REAL_TRANSPARENCY: alpha must include both 0 and 255')
    x0, y0, x1, y1 = info['alpha_bbox']
    bbox_area = (x1 - x0) * (y1 - y0)
    full_bbox = (x1 - x0) >= im.width * .98 and (y1 - y0) >= im.height * .98
    if full_bbox and info['alpha_counts']['opaque'] / bbox_area >= .95:
        raise ValueError('NO_REAL_TRANSPARENCY: near-full opaque rectangular bbox')
    return im, info


def package(im):
    crop = im.crop(im.getchannel('A').getbbox())
    scale = ART_SIZE / max(crop.size)
    target = tuple(max(1, int(v * scale + .5)) for v in crop.size)
    # Premultiplied resize preserves alpha without hidden RGB edge halos.
    crop = crop.convert('RGBa').resize(target, Image.Resampling.LANCZOS).convert('RGBA')
    result = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    result.paste(crop, ((SIZE - target[0]) // 2, (SIZE - target[1]) // 2))
    return result


def font(size):
    for path in ('C:/Windows/Fonts/malgun.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def old_icon(repo, item_id):
    definition = repo / 'data/items' / (item_id + '.tres')
    if not definition.exists():
        return None
    text = definition.read_text(encoding='utf-8')
    icon = re.search(r'^icon\s*=\s*ExtResource\("([^"]+)"\)', text, re.M)
    if icon:
        for resource in re.findall(r'\[ext_resource ([^\]]+)\]', text):
            attrs = dict(re.findall(r'(\w+)="([^"]+)"', resource))
            if attrs.get('id') == icon[1] and attrs.get('type') == 'Texture2D':
                path = repo / attrs['path'].removeprefix('res://')
                if path.exists():
                    with Image.open(path) as im:
                        return im.convert('RGBA')
    return None


def contact(records, out, repo):
    width, height, cols = 296, 272, 4
    sheet = Image.new('RGB', (width * cols, height * max(1, (len(records) + cols - 1) // cols)), '#303033')
    draw = ImageDraw.Draw(sheet)
    for index, rec in enumerate(records):
        x, y = (index % cols) * width, (index // cols) * height
        draw.text((x + 8, y + 4), rec['id'], fill='white', font=font(13))
        draw.text((x + 8, y + 23), rec['name'], fill='#d6c9ab', font=font(14))
        with Image.open(out / rec['output']) as im:
            icon = im.convert('RGBA')
        for offset, background in ((8, '#17181c'), (152, '#e4e1d8')):
            tile = Image.new('RGBA', (128, 128), background)
            tile.alpha_composite(icon)
            sheet.paste(tile.convert('RGB'), (x + offset, y + 46))
            draw.text((x + offset, y + 177), '128px native', fill='#d6c9ab', font=font(11))
            for px, dx in ((32, 0), (40, 48)):
                tile = Image.new('RGBA', (px, px), background)
                tile.alpha_composite(icon.resize((px, px), Image.Resampling.LANCZOS))
                sheet.paste(tile.convert('RGB'), (x + offset + dx, y + 196))
                draw.text((x + offset + dx, y + 238), f'{px}px', fill='white', font=font(11))
        old = old_icon(repo, rec['id']) if repo else None
        if old:
            old.thumbnail((40, 40), Image.Resampling.LANCZOS)
            tile = Image.new('RGBA', (40, 40), '#17181c')
            tile.alpha_composite(old, ((40 - old.width) // 2, (40 - old.height) // 2))
            sheet.paste(tile.convert('RGB'), (x + 248, y + 196))
            draw.text((x + 248, y + 238), 'old', fill='white', font=font(11))
    sheet.save(out / 'contact_icons_h1.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_map', type=Path)
    parser.add_argument('--output', type=Path, default=None)
    parser.add_argument('--complete', action='store_true')
    parser.add_argument('--repo', type=Path, help='Optional repo root for old icon comparison')
    args = parser.parse_args()
    entries = json.loads(args.source_map.read_text(encoding='utf-8-sig'))
    if not isinstance(entries, list):
        parser.error('source_map must be a JSON list')
    ids = [e.get('id') for e in entries]
    if len(ids) != len(set(ids)) or any(i not in EXPECTED for i in ids):
        parser.error('duplicate or unexpected item ids')
    if args.complete and set(ids) != EXPECTED:
        parser.error('complete requires exactly 17 ids; missing: ' + ', '.join(sorted(EXPECTED - set(ids))))
    out = args.output or args.source_map.parent / 'output'
    out.mkdir(parents=True, exist_ok=True)
    records, failures = [], []
    for entry in entries:
        source = Path(entry['source'])
        if not source.is_absolute():
            source = args.source_map.parent / source
        try:
            for field in ('name', 'prompt'):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    raise ValueError('missing nonempty ' + field)
            im, original = read_art(source)
            result = package(im)
            target = out / (entry['id'] + '.png')
            result.save(target, compress_level=9)
            info = alpha_info(result)
            x0, y0, x1, y1 = info['alpha_bbox']
            safe = x0 >= 12 and y0 >= 12 and x1 <= 116 and y1 <= 116
            if not safe:
                raise ValueError('packaged alpha bbox outside slot-safe bounds')
            records.append({**entry, 'source': str(source.resolve()), 'source_sha256': sha(source),
                            'source_info': original, 'output': target.name, 'output_sha256': sha(target),
                            **info, 'padding': [x0, y0, SIZE - x1, SIZE - y1],
                            'slot_safe_bounds': [12, 12, 116, 116], 'slot_safe': safe})
        except (OSError, ValueError) as error:
            failures.append({'id': entry['id'], 'source': str(source), 'error': str(error)})
            print(f"STOP source {entry['id']}: {error}")
    manifest = {'schema': 1, 'canvas': [128, 128], 'art_longest': 103,
                'complete': len(records) == 17 and not failures, 'items': records,
                'rejected_sources': failures, 'missing_ids': sorted(EXPECTED - {r['id'] for r in records})}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    contact(records, out, args.repo)
    print(f'Packaged {len(records)}; rejected {len(failures)}; manifest: {out / "manifest.json"}')
    return 2 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
