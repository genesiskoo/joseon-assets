import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
OLD=Path(r'C:\workspace\joseon\assets\models\doho\doho.glb')
NEW=Path(r'C:\workspace\joseon\tmp\tripo_mixamo_compare\new_684a9cfb\mixamo_restored\doho_mixamo25_original_pbr_rigged.blend')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OLD))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
old=next(o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o!=old:bpy.data.objects.remove(o,do_unlink=True)
rest={b.name:[list(row) for row in b.matrix_local] for b in arm.data.bones}
tracks=[{'name':t.name,'strips':[{'name':s.name,'start':s.frame_start,'end':s.frame_end} for s in t.strips]} for t in arm.animation_data.nla_tracks]
arm.data.pose_position='REST'
with bpy.data.libraries.load(str(NEW),link=False) as (available,loaded):
    loaded.objects=list(available.objects)
for obj in loaded.objects:
    if obj:bpy.context.collection.objects.link(obj)
bpy.context.view_layer.update()
new=next(o for o in loaded.objects if o and o.type=='MESH')
world=new.matrix_world.copy();new.parent=None;new.matrix_world=world
for obj in loaded.objects:
    if obj and obj!=new:bpy.data.objects.remove(obj,do_unlink=True)
for mod in list(new.modifiers):new.modifiers.remove(mod)
new.vertex_groups.clear();new.animation_data_clear()
bpy.context.view_layer.update()
# Convert both rest surfaces to same world coordinate system; align height/foot/center only.
def box(obj):
    p=[obj.matrix_world@v.co for v in obj.data.vertices]
    return Vector([min(v[i] for v in p) for i in range(3)]),Vector([max(v[i] for v in p) for i in range(3)])
lo,hi=box(old);nl,nh=box(new)
scale=(hi.z-lo.z)/(nh.z-nl.z)
offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))-Vector(((nl.x+nh.x)/2,(nl.y+nh.y)/2,nl.z))*scale
new.matrix_world=Matrix.Translation(offset)@Matrix.Scale(scale,4)@new.matrix_world
bpy.ops.object.select_all(action='DESELECT');new.select_set(True);bpy.context.view_layer.objects.active=new
dt=new.modifiers.new('ExistingSurfaceWeights','DATA_TRANSFER');dt.object=old;dt.use_vert_data=True;dt.data_types_verts={'VGROUP_WEIGHTS'};dt.vert_mapping='POLYINTERP_NEAREST'
bpy.ops.object.datalayout_transfer(modifier=dt.name)
bpy.ops.object.modifier_apply(modifier=dt.name)
world=new.matrix_world.copy();new.parent=arm;new.matrix_world=world
mod=new.modifiers.new('ExistingGameRig','ARMATURE');mod.object=arm
weights=[]
for v in new.data.vertices:
    weights.append(sum(g.weight for g in v.groups))
new.data.calc_loop_triangles()
report={'source_game_glb':str(OLD),'source_game_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'source_visual_blend':str(NEW),'source_visual_sha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),'bone_count':len(rest),'bone_rest_before':rest,'animation_tracks_before':tracks,'method':'Nearest source polygon interpolated vertex-group transfer in aligned rest world coordinates; no retarget or new rig','alignment_scale':scale,'alignment_offset':list(offset),'target_rest_aabb':[list(lo),list(hi)],'new_triangles':len(new.data.loop_triangles),'new_vertices':len(new.data.vertices),'unweighted':sum(w<1e-6 for w in weights),'weight_sum_range':[min(weights),max(weights)]}
assert not report['unweighted']
bpy.data.objects.remove(old,do_unlink=True)
arm.data.pose_position='POSE';arm.animation_data.action=None
assert rest=={b.name:[list(row) for row in b.matrix_local] for b in arm.data.bones}
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'existing_rig_new_visual.blend'))
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);new.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'existing_rig_new_visual_blender.glb'),export_format='GLB',use_selection=True,export_skins=True,export_all_influences=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_yup=True)
(ROOT/'transfer_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('TRANSFER',json.dumps({k:v for k,v in report.items() if k not in ['bone_rest_before','animation_tracks_before']}),flush=True)
# Render the original stored NLA clips directly, without rewriting animation.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Review');scene.world.color=(.17,.17,.17);scene.view_settings.view_transform='Standard'
for pos,power in [((-3,-4,5),700),((4,-2,3),400),((0,3,4),500)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=4
    o.rotation_euler=(Vector((0,0,.85))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.3,-7,.95));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.4;scene.camera=cam
for key in ['idle','walk','run','attack','hit','die']:
    track=next((t for t in arm.animation_data.nla_tracks if key==t.name or t.name.startswith(key)),None)
    if track is None:continue
    for t in arm.animation_data.nla_tracks:t.mute=t!=track
    s=track.strips[0];f=s.frame_start+(s.frame_end-s.frame_start)*.5;scene.frame_set(int(f),subframe=f-int(f))
    scene.render.filepath=str(ROOT/f'{key}_50.png');bpy.ops.render.render(write_still=True)
