param([switch]$BuildOnly,[switch]$RenderOnly,[switch]$SocketMeasure)
$ErrorActionPreference='Stop'
$runtime='C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
$project=$PSScriptRoot
function Invoke-IsolatedGodot([string]$phase,[string[]]$Arguments) {
    $stdout=Join-Path $project ($phase+'_stdout.log')
    $stderr=Join-Path $project ($phase+'_stderr.log')
    $info=New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName=$runtime
    $info.Arguments=$Arguments -join ' '
    $info.WorkingDirectory=$project
    $info.UseShellExecute=$false
    $info.CreateNoWindow=$true
    $info.WindowStyle=[Diagnostics.ProcessWindowStyle]::Hidden
    $info.RedirectStandardOutput=$true
    $info.RedirectStandardError=$true
    $proc=New-Object System.Diagnostics.Process
    $proc.StartInfo=$info
    $proc.Start() | Out-Null
    $readOut=$proc.StandardOutput.ReadToEndAsync()
    $readErr=$proc.StandardError.ReadToEndAsync()
    if (-not $proc.WaitForExit(30000)) {
        $proc.Kill()
        $proc.WaitForExit()
        [IO.File]::WriteAllText($stdout,$readOut.Result,(New-Object Text.UTF8Encoding($false)))
        [IO.File]::WriteAllText($stderr,$readErr.Result,(New-Object Text.UTF8Encoding($false)))
        Write-Output $readErr.Result
        [pscustomobject]@{phase=$phase;pid=$proc.Id;finished=$false} | ConvertTo-Json -Compress
        exit 3
    }
    $rawOut=$readOut.Result
    $rawErr=$readErr.Result
    [IO.File]::WriteAllText($stdout,$rawOut,(New-Object Text.UTF8Encoding($false)))
    [IO.File]::WriteAllText($stderr,$rawErr,(New-Object Text.UTF8Encoding($false)))
    [pscustomobject]@{phase=$phase;pid=$proc.Id;finished=$true;exit_code=$proc.ExitCode} | ConvertTo-Json -Compress
    if ($rawOut -and $phase -ne 'import') { Write-Output $rawOut }
    if ($rawErr) { Write-Output $rawErr }
    if ($proc.ExitCode -ne 0 -or $rawErr -match '(?m)^(SCRIPT ERROR|ERROR):') { throw ('Failed isolated phase: '+$phase) }
}
if ($SocketMeasure) {
    Invoke-IsolatedGodot 'socket_import' @('--headless','--path',('"'+$project+'"'),'--editor','--import')
    Invoke-IsolatedGodot 'socket_measure' @('--headless','--path',('"'+$project+'"'),'-s','tools/weapon_socket.gd','--',('--model='+$project+'/reference_actor/H1_doho_preserved.glb'),('--report='+$project+'/reference_actor/H1_doho_fist_fist.json'))
    exit 0
}
if (-not $RenderOnly) {
Invoke-IsolatedGodot 'build' @('--headless','--path',('"'+$project+'"'),'-s','build_modules.gd')
Invoke-IsolatedGodot 'props_build' @('--headless','--path',('"'+$project+'"'),'-s','build_props.gd')
if ($BuildOnly) { exit 0 }
Invoke-IsolatedGodot 'import' @('--headless','--path',('"'+$project+'"'),'--editor','--import')
}
Invoke-IsolatedGodot 'review' @('--path',('"'+$project+'"'),'--windowed')
if (-not (Test-Path -LiteralPath (Join-Path $project 'render_report.json'))) { throw 'No render_report.json was produced.' }
