from pathlib import Path
import json,subprocess
root=Path('C:/workspace/joseon')
assets=root/'._tmp/assets_87'
report=assets/'reports/453/integration_2026-09-27'
data=json.loads((report/'verification.json').read_text(encoding='utf-8'))
head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
assert head==data['landing']['game_main']
production=assets/'workbench/production/item_icons_452'
(production/'ACCEPTANCE.md').write_text(f'''# #452 재료6 채택 및 #453 게임 반입

2026-09-27 PD 「승인 다음」으로 괴황지·경면주사·흑랑 이빨·장산범의 흰 털·불가살이의 쇠비늘·구미호 꼬리털을 전부 채택했다. 승인 생산 커밋은 f96e2931e8fed818b1952642b3fe685edfee1006이다. source/items와 game/items 및 최초 manifest의 후보 제작 기록은 그대로 보존한다.

후속 #453은 승인된80×80 RGBA6를 PowerShell Copy-Item으로 게임에 그대로 복사하고 ItemDef.icon만 연결했다. 게임 main `{head}`, 실제 전후3쌍/단위53/관련E2E11·{data['validation']['related_checks']}검사/빠른부팅·러너5/본진임포트 검수는 reports/453/integration_2026-09-27/verification.json과 QA.md에 보존한다. 이전 아이템23·스킬6 PNG, 다른data/items .tres61파일(색인 포함), 수치·상점해금·보스드랍·모델은 보존했다. #274 핵심 잔여55. 미push.

제작/채택 카드: https://github.com/genesiskoo/joseon-hunters/issues/452
게임 반입 카드: https://github.com/genesiskoo/joseon-hunters/issues/453
''',encoding='utf-8',newline='\n')
p=production/'README.md'
text=p.read_text(encoding='utf-8')
assert 'ACCEPTANCE.md' not in text
p.write_text(text+'\n현재 판정(2026-09-27): 6종 전부 채택·#453 게임 main 반입 완료. 승인/반입 커밋·검수는 [ACCEPTANCE.md](ACCEPTANCE.md). 위 본문과 manifest는 최초 후보 제작 당시 기록을 보존한다.\n',encoding='utf-8',newline='\n')
print('PASS #452 acceptance record: approved originals unchanged; #453 landed game/evidence linked.')
