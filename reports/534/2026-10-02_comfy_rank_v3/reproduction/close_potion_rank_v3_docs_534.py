"""Keep the #534 UI specification short and freeze exact validation output."""
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path('C:/workspace/joseon')
ASSET = ROOT / '._tmp/assets_534'
HERE = ASSET / 'workbench/production/item_icons_534/rank_v3_2026-10-02'
REPORT = ASSET / 'reports/534/2026-10-02_comfy_rank_v3'
GAME = Path('C:/Users/FORYOUCOM/.codex/worktrees/534-potion-grade-art/joseon')


def main():
    log = GAME / 'docs/design/potion_rank_534_log.md'
    if log.exists():
        raise SystemExit('The #534 review log is already preserved.')
    ui = GAME / 'docs/design/ui_v2.md'
    text = ui.read_text(encoding='utf-8')
    marker = '## #534 상위 물약4 원화 후보 계약 (2026-10-01)'
    head, old_record = text.split(marker, 1)
    assert '\n## ' not in old_record, 'Do not replace another card section.'
    # The existing candidate description is a record, not the current rule.
    paragraphs = old_record.strip().split('\n\n')
    assert paragraphs[0].startswith('2026-10-02 PD가')
    prior = '\n\n'.join(paragraphs[1:])
    log.write_text('# #534 물약 원화·검수 기록\n\n'
                   '규칙 = `potion_rank_534_2026-10-02.md`. 새 시안은 아직 미채택·미반입이다.\n\n'
                   '## 2026-10-01 R2 후보 — 보완 전 이력\n\n' + prior + '\n\n'
                   '## 2026-10-02 R3 보완 검수\n\n'
                   'Comfy GPT2.5 Flare high의 HP/MP 상위4 원화를 새로 제작했다. 현재 UiSkin은 알파 여백을 제거하므로 검수판에만0.75/0.86/1.0 표시 영역을 적용했다. 실제 UI에 이 비율을 반입하지 않았다. 기본 원화2·정의6·아이콘/정의/UI191파일 SHA는 불변이다. 원본/clean4 RGB 차이0·1024²·clean alpha0~255, 실제 UiSkin6모드(원화/실제크기/벨트축소/검정/무채색/이름·숫자 없는 섞인 판) PASS. 사람의 판독 정확도를 수치로 측정한 결과는 아니다.\n\n'
                   '첫 임포트에서 기존 OPENING class-cache 해석 오류가 발생했다. raw stdout/stderr 전문을 보고서에 보존했고 코드 변경 없이 별도 import_cache_retry1이 통과했다. 뒤6렌더에서 엔진/스크립트 오류0이다. 자세한 manifest·SHA·검수·credential audit·재현 소스는 자산 `rank_v3_2026-10-02`와 `reports/534/2026-10-02_comfy_rank_v3`에 보존한다. 이전 JPG6도 previous_gallery에서 그대로 보존했다.\n\n'
                   '대화/게임 검토판6 = overview 전후·actual 전후·belt_stress·blind. 모두1280폭/각300KB 이하. 현재 게임 반입은 없으며 부모#274 잔여25도 차감하지 않는다. 채택 뒤 원화4와 표시 크기 정책을 함께 연결하는 별도 반입 카드를 만든다.\n',
                   encoding='utf-8', newline='\n')
    ui.write_text(head + '## #534 물약 단계별 시각 위계\n\n'
                  '정본 = `potion_rank_534_2026-10-02.md`, 생산·검수 이력 = `potion_rank_534_log.md`. 기본→금속 봉인1줄→금속 뚜껑/봉인2줄과 부피 증가를 적용한다. 원화4·표시 비율0.75/0.86/1.0은 반입 전 후보이며 기존 원화·수치·UI를 보존한다. 채택 뒤 별도 카드에서 표시 경로를 함께 연결한다.\n',
                  encoding='utf-8', newline='\n')
    frozen = REPORT / 'gallery_r3'
    frozen.mkdir()
    for path in (GAME / 'docs/art/534_potion_grade').glob('*.jpg'):
        shutil.copy2(path, frozen / path.name)
    shutil.copy2(Path(__file__), REPORT / 'reproduction' / Path(__file__).name)
    task_env = os.environ.copy()
    task_env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(['python', 'tools/doc_budget.py'], cwd=GAME, env=task_env, capture_output=True)
    (REPORT / 'doc_budget.stdout.raw.log').write_bytes(result.stdout)
    (REPORT / 'doc_budget.stderr.raw.log').write_bytes(result.stderr)
    assert result.returncode == 0, 'Inspect preserved raw document diagnostics.'
    assert ui.stat().st_size < 60_000
    print(f'PASS #534 rules/log separation; ui_v2={ui.stat().st_size}B; candidate JPG6 and raw doc budget frozen.')
    print('PASS doc budget; unchanged legacy specifications retain their existing warnings.')


if __name__ == '__main__':
    main()
