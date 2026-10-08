param(
    [Parameter(Mandatory = $true)][string]$Game,
    [string]$GodotExe = 'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
)
$ErrorActionPreference = 'Stop'
$qaGameRoot = (Resolve-Path -LiteralPath $Game).Path
$qaPackRoot = $PSScriptRoot
$qaRepoRoot = (Resolve-Path -LiteralPath (Join-Path $qaPackRoot '../../..')).Path
$qaReportRoot = Join-Path $qaRepoRoot 'reports/534/packing'
$qaOut = Join-Path $qaPackRoot 'qa'
New-Item -ItemType Directory -Force -Path $qaReportRoot, $qaOut | Out-Null
foreach ($qaMode in @('overview', 'actual', 'belt_stress', 'black', 'grayscale')) {
    $qaArgs = @('--path', ('"{0}"' -f $qaGameRoot), '--script', ('"{0}/qa_godot.gd"' -f $qaPackRoot),
        '--', ('"--root={0}"' -f $qaPackRoot), ('"--out={0}"' -f $qaOut), "--mode=$qaMode")
    $qaStdout = Join-Path $qaReportRoot "godot_${qaMode}_stdout.txt"
    $qaStderr = Join-Path $qaReportRoot "godot_${qaMode}_stderr.txt"
    $qaProcess = Start-Process -FilePath $GodotExe -ArgumentList $qaArgs -WorkingDirectory $qaGameRoot -WindowStyle Hidden -RedirectStandardOutput $qaStdout -RedirectStandardError $qaStderr -PassThru
    if (-not $qaProcess.WaitForExit(30000)) {
        throw "Owned Godot QA process PID=$($qaProcess.Id) did not finish within 30 seconds; raw logs: $qaReportRoot"
    }
    $qaRaw = [IO.File]::ReadAllText($qaStdout) + [IO.File]::ReadAllText($qaStderr)
    if ($qaProcess.ExitCode -ne 0 -or -not $qaRaw.Contains("GODOT_534_PASS mode=$qaMode items=6") -or $qaRaw.Contains('SCRIPT ERROR') -or $qaRaw.Contains('ERROR:') -or (Get-Item -LiteralPath $qaStderr).Length -ne 0) {
        Get-Content -LiteralPath $qaStdout
        Get-Content -LiteralPath $qaStderr
        throw "Godot #534 $qaMode failed; exit=$($qaProcess.ExitCode); raw logs: $qaReportRoot"
    }
    Write-Output "PASS #534 actual UiSkin $qaMode exit0/error0"
}
