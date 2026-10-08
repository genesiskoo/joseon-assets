"""Verify #448 generated originals, deterministic packing and real UiSkin captures."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
from PIL import Image, ImageChops

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(p,text):
    p=Path(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8',newline='\n')

def git_head(p):
    return subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()

def finish(root):
    assets=root.parents[2]
    report=assets/'reports/448/integration_2026-09-27'
    gallery=assets/'docs/art/448_d1_items_t2'
    gallery.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    generation=json.loads((root/'generation_sources.json').read_text(encoding='utf-8'))
    assert generation['count']==len(generation['items'])==len(manifest['items'])==6
    generated={e['item_id']:e for e in generation['items']}
    for e in manifest['items']:
        id=e['item_id']
        src=root/'source/items'/f'{id}.png'
        dst=root/'game/items'/f'{id}.png'
        assert sha(src)==e['source_sha256']==sha(generated[id]['generated_path'])
        assert sha(dst)==e['game_sha256']
        assert sha(e['definition_path'])==e['definition_sha256'],f'current ItemDef changed: {id}'
        im=Image.open(dst)
        assert im.size==(80*e['grid_w'],80*e['grid_h'])
        assert im.getchannel('A').getextrema()[0]==0 and im.getchannel('A').getextrema()[1]>=250
        assert not Path(e['definition_path']).read_text(encoding='utf-8').count('icon = ExtResource'),f'candidate installed: {id}'
    frames={}
    for mode,height in [('before',720),('after',720),('sizes',790)]:
        log=report/f'godot_{mode}.log'
        err=report/f'godot_{mode}_errors.log'
        text=log.read_text(encoding='utf-8',errors='replace')
        assert 'GODOT_D1_448 PASS' in text and 'Godot Engine v4.7.2' in text
        assert not err.read_text(encoding='utf-8',errors='replace').strip()
        assert 'ERROR' not in text
        p=root/'qa'/f'godot_{mode}.png'
        assert Image.open(p).size==(1280,height)
        frames[mode]={'sha256':sha(p),'size':[1280,height],'stderr_bytes':err.stat().st_size}
    before=Image.open(root/'qa/godot_before.png').convert('RGB')
    after=Image.open(root/'qa/godot_after.png').convert('RGB')
    refs_same=ImageChops.difference(before.crop((20,535,1260,718)),after.crop((20,535,1260,718))).getbbox() is None
    assert refs_same,'approved references changed'
    pictures=[]
    for name,source in {'overview':root/'qa/overview.png','before':root/'qa/godot_before.png','after':root/'qa/godot_after.png','sizes':root/'qa/godot_sizes.png'}.items():
        target=gallery/f'{name}.jpg'
        Image.open(source).convert('RGB').save(target,quality=85,optimize=True)
        assert target.stat().st_size<=300*1024 and Image.open(target).width==1280
        shutil.copy2(source,report/source.name)
        shutil.copy2(target,report/target.name)
        pictures.append({'name':name,'bytes':target.stat().st_size,'sha256':sha(target)})
    game=Path(manifest['items'][0]['definition_path']).parents[2]
    baseline={'game':git_head(game),'assets_main':git_head(Path(r'C:/workspace/joseon-assets'))}
    verification={'card':448,'parent':274,'baseline':baseline,'method':'built-in image_gen, no CLI/API fallback',
                  'originals_immutable':'6/6','current_definition_hashes_unchanged':'6/6','packed_alpha_and_footprints':'6/6',
                  'source_alpha':{e['item_id']:e['source_alpha'] for e in manifest['items']},
                  'actual_godot_renderer':'4.7.2 Forward+','render_cases':frames,'approved_reference_pixels_identical':refs_same,
                  'gallery':pictures,'game_installation':False,'source_manifest_sha256':sha(root/'generation_sources.json'),
                  'item_manifest_sha256':sha(root/'manifest.json')}
    put(report/'verification.json',json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
    put(gallery/'README.md',"""# #448 D1 소지품 확장 2차

정자관·첨주·윤도·부적 목판(2×2)과 청심환·벽력부(1×1) 후보. overview.jpg는 확대 원화+실제40px 점유 접촉판, before.jpg / after.jpg는 같은 구도의 기존 글리프와 후보 그림을 현재 게임 공통 UiSkin으로 실제 렌더한 결과다. sizes.jpg는30/48/60px/칸 검수. 모두1280폭·300KB 이하, 총4장.

실제 게임 장면 캡처가 아니라 현재 ItemDef·UiSkin을 사용하는 외부 Godot 검수판이다. 위 줄은40px/칸, 아래 줄은 검정 바탕, 하단은 현재 게임에 채택한 D1 패랭이·가죽신·무명띠 기준이다. before/after 하단 픽셀은 동일하다. 후보 그림은 검수 프로세스 메모리에만 넣었으며 게임 파일과 데이터는 바꾸지 않았다.

source/프롬프트/최종PNG/manifest/대본 = workbench/production/item_icons_448/. 원본검수PNG/raw로그/verification = reports/448/integration_2026-09-27/. 채택 뒤 게임 반입은 별도 카드다.
""")
    put(root/'README.md',"""# #448 D1 소지품 2차 납품 후보 (상위 #274)

현재 실제 정의가 있으며 icon=null인 T2 머리·보조4 + 소모품2의 독립 물체 원화다. #446/#393 승인 화풍으로 내장 image_gen을 항목별1회 사용했다. 게임 반입은 아직 하지 않았다.

|id|이름|점유|최종PNG|
|---|---|---:|---:|
|jeongjagwan|정자관|2×2|160×160|
|cheomju|첨주|2×2|160×160|
|yundo|윤도|2×2|160×160|
|bujeok_mokpan|부적 목판|2×2|160×160|
|rejuv|청심환|1×1|80×80|
|talisman_thunder|벽력부|1×1|80×80|

BRIEF.md는 정본과 제작 해석, PROMPTS.md / generation_sources.json은 실제 프롬프트·내장 생성 원본출처, inputs.json은 점유/현재데이터 경로, manifest.json은 원본/패킹/현재ItemDef 해시다. source/items는 생성 원본 그대로, game/items는 기존 alpha16·8%여백·LANCZOS 패킹 결과다. 부적목판 원본 알파는0~254(나머지0~255)이고 보이는 외곽 후광 영역의 실제알파는0이었다. 원본의 near-opaque254를 그대로 유지하므로 불필요한 배경 제거/알파 증폭을 하지 않았다. 검수는 투명0와 객체>=250을 확인한다.

prepare_assets.py는 원본 패킹과 접촉판·외부Godot검수 대본을 준비한다. python prepare_assets.py 뒤 현재 게임 경로로 Godot --script <절대qa_godot.gd> -- --root=<이폴더> --out=<이폴더/qa> --mode=before|after|sizes. 세 raw로그는 reports/448/integration_2026-09-27/godot_<mode>.log와godot_<mode>_errors.log에 저장한다. python finish_review.py가 해시·알파·현재데이터 불변·실제 캡처3회와 승인 기준 동일픽셀을 검증해 gallery4장과verification을 기록한다.

## 왜 이 구조인가

현재 점유와 공통 UiSkin을 기준으로 그림을 독립 물체로 만들면 가방·장비·상점에 비율을 공유할 수 있다. 정사각 장식 액자로 통일하는 대안은 점유와 긴 물체의 형태를 흐려 기각했다. 원본을 남기고 패킹만 결정적으로 수행해 후속 반입·교체를 재현한다. 유니크 전용그림·아직 없는 ItemDef는 이 묶음에 넣지 않았다.

#274 핵심잔여67에서 이번 후보6을 채택하면61. 이 수치는 정의만 있는 품목과 설계에만 있는 품목을 포함한 상위 목록 기준이며, 현재 데이터6개를 미리 채택으로 세지 않는다.
""")
    put(report/'README.md',f"# #448 실제 공통 UI 렌더 검수\n\n기준 game={baseline['game']} / assets-main={baseline['assets_main']}. 내장 image_gen 원본6장, 실제 Godot4.7.2 Forward+ 렌더3회 PASS·stderr0. 현재 ItemDef·UiSkin을 사용하며 게임 파일은 미반입. 승인표본 픽셀은before/after 동일, 원본/현재데이터/최종알파·점유6/6 검증. overview는Pillow확대 접촉판, 나머지3개는실제GPU캡처.\n")
    print('PASS #448 original hashes6, definition hashes6 unchanged, alpha/size6, Godot3 stderr0, reference pixels identical, JPG4 <=300KB')
    print('BASELINE',baseline)
    for p in pictures:
        print(p['name'],p['bytes'])

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    finish(ap.parse_args().root)
