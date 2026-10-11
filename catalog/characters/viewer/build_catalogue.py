#!/usr/bin/env python3
"""Read-only catalogue renderer. JSON is the only editable data source.
Requires Pillow. Outputs durable standalone and host-compatible inline views.
"""
import argparse
import base64
import copy
import hashlib
import io
import json
import os
from pathlib import Path
from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
FALLBACK_CSS = '''
:root { color-scheme: light dark; --background:light-dark(#fafafa,#191919); --foreground:light-dark(#202020,#eeeeee); --muted:light-dark(#ededed,#303030); --muted-foreground:light-dark(#575757,#c2c2c2); --popover:var(--background); --popover-foreground:var(--foreground); --border:light-dark(#c5c5c5,#595959); --primary:var(--foreground); --primary-foreground:var(--background); font-family:system-ui,sans-serif; }
body { margin:0; padding:24px; background:var(--background); color:var(--foreground); }
main { max-width:1200px; margin:auto; }
h2,h3 { font-weight:500; } p { line-height:1.5; }
.btn,input,select { font:inherit; color:var(--foreground); background:var(--background); border:1px solid var(--border); border-radius:6px; padding:8px 12px; }
.btn { display:inline-block; text-decoration:none; }
.btn[aria-pressed=true] { background:var(--primary); color:var(--primary-foreground); }
.viz-row,.viz-controls { display:flex; flex-wrap:wrap; align-items:center; gap:10px; }
.form-label { display:flex; flex-direction:column; gap:5px; }
.viz-controls .form-label { flex:1 1 180px; }
.text-small { font-size:.875em; } .text-muted { color:var(--muted-foreground); }
.viz-badge { display:inline-block; padding:3px 8px; background:var(--muted); color:var(--foreground); border-radius:4px; }
hr { border:0; border-top:1px solid var(--border); margin:24px 0; }
pre { white-space:pre-wrap; font:inherit; } summary { padding:10px 0; } blockquote { margin:12px 0; }
@media(max-width:650px) { body { padding:12px; } }
'''


def resolve_file(file, roots):
    """Resolve repository paths; never read arbitrary absolute/external locations."""
    if not file or not file.get('path') or file.get('repository') not in roots:
        return None
    root = roots[file['repository']].resolve()
    rel = Path(file['path'])
    if rel.is_absolute():
        raise ValueError('file.path must be repository-relative')
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError('file.path escapes repository root')
    if not path.is_file() and file['repository']=='assets' and roots.get('assets-overlay'):
        overlay=roots['assets-overlay'].resolve()
        alternate=(overlay/rel).resolve()
        if not alternate.is_relative_to(overlay): raise ValueError('overlay path escapes root')
        if alternate.is_file(): return alternate
    return path


def crop_rectangle(asset):
    panel = asset.get('panel') or {}
    rect = panel.get('crop_rect') or panel.get('crop') or panel.get('rect') or (asset.get('portrait') or {}).get('crop_rect')
    if isinstance(rect, dict) and all(k in rect for k in ('x','y','width','height')):
        return [rect['x'],rect['y'],rect['width'],rect['height']]
    if isinstance(rect, list) and len(rect) == 4:
        return rect
    return None


def preview(asset, roots, size, quality, inline, output, standalone_url, manifest):
    file = asset.get('file') or {}
    path = resolve_file(file, roots)
    if not path or not path.is_file():
        return {'src':None, 'missing_reason':'이미지 파일 미확인'}
    if path.suffix.lower() not in IMAGE_TYPES:
        return {'src':None,'missing_reason':'3D 리소스 연결 · 이미지 캡처 미확인'}
    content = path.read_bytes()
    sha = hashlib.sha256(content).hexdigest()
    if file.get('sha256') and file['sha256'] != sha:
        raise ValueError(f"SHA mismatch: {asset['asset_id']} {file['path']}")
    provided=asset.get('preview') or {}
    provided_path=resolve_file(provided,roots) if provided.get('path') else None
    using_provided=bool(provided_path and provided_path.is_file())
    if using_provided:
        content=provided_path.read_bytes()
        if provided.get('sha256') and hashlib.sha256(content).hexdigest()!=provided['sha256']:
            raise ValueError(f"Preview SHA mismatch: {asset['asset_id']}")
    with Image.open(io.BytesIO(content)) as original:
        image = ImageOps.exif_transpose(original).convert('RGBA')
        rect = crop_rectangle(asset)
        if rect and not using_provided:
            x,y,w,h = map(int,rect)
            if x<0 or y<0 or w<=0 or h<=0 or x+w>image.width or y+h>image.height:
                raise ValueError(f"Invalid crop_rect: {asset['asset_id']}")
            image=image.crop((x,y,x+w,y+h))
        image.thumbnail((size,size),Image.Resampling.LANCZOS)
        buffer=io.BytesIO()
        image.save(buffer,format='WEBP',quality=quality,method=4)
    result={'src':'data:image/webp;base64,'+base64.b64encode(buffer.getvalue()).decode('ascii'),'derived_from':sha,'crop_rect':provided.get('crop_rect',rect),'width':image.width,'height':image.height,'original_url':standalone_url if inline else path.as_uri(),'original_path':str(path)}
    key=hashlib.sha256((sha+json.dumps(rect)+str(size)+str(quality)).encode()).hexdigest()[:20]
    if not inline:
        thumbnail=output/'previews'/f'{key}.webp'
        thumbnail.parent.mkdir(parents=True,exist_ok=True)
        thumbnail.write_bytes(buffer.getvalue())
        manifest.append({'path':'previews/'+thumbnail.name,'derived_from':sha,'crop_rect':provided.get('crop_rect',rect),'width':image.width,'height':image.height,'asset_id':asset['asset_id']})
    return result


def compact_binding(binding):
    result = copy.deepcopy(binding)
    for key in ('definition_config','model_config','portrait_config'):
        if key in result:
            text = str(result.pop(key))
            result[key+'_sha256'] = hashlib.sha256(text.encode()).hexdigest()
    return result


def merge_status(target, source):
    # Evidence is independent. Never let an unchecked record erase checked evidence.
    priorities = {
        'connection': ['not_checked','not_connected','definition_only','connected'],
        'load': ['not_checked','success','failed'],
        'world_display': ['not_checked','not_confirmed','confirmed'],
        'freshness': ['indeterminate','current','stale'],
    }
    for key, order in priorities.items():
        incoming = source.get(key)
        if incoming and (incoming not in order or order.index(incoming) > order.index(target.get(key,order[0]))):
            target[key] = incoming

def runtime_records(inventory):
    if isinstance(inventory,list): return inventory
    if isinstance(inventory,dict):
        for key in ('entries','bindings','records','items','characters'):
            if isinstance(inventory.get(key),list): return inventory[key]
    return []


def normalise(catalog, roots, size, quality, inline, output, standalone_url, validation=None):
    groups={}
    characters={c['character_id']:c for c in catalog.get('characters',[])}
    manifest=[]
    checks={c['asset_id']:c['freshness'] for c in (validation or {}).get('capture_checks',[]) if c.get('asset_id') and c.get('freshness') in ('current','stale','indeterminate')}
    for asset in catalog.get('assets',[]):
        key=asset['character_id']+':'+asset['form_id']
        char=characters.get(asset['character_id'],{})
        form=next((f for f in char.get('forms',[]) if f['form_id']==asset['form_id']),{})
        if key not in groups:
            groups[key]={'id':key,'character_id':asset['character_id'],'name':char.get('display_name',asset['character_id']),'form':form.get('display_name',asset['form_id']),'role':char.get('role',asset.get('role','unknown')),'aliases':form.get('runtime_aliases',[]),'assets':[],'notes':[],'runtime':{'connection':'not_checked','load':'not_checked','world_display':'not_checked','freshness':'indeterminate','bindings':[],'evidence':[]}}
        group=groups[key]
        item=copy.deepcopy(asset)
        if item['asset_id'] in checks:
            item.setdefault('runtime',{})['freshness']=checks[item['asset_id']]
        if item.get('runtime',{}).get('bindings'):
            item['runtime']['bindings']=[compact_binding(b) for b in item['runtime']['bindings']]
        item['preview']=preview(item,roots,size,quality,inline,output,standalone_url,manifest)
        group['assets'].append(item)
        group['aliases']=list(dict.fromkeys(group['aliases']+asset.get('runtime_aliases',[])))
        r=item.get('runtime') or {}
        merge_status(group['runtime'],r)
        group['runtime']['bindings']+=[compact_binding(b) for b in r.get('bindings',[])]
        group['runtime']['evidence']+=r.get('evidence',[])
    for char in catalog.get('characters',[]):
        for form in char.get('forms',[]):
            key=char['character_id']+':'+form['form_id']
            if key not in groups:
                groups[key]={'id':key,'character_id':char['character_id'],'name':char['display_name'],'form':form['display_name'],'role':char['role'],'aliases':form.get('runtime_aliases',[]),'assets':[],'notes':[],'runtime':{'connection':'not_checked','load':'not_checked','world_display':'not_checked','freshness':'indeterminate','bindings':[],'evidence':[]}}
    records=runtime_records(catalog.get('runtime_inventory'))
    for g in groups.values():
        for record in records:
            if record.get('runtime_id') in g['aliases'] or (record.get('character_id')==g['character_id'] and record.get('form_id',g['id'].split(':',1)[1])==g['id'].split(':',1)[1]):
                g['runtime']['bindings'].append(compact_binding(record))
                status=record.get('runtime') or record.get('status') or record
                if isinstance(status,dict):
                    merge_status(g['runtime'],status)
                    if status.get('connection'): g['runtime']['connection']=status['connection']
        if g['character_id']=='gumiho' and any(b.get('model_id')=='heukrang' or 'heukrang' in str(b.get('scene_path',b.get('asset_path',''))) for b in g['runtime']['bindings']):
            g['notes'].append('현재 보스 연결은 흑랑 모델. 구미호 원화 외형과 대체 모델 차이 확인 필요.')
    return {'schema_version':catalog.get('schema_version'),'updated_at':catalog.get('updated_at'),'inline':inline,'groups':list(groups.values()),'issues':catalog.get('issues',[])},manifest


def fragment(data):
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    template=(HERE/'template.html').read_text(encoding='utf-8-sig')
    # JSON is inert and queried from the unique fragment root.
    at=template.rfind('</div>')
    template=template[:at]+'<script type="application/json" data-catalogue-data>'+payload+'</script>\n'+template[at:]
    return '<style>\n'+(HERE/'style.css').read_text(encoding='utf-8-sig')+'\n</style>\n'+template+'\n<script>\n'+(HERE/'app.js').read_text(encoding='utf-8-sig')+'\n</script>\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',required=True,type=Path)
    parser.add_argument('--assets-root',required=True,type=Path)
    parser.add_argument('--validation',type=Path,help='Optional C --check JSON; capture_checks freshness only')
    parser.add_argument('--assets-overlay',type=Path,help='Optional staging asset worktree; only missing canonical files use it')
    parser.add_argument('--game-root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--standalone-url',help='Durable standalone URL for inline original links')
    parser.add_argument('--mode',choices=['both','standalone','inline'],default='both')
    parser.add_argument('--inline-budget',type=int,default=950000)
    args=parser.parse_args()
    catalog=json.loads(args.catalog.read_text(encoding='utf-8-sig'))
    if catalog.get('schema_version')!='1.0.0': raise ValueError('Unsupported schema_version')
    validation=json.loads(args.validation.read_text(encoding='utf-8-sig')) if args.validation else None
    roots={'assets':args.assets_root,'game':args.game_root,'assets-overlay':args.assets_overlay}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'previews').mkdir(exist_ok=True)
    standalone_url=args.standalone_url or (args.output.resolve()/'index.html').as_uri()
    report={'catalog_sha256':hashlib.sha256(args.catalog.read_bytes()).hexdigest(),'assets':len(catalog.get('assets',[])),'outputs':{}}
    if args.mode in ('both','standalone'):
        data,manifest=normalise(catalog,roots,1100,82,False,args.output,standalone_url,validation)
        html='<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>조선헌터스 캐릭터 자료관</title><style>'+FALLBACK_CSS+'</style></head><body><main>'+fragment(data)+'</main></body></html>\n'
        (args.output/'index.html').write_text(html,encoding='utf-8')
        (args.output/'previews'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        report['outputs']['index.html']=len(html.encode())
    if args.mode in ('both','inline'):
        for size,quality in [(480,60),(360,50),(280,45),(220,40),(160,35),(120,30)]:
            data,_=normalise(catalog,roots,size,quality,True,args.output,standalone_url,validation)
            html=fragment(data)
            if len(html.encode())<=args.inline_budget: break
        else: raise ValueError('Inline exceeds budget; reduce catalogue scope rather than omit evidence')
        (args.output/'inline.html').write_text(html,encoding='utf-8')
        report['outputs']['inline.html']=len(html.encode())
        report['inline_preview']={'max_edge':size,'quality':quality}
    (args.output/'previews').mkdir(exist_ok=True)
    (args.output/'previews'/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__': main()





