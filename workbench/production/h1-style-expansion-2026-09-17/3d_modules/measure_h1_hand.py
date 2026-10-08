"""Read-only H1 hand measurement; derived from rig_fix.py's grip geometry.
Unlike rig_fix.py, this does not deform/export any character mesh or change weights.
The palm plane is measured from H1 hand vertices rather than assumed from GT1.
"""
import bpy, pathlib, json, math, numpy as np
from mathutils import Vector

base=pathlib.Path(__file__).resolve().parent
source=pathlib.Path('C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/H1_doho.glb')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
mesh=next(o for o in bpy.data.objects if o.type=='MESH' and 'RightHand' in o.vertex_groups)
arm.data.pose_position='REST'
wrist=arm.matrix_world @ arm.data.bones['RightHand'].head_local
elbow=arm.matrix_world @ arm.data.bones['RightForeArm'].head_local
forward=(wrist-elbow).normalized()
group=mesh.vertex_groups['RightHand'].index
points=[mesh.matrix_world @ v.co for v in mesh.data.vertices if any(g.group==group and g.weight>.65 for g in v.groups)]
length=max((p-wrist).dot(forward) for p in points)
palm=[p for p in points if .15*length<(p-wrist).dot(forward)<.60*length]
arr=np.array([list(p) for p in palm])
eigenvalues,eigenvectors=np.linalg.eigh(np.cov(arr.T))
normal=Vector(eigenvectors[:,0].tolist())
normal=(normal-forward*normal.dot(forward)).normalized()
width=forward.cross(normal).normalized()
distal=[p for p in points if (p-wrist).dot(forward)>.65*length]
mid=sum((p-wrist).dot(width) for p in distal)/len(distal)
base_points=[p for p in points if .15*length<(p-wrist).dot(forward)<.65*length]
high=max((p-wrist).dot(width)-mid for p in base_points)
low=max(mid-(p-wrist).dot(width) for p in base_points)
if low>high: width=-width
# Right hand convention used in rig_fix: finger_dir cross palm_dir = thumb/blade.
palm_direction=width.cross(forward).normalized()
knuckle=.45*length
radius=(length-knuckle)/math.radians(170)
knuckle_origin=wrist+forward*knuckle
fingers=[p for p in points if (p-wrist).dot(forward)>knuckle]
wmid=sum((p-knuckle_origin).dot(width) for p in fingers)/len(fingers)
grip=knuckle_origin+width*wmid+palm_direction*radius
def v(value):return [round(float(c),7) for c in value]
report={'Right':{'grip':v(grip),'blade_dir':v(width),'width_dir':v(forward),'wrist':v(wrist),'hand_len':length,'R':radius,'fingers':len(fingers),'coords':'blender world (z up, -y front)','palm_dir':v(palm_direction)},'measurement':{'source':str(source),'method':'H1 weighted hand vertices (>0.65); palm covariance thin axis; thumb-side sign from proximal excess relative to distal fingers; rig_fix knuckle=.45,curl=170 geometry; no mesh deformation','vertex_count':len(points),'palm_vertex_count':len(palm),'palm_covariance_eigenvalues':eigenvalues.tolist(),'thumb_extent_positive':high,'thumb_extent_negative':low,'assumption':'Grip is the expected curl-axis center for an open hand, not closed-finger contact proof','main_assets_modified':False}}
(base/'h1_hand_measured_fist.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
