"""Merge approved art, reconcile the parent count, and record the next-work queue."""
import json
import shutil
from pathlib import Path

import approve_potion_534_queue as task
import land_potion_534_review as review
import finalize_potion_rank_v3_534 as audit

ROOT, GAME, ASSET, REPORT, PROD = task.ROOT, task.GAME, task.ASSET, task.REPORT, task.PROD
PRIMARY_ASSET = Path('C:/workspace/joseon-assets')


def step(state, key, *args):
    if key in state:
        return
    text = task.command(['python', 'tools/board.py', *args]).decode('utf-8', errors='replace')
    state[key] = text
    task.write(task.JOURNAL, state)
    print(text, flush=True)


def main():
    state = json.loads(task.JOURNAL.read_text(encoding='utf-8'))
    if state['phase'] == 'complete':
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    assert state['phase'] == 'game_landed'
    if 'asset_approved_commit' not in state:
        expected_prefixes = ['workbench/production/item_icons_534/rank_v3_2026-10-02/APPROVAL.json',
                             'reports/534/adoption_2026-10-02/']
        staged_before = task.git(ASSET, 'diff', '--cached', '--name-only').decode().splitlines()
        assert all(any(path == x or path.startswith(x) for x in expected_prefixes) for path in staged_before)
        changed = task.git(ASSET, 'status', '--porcelain=v1', '--untracked-files=all').decode().splitlines()
        assert all(any(row[3:] == x or row[3:].startswith(x) for x in expected_prefixes) for row in changed)
        assert review.art.snapshot(ROOT) == json.loads((REPORT / 'game_runtime_before.json').read_text(encoding='utf-8'))
        task.write(REPORT / 'acceptance.json', {'card': 534, 'adoption': 'approved',
                    'game_review_main': state['game_landed_commit'], 'runtime_intake': False,
                    'intake_card': state['intake_card'], 'current_title_unchanged': True,
                    'runtime_files_unchanged': state['game_runtime_files_unchanged'],
                    'parent_core_remaining_before': 25, 'parent_core_remaining_after': 21,
                    'validation': 'Same approved source/output SHA; six candidate render modes already PASS; review landing doc budget PASS.',
                    'native_landing_logs': 'land.stdout.raw.log / land.stderr.raw.log', 'push': False})
        for name in ['approve_potion_534_queue.py', 'land_potion_534_review.py', 'finish_potion_534_adoption_queue.py']:
            source, frozen = ROOT / '._tmp' / name, REPORT / name
            if frozen.exists() and task.sha(source) != task.sha(frozen):
                prior = REPORT / (frozen.stem + '_initial' + frozen.suffix)
                assert not prior.exists()
                shutil.copy2(frozen, prior)
            shutil.copy2(source, frozen)
        task.write(REPORT / 'receipt_guard_fix.json', {'card': 534,
                    'cause': 'Receipt inspection saw the literal deferred-marker character inside an archived Python helper.',
                    'fix': 'Apply the deferred-marker guard only to actual board.py command output, never git show file bytes.',
                    'initial_scripts_preserved': True, 'board_deferred_response_received': False,
                    'gameplay_or_art_modified': False})
        for path in [PROD / 'APPROVAL.json', *REPORT.rglob('*')]:
            if not path.is_file() or path.suffix.lower() not in ('.json', '.py', '.log'):
                continue
            text = path.read_bytes().decode('utf-8-sig', errors='replace')
            assert not audit.scan.TOKEN_VALUE.search(text) and not audit.scan.SIGNED_URL.search(text)
            findings = []
            if path.suffix == '.json':
                audit.scan.walk(json.loads(text), path.name, findings)
                assert not findings
        task.git(ASSET, 'add', '--', 'workbench/production/item_icons_534/rank_v3_2026-10-02/APPROVAL.json',
                 'reports/534/adoption_2026-10-02')
        exact = []
        for relative in task.git(ASSET, 'diff', '--cached', '--name-only', '-z').decode().split('\0'):
            if not relative:
                continue
            assert task.git(ASSET, 'show', ':' + relative) == (ASSET / relative).read_bytes()
            exact.append({'path': relative, 'sha256': task.sha(ASSET / relative)})
        task.write(REPORT / 'staged_byte_proof.json', {'card': 534, 'status': 'PASS', 'files': exact})
        task.git(ASSET, 'add', '--', 'reports/534/adoption_2026-10-02/staged_byte_proof.json')
        task.git(ASSET, 'diff', '--cached', '--check')
        task.git(ASSET, 'commit', '-m', 'art(#534): adopt potion R3 and preserve review landing proof')
        state['asset_approved_commit'] = task.git(ASSET, 'rev-parse', 'HEAD').decode().strip()
        task.write(task.JOURNAL, state)
    if 'asset_main_commit' not in state:
        assert task.git(PRIMARY_ASSET, 'branch', '--show-current').decode().strip() == 'main'
        assert not task.git(PRIMARY_ASSET, 'diff', '--name-only').strip()
        assert not task.git(PRIMARY_ASSET, 'diff', '--cached', '--name-only').strip()
        # Never clean or overwrite existing untracked models/audio/video in the primary asset checkout.
        current_untracked = set(task.git(PRIMARY_ASSET, 'ls-files', '--others', '--exclude-standard', '-z').decode().split('\0'))
        incoming = set(task.git(ASSET, 'diff', '--name-only', 'main...HEAD', '-z').decode().split('\0')) - {''}
        assert not current_untracked.intersection(incoming)
        task.git(ASSET, 'rebase', 'main')
        task.git(PRIMARY_ASSET, 'merge', '--ff-only', 'codex/534-potion-grades')
        state['asset_main_commit'] = task.git(PRIMARY_ASSET, 'rev-parse', 'HEAD').decode().strip()
        task.write(task.JOURNAL, state)
        final_prod = PRIMARY_ASSET / 'workbench/production/item_icons_534/rank_v3_2026-10-02'
        approval = json.loads((final_prod / 'APPROVAL.json').read_text(encoding='utf-8'))
        for item in approval['approved_items']:
            assert task.sha(final_prod / item['source_path']) == item['source_sha256']
            assert task.sha(final_prod / item['game_path']) == item['game_sha256']
        assert not task.git(ASSET, 'status', '--porcelain').strip()
    number = str(state['intake_card'])
    if 'state_commit' not in state:
        path = ROOT / 'docs/STATE.md'
        text = path.read_text(encoding='utf-8')
        old = next(line for line in text.splitlines() if line.startswith('- 2026-10-02 Codex: #274 옥20·호리병1'))
        text = text.replace(old, '- 2026-10-02 Codex: #534 물약R3 원화4·표시비율 PD채택, 검토판main' + state['game_landed_commit'][:8]
                            + '/원화assets' + state['asset_main_commit'][:8] + '. 게임반입 #' + number
                            + ' 이번주(1순위). #274 잔여21=옥20+호리병1. 기존191SHA/기본2/수치/타이틀 보존·실반입 전.')
        old = next(line for line in text.splitlines() if line.startswith('- Codex 남은 것:'))
        text = text.replace(old, '- Codex 남은 것: #' + number + ' 승인물약 실반입(이번주). #132 소품7·#519 보스5·#274 옥20/호리병1·#463 버전표시=PD확인. #273 홈/창3=#265/#266/#267 뒤. #536 후속 직접승인 대기, #545 타이틀 차후.')
        old = next(line for line in text.splitlines() if line.startswith('- 다음: Codex는 #534'))
        text = text.replace(old, '- 다음: Codex는 #' + number + '에서 승인 물약4 연결+표시 크기를 구현한다. 이번 지시는 다음 목록 요청이므로 카드 등록 후 대기. 다른 시안/검증 판정과 #273 선행은 유지, #545 현재 메인 보존.')
        assert len(text.encode('utf-8')) <= 16_000 and all(len(line) <= 300 for line in text.splitlines())
        assert not task.git(ROOT, 'diff', '--cached', '--name-only').strip()
        path.write_text(text, encoding='utf-8', newline='\n')
        task.command(['python', 'tools/doc_budget.py'])
        task.command(['python', '._tmp/preserve_main_changes451.py', '--check'])
        task.git(ROOT, 'diff', '--check', '--', 'docs/STATE.md')
        task.git(ROOT, 'add', '--', 'docs/STATE.md')
        task.git(ROOT, 'commit', '-m', 'docs(#534): record adoption and prioritize tracked potion intake')
        state['state_commit'] = task.git(ROOT, 'rev-parse', 'HEAD').decode().strip()
        task.write(task.JOURNAL, state)
    step(state, '534_note', 'note', '534', 'PD 직접 「승인. 다음 작업 리스트업」을 물약R3 원화4·단계별 표시 비율 채택으로 반영했다. 검토판/사양은 main'
         + state['game_landed_commit'][:8] + ', 원화/승인SHA/착륙raw는 자산main' + state['asset_main_commit'][:8]
         + '에 병합했다. #534 원화 카드 완료. 실제 아이콘4 연결·0.75/0.86/1.0 표시 크기는 새 #' + number
         + ' Codex 이번주로 분리했다. 다음목록 요청에 따라 구현은 아직 시작하지 않았으며 기존191파일·기본2·수치·메인화면은 그대로다. 다른 PD 카드 승인/추가 이미지 생성/push는 이번 지시에 포함하지 않는다.')
    step(state, '274_note', 'note', '274', 'PD 2026-10-02 #534 R3 물약4(hp_potion_2/3·mp_potion_2/3) 채택/원화 병합으로 핵심잔여25→21=오방옥20+호리병1. '
         '승인 정확SHA와 증거=game docs/art/534_potion_grade/approval_2026-10-02.json 및 assets workbench/production/item_icons_534/rank_v3_2026-10-02/APPROVAL.json. '
         '원화main' + state['asset_main_commit'][:8] + '/게임검토판main' + state['game_landed_commit'][:8]
         + '. 실게임물약반입은 Codex #' + number + '로 추적한다(미반입). 나머지21은 기존 후보 PD 확인이며 새 제작량으로 세거나 중복 생성하지 않는다. #265 데이터 선행과 기존 승인 원장은 유지한다. 미push.')
    step(state, '548_note', 'note', number, '다음 작업1순위. 선행 #534 PD채택·원화/검토판 병합 완료(game '
         + state['game_landed_commit'][:8] + ' / assets ' + state['asset_main_commit'][:8]
         + '). 기존 ItemDef6이 있어 #265/#266/#267을 기다릴 필요가 없다. 먼저 단계별 표시 비율/아이콘 선택 사양→전후 스샷→승인SHA4 복사→가방/좌판/벨트/커서 공통 적용·실제 구매/복용·회귀 검수. 지금은 다음 목록 요청으로 카드 등록만 완료, 코드·에셋 반입 미착수. 현재 메인은 유지, 미push.')
    assert review.art.snapshot(ROOT) == json.loads((REPORT / 'game_runtime_before.json').read_text(encoding='utf-8'))
    task.command(['python', '._tmp/preserve_main_changes451.py', '--check'])
    state['phase'] = 'complete'
    task.write(task.JOURNAL, state)
    print(json.dumps({key: state[key] for key in ['phase', 'intake_card', 'game_landed_commit', 'asset_main_commit',
                                                'state_commit', 'game_runtime_files_unchanged', 'runtime_intake']}, indent=2))


if __name__ == '__main__':
    main()
