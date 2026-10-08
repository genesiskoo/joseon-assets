param([Parameter(Mandatory=$true)][string]$Id,[Parameter(Mandatory=$true)][string]$Source,[string]$TexturePrompt,[switch]$Humanoid)
$ErrorActionPreference='Stop'
$packRoot='C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_enemies'
$allowed=@('bandit','bat','talisman_master','boss_heukrang')
if ($Id -notin $allowed) { throw 'Unexpected enemy ID.' }
$assetRoot=Join-Path $packRoot $Id
foreach($part in @('inputs','requests','responses','inbox','models','renders')) { New-Item -ItemType Directory -Path (Join-Path $assetRoot $part) -Force | Out-Null }
$dst=Join-Path $assetRoot 'inputs/concept.png'
if (Test-Path -LiteralPath $dst) { if((Get-FileHash -LiteralPath $dst).Hash -ne (Get-FileHash -LiteralPath $Source).Hash) { throw 'Conflicting source image.' } } else { Copy-Item -LiteralPath $Source -Destination $dst }
$argsData=[ordered]@{file_path=$dst;ai_model='meshy-7';model_type='standard';topology='triangle';target_polycount=8000;should_remesh=$true;should_texture=$true;enable_pbr=$false;texture_resolution='2k';texture_prompt=$TexturePrompt;target_formats=@('glb');multi_view_thumbnails=$true;response_format='json'}
if($Humanoid) { $argsData.pose_mode='t-pose' }
$utf8=[Text.UTF8Encoding]::new($false)
$requestPath=Join-Path $assetRoot 'requests/create.json'
if(Test-Path -LiteralPath $requestPath) { throw 'Creation request already exists; inspect response before retrying.' }
[IO.File]::WriteAllText($requestPath,($argsData|ConvertTo-Json -Depth 10)+"`n",$utf8)
$meta=[ordered]@{id=$Id;source=$Source;input=$dst;input_sha256=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash;requested_at=[DateTimeOffset]::Now.ToString('o');model='meshy-7';expected_credits=30;texture_service_minimum='2k';delivery_albedo_max=1024;is_game_intake=$false}
[IO.File]::WriteAllText((Join-Path $assetRoot 'input_manifest.json'),($meta|ConvertTo-Json -Depth 8)+"`n",$utf8)
$meta|ConvertTo-Json -Depth 8
