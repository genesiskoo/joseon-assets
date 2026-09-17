"""Run the unchanged official rig_fix helper, then write only its rest-position delta.

The Blender export remains a diagnostic. The final GLB is patched from the original
buffer so clips, skin weights, nodes, materials and image bytes do not get re-exported.
"""
import json, math, os, runpy, struct, sys

argv = sys.argv[sys.argv.index('--') + 1:]
opts = dict(a.lstrip('-').split('=', 1) for a in argv if '=' in a)
source = opts['src']
raw = open(source, 'rb').read()
doc = None
binary = None
at = 12
while at < len(raw):
    size, kind = struct.unpack_from('<II', raw, at)
    chunk = raw[at + 8:at + 8 + size]
    if kind == 0x4E4F534A:
        doc = json.loads(chunk)
    elif kind == 0x004E4942:
        binary = chunk
    at += size + 8
primitive = doc['meshes'][0]['primitives'][0]
accessor = doc['accessors'][primitive['attributes']['POSITION']]
view = doc['bufferViews'][accessor['bufferView']]
start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
stride = view.get('byteStride', 12)
before = [struct.unpack_from('<fff', binary, start + i * stride) for i in range(accessor['count'])]

helper = os.path.join(os.path.dirname(__file__), 'tools', 'blender', 'rig_fix.py')
state = runpy.run_path(helper, run_name='__main__')
mesh = state['mesh']
world = state['mw']
old_world = state['wpos']
assert len(before) == len(old_world) == len(mesh.data.vertices), 'Vertex inventory changed'
def godot(v):
    return (float(v.x), float(v.z), -float(v.y))
max_import_error = max(math.dist(old, godot(w)) for old, w in zip(before, old_world))
assert max_import_error < 0.00001, f'Importer vertex order/space mismatch: {max_import_error}'
deltas = []
for index, vertex in enumerate(mesh.data.vertices):
    old = godot(old_world[index])
    new = godot(world @ vertex.co)
    if math.dist(old, new) > 0.000001:
        deltas.append({'index': index, 'old': before[index], 'new': new})
assert 50 <= len(deltas) < 600, f'Unexpected changed vertex count {len(deltas)}'
report = {
    'source': source,
    'helper': helper,
    'max_import_vertex_error_m': max_import_error,
    'vertex_count': len(before),
    'changed_vertex_count': len(deltas),
    'deltas': deltas,
    'scope': 'Only rest positions changed by the unchanged rig_fix --fist helper; no exported animation/material/weights reused',
}
path = opts['delta']
with open(path, 'w') as f:
    json.dump(report, f, indent=1)
print('== position delta', path, 'changed', len(deltas), 'max import error', max_import_error)
