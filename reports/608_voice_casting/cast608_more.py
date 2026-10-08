exec(open('C:/workspace/joseon/tmp/cast608_fetch.py',encoding='utf-8').read().split('for name,path in')[0])
pages=[];n=0
while True:
 data=get('/v1/shared-voices?page_size=100&language=ko&accent=korean&page='+str(n));pages.append(data);n+=1
 print('NATIVE_PAGE',n,len(data.get('voices',[])),data.get('total_count'),data.get('has_more'),flush=True)
 if not data.get('has_more') or n>=40:break
voices={v['voice_id']:v for p in pages for v in p.get('voices',[])}
(out/'native_filtered.json').write_text(json.dumps({'voices':list(voices.values()),'has_more':data.get('has_more'),'pages':n,'query':'language=ko&accent=korean','total_count':data.get('total_count')},ensure_ascii=False,indent=2),encoding='utf-8')
