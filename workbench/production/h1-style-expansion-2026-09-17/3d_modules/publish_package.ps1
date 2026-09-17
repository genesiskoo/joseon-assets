param([string]$Destination='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_modules')
$ErrorActionPreference='Stop'
$sourceRoot=[IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\','/')
$targetRoot=[IO.Path]::GetFullPath($Destination).TrimEnd('\','/')
$authorizedRoot=[IO.Path]::GetFullPath('C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_modules').TrimEnd('\','/')
if ($targetRoot -ne $authorizedRoot) { throw 'Destination outside the assigned production folder.' }
$rootNames=@('build_modules.gd','build_props.gd','review.gd','review.tscn','project.godot','run_review.ps1','prepare_stairs.py','measure_h1_hand.py','audit_glb.py','finalize_package.py','publish_package.ps1','README.md','REPRODUCE.md','index.html','module_report.json','props_report.json','render_report.json','h1_hand_measured_fist.json','h1_socket_correction.json','glb_export_audit.json','source_preservation.json','qa_report.json','manifest.json','canonical_glbs.json','build_initial_raw.log','socket_probe_engine.log')
$files=[Collections.Generic.List[IO.FileInfo]]::new()
foreach ($name in $rootNames) { $files.Add((Get-Item -LiteralPath (Join-Path $sourceRoot $name))) }
foreach ($name in @('*_stdout.log','*_stderr.log')) {
    foreach ($item in Get-ChildItem -LiteralPath $sourceRoot -Filter $name -File) { $files.Add($item) }
}
$folderRules=@{'models'=@('.glb','.json');'props'=@('.glb','.json');'captures'=@('.png');'world'=@('.gd','.gdshader');'tools'=@('.gd');'actors'=@('.gd');'references'=@('.tres','.tscn');'textures'=@('.png','.json')}
foreach ($folder in $folderRules.Keys) {
    foreach ($item in Get-ChildItem -LiteralPath (Join-Path $sourceRoot $folder) -File) {
        if ($item.Extension -in $folderRules[$folder]) { $files.Add($item) }
    }
}
foreach ($name in @('H1_doho_preserved.glb','H1_doho_fist_fist.json')) { $files.Add((Get-Item -LiteralPath (Join-Path $sourceRoot ('reference_actor/'+$name)))) }
New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
$checks=@()
foreach ($item in ($files | Sort-Object FullName -Unique)) {
    $relative=[IO.Path]::GetRelativePath($sourceRoot,$item.FullName)
    if ($relative.StartsWith('..')) { throw ('Source escaped owned folder: '+$relative) }
    $target=[IO.Path]::GetFullPath((Join-Path $targetRoot $relative))
    if (-not $target.StartsWith($targetRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw ('Target escaped authorized folder: '+$target) }
    $sourceHash=(Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $action='added'
    if (Test-Path -LiteralPath $target) {
        $oldHash=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
        $action=if ($oldHash -eq $sourceHash) { 'unchanged' } else { 'updated' }
    }
    if ($action -ne 'unchanged') {
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
        Copy-Item -LiteralPath $item.FullName -Destination $target
    }
    $copiedHash=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($copiedHash -ne $sourceHash) { throw ('Copy hash mismatch: '+$relative) }
    $checks+=[pscustomobject]@{file=$relative.Replace('\','/');bytes=$item.Length;sha256=$copiedHash;copy_action=$action;source_destination_match=$true}
}
$manifest=Get-Content -LiteralPath (Join-Path $targetRoot 'manifest.json') -Raw | ConvertFrom-Json
$canonical=@($manifest.assets)
if ($canonical.Count -ne 18) { throw 'Canonical count is not 18.' }
$canonicalPass=$true
foreach ($asset in $canonical) {
    $digest=(Get-FileHash -LiteralPath (Join-Path $targetRoot $asset.file) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $asset.sha256) { $canonicalPass=$false }
}
$capturePass=$true
foreach ($capture in $manifest.captures) {
    $digest=(Get-FileHash -LiteralPath (Join-Path $targetRoot $capture.file) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $capture.sha256) { $capturePass=$false }
}
$canonicalFiles=@(Get-ChildItem -LiteralPath (Join-Path $targetRoot 'models'),(Join-Path $targetRoot 'props') -File -Filter '*.glb')
$utf8=New-Object Text.UTF8Encoding($false)
$hashPath=Join-Path $targetRoot 'package_hashes.json'
$hashManifest=[pscustomobject]@{generated_utc=[DateTime]::UtcNow.ToString('o');scope='All published payload files; excludes package_hashes.json and package_validation.json to avoid self-reference';files=$checks}
[IO.File]::WriteAllText($hashPath,($hashManifest | ConvertTo-Json -Depth 8),$utf8)
$validation=[pscustomobject]@{
    generated_utc=[DateTime]::UtcNow.ToString('o');status='PASS';destination=$targetRoot;
    payload_files=$checks.Count;payload_bytes=($checks | Measure-Object bytes -Sum).Sum;
    files_added=@($checks | Where-Object copy_action -eq 'added').Count;
    files_updated=@($checks | Where-Object copy_action -eq 'updated').Count;
    files_unchanged=@($checks | Where-Object copy_action -eq 'unchanged').Count;
    all_source_destination_sha256_match=$true;canonical_candidate_glbs=$canonicalFiles.Count;
    canonical_manifest_hashes_match=$canonicalPass;capture_count=@($manifest.captures).Count;
    capture_manifest_hashes_match=$capturePass;reference_actor_glbs=1;
    reference_actor_is_canonical_candidate=$false;production_game_intake=$false;
    package_hashes_sha256=(Get-FileHash -LiteralPath $hashPath -Algorithm SHA256).Hash.ToLowerInvariant()
}
if (-not $canonicalPass -or -not $capturePass -or $canonicalFiles.Count -ne 18) { $validation.status='FAIL' }
[IO.File]::WriteAllText((Join-Path $targetRoot 'package_validation.json'),($validation | ConvertTo-Json -Depth 5),$utf8)
$validation | ConvertTo-Json -Depth 5
if ($validation.status -ne 'PASS') { exit 2 }
