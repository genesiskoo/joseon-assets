from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])

def trace_refine(s):
    s = replace(s, 'var hit := body.get_slide_collision(i)', 'var hit: KinematicCollision3D = body.get_slide_collision(i)')
    s = replace(s, '"rng": rng, "seed": decimal(seed), "initial": decimal(initial), "swing0": swing0,', '"rng": rng, "seed": decimal(seed), "initial": decimal(initial), "swing0": swing0,\n\t\t"hitstop0": int(visual.get("_hitstop_token")) if visual != null else 0,')
    s = replace(s, 'static func rng_key(rng: RandomNumberGenerator) -> String:', '''static func relative_swing(source: Node, absolute: int) -> int:
\tvar key := body_key(source)
\treturn absolute - int(_bodies[key].swing0) if absolute >= 0 and _bodies.has(key) else -1


static func relative_hitstop(source: Node, absolute: int) -> int:
\tvar key := body_key(source)
\treturn absolute - int(_bodies[key].hitstop0) if _bodies.has(key) else absolute


static func rng_key(rng: RandomNumberGenerator) -> String:''')
    s = replace(s, '## 終了・timeout・途中中断・tree_exitingのどれでも1回だけ。出力より前にdisabledにする。', '## 정상 종료·timeout·중단·tree_exiting 모두 한 번만 저장한다. 출력 전에 disabled로 바꾼다.')
    return s
edit('core/combat_trace.gd',trace_refine)
edit('actors/actor_visual.gd',lambda s: s.replace('"raw_mark_swing": TRACE.decimal(int(mk.no)),', '"mark_swing": TRACE.relative_swing(self, int(mk.no)), "raw_mark_swing": TRACE.decimal(int(mk.no)),').replace('"token": tok,','"token": TRACE.relative_hitstop(self, tok), "raw_token": tok,').replace('"current_token": _hitstop_token,','"current_token": TRACE.relative_hitstop(self, _hitstop_token), "raw_current_token": _hitstop_token,'))
edit('actors/player_combat.gd',lambda s: s.replace('{"generation": generation, "current_generation": _session_generation,','{"raw_generation": generation, "raw_current_generation": _session_generation,'))
edit('tests/fixtures/balance_combat_rng.gd',lambda s: replace(replace(s, 'note: Callable = Callable()) -> void:', 'note: Callable = Callable(), trace_enabled: bool = false, trace_directory: String = "") -> void:'), 'if TRACE.requested():\n\t\tTRACE.begin(_tree, {"scenario": "balance_boss", "base_seed": TRACE.decimal(base), "level": level, "attempt": attempt}, TRACE.requested_directory())', 'if trace_enabled or TRACE.requested():\n\t\tTRACE.begin(_tree, {"scenario": "balance_boss", "base_seed": TRACE.decimal(base), "level": level, "attempt": attempt}, trace_directory if not trace_directory.is_empty() else TRACE.requested_directory())'))

def ps_patch(s):
    s = replace(s, '    [string]$Scenario = "all",', '    [string]$Scenario = "all",\n    [ValidateSet(0, 60)]\n    [int]$FixedFps = 0,\n    [switch]$CombatTrace,\n    [string]$TraceOut = "",')
    s = replace(s, '$ErrorActionPreference = "Continue"', '''$ErrorActionPreference = "Continue"

# #536 고정60은 headless focused 진단만. #553 분할 루프/기본 full의 자연 시계는 유지한다.
function Test-FixedFpsAllowed([int]$Value, [bool]$IsE2e, [bool]$IsUnit, [bool]$IsExport, [bool]$IsWindowed, [bool]$IsSelfTest, [string]$Name) {
    return ($Value -eq 0 -or ($Value -eq 60 -and $IsE2e -and -not $IsUnit -and -not $IsExport -and -not $IsWindowed -and -not $IsSelfTest -and $Name -ceq "balance_boss"))
}
if (-not (Test-FixedFpsAllowed $FixedFps ([bool]$E2e) ([bool]$Unit) ([bool]$Export) ([bool]$Windowed) ([bool]$SelfTestTimeout) $Scenario)) {
    Write-Host "FAIL FixedFps60 requires only -E2e -Scenario balance_boss (headless focused replay)" -ForegroundColor Red
    exit 1
}
if (($TraceOut -and -not $CombatTrace) -or ($CombatTrace -and ($Windowed -or $SelfTestTimeout -or ($Unit -and -not $E2e) -or ($Export -and -not $E2e)))) {
    Write-Host "FAIL CombatTrace requires a headless E2e layer; TraceOut requires CombatTrace" -ForegroundColor Red
    exit 1
}''')
    s = replace(s, '[System.Text.Encoding]$Encoding = $null)\n    # 전체 경로로', '[System.Text.Encoding]$Encoding = $null, [System.Collections.IDictionary]$LaunchMetadata = $null)\n    # 전체 경로로')
    s = replace(s, '    try { $p = [System.Diagnostics.Process]::Start($psi) }', '''    try { $p = [System.Diagnostics.Process]::Start($psi) }
'''.rstrip())
    # no-op anchor above is intentional: add launch after catch, once a real process exists
    catch_line='    catch { return [pscustomobject]@{ Out = "실행 못 함: $($psi.FileName) — $($_.Exception.Message)"; Code = -1; TimedOut = $false; Sec = 0.0; Pid = 0; Note = "" } }'
    s = replace(s, catch_line, catch_line+'''
    if ($LaunchMetadata) {
        $LaunchMetadata["launcher_pid"] = $p.Id
        $LaunchMetadata["launched_utc"] = [DateTime]::UtcNow.ToString("o")
        Write-Host ("E2E_PHASE_LAUNCH " + (ConvertTo-Json -InputObject $LaunchMetadata -Depth 8 -Compress))
        if ($LaunchMetadata["contains_balance_boss"]) { Write-Host ("BALANCE_REPLAY_LAUNCH " + (ConvertTo-Json -InputObject $LaunchMetadata -Depth 8 -Compress)) }
    }''')
    anchor='# 칸 수 (#553) — -Slots > 환경 변수 JOSEON_E2E_SLOTS > $E2E_SLOTS_DEFAULT.'
    phase_functions='''# #558 실제 phase 인자와 프로세스 종료 직후 원문. 마지막 로그만 복사하지 않는다.
function Get-E2ePhaseMetadata($Phase, [string[]]$Argv, [int]$Fps, [bool]$Tracing, [string]$Exe) {
    $tokens = @($Phase.Arg -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    $contains = (($tokens -contains "balance_boss") -or ($tokens -contains "all" -and @($Phase.Skip) -notcontains "balance_boss"))
    return [ordered]@{ schema = 1; fixed_fps = $Fps; exe = $Exe; argv = @($Argv); phase_arg = $Phase.Arg;
        phase_tokens = $tokens; skip = @($Phase.Skip); exclusive = [bool]$Phase.Exclusive; contains_balance_boss = $contains;
        combat_trace = $Tracing; launcher_pid = 0; launched_utc = $null }
}

function Save-E2ePhaseRaw($Result, [System.Collections.IDictionary]$Launch, [string]$UserDir, [string]$OutDir) {
    # caller makes one fresh run/phase path; never overwrite an earlier failed or successful run.
    if (Test-Path -LiteralPath $OutDir) { throw "E2e phase archive already exists: $OutDir" }
    New-Item -ItemType Directory -Path $OutDir -ErrorAction Stop | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $OutDir "console.merged.raw.log"), $Result.Out, [System.Text.UTF8Encoding]::new($false))
    $runtimePid = $null
    foreach ($line in @($Result.Out -split "`r?`n")) {
        if ($line -match 'BALANCE_REPLAY_ENV (.+)$') {
            try { $runtimePid = [int](($Matches[1] | ConvertFrom-Json).pid) } catch { }
        }
    }
    $detail = Join-Path $UserDir "logs\\godot.log"
    $detailMeta = $null
    if (Test-Path -LiteralPath $detail) {
        $dest = Join-Path $OutDir "godot.raw.log"
        Copy-Item -LiteralPath $detail -Destination $dest -ErrorAction Stop
        $detailMeta = [ordered]@{ source = $detail; archive = $dest; bytes = (Get-Item -LiteralPath $dest).Length; sha256 = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() }
    }
    $record = [ordered]@{ schema = 1; launch = $Launch; runtime_pid = $runtimePid; exit_code = $Result.Code; timed_out = $Result.TimedOut;
        elapsed_sec = $Result.Sec; archived_utc = [DateTime]::UtcNow.ToString("o"); godot_log = $detailMeta;
        console_format = "Invoke-Step merged decoded lines; godot.raw.log is byte-exact original" }
    [System.IO.File]::WriteAllText((Join-Path $OutDir "phase.json"), (ConvertTo-Json -InputObject $record -Depth 10), [System.Text.UTF8Encoding]::new($false))
    if (-not $detailMeta) { throw "E2e phase detailed Godot log missing: $detail" }
    Write-Host ("E2E_PHASE_RAW " + $OutDir)
}

'''
    s = replace(s, anchor,phase_functions+anchor)
    test_anchor='    # ⑬ 단독 묶음 이름이 러너 SCENARIOS 에 다 있다'
    self_checks='''    # #558 fixed60 guard + actual phase tokens + detailed raw preserved before rotation (Godot battle0).
    $fixedCases = @(
        @(0,$false,$false,$false,$false,$false,"all",$true), @(60,$true,$false,$false,$false,$false,"balance_boss",$true),
        @(60,$false,$false,$false,$false,$false,"balance_boss",$false), @(60,$true,$true,$false,$false,$false,"balance_boss",$false),
        @(60,$true,$false,$true,$false,$false,"balance_boss",$false), @(60,$true,$false,$false,$true,$false,"balance_boss",$false),
        @(60,$true,$false,$false,$false,$true,"balance_boss",$false), @(60,$true,$false,$false,$false,$false,"all",$false),
        @(60,$true,$false,$false,$false,$false,"balance_boss,balance_room",$false), @(60,$true,$false,$false,$false,$false,"Balance_boss",$false))
    $guardWrong = @($fixedCases | Where-Object { (Test-FixedFpsAllowed $_[0] $_[1] $_[2] $_[3] $_[4] $_[5] $_[6]) -ne $_[7] })
    Confirm-That ($guardWrong.Count -eq 0) ("FixedFps guard: default0 + only focused60; " + $fixedCases.Count + " cases")
    $phaseFixture = [pscustomobject]@{ Arg = "balance_room,balance_boss,hit_stagger"; Skip = @(); Exclusive = $true }
    $phaseMeta = Get-E2ePhaseMetadata $phaseFixture @("--headless", "--", "--e2e=balance_room,balance_boss,hit_stagger") 0 $true "fake.exe"
    $skipMeta = Get-E2ePhaseMetadata ([pscustomobject]@{ Arg="all"; Skip=@("balance_boss"); Exclusive=$false }) @("--e2e=all") 0 $false "fake.exe"
    Confirm-That ($phaseMeta.contains_balance_boss -and $phaseMeta.phase_tokens.Count -eq 3 -and -not $skipMeta.contains_balance_boss -and $phaseMeta.fixed_fps -eq 0) "Actual phase tokens and skipped balance scenario are distinguished"
    $rawFixture = Join-Path $tmp "phase_raw_fixture"
    New-Item -ItemType Directory -Path (Join-Path $rawFixture "logs") -Force | Out-Null
    $sourceRaw = Join-Path $rawFixture "logs\\godot.log"
    $originalBytes = [byte[]](0..255)
    [System.IO.File]::WriteAllBytes($sourceRaw, $originalBytes)
    $fakeResult = [pscustomobject]@{ Out = "FAIL retained`n"; Code = 1; TimedOut = $false; Sec = 0.1 }
    $beforeRaw = Join-Path $tmp "phase_558_first"
    Save-E2ePhaseRaw $fakeResult $phaseMeta $rawFixture $beforeRaw
    [System.IO.File]::WriteAllBytes($sourceRaw, [byte[]](255..0))
    $afterRaw = Join-Path $tmp "phase_558_second"
    Save-E2ePhaseRaw $fakeResult $phaseMeta $rawFixture $afterRaw
    $retained = [System.IO.File]::ReadAllBytes((Join-Path $beforeRaw "godot.raw.log"))
    $firstMeta = Get-Content -LiteralPath (Join-Path $beforeRaw "phase.json") -Raw | ConvertFrom-Json
    Confirm-That (($retained -join ",") -eq ($originalBytes -join ",") -and $firstMeta.exit_code -eq 1 -and $firstMeta.launch.contains_balance_boss) "Failed phase raw bytes stay intact when next phase rotates the source"

'''
    s = replace(s,test_anchor,self_checks+test_anchor)
    self_tool_anchor='        # 작업 트리 도구 셀프테스트 (python+git, 임시 저장소'
    s = replace(s,self_tool_anchor,'''        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "balance_replay.py --selftest" python @("tools/balance_replay.py", "--selftest") $LIMIT_STEP "BALANCE_REPLAY_TEST checks=\\d+ fails=0 PASS" "BALANCE_REPLAY_TEST" $UTF8
            Invoke-Check "combat_trace_compare.py --selftest" python @("tools/combat_trace_compare.py", "--selftest") $LIMIT_STEP "COMBAT_TRACE_COMPARE_TEST checks=\\d+ fails=0 PASS" "COMBAT_TRACE_COMPARE_TEST" $UTF8
        }
'''+self_tool_anchor)
    s = replace(s, '        $runnerDone = $false\n        $runnerStuck = $false', '''        $runArchive = Join-Path $root ("tmp\\e2e_raw\\" + [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffffff") + "_" + $PID)
        $phaseIndex = 0
        $runnerDone = $false
        $runnerStuck = $false''')
    s = replace(s, '            foreach ($ph in $phases) {\n', '            foreach ($ph in $phases) {\n                $phaseIndex++\n')
    s = replace(s, '                    $eArgs += @("--", ("--e2e=" + $ph.Arg))', '''                    if ($FixedFps -eq 60) { $eArgs += @("--fixed-fps", "60") }
                    $eArgs += @("--", ("--e2e=" + $ph.Arg))''')
    s = replace(s, '                    if ($Shots) { $eArgs += "--e2e-shots" }\n                    $script:scriptErr = 0', '''                    if ($Shots) { $eArgs += "--e2e-shots" }
                    $phaseArchive = Join-Path $runArchive ("phase_" + $phaseIndex + "_" + $(if ($ph.Exclusive) { "solo" } else { "shared" }))
                    if ($CombatTrace) {
                        $traceBase = if ($TraceOut) { [System.IO.Path]::GetFullPath($TraceOut) } else { Join-Path $runArchive "traces" }
                        $traceDir = Join-Path $traceBase ("phase_" + $phaseIndex + "_" + $PID)
                        $eArgs += @("--combat-trace", ("--combat-trace-dir=" + $traceDir))
                    }
                    $launch = Get-E2ePhaseMetadata $ph $eArgs $FixedFps ([bool]$CombatTrace) $godot
                    $script:scriptErr = 0''')
    s = replace(s, '-Limit $LIMIT_E2E -Encoding $UTF8 -OnLine {', '-Limit $LIMIT_E2E -Encoding $UTF8 -LaunchMetadata $launch -OnLine {')
    s = replace(s, '                    if (-not $r.TimedOut -and ($r.Code -ne 0 -or $script:scriptErr -gt 0))', '''                    # Save even failure/timeout immediately, before judgment or any next Godot launch.
                    try { Save-E2ePhaseRaw $r $launch $userDir $phaseArchive }
                    catch { Write-Host ("FAIL phase raw archive: " + $_.Exception.Message) -ForegroundColor Red; $fail++ }
                    if (-not $r.TimedOut -and ($r.Code -ne 0 -or $script:scriptErr -gt 0))''')
    return s
edit('tools/test.ps1',ps_patch)
print('EXTEND558 trace IDs + #553 incremental phase archive complete')
