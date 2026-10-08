import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ASSET = Path('C:/workspace/joseon/._tmp/assets_534')
BASE = ASSET / 'workbench/production/item_icons_534'
HERE = BASE / 'rank_v3_2026-10-02'
REPORT = ASSET / 'reports/534/2026-10-02_comfy_rank_v3'
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/534-potion-grade-art/joseon')
spec = importlib.util.spec_from_file_location('old_potion_pack', BASE / 'prepare_534.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def contain(image, edge):
    bounds = image.getchannel('A').getbbox()
    assert bounds
    cropped = image.crop(bounds)
    factor = edge / max(cropped.size)
    scaled = cropped.convert('RGBa').resize((round(cropped.width * factor), round(cropped.height * factor)), Image.Resampling.LANCZOS).convert('RGBA')
    canvas = Image.new('RGBA', (80, 80))
    canvas.alpha_composite(scaled, ((80 - scaled.width) // 2, (80 - scaled.height) // 2))
    return canvas, list(bounds)


def main():
    if (HERE / 'manifest.json').exists():
        raise SystemExit('Existing packed revision must not be overwritten.')
    source = json.loads((BASE / 'inputs.json').read_text(encoding='utf-8'))
    result = copy.deepcopy(source)
    plan = json.loads((HERE / 'generation_plan.json').read_text(encoding='utf-8'))
    result.update({'date_kst': '2026-10-02', 'revision': 'rank_v3', 'status': 'candidate_not_installed',
                   'runtime_scale_policy_installed': False, 'display_scale_by_stage': {'1': .75, '2': 62 / 72, '3': 1.0},
                   'packing_only_cannot_change_ui_size': True, 'candidate_renderer': 'Current UiSkin plus proposed per-potion inner-rectangle scale; no production UI code changed.',
                   'manual_pixel_editing': False, 'manual_alpha_editing': False, 'production_alpha_thresholding': False})
    save_json(HERE / 'runtime_before.json', old.snapshot(GAME))
    prior = REPORT / 'previous_gallery'
    prior.mkdir()
    for path in (GAME / 'docs/art/534_potion_grade').glob('*.jpg'):
        shutil.copy2(path, prior / path.name)
    for directory in ('source/items', 'source/reference_runtime', 'game/items', 'qa'):
        (HERE / directory).mkdir(parents=True, exist_ok=True)
    for row in result['references']:
        family, uid = row['resource'], row['item_id']
        native = BASE / row['source_path']
        runtime = GAME / f'assets/sprites/ui/icons_a/items/{family}_potion.png'
        assert sha(native) == row['source_sha256'] and sha(runtime) == row['runtime_sha256']
        assert sha(GAME / f'data/items/{uid}.tres') == row['definition_sha256']
        native_dest = HERE / f'source/items/{uid}_native_reference.png'
        runtime_dest = HERE / f'source/reference_runtime/{uid}.png'
        shutil.copy2(native, native_dest)
        shutil.copy2(runtime, runtime_dest)
        packed, bounds = contain(Image.open(runtime).convert('RGBA'), 54)
        path = HERE / f'game/items/{uid}.png'
        packed.save(path, optimize=True)
        row.update({'source_path': native_dest.relative_to(HERE).as_posix(),
                    'runtime_snapshot_path': runtime_dest.relative_to(HERE).as_posix(),
                    'candidate_game_path': path.relative_to(HERE).as_posix(), 'candidate_sha256': sha(path),
                    'candidate_packing_source': runtime_dest.relative_to(HERE).as_posix(), 'source_crop': bounds,
                    'target_long_edge_px': 54, 'display_scale': .75})
    for row in result['items']:
        uid = row['item_id']
        definition = GAME / f'data/items/{uid}.tres'
        assert sha(definition) == row['definition_sha256']
        contract = next(x['contract'] for x in plan['jobs'] if x['id'] == uid + '_rank_v3')
        assert contract['tier'] == 1 and contract['max_stack'] == 10 and contract['restores'] == row['power']
        job = json.loads((REPORT / f'{uid}_rank_v3.job.json').read_text(encoding='utf-8'))
        assert job['state'] == 'downloaded' and not job['reference_images']
        native, clean = REPORT / job['raw_output'], REPORT / job['output']
        assert sha(native) == job['raw_output_sha256'] and sha(clean) == job['output_sha256']
        raw_pixels = np.asarray(Image.open(native).convert('RGBA'))
        clean_image = Image.open(clean).convert('RGBA')
        assert clean_image.size == (1024, 1024) and clean_image.getchannel('A').getextrema() == (0, 255)
        assert np.array_equal(raw_pixels[:, :, :3], np.asarray(clean_image)[:, :, :3]), 'Segmentation may not redraw materials.'
        native_dest, clean_dest = HERE / f'source/items/{uid}_generated.png', HERE / f'source/items/{uid}.png'
        shutil.copy2(native, native_dest)
        shutil.copy2(clean, clean_dest)
        stage = int(row['efficacy_stage'])
        edge = 62 if stage == 2 else 72
        packed, bounds = contain(clean_image, edge)
        path = HERE / f'game/items/{uid}.png'
        packed.save(path, optimize=True)
        row.update({'generated_path': native_dest.relative_to(HERE).as_posix(), 'generated_sha256': sha(native_dest),
                    'source_path': clean_dest.relative_to(HERE).as_posix(), 'source_sha256': sha(clean_dest),
                    'game_path': path.relative_to(HERE).as_posix(), 'game_sha256': sha(path), 'game_size': [80, 80],
                    'source_crop': bounds, 'visible_bbox': list(packed.getchannel('A').getbbox()),
                    'target_long_edge_px': edge, 'display_scale': edge / 72,
                    'rgb_pixels_changed_by_segmentation': 0, 'cloud_prompt_id': job['prompt_id']})
    assert old.snapshot(GAME) == json.loads((HERE / 'runtime_before.json').read_text(encoding='utf-8'))
    save_json(HERE / 'manifest.json', result)
    renderer = (BASE / 'qa_godot.gd').read_text(encoding='utf-8')
    renderer = renderer.replace('assert(skin.item_icon(self, rect, tex, 1.0, padding))',
        'var shrink := minf(rect.size.x - padding * 2.0, rect.size.y - padding * 2.0) * (1.0 - float(row.spec.display_scale)) * 0.5\n\t\tassert(skin.item_icon(self, rect, tex, 1.0, padding + shrink))')
    renderer = renderer.replace('assert(skin.item_icon(self, Rect2(x + 28, y + 44, 347, 229), row.source, 1.0, 0.0))',
        'var large_pad: float = 229.0 * (1.0 - float(row.spec.display_scale)) * 0.5\n\t\t\t\tassert(skin.item_icon(self, Rect2(x + 28, y + 44, 347, 229), row.source, 1.0, large_pad))')
    renderer = renderer.replace('spec.runtime_snapshot_path if basic else spec.game_path', 'spec.candidate_game_path if basic else spec.game_path')
    renderer = renderer.replace('기존 80 출력 보존', '기본 원화 · 크기 후보')
    renderer = renderer.replace('UiSkin.item_icon 실제 경로·선형 필터·비율 보존 / 기존 정의·기본 그림 유지 / 후보 미반입',
        '현재 UiSkin + 물약별 표시비율 후보 0.75 / 0.86 / 1.0 · 게임 미반입')
    renderer = renderer.replace('80px 출력의 여백은 6px(8% 반올림). 30/36은 현 42px 벨트의 축소 스트레스 검수다.',
        '투명 여백은 UI가 제거함: 표시비율 별도 반입 필요 · 30/36은 벨트 축소 검수')
    renderer = renderer.replace('card534', 'card534rankv3')
    renderer = renderer.replace('qa534/', 'qa534rankv3/')
    renderer = renderer.replace(' items=6 candidate4/existing1x1', ' items=6 candidate4/scale_proposal/existing1x1')
    (HERE / 'qa_godot.gd').write_text(renderer, encoding='utf-8', newline='\n')
    print(f'Packed new4 + scaled basic2 candidates; preserved runtime {len(old.snapshot(GAME))} files and all old JPG6.')
    print('NOTE: Per-rank preview scale is a proposal; current UiSkin ignores PNG margins. No runtime UI policy installed.')


if __name__ == '__main__':
    main()
