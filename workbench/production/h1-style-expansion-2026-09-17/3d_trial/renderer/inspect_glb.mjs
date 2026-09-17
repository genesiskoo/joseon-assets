import fs from 'node:fs';
import crypto from 'node:crypto';
const files=process.argv.slice(2);
const out=[];
for(const file of files){
 const data=fs.readFileSync(file); let gltf,bin;
 for(let p=12;p<data.length;){const size=data.readUInt32LE(p),type=data.readUInt32LE(p+4),chunk=data.subarray(p+8,p+8+size);if(type===0x4e4f534a)gltf=JSON.parse(chunk.toString());if(type===0x004e4942)bin=chunk;p+=size+8;}
 const read=(id)=>{const a=gltf.accessors[id],v=gltf.bufferViews[a.bufferView],size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a.componentType],n={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16}[a.type];if(!size||!n)throw Error('Unknown accessor');const fn={5120:'readInt8',5121:'readUInt8',5122:'readInt16LE',5123:'readUInt16LE',5125:'readUInt32LE',5126:'readFloatLE'}[a.componentType];const ar=[];for(let i=0;i<a.count;i++){const row=[];for(let j=0;j<n;j++)row.push(bin[fn]((v.byteOffset||0)+(a.byteOffset||0)+i*(v.byteStride||n*size)+j*size));ar.push(row);}return ar;};
 const stats=[];
 for(const mesh of gltf.meshes||[])for(const primitive of mesh.primitives){
  const p=read(primitive.attributes.POSITION),n=primitive.attributes.NORMAL===undefined?null:read(primitive.attributes.NORMAL),ix=primitive.indices===undefined?p.map((_,i)=>[i]):read(primitive.indices);
  let aligned=0,opposed=0,degenerate=0,total=0,nonfinite=0,minDot=1,maxDot=-1;
  for(let i=0;i<ix.length;i+=3){const [a,b,c]=[p[ix[i][0]],p[ix[i+1][0]],p[ix[i+2][0]]];const u=b.map((x,k)=>x-a[k]),v=c.map((x,k)=>x-a[k]),cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],length=Math.hypot(...cross);total++;if(!Number.isFinite(length)){nonfinite++;continue;}if(length<1e-12){degenerate++;continue;}if(n){const normal=n[ix[i][0]].map((_,k)=>(n[ix[i][0]][k]+n[ix[i+1][0]][k]+n[ix[i+2][0]][k])/3),nl=Math.hypot(...normal),dot=cross.reduce((s,x,k)=>s+x*normal[k],0)/(length*nl);minDot=Math.min(minDot,dot);maxDot=Math.max(maxDot,dot);if(dot>=0)aligned++;else opposed++;}}
  stats.push({vertices:p.length,triangles:total,aligned,opposed,degenerate,nonfinite,min_dot:minDot,max_dot:maxDot});
 }
 out.push({file,sha256:crypto.createHash('sha256').update(data).digest('hex'),byte_length:data.length,materials:gltf.materials,meshes:stats,bones:(gltf.skins||[]).map(s=>s.joints.length),animations:(gltf.animations||[]).map(a=>a.name),gltf_winding_convention:'CCW triangle cross product compared to average vertex normal; not Godot CW'});
}
process.stdout.write(JSON.stringify(out,null,2)+'\n');
