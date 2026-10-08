param(
    [ValidateSet('assembly_reference','h1_trial')][string]$Mode = 'assembly_reference',
    [string]$Doho = '',
    [string]$Merchant = '',
    [string]$Output = '',
    [switch]$SwordProxy,
    [string]$Socket = '',
    [switch]$GripCloseup,
    [switch]$TilesTwoSided,
    [switch]$TilesFlipWinding,
    [switch]$PCMatte,
    [switch]$PCFill,
    [ValidateSet('','neutral','unshaded','solid','nearest')][string]$Diagnostic = '',
    [string]$Godot = 'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
)
$ErrorActionPreference = 'Stop'
if (-not $Output) { $Output = Join-Path $PSScriptRoot ('captures/' + $Mode) }
$Output = [IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Path $Output -Force | Out-Null
if ($Mode -eq 'h1_trial') {
    foreach ($model in @($Doho,$Merchant)) { if (-not $model -or -not (Test-Path -LiteralPath $model -PathType Leaf)) { throw 'h1_trial requires both actual model paths.' } }
}
$args = @('--path', ('"' + $PSScriptRoot + '"'), '--windowed', '--', ('--mode=' + $Mode), ('"--shots=' + $Output + '"'))
if ($Doho) { $args += ('"--doho=' + [IO.Path]::GetFullPath($Doho) + '"') }
if ($Merchant) { $args += ('"--merchant=' + [IO.Path]::GetFullPath($Merchant) + '"') }
if ($SwordProxy) { $args += '--sword-proxy' }
if ($Socket) { $args += ('"--socket=' + [IO.Path]::GetFullPath($Socket) + '"') }
if ($GripCloseup) { $args += '--grip-closeup' }
if ($TilesTwoSided) { $args += '--tiles-two-sided' }
if ($TilesFlipWinding) { $args += '--tiles-flip-winding' }
if ($PCMatte) { $args += '--pc-matte' }
if ($PCFill) { $args += '--pc-fill' }
if ($Diagnostic) { $args += ('--diagnostic=' + $Diagnostic) }
$proc = Start-Process -FilePath $Godot -ArgumentList $args -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Output 'stdout.log') -RedirectStandardError (Join-Path $Output 'stderr.log')
$done = $proc.WaitForExit(30000)
if ($done) {
    $proc.Refresh()
    $rawStderr = Get-Content -LiteralPath (Join-Path $Output 'stderr.log') -Raw -ErrorAction SilentlyContinue
    $engineErrors = [bool]($rawStderr -match '(?m)^(SCRIPT ERROR|ERROR):')
    $reportExists = Test-Path -LiteralPath (Join-Path $Output 'report.json') -PathType Leaf
    [pscustomobject]@{ pid=$proc.Id; finished=$true; exit_code=$proc.ExitCode; engine_errors=$engineErrors; report_exists=$reportExists; output=$Output } | ConvertTo-Json
    if ($proc.ExitCode -ne 0 -or $engineErrors -or -not $reportExists) { throw 'Independent capture failed. Inspect the saved raw stdout/stderr logs.' }
} else {
    [pscustomobject]@{ pid=$proc.Id; finished=$false; output=$Output; note='Only this independent trial process is running. Poll this PID; do not stop the main editor.' } | ConvertTo-Json
}
