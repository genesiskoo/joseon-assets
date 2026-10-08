param([string]$Root='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial')
$ErrorActionPreference='Stop'
$engine='C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
$source=Join-Path $PSScriptRoot 'references/CURRENT_REFERENCE_NOT_H1.glb'
$records=@()
foreach($id in @('doho','merchant')){
    $base=Join-Path $Root "rigged/H1_${id}_rigged.glb"
    $output=Join-Path $Root "models/H1_${id}.glb"
    $cli=@('--headless','--path',('"'+$PSScriptRoot+'"'),'-s','res://tools/retarget_mixamo.gd','--',('"--base='+$base+'"'),('"--out='+$output+'"'),'--fps=30','--inplace=idle,walk',('"idle='+$source+'#idle"'),('"walk='+$source+'#walk"'),('"attack='+$source+'#attack"'))
    $stdout=Join-Path $Root "models/${id}_retarget.stdout.log"
    $stderr=Join-Path $Root "models/${id}_retarget.stderr.log"
    $proc=Start-Process -FilePath $engine -ArgumentList $cli -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if(-not $proc.WaitForExit(30000)){throw "Own retarget process still running: $($proc.Id); do not relaunch."}
    $proc.Refresh()
    $rawError=Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue
    if($proc.ExitCode -ne 0 -or $rawError -match '(?m)^(SCRIPT ERROR|ERROR):' -or -not(Test-Path -LiteralPath $output)){throw "Retarget failed; inspect $stdout and $stderr"}
    $records+=[ordered]@{id=$id;source=$source;source_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash;source_clips=@('idle','walk','attack');base=$base;base_sha256=(Get-FileHash -LiteralPath $base -Algorithm SHA256).Hash;output=$output;output_sha256=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash;fps=30;additional_upright_degrees=0;additional_yaw_degrees=0;explanation='Retarget named current-game clips from frozen source; existing posture/yaw corrections are already baked. Merchant clips are technical motion probes, not an approved NPC performance.'}
}
$records | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Root 'retarget_manifest.json') -Encoding utf8
$records | ForEach-Object { [pscustomobject]$_ } | Select-Object id,output,output_sha256 | ConvertTo-Json
