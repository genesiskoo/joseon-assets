from pathlib import Path
import json, shutil
root = Path('C:/workspace/joseon-assets/workbench/vfx/680_blender_vfx_test')
backup = root / 'revisions' / 'pack_v1'
backup.mkdir(parents=True, exist_ok=True)
paths = [root / 'manifest.json', root / 'README.md', root / 'pack_report.json', root / 'source' / 'pack_atlases.py', root / 'source' / 'finalize_report.py', root / 'previews' / 'fire_contact.jpg', root / 'previews' / 'sal_contact.jpg']
paths += [p for p in (root / 'staged').rglob('*') if p.is_file()]
for source in paths:
    destination = backup / source.relative_to(root)
    if destination.exists():
        raise SystemExit('Immutable packing v1 backup already exists: ' + str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
path = root / 'source' / 'pack_atlases.py'
text = path.read_text(encoding='utf-8-sig')
text = text.replace('Fixed full canvas is the common crop; alpha padding and emitter anchors never move.', 'Revision2: fixed alpha-union common crop; original RGBA data unchanged, anchor transformed from original384 canvas.')
old = '''    cooked = blend_loop(raw)
    atlas = Image.new('RGBA', (384 * 6, 384 * 4))'''
new = '''    cooked_full = blend_loop(raw)
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
    atlas = Image.new('RGBA', (fw * 6, fh * 4))'''
if old not in text:
    raise SystemExit('Packing source expected fixed canvas block absent')
text = text.replace(old, new)
text = text.replace("((i % 6) * 384, (i // 6) * 384)", "((i % 6) * fw, (i // 6) * fh)")
text = text.replace("'fw': 384, 'fh': 384", "'fw': fw, 'fh': fh")
text = text.replace("'common_crop': [0, 0, 384, 384]", "'packing_revision': 2, 'common_crop': crop, 'source_canvas': [384, 384], 'source_anchor': old_anchor, 'crop_alpha_threshold': 2, 'crop_margin_px': 8, 'source_alpha_union': union")
text = text.replace("'edge_alpha': max(edge_max)", "'edge_alpha': max(edge_max), 'fw': fw, 'fh': fh, 'common_crop': crop, 'anchor': anchor, 'source_alpha_union': union")
path.write_text(text, encoding='utf-8')
print('PACKING_REVISION2_SOURCE_READY')
