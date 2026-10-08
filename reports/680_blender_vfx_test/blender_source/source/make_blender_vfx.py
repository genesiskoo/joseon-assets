"""#680: real Blender procedural 3D volumes, not a fluid solver bake.
Run Blender --background --factory-startup --python this_file -- --root PATH --mode preview|full.
Fixed 384 RGBA camera canvas. 28 raw frames = one periodic 24-frame cycle + 4 tail frames;
pack_atlases.py performs premultiplied-alpha 4-frame loop overlap, retaining 24 frames.
"""
import argparse, json, math, random, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

SEED = 680
random.seed(SEED)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
parser.add_argument('--mode', choices=['preview', 'full'], default='preview')
parser.add_argument('--effect', choices=['fire', 'sal', 'all'], default='all')
parser.add_argument('--size', type=int, default=384)
parser.add_argument('--samples', type=int, default=64)
args = parser.parse_args(argv)
ROOT = Path(args.root)
(ROOT / 'previews').mkdir(parents=True, exist_ok=True)
(ROOT / 'blends').mkdir(parents=True, exist_ok=True)
(ROOT / 'frames').mkdir(parents=True, exist_ok=True)
(ROOT / 'staged' / 'assets' / 'vfx' / 'blender_hybrid').mkdir(parents=True, exist_ok=True)


def n(nt, kind, name):
    node = nt.nodes.new(kind)
    node.name = name
    node.label = name
    return node


def link(nt, source, target):
    nt.links.new(source, target)


def scalar(nt, op, a, b=None, name=None):
    node = n(nt, 'ShaderNodeMath', name or op)
    node.operation = op
    for i, value in enumerate([a, b]):
        if value is None:
            continue
        if isinstance(value, (float, int)):
            node.inputs[i].default_value = float(value)
        else:
            link(nt, value, node.inputs[i])
    return node.outputs[0]


def vec(nt, op, a, b=None, scale=None, name=None):
    node = n(nt, 'ShaderNodeVectorMath', name or op)
    node.operation = op
    for i, value in enumerate([a, b]):
        if value is None:
            continue
        if isinstance(value, (tuple, list, Vector)):
            node.inputs[i].default_value = value
        else:
            link(nt, value, node.inputs[i])
    if scale is not None:
        if isinstance(scale, (float, int)):
            node.inputs['Scale'].default_value = scale
        else:
            link(nt, scale, node.inputs['Scale'])
    return node.outputs['Value' if op in ['LENGTH', 'DISTANCE', 'DOT_PRODUCT'] else 'Vector']


def clamp(nt, a):
    return scalar(nt, 'MINIMUM', scalar(nt, 'MAXIMUM', a, 0.0), 1.0)


def noise(nt, coords, scale, detail, phase, label):
    node = n(nt, 'ShaderNodeTexNoise', label)
    node.noise_dimensions = '4D'
    node.inputs['Scale'].default_value = scale
    node.inputs['Detail'].default_value = detail
    node.inputs['Roughness'].default_value = 0.65
    if 'Distortion' in node.inputs:
        node.inputs['Distortion'].default_value = 0.35
    link(nt, coords, node.inputs['Vector'])
    link(nt, phase, node.inputs['W'])
    return node


def colors(nt, factor, points, label):
    ramp = n(nt, 'ShaderNodeValToRGB', label)
    ramp.color_ramp.interpolation = 'EASE'
    while len(ramp.color_ramp.elements) > 2:
        ramp.color_ramp.elements.remove(ramp.color_ramp.elements[-1])
    for i, (at, color) in enumerate(points):
        e = ramp.color_ramp.elements[i] if i < 2 else ramp.color_ramp.elements.new(at)
        e.position = at
        e.color = (*color, 1.0)
    link(nt, factor, ramp.inputs['Fac'])
    return ramp.outputs['Color']


def periodic_controls(nt):
    phase = n(nt, 'ShaderNodeValue', 'phase_W')
    shift = n(nt, 'ShaderNodeCombineXYZ', 'phase_shift')
    return phase, shift


def update_phase(mat, frame):
    phi = 2.0 * math.pi * frame / 24.0
    nt = mat.node_tree
    nt.nodes['phase_W'].outputs[0].default_value = SEED * 0.013 + math.cos(phi) * 0.85
    nt.nodes['phase_shift'].inputs['X'].default_value = math.sin(phi) * 0.18
    nt.nodes['phase_shift'].inputs['Y'].default_value = math.cos(phi) * 0.12
    nt.nodes['phase_shift'].inputs['Z'].default_value = math.sin(phi + 0.7) * 0.09


def material(effect):
    mat = bpy.data.materials.new(effect + '_procedural_3d_volume')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = n(nt, 'ShaderNodeOutputMaterial', 'Volume_only_output')
    pv = n(nt, 'ShaderNodeVolumePrincipled', 'Participating_medium')
    pv.inputs['Anisotropy'].default_value = 0.25 if effect == 'sal' else 0.1
    tc = n(nt, 'ShaderNodeTexCoord', 'Fixed_volume_coordinates')
    phase, shift = periodic_controls(nt)
    coords = vec(nt, 'ADD', tc.outputs['Generated'], shift.outputs[0], name='Looped_advection')
    warp = noise(nt, coords, 3.2, 3.0, phase.outputs[0], 'Large_4D_domain_warp')
    warpv = vec(nt, 'SCALE', vec(nt, 'SUBTRACT', warp.outputs['Color'], (0.5, 0.5, 0.5)), scale=0.27 if effect == 'sal' else 0.15)
    q = vec(nt, 'ADD', tc.outputs['Generated'], warpv, name='Turbulent_density_coordinates')
    fine = noise(nt, coords, 7.0 if effect == 'sal' else 6.0, 4.0, phase.outputs[0], 'Fine_turbulence')
    sep = n(nt, 'ShaderNodeSeparateXYZ', 'Coordinates')
    link(nt, q, sep.inputs[0])
    x, y, z = [sep.outputs[k] for k in ['X', 'Y', 'Z']]
    if effect == 'fire':
        rawsep = n(nt, 'ShaderNodeSeparateXYZ', 'Fixed_source_tail_bounds')
        link(nt, tc.outputs['Generated'], rawsep.inputs[0])
        rawx = rawsep.outputs['X']
        spread = scalar(nt, 'POWER', clamp(nt, scalar(nt, 'SUBTRACT', 1.0, rawx)), 0.72)
        radius = scalar(nt, 'ADD', 0.027, scalar(nt, 'MULTIPLY', spread, 0.22), 'Jet_radius')
        phasewave = scalar(nt, 'ADD', scalar(nt, 'MULTIPLY', rawx, 12.0), phase.outputs[0])
        wave = scalar(nt, 'MULTIPLY', scalar(nt, 'SINE', phasewave), scalar(nt, 'MULTIPLY', spread, 0.05))
        zcenter = scalar(nt, 'ADD', 0.5, wave)
        yy, zz = scalar(nt, 'SUBTRACT', y, 0.5), scalar(nt, 'SUBTRACT', z, zcenter)
        radial = scalar(nt, 'SQRT', scalar(nt, 'ADD', scalar(nt, 'MULTIPLY', yy, yy), scalar(nt, 'MULTIPLY', zz, zz)), name='Radial_distance')
        edge = clamp(nt, scalar(nt, 'DIVIDE', scalar(nt, 'SUBTRACT', radius, radial), 0.09))
        end_fade = scalar(nt, 'POWER', clamp(nt, scalar(nt, 'DIVIDE', scalar(nt, 'SUBTRACT', rawx, 0.045), 0.38)), 2.0)
        grain = scalar(nt, 'POWER', clamp(nt, scalar(nt, 'DIVIDE', scalar(nt, 'SUBTRACT', fine.outputs['Fac'], 0.40), 0.22)), 1.7)
        body = scalar(nt, 'MULTIPLY', scalar(nt, 'MULTIPLY', scalar(nt, 'POWER', edge, 1.4), end_fade), grain, 'Broken_turbulent_flame_body')
        branches = None
        for sign in [-1.0, 1.0]:
            separation = scalar(nt, 'MULTIPLY', scalar(nt, 'MULTIPLY', spread, spread), sign * 0.19)
            branchz = scalar(nt, 'ADD', zcenter, separation)
            bz = scalar(nt, 'SUBTRACT', z, branchz)
            by = scalar(nt, 'SUBTRACT', y, 0.5)
            br = scalar(nt, 'SQRT', scalar(nt, 'ADD', scalar(nt, 'MULTIPLY', by, by), scalar(nt, 'MULTIPLY', bz, bz)))
            tube = clamp(nt, scalar(nt, 'DIVIDE', scalar(nt, 'SUBTRACT', 0.04, br), 0.028))
            ribbon = scalar(nt, 'MULTIPLY', scalar(nt, 'MULTIPLY', tube, end_fade), grain, 'Frayed_curved_branch_' + str(sign))
            branches = ribbon if branches is None else scalar(nt, 'ADD', branches, ribbon)
        body_branches = scalar(nt, 'ADD', body, scalar(nt, 'MULTIPLY', branches, 0.65))
        density = scalar(nt, 'MULTIPLY', body_branches, 4.4, 'Volume_density')
        core_radius = scalar(nt, 'ADD', 0.019, scalar(nt, 'MULTIPLY', spread, 0.021))
        core = scalar(nt, 'MULTIPLY', clamp(nt, scalar(nt, 'DIVIDE', scalar(nt, 'SUBTRACT', core_radius, radial), 0.024)), end_fade, 'Narrow_hot_core')
        heat = clamp(nt, scalar(nt, 'ADD', scalar(nt, 'MULTIPLY', core, 0.84), scalar(nt, 'MULTIPLY', fine.outputs['Fac'], 0.32)))
        color = colors(nt, heat, [(0.0, (0.015, 0.001, 0.001)), (0.23, (0.15, 0.012, 0.001)), (0.47, (1.0, 0.10, 0.003)), (0.72, (2.5, 0.62, 0.01)), (1.0, (5.0, 3.9, 1.2))], 'Fire_black_red_orange_white_temperature')
        link(nt, color, pv.inputs['Color'])
        link(nt, color, pv.inputs['Emission Color'])
        glow = scalar(nt, 'ADD', scalar(nt, 'MULTIPLY', body_branches, 0.28), scalar(nt, 'MULTIPLY', core, 5.0), 'Bright_core_broken_boundary')
        link(nt, glow, pv.inputs['Emission Strength'])
    else:
        # Five separate billowing ellipsoids with negative spaces, not a uniform ball.
        envelope = None
        lobes = [((0.28, 0.5, 0.42), 0.175), ((0.43, 0.52, 0.56), 0.21), ((0.6, 0.50, 0.6), 0.175), ((0.7, 0.5, 0.40), 0.14), ((0.51, 0.49, 0.42), 0.19)]
        for i, (center, radius) in enumerate(lobes):
            off = vec(nt, 'SUBTRACT', q, center)
            ellipsoid = vec(nt, 'MULTIPLY', off, (1.0, 1.65, 1.40))
            r = vec(nt, 'LENGTH', ellipsoid)
            lobe = clamp(nt, scalar(nt, 'DIVIDE', scalar(nt, 'SUBTRACT', radius, r), 0.065))
            envelope = lobe if envelope is None else scalar(nt, 'MAXIMUM', envelope, lobe, 'Overlapping_lobe_' + str(i))
        curl = clamp(nt, scalar(nt, 'DIVIDE', scalar(nt, 'SUBTRACT', fine.outputs['Fac'], 0.395), 0.28))
        density = scalar(nt, 'MULTIPLY', scalar(nt, 'MULTIPLY', envelope, scalar(nt, 'POWER', curl, 1.8)), 2.0, 'Thin_turbulent_ink_density')
        color = colors(nt, fine.outputs['Fac'], [(0.0, (0.018, 0.003, 0.04)), (0.38, (0.05, 0.006, 0.08)), (0.58, (0.17, 0.017, 0.22)), (0.80, (0.36, 0.07, 0.42)), (1.0, (0.45, 0.17, 0.56))], 'Sal_black_purple_ink_variation')
        link(nt, color, pv.inputs['Color'])
        pv.inputs['Emission Color'].default_value = (0.3, 0.025, 0.35, 1.0)
        link(nt, scalar(nt, 'MULTIPLY', density, 0.065), pv.inputs['Emission Strength'])
    link(nt, density, pv.inputs['Density'])
    link(nt, pv.outputs[0], out.inputs['Volume'])
    return mat


def scene_setup(effect):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = args.size
    scene.render.resolution_y = args.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.film_transparent = True
    scene.render.fps = 24
    scene.render.use_file_extension = True
    scene.render.use_persistent_data = True
    for attr, value in [('taa_render_samples', args.samples), ('volumetric_samples', 64), ('volumetric_tile_size', '2'), ('volumetric_shadow_samples', 16), ('use_volumetric_shadows', True)]:
        if hasattr(scene.eevee, attr):
            setattr(scene.eevee, attr, value)
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    world = bpy.data.worlds.new(effect + '_black_world')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.005, 0.008, 1.0)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.15
    scene.world = world
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-1.2, 0.0, 0.0) if effect == 'fire' else (0.0, 0.0, 0.0))
    cube = bpy.context.object
    cube.name = effect + '_bounded_procedural_volume'
    cube.scale = (1.45, 0.5, 0.65) if effect == 'fire' else (1.4, 1.2, 1.2)
    mat = material(effect)
    cube.data.materials.append(mat)
    camera_center = Vector((-0.9, 0.0, 0.0)) if effect == 'fire' else Vector((0.0, 0.0, 0.0))
    bpy.ops.object.camera_add(location=camera_center + Vector((0.0, -7.0, 0.0)))
    camera = bpy.context.object
    camera.name = effect + '_fixed_RGBA_orthographic_camera'
    camera.rotation_euler = (camera_center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 3.6 if effect == 'fire' else 3.4
    camera.data.lens = 50.0
    scene.camera = camera
    lights = [((0.0, -2.0, 2.0), (1.0, 0.6, 0.35), 100.0), ((-2.0, 1.0, -1.0), (1.0, 0.25, 0.08), 70.0)] if effect == 'fire' else [((1.2, -1.2, 1.8), (0.67, 0.25, 1.0), 420.0), ((-1.7, 0.0, -0.6), (0.16, 0.35, 0.75), 160.0)]
    for i, (position, color, energy) in enumerate(lights):
        bpy.ops.object.light_add(type='AREA', location=position)
        light = bpy.context.object
        light.name = effect + '_volume_rim_' + str(i)
        light.rotation_euler = (cube.location - light.location).to_track_quat('-Z', 'Y').to_euler()
        light.data.energy = energy
        light.data.color = color
        light.data.shape = 'DISK'
        light.data.size = 2.0
    scene.frame_start = 1
    scene.frame_end = 28
    for index in range(29):
        update_phase(mat, index)
        mat.node_tree.nodes['phase_W'].outputs[0].keyframe_insert(data_path='default_value', frame=index + 1)
        for key in ['X', 'Y', 'Z']:
            mat.node_tree.nodes['phase_shift'].inputs[key].keyframe_insert(data_path='default_value', frame=index + 1)
    scene.frame_set(1)
    scene['authoring_method'] = 'Procedural animated 3D volume. No fluid solver or baked simulation.'
    scene['seed'] = SEED
    scene['render_settings_verified'] = json.dumps({a: getattr(scene.eevee, a) for a in ['taa_render_samples', 'volumetric_samples', 'volumetric_tile_size', 'volumetric_shadow_samples', 'use_volumetric_shadows'] if hasattr(scene.eevee, a)})
    print('RENDER_SETTINGS ' + scene['render_settings_verified'], flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'blends' / (effect + '_jet' if effect == 'fire' else effect + '_mist')) + '.blend')
    return scene, mat


def export_meshes():
    output = ROOT / 'staged' / 'assets' / 'vfx' / 'blender_hybrid'
    for name in ['ember', 'drop']:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1 if name == 'ember' else 2, radius=1.0)
        obj = bpy.context.object
        obj.name = 'Blender_' + name
        for vertex in obj.data.vertices:
            z = vertex.co.z
            if name == 'ember':
                vertex.co.x *= 0.027
                vertex.co.y *= 0.027
                vertex.co.z *= 0.075
            else:
                taper = 1.0 - max(z, 0.0) * 0.52
                vertex.co.x *= 0.035 * taper
                vertex.co.y *= 0.035 * taper
                vertex.co.z *= 0.065
                if z > 0.0:
                    vertex.co.z += z * z * 0.025
        for poly in obj.data.polygons:
            poly.use_smooth = True
        mat = bpy.data.materials.new(name + '_runtime_tint_basis')
        mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)
        obj.data.materials.append(mat)
        bpy.ops.export_scene.gltf(filepath=str(output / (name + '.glb')), export_format='GLB', use_selection=True, export_yup=True, export_animations=False)
        coords = [v.co for v in obj.data.vertices]
        bounds_blender = [[min(v[k] for v in coords), max(v[k] for v in coords)] for k in range(3)]
        print('MESH_EXPORT ' + json.dumps({'name': name, 'path': str(output / (name + '.glb')), 'vertices': len(obj.data.vertices), 'triangles': len(obj.data.polygons), 'blender_axis_bounds': bounds_blender, 'gltf_axis_bounds': [bounds_blender[0], bounds_blender[2], [-bounds_blender[1][1], -bounds_blender[1][0]]], 'long_axis': 'glTF +Y; Blender +Z', 'bytes': (output / (name + '.glb')).stat().st_size}), flush=True)


effects = ['fire', 'sal'] if args.effect == 'all' else [args.effect]
started = time.perf_counter()
render_records = []
for effect in effects:
    scene, mat = scene_setup(effect)
    if args.mode == 'preview':
        indices = [6]
        folder = ROOT / 'previews'
    else:
        indices = range(28)
        folder = ROOT / 'frames' / effect
        folder.mkdir(parents=True, exist_ok=True)
    for index in indices:
        tick = time.perf_counter()
        update_phase(mat, index)
        scene.frame_set(index + 1)
        scene.render.filepath = str(folder / (effect + '_preview.png' if args.mode == 'preview' else 'f_%04d.png' % index))
        bpy.ops.render.render(write_still=True)
        record = {'effect': effect, 'index': index, 'seconds': round(time.perf_counter() - tick, 3), 'path': scene.render.filepath, 'bytes': Path(scene.render.filepath).stat().st_size}
        render_records.append(record)
        print('FRAME_RENDER ' + json.dumps(record), flush=True)
if args.mode == 'preview':
    export_meshes()
report = {'method': 'Blender Eevee procedural bounded 3D participating media with animated periodic 4D noise; no fluid solver/bake/cache', 'blender': bpy.app.version_string, 'hardware': 'NVIDIA GeForce RTX 4070, OpenGL 4.6 NVIDIA 595.79 (verified before production)', 'seed': SEED, 'size': args.size, 'samples_requested': args.samples, 'frames_raw': 28, 'loop_period_frames': 24, 'fps': 24, 'loop_overlap_frames': 4, 'render_records': render_records, 'elapsed_seconds': round(time.perf_counter() - started, 3)}
(ROOT / (args.mode + ('_' + args.effect if args.effect != 'all' else '') + '_render_report.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
print('PRODUCER_DONE ' + json.dumps({'mode': args.mode, 'seconds': report['elapsed_seconds'], 'frames': len(render_records)}), flush=True)




