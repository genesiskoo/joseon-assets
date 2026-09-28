"""Common alpha16/8percent/Lanczos packing and analysis plates, no creative edits."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps
from prepare_491 import GAME, sha

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
    assert len(inputs['items']) == len(sources['items']) == 3
    for folder in ['source/items', 'game/items', 'qa']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    rows = []
    for spec, gen in zip(inputs['items'], sources['items']):
        uid = spec['item_id']
        assert uid == gen['id'] and spec['definition_state'] == 'design_only'
        assert not Path(spec['planned_definition_path']).exists()
        native = Path(gen['native_path'])
        source = ROOT / 'source/items' / f'{uid}.png'
        if source.exists():
            assert sha(source) == sha(native)
        else:
            shutil.copyfile(native, source)
        raw = Image.open(source)
        assert raw.mode == 'RGBA'
        alpha = raw.getchannel('A').getextrema()
        assert alpha[0] == 0 and alpha[1] >= 250
        packed, bbox = contain(raw, (160, 240))
        assert 0 < bbox[0] < bbox[2] < raw.width and 0 < bbox[1] < bbox[3] < raw.height
        path = ROOT / 'game/items' / f'{uid}.png'
        packed.save(path, optimize=True)
        bounds = packed.getchannel('A').getbbox()
        assert bounds and bounds[0] >= 2 and bounds[1] >= 2 and bounds[2] <= 158 and bounds[3] <= 238
        packed_alpha = packed.getchannel('A').getextrema()
        assert packed_alpha[0] == 0 and packed_alpha[1] >= 250
        assert sha(Path(spec['reference_path'])) == spec['reference_sha256']
        rows.append(dict(spec, source_path=source.relative_to(ROOT).as_posix(), source_size=list(raw.size),
                         source_sha256=sha(source), source_alpha=list(alpha), source_bbox=list(bbox),
                         game_path=path.relative_to(ROOT).as_posix(), game_sha256=sha(path),
                         game_size=[160, 240], game_alpha=list(packed.getchannel('A').getextrema()),
                         visible_bbox=list(bounds)))
    for rel, expected in inputs['source_docs'].items():
        assert sha(GAME / rel) == expected
    manifest = dict(card=491, parent_card=274, status='candidate_not_installed', definition_state='design_only',
                    intake_predecessor=272, method='native image_gen; common alpha16/8percent/Lanczos ratio packing',
                    logical_cell_px=40, output_scale=2, source_docs=inputs['source_docs'], items=rows)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    image = Image.new('RGBA', (1280, 960), (29, 25, 21, 255))
    draw = ImageDraw.Draw(image)
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    fonts = {n: ImageFont.truetype(font_path, n) for n in [13, 16, 18, 24]}
    draw.text((22, 17), '#491 D1 T3 갑·포3 — 원화 / 승인 T2 비교 / 40px칸', font=fonts[24], fill='#e5d5bd')
    for i, row in enumerate(rows):
        x = 16 + i * 420
        draw.rectangle((x, 66, x + 407, 904), fill='#241f1b', outline='#665744')
        draw.text((x + 18, 79), row['display_name'], font=fonts[24], fill='#e5d5bd')
        raw = Image.open(ROOT / row['source_path'])
        hero, _ = contain(raw, (369, 466))
        image.alpha_composite(hero, (x + 19, 116))
        draw.text((x + 18, 592), row['note'], font=fonts[16], fill='#b6a791')
        draw.text((x + 18, 630), row['reference_display_name'] + ' / 후보 / 무채색', font=fonts[16], fill='#b6a791')
        packed = Image.open(ROOT / row['game_path'])
        gray = ImageOps.grayscale(packed).convert('RGBA')
        gray.putalpha(packed.getchannel('A'))
        for j, target in enumerate([Image.open(row['reference_path']), packed, gray]):
            sx = x + 34 + j * 120
            draw.rectangle((sx, 665, sx + 80, 785), fill='black', outline='#82705b')
            shown = target.convert('RGBA').resize((80, 120), Image.Resampling.LANCZOS)
            image.alpha_composite(shown, (sx, 665))
        draw.text((x + 18, 817), '예정2×3 / 160×240 RGBA', font=fonts[16], fill='#b6a791')
        draw.text((x + 18, 851), row['item_id'], font=fonts[13], fill='#9a8e7c')
        draw.text((x + 18, 875), '사양기반 원화 · #272 게임반입 선행', font=fonts[13], fill='#9a8e7c')
    draw.text((20, 927), '비교는 #464 채택 T2 원화(미게임반입) · T3 실제 데이터 아직 없음 · 길이/형태를 왜곡하지 않음', font=fonts[16], fill='#b6a791')
    image.convert('RGB').save(ROOT / 'qa/overview.png')
    image.convert('RGB').save(ROOT / 'qa/overview.jpg', quality=86, optimize=True)
    assert (ROOT / 'qa/overview.jpg').stat().st_size < 300000
    print('PACKED #491 native3 preserved -> RGBA160x240/2x3, approved T2 SHA3, overview1280x960')
    print(json.dumps([dict(id=r['item_id'], native=r['source_size'], alpha=r['source_alpha'], bbox=r['visible_bbox']) for r in rows]))


if __name__ == '__main__':
    main()
