import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'doho_tailored_candidate.glb'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and o not in meshes:bpy.data.objects.remove(o,do_unlink=True)
scene=bpy.context.scene;ad=arm.animation_data;ad.action=None
hips=next(b for b in arm.pose.bones if b.name.endswith('Hips'))
feet=[next(b for b in arm.pose.bones if b.name.endswith(s+'Foot')) for s in ['Left','Right']]
def select(track):
 for t in ad.nla_tracks:t.mute=t!=track
def sample(track,f):
 scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get();vals=[]
 for o in meshes:
  ev=o.evaluated_get(dg);me=ev.to_mesh();vals.extend((ev.matrix_world@v.co).z for v in me.vertices);ev.to_mesh_clear()
 return {'frame':f,'min_z':min(vals),'feet':[list(arm.matrix_world@b.matrix.translation) for b in feet]}
report={}
for name in ['walk','run']:
 track=next(t for t in ad.nla_tracks if t.name==name);select(track);s=track.strips[0]
 rows=[sample(track,s.frame_start+(s.frame_end-s.frame_start)*i/32) for i in range(33)]
 report[name]={'sole_min':min(r['min_z'] for r in rows),'sole_max':max(r['min_z'] for r in rows),'samples':rows}
(ROOT/'final_contact_check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for t in ad.nla_tracks:t.mute=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'tailored_motion_candidate.blend'))
print('FINAL_CONTACT',json.dumps({n:{k:v for k,v in r.items() if k!='samples'} for n,r in report.items()}),flush=True)
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=850;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Review');scene.world.color=(.17,.17,.17);scene.view_settings.view_transform='Standard'
for pos,power in [((-3,-4,5),700),((4,-2,3),400),((0,3,4),500)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=4;o.rotation_euler=(Vector((0,0,.85))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.3,-7,.95));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.3;scene.camera=cam
for name in ['walk','run']:
 track=next(t for t in ad.nla_tracks if t.name==name);select(track);s=track.strips[0]
 for fraction in [0,.25,.5,.75]:
  f=s.frame_start+(s.frame_end-s.frame_start)*fraction;scene.frame_set(int(f),subframe=f-int(f))
  scene.render.filepath=str(ROOT/f'{name}_{int(fraction*100):02}.png');bpy.ops.render.render(write_still=True)

