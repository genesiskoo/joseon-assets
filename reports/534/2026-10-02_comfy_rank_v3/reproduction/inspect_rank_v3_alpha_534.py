import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path('C:/workspace/joseon/._tmp/assets_534/reports/534/2026-10-02_comfy_rank_v3')
rows = []
for item in ('hp_potion_2', 'hp_potion_3', 'mp_potion_2', 'mp_potion_3'):
    images = {}
    for suffix in ('_rank_v3_raw.png', '_rank_v3.png'):
        pic = Image.open(ROOT / (item + suffix)).convert('RGBA')
        pixels = np.asarray(pic)
        images[suffix] = {'bbox': pic.getchannel('A').getbbox(), 'alpha_extrema': pic.getchannel('A').getextrema(),
                         'samples': {str((x, y)): int(pixels[y, x, 3]) for x, y in ((0, 0), (50, 50), (512, 25), (512, 80), (80, 512), (950, 512))},
                         'pixels_alpha_gt16': int(np.count_nonzero(pixels[:, :, 3] > 16)),
                         'pixels_alpha_gt128': int(np.count_nonzero(pixels[:, :, 3] > 128))}
    rows.append({'item': item, 'images': images})
(ROOT / 'alpha_inspection.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
print(json.dumps(rows, indent=2))
