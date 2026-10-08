from pathlib import Path
import hashlib,json,subprocess
assets=Path('C:/workspace/joseon/._tmp/assets_87')
report=assets/'reports/453/integration_2026-09-27'
# Save the first whole check result exactly. CR in raw Windows engine logs must not be normalized for a whitespace check.
raw=subprocess.run(['git','-C',str(assets),'diff','--cached','--check'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
assert raw.returncode==2
p=report/'453_initial_diff_check.log'
p.write_bytes(raw.stdout)
data=json.loads((report/'verification.json').read_text(encoding='utf-8'))
data['repository_check']={'initial_exit':raw.returncode,'initial_raw':p.name,'initial_raw_sha256':hashlib.sha256(raw.stdout).hexdigest(),
    'cause':'Preserved raw Windows CR line endings reported as trailing whitespace by default git diff --check.',
    'resolution':'Keep raw log bytes untouched; check all staged source/documentation with only reports/453/**/*.log excluded.'}
(report/'verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run(['git','-C',str(assets),'add','--','reports/453','docs/art/453_d1_material_intake'],check=True)
subprocess.run(['git','-C',str(assets),'diff','--cached','--check','--','.',':(exclude)reports/453/**/*.log'],check=True)
subprocess.run(['git','-C',str(assets),'commit','-m','test(#453): 재료6 반입 전후·실제 입력·보존·회귀 증거'],check=True)
for log in report.glob('*.log'):
    rel=log.relative_to(assets).as_posix()
    blob=subprocess.check_output(['git','-C',str(assets),'show',f'HEAD:{rel}'])
    assert blob==log.read_bytes(), rel
print('PASS #453 asset commit; all raw log Git blobs byte-identical; source/document whitespace clean.')
