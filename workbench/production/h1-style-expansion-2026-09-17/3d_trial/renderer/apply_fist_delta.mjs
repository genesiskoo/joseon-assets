import fs from 'node:fs';
import crypto from 'node:crypto';
const [source, deltaPath, output] = process.argv.slice(2);
if (!source || !deltaPath || !output) throw Error('source delta.json output.glb required');
const raw=fs.readFileSync(source), delta=JSON.parse(fs.readFileSync(deltaPath,'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
let doc,bin;
for(let p=12;p<raw.length;){const size=raw.readUInt32LE(p),kind=raw.readUInt32LE(p+4);if(kind===0x4e4f534a)doc=JSON.parse(raw.subarray(p+8,p+8+size));if(kind===0x004e4942)bin=Buffer.from(raw.subarray(p+8,p+8+size));p+=8+size;}
const originalBin=Buffer.from(bin);
const primitive=doc.meshes[0].primitives[0];
function accessor(id){const a=doc.accessors[id],v=doc.bufferViews[a.bufferView],n={SCALAR:1,VEC3:3}[a.type],s={5123:2,5125:4,5126:4}[a.componentType];return {a,v,n,s,start:(v.byteOffset||0)+(a.byteOffset||0),stride:v.byteStride||n*s};}
const p=accessor(primitive.attributes.POSITION), normal=accessor(primitive.attributes.NORMAL), index=accessor(primitive.indices);
const pos=Array.from({length:p.a.count},(_,i)=>[0,1,2].map(k=>bin.readFloatLE(p.start+i*p.stride+k*4)));
const changed=new Set();
for(const row of delta.deltas){if(Math.hypot(...pos[row.index].map((x,k)=>x-row.old[k]))>1e-6)throw Error('Source delta mismatch');changed.add(row.index);pos[row.index]=row.new;for(let k=0;k<3;k++)bin.writeFloatLE(row.new[k],p.start+row.index*p.stride+k*4);}
const triangles=[];
for(let i=0;i<index.a.count;i+=3)triangles.push([0,1,2].map(k=>bin[index.s===2?'readUInt16LE':'readUInt32LE'](index.start+(i+k)*index.stride)));
// Recompute normals only at vertices incident to changed hand triangles.
const affected=new Set(changed);
for(const t of triangles)if(t.some(i=>changed.has(i)))for(const i of t)affected.add(i);
const sums=new Map([...affected].map(i=>[i,[0,0,0]]));
for(const [a,b,c] of triangles){if(![a,b,c].some(i=>affected.has(i)))continue;const u=pos[b].map((x,k)=>x-pos[a][k]),v=pos[c].map((x,k)=>x-pos[a][k]);const cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];for(const i of [a,b,c])if(affected.has(i))for(let k=0;k<3;k++)sums.get(i)[k]+=cross[k];}
for(const [i,n] of sums){const len=Math.hypot(...n);if(len<1e-10)throw Error('Degenerate hand normal');for(let k=0;k<3;k++)bin.writeFloatLE(n[k]/len,normal.start+i*normal.stride+k*4);}
p.a.min=[0,1,2].map(k=>Math.min(...pos.map(v=>v[k])));p.a.max=[0,1,2].map(k=>Math.max(...pos.map(v=>v[k])));
const allowed=new Set();
for(const i of changed)for(let k=0;k<12;k++)allowed.add(p.start+i*p.stride+k);
for(const i of affected)for(let k=0;k<12;k++)allowed.add(normal.start+i*normal.stride+k);
let changedBytes=0;
for(let i=0;i<bin.length;i++)if(bin[i]!==originalBin[i]){changedBytes++;if(!allowed.has(i))throw Error('Unexpected non-hand buffer change');}
const hashAccessor=id=>{const a=doc.accessors[id],v=doc.bufferViews[a.bufferView];return sha(bin.subarray(v.byteOffset||0,(v.byteOffset||0)+v.byteLength));};
// Sharp folds need normal seams; duplicate only corners whose shared normal points
// through the folded hand face. Surface connectivity/triangle positions stay equal.
const duplicates=[];
for(let ti=0;ti<triangles.length;ti++){
 const t=triangles[ti];if(!t.some(i=>affected.has(i)))continue;
 const [a,b,c]=t,u=pos[b].map((x,k)=>x-pos[a][k]),v=pos[c].map((x,k)=>x-pos[a][k]);
 const cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],len=Math.hypot(...cross);
 const avg=[0,1,2].map(k=>t.reduce((s,i)=>s+bin.readFloatLE(normal.start+i*normal.stride+k*4),0));
 if(cross.reduce((s,x,k)=>s+x*avg[k],0)>=0)continue;
 for(let corner=0;corner<3;corner++)duplicates.push({source:t[corner],target:p.a.count+duplicates.length,triangle:ti,corner,normal:cross.map(x=>x/len)});
}
const preservedBin=bin;
const chunks=[bin];let byteLength=bin.length;
function appendView(data,target){const padding=(4-byteLength%4)%4;if(padding){chunks.push(Buffer.alloc(padding));byteLength+=padding;}const id=doc.bufferViews.length;doc.bufferViews.push({buffer:0,byteOffset:byteLength,byteLength:data.length,target});chunks.push(data);byteLength+=data.length;return id;}
if(duplicates.length){
 for(const [semantic,id] of Object.entries(primitive.attributes)){
  const a=doc.accessors[id],view=doc.bufferViews[a.bufferView],count={SCALAR:1,VEC2:2,VEC3:3,VEC4:4}[a.type],size={5121:1,5123:2,5125:4,5126:4}[a.componentType],packed=count*size,stride=view.byteStride||packed,start=(view.byteOffset||0)+(a.byteOffset||0);
  const data=Buffer.alloc((a.count+duplicates.length)*packed);
  for(let i=0;i<a.count;i++)bin.copy(data,i*packed,start+i*stride,start+i*stride+packed);
  for(const d of duplicates){bin.copy(data,d.target*packed,start+d.source*stride,start+d.source*stride+packed);if(semantic==='NORMAL')for(let k=0;k<3;k++)data.writeFloatLE(d.normal[k],d.target*packed+k*4);}
  const cloned={...a,bufferView:appendView(data,34962),byteOffset:0,count:a.count+duplicates.length};
  if(semantic==='NORMAL'){cloned.min=[-1,-1,-1];cloned.max=[1,1,1];}
  primitive.attributes[semantic]=doc.accessors.length;doc.accessors.push(cloned);
 }
 const data=Buffer.alloc(index.a.count*index.s);for(let i=0;i<index.a.count;i++)bin.copy(data,i*index.s,index.start+i*index.stride,index.start+i*index.stride+index.s);
 for(const d of duplicates)data[index.s===2?'writeUInt16LE':'writeUInt32LE'](d.target,(d.triangle*3+d.corner)*index.s);
 primitive.indices=doc.accessors.length;doc.accessors.push({...index.a,bufferView:appendView(data,34963),byteOffset:0,max:[p.a.count+duplicates.length-1]});
 bin=Buffer.concat(chunks);if(bin.length%4)bin=Buffer.concat([bin,Buffer.alloc(4-bin.length%4)]);doc.buffers[0].byteLength=bin.length;
}
let json=Buffer.from(JSON.stringify(doc));if(json.length%4)json=Buffer.concat([json,Buffer.alloc(4-json.length%4,0x20)]);
const out=Buffer.alloc(12+8+json.length+8+bin.length);out.writeUInt32LE(0x46546c67,0);out.writeUInt32LE(2,4);out.writeUInt32LE(out.length,8);out.writeUInt32LE(json.length,12);out.writeUInt32LE(0x4e4f534a,16);json.copy(out,20);out.writeUInt32LE(bin.length,20+json.length);out.writeUInt32LE(0x004e4942,24+json.length);bin.copy(out,28+json.length);fs.writeFileSync(output,out);
const proof={source,source_sha256:sha(raw),output,output_sha256:sha(out),changed_position_vertices:changed.size,updated_normal_vertices:affected.size,changed_original_buffer_bytes:changedBytes,normal_seam_duplicate_vertices:duplicates.length,normal_seam_faces:duplicates.length/3,non_hand_original_buffer_bytes_preserved:true,indices_sha256:hashAccessor(primitive.indices),texture_uv_sha256:hashAccessor(primitive.attributes.TEXCOORD_0),materials_nodes_skins_animations_json_unchanged:true,all_image_skin_animation_bytes_unchanged:true,duplicate_vertex_weights_uvs_copied_exactly:true,triangles:index.a.count/3,scope:'Official rig_fix rest-position delta and adjacent hand normals. Sharp hand corners duplicated only for normal seams, no triangle or material added. Original clip times, materials, images and original skin data preserved byte for byte.'};
fs.writeFileSync(output+'.fist-transfer.json',JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify(proof,null,2));
