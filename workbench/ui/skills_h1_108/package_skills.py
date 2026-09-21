"""#108: mechanical sizing and diagnostic UI previews, never repaint assets."""
from pathlib import Path
import hashlib
import importlib.util
import json
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
helper_path = ROOT.parent/'icons_readability_102'/'package_review.py'
spec = importlib.util.spec_from_file_location('h1_review_helpers', helper_path)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
SKILLS = [('slash', '참격', '대각 반달 궤적'), ('dash_strike', '돌진베기', '수평 전진 쐐기'), ('whirl', '회오리베기', '중앙이 빈 회전 궤적')]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def slot(icon, px, state='normal'):
    n = px+16
    im = Image.new('RGBA', (n,n), h.WELL)
    im.alpha_composite(h.fit(icon, (n,n), 8))
    draw = ImageDraw.Draw(im)
    draw.rectangle((0,0,n-1,n-1), outline='#59585b', width=1)
    if state == 'selected':
        draw.rectangle((1,1,n-2,n-2), outline='#ceb276', width=2)
    elif state == 'locked':
        cover = Image.new('RGBA', im.size, (5,7,10,130))
        im.alpha_composite(cover)
        draw = ImageDraw.Draw(im)
        w = 10 if px == 30 else 14
        x,y = n-w-3,n-w-3
        draw.arc((x+2,y-5,x+w-2,y+5), 180,360,fill='#d2c7ad',width=2)
        draw.rounded_rectangle((x,y+1,x+w,y+w),radius=1,fill='#24262a',outline='#d2c7ad',width=1)
        draw.point((x+w//2,y+5),fill='#d2c7ad')
    elif state == 'cooldown':
        cover = Image.new('RGBA', im.size)
        ImageDraw.Draw(cover).pieslice((-n,-n,2*n,2*n),270,450,fill=(4,6,9,155))
        im.alpha_composite(cover)
        ImageDraw.Draw(im).line((n//2,2,n//2,n-3),fill='#aaa18d',width=1)
    return im

def main():
    review = ROOT/'review'
    review.mkdir(exist_ok=True)
    icons, records = {}, []
    for key,name,_ in SKILLS:
        source = ROOT/'sources'/f'{key}.png'
        im = Image.open(source).convert('RGBA')
        info = h.alpha_info(im)
        assert info['alpha_extrema'] == [0,255] and info['transparent_pixels']>im.width*im.height*.15
        icon,crop = h.package(im)
        dest = ROOT/f'{key}.png'
        icon.save(dest,compress_level=9)
        output = h.alpha_info(icon)
        x0,y0,x1,y1=output['alpha_bbox']
        assert x0>=12 and y0>=12 and x1<=116 and y1<=116
        assert icon.mode=='RGBA' and icon.size==(128,128)
        metadata = json.loads((ROOT/'sources'/f'{key}.json').read_text(encoding='utf-8-sig'))
        records.append({**metadata,'name':name,'source_sha256':sha(source),'source_info':info,
                        'reference_sha256':{str(p):sha(Path(p)) for p in metadata['references']},
                        'crop_alpha_ge_8_plus_2px':crop,'output':dest.name,
                        'output_sha256':sha(dest),'output_info':output})
        icons[key]=icon

    sheet = Image.new('RGBA',(1056,964),h.BG)
    h.label(sheet,(22,15),'#108  H1 검술 아이콘 — 참격 / 돌진 / 회오리',24)
    h.label(sheet,(22,52),'128px 납품 후보 · 제안 슬롯 / UI 상태 모의 검수 · 실게임 스크린샷 아님',15)
    for i,(key,name,meaning) in enumerate(SKILLS):
        x=22+i*346
        h.label(sheet,(x,101),name,22)
        h.label(sheet,(x,132),meaning,14,h.MUTED)
        for j,bg in enumerate([h.WELL,'#d8d0c1']):
            plate=Image.new('RGBA',(128,128),bg)
            plate.alpha_composite(icons[key])
            sheet.alpha_composite(plate,(x+j*154,164))
        h.label(sheet,(x,301),'128px · 어두운 / 밝은 바탕 알파 검수',13,h.MUTED)
        sheet.alpha_composite(slot(icons[key],30),(x+38,342))
        sheet.alpha_composite(slot(icons[key],60),(x+172,327))
        h.label(sheet,(x+27,411),'내용 30px',13)
        h.label(sheet,(x+169,411),'내용 60px',13)
    h.label(sheet,(22,457),'상태 덮개 — 아래 모든 아이콘은 같은 원본 PNG',18)
    states=[('normal','기본'),('selected','선택'),('locked','잠금'),('cooldown','쿨다운 50%')]
    for j,(_,name) in enumerate(states):
        h.label(sheet,(222+j*204,497),name,17)
    for i,(key,name,_) in enumerate(SKILLS):
        y=535+i*124
        h.label(sheet,(22,y+23),name,17)
        for j,(state,_) in enumerate(states):
            x=222+j*204
            sheet.alpha_composite(slot(icons[key],60,state),(x,y))
            sheet.alpha_composite(slot(icons[key],30,state),(x+96,y+15))
            h.label(sheet,(x+16,y+82),'60px',11,h.MUTED)
            h.label(sheet,(x+104,y+82),'30px',11,h.MUTED)
    h.label(sheet,(22,923),'테두리·잠금·쿨다운은 검수판 UI이며 납품 PNG에 포함되지 않습니다. 실제 HUD 적용은 #109.',14)
    sheet.convert('RGB').save(review/'skills_preview.png')

    mono=Image.new('RGBA',(1056,527),h.BG)
    h.label(mono,(22,15),'#108  흑백 / 실루엣 진단',24)
    h.label(mono,(22,54),'진단용 합성만 흑백 변환 · 납품 PNG 원본은 변경하지 않음 · 내용 30 / 60px',15)
    for i,(key,name,_) in enumerate(SKILLS):
        x=22+i*346
        h.label(mono,(x,99),name,21)
        gray=ImageOps.grayscale(icons[key]).convert('RGBA')
        gray.putalpha(icons[key].getchannel('A'))
        mask=Image.new('RGBA',(128,128),'#deded8')
        mask.putalpha(icons[key].getchannel('A'))
        for j,(desc,probe) in enumerate([('흑백 휘도',gray),('단색 실루엣',mask)]):
            y=150+j*163
            h.label(mono,(x,y),desc,15,h.MUTED)
            mono.alpha_composite(slot(probe,30),(x+38,y+49))
            mono.alpha_composite(slot(probe,60),(x+172,y+34))
            h.label(mono,(x+42,y+113),'30px',12,h.MUTED)
            h.label(mono,(x+191,y+113),'60px',12,h.MUTED)
    h.label(mono,(22,489),'방향(대각 / 수평)과 닫힘 정도(열린 반달 / 쐐기 / 큰 원)를 기준으로 판정.',14)
    mono.convert('RGB').save(review/'monochrome_diagnostic.png')
    manifest={'schema':1,'issue':108,'date':'2026-09-21','status':'PD_review_required',
              'tool':'built-in imagegen','model_version':'not exposed by tool','requested_size':[1024,1024],
              'canvas':[128,128],'art_longest_px':103,'items':records,
              'rejected':[{'id':'dash_strike','source':'rejected/thin_dash/dash_strike.png',
                           'sha256':sha(ROOT/'rejected/thin_dash/dash_strike.png'),
                           'reason':'Too little visible area at 30px with lock/cooldown overlays; replaced by broader revision.'}],
              'processing':'alpha-support bounds >=8/255 +2px rectangular crop; preserve retained RGBA; proportional premultiplied resize; center. No repaint or background keying.',
              'preview':'Mock UI only: content 30/60px, neutral well, selected border, dark lock overlay + lock glyph, half radial dark cooldown overlay. Grayscale and alpha silhouette are diagnostic renders only.',
              'helper':{'path':'../icons_readability_102/package_review.py','sha256':sha(helper_path)},
              'checks':{'rgba_128_count':3,'real_alpha_count':3,'safe_bounds_count':3,
                        'center_alpha_whirl':icons['whirl'].getpixel((64,64))[3],
                        'runtime':'not_run_candidate_assets_only','input_test':'deferred_to_109'}}
    assert manifest['checks']['center_alpha_whirl'] <= 7,'whirl center must remain transparent'
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: 3 real-alpha source images, 3 safe 128px RGBA icons, 2 diagnostic sheets; whirl center transparent.')
    for rec in records:
        print(rec['id'],rec['source_info']['dimensions'],rec['output_info']['alpha_bbox'])
    print('Runtime not tested; review sheets are mock UI.')

if __name__=='__main__':
    main()
