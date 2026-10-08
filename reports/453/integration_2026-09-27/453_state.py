from pathlib import Path
import json,re,subprocess
root=Path('C:/workspace/joseon')
assets=Path('C:/workspace/joseon-assets')
head=lambda path:subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
data=json.loads((assets/'reports/453/integration_2026-09-27/verification.json').read_text(encoding='utf-8'))
assert data['landing']['game_main']==head(root)
assert (root/'art/ui_intake_453/intake_manifest.json').exists()
p=root/'docs/STATE.md'
text=p.read_text(encoding='utf-8')
assert '#453 재료6' not in text
text=re.sub(r'^- 2026-09-27 Codex: #452 재료6 후보.*$',
    '- 2026-09-27 Codex: #452 재료6 전부채택(PD 승인 다음). 원화 assets main f96e293·검수 main996fa75d 확정, 원화/프롬프트 workbench/production/item_icons_452, 게임 반입은 #453 완료. #274핵심잔여55. 미push.',text,flags=re.M)
line=(f'- 2026-09-27 Codex: #453 재료6 게임{head(root)[:8]}·검수{head(assets)[:8]} 착륙. 승인PNG/icon만·해시/다른필드6·기존29PNG/정의61·기준픽셀3 보존. 단위53/관련E2E11({data["validation"]["related_checks"]}검사)/빠른부팅·러너5 PASS·전후6JPG. 아이콘대기3(봉인조각), 미push.\n')
text=text.replace('## 이번 주 (2026-09-27 기준)\n','## 이번 주 (2026-09-27 기준)\n'+line,1)
text=re.sub(r'^- Codex #160·#445~#450 완료\..*$',
    '- Codex #160·#445~#450·#452·#453 완료. #451 부적 표적 후보는 PD 확인 대기. #274핵심잔여55, 현재 정의 아이콘대기3(봉인조각), 원화 assets item_icons_446·448·452, 반입 docs/art/447·450·453. #273창3은 #265/#266/#267, #392는 #391 대기. 다음은 최신PD댓글/선행 확인.',text,flags=re.M)
p.write_text(text,encoding='utf-8',newline='\n')
assert all(len(line)<=300 for line in text.splitlines())
print('PASS #453 state saved after both main landings; #452 accepted, #451 still pending, parent274 remaining55.')
