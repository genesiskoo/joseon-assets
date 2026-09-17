param([Parameter(Mandatory=$true)][string]$Model,[Parameter(Mandatory=$true)][string]$Id,[Parameter(Mandatory=$true)][double]$Height,[Parameter(Mandatory=$true)][string]$Output,[ValidateSet('neutral','actual')][string]$Mode='neutral',[switch]$Reference)
$ErrorActionPreference='Stop'
if(-not(Test-Path -LiteralPath $Model -PathType Leaf)){throw 'Missing model; no placeholder is rendered.'}
$engine='C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
New-Item -ItemType Directory -Path $Output -Force|Out-Null
$launchArgs=@('--path',('"'+$PSScriptRoot+'"'),'--windowed','--',('"--model='+[IO.Path]::GetFullPath($Model)+'"'),('--id='+$Id),('--height='+$Height.ToString([Globalization.CultureInfo]::InvariantCulture)),('--mode='+$Mode),('"--output='+[IO.Path]::GetFullPath($Output)+'"'))
if($Reference){$launchArgs+='--reference'}
$stdout=Join-Path $Output ($Mode+'_stdout.log')
$stderr=Join-Path $Output ($Mode+'_stderr.log')
$proc=Start-Process -FilePath $engine -ArgumentList $launchArgs -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
if($proc.WaitForExit(30000)){
 $raw=Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue
 $engineErrors=[bool]($raw -match '(?m)^(SCRIPT ERROR|ERROR):')
 $okay=(Test-Path -LiteralPath (Join-Path $Output ($Mode+'_contract.json'))) -and -not $engineErrors
 [pscustomobject]@{pid=$proc.Id;finished=$true;report_exists=$okay;output=$Output}|ConvertTo-Json
 if(-not $okay){if($raw){Write-Output $raw};throw 'Independent renderer failed; raw stderr is preserved.'}
}else{[pscustomobject]@{pid=$proc.Id;finished=$false;output=$Output}|ConvertTo-Json}
