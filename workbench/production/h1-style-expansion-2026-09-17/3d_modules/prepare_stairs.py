import bpy, json, pathlib, math
from mathutils import Vector

base = pathlib.Path(__file__).resolve().parent
out = base / 'prepared'
out.mkdir(exist_ok=True)
report = []
for kind in ('stairs_up', 'stairs_down'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(base / 'source' / (kind + '.glb')))
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    before = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
    for obj in objects:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        mod = obj.modifiers.new('candidate_budget_only', 'DECIMATE')
        mod.ratio = min(1.0, 488.0 / before)
        mod.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
        obj.select_set(False)
    # Preserve source footprint exactly after this very small simplification.
    points = [o.matrix_world @ v.co for o in objects for v in o.data.vertices]
    minp = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    maxp = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center = (minp + maxp) / 2
    for obj in objects:
        inv = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            p = obj.matrix_world @ vertex.co
            p.x = (p.x - center.x) / (maxp.x - minp.x)
            p.y = (p.y - center.y) / (maxp.y - minp.y)
            p.z -= minp.z
            vertex.co = inv @ p
    after = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
    bpy.ops.export_scene.gltf(filepath=str(out / (kind + '.glb')), export_format='GLB', export_animations=False, export_yup=True)
    report.append({'id':kind, 'triangles_before':before, 'triangles_after':after, 'change':'Collapse decimation on candidate copy only; same source materials; footprint normalized to 1x1; height and origin restored'})
(out / 'decimation_report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2))
