(() => {
'use strict';
const root = document.getElementById('jh-character-catalogue');
if (!root) return;
const data = JSON.parse(root.querySelector('[data-catalogue-data]').textContent);
const groups = data.groups;
const label = {
 approved:'승인',recommended:'추천 · 미승인',unreviewed:'미판정',unknown:'판정 불명',rejected:'기각',superseded:'과거 승인 · 대체됨',
 connected:'연결됨',not_connected:'미연결',definition_only:'정의만 있음 · 사용 미확인',not_checked:'미검사',success:'성공',failed:'실패',confirmed:'확인',not_confirmed:'미확인',current:'현재 조건 일치',stale:'재확인 필요',indeterminate:'최신성 판정 불가',
 face:'얼굴',costume:'복식',tone:'톤',silhouette:'실루엣',eyes:'눈',appearance:'외형',hair:'머리',player:'플레이어',npc:'마을 NPC',boss:'보스',enemy:'일반 몬스터',related_character:'관련 인물',boss_npc:'보스 · NPC',concept:'원화',concept_board:'원화 보드',portrait:'초상',model_render:'모델 렌더',game_capture:'게임 화면',model:'3D 모델'
};
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const tr = value => label[value] || value || '미확인';
const $ = selector => root.querySelector(selector);
const saved = window.openai?.widgetState?.privateContent || {};
let state = {selected:saved.selected || groups[0]?.id,version:saved.version || '',tab:saved.tab || 'portrait',currentVersion:saved.currentVersion || '',search:saved.search || '',role:saved.role || '',status:saved.status || ''};
function save() {
 if (window.openai?.setWidgetState) window.openai.setWidgetState({modelContent:{character:state.selected,version:state.version,view:state.tab},privateContent:state}).catch(() => {});
}
const isConcept = a => ['concept','concept_board','reference','illustration','key_art'].includes(a.media_type);
const hasConnected = g => g.runtime.connection === 'connected';
function versions(g) { return g.assets.filter(isConcept); }
function preferredConcept(g) {
 const items=versions(g);
 const latest=aa=>aa.sort((a,b)=>String(b.decision?.date || '').localeCompare(String(a.decision?.date || '')) || (b.provenance?.source_card || 0)-(a.provenance?.source_card || 0))[0];
 // Display choice is independent of approval; keep every earlier version selectable.
 const anchors=items.filter(a=>a.decision?.status==='approved' && (a.asset_id.endsWith('-anchor') || (a.decision.scope || []).includes('identity') && (a.decision.scope || []).includes('face')));
 const directions=items.filter(a=>a.decision?.status==='recommended' || a.decision?.status==='approved' && (a.decision.scope || []).includes('tone'));
 return latest(anchors) || latest(directions) || latest(items.filter(a=>a.decision?.status==='approved')) || items[0];
}
function evidenceHTML(asset) {
 if (!asset) return '';
 const d = asset.decision || {};
 return `<p><span class="viz-badge">${esc(tr(d.status))}</span> ${esc((d.scope || []).map(tr).join(' · ') || (['recommended','unreviewed','rejected'].includes(d.status) ? '승인 없음' : '승인 범위 미확인'))}</p>`+
 `<p class="text-small">${esc(d.date || '판정 날짜 미확인')}${d.card ? ' · #'+esc(d.card) : ''}</p>`+
 (d.quote ? `<blockquote>${esc(d.quote)}</blockquote>` : '')+
 (asset.panel ? `<p class="notice">${esc(asset.panel.selection || '선택 패널')} 선택 범위만 판정. 전체 보드 승인 아님${asset.preview?.crop_rect ? ' · 선택 패널 파생 미리보기' : ''}</p>` : '')+
 (d.supersedes?.length ? `<p class="text-small">대체 대상: ${esc(d.supersedes.join(', '))}</p>` : '');
}
function details(asset) {
 if (!asset) return '';
 const p = asset.provenance || {}, f = asset.file || {};
 const rows = [ ['자료 ID',asset.asset_id],['원본 경로',`${f.repository || '?'}:${f.path || '출처 불명'}`],['원본 크기',f.width&&f.height ? `${f.width} × ${f.height} · ${f.bytes ?? '?'} bytes`:'미확인'],['SHA256',f.sha256 || '미확인'],['판정 근거',(asset.decision?.evidence || []).map(e=>typeof e==='string'?e:JSON.stringify(e)).join('\n') || '미확인'],['수록 이유',p.inclusion_reason || '미확인'],['프롬프트',p.prompt ? JSON.stringify(p.prompt,null,2) : '출처 미확인'],['참조 순서·역할',p.references?.length ? JSON.stringify(p.references,null,2) : '확인된 참조 없음'],['생성 출처',`${p.tool || '미확인'} / ${p.backend || '미확인'}`],['출처 카드·커밋',`${p.source_card || '미확인'} / ${p.source_commit || '미확인'}`],['캡처 조건',asset.capture ? JSON.stringify(asset.capture,null,2) : '해당 없음 / 미확인'],['연결·검증 근거',JSON.stringify(asset.runtime || {},null,2)],['미리보기 파생 정보',JSON.stringify(asset.preview || {},null,2)] ];
 return `<details><summary>근거·출처 상세</summary><dl class="metadata">${rows.map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details>`;
}
function imageHTML(asset, missing) {
 if (!asset?.preview?.src) return `<div class="image-stage"><p>${esc(asset?.preview?.missing_reason || missing)}</p></div>`;
 return `<figure><div class="image-stage"><img src="${esc(asset.preview.src)}" alt="${esc(asset.display_name)}"></div><figcaption>${esc(asset.display_name)}${asset.preview.crop_rect ? ' · 선택 패널' : ''}</figcaption></figure><div class="viz-row"><button class="btn" type="button" data-enlarge="${esc(asset.asset_id)}">확대</button>${asset.preview.original_url && !data.inline ? `<a class="btn" href="${esc(asset.preview.original_url)}" target="_blank" rel="noopener">원본 보기</a>` : ''}</div>${asset.preview.original_path ? `<details><summary>원본 파일 위치</summary><label class="form-label">복사할 로컬 경로<input class="form-control" data-original-path readonly value="${esc(asset.preview.original_path)}"></label><p class="text-small">${data.inline ? '원본은 로컬 파일입니다. 경로를 복사해 파일 탐색기에서 여세요.' : '브라우저가 로컬 링크를 차단하면 경로를 복사해 파일 탐색기에서 여세요.'}</p></details>` : ''}`;
}
function captureSummary(conditions) {
 if (!conditions) return '';
 if (typeof conditions==='string') return `<p class="text-small">촬영 조건: ${esc(conditions)}</p>`;
 const kind=conditions['종류'] || conditions.kind || conditions.type;
 const size=conditions['화면크기'] || conditions.resolution || conditions.viewport;
 const camera=conditions['카메라'] || conditions.camera;
 const action=conditions['동작'] || conditions.action || conditions.animation || conditions['시나리오'] || conditions.scenario;
 const parts=[kind,Array.isArray(size) ? size.join(' × ') : typeof size==='string' ? size : null,camera,action].filter(v=>typeof v==='string' && v);
 const limit=conditions['비교한계'] || conditions['비교 한계'] || conditions.limitations;
 return `<p class="text-small">${esc(parts.length ? parts.join(' · ') : '촬영 조건은 근거 상세에서 확인')}</p>`+(typeof limit==='string' ? `<p class="text-small">비교 한계: ${esc(limit)}</p>` : '');
}
function runtimeHTML(g, current) {
 const r = current?.runtime || g.runtime;
 return `<p>연결: ${esc(tr(r.connection))} · 로드: ${esc(tr(r.load))}</p><p>월드 표시: ${esc(tr(r.world_display))} · 최신성: ${esc(tr(r.freshness))}</p>`+
 (r.bindings?.length ? `<p class="text-small">현재 연결: ${esc([...new Set(r.bindings.map(b=>b.model_id || b.portrait_id || b.runtime_id || '미확인'))].join(' · '))}</p>` : '<p class="text-small">확인된 runtime 연결 자료 없음</p>')+
 (g.notes?.length ? `<p class="notice">${esc(g.notes.join(' · '))}</p>` : '');
}
function matching() {
 const q = state.search.trim().toLowerCase();
 return groups.filter(g => (!q || [g.name,g.form,g.character_id,...g.aliases].join(' ').toLowerCase().includes(q)) && (!state.role || g.role===state.role) && (!state.status || ({approved:g.assets.some(a=>isConcept(a) && a.decision?.status==='approved'),unapproved:g.assets.some(a=>isConcept(a) && ['recommended','unreviewed','unknown'].includes(a.decision?.status)),connected:hasConnected(g),stale:g.runtime.freshness==='stale'}[state.status])));
}
function render() {
 const shown = matching();
 if (!shown.some(g=>g.id===state.selected)) { state.selected=shown[0]?.id; state.version=''; }
 $('[data-count]').textContent = `${shown.length}개 형태 / 전체 ${groups.length}개 형태`;
 $('[data-list]').innerHTML = shown.map(g => {
 const cover = preferredConcept(g) || g.assets.find(a=>a.preview?.src);
 return `<button class="btn viz-tile" type="button" data-select="${esc(g.id)}" aria-pressed="${g.id===state.selected}"><span class="catalogue-entry">${cover?.preview?.src ? `<img src="${esc(cover.preview.src)}" alt="">` : ''}<span>${esc(g.name)} · ${esc(g.form)}</span><span class="text-small">${esc(tr(g.role))} · ${hasConnected(g)?'게임 연결':g.runtime.connection==='definition_only'?'정의만 있음 · 사용 미확인':tr(g.runtime.connection)}</span></span></button>`;
 }).join('');
 const g = groups.find(g=>g.id===state.selected);
 if (!g) { $('[data-detail]').innerHTML='<p>검색 조건에 맞는 자료가 없습니다.</p>'; return; }
 const vv=versions(g), concept=vv.find(a=>a.asset_id===state.version) || preferredConcept(g);
 state.version=concept?.asset_id || '';
 const types = {portrait:['portrait','portrait_sheet','portrait_atlas','portrait_still'],model_render:['model_render','render'],game_capture:['game_capture','game_screenshot','capture']};
 const media = g.assets.filter(a=>types[state.tab].includes(a.media_type));
 const current = media.find(a=>a.asset_id===state.currentVersion) || media.find(a=>a.media_type==='portrait_atlas' && a.runtime?.connection==='connected') || media.find(a=>a.runtime?.connection==='connected') || media[0];
 state.currentVersion=current?.asset_id || '';
 const mediaSelector=media.length>1 ? `<label class="form-label">현재 자료<select class="form-select" data-current-version>${media.map(a=>`<option value="${esc(a.asset_id)}" ${a===current?'selected':''}>${esc(a.display_name)}</option>`).join('')}</select></label>` : '';
 const condition=current?.capture?.conditions;
 $('[data-detail]').innerHTML=`<h3>${esc(g.name)} · ${esc(g.form)}</h3><div class="comparison"><section><h3>원화 · 판정 이력</h3>${vv.length ? `<label class="form-label">원화 버전<select class="form-select" data-version>${vv.map(a=>`<option value="${esc(a.asset_id)}" ${a===concept?'selected':''}>${esc(a.display_name)} · ${esc(tr(a.decision?.status))}</option>`).join('')}</select></label>`:''}${evidenceHTML(concept)}${imageHTML(concept,'원화 자료 미확인')}${(concept?.notes || []).map(n=>`<p class="notice">${esc(n)}</p>`).join('')}${details(concept)}</section><section><h3>현재 게임 모습</h3><div class="viz-row" role="group" aria-label="현재 매체">${Object.keys(types).map(t=>`<button class="btn" type="button" data-tab="${t}" aria-pressed="${state.tab===t}">${esc(tr(t))}</button>`).join('')}</div>${runtimeHTML(g,current)}${mediaSelector}${imageHTML(current,{portrait:'현재 초상 이미지 미확인',model_render:'현재 모델 렌더 미확인 · 3D 파일만으로 화면을 추정하지 않음',game_capture:'현재 게임 캡처 미확인 · 월드 표시 확인 필요'}[state.tab])}${captureSummary(condition)}${details(current)}<details><summary>현재 연결 근거</summary><pre class="metadata">${esc(JSON.stringify(g.runtime,null,2))}</pre></details></section></div>`;
}
for (const role of [...new Set(groups.map(g=>g.role))]) $('[data-role]').insertAdjacentHTML('beforeend',`<option value="${esc(role)}">${esc(tr(role))}</option>`);
$('[data-search]').value=state.search; $('[data-role]').value=state.role; $('[data-status]').value=state.status;
root.addEventListener('input',e=>{if(e.target.matches('[data-search]')){state.search=e.target.value;render();save();}});
root.addEventListener('change',e=>{if(e.target.matches('[data-current-version]')){state.currentVersion=e.target.value;render();save();}for(const key of ['role','status','version'])if(e.target.matches(`[data-${key}]`)){state[key]=e.target.value;render();save();}});
root.addEventListener('click',e=>{
 if(e.target.matches('[data-original-path]'))e.target.select();
 const b=e.target.closest('button'); if(!b)return;
 if(b.hasAttribute('data-select')) {state.selected=b.dataset.select;state.version='';state.currentVersion='';render();save();}
 if(b.hasAttribute('data-tab')){state.tab=b.dataset.tab;state.currentVersion='';render();save();}
 if(b.hasAttribute('data-enlarge')){
 const a=groups.flatMap(g=>g.assets).find(a=>a.asset_id===b.dataset.enlarge);
 if(a?.preview?.src){$('[data-zoom-image]').src=a.preview.src;$('[data-zoom-image]').alt=a.display_name;$('[data-zoom-caption]').textContent=a.display_name;$('[data-zoom]').showModal();}
 }
 if(b.hasAttribute('data-close'))$('[data-zoom]').close();
});
window.addEventListener('openai:set_globals',event=>{const incoming=event.detail?.globals?.widgetState?.privateContent;if(incoming){state={...state,...incoming};$('[data-search]').value=state.search;$('[data-role]').value=state.role;$('[data-status]').value=state.status;render();}});
if(data.issues?.length){$('[data-issues]').hidden=false;$('[data-issues-content]').textContent=JSON.stringify(data.issues,null,2);}
render();
})();










