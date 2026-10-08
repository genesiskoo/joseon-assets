param(
 [string]$Root='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial',
 [string]$Blender='E:/SteamLibrary/steamapps/common/Blender/blender.exe'
)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
$source=Join-Path $Root 'pre_fist/H1_doho.glb'
if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne 'AEEDB3148D40492614106F02DEA9E818B54BE01E6D2DC3271B316CE4676B25CE'){throw 'Expected preserved pre-fist source hash differs; do not double-curl a corrected model.'}
$fist=Join-Path $Root 'fist'
New-Item -ItemType Directory -Path (Join-Path $fist 'blender_delta') -Force | Out-Null
$cli=@('--background','--factory-startup','--python',('"'+(Join-Path $PSScriptRoot 'fist_delta.py')+'"'),'--',('"--src='+$source+'"'),('"--out='+$fist+'/blender_delta/H1_doho_diagnostic.glb"'),('"--delta='+$fist+'/position_delta.json"'),'--fist=both','--palm=down','--hem=10','--waist=11','--sash_y=-999','--chin=-999')
$p=Start-Process -FilePath $Blender -ArgumentList $cli -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $fist 'delta.stdout.log') -RedirectStandardError (Join-Path $fist 'delta.stderr.log')
if(-not $p.WaitForExit(30000)){throw "Only the separate fist process is still running: $($p.Id); inspect it before any retry."}
$p.Refresh()
if($p.ExitCode -ne 0 -or -not(Test-Path -LiteralPath (Join-Path $fist 'position_delta.json'))){throw 'Fist delta failed; inspect raw logs.'}
& node (Join-Path $PSScriptRoot 'apply_fist_delta.mjs') $source (Join-Path $fist 'position_delta.json') (Join-Path $fist 'H1_doho_preserved.glb')
if($LASTEXITCODE -ne 0){throw 'Fist transfer failed; final root candidate not replaced.'}
Copy-Item -LiteralPath (Join-Path $fist 'H1_doho_preserved.glb') -Destination (Join-Path $Root 'H1_doho.glb')
