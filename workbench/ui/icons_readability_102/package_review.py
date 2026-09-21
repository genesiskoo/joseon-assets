"""Ticket #102: alpha-preserving sizing and reproducible review composition only."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

ITEMS = [
    ('leather_shoes', '가죽신', (2, 2), '발등·발목의 넓은 면'),
    ('leather_armor', '가죽갑', (2, 3), '옷깃·몸통을 큰 면으로 분리'),
    ('jade_charm', '옥패', (1, 1), '큰 원반·짧은 고리'),
    ('long_sword', '장검', (1, 3), '곧은 장검·넓힌 칼날'),
    ('iron_sword', '철검', (1, 3), '짧은 손잡이·넓은 직선 칼날'),
    ('hwando', '환도', (1, 3), '곡선 칼날·짧은 술'),
    ('ident_scroll', '식별부', (1, 1), '넓은 종이·접힌 모서리'),
    ('town_portal', '귀환부', (1, 1), '긴 종이·먹문양의 빈 중앙'),
]
RESAMPLE = Image.Resampling.LANCZOS
BG = '#171b21'
WELL = '#292d33'
INK = '#e0d8c9'
MUTED = '#a5adb6'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', size)

def label(im, xy, text, size=15, fill=INK):
    ImageDraw.Draw(im).text(xy, text, font=font(size), fill=fill)

def resize(im, size, method=RESAMPLE):
    return im.convert('RGBa').resize(size, method).convert('RGBA')

def alpha_info(im):
    a = im.getchannel('A')
    h = a.histogram()
    return {'dimensions': list(im.size), 'alpha_extrema': list(a.getextrema()),
            'alpha_bbox': list(a.getbbox()), 'transparent_pixels': h[0],
            'partial_pixels': sum(h[1:255]), 'opaque_pixels': h[255]}

def package(im):
    # Crop bounds ignore alpha 1..7 specks far from the visible object. This
    # does not repaint, key a background, or threshold any retained pixel.
    a = im.getchannel('A')
    box = a.point(lambda v: 255 if v >= 8 else 0).getbbox()
    assert box
    box = (max(0, box[0]-2), max(0, box[1]-2), min(im.width, box[2]+2), min(im.height, box[3]+2))
    crop = im.crop(box)
    scale = 103 / max(crop.size)
    target = tuple(max(1, round(v*scale)) for v in crop.size)
    art = resize(crop, target)
    out = Image.new('RGBA', (128, 128))
    out.paste(art, ((128-art.width)//2, (128-art.height)//2))
    return out, list(box)

def fit(icon, size, padding=8):
    # Geometry follows UiSkin.item_icon: used rect -> content area -> contain.
    art = icon.crop(icon.getchannel('A').getbbox())
    scale = min((size[0]-2*padding)/art.width, (size[1]-2*padding)/art.height)
    art = resize(art, tuple(max(1, round(v*scale)) for v in art.size), Image.Resampling.BILINEAR)
    out = Image.new('RGBA', size)
    out.alpha_composite(art, ((size[0]-art.width)//2, (size[1]-art.height)//2))
    return out

def nine_slice(slot, size):
    out = Image.new('RGBA', size)
    sx, sy = [0, 8, slot.width-8, slot.width], [0, 8, slot.height-8, slot.height]
    tx, ty = [0, 8, size[0]-8, size[0]], [0, 8, size[1]-8, size[1]]
    for y in range(3):
        for x in range(3):
            part = slot.crop((sx[x], sy[y], sx[x+1], sy[y+1]))
            out.paste(resize(part, (tx[x+1]-tx[x], ty[y+1]-ty[y]), Image.Resampling.BILINEAR), (tx[x], ty[y]))
    return out

def well(size, slot, neutral, cells=None):
    out = Image.new('RGBA', size, WELL)
    if neutral:
        ImageDraw.Draw(out).rectangle((0, 0, size[0]-1, size[1]-1), outline='#57565a', width=1)
    elif cells:
        for y in range(cells[1]):
            for x in range(cells[0]):
                out.alpha_composite(nine_slice(slot, (40, 40)), (x*40, y*40))
    else:
        out.alpha_composite(nine_slice(slot, size))
    return out

def tile(icon, size, slot, neutral, cells=None):
    out = well(size, slot, neutral, cells)
    out.alpha_composite(fit(icon, size))
    return out

def make_review(out, icons, baseline, slot):
    # Every raster is displayed at its labelled pixel dimensions, without zoom.
    sheet = Image.new('RGBA', (1192, 752), BG)
    label(sheet, (22, 14), '#102  H1 아이템 8종 — 기존 / 후보', 24)
    label(sheet, (22, 51), '128px 납품 파일 · 아래 32px는 그림 경계를 맞춘 축소 · 제안 바탕 / 실게임 아님', 16)
    for i, (key, name, _, change) in enumerate(ITEMS):
        x, y = 16+(i%4)*294, 93+(i//4)*322
        label(sheet, (x+4, y), name, 19)
        label(sheet, (x+4, y+28), change, 13, MUTED)
        for j, (tag, icon) in enumerate([('기존', baseline[key]), ('후보', icons[key])]):
            bx = x+4+j*142
            base = Image.new('RGBA', (128, 128), WELL)
            base.alpha_composite(icon)
            sheet.alpha_composite(base, (bx, y+55))
            label(sheet, (bx, y+189), tag+' · 128px', 13)
            sheet.alpha_composite(tile(icon, (48, 48), slot, True), (bx+40, y+217))
            label(sheet, (bx+23, y+272), '내용 32px', 13, MUTED)
    sheet.convert('RGB').save(out/'review'/'comparison.png')

    small = Image.new('RGBA', (1180, 1160), BG)
    label(small, (22, 14), '#102  축소 검수 — 24 / 32 / 46px', 24)
    label(small, (22, 50), '숫자 = 아이콘 내용 영역의 한 변 · 슬롯 = 내용 + 16px · CPU 재현 / 실게임 아님', 15)
    groups = [('기존 / 현재 목조', False, False), ('후보 / 현재 목조', True, False),
              ('기존 / 제안 중성', False, True), ('후보 / 제안 중성', True, True)]
    for g, (title, _, _) in enumerate(groups):
        label(small, (202+g*242, 87), title, 17)
    for i, (key, name, _, _) in enumerate(ITEMS):
        y = 122+i*123
        label(small, (20, y+19), name, 17)
        label(small, (20, y+49), key, 12, MUTED)
        for g, (_, new, neutral) in enumerate(groups):
            for px, offset in [(24, 0), (32, 62), (46, 134)]:
                x = 202+g*242+offset
                size = px+16
                small.alpha_composite(tile((icons if new else baseline)[key], (size, size), slot, neutral), (x, y))
                label(small, (x+7, y+67), str(px)+'px', 12, MUTED)
    label(small, (22, 1118), '동일한 비율·안쪽 여백. 제안 중성 바탕은 #101의 최종 구현이 아닙니다.', 15)
    small.convert('RGB').save(out/'review'/'small_sizes.png')

    multi = Image.new('RGBA', (980, 1575), BG)
    label(multi, (20, 14), '#102  인벤토리 실제 점유 크기 비교', 24)
    label(multi, (20, 50), '40px × 칸수, 안쪽 여백 8px · CPU 레이아웃 재현 / 실게임 아님', 15)
    for g, (title, _, _) in enumerate(groups):
        label(multi, (202+g*190, 87), title, 16)
    for i, (key, name, cells, _) in enumerate(ITEMS):
        y = 127+i*151
        size = (40*cells[0], 40*cells[1])
        label(multi, (20, y+18), name, 18)
        label(multi, (20, y+48), f'{cells[0]}×{cells[1]}칸 · {size[0]}×{size[1]}px', 13, MUTED)
        for g, (_, new, neutral) in enumerate(groups):
            im = tile((icons if new else baseline)[key], size, slot, neutral, cells)
            multi.alpha_composite(im, (202+g*190+(128-size[0])//2, y))
    label(multi, (20, 1360), '밝은 장비 기준점 — 기존 무명도포 / 짚신 (재생성하지 않음)', 17)
    for i, key in enumerate(['cotton_robe', 'straw_shoes']):
        multi.alpha_composite(tile(baseline[key], (112, 128), slot, True), (26+i*138, 1404))
    label(multi, (332, 1420), '검 3종은 세로 구도로 1×3칸의 높이를 활용합니다.', 16)
    label(multi, (332, 1452), '첫 대각선 후보 2종은 기각 보관. 반입 검수는 #103.', 15)
    label(multi, (332, 1493), '게임 속 등급·선택·드래그 오버레이는 여기서 판정하지 않습니다.', 14, MUTED)
    multi.convert('RGB').save(out/'review'/'inventory_footprints.png')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-inputs', action='store_true')
    parser.add_argument('--game', type=Path, default=Path('C:/workspace/joseon'))
    args = parser.parse_args()
    out = Path(__file__).resolve().parent
    inputs = out/'review'/'baseline'
    inputs.mkdir(parents=True, exist_ok=True)
    if args.capture_inputs:
        for key in [v[0] for v in ITEMS]+['cotton_robe', 'straw_shoes']:
            shutil.copy2(args.game/'assets/sprites/ui/icons_h1'/f'{key}.png', inputs/f'{key}.png')
        shutil.copy2(args.game/'assets/sprites/ui/skin/slot.png', inputs/'slot.png')
    icons, records = {}, []
    for key, name, cells, _ in ITEMS:
        source = out/'sources'/f'{key}.png'
        im = Image.open(source).convert('RGBA')
        before = alpha_info(im)
        assert before['alpha_extrema'] == [0, 255], key+' missing true alpha'
        assert before['transparent_pixels'] > im.width*im.height*.05, key+' nearly opaque'
        icon, crop = package(im)
        path = out/f'{key}.png'
        icon.save(path, compress_level=9)
        info = alpha_info(icon)
        x0,y0,x1,y1 = info['alpha_bbox']
        assert x0>=12 and y0>=12 and x1<=116 and y1<=116, key+' unsafe bounds'
        metadata = json.loads((out/'sources'/f'{key}.json').read_text(encoding='utf-8-sig'))
        icons[key] = icon
        records.append({**metadata, 'name': name, 'inventory_cells': list(cells),
                        'source_info': before, 'crop_alpha_ge_8_plus_2px': crop,
                        'source_sha256': digest(source), 'output': path.name,
                        'output_sha256': digest(path), 'output_info': info,
                        'baseline_sha256': digest(inputs/f'{key}.png')})
    baseline = {key: Image.open(inputs/f'{key}.png').convert('RGBA')
                for key in [v[0] for v in ITEMS]+['cotton_robe', 'straw_shoes']}
    slot = Image.open(inputs/'slot.png').convert('RGBA')
    make_review(out, icons, baseline, slot)
    manifest = {'schema': 1, 'issue': 102, 'date': '2026-09-21', 'status': 'PD_review_required',
                'tool': 'built-in imagegen', 'model_version': 'not exposed by tool',
                'requested_size': [1024,1024], 'canvas': [128,128], 'art_longest_px': 103,
                'processing': 'alpha-support bounding crop >=8/255 plus 2px; preserve retained RGBA; premultiplied proportional resize; center; no repaint or background keying',
                'preview': 'CPU approximation of used-rect, 8px padding, linear texture filter, 8px 9-slice. Not Godot screenshots. Neutral well is an unimplemented #101 proposal.',
                'preview_inputs': {p.name:digest(p) for p in sorted(inputs.glob('*.png'))},
                'rejected': [{'id': key, 'source': f'rejected/diagonal_swords/{key}.png',
                'sha256': digest(out/'rejected'/'diagonal_swords'/f'{key}.png'),
                'reason': 'Diagonal composition shrank to about 24px in a 1x3 slot; superseded by upright revision.'}
                for key in ['iron_sword', 'hwando']],
                'items': records, 'checks': {'count': len(records), 'rgba_128': True, 'slot_safe_bounds': True,
                'runtime_test': 'not_run_asset_candidate_only', 'engine_input_test': 'deferred_to_103'}}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: 8 transparent RGBA sources; 8 slot-safe 128px outputs; 3 review sheets. Runtime not tested.')
    for row in records:
        print(row['id'], row['source_info']['dimensions'], row['output_info']['alpha_bbox'])

if __name__ == '__main__':
    main()
