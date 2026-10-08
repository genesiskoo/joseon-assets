"""Read-only native portrait/geometry metrics, using the actual intake contract; no pixel edits."""
import hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
root = Path('C:/workspace/joseon')
spec = importlib.util.spec_from_file_location('portrait_contract', root / 'tools/portrait_intake.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
records = {r['id']: r for r in json.loads((root / '._tmp/624_generation_registry.json').read_text(encoding='utf-8'))}
for p in sorted((root / '._tmp/624_generation_parts').glob('*.json')):
    r = json.loads(p.read_text(encoding='utf-8'))
    records[r['id']] = r
out = {'card': 624, 'alpha_modified': False, 'metrics': {}, 'sets': {}}
arrays = {}
for key, r in records.items():
    p = Path(r['native_path'])
    im = Image.open(p)
    a = np.asarray(im.convert('RGBA'))
    alpha = a[...,3]
    vis = alpha > contract.ALPHA_THR
    b = contract.bbox(vis)
    side_rows = np.nonzero(vis[:,0] | vis[:,-1])[0].tolist()
    from PIL import ImageFilter
    interior = np.asarray(Image.fromarray((vis*255).astype('uint8')).filter(ImageFilter.MinFilter(31))) > 0
    core_values = alpha[interior]
    item = {'native_path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
            'bytes': p.stat().st_size, 'mode': im.mode, 'size': list(im.size),
            'alpha_min_max': [int(alpha.min()), int(alpha.max())],
            'alpha_255_pixels': int((alpha==255).sum()),
            'core_alpha_254_pixels': int((alpha==254).sum()),
            'interior_alpha_quantiles_0_10_50_90_100': np.quantile(core_values,[0,.1,.5,.9,1]).tolist() if core_values.size else [],
            'clear_pct': round(float((alpha==0).mean())*100, 4),
            'bbox16': b, 'head_top_pct16': round(b[1] / im.height*100, 4),
            'head_contract_pass': abs(b[1]/im.height - contract.TOP_RATIO) <= contract.TOP_TOL,
            'side_contract_pass': b[0] >= contract.SIDE_MIN and b[2] <= im.width-contract.SIDE_MIN,
            'side_touch_rows': [min(side_rows), max(side_rows)] if side_rows else [],
            'waist_width_pct': round(float(vis[int(contract.WAIST_ROW*im.height)].mean())*100,4)}
    try:
        contract.measure(str(p))
        item['intake_measure'] = {'pass': True}
    except contract.Reject as e:
        item['intake_measure'] = {'pass': False, 'code': e.code, 'message': str(e)}
    out['metrics'][key] = item
    arrays[key] = a
pairs = [('shaman_A_neutral_r3','shaman_A_serious_r1'),
         ('shaman_B_neutral_r1','shaman_B_serious_r1'),
         ('shaman_B_neutral_r1','shaman_B_serious_r2'),
         ('shaman_B_neutral_r1','shaman_B_serious_r3'),
         ('jumo_A_neutral_r2','jumo_A_smile_r1'),
         ('jumo_B_neutral_r1','jumo_B_smile_r1'),
         ('elder_A_neutral_r2','elder_A_smile_r1'),
         ('elder_B_neutral_r1','elder_B_smile_r1')]
for neutral, expr in pairs:
    if neutral not in arrays or expr not in arrays:
        continue
    n, e = arrays[neutral], arrays[expr]
    nb, eb = contract.bbox(n[...,3]>16), contract.bbox(e[...,3]>16)
    iou = contract.iou(n[...,3]>16,e[...,3]>16)
    dtop = abs(nb[1]-eb[1])
    dcx = abs((nb[0]+nb[2]-eb[0]-eb[2])/2)
    # The lower half is outside all faces. Diagnostic only, not a claim of exact pixel invariance.
    mask = (n[768:,:,3]>128)&(e[768:,:,3]>128)
    delta = np.abs(n[768:,:,:3].astype(float)-e[768:,:,:3].astype(float))
    out['sets'][neutral+' / '+expr] = {'alpha16_iou': round(iou,6), 'top_delta_px': dtop,
         'center_delta_px': dcx,
         'lower_body_rgb_mae': round(float(delta[mask].mean()),4) if mask.any() else None,
         'geometry_pass': iou>=contract.SET_IOU and dtop<=contract.SET_TOL_PX and dcx<=contract.SET_TOL_PX}
target=root/'._tmp/624_contract_qa.json'
target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(out['metrics']),'native_bytes':sum(m['bytes'] for m in out['metrics'].values()),'sets':out['sets'],'intake_pass_count':sum(m['intake_measure']['pass'] for m in out['metrics'].values())},ensure_ascii=False))
