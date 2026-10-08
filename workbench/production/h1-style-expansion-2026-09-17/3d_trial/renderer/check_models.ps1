param([string]$Root='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial')
$ErrorActionPreference='Stop'
$engine='C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
$out=@()
foreach($spec in @(@('doho',1.7),@('merchant',1.6))){
 $id=$spec[0]
 $model=Join-Path $Root "H1_${id}.glb"
 $stdout=Join-Path $Root "models/${id}_final_check.stdout.log"
 $stderr=Join-Path $Root "models/${id}_final_check.stderr.log"
 $cli=@('--headless','--path',('"'+$PSScriptRoot+'"'),'-s','res://tools/model_check.gd','--',('"'+$model+'"'),('--height='+$spec[1]))
 $proc=Start-Process -FilePath $engine -ArgumentList $cli -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
 if(-not $proc.WaitForExit(30000)){throw "Own model check still running: $($proc.Id)"}
 $proc.Refresh()
 $rawError=Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue
 $rawOutput=Get-Content -LiteralPath $stdout -Raw
 if($proc.ExitCode -ne 0 -or $rawError -match '(?m)^(SCRIPT ERROR|ERROR):' -or $rawOutput -notmatch 'RESULT (PASS|WARN)'){throw "Model check failed; inspect $stdout and $stderr"}
 $out+=[pscustomobject]@{id=$id;exit_code=$proc.ExitCode;result=([regex]::Match($rawOutput,'RESULT (PASS|WARN)').Value);stdout=$stdout;stderr=$stderr}
}
$out | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Root 'model_checks.json') -Encoding utf8
$out | ConvertTo-Json -Depth 5
