# #316·#317 — 외형 밴드 보정(소품과 같은 목표 밝기 0.34 · 채도 0.16) → 반입(buildings/<이름>)
$wt = "C:\workspace\joseon\.claude\worktrees\164-area-system"
$src = Join-Path $PSScriptRoot "glb_1024"
$out = Join-Path $PSScriptRoot "glb_graded"
New-Item -ItemType Directory -Force $out | Out-Null
# 이름 = [잰 밝기, 잰 채도, 목표 채도]
$m = [ordered]@{ choga = @(0.420, 0.260, 0.16); giwa = @(0.307, 0.280, 0.16); well = @(0.439, 0.085, 0.16) }
Push-Location $wt
foreach ($name in $m.Keys) {
    $v = $m[$name]
    $b = [math]::Round([math]::Min(1.0, 0.34 / $v[0]), 3)
    $s = [math]::Round([math]::Min(1.0, $v[2] / $v[1]), 3)
    $log = & godot --headless -s tools/tex_grade.gd -- "--src=$src\$name.glb" "--out=$out\$name.glb" "--brightness=$b" "--saturation=$s" "--contrast=1.0" 2>&1 | Out-String
    $ok = if (Test-Path "$out\$name.glb") { "OK" } else { "FAIL" }
    Write-Output ("== grade {0}: brightness x{1} saturation x{2} -> {3}" -f $name, $b, $s, $ok)
}
foreach ($name in $m.Keys) {
    $r = & (Join-Path $wt "tools\intake_model.ps1") -Src (Join-Path $out "$name.glb") -Id "buildings/$name" -NoTest 2>&1 | Out-String
    $look = ($r -split "`r?`n" | Where-Object { $_ -match "^buildings/" }) -join " "
    Write-Output ("== intake {0} | {1}" -f $name, $look)
}
Pop-Location
Write-Output "GRADE_INTAKE DONE"
