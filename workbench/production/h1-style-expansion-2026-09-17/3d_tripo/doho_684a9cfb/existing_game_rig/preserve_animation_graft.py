import json,struct,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=Path(r'C:\workspace\joseon\assets\models\doho\doho.glb')
def load(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);off=20+n;size=struct.unpack_from('<I',b,off)[0];return j,b[off+8:off+8+size]
old,ob=load(OLD);new,nb=load(ROOT/'existing_rig_new_visual_blender.glb');out=copy.deepcopy(old)
offset=(len(ob)+3)//4*4;blob=ob+b'\0'*(offset-len(ob))+nb
shifts={k:len(out.get(k,[])) for k in ['bufferViews','accessors','images','samplers','textures','materials','meshes','skins']}
for v in new.get('bufferViews',[]):
 v=copy.deepcopy(v);v['buffer']=0;v['byteOffset']=v.get('byteOffset',0)+offset;out.setdefault('bufferViews',[]).append(v)
for a in new.get('accessors',[]):
 a=copy.deepcopy(a)
 if 'bufferView'in a:a['bufferView']+=shifts['bufferViews']
 assert 'sparse' not in a
 out.setdefault('accessors',[]).append(a)
for k in ['images','samplers','textures','materials','meshes']:
 for item in new.get(k,[]):
  item=copy.deepcopy(item)
  if k=='images' and 'bufferView'in item:item['bufferView']+=shifts['bufferViews']
  if k=='textures':
   if 'source'in item:item['source']+=shifts['images']
   if 'sampler'in item:item['sampler']+=shifts['samplers']
  if k=='materials':
   def adjust(d):
    if isinstance(d,dict):
     for key,v in d.items():
      if key.endswith('Texture') and isinstance(v,dict) and 'index'in v:v['index']+=shifts['textures']
      else:adjust(v)
    elif isinstance(d,list):
     for v in d:adjust(v)
   adjust(item)
  if k=='meshes':
   for p in item['primitives']:
    p['attributes']={k:v+shifts['accessors'] for k,v in p['attributes'].items()}
    if 'indices'in p:p['indices']+=shifts['accessors']
    if 'material'in p:p['material']+=shifts['materials']
    assert 'targets'not in p
  out.setdefault(k,[]).append(item)
old_names={n.get('name'):i for i,n in enumerate(old['nodes'])}
mapping={i:old_names[n['name']] for i,n in enumerate(new['nodes']) if n.get('name')in old_names}
for skin in new['skins']:
 skin=copy.deepcopy(skin);skin['joints']=[mapping[i] for i in skin['joints']]
 if 'skeleton'in skin:skin['skeleton']=mapping[skin['skeleton']]
 skin['inverseBindMatrices']+=shifts['accessors'];out.setdefault('skins',[]).append(skin)
old_mesh_nodes=[i for i,n in enumerate(out['nodes']) if 'mesh'in n]
new_mesh_nodes=[n for n in new['nodes'] if 'mesh'in n]
assert len(old_mesh_nodes)==len(new_mesh_nodes)==1
node=out['nodes'][old_mesh_nodes[0]];node['mesh']=new_mesh_nodes[0]['mesh']+shifts['meshes'];node['skin']=new_mesh_nodes[0]['skin']+shifts['skins']
out['buffers']=[{'byteLength':len(blob)}]
assert out['animations']==old['animations']
for i,n in enumerate(old['nodes']):
 if i not in old_mesh_nodes:assert out['nodes'][i]==n
j=json.dumps(out,separators=(',',':')).encode();j+=b' '*(-len(j)%4);blob+=b'\0'*(-len(blob)%4)
data=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob
dest=ROOT/'doho_existing_rig_new_visual_exact_anims.glb';dest.write_bytes(data)
report={'output':str(dest),'method':'New mesh/material/skin appended to original GLB; original skeleton nodes and animation JSON/accessors/buffer bytes kept exactly. No animation re-export quantization.', 'original_animation_names':[a.get('name') for a in old['animations']],'animation_count':len(old['animations']),'animation_json_exact':out['animations']==old['animations'],'original_binary_prefix_exact':blob[:len(ob)]==ob,'bone_node_rest_exact':True,'animation_tolerance':'0: original float bytes and samplers unchanged','mesh_nodes_modified':old_mesh_nodes,'source_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(data).hexdigest()}
(ROOT/'exact_preservation_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
