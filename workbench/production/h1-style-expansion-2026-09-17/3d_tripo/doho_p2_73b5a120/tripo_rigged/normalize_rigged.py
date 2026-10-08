import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(r'C:\workspace\joseon\tmp\tripo_mixamo_compare')
src=next((ROOT/'candidate_1k').glob('*.fbx'))
out=ROOT/'doho_h1_tripo_p2_rigged_1k_170cm.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(src))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector([min(p[a] for p in points) for a in range(3)])
hi=Vector([max(p[a] for p in points) for a in range(3)])
factor=1.7/(hi.z-lo.z)
offset=Vector((-(hi.x+lo.x)*.5,-(hi.y+lo.y)*.5,-lo.z))*factor
xf=Matrix.Translation(offset)@Matrix.Scale(factor,4)
for obj in list(bpy.context.scene.objects):
    if obj.parent is None:obj.matrix_world=xf@obj.matrix_world
bpy.context.view_layer.update()
for obj in bpy.context.scene.objects:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_yup=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o not in meshes:bpy.data.objects.remove(o,do_unlink=True)
arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
low=[min(p[a] for p in points) for a in range(3)]
high=[max(p[a] for p in points) for a in range(3)]
for o in meshes:o.data.calc_loop_triangles()
report={'source':str(src),'output':str(out),'normalizing_scale':factor,'bones':sum(len(a.data.bones) for a in arms),'meshes':len(meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),'bbox_min':low,'bbox_max':high,'height':high[2]-low[2],'images':[{'name':i.name,'size':list(i.size)} for i in bpy.data.images],'skin_modifiers':sum(m.type=='ARMATURE' for o in meshes for m in o.modifiers),'bytes':out.stat().st_size}
print('RAW_REPORT',json.dumps(report))
assert report['bones']>=41 and report['skin_modifiers']>=1
assert abs(report['height']-1.7)<1e-4 and abs(low[2])<1e-4
assert all(i['size']==[1024,1024] for i in report['images'])
(ROOT/'normalized_rigged_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
# Three full-body views in one orthographic 3D scene.
original=list(bpy.context.scene.objects)
for view,angle,x in [('front',0,-1.5),('side',math.pi/2,0),('back',math.pi,1.5)]:
    lookup={}
    for obj in original:
        clone=obj.copy()
        if obj.data:clone.data=obj.data.copy()
        bpy.context.collection.objects.link(clone)
        lookup[obj]=clone
    for obj,clone in lookup.items():
        clone.parent=lookup.get(obj.parent)
        for mod in clone.modifiers:
            if mod.type=='ARMATURE':mod.object=lookup.get(mod.object,mod.object)
    transform=Matrix.Translation((x,0,0))@Matrix.Rotation(angle,4,'Z')
    for obj,clone in lookup.items():
        if obj.parent is None:clone.matrix_world=transform@obj.matrix_world
for obj in original:bpy.data.objects.remove(obj,do_unlink=True)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.render.resolution_x=1800
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('ReviewWorld')
scene.world.color=(.17,.17,.17)
scene.view_settings.view_transform='Standard'
for pos,power,size in [((-3,-4,5),700,5),((4,-2,3),400,4),((0,3,4),500,4)]:
    bpy.ops.object.light_add(type='AREA',location=pos)
    light=bpy.context.object
    light.data.energy=power;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(Vector((0,0,.8))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-8,.85))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,.85))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=4.6
scene.camera=camera
scene.render.filepath=str(ROOT/'doho_tripo_rigged_front_side_back.png')
bpy.ops.render.render(write_still=True)
