param([string]$Root='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial')
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
$expected=[IO.Path]::GetFullPath('C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial')
if($Root -ne $expected){throw 'Only the explicitly assigned trial output root is permitted.'}
function Read-Response([string]$Name){Get-Content -LiteralPath (Join-Path $Root "responses/$Name.json") -Raw | ConvertFrom-Json}
$specs=@(
 @('doho','initial_generation','doho_generate','doho_status_01'),
 @('merchant','initial_generation','merchant_generate','merchant_status_01'),
 @('doho','authorized_generation_retry','doho_generate_retry','doho_status_retry_02'),
 @('merchant','authorized_generation_retry','merchant_generate_retry','merchant_status_retry_01'),
 @('doho','rigging','doho_rig','doho_rig_status_01'),
 @('merchant','rigging','merchant_rig','merchant_rig_status_01'),
 @('merchant','text_only_retexture','merchant_retexture_text','merchant_retexture_status_01')
)
$tasks=@()
foreach($spec in $specs){
 $create=Read-Response $spec[2]
 $status=Read-Response $spec[3]
 $s=$status.result.structuredContent
 $tasks+=[pscustomobject][ordered]@{character=$spec[0];operation=$spec[1];task_id=$s.task_id;created_response_at=$create.captured_at;last_status_at=$status.captured_at;status=$s.status;progress=$s.progress;consumed_credits=$s.consumed_credits;error_message=$s.error_message;create_response="responses/$($spec[2]).json";status_response="responses/$($spec[3]).json"}
}
$before=(Read-Response 'balance_before').result.structuredContent.balance
$after=(Read-Response 'balance_final').result.structuredContent.balance
$total=($tasks | Measure-Object consumed_credits -Sum).Sum
if(($before-$after) -ne $total){throw 'Credit ledger does not reconcile.'}
$input=Get-Content -LiteralPath (Join-Path $Root 'input_manifest.json') -Raw | ConvertFrom-Json
$sourceChecks=@()
foreach($source in $input.sources){
 $originalHash=(Get-FileHash -LiteralPath $source.source -Algorithm SHA256).Hash
 $copyHash=(Get-FileHash -LiteralPath $source.copied_to -Algorithm SHA256).Hash
 $match=($originalHash -eq $source.sha256 -and $copyHash -eq $source.sha256)
 $sourceChecks+=[pscustomobject]@{name=$source.name;original=$source.source;copy=$source.copied_to;sha256=$source.sha256;original_and_copy_match=$match}
 if(-not $match){throw "Input provenance changed: $($source.name)"}
}
$ledger=[ordered]@{
 recorded_at=(Get-Date).ToString('o')
 status='technical_trial_complete_visual_acceptance_pending'
 main_game_intake=$false
 authorization=@(
  'PD approved sequential H1 expansion in docs/design/h1_style_expansion_2026-09-17.md; parent authorized one initial generation each, rigging and isolated trial.',
  'Both initial generations definitively failed service_unavailable with 0 credits. Parent explicitly authorized one same-input retry each; both succeeded.',
  'Parent authorized one merchant retexture to fix albedo artifacts while preserving geometry. New-image transfer was rejected by automatic approval review before execution.',
  'After checking approval evidence, a safer official request using only the existing Meshy task ID and nonsensitive text (no image/file/URL upload) was approved and executed once.'
 )
 generation_attempts_per_character=2
 successful_generations_per_character=1
 retexture_attempts=1
 rejected_image_retexture_executed=$false
 rejected_image_retexture_credits=0
 balance_before=$before
 balance_after=$after
 total_consumed_credits=$total
 tasks=$tasks
 input_hash_checks=$sourceChecks
 local_fist_postprocess=@{additional_credits=0;source='pre_fist/H1_doho.glb';final='H1_doho.glb';proof='fist/H1_doho_preserved.glb.fist-transfer.json';grip_report='fist/H1_doho_fist_fist.json';socket='fist/H1_doho_socket.json';changed_position_vertices=180;updated_normal_vertices=262;normal_seam_duplicate_vertices=12;clips_materials_skin_images_preserved=$true;grip_correction_and_socket_alignment_passed=$true;full_visual_approval=$false}
 visual_gate=@{approved=$false;passed=@('Local fist correction and measured H1 socket improve handle contact and blade direction','All three original clip times and original materials/images/skin data preserved');remaining=@('Coarse finger tips and exact thumb contact need final visual approval; right separate thumb selection was 0','Robe/sleeve deformation and overlap need production weighting review','Merchant face and shoe interpretation changed in text-only retexture','Merchant uses combat idle as a technical probe, not final NPC performance','PC emphasis at the real game camera needs PD selection among candidates')}
 response_redaction=@{report='response_redaction.json';private_raw_responses_excluded_from_package=$true;input_art_and_game_hash_checks_are_separate=$true}
 contract_gate=@{approved=$false;reference='docs/design/art_3d_pipeline.md 2.1/2.2 and data/models/merchant.tres';doho_triangle_limit=12000;doho_triangles=10827;merchant_triangle_limit=8000;merchant_triangles=10620;texture_limit=1024;actual_textures=2048;merchant_current_height=1.5;merchant_trial_height=1.6;trial_override_source='Parent explicitly requested ~11000 triangles / 1024-2048 texture and NPCheight1.6 for this isolated trial';permanent_exception_found=$false;doho_missing_full_contract_clips=@('hit','die');note='Later 11k ordering instructions and Doho 2K measurements are not a clear permanent NPC/texture budget exception. model_check uses a generic 12k warning and does not enforce texture cap.'}
}
$ledger | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $Root 'task_ledger.json') -Encoding utf8
Copy-Item -LiteralPath 'C:/workspace/joseon/data/models/merchant.tres' -Destination (Join-Path $PSScriptRoot 'references/current_merchant_contract_1_5m.tres')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'TRIAL_RESULTS.md') -Destination (Join-Path $Root 'README.md')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'review.html') -Destination (Join-Path $Root 'review.html')
$renderer=Join-Path $Root 'renderer'
New-Item -ItemType Directory -Path $renderer -Force | Out-Null
$top=@('project.godot','trial.gd','trial.tscn','capture_trial.ps1','retarget_trial.ps1','check_models.ps1','inspect_glb.mjs','apply_retexture.mjs','download_rigged.mjs','fist_delta.py','apply_fist_delta.mjs','fix_fist.ps1','redact_responses.mjs','publish_trial.ps1','validate_package.mjs','README.md','TRIAL_RESULTS.md','.gdignore')
foreach($name in $top){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $renderer $name)}
foreach($folder in @('actors','world','tools','references','assets')){
 foreach($file in Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot $folder) -File -Recurse){
  if($file.Extension -notin @('.gd','.py','.tscn','.tres','.glb','.png','.json')){continue}
  $relative=[IO.Path]::GetRelativePath($PSScriptRoot,$file.FullName)
  $destination=Join-Path $renderer $relative
  New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
  Copy-Item -LiteralPath $file.FullName -Destination $destination
 }
}
foreach($spec in @(@('assembly_reference_v2','winding_before'),@('assembly_reference_cullcheck','winding_two_sided'),@('assembly_reference_windingcheck','winding_after'))){
 $destination=Join-Path $Root "captures/$($spec[1])"
 New-Item -ItemType Directory -Path $destination -Force | Out-Null
 foreach($file in Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot "captures/$($spec[0])") -File){Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $destination $file.Name)}
}
$assets=@()
foreach($name in @('H1_doho.glb','H1_merchant.glb')){
 $file=Get-Item -LiteralPath (Join-Path $Root $name)
 $assets+=[pscustomobject]@{path=$name;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash;bytes=$file.Length;status='candidate; visual approval pending'}
}
$snapshots=@()
foreach($file in Get-ChildItem -LiteralPath $renderer -File -Recurse){$snapshots+=[pscustomobject]@{path=[IO.Path]::GetRelativePath($Root,$file.FullName);bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash}}
$checks=Get-Content -LiteralPath (Join-Path $Root 'model_checks.json') -Raw | ConvertFrom-Json
$redaction=Get-Content -LiteralPath (Join-Path $Root 'response_redaction.json') -Raw | ConvertFrom-Json
$artifact=[ordered]@{created_at=(Get-Date).ToString('o');assets=$assets;model_checks=$checks;renderer_files=$snapshots;response_files=$redaction.response_hash_manifest;response_redaction=@{path='response_redaction.json';sha256=(Get-FileHash -LiteralPath (Join-Path $Root 'response_redaction.json') -Algorithm SHA256).Hash};fist_transfer=@{path='fist/H1_doho_preserved.glb.fist-transfer.json';sha256=(Get-FileHash -LiteralPath (Join-Path $Root 'fist/H1_doho_preserved.glb.fist-transfer.json') -Algorithm SHA256).Hash};review='review.html';cost_ledger='task_ledger.json';visual_approval=$false;main_game_intake=$false}
$artifact | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $Root 'artifact_manifest.json') -Encoding utf8
[pscustomobject]@{output=$Root;files_in_renderer=$snapshots.Count;models=$assets;credits=$total;remaining_balance=$after;input_hashes_match=$true} | ConvertTo-Json -Depth 6
