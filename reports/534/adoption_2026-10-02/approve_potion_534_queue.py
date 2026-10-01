"""Record the human's #534 adoption and prepare its separately tracked UI intake."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path('C:/workspace/joseon')
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/534-potion-grade-art/joseon')
ASSET = ROOT / '._tmp/assets_534'
PROD = ASSET / 'workbench/production/item_icons_534/rank_v3_2026-10-02'
REPORT = ASSET / 'reports/534/adoption_2026-10-02'
JOURNAL = ROOT / '._tmp/approval_534_queue_2026-10-02.json'
task_env = os.environ.copy()
task_env['PYTHONIOENCODING'] = 'utf-8'


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, cwd=ROOT):
    r = subprocess.run(args, cwd=cwd, env=task_env, capture_output=True)
    body = (r.stdout + r.stderr).decode('utf-8', errors='replace')
    is_board_call = 'tools/board.py' in args
    if r.returncode or (is_board_call and '⏳' in body):
        print(body, flush=True)
        raise SystemExit(r.returncode or 1)
    return r.stdout


def git(repo, *args):
    return command(['git', '-c', 'safe.directory=' + str(repo), '-C', str(repo), *args])


def main():
    state = json.loads(JOURNAL.read_text(encoding='utf-8')) if JOURNAL.exists() else {'card': 534, 'phase': 'new'}
    if state['phase'] == 'prepared':
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    assert not git(GAME, 'status', '--porcelain').strip()
    assert not git(ASSET, 'status', '--porcelain').strip()
    previous = json.loads((ROOT / '._tmp/potion_rank_v3_commits_534.json').read_text(encoding='utf-8'))
    assert git(GAME, 'rev-parse', 'HEAD').decode().strip() == previous['game']
    assert git(ASSET, 'rev-parse', 'HEAD').decode().strip() == previous['assets']
    if 'intake_card' not in state:
        body = ('PD 2026-10-02 「승인. 다음 작업 리스트업」으로 #534 R3 원화4 및 표시 비율을 채택했다. '
                '현재 게임에는 아직 반입하지 않았다. 원화 기준=game e155ff47/assets6d32b5b1의 '
                'workbench/production/item_icons_534/rank_v3_2026-10-02/manifest.json·APPROVAL.json. '
                'hp_potion_2/3·mp_potion_2/3의 승인 PNG4를 그대로 복사하고 기존 ItemDef.icon에 각각 연결한다. '
                '기본 HP/MP PNG는 보존한다. UiSkin은 투명 여백을 제거하므로 모든 효능 단계에 표시비율 '
                '기본0.75·2단62/72(약0.86)·3단1.0을 별도로 반영한다. 가방40·좌판48·HUD벨트42·커서 '
                '및 같은 아이콘을 쓰는 표면에서 같은 정책으로 표시한다. 일반 물체/장비 표시 규칙은 유지한다. '
                '실제 정의는 모두 CONSUMABLE/tier1/1×1/stack10, HP40/80/140·MP25/50/90·ilvl1/6/13. '
                '효능 단계와 아이템 등급을 섞지 않는다. 회복·가격·점유·벨트/거래/세이브·타이틀은 보존한다. '
                '먼저 docs/design에 표시 정책 사양을 기록하고 카드 작업 트리에서 구현한다. '
                '검수=동일 게임 상태 전후3쌍(가방·좌판·벨트/커서), 실제 입력 구매/판매/스택/벨트/복용·수량·HP/MP 회복, '
                '승인SHA4·기본PNG2/다른아이콘/비그림필드 보존, 단위·관련E2E·착륙 회귀. '
                'JPG1280폭/각300KB/최대6·원본/raw는 자산 reports. #265/#266/#267 선행 없이 착수 가능. '
                '이번 지시는 다음 목록 요청이므로 카드 등록 후 대기, 새 원화 추가 생성 없음·미push.')
        raw = command(['python', 'tools/board.py', 'new',
                       '[P2] 승인 물약4 게임 반입 — 효능 단계별 크기·봉인 위계 및 모든 UI 표시 연결',
                       '-l', 'P2,UI,아이템,codex,M', '--who', 'codex', '--week', '-b', body])
        text = raw.decode('utf-8', errors='replace')
        ids = re.findall(r'issues/(\d+)', text)
        if not ids:
            raise SystemExit('Inspect new card outcome before any retry; number not returned.')
        state['intake_card'] = int(ids[-1])
        write(JOURNAL, state)
        print(text, flush=True)
    number = state['intake_card']
    manifest = json.loads((PROD / 'manifest.json').read_text(encoding='utf-8'))
    approved = []
    for item in manifest['items']:
        assert sha(PROD / item['source_path']) == item['source_sha256']
        assert sha(PROD / item['game_path']) == item['game_sha256']
        approved.append({key: item[key] for key in ['item_id', 'display_name', 'efficacy_stage', 'source_path', 'source_sha256',
                                                   'game_path', 'game_sha256', 'generated_sha256', 'display_scale', 'cloud_prompt_id']})
    approval = {'card': 534, 'parent_card': 274, 'date_kst': '2026-10-02',
                'authorization_source': 'Current direct human message in this chat',
                'human_message': '승인. 다음 작업 리스트업',
                'scope': 'Shown #534 R3 four potion artworks and preview size hierarchy; other PD cards are not approved.',
                'approved_game_review_commit': previous['game'], 'approved_asset_commit': previous['assets'],
                'adoption': 'approved', 'runtime_intake': False, 'runtime_scale_policy_installed': False,
                'intake_card': number, 'approved_items': approved,
                'display_scale_by_efficacy_stage': {'1': .75, '2': 62 / 72, '3': 1.0},
                'basic_art_and_gameplay_preserved': True, 'current_title_unchanged': True,
                'parent_core_remaining_before': 25, 'newly_adopted_core_items': 4, 'parent_core_remaining_after': 21,
                'remaining_unadopted': {'obang_jade_icons': 20, 'horibyeong_icon': 1}, 'push': False}
    asset_approval = PROD / 'APPROVAL.json'
    game_approval = GAME / 'docs/art/534_potion_grade/approval_2026-10-02.json'
    assert not asset_approval.exists() and not game_approval.exists()
    write(asset_approval, approval)
    write(game_approval, approval)
    spec = GAME / 'docs/design/potion_rank_534_2026-10-02.md'
    text = spec.read_text(encoding='utf-8')
    text = text.replace('# #534 물약 단계 판독 보완 — 2026-10-02 후보', '# #534 물약 단계 판독 보완 — 2026-10-02 채택 규격', 1)
    text = text.replace('이전 후보는 채택 보류하며,', '보완 R3 원화4와 표시 비율은 2026-10-02 PD 「승인. 다음 작업 리스트업」으로 채택했다. 실제 반입은 #' + str(number) + '에서 추적하며 현재 UI/그림은 그대로다. ', 1)
    spec.write_text(text, encoding='utf-8', newline='\n')
    ui = GAME / 'docs/design/ui_v2.md'
    ui.write_text(ui.read_text(encoding='utf-8').replace('원화4·표시 비율0.75/0.86/1.0은 반입 전 후보이며',
                                                       '원화4·표시 비율0.75/0.86/1.0은 PD 채택 규격이며 실제 반입은 #' + str(number) + '에서 추적한다. '),
                  encoding='utf-8', newline='\n')
    log = GAME / 'docs/design/potion_rank_534_log.md'
    text = log.read_text(encoding='utf-8').replace('새 시안은 아직 미채택·미반입이다.',
                'R3는 2026-10-02 PD 채택. 실제 게임 반입은 #' + str(number) + ' 대기다.', 1)
    text = text.replace('현재 게임 반입은 없으며 부모#274 잔여25도 차감하지 않는다.',
                        '채택 전 검수 시점에는 게임 반입이 없고 부모#274 잔여25도 차감하지 않았다.', 1)
    text += '\n## 2026-10-02 PD 채택\n\n직접 사용자 「승인. 다음 작업 리스트업」으로 R3 원화4·표시 크기 정책을 채택했다. '
    text += '정확한 원본/출력 SHA와 jobID는 docs/art/534_potion_grade/approval_2026-10-02.json 및 자산 APPROVAL.json에 보존한다. '
    text += '부모#274 원화 잔여는25→21(오방옥20+호리병1). 기존 후보·수치·기본2는 그대로다. '
    text += '아이콘 연결/단계별 표시 크기의 실제 반입은 #' + str(number) + '로 등록했다. 메인 개편#545와 다른 PD 카드는 이번 승인에 포함하지 않는다.\n'
    log.write_text(text, encoding='utf-8', newline='\n')
    REPORT.mkdir()
    (REPORT / '.gitattributes').write_text('** -text -whitespace\n', encoding='utf-8', newline='\n')
    write(REPORT / 'approval.json', approval)
    git(GAME, 'add', '--', 'docs/art/534_potion_grade/approval_2026-10-02.json',
        'docs/design/potion_rank_534_2026-10-02.md', 'docs/design/potion_rank_534_log.md', 'docs/design/ui_v2.md')
    git(GAME, 'diff', '--cached', '--check')
    git(GAME, 'commit', '-m', 'docs(#534): adopt potion R3 artwork and queue tracked UI intake')
    state.update(phase='prepared', game_approval_commit=git(GAME, 'rev-parse', 'HEAD').decode().strip(),
                 asset_approval_staged=False, approval_scope=534, runtime_intake=False)
    write(JOURNAL, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
