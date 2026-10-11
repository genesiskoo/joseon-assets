'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const src = fs.readFileSync(__dirname+'/app.js','utf8');
const context = {esc:v=>String(v ?? ''),tr:v=>v,versions:g=>g.assets};
vm.createContext(context);
for (const [first,last] of [['function preferredConcept','function evidenceHTML'],['function captureSummary','function runtimeHTML'],['function evidenceHTML','function details']]) {
 vm.runInContext(src.slice(src.indexOf(first),src.indexOf(last)),context);
}
const old={asset_id:'old-f01',decision:{status:'approved',scope:['appearance'],date:'2026-09-17'},provenance:{}};
const anchor={asset_id:'new-anchor',decision:{status:'approved',scope:['face','identity'],date:'2026-09-25'},provenance:{}};
assert.equal(context.preferredConcept({assets:[old,anchor]}).asset_id,'new-anchor');
const candidate={asset_id:'candidate-h01',decision:{status:'recommended',scope:[],date:'2026-10-11'},provenance:{source_card:742}};
const snapshot=JSON.stringify(candidate);
assert.equal(context.preferredConcept({assets:[old,candidate]}).asset_id,'candidate-h01');
assert.equal(JSON.stringify(candidate),snapshot);
assert.match(context.evidenceHTML(candidate),/승인 없음/);
assert.match(context.evidenceHTML({decision:{status:'approved',scope:[]}}),/승인 범위 미확인/);
const summary=context.captureSummary({'종류':'중립 뷰어','화면크기':[1280,720],'카메라':'직교','동작':'idle','비교한계':'씬 틴트 없음','실행환경':'hidden detail'});
assert.match(summary,/중립 뷰어 · 1280 × 720 · 직교 · idle/);
assert.match(summary,/비교 한계: 씬 틴트 없음/);
assert.doesNotMatch(summary,/hidden detail|화면크기|\{/);
console.log('UI selection, approval wording and capture summary: PASS');
