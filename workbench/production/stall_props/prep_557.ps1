# #557 stall props intake prep - same steps as art_514/prep_514.ps1 (town_props_ab/grade_ab.ps1)
#   0) comfy/<name>_hunyuan31.glb = Comfy Cloud Hunyuan3D 3.1 (TencentImageToModelNode, face_count 5000) from refs/<name>_concept.png (Seedream 5.0 Pro)
#   1) comfy -> glb_1024 : Blender decimate_glb.py --tris=999999 --floor, texture 4096 -> 1024 (sign) / 512 (cup, 0.15 wide in game)
#   2) look_audit on glb_1024 (intake_model.ps1 -CheckOnly) -> measured lum / sat
#   3) glb_1024 -> glb_graded : tools/tex_grade.gd, #277 rule = only pull DOWN
#        brightness x min(1, 0.34 / lum) ; saturation x min(1, 0.16 / sat)
#   Materials are already matte (metallic 0, roughness 1, specular 0) - no albedo_ops matte.
#   Game scale is fitted in code (world/jumo_stall.gd: sign height 0.95, cup diameter 0.15) - files keep the generator scale.
param([string]$Game = "C:\workspace\joseon\.claude\worktrees\557-stall-props")
$B = "E:\SteamLibrary\steamapps\common\Blender\blender.exe"
$src = Join-Path $PSScriptRoot "comfy"
$mid = Join-Path $PSScriptRoot "glb_1024"
$out = Join-Path $PSScriptRoot "glb_graded"
New-Item -ItemType Directory -Force $mid | Out-Null
New-Item -ItemType Directory -Force $out | Out-Null
# name = @(texture size, measured lum, measured sat) - measured on glb_1024 (2026-10-02)
$m = [ordered]@{ away_sign = @(1024, 0.266, 0.386); cold_cup = @(512, 0.237, 0.394) }
foreach ($name in $m.Keys) {
    $r = & $B -b -P (Join-Path $Game "tools\blender\decimate_glb.py") -- "--src=$src\${name}_hunyuan31.glb" "--out=$mid\$name.glb" "--tris=999999" "--tex=$($m[$name][0])" "--floor" 2>&1 | Out-String
    $ok = if ($r -match "DECIMATE_OK") { "OK" } else { "FAIL" }
    Write-Output ("== {0} {1}: {2}" -f $m[$name][0], $name, $ok)
}
Push-Location $Game
foreach ($name in $m.Keys) {
    $v = $m[$name]
    $b = [math]::Round([math]::Min(1.0, 0.34 / $v[1]), 3)
    $s = [math]::Round([math]::Min(1.0, 0.16 / $v[2]), 3)
    $log = & godot --headless -s tools/tex_grade.gd -- "--src=$mid\$name.glb" "--out=$out\$name.glb" "--brightness=$b" "--saturation=$s" "--contrast=1.0" 2>&1 | Out-String
    $ok = if (Test-Path "$out\$name.glb") { "OK" } else { "FAIL" }
    Write-Output ("== {0}: brightness x{1} saturation x{2} -> {3}" -f $name, $b, $s, $ok)
}
Pop-Location
Write-Output "PREP DONE"
