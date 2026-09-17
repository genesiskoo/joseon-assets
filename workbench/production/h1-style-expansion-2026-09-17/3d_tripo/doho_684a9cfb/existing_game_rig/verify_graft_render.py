import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'doho_existing_rig_new_visual_exact_anims.glb'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and not any(m.type=='ARMATURE' for m in o.modifiers):bpy.data.objects.remove(o,do_unlink=True)
arm.animation_data.action=None
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Review');scene.world.color=(.17,.17,.17);scene.view_settings.view_transform='Standard'
for pos,power in [((-3,-4,5),700),((4,-2,3),400),((0,3,4),500)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=4
    o.rotation_euler=(Vector((0,0,.85))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.3,-7,.95));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.4;scene.camera=cam
for key in ['idle','walk']:
    track=next((t for t in arm.animation_data.nla_tracks if key==t.name or t.name.startswith(key)),None)
    if track is None:continue
    for t in arm.animation_data.nla_tracks:t.mute=t!=track
    s=track.strips[0];f=s.frame_start+(s.frame_end-s.frame_start)*.5;scene.frame_set(int(f),subframe=f-int(f))
    scene.render.filepath=str(ROOT/f'exact_graft_{key}_50.png');bpy.ops.render.render(write_still=True)
