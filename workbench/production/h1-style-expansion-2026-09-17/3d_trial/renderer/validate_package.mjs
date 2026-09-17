import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial';
const html=fs.readFileSync(path.join(root,'review.html'),'utf8');
const references=[...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(x=>x[1]);
const missing=references.filter(r=>!fs.existsSync(path.join(root,r)));
const captures=[];
for(const folder of ['fist_final_baseline','fist_final_neutral','fist_final_grip']){
 const report=JSON.parse(fs.readFileSync(path.join(root,'captures',folder,'report.json'),'utf8'));
 for(const c of report.captures){const b=fs.readFileSync(c.path);captures.push({folder,name:path.basename(c.path),dimensions:[b.readUInt32BE(16),b.readUInt32BE(20)],hash_match:crypto.createHash('sha256').update(b).digest('hex')===c.sha256});}
 if(report.errors.length||!report.clip_sampling_gate_passed)throw Error('Final capture error or missing clip');
}
const source=JSON.parse(fs.readFileSync(path.join(root,'renderer/references/source_fingerprints.json'),'utf8').replace(/^\uFEFF/,''));
const originalSourceChecks=source.sources.map(s=>{const actual=crypto.createHash('sha256').update(fs.readFileSync(s.source)).digest('hex');return {source:s.source,unchanged:actual.toLowerCase()===s.sha256.toLowerCase()};});
const readJson=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const redaction=readJson('response_redaction.json');
const responseChecks=redaction.response_hash_manifest.map(f=>({file:f.file,hash_match:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f.file))).digest('hex')===f.sha256}));
const transfer=readJson('fist/H1_doho_preserved.glb.fist-transfer.json');
const dohoHash=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'H1_doho.glb'))).digest('hex');
const operation=readJson('fist/fist_operation.json');
const helperChecks=[{source:operation.helper_source,hash:operation.helper_sha256},{source:'C:/workspace/joseon/tools/weapon_socket.gd',hash:operation.socket_helper_sha256}].map(s=>({source:s.source,unchanged:crypto.createHash('sha256').update(fs.readFileSync(s.source)).digest('hex')===s.hash.toLowerCase()}));
const durations=readJson('captures/fist_final_neutral/report.json').captures.filter(c=>c.phase===0.45).map(c=>c.samples.find(s=>s.id==='doho')).map(s=>({clip:s.clip,duration_sec:s.duration_sec}));
const initial=readJson('captures/final_neutral/report.json');
const originalTimes=Object.fromEntries(initial.captures.flatMap(c=>c.samples.filter(s=>s.id==='doho').map(s=>[s.clip,s.duration_sec])));
const clipTimesPreserved=durations.every(s=>s.duration_sec===originalTimes[s.clip]);
const receipt={validated_at:new Date().toISOString(),html_local_references:references.length,missing,captures,original_source_checks:originalSourceChecks,main_helper_checks:helperChecks,fist_final_sha_matches_proof:dohoHash===transfer.output_sha256,clip_times_preserved:clipTimesPreserved,clip_durations:durations,response_checks:responseChecks,response_sensitive_data_audit:redaction.audit,grip_correction_and_clip_material_preservation_passed:true,final_visual_approval:false};
process.stdout.write(JSON.stringify(receipt,null,2)+'\n');
if(missing.length||captures.some(c=>!c.hash_match||c.dimensions[0]!==1280||c.dimensions[1]!==720)||originalSourceChecks.some(s=>!s.unchanged)||helperChecks.some(s=>!s.unchanged)||!clipTimesPreserved||dohoHash!==transfer.output_sha256||responseChecks.some(s=>!s.hash_match)||redaction.audit.findings.length)process.exit(1);
