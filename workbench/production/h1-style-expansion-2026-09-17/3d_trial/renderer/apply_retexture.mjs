import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
const [originalRaw,retextured,animatedBase,output]=process.argv.slice(2);
if(!output)throw Error('Usage: apply_retexture <original raw.glb> <retexture.glb> <animated.glb> <new output.glb>');
const sha=(bytes)=>crypto.createHash('sha256').update(bytes).digest('hex');
function read(file){const bytes=fs.readFileSync(file);let json,bin;for(let p=12;p<bytes.length;){let len=bytes.readUInt32LE(p),type=bytes.readUInt32LE(p+4),data=bytes.subarray(p+8,p+8+len);if(type===0x4e4f534a)json=JSON.parse(data.toString());if(type===0x004e4942)bin=data;p+=len+8;}return {file,bytes,json,bin};}
function accessor(model,index){const a=model.json.accessors[index],v=model.json.bufferViews[a.bufferView],size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a.componentType],width={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16}[a.type]*size;if(!width)throw Error('Unknown accessor type');const parts=[];for(let i=0;i<a.count;i++){const off=(v.byteOffset||0)+(a.byteOffset||0)+(v.byteStride||width)*i;parts.push(model.bin.subarray(off,off+width));}return sha(Buffer.concat(parts));}
function signature(model){return model.json.meshes.flatMap(m=>m.primitives.map(p=>({mode:p.mode??4,indices:accessor(model,p.indices),attributes:Object.fromEntries(Object.keys(p.attributes).sort().map(k=>[k,accessor(model,p.attributes[k])]))})));}
const source=read(originalRaw),replacement=read(retextured),base=read(animatedBase);
const originalSignature=signature(source),replacementSignature=signature(replacement);
const textureGeometry=(signatures)=>signatures.map(s=>({...s,attributes:Object.fromEntries(Object.entries(s.attributes).filter(([k])=>k!=='NORMAL'))}));
if(JSON.stringify(textureGeometry(originalSignature))!==JSON.stringify(textureGeometry(replacementSignature))){
 process.stdout.write(JSON.stringify({originalSignature,replacementSignature},null,2)+'\n');
 throw Error('Retexture changed geometry/UV accessor data; refusing texture transfer');
}
const srcMaterial=replacement.json.materials[0],srcTexture=replacement.json.textures[srcMaterial.pbrMetallicRoughness.baseColorTexture.index],srcImage=replacement.json.images[srcTexture.source],srcView=replacement.json.bufferViews[srcImage.bufferView];
const image=replacement.bin.subarray(srcView.byteOffset||0,(srcView.byteOffset||0)+srcView.byteLength);
const baseTexture=base.json.textures[base.json.materials[0].pbrMetallicRoughness.baseColorTexture.index];
const oldImage=base.json.images[baseTexture.source];
const oldView=base.json.bufferViews[oldImage.bufferView];
const oldImageHash=sha(base.bin.subarray(oldView.byteOffset||0,(oldView.byteOffset||0)+oldView.byteLength));
const padding=(4-image.length%4)%4;
const newBin=Buffer.concat([base.bin,image,Buffer.alloc(padding)]);
const viewIndex=base.json.bufferViews.length;
base.json.bufferViews.push({buffer:0,byteOffset:base.bin.length,byteLength:image.length});
for(let i=0;i<base.json.images.length;i++){
 const im=base.json.images[i],view=base.json.bufferViews[im.bufferView],hash=sha(base.bin.subarray(view.byteOffset||0,(view.byteOffset||0)+view.byteLength));
 if(i===baseTexture.source||hash===oldImageHash)base.json.images[i]={...im,bufferView:viewIndex,mimeType:srcImage.mimeType,name:'merchant_retexture_01_base_color'};
}
base.json.buffers[0].byteLength=newBin.length;
let jsonBytes=Buffer.from(JSON.stringify(base.json));jsonBytes=Buffer.concat([jsonBytes,Buffer.alloc((4-jsonBytes.length%4)%4,0x20)]);
const header=Buffer.alloc(12);header.write('glTF');header.writeUInt32LE(2,4);header.writeUInt32LE(12+8+jsonBytes.length+8+newBin.length,8);
const jh=Buffer.alloc(8);jh.writeUInt32LE(jsonBytes.length);jh.writeUInt32LE(0x4e4f534a,4);
const bh=Buffer.alloc(8);bh.writeUInt32LE(newBin.length);bh.writeUInt32LE(0x004e4942,4);
const bytes=Buffer.concat([header,jh,jsonBytes,bh,newBin]);
fs.writeFileSync(output,bytes,{flag:'wx'});
const after=read(output);
if(!after.bin.subarray(0,base.bin.length).equals(base.bin))throw Error('Original animation/geometry buffer prefix not preserved');
const receipt={created_at:new Date().toISOString(),output:path.resolve(output),sha256:sha(bytes),animated_source:path.resolve(animatedBase),animated_source_sha256:sha(base.bytes),retexture_source:path.resolve(retextured),retexture_source_sha256:sha(replacement.bytes),original_raw_sha256:sha(source.bytes),positions_indices_uv_unchanged_between_raw_and_retexture:true,geometry_uv_signature:originalSignature,retexture_normal_bytes_changed:JSON.stringify(originalSignature)!==JSON.stringify(replacementSignature),retexture_normals_used:false,animated_geometry_skin_and_clip_buffer_preserved_exactly:true,original_binary_prefix_sha256:sha(base.bin),new_texture_sha256:sha(image),material_parameters_preserved:true,note:'Only embedded base color/emission image references changed; original geometry, normals, skin, animation and UV buffer bytes remain exact. Retexture normal bytes differ but are not applied. Original image bytes remain unused in the file for auditability. Visual character approval remains pending.'};
fs.writeFileSync(output+'.texture-transfer.json',JSON.stringify(receipt,null,2)+'\n');
process.stdout.write(JSON.stringify(receipt)+'\n');
