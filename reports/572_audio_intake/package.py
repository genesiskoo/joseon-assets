import pathlib,json,re,shutil,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path('C:/workspace/joseon');p=root/'tmp/audio572';work=pathlib.Path('C:/Users/FORYOUCOM/.codex/worktrees/572-audio-intake/joseon')
assets=pathlib.Path('C:/workspace/joseon-assets');library=assets/'workbench/audio/560_audio_library';out=library/'release572';out.mkdir(exist_ok=True)
vm=json.loads((p/'voice_manifest.json').read_text(encoding='utf-8'));voices={r['id']:r for r in vm['lines']};rows=[];records=[]
for kind in ['sfx','voice','opening']:
 for r in json.loads((p/(kind+'_intake.json')).read_text(encoding='utf-8')):
  src=work/r['target'];dst=out/pathlib.Path(r['target']).relative_to('assets/audio');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  ident=src.stem;v=voices.get(ident);category='대사' if v else 'BGM' if kind=='opening' else '환경음' if '/amb/' in src.as_posix() else '효과음'
  rows.append(dict(category=category,origin='게임 반입 #572',title=(v['speaker']+' · '+v['text']) if v else ('판소리 오프닝 A1' if kind=='opening' else ident),detail='ElevenLabs v4 · 최신 대본 · 분기 문맥' if v else 'Suno A1 · 오프닝 1회 재생' if kind=='opening' else '새 생성 교체본 · 원본 클리핑 0 · 규격 음량',group=ident if v else re.sub(r'_\d+$','',ident),path=dst.relative_to(out).as_posix(),duration=r['format']['dur'],today=True))
  records.append(dict(target=r['target'].replace('\\','/'),sha256=r['sha256'],source_sha256=r['source_sha256'],source=pathlib.Path(r['source']).as_posix(),loudness=r['loudness'],duration=r['format']['dur']))
provenance=dict(card=572,generated_by='codex',voice_model='eleven_v4',voice_cast=vm['voices'],dialogue_source_sha256=vm['source_sha256'],files=records)
(work/'data/audio').mkdir(exist_ok=True);(work/'data/audio/production_572.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
template=(library/'compare567/index.html').read_text(encoding='utf-8')
html=re.sub(r'const data=\[.*?\];const \$',lambda m:'const data='+json.dumps(rows,ensure_ascii=False)+';const $',template,flags=re.S)
html=html.replace('전체 사운드 교체 비교','게임 반입 음원 #572').replace('오늘 생성·비교 277항목 + 기존 게임119개. Typecast SDK12개와 기각 실험도 포함했습니다.','효과음109 · 환경음2 · v4 대사155 · 판소리 오프닝1. 실제 게임에 연결하는 최종 음원267개입니다.')
html=html.replace('기존 게임 음원은 교체 검토 대상으로 표시했습니다. 이전 Suno·Typecast·Eleven 후보도 함께 검색하고 재생할 수 있습니다.','개별 재생과 필터 연속 재생으로 반입 결과를 확인할 수 있습니다.').replace('<option value="새 생성 #567">Eleven 신규 #567</option>','<option value="게임 반입 #572">게임 반입 #572</option>')
(out/'index.html').write_text(html,encoding='utf-8');(out/'list.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
compare=library/'compare567';data=json.loads((compare/'list.json').read_text(encoding='utf-8'));data=[x for x in data if x.get('origin')!='게임 반입 #572']
data.extend([dict(x,path='../release572/'+x['path']) for x in rows]);data.sort(key=lambda x:(x['category'],x.get('group',''),x['origin']))
html=re.sub(r'const data=\[.*?\];const \$',lambda m:'const data='+json.dumps(data,ensure_ascii=False)+';const $',template,flags=re.S)
html=html.replace('오늘 생성·비교 277항목 + 기존 게임119개. Typecast SDK12개와 기각 실험도 포함했습니다.','생성·비교·반입 544항목 + 기존 게임119개. 최종 게임 반입267개를 추가했습니다.')
html=html.replace('<nav>','<p><a href="../release572/">▶ 게임 반입 최종267개</a></p><nav>',1)
(compare/'index.html').write_text(html,encoding='utf-8');(compare/'list.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
report=assets/'reports/572_audio_intake';report.mkdir(parents=True,exist_ok=True)
shutil.copytree(p,report,dirs_exist_ok=True)
print('PACKAGED',len(rows),'selected;',len(data),'comparison total; voice seconds',round(sum(x['duration'] for x in rows if x['category']=='대사'),2))
