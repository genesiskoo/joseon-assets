from pathlib import Path
from PIL import Image
import hashlib
import json
import sys

mode = sys.argv[1]
assert mode in ('before', 'after')
user = Path(r'C:\Users\FORYOUCOM\AppData\Roaming\Godot\app_userdata\Joseon Hunters\wt\codex-293-monster-elite-ui\e2e')
game = Path(r'C:\Users\FORYOUCOM\.codex\worktrees\293-monster-elite-ui\joseon')
assets = Path(r'C:\Users\FORYOUCOM\.codex\worktrees\393-ui-icon-redesign\joseon-assets')
report = assets / 'reports/447/integration_2026-09-27'
gallery = game / 'docs/art/447_d1_icons_intake'
report.mkdir(parents=True, exist_ok=True)
gallery.mkdir(parents=True, exist_ok=True)
records = []
for state in ['inventory', 'held_swap', 'skills_sword', 'skills_body', 'skills_talisman',
        't1_inventory', 't1_held', 't1_vendor_tooltip']:
    candidates = list(user.glob(f'icon_intake_*_{state}.png'))
    assert candidates, state
    source = max(candidates, key=lambda p: p.stat().st_mtime)
    raw = report / f'{state}_{mode}.png'
    raw.write_bytes(source.read_bytes())
    if state.startswith('t1_'):
        im = Image.open(raw).convert('RGB')
        im.thumbnail((1280, 720), Image.Resampling.LANCZOS)
        jpg = gallery / f'{state}_{mode}.jpg'
        im.save(jpg, quality=85, optimize=True)
        assert im.width == 1280 and jpg.stat().st_size <= 300_000
        (report / jpg.name).write_bytes(jpg.read_bytes())
    records.append({'state': state, 'source': str(source), 'mtime': source.stat().st_mtime,
        'sha256': hashlib.sha256(raw.read_bytes()).hexdigest(), 'size': list(Image.open(raw).size)})
(report / f'captures_{mode}.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
for name in [f'447_{mode}.log', f'447_{mode}_errors.log']:
    p = Path(r'C:\workspace\joseon\tmp') / name
    if p.exists():
        (report / name).write_bytes(p.read_bytes())
print(f'{mode}: 8 raw frames retained; 3 gallery JPG, width1280/<=300KB.')
