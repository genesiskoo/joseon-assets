"""Assemble candidate documentation from actual output reports. Does not alter GLBs."""
from pathlib import Path
import datetime, hashlib, html, json

BASE = Path(__file__).resolve().parent
MAIN = Path('C:/workspace/joseon')
def read(name):
    return json.loads((BASE/name).read_text(encoding='utf-8'))
def save(name,obj):
    (BASE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def fmt(vector):
    return ' × '.join(f'{x:.4f}'.rstrip('0').rstrip('.') for x in vector)

module = read('module_report.json')
props = read('props_report.json')
render = read('render_report.json')
export = read('glb_export_audit.json')
socket = read('h1_socket_correction.json')
socket['visual_sample_review']={
    'reviewed_images':9,
    'model_sha256':'e5fea5c6383180d1369d5f1975f804c4f3a2dd70a608918e26593d94c2511749',
    'finding':'H1 socket follows the fist candidate; attack samples show blade extending away from hand/body. Idle blade overlaps forearm in projection; walk 78% hides blade behind garment/body, so exact skin clearance is unresolved.',
    'finger_contact_final_approval':False,
    'full_clip_collision_test_performed':False,
    'exact_skinned_mesh_collision_test_performed':False}
save('h1_socket_correction.json',socket)
atlas = read('textures/atlas_layout.json')
assert sha(BASE/'textures/H1_matte_atlas.png')==atlas['source_sha256']
assert sha(Path(atlas['source']))==atlas['source_sha256']
module['supplied_material_atlas']=atlas
module['limitations']=[
    'Candidates only; collision, navigation, runtime batching/cutaway integration not implemented',
    'Stone albedos inherited unchanged; stairs retain inherited 2K textures',
    'Door_frame and market_bay use 3-cell assembly pitch; not single-cell tile replacements',
    'Brazier and lantern omit light; effect is separate in the review scene',
    'Town TEX01 shared atlas is 1254x1254, above nominal 1K; seamless/fully unlit not guaranteed',
    'Onggi retains matte solid color; H1 illustration-level material finish is unapproved']
props['supplied_material_atlas']=atlas
props['limitations']=[
    'Wood and dark scabbard use the supplied 1254x1254 TEX01 atlas; remaining surfaces use matte colors',
    'Geometry/material candidates, not illustration-level finish',
    'H1 preserved fist candidate attachability does not certify finger/sleeve contact or full animation clearance',
    'No main weapon_scene, socket offset or runtime asset changed']
for group in (module['modules'],props['props']):
    for item in group:
        if any(m['name'].startswith('h1_atlas_') for m in item['materials']):
            item['derivation']='Procedural candidate; supplied TEX01 unchanged PNG, quadrant UV0 in mesh; matte color for remaining parts'
            item['atlas']='textures/atlas_layout.json'
            save(str(Path(item['file']).with_suffix('.json')),item)
save('module_report.json',module)
save('props_report.json',props)
assets = module['modules']+props['props']
assert len(assets)==18 and len(module['modules'])==14 and len(props['props'])==4
assert export['all_pass'] and not module['errors'] and not props['errors'] and not render['errors']
source_checks=[]
for item in module['sources']:
    path=MAIN/'assets/models/tilekit_stone'/item['file']
    actual=sha(path)
    source_checks.append({'source':str(path),'initial_sha256':item['sha256'],'current_sha256':actual,'unchanged':actual==item['sha256']})
assert all(item['unchanged'] for item in source_checks)
save('source_preservation.json',{'all_unchanged':True,'checks':source_checks})

limitations = [
    '미승인 후보 묶음. 프로덕션 게임 반입, 충돌, 길찾기, 게임플레이, 실제 DungeonBuilder 배치 검증은 수행하지 않았다.',
    '마을·곤봉·검집에 공급받은 TEX01 재질을 추가한 후보이며, 옹기·종이부적 등은 무광 단색을 유지한다. H1 원화 수준의 표면 완성본으로 승인되지 않았다.',
    '기존 돌 텍스처의 규칙적인 반복 무늬를 보존했다. 기하 접합 간격 0이 시각적 텍스처 무봉제를 보증하지 않는다.',
    '계단 2종은 기존 2048² 텍스처를 유지한다. 모서리·기둥은 각각 1024² 텍스처 2장 및 2재질을 사용하여 단일 1K 타일 재질 목표의 예외다.',
    'TEX01 공유 아틀라스는 실제 1254×1254로 1K 목표를 넘는다. 기와에 얕은 명암이 포함되어 완전 평광·seamless를 보증하지 않는다. 원본 PNG를 편집하지 않고 UV로만 4분면을 선택했다.',
    'stairs_down은 기존 쐐기 형상이다. 실제 바닥 개구부나 층 이동 기능이 없다.',
    '문틀은 3칸 조립물, 상점은 3칸 배치 간격의 정면 한 칸이다. 상점 총폭 3.25u는 처마 돌출을 포함한다. 반복 처마 연결부는 지붕 설계 확정 시 추가 검수한다.',
    '화로 불·등불 조명은 예제 씬 효과로 분리했다. GLB에는 화염, 빛, 콜리전, 문 애니메이션이 포함되지 않는다.',
    '손 소켓 계산과 9개 포즈 표본은 손가락 접촉·소매 간섭·전체 공격 클립의 최종 승인이 아니다. 실제 손아귀 시각 상태는 h1_socket_correction.json을 따른다.',
]
qa={
    'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status':'CANDIDATE_REVIEW_READY_NOT_GAME_INTAKE',
    'candidate_count':18,'environment_count':14,'separate_prop_count':4,
    'actual_godot_capture_count':len(render['captures']),
    'checks':{'source_assets_unchanged':True,'all_glb_self_contained':all(not x['external_dependencies'] for x in export['assets']),
              'all_at_most_500_triangles':all(x['triangles']<=500 for x in assets),
              'winding_normal_disagreements':sum(x['gltf_ccw_normal_disagreements'] for x in export['assets']),
              'degenerate_triangles':sum(x['degenerate_triangles'] for x in export['assets']),
              'paper_vertex_z_thickness':next(x for x in assets if x['id']=='paper_talisman')['vertex_aabb_size'][2],
              'paper_all_materials_double_sided':all(x['cull_mode']==2 for x in next(x for x in assets if x['id']=='paper_talisman')['materials']),
              'final_build_error_count':len(module['errors'])+len(props['errors']),
              'final_render_error_count':len(render['errors'])},
    'camera':render['camera'],'tile_seams':render['tile_seams'],'occlusion':render['occlusion'],
    'material_atlas':render['material_atlas'],'material_comparison':render['material_comparison'],
    'sheath_fit':props['sheath_fit'],'socket':socket,'limitations':limitations,
    'visual_review':{'environment':'Actual exported GLBs inspected in neutral catalog and copied dark lighting. Integer floor/wall joins meet; source periodic texture repetition remains visible.',
                     'town':'TEX01 distinguishes timber, roof tiles, plaster and hanji in neutral catalog. Copied dark lights keep roof dark. Onggi remains matte solid color. Final H1 surface approval is pending.',
                     'props':'Sword grip-origin rotations and front/back talisman viewed; handles and scabbard visibly distinguishable in auxiliary closeup.',
                     'socket':'See dedicated hand/socket status and sampled renders. No production ModelDef edited.'},
    'raw_logs':'*_stdout.log and *_stderr.log retain raw engine output; socket_probe_engine.log and build_initial_raw.log retain recovered initial failures.'
}
save('qa_report.json',qa)

manifest={
    'title':'H1 환경 14종 + 분리 소품 4종 · 로컬 3D 후보',
    'status':qa['status'],'unit':'1 Godot unit = 1 tile; actor reference height 1.70u',
    'is_game_intake':False,'local_module_agent_ai_generation_calls':0,'supplied_ai_material_atlas':atlas,'main_assets_modified':False,
    'candidate_count':18,'assets':assets,'reference_actor':render['h1_actor'],
    'captures':render['captures'],'material_comparison':render['material_comparison'],'qa':'qa_report.json','readme':'README.md','gallery':'index.html',
    'geometry_readback_audit':'glb_export_audit.json','source_preservation':'source_preservation.json',
    'socket_report':'h1_socket_correction.json','reproduction':'REPRODUCE.md',
    'concept_reference_roles':{
        '../00_style_anchor.md':'H1 common shape/material direction',
        '../02_motgol_wide.png':'town mood and shapes; not texture or dimension source',
        '../03b_sealed_chamber_club.png':'dungeon mood; not render evidence',
        '../14_motgol_modules_props.png':'town prop shape reference; SIGN/BENCH excluded from this scope',
        'dungeon and weapon concept sheets supplied by parent':'art direction only; candidate dimensions follow current pipeline'},
    'limits':limitations,
}
save('manifest.json',manifest)
save('canonical_glbs.json',{'candidate_count':18,'environment_count':14,'prop_count':4,'reference_actor_excluded':True,'assets':[{'id':x['id'],'file':x['file'],'sha256':x['sha256'],'triangles':x['triangles']} for x in assets]})

names={'floor':'바닥','wall_straight':'직선벽','stairs_up':'올라가는 계단','stairs_down':'내려가는 계단 후보','wall_corner':'바깥 모서리','door_frame':'문틀','seal_door':'봉인문','pillar':'기둥','brazier':'철화로','market_bay':'목조 상점 정면','paper_sliding_door':'한지 미닫이문','wood_crate':'나무 상자','onggi_jar':'옹기 항아리','square_paper_lantern':'사각 종이등','doho_sword':'도호 검','doho_scabbard':'검집','bandit_club':'곤봉','paper_talisman':'종이부적'}
table='\n'.join(f"| [{names[x['id']]}]({x['file']}) | {fmt(x['vertex_aabb_size'])} | {x['triangles']} | {len(x['materials'])} |" for x in assets)
minimum=min(s['torso_axis_min_distance']-s['torso_proxy_radius'] for s in socket.get('samples',[]))
readme=f'''# H1 환경·소품 3D 후보 묶음

던전 9종, 마을 5종, 분리 소품 4종의 **실제 GLB 18개**와 **Godot 렌더 {len(render['captures'])}장**이다. 정식 게임 반입 전 후보이며, 원화 이미지를 3D 렌더처럼 사용하지 않았다. 빠른 비교는 [실제 렌더 갤러리](index.html), 상세 수치는 [검사표](qa_report.json)와 [목록](manifest.json)을 본다.

![던전 실제 조합 렌더](captures/03_dungeon_assembly.png)

![마을 실제 조합 렌더](captures/02_town_assembly.png)

## 형상과 재질

현재 게임 바닥·벽·계단과 텍스처를 재사용하고, 모서리·문·기둥·소품을 큰 무광 형태로 만들었다. 바닥·벽은 복사본의 인덱스 winding만 수정했고 원본 정점·UV·노멀·알베도를 보존했다. 계단은 후보 사본에서만 502→488 / 514→487 삼각형으로 줄였다. 원본 8파일의 SHA256은 시작 시점과 동일하다.

이 구조는 현재 렌더와 색·명암 관계를 유지하면서 1u 접합 규격을 직접 검증하기 위해 선택했다. AI로 타일 전체를 다시 생성하는 방법은 치수·면 방향·반복 접합 변수가 늘어나므로 이 후보 묶음에서는 사용하지 않았다. 마을은 공급받은 TEX01 1254² 아틀라스를 추가 적용했다. PNG 원본을 그대로 사용하고 목재·기와·회벽·한지 4분면을 정점 UV로 선택했다. 검집·곤봉도 목재 분면을 공유한다. 옹기와 종이부적은 단색 후보다.

원본 PNG 픽셀 후처리는 없다. 런타임 GLTFDocument가 에디터 임포트를 우회하므로 렌더 때 아틀라스의 표준 mipmap과 anisotropic 필터를 만들었다. 이 필터는 화면 축소 시 잔점·앨리어싱을 줄이며 PNG 파일은 바꾸지 않는다. 동일 최종 형상·H1·카메라·조명을 쓴 단색 control은 12/13/14번, 재질판은 01b/02/07번 캡처다.

## 파일 규격

축은 Godot Y-up, 1u=1타일이다. 바닥 상면 Y=0, 일반 환경 소품은 밑면 중앙 원점이다. 봉인문·미닫이문 앞면은 +Z다. 벽 모서리는 +X/+Z 바깥 모서리만 0.12u 모따기했다. 문틀의 열린 폭은 1.5u, 높이는 2.05u다. 총 치수는 실제 정점 AABB 기준이다.

| GLB | X × Y × Z (u) | 삼각형 | 재질 수 |
|---|---:|---:|---:|
{table}

검은 손아귀 원점, +Y 칼끝, XY 넓은 면이다. 칼날 길이 0.74u는 현재 ActorVisual 프록시와 같다. 검집 입구를 검 로컬 Y=0.06에 놓으면 내부 폭 여유 0.009u, 두께 여유 0.008u, 끝 여유 0.01u다. 곤봉도 손아귀 원점/+Y 타격부다. 종이부적은 윗변 집는 점 원점, -Y로 늘어지는 XY 평면이다. 정점 Z 두께는 정확히 0이고 세 재질 모두 double-sided다. Godot 표시 AABB의 약 0.00001u 깊이는 최소 경계 상자 패딩이다.

## 실제 렌더 검수

- 환경: 직교 크기 11, pitch 35.264°, yaw 45°, 1280×720. 프로덕션 환경·광원 값을 복사한 독립 예제 씬이다.
- 소품 확대: 직교 2.2. 손 소켓 확대: 직교 3.5. 확대 화면은 실제 인게임 표시 크기가 아니다.
- 1u 간격 바닥/벽 및 정수 좌표 모서리의 기하 접합 간격은 0u다. 문틀 아래 바닥도 포함했다.
- 같은 1.7u 마젠타 캡슐의 가시 픽셀은 앞벽 없음 {render['occlusion']['baseline_pixels']}, 불투명 앞벽 {render['occlusion']['opaque_pixels']}({render['occlusion']['opaque_visible_ratio']:.1%}), 기존 cutaway 적용 {render['occlusion']['cutaway_pixels']}({render['occlusion']['cutaway_visible_ratio']:.1%})였다. 독립 메시/단일 배치 진단이다.
- 18개 GLB를 바이너리로 다시 읽어 삼각형·노멀 방향·퇴화면·해시·외부 의존성을 검사했다. 전부 500삼각형 이하, 방향 불일치 0, 퇴화면 0, 외부 텍스처/버퍼 의존성 0이다.

## H1 검 소켓

실제 H1 RightHand와 분리검의 원점/+Y축을 사용했다. 위치 `{socket['position']}`, 회전도 `{socket['rotation_degrees']}`이며, 정확한 원본 및 측정 방식은 [소켓 보고서](h1_socket_correction.json)에 기록했다. 메인 ModelDef는 수정하지 않았다.

idle/walk/attack의 12%,45%,78% 시점 9개를 렌더했다. 반지름 0.18u의 Hips→neck 프록시와 33개 칼날 표본을 비교한 최소 여유는 {minimum:.4f}u다. 이 수치는 실제 스킨 표면의 충돌 검사가 아니다. 손가락 형상·그립 시각 승인은 별도이며, 최종 손아귀 상태는 보고서의 표시를 따른다. 09·10번 캡처는 기존 GT1 오프셋을 복사한 비교용이고, 11번 계열이 H1 측정값이다.

## 남은 한계

'''+ '\n'.join('- '+x for x in limitations)+'''

재현 절차와 원시 로그 위치는 [REPRODUCE.md](REPRODUCE.md)에 있다. 최종 build/render 로그는 오류 0으로 끝났으며 복구한 최초 오류도 원문으로 남겼다.
'''
(BASE/'README.md').write_text(readme,encoding='utf-8')

sections=[('환경 조합',['03_dungeon_assembly','02_town_assembly']),('단색 → TEX01 재질 비교',['12_town_catalog_flat_control','01b_town_catalog','13_town_assembly_flat_control','02_town_assembly','14_props_catalog_flat_control','07_props_catalog']),('카탈로그',['01_dungeon_catalog','01b_town_catalog','07_props_catalog','08_sword_angles']),('가림 비교',['04_occlusion_baseline','05_occlusion_opaque','06_occlusion_cutaway']),('H1 소켓 표본',[f'11_h1_socket_{a}_{i:02d}' for a in ('idle','walk','attack') for i in range(3)]),('기존 GT1 값 비교용',['09_sword_socket','10_sword_socket_closeup'])]
by_id={x['id']:x for x in render['captures']}
cards=[]
for title, ids in sections:
    items=[]
    for ident in ids:
        if ident not in by_id:continue
        item=by_id[ident]
        items.append(f'<figure><a href="{item["file"]}"><img loading="lazy" src="{item["file"]}" alt="{ident}"></a><figcaption>{ident} · ortho {item["ortho_size"]:.1f}</figcaption></figure>')
    cards.append(f'<section><h2>{title}</h2><div class="grid">'+''.join(items)+'</div></section>')
rows=''.join(f'<tr><td><a href="{x["file"]}">{names[x["id"]]}</a></td><td>{fmt(x["vertex_aabb_size"])}</td><td>{x["triangles"]}</td><td><a href="{x["file"].replace(".glb",".json")}">검사 JSON</a></td></tr>' for x in assets)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>H1 3D 환경·소품 후보</title><style>body{margin:0;background:#111315;color:#dedbd1;font:16px/1.65 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:36px 24px}h1{font-size:32px;line-height:1.25}h2{margin-top:40px;font-size:23px}.tag{color:#dbb676;letter-spacing:.08em;font-size:12px}p{max-width:1000px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:20px}figure{margin:0;background:#1b1e20;border:1px solid #363836;border-radius:6px;overflow:hidden}img{display:block;width:100%;height:auto}figcaption{padding:12px 16px;color:#acb1b3;font-size:13px}a{color:#dbb676}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:10px;border-bottom:1px solid #363836}.note{background:#211f1a;padding:18px 22px;border-left:3px solid #aa8751}code{color:#c9c6a6}</style><main><div class="tag">H1 STYLE EXPANSION / LOCAL 3D CANDIDATES</div><h1>환경 14종 + 분리 소품 4종</h1><p>실제 GLB 18개와 Godot 검수 렌더. 현재 게임의 돌 텍스처와 H1의 큰 무광 형태를 연결한 후보입니다. 그림으로 만든 조감도가 아니라, 아래 GLB를 독립 씬에서 렌더했습니다.</p><p><a href="README.md">상세 설명</a> · <a href="qa_report.json">QA 보고서</a> · <a href="manifest.json">전체 목록</a> · <a href="h1_socket_correction.json">H1 소켓 값</a></p><p class="note">게임 반입 전 후보입니다. 목재·한지·옹기·무기는 단색 재질 단계이며 원화의 표면 완성도에 도달하지 않았습니다. 충돌·길찾기·게임플레이는 미검증입니다. 환경은 실제 카메라 ortho 11, 소품·손아귀는 표시된 확대 카메라로 확인하세요.</p>'''+''.join(cards)+'''<section><h2>실제 GLB 파일</h2><table><thead><tr><th>종류</th><th>치수 X×Y×Z (u)</th><th>삼각형</th><th>검사</th></tr></thead><tbody>'''+rows+'''</tbody></table></section></main></html>'''
(BASE/'index.html').write_text(page,encoding='utf-8')
page=page.replace('목재·한지·옹기·무기는 단색 재질 단계이며 원화의 표면 완성도에 도달하지 않았습니다.','목재·기와·회벽·한지에 TEX01 재질을 적용했으며, 옹기·부적은 단색 후보입니다. 아틀라스는 실제 1254²로 1K 규격 합격이 아니며 원화의 표면 완성도에 도달했다고 보증하지 않습니다.')
(BASE/'index.html').write_text(page,encoding='utf-8')
print(json.dumps({'candidate_count':18,'capture_count':len(render['captures']),'all_sources_unchanged':True,'qa_status':qa['status']},ensure_ascii=False))
