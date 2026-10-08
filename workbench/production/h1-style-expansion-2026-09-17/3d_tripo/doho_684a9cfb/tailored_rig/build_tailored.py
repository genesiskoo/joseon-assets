import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SRC=Path(r'C:\workspace\joseon\tmp\tripo_mixamo_compare\new_684a9cfb\mixamo_restored\doho_mixamo25_original_pbr_rigged.blend')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=arm
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
before={b.name:{'head':list(arm.matrix_world@b.head_local),'tail':list(arm.matrix_world@b.tail_local)} for b in arm.data.bones}
bpy.ops.export_scene.gltf(filepath=str(ROOT/'before_body25.glb'),export_format='GLB',use_selection=True,export_skins=True,export_animations=False,export_all_influences=True)
verts=[mesh.matrix_world@v.co for v in mesh.data.vertices]
oldweights=[{mesh.vertex_groups[g.group].name:g.weight for g in v.groups} for v in mesh.data.vertices]
bpy.ops.object.mode_set(mode='EDIT')
specs=[('Hem.L','mixamorig:LeftUpLeg',(.14,0,.92),(.14,0,.52)),('Hem.R','mixamorig:RightUpLeg',(-.14,0,.92),(-.14,0,.52)),('SashTail','mixamorig:Hips',(0,-.16,.99),(0,-.18,.58)),('Sleeve.L','mixamorig:LeftArm',(.30,0,1.36),(.30,0,1.05)),('Sleeve.R','mixamorig:RightArm',(-.30,0,1.36),(-.30,0,1.05))]
inv=arm.matrix_world.inverted()
for name,parent,head,tail in specs:
 b=arm.data.edit_bones.new(name);b.head=inv@Vector(head);b.tail=inv@Vector(tail);b.parent=arm.data.edit_bones[parent];b.use_connect=False
bpy.ops.object.mode_set(mode='OBJECT')
groups={g.name:g for g in mesh.vertex_groups}
for name,_,_,_ in specs:groups[name]=mesh.vertex_groups.new(name=name)
counts={'hat':0,'hem':0,'sash':0,'sleeve':0};changes=[]
for i,p in enumerate(verts):
 w=dict(oldweights[i]);reason=None
 # Black hat vertices above forehead: rigid head, excluding face and hanging cords.
 if p.z>1.535:
  w={'mixamorig:Head':1.};reason='hat'
 elif .55<p.z<.98 and p.y<-.135 and abs(p.x)<.13:
  # Forward hanging sash only, not the whole waist/body.
  w={'SashTail':.85,'mixamorig:Hips':.15};reason='sash'
 elif .48<p.z<.97 and abs(p.x)<.36 and (p.y<-.065 or p.y>.075):
  # Redirect lower-leg weights on robe surfaces to thigh-following auxiliary bones.
  for side in ['Left','Right']:
   names=[f'mixamorig:{side}{n}' for n in ['Leg','Foot','ToeBase','Toe_End']]
   amount=sum(w.pop(n,0) for n in names)
   if amount:w['Hem.'+('L' if side=='Left' else 'R')]=w.get('Hem.'+('L' if side=='Left' else 'R'),0)+amount;reason='hem'
 elif 1.01<p.z<1.32 and .23<abs(p.x)<.50:
  side='Left' if p.x>0 else 'Right';key=f'mixamorig:{side}ForeArm'
  amount=w.get(key,0)*.65
  if amount>.02:w[key]-=amount;w['Sleeve.'+('L' if side=='Left' else 'R')]=amount;reason='sleeve'
 if reason:
  for n in oldweights[i]:groups[n].remove([i])
  total=sum(w.values())
  for n,a in w.items():
   if a>1e-7:groups[n].add([i],a/total,'REPLACE')
  counts[reason]+=1;changes.append({'i':i,'reason':reason})
assert before=={b.name:{'head':list(arm.matrix_world@b.head_local),'tail':list(arm.matrix_world@b.tail_local)} for b in arm.data.bones if b.name in before}
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'tailored_rest.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'tailored_rest.glb'),export_format='GLB',use_selection=True,export_skins=True,export_animations=False,export_all_influences=True)
report={'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'body_joint_policy':'New body Mixamo25 joint head/tail positions retained exactly; no old26 body rig transfer','body_joints_world':before,'added_helpers':specs,'changed_vertex_counts':counts,'changes':changes,'mesh_coordinate_edits':0,'uv_texture_edits':0,'helper_policy':'Rigid parent-following first pass, no physics; lower hem follows thigh instead of calf, sleeves follow upper arm, sash follows hips','status':'candidate, pending actual motion/foot metrics'}
(ROOT/'tailored_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(counts))
