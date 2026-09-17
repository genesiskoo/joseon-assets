import json,struct,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ground='--ground' in sys.argv
src=ROOT/('tailored_motion_loop.glb' if ground else 'tailored_motion_raw.glb')
b=bytearray(src.read_bytes());jn=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+jn]);bo=28+jn
def values(index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];d={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];off=bo+v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',d*4)
 return [list(struct.unpack_from('<'+'f'*d,b,off+i*stride)) for i in range(a['count'])],off,stride,d
def slerp(a,z,w):
 dot=sum(x*y for x,y in zip(a,z))
 if dot<0:z=[-x for x in z];dot=-dot
 if dot>.9995:q=[x*(1-w)+y*w for x,y in zip(a,z)]
 else:
  theta=math.acos(max(-1,min(1,dot)));q=[(x*math.sin((1-w)*theta)+y*math.sin(w*theta))/math.sin(theta) for x,y in zip(a,z)]
 norm=math.sqrt(sum(x*x for x in q));return [x/norm for x in q]
r=json.loads((ROOT/'loop_before_contact.json').read_text()) if ground else {}
for a in j['animations']:
 name=a.get('name')
 if name not in ['walk','run']:continue
 for c in a['channels']:
  path=c['target']['path'];s=a['samplers'][c['sampler']];times,*_=values(s['input']);out,off,stride,d=values(s['output']);duration=times[-1][0]
  if ground:
   if path!='translation' or not j['nodes'][c['target']['node']].get('name','').endswith('Hips'):continue
   vals=[row['min_z'] for row in r[name]['samples']]
   for i,t in enumerate(times):
    f=t[0]/duration*32;low=min(31,int(f));amount=vals[low]*(1-(f-low))+vals[low+1]*(f-low)
    # Running keeps the complete original vertical flight/bob waveform.
    # A single baseline offset grounds its lowest sample; no per-frame clamping.
    out[i][1]-=min(vals) if name=='run' else amount
  else:
   for i,t in enumerate(times):
    v=max(0,min(1,(t[0]/duration-.85)/.15));w=v*v*(3-2*v)
    out[i]=slerp(out[i],out[0],w) if path=='rotation' else [x*(1-w)+y*w for x,y in zip(out[i],out[0])]
  for i,q in enumerate(out):struct.pack_into('<'+'f'*d,b,off+i*stride,*q)
dest=ROOT/('doho_tailored_candidate.glb' if ground else 'tailored_motion_loop.glb');dest.write_bytes(b);print(dest)
