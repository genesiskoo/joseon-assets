"""Read the exported candidate GLBs; no third-party dependencies or asset mutation."""
from pathlib import Path
import hashlib, json, math, struct

BASE = Path(__file__).resolve().parent
COMP = {5120: ('b',1), 5121: ('B',1), 5122: ('h',2), 5123: ('H',2), 5125: ('I',4), 5126: ('f',4)}
COUNT = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4, 'MAT4':16}

def read_glb(path):
    raw = path.read_bytes()
    magic, version, total = struct.unpack_from('<III', raw)
    assert magic == 0x46546C67 and version == 2 and total == len(raw)
    offset = 12
    payload = None
    binary = b''
    while offset < total:
        length, kind = struct.unpack_from('<II', raw, offset)
        chunk = raw[offset+8:offset+8+length]
        if kind == 0x4E4F534A:
            payload = json.loads(chunk)
        elif kind == 0x004E4942:
            binary = chunk
        offset += 8 + length
    assert payload is not None
    return raw, payload, binary

def values(doc, binary, index):
    accessor = doc['accessors'][index]
    assert 'sparse' not in accessor
    view = doc['bufferViews'][accessor['bufferView']]
    assert view.get('buffer',0) == 0
    fmt, size = COMP[accessor['componentType']]
    n = COUNT[accessor['type']]
    stride = view.get('byteStride', size*n)
    start = view.get('byteOffset',0) + accessor.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*n, binary, start+i*stride) for i in range(accessor['count'])]

def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def audit(path):
    raw, doc, binary = read_glb(path)
    external = [x['uri'] for key in ('buffers','images') for x in doc.get(key,[]) if 'uri' in x and not x['uri'].startswith('data:')]
    triangles = bad = degenerate = missing = 0
    atlas_uv_checks=[]
    layout_path=BASE/'textures/atlas_layout.json'
    layout=json.loads(layout_path.read_text(encoding='utf-8')) if layout_path.exists() else None
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            assert primitive.get('mode',4) == 4
            positions = values(doc,binary,primitive['attributes']['POSITION'])
            normals = values(doc,binary,primitive['attributes']['NORMAL']) if 'NORMAL' in primitive['attributes'] else None
            ids = [v[0] for v in values(doc,binary,primitive['indices'])] if 'indices' in primitive else list(range(len(positions)))
            material=doc.get('materials',[])[primitive.get('material',0)]
            material_name=material.get('name','')
            if material_name.startswith('h1_atlas_') and layout:
                key=material_name.removeprefix('h1_atlas_')
                spec=layout['materials'][key]
                uvs=values(doc,binary,primitive['attributes']['TEXCOORD_0'])
                low=[min(v[k] for v in uvs) for k in range(2)]
                high=[max(v[k] for v in uvs) for k in range(2)]
                contained=all(low[k]>=spec['offset'][k]-1e-6 and high[k]<=spec['offset'][k]+spec['scale'][k]+1e-6 for k in range(2))
                atlas_uv_checks.append({'material':material_name,'uv_min':low,'uv_max':high,'contained_in_assigned_quadrant':contained})
            assert len(ids)%3 == 0
            triangles += len(ids)//3
            for i in range(0,len(ids),3):
                ia,ib,ic = ids[i:i+3]
                a,b,c = (positions[j] for j in (ia,ib,ic))
                face = cross(tuple(b[k]-a[k] for k in range(3)),tuple(c[k]-a[k] for k in range(3)))
                size = math.sqrt(sum(x*x for x in face))
                if size < 1e-12:
                    degenerate += 1
                elif normals:
                    normal = tuple(sum(normals[j][k] for j in (ia,ib,ic)) for k in range(3))
                    if sum(face[k]*normal[k] for k in range(3)) < -size*1e-5:
                        bad += 1
                else:
                    missing += 1
    expected = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(raw).hexdigest()
    return {'file':path.relative_to(BASE).as_posix(),'sha256':digest,'bytes':len(raw),
            'triangles':triangles,'triangle_report_matches':triangles==expected['triangles'],
            'hash_report_matches':digest==expected['sha256'],
            'gltf_ccw_normal_disagreements':bad,'degenerate_triangles':degenerate,
            'triangles_without_normals':missing,'external_dependencies':external,
            'embedded_images':len(doc.get('images',[])),
            'atlas_uv_checks':atlas_uv_checks,
            'double_sided_materials':[m.get('name','') for m in doc.get('materials',[]) if m.get('doubleSided',False)],
            'pass':not any((bad,degenerate,missing,external)) and triangles==expected['triangles'] and digest==expected['sha256'] and all(x['contained_in_assigned_quadrant'] for x in atlas_uv_checks)}

if __name__ == '__main__':
    result = [audit(p) for folder in ('models','props') for p in sorted((BASE/folder).glob('*.glb'))]
    document = {'method':'Independent glTF 2.0 binary readback; CCW face cross products vs supplied normals; report count and SHA256 comparison',
                'candidate_count':len(result),'all_pass':all(x['pass'] for x in result),'assets':result}
    (BASE/'glb_export_audit.json').write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'candidate_count':len(result),'all_pass':document['all_pass'],'issues':[x for x in result if not x['pass']]},indent=2))
