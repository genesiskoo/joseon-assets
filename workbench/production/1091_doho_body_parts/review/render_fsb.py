# 정면·옆·뒤 한 장 — GLB 여러 개를 같은 키 축척으로 나란히 (#1091 리깅 전 확인)
# blender --background --python render_fsb.py -- --glb=a.glb,b.glb --label=새 몸,지금 --out=x.png
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
A = dict(a[2:].split("=", 1) for a in argv if a.startswith("--"))
GLBS = A["glb"].split(",")
OUT = A["out"]
RES = int(A.get("res", 700))

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene

groups = []
for path in GLBS:
    have = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in have]
    for o in new:
        if o.animation_data:
            o.animation_data.action = None
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in new if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    roots = [o for o in new if o.parent is None]
    groups.append((roots, lo, hi, new))
    print(path, "size", tuple(round(v, 3) for v in (hi - lo)))

# 키 1.7로 맞춰 나란히 (발 = z 0)
for k, (roots, lo, hi, new) in enumerate(groups):
    s = 1.7 / (hi.z - lo.z)
    ctr = (lo + hi) / 2
    for r in roots:
        r.location = (r.location - Vector((ctr.x, ctr.y, lo.z))) * s
        r.scale = r.scale * s
    groups[k] = (roots, s)

sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "TEXTURE"
sc.display.shading.show_backface_culling = False
sc.render.resolution_x = RES
sc.render.resolution_y = int(RES * 1.25)
sc.render.film_transparent = False
sc.world = sc.world or bpy.data.worlds.new("w")
sc.render.image_settings.file_format = "PNG"

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.2
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam

views = [("front", Vector((0, -6, 0.85)), (math.radians(90), 0, 0)),
         ("side", Vector((6, 0, 0.85)), (math.radians(90), 0, math.radians(90))),
         ("back", Vector((0, 6, 0.85)), (math.radians(90), 0, math.radians(180)))]
paths = []
objs_by_group = []
for k in range(len(GLBS)):
    pass
# 그룹마다 따로 렌더(나머지 숨김)
all_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for k, (roots, s) in enumerate(groups):
    keep = set()
    stack = list(roots)
    while stack:
        o = stack.pop()
        keep.add(o)
        stack.extend(o.children)
    for o in all_meshes:
        o.hide_render = o not in keep
    for name, loc, rot in views:
        cam.location = loc
        cam.rotation_euler = rot
        p = f"{OUT}_{k}_{name}.png"
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
print("RENDERED", ";".join(paths))
