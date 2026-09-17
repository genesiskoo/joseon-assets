"""Blender --background --python prepare_candidates.py -- --src=<ZIP or FBX>
Only writes under this script's directory. Never overwrites the source.
Decimation keeps existing UV/material data and vertex groups, but requires visual
and animated deformation review; reduced UV interpolation is not pixel-identical.
"""
import bpy, sys, json, zipfile, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parent
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
opts=dict(a[2:].split('=',1) for a in argv if a.startswith('--') and '=' in a)
if 'src' not in opts:
    raise RuntimeError('Explicit --src=<downloaded ZIP or FBX> required; no automatic file selection')
src=Path(opts['src']).resolve()
assert src.exists()
source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
if src.suffix.lower()=='.zip':
    extract=(ROOT/'source_extracted').resolve()
    with zipfile.ZipFile(src) as z:
        for e in z.infolist():
            if not (extract/e.filename).resolve().is_relative_to(extract):raise RuntimeError('Unsafe ZIP path')
            if ((e.external_attr>>16)&0o170000)==0o120000:raise RuntimeError('ZIP symlink rejected')
        z.extractall(extract)
    choices=list(extract.rglob('*.fbx'))
    assert len(choices)==1, f'Expected one FBX, found {choices}'
    fbx=choices[0]
else:
    assert src.suffix.lower()=='.fbx'
    fbx=src

def inspect():
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    low=[min(p[i] for p in pts) for i in range(3)]
    high=[max(p[i] for p in pts) for i in range(3)]
    for o in meshes:o.data.calc_loop_triangles()
    return {'meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),
       'bones':{o.name:[b.name for b in o.data.bones] for o in arms},'actions':[a.name for a in bpy.data.actions],
       'images':[{'name':i.name,'size':list(i.size),'path':i.filepath} for i in bpy.data.images],
       'uv_layers':{o.name:[u.name for u in o.data.uv_layers] for o in meshes},'bbox_min':low,'bbox_max':high,'height':high[2]-low[2]}

def render_triptych(path):
    original=list(bpy.context.scene.objects)
    for angle,x in [(0,-1.5),(math.pi/2,0),(math.pi,1.5)]:
        copies={}
        for obj in original:
            c=obj.copy()
            if obj.data:c.data=obj.data.copy()
            bpy.context.collection.objects.link(c);copies[obj]=c
        for obj,c in copies.items():
            c.parent=copies.get(obj.parent)
            for m in c.modifiers:
                if m.type=='ARMATURE':m.object=copies.get(m.object,m.object)
        xf=Matrix.Translation((x,0,0))@Matrix.Rotation(angle,4,'Z')
        for obj,c in copies.items():
            if obj.parent is None:c.matrix_world=xf@obj.matrix_world
    for o in original:bpy.data.objects.remove(o,do_unlink=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.render.resolution_x=1800;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.color=(.17,.17,.17)
    scene.view_settings.view_transform='Standard'
    for pos,power,size in [((-3,-4,5),700,5),((4,-2,3),400,4),((0,3,4),500,4)]:
        bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object
        o.data.energy=power;o.data.shape='DISK';o.data.size=size
        o.rotation_euler=(Vector((0,0,.85))-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(0,-8,.85));o=bpy.context.object
    o.rotation_euler=(Vector((0,0,.85))-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.type='ORTHO';o.data.ortho_scale=4.6;scene.camera=o
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)

reports=[]
for target in [12000,20000]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    before=inspect()
    assert before['bones'], 'Downloaded source has no rig'
    (ROOT/'source_inspection.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
    print('SOURCE_INSPECTION',json.dumps(before),flush=True)
    assert before['images'] and all(min(i['size'])>0 for i in before['images']), 'Missing texture pixels'
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    total=before['triangles']
    for obj in meshes:
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        dec=obj.modifiers.new('CandidateReduction','DECIMATE');dec.decimate_type='COLLAPSE'
        dec.ratio=min(1.0,target/total);dec.use_collapse_triangulate=True
        # Place before armature so evaluation does not bake the posed deformation.
        bpy.ops.object.modifier_move_to_index(modifier=dec.name,index=0)
        bpy.ops.object.modifier_apply(modifier=dec.name)
    reduced=inspect()
    low=Vector(reduced['bbox_min']);high=Vector(reduced['bbox_max']);factor=1.7/reduced['height']
    offset=Vector((-(low.x+high.x)*.5,-(low.y+high.y)*.5,-low.z))*factor
    xf=Matrix.Translation(offset)@Matrix.Scale(factor,4)
    for o in bpy.context.scene.objects:
        if o.parent is None:o.matrix_world=xf@o.matrix_world
    bpy.context.view_layer.update()
    candidate=inspect()
    assert before['bones']==candidate['bones']
    assert abs(candidate['height']-1.7)<1e-4
    stem=f'doho_684a9cfb_{target//1000}k_rigged_originaltex_170cm'
    out=ROOT/(stem+'.glb')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_skins=True,export_animations=False,export_yup=True)
    entry={'target_triangles':target,'source':str(src),'source_sha256':source_sha,'source_inspection':before,'candidate_inspection':candidate,
       'glb':str(out),'glb_bytes':out.stat().st_size,'note':'UV layers, texture image files and original rig retained; collapsed topology needs deformation/visual QA'}
    reports.append(entry)
    (ROOT/'candidate_reports.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
    if target==12000:
        # Save rigged scene first; modify only this in-memory copy for Mixamo.
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'candidate_12k_rigged.blend'))
        for o in meshes:
            world=o.matrix_world.copy();o.parent=None;o.matrix_world=world
            for m in list(o.modifiers):
                if m.type=='ARMATURE':o.modifiers.remove(m)
            o.vertex_groups.clear();o.animation_data_clear()
        for o in list(bpy.context.scene.objects):
            if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
        static=ROOT/'doho_684a9cfb_12k_textured_static_mixamo.fbx'
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.fbx(filepath=str(static),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,
          apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,mesh_smooth_type='OFF',
          add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
        entry['mixamo_static_fbx']=str(static)
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'candidate_12k_rigged.blend'))
    render_triptych(ROOT/(stem+'_front_side_back.png'))
    (ROOT/'candidate_reports.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
assert hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
print('CANDIDATES_COMPLETE',json.dumps([{'triangles':r['candidate_inspection']['triangles'],'glb':r['glb']} for r in reports]))
