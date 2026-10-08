# #316·#317 — Meshy가 이미 가볍게 구운 GLB(should_remesh)라 감량 없이 텍스처만 1024 → 외형 수치 재기(-CheckOnly)
$B = "E:\SteamLibrary\steamapps\common\Blender\blender.exe"
$wt = "C:\workspace\joseon\.claude\worktrees\164-area-system"
$tool = Join-Path $wt "tools\blender\decimate_glb.py"
$src = Join-Path $PSScriptRoot "glb"
$out = Join-Path $PSScriptRoot "glb_1024"
New-Item -ItemType Directory -Force $out | Out-Null
foreach ($name in @("choga", "giwa", "well")) {
    $in = Join-Path $src "$name.glb"
    $o = Join-Path $out "$name.glb"
    & $B -b -P $tool -- "--src=$in" "--out=$o" "--tris=999999" "--tex=1024" 2>&1 | Select-String "TRIS_AFTER|TEX_SCALED|DECIMATE_OK"
}
Push-Location $wt
foreach ($name in @("choga", "giwa", "well")) {
    $r = & (Join-Path $wt "tools\intake_model.ps1") -Src (Join-Path $out "$name.glb") -Id "buildings/$name" -CheckOnly 2>&1 | Out-String
    $look = ($r -split "`r?`n" | Where-Object { $_ -match "^buildings/" }) -join " "
    Write-Output ("== {0} | {1}" -f $name, $look)
}
Pop-Location
Write-Output "PREP DONE"
