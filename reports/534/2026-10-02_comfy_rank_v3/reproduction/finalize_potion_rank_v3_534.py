"""Freeze the #534 revision, preserve old gallery bytes, and audit candidate-only output."""
import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path('C:/workspace/joseon')
ASSET = ROOT / '._tmp/assets_534'
BASE = ASSET / 'workbench/production/item_icons_534'
HERE = BASE / 'rank_v3_2026-10-02'
REPORT = ASSET / 'reports/534/2026-10-02_comfy_rank_v3'
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/534-potion-grade-art/joseon')
GALLERY = GAME / 'docs/art/534_potion_grade'
SPEC = importlib.util.spec_from_file_location('old534', BASE / 'prepare_534.py')
old = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(old)
SCAN_SPEC = importlib.util.spec_from_file_location('scan534', BASE / 'audit_receipts_534.py')
scan = importlib.util.module_from_spec(SCAN_SPEC)
# The preserved scanner imports its sibling without credentials or network calls.
import sys
sys.path.insert(0, str(BASE))
SCAN_SPEC.loader.exec_module(scan)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    if (HERE / 'verification.json').exists():
        raise SystemExit('Frozen verification already exists; inspect instead of overwriting it.')
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    before = json.loads((HERE / 'runtime_before.json').read_text(encoding='utf-8'))
    current = old.snapshot(GAME)
    assert current == before and len(current) == 191
    checks = []
    for row in manifest['references'] + manifest['items']:
        uid, stage = row['item_id'], int(row['efficacy_stage'])
        family = row['resource']
        definition = GAME / f'data/items/{uid}.tres'
        body = definition.read_text(encoding='utf-8')
        assert sha(definition) == row['definition_sha256']
        assert old.scalar(body, 'slot') == '6' and int(old.scalar(body, 'tier', '1')) == 1
        assert old.scalar(body, 'size') == 'Vector2i(1, 1)' and int(old.scalar(body, 'max_stack')) == 10
        assert int(old.scalar(body, 'consumable')) == (1 if family == 'hp' else 2)
        assert float(old.scalar(body, 'power')) == row['power']
        assert int(old.scalar(body, 'min_ilvl')) == row['min_ilvl']
        assert f'path="res://assets/sprites/ui/icons_a/items/{family}_potion.png"' in body
        assert row['display_scale'] == {1: .75, 2: 62 / 72, 3: 1.0}[stage]
        source = HERE / row['source_path']
        assert sha(source) == row['source_sha256']
        record = dict(item_id=uid, efficacy_stage=stage, power=row['power'], min_ilvl=row['min_ilvl'],
                      definition_sha256=sha(definition), source_sha256=sha(source), display_scale=row['display_scale'])
        if stage == 1:
            assert sha(GAME / f'assets/sprites/ui/icons_a/items/{family}_potion.png') == row['runtime_sha256']
            assert sha(HERE / row['runtime_snapshot_path']) == row['runtime_sha256']
            assert sha(BASE / f'refs/{family}_potion_basic.png') == row['source_sha256']
            record['basic_original_and_runtime_unchanged'] = True
            packed_path = HERE / row['candidate_game_path']
            assert sha(packed_path) == row['candidate_sha256']
        else:
            native = HERE / row['generated_path']
            assert sha(native) == row['generated_sha256']
            raw = np.asarray(Image.open(native).convert('RGBA'))
            clean = np.asarray(Image.open(source).convert('RGBA'))
            assert raw.shape == clean.shape == (1024, 1024, 4)
            assert np.array_equal(raw[:, :, :3], clean[:, :, :3])
            assert (int(clean[:, :, 3].min()), int(clean[:, :, 3].max())) == (0, 255)
            job_path = REPORT / f'{uid}_rank_v3.job.json'
            job = json.loads(job_path.read_text(encoding='utf-8'))
            assert job['state'] == 'downloaded' and job['reference_images'] == []
            assert job['prompt_id'] == row['cloud_prompt_id']
            assert sha(REPORT / job['raw_output']) == sha(native) == job['raw_output_sha256']
            assert sha(REPORT / job['output']) == sha(source) == job['output_sha256']
            record.update(rgb_pixels_changed=0, clean_alpha=[0, 255], cloud_prompt_id=job['prompt_id'],
                          reference_uploads=0, generated_sha256=sha(native))
            packed_path = HERE / row['game_path']
            assert sha(packed_path) == row['game_sha256']
        packed = Image.open(packed_path)
        assert packed.mode == 'RGBA' and packed.size == (80, 80)
        record.update(packed_sha256=sha(packed_path), packed_bbox=list(packed.getchannel('A').getbbox()))
        checks.append(record)

    # Preserve old six-review gallery byte-for-byte before writing the revised six.
    prior = REPORT / 'previous_gallery'
    assert len(list(prior.glob('*.jpg'))) == 6
    for path in GALLERY.glob('*.jpg'):
        assert (prior / path.name).is_file() and sha(path) == sha(prior / path.name)
    gallery_plan = [('before_overview.jpg', prior / 'overview.jpg'),
                    ('overview.jpg', HERE / 'qa/godot_overview.png'),
                    ('before_actual.jpg', prior / 'actual.jpg'),
                    ('actual.jpg', HERE / 'qa/godot_actual.png'),
                    ('belt_stress.jpg', HERE / 'qa/godot_belt_stress.png'),
                    ('blind.jpg', HERE / 'qa/godot_blind.png')]
    assert Image.open(prior / 'overview.jpg').size == Image.open(HERE / 'qa/godot_overview.png').size
    assert Image.open(prior / 'actual.jpg').size == Image.open(HERE / 'qa/godot_actual.png').size
    gallery = []
    for name, source in gallery_plan:
        target = GALLERY / name
        if source.suffix == '.jpg':
            shutil.copy2(source, target)
        else:
            image = Image.open(source).convert('RGB')
            assert image.width == 1280
            image.save(target, quality=87, optimize=True)
        assert target.stat().st_size <= 300_000 and Image.open(target).width == 1280
        gallery.append(dict(name=name, source=source.relative_to(ASSET).as_posix(),
                            bytes=target.stat().st_size, sha256=sha(target)))
    obsolete = GALLERY / 'alpha_comparison.jpg'
    assert obsolete.resolve().parent == GALLERY.resolve()
    assert sha(obsolete) == sha(prior / obsolete.name)
    obsolete.unlink()
    assert len(list(GALLERY.glob('*.jpg'))) == 6
    assert old.snapshot(GAME) == before

    rendering = []
    for mode in ('overview', 'actual', 'belt_stress', 'black', 'grayscale', 'blind'):
        stdout, stderr = REPORT / f'{mode}.stdout.raw.log', REPORT / f'{mode}.stderr.raw.log'
        raw = stdout.read_bytes() + stderr.read_bytes()
        marker = f'GODOT_534_PASS mode={mode} items=6 candidate4/scale_proposal'.encode()
        assert marker in raw and b'SCRIPT ERROR' not in raw and b'ERROR:' not in raw
        png = HERE / f'qa/godot_{mode}.png'
        assert Image.open(png).size == (1280, 960)
        rendering.append(dict(mode=mode, status='PASS', png_sha256=sha(png),
                              stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
    failure = (REPORT / 'import.stdout.raw.log').read_bytes() + (REPORT / 'import.stderr.raw.log').read_bytes()
    assert b'Could not resolve external class member "OPENING"' in failure
    retry = (REPORT / 'import_cache_retry1.stdout.raw.log').read_bytes() + (REPORT / 'import_cache_retry1.stderr.raw.log').read_bytes()
    assert b'SCRIPT ERROR' not in retry and b'ERROR:' not in retry
    (REPORT / '.gitattributes').write_text('** -text -whitespace\n', encoding='utf-8', newline='\n')

    frozen = REPORT / 'reproduction'
    frozen.mkdir()
    helpers = ['prepare_potion_rank_v3_534.py', 'pack_potion_rank_v3_534.py',
               'inspect_rank_v3_alpha_534.py', 'render_potion_rank_v3_534.py',
               'render_blind_rank_v3_534.py', 'finalize_potion_rank_v3_534.py',
               'comfy_bounded_queue.py', 'comfy_image_production.py', 'comfy_516_api.py']
    for name in helpers:
        source = ROOT / '._tmp' / name
        shutil.copy2(source, frozen / name)
        assert sha(source) == sha(frozen / name)

    readme = '''# #534 단계 위계 보완 R3 — 2026-10-02

PD의 단계별 판독 피드백으로 상위 HP/MP 4장을 새로 제작했다. 기본2 승인 원화와 현재 게임 PNG·정의·UI는 보존했다. 후보이며 아직 채택/실반입되지 않았다. 이전 R2 생산물은 상위 폴더와 보고서에 유지하고, 이전 게임 JPG6은 보고서 previous_gallery에 바이트 그대로 보존했다.

단계1 소박한 병 → 단계2 넓은 몸통·목재 마개·금속 봉인1줄 → 단계3 육중한 몸통·금속 뚜껑·봉인2줄과 큰 문장. HP는 적갈색 약단지/붉은 끈, MP는 청자 이중 호리병/남색 끈 계열이다. 현재 모든 효능 단계는 ItemDef.tier1/1×1/스택10이며 HP40/80/140·MP25/50/90·ilvl1/6/13을 유지한다.

Comfy Cloud GPT Image 2.5 Flare high 1024² 텍스트 생성4회 + 같은 그래프 BiRefNet-general 알파 분리. 기존 이미지 업로드0. native/clean RGB 차이0, clean alpha0~255. 정확한 prompt/API graph/job ID/history/native/clean PNG와 SHA를 reports/534/2026-10-02_comfy_rank_v3에 보존했다. alpha 수정·수작업 픽셀 그리기·등급 배경·글자·발광은 사용하지 않았다. production game/items의 80px 패킹은 premultiplied Lanczos로 비율을 유지한다.

중요: 현 UiSkin은 알파 여백을 제거하므로 PNG 여백만으로 크기 위계가 적용되지 않는다. 검수판은 현재 UiSkin을 호출하면서 미리보기의 표시 영역에만 단계별0.75/0.86/1.0을 적용했다. 이 정책은 프로덕션 UI에 아직 설치하지 않았다. 채택 뒤 별도 반입 카드에서 아이콘4 연결과 같은 표시 비율을 가방·좌판·벨트·커서에 함께 적용하고 실제 입력·수치·다른 그림 보존을 검수해야 한다. 기본 PNG는 교체할 필요가 없다.

검수: 현 가방40/여백8, 좌판48/여백3, 벨트42/여백8, 축소30/36, 검정·무채색, 이름/숫자를 숨겨 섞은 판6모드. 자동 PASS는 파일 계약과 렌더 실행이며 사람의 판독 정확도를 측정한 결과가 아니다. 매우 작은30px 검수에서 미세 문장·끈은 약하므로 크기·마개·굵은 봉인을 주요 식별점으로 삼는다. JPG6은 게임 docs/art/534_potion_grade에 보존한다.

처음 임포트의 OPENING class-cache 오류는 raw stdout/stderr 전문을 별도로 보존했다. 추가 코드 수정 없이 두 번째 import_cache_retry1이 통과했고 이후6모드는 SCRIPT ERROR/ERROR0이다. runtime_before.json과 verification.json은 그림·정의·UI191파일 SHA 불변, 원본/패킹/SHA, 각 렌더 로그를 대조한다.

재현 자료: qa_godot.gd/qa_godot_blind.gd는 현재 UiSkin·기존 ItemDef를 로드한다. renderer는 정확한 작업 트리/생산 경로와 Godot 실행 파일을 상수로 사용한다. 보고서 reproduction에 당시 준비·큐·생성·패킹·렌더·검증 Python 원본을 그대로 동결했으며 다른 컴퓨터에서는 상수를 실제 경로로 바꿔야 한다. 기존 cloud job을 다시 제출하지 않는다. 같은 이름의 원본·로그·검증 파일이 있으면 준비/렌더/동결 스크립트가 중단한다. 새 검수가 필요하면 별도 run label/출력 폴더로 보존한다.

왜 이 구조인가: 작은 슬롯에서도 부피와 금속 봉인이라는 독립 단서가 남도록 원화와 실제 표시 비율을 함께 고정한다. 패킹 여백만 늘리는 대안은 현 UiSkin에서 효과가 없고 회복 수치 변경은 이 시각 피드백의 범위를 벗어나므로 사용하지 않는다.
'''
    (HERE / 'README.md').write_text(readme, encoding='utf-8', newline='\n')
    result = dict(card=534, revision='rank_v3', status='PASS', adoption='pending_PD', runtime_intake=False,
                  runtime_scale_policy_installed=False, runtime_files_unchanged=len(current),
                  runtime_before_sha256=sha(HERE / 'runtime_before.json'), original_basic_sources_unchanged=2,
                  item_definitions_unchanged=6, generated_candidates=4, reference_uploads=0,
                  model=json.loads((HERE / 'generation_plan.json').read_text(encoding='utf-8'))['model'],
                  items=checks, render_modes=rendering, gallery=gallery,
                  initial_import='FAIL: existing OPENING class cache; raw retained', import_cache_retry1='PASS',
                  readout='Visual review only; no measured human classification accuracy.',
                  packing_only_cannot_change_ui_size=True,
                  scale_policy={'1': .75, '2': 62 / 72, '3': 1.0}, gameplay_values_changed=False)
    save_json(HERE / 'verification.json', result)

    # Scan only this revision, including the native PNG metadata and raw logs.
    findings, checked = [], []
    secret_fields = re.compile(r'^(?:api[_-]?key(?:_comfy_org)?|authorization|password|secret|access[_-]?token|refresh[_-]?token|cookie|client[_-]?secret)$', re.I)

    def inspect_fields(value, location):
        if isinstance(value, dict):
            for key, child in value.items():
                if secret_fields.fullmatch(key) and child not in [None, '', False, '<redacted>', 'REDACTED', '***']:
                    findings.append(dict(location=location + '/' + key, reason='Credential field; value not printed'))
                inspect_fields(child, location + '/' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                inspect_fields(child, location + '/' + str(index))

    for folder in (HERE, REPORT):
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            rel = path.relative_to(ASSET).as_posix()
            text = None
            if path.suffix.lower() in ('.json', '.txt', '.md', '.py', '.gd', '.ps1', '.log'):
                text = path.read_bytes().decode('utf-8-sig', errors='replace')
                if path.suffix == '.json':
                    inspect_fields(json.loads(text), rel)
            elif path.suffix.lower() == '.png':
                info = Image.open(path).info
                text = json.dumps(info, default=str)
                for key, value in info.items():
                    if isinstance(value, str):
                        try:
                            inspect_fields(json.loads(value), rel + '/png_metadata/' + key)
                        except json.JSONDecodeError:
                            pass
            if text is None:
                continue
            if scan.TOKEN_VALUE.search(text):
                findings.append(dict(location=rel, reason='Credential pattern; value not printed'))
            if scan.SIGNED_URL.search(text):
                findings.append(dict(location=rel, reason='Credential URL query; value not printed'))
            checked.append(dict(path=rel, sha256=sha(path)))
    audit = dict(card=534, status='PASS' if not findings else 'FAIL', checked_files=len(checked),
                 credential_fields_or_tokens_or_signed_urls=len(findings), findings=findings,
                 checked=checked, png_metadata_included=True, secret_values_printed=False)
    save_json(REPORT / 'receipt_audit.json', audit)
    assert not findings, 'Inspect local audit findings without printing values.'
    print('PASS #534 R3: runtime191/basic2/definitions6 unchanged; raw4/clean4 RGB equal; alpha0..255.')
    print('PASS UiSkin six modes; initial cache error/retry logs retained; JPG6 <=300KB/1280px; candidate only.')
    print(f'PASS credential scan: {len(checked)} revision text/JSON/raw/PNG metadata files; findings0.')


if __name__ == '__main__':
    main()
