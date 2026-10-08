import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial';
const backup=path.join(import.meta.dirname,'private_original_responses');
fs.mkdirSync(backup,{recursive:true});
fs.writeFileSync(path.join(backup,'.gitignore'),'*\n');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const marker='[REDACTED_TEMPORARY_DOWNLOAD_QUERY]';
let replaced=0;
function visit(value){
 if(Array.isArray(value))return value.map(visit);
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,visit(v)]));
 if(typeof value!=='string')return value;
 // Official MCP content.text embeds JSON as a string; sanitize that layer too.
 const trimmed=value.trim();
 if(trimmed.startsWith('{')||trimmed.startsWith('[')){try{return JSON.stringify(visit(JSON.parse(value)));}catch{}}
 return value.replace(/https?:\/\/[^\s"'<>\\]+/g,url=>{
  const q=url.indexOf('?');
  if(q<0||!/[?&](?:x-amz-[^=]+|signature|expires|policy|key-pair-id|x-goog-[^=]+)=/i.test(url))return url;
  replaced++;return url.slice(0,q)+'?'+marker;
 });
}
const files=fs.readdirSync(path.join(root,'responses')).filter(n=>n.endsWith('.json'));
const changes=[];
for(const name of files){
 const file=path.join(root,'responses',name),before=fs.readFileSync(file),data=JSON.parse(before.toString('utf8').replace(/^\uFEFF/,''));
 const start=replaced,clean=visit(data);
 if(replaced===start)continue;
 const saved=path.join(backup,name);
 if(!fs.existsSync(saved))fs.writeFileSync(saved,before);
 const after=Buffer.from(JSON.stringify(clean,null,2)+'\n');fs.writeFileSync(file,after);
 changes.push({file:'responses/'+name,temporary_query_occurrences:replaced-start,original_sha256:sha(before),redacted_sha256:sha(after)});
}
const findings=[];
const counts={signed_query_files:0,bearer_value_files:0,api_key_value_files:0,data_uri_files:0};
for(const folder of ['responses','requests'])for(const name of fs.readdirSync(path.join(root,folder)).filter(n=>n.endsWith('.json'))){
 const file=path.join(root,folder,name),s=fs.readFileSync(file,'utf8');
 const flags={signed_query:/[?&](?:x-amz-signature|x-amz-credential|x-goog-signature|signature)=/i.test(s),bearer_value:/Bearer\s+[A-Za-z0-9_.\-]{12,}/i.test(s),api_key_value:/["']?(?:api[_-]?key|MESHY_API_KEY)["']?\s*[:=]\s*["'][A-Za-z0-9_.\-]{12,}/i.test(s),data_uri:/data:[^;\s"']+;base64,[A-Za-z0-9+/=]{8,}/i.test(s)};
 if(Object.values(flags).some(Boolean))findings.push({file:folder+'/'+name,kinds:Object.keys(flags).filter(k=>flags[k])});
 for(const [k,v]of Object.entries(flags))if(v)counts[k+'_files']++;
}
const manifestFiles=files.map(name=>{const b=fs.readFileSync(path.join(root,'responses',name));return {file:'responses/'+name,sha256:sha(b),bytes:b.length};});
const priorPath=path.join(root,'response_redaction.json');
const prior=fs.existsSync(priorPath)?JSON.parse(fs.readFileSync(priorPath,'utf8').replace(/^\uFEFF/,'')):null;
const report={sanitized_at:new Date().toISOString(),scope:'Shareable production response copies only. Local raw execution responses retained in git-ignored tmp/h1_3d_trial/private_original_responses.',marker,response_file_count:files.length,changed_files:changes.length?changes:prior?.changed_files||[],audit:{...counts,findings},response_hash_manifest:manifestFiles,source_art_and_game_fingerprint_checks:'Separate checks; response redaction intentionally changes response hashes only.'};
fs.writeFileSync(priorPath,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({changed_file_count:changes.length,changed_filenames:changes.map(c=>c.file),response_file_count:files.length,audit:report.audit},null,2));
if(findings.length)process.exit(2);
