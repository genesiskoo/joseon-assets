"""#680 packing of actually rendered Blender RGBA PNGs; no image generation.
28 raw frames -> premultiplied-alpha 4-frame overlap -> 24 frames at 24fps.
Revision2: fixed alpha-union common crop; original RGBA data unchanged, anchor transformed from original384 canvas.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
args = parser.parse_args()
ROOT = Path(args.root)


def seam(frames):
    samples = []
    for a, b in zip(frames, frames[1:] + frames[:1]):
        a, b = np.asarray(a).astype(np.float32), np.asarray(b).astype(np.float32)
        aa, ba = a[..., 3:4] / 255.0, b[..., 3:4] / 255.0
        ac = a[..., :3] * aa + 128 * (1 - aa)
        bc = b[..., :3] * ba + 128 * (1 - ba)
        mask = (a[..., 3] > 16) | (b[..., 3] > 16)
        samples.append(float(np.abs(ac - bc)[mask].mean()) if mask.any() else 0.0)
    median = float(np.median(samples[:-1]))
    return round(samples[-1] / median, 3) if median > 1e-8 else 0.0


def blend_loop(frames, count=4):
    first = []
    for i in range(count):
        h = np.asarray(frames[i]).astype(np.float32)
        t = np.asarray(frames[-count + i]).astype(np.float32)
        w = (i + 1) / (count + 1)
        alpha = h[..., 3:4] * w + t[..., 3:4] * (1 - w)
        premult = h[..., :3] * h[..., 3:4] / 255.0 * w + t[..., :3] * t[..., 3:4] / 255.0 * (1 - w)
        rgb = np.where(alpha > 0.5, premult * 255.0 / np.maximum(alpha, 0.5), 0)
        first.append(Image.fromarray(np.clip(np.concatenate([rgb, alpha], axis=2), 0, 255).astype(np.uint8), 'RGBA'))
    return first + frames[count:-count]


reports = []
for effect, cue, anchor, units in [('fire', 'blender_fire_jet', [0.8194, 0.5], 1.5), ('sal', 'blender_sal_mist', [0.5, 0.5], 1.8)]:
    paths = sorted((ROOT / 'frames' / effect).glob('f_*.png'))
    if len(paths) != 28:
        raise SystemExit(f'Expected 28 real rendered PNGs for {effect}, got {len(paths)}')
    raw = [Image.open(path).convert('RGBA') for path in paths]
    sizes = {im.size for im in raw}
    if sizes != {(384, 384)}:
        raise SystemExit(f'Fixed common canvas mismatch: {sizes}')
    cooked_full = blend_loop(raw)
    union = None
    for im in raw:
        alpha = np.asarray(im)[..., 3]
        yy, xx = np.where(alpha > 2)
        if not xx.size:
            continue
        box = [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]
        union = box if union is None else [min(union[0], box[0]), min(union[1], box[1]), max(union[2], box[2]), max(union[3], box[3])]
    if union is None:
        raise SystemExit('No alpha>2 pixels for fixed crop: ' + effect)
    old_anchor = list(anchor)
    anchor_px = [old_anchor[0] * 384.0, old_anchor[1] * 384.0]
    margin = 8
    if effect == 'sal':
        half_w = min(192, int(math.ceil(max(192 - union[0], union[2] - 192))) + margin)
        half_h = min(192, int(math.ceil(max(192 - union[1], union[3] - 192))) + margin)
        crop = [192 - half_w, 192 - half_h, 192 + half_w, 192 + half_h]
    else:
        crop = [max(0, union[0] - margin), max(0, union[1] - margin), min(384, union[2] + margin), min(384, union[3] + margin)]
    fw, fh = crop[2] - crop[0], crop[3] - crop[1]
    anchor = [round((anchor_px[0] - crop[0]) / fw, 8), round((anchor_px[1] - crop[1]) / fh, 8)]
    if not (0 <= anchor[0] <= 1 and 0 <= anchor[1] <= 1):
        raise SystemExit('Transformed nozzle anchor is outside crop: ' + str(anchor))
    cooked = [im.crop(crop) for im in cooked_full]
    atlas = Image.new('RGBA', (fw * 6, fh * 4))
    bounds = []
    alpha_max = []
    edge_max = []
    for i, im in enumerate(cooked):
        atlas.paste(im, ((i % 6) * fw, (i // 6) * fh))
        a = np.asarray(im)[..., 3]
        yy, xx = np.where(a > 16)
        bounds.append([int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)] if xx.size else None)
        alpha_max.append(int(a.max()))
        edge_max.append(int(max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max())))
    if any(b is None for b in bounds) or min(alpha_max) < 64:
        raise SystemExit(f'Blank/weak-alpha rendered frames for {effect}: {alpha_max}')
    if max(edge_max) > 3:
        raise SystemExit(f'Canvas boundary alpha leak for {effect}: {edge_max}')
    output = ROOT / 'staged' / 'assets' / 'vfx' / cue
    output.mkdir(parents=True, exist_ok=True)
    sheet_path = output / (cue + '_sheet.png')
    atlas.save(sheet_path, optimize=True)
    meta = {'schema': 1, 'cue': cue, 'fw': fw, 'fh': fh, 'cols': 6, 'rows': 4, 'total': 24, 'fps': 24.0, 'loop': True, 'units': units, 'anchor': anchor, 'loop_blend': 4, 'raw_frames': 28, 'seam_z_raw': seam(raw), 'seam_z': seam(cooked), 'packing_revision': 2, 'common_crop': crop, 'source_canvas': [384, 384], 'source_anchor': old_anchor, 'crop_alpha_threshold': 2, 'crop_margin_px': 8, 'source_alpha_union': union, 'rgba': True, 'seed': 680, 'method': 'Blender Eevee procedural 3D participating volume, periodic 4D density and emission; not fluid simulation', 'axis': 'sheet +X right, +Y down; fire nozzle right/tail left; sal centered', 'frame_alpha_bounds_gt16': bounds, 'frame_alpha_max': alpha_max, 'canvas_edge_alpha_max': max(edge_max)}
    (output / (cue + '_meta.json')).write_text(json.dumps(meta, indent=2), encoding='utf-8')
    size = sheet_path.stat().st_size
    if size >= 10 * 1024 * 1024:
        raise SystemExit(f'Sheet exceeds 10MiB: {size}')
    # Native raster preview on neutral dark background, with actual RGBA compositing.
    contact = Image.new('RGB', (6 * 192, 4 * 212), (20, 18, 25))
    draw = ImageDraw.Draw(contact)
    for i, im in enumerate(cooked):
        tile = Image.new('RGBA', (192, 192), (20, 18, 25, 255))
        tile.alpha_composite(im.resize((192, 192), Image.Resampling.LANCZOS))
        contact.paste(tile.convert('RGB'), ((i % 6) * 192, (i // 6) * 212))
        draw.text(((i % 6) * 192 + 8, (i // 6) * 212 + 193), f'{effect} {i:02d}', fill=(210, 205, 217))
    contact.save(ROOT / 'previews' / (effect + '_contact.jpg'), quality=90)
    reports.append({'effect': effect, 'path': str(sheet_path), 'bytes': size, 'sha256': hashlib.sha256(sheet_path.read_bytes()).hexdigest(), 'seam_z': meta['seam_z'], 'alpha_max_min': min(alpha_max), 'edge_alpha': max(edge_max), 'fw': fw, 'fh': fh, 'common_crop': crop, 'anchor': anchor, 'source_alpha_union': union})
(ROOT / 'pack_report.json').write_text(json.dumps(reports, indent=2), encoding='utf-8')
for record in reports:
    print('ATLAS_READY ' + json.dumps(record), flush=True)
