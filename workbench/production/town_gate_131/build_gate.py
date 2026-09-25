"""Deterministic #131 cave gate assembly; run from this directory in Blender 5.2."""
from pathlib import Path
from math import pi
import random
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
OUT = ROOT / "town_sealed_threshold.glb"
PREVIEW = ROOT / "preview"
PREVIEW.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(131)


def material(name, color, roughness=0.9, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


stone = material("dark_blue_stone", (0.085, 0.105, 0.125))
stone_edge = material("cut_stone_edge", (0.105, 0.120, 0.130))
wood = material("aged_reinforcement_wood", (0.092, 0.069, 0.052))
socket_dark = material("empty_fragment_recess", (0.028, 0.035, 0.043))
socket_lip = material("fragment_socket_lip", (0.18, 0.225, 0.235))
fissure = material("cold_fissure_low_energy", (0.065, 0.19, 0.25), emission=0.45)
model_objects = []

# Small embedded stone albedo, seeded and repeatable. Broad noise prevents the
# new cut blocks from reading as clean flat boxes beside the graded cave rock.
rng = np.random.default_rng(131)
coarse = rng.random((32, 32), dtype=np.float32)
coarse = np.repeat(np.repeat(coarse, 8, axis=0), 8, axis=1)
for _ in range(4):
    coarse = (coarse + np.roll(coarse, 1, 0) + np.roll(coarse, -1, 0) + np.roll(coarse, 1, 1) + np.roll(coarse, -1, 1)) / 5
fine = rng.random((256, 256), dtype=np.float32)
level = np.clip(.68 + .38*(coarse-.5) + .12*(fine-.5), .48, .92)
rgba = np.stack((.19*level, .225*level, .25*level, np.ones_like(level)), axis=-1)
image = bpy.data.images.new("cut_stone_grain_131", width=256, height=256, alpha=True)
image.pixels.foreach_set(rgba.astype(np.float32).ravel())
image.pack()
tex = stone.node_tree.nodes.new("ShaderNodeTexImage")
tex.image = image
stone.node_tree.links.new(tex.outputs["Color"], stone.node_tree.nodes["Principled BSDF"].inputs["Base Color"])


def import_asset(name, filename, position=(0, 0, 0), scale=(1, 1, 1)):
    old = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE / filename))
    imported = sorted(set(bpy.data.objects) - old, key=lambda ob: ob.name)
    anchor = bpy.data.objects.new(name + "_anchor", None)
    bpy.context.collection.objects.link(anchor)
    anchor.location = position
    anchor.scale = scale
    for ob in imported:
        if ob.parent not in imported:
            ob.parent = anchor
    model_objects.extend(imported)
    model_objects.append(anchor)
    return [ob for ob in imported if ob.type == "MESH"]


def box(name, center, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("worn_edges", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    model_objects.append(ob)
    return ob


def line(name, points, radius, mat):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for pt, point in zip(spline.points, points):
        pt.co = (*point, 1)
    ob = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    model_objects.append(ob)
    return ob


def rock(name, center, scale, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.rotation_euler = tuple(random.uniform(-0.25, 0.25) for _ in range(3))
    ob.data.materials.append(mat)
    model_objects.append(ob)


# Existing graded rock is the full silhouette; stone door sits in the cave mouth.
cave_meshes = import_asset("reused_cave_arch_321", "cave_arch.glb")
door_meshes = import_asset("reused_seal_door_13", "seal_door.glb", (0, -0.42, 0), (1.51, 1, 1.07))
# The original 10,212-triangle rock can lose 6% without erasing its stone
# silhouette. This leaves room for the door/frame within the 12k prop budget.
for ob in cave_meshes:
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    modifier = ob.modifiers.new("gentle_rock_decimation", "DECIMATE")
    modifier.ratio = .94
    bpy.ops.object.modifier_apply(modifier=modifier.name)

# The original 1m stairs are wood-plank coloured and 0.61u tall: both clash
# with the concept and flat navigation plane. The inspected source is retained
# for provenance but replaced by a shallow worn-stone apron in this candidate.
for row, (y, centers, widths) in enumerate((
    (-1.38, (-.58,.55), (1.04,1.10)),
    (-1.84, (-.74,0,.73), (.64,.64,.64)),
    (-2.28, (-.57,.52), (1.02,1.01)),
    (-2.72, (-.73,.02,.71), (.62,.66,.60)),
    (-3.10, (-.48,.49), (.84,.86)),
)):
    for col, (x, width) in enumerate(zip(centers, widths)):
        ob = box(f"shallow_stone_step_{row}_{col}", (x,y,.035), (width, .42, .068), stone, .025)
        ob.rotation_euler.z = random.uniform(-.025,.025)

# Cut-stone frame and quiet wooden backing make the old slab part of the cave.
for side in (-1, 1):
    box(f"stone_jamb_{side}", (side * 1.18, -0.88, 1.15), (.22, .31, 2.27), stone, .035)
    box(f"timber_reinforcement_{side}", (side * 1.36, -0.50, 1.14), (.13, .20, 2.33), wood, .015)
box("broken_lintel", (0, -0.83, 2.29), (2.55, .36, .28), stone, .038)
box("threshold_sill", (0, -1.03, .075), (2.46, .47, .15), stone, .020)
box("three_fragment_socket_plate", (-.12, -.654, 1.13), (1.90, .08, .64), stone, .022)

# Three EMPTY sockets in one readable row. No collected fragment is shown.
for index, x in enumerate((-.55, -.12, .31), 1):
    z = 1.13
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.202, depth=.038, location=(x, -0.717, z), rotation=(pi / 2, 0, 0))
    lip = bpy.context.object
    lip.name = f"empty_fragment_socket_{index}_lip"
    lip.data.materials.append(socket_lip)
    model_objects.append(lip)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.146, depth=.043, location=(x, -0.738, z), rotation=(pi / 2, 0, 0))
    recess = bpy.context.object
    recess.name = f"empty_fragment_socket_{index}_dark"
    recess.data.materials.append(socket_dark)
    model_objects.append(recess)

# A thin cracked seam is the only cold glow; local light is a placement choice.
line("cracked_blue_fissure", ((.08,-.69,2.13),(.025,-.69,1.96),(.10,-.69,1.82),(.04,-.69,1.58),(-.035,-.69,1.47)), .009, fissure)
line("cracked_blue_fissure_lower", ((.07,-.69,.75),(.00,-.69,.55),(.045,-.69,.22)), .009, fissure)

# Cave arch already includes a rope with hanging paper seals. Repeating it on
# the door obscured the three empty sockets, so no second rope is generated.

# Damage and side debris stop at the edge of the 2u central clickable lane.
for side in (-1, 1):
    for i in range(7):
        x = side * (1.38 + .13*(i % 3) + random.uniform(0,.18))
        y = -1.22 - .23*(i//3) + random.uniform(-.08,.08)
        s = random.uniform(.12,.24)
        rock(f"rubble_{side}_{i}", (x,y,s*.42), (s*1.35,s,s*.72), stone_edge if i % 3 == 0 else stone)
for i,(x,y,w,d) in enumerate(((-.76,-3.04,.72,.35),(.18,-3.05,.65,.37),(.80,-2.65,.48,.30),(-.80,-2.25,.36,.26))):
    box(f"broken_step_{i}", (x,y,.032), (w,d,.060), stone, .014)

# Merge authored pieces by material. Keeping dozens of tiny rock and socket
# meshes separate is costly in the town camera even if triangle count is fine.
from collections import defaultdict
for ob in model_objects:
    if ob.type == "MESH" and ob not in cave_meshes and ob not in door_meshes:
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
groups = defaultdict(list)
for ob in model_objects:
    if ob.type == "MESH" and ob not in cave_meshes and ob not in door_meshes and len(ob.data.materials) == 1:
        groups[ob.data.materials[0].name].append(ob)
for mat_name, group in groups.items():
    if len(group) < 2:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    for ob in group:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = group[0]
    bpy.ops.object.join()
    group[0].name = mat_name + "_merged"
    for ob in group[1:]:
        model_objects.remove(ob)

bpy.context.view_layer.update()
verts = [ob.matrix_world @ Vector(corner) for ob in model_objects if ob.type == "MESH" for corner in ob.bound_box]
lo = Vector(min(v[i] for v in verts) for i in range(3))
hi = Vector(max(v[i] for v in verts) for i in range(3))
triangles = sum(len(ob.data.polygons) for ob in model_objects if ob.type == "MESH")
print("GATE_ASSET_BOUNDS", tuple(round(v,3) for v in lo), tuple(round(v,3) for v in hi), "mesh_faces", triangles)

bpy.ops.object.select_all(action="DESELECT")
for ob in model_objects:
    ob.select_set(True)
bpy.context.view_layer.objects.active = model_objects[0]
bpy.ops.export_scene.gltf(filepath=str(OUT), export_format="GLB", use_selection=True, export_apply=True)

# Isometric-ish neutral preview. The final verdict uses in-game fixed shots.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.035))
floor = bpy.context.object
floor.name = "preview_only_floor"
floor.data.materials.append(material("preview_earth", (.075,.078,.077)))
for location, energy, size in (((-3,-5,8),1200,7),((4,2,7),650,6)):
    data = bpy.data.lights.new("preview_area", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    ob = bpy.data.objects.new("preview_area", data)
    bpy.context.collection.objects.link(ob)
    ob.location = location
    ob.rotation_euler = (Vector((0,-1,1))-ob.location).to_track_quat("-Z","Y").to_euler()
cam_data = bpy.data.cameras.new("preview_camera")
cam = bpy.data.objects.new("preview_camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (6,-8,5.8)
cam.rotation_euler = (Vector((0,-.8,1.25))-cam.location).to_track_quat("-Z","Y").to_euler()
cam_data.type = "ORTHO"
cam_data.ortho_scale = 7.7
scene = bpy.context.scene
scene.camera = cam
scene.world = bpy.data.worlds.new("preview_world")
scene.world.color = (.1,.12,.14)
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW / "gate_neutral.png")
bpy.ops.render.render(write_still=True)
