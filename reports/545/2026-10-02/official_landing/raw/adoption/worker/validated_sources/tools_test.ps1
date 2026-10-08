# tools/test.ps1 — 단위 + 도구 셀프테스트 + e2e 전부 (design/testing.md). 실패가 하나라도 있으면 종료 코드 1.
#   .\tools\test.ps1            전부 = 단위 + e2e (내보내기는 안 든다 — 착륙 시험도 이것)
#   .\tools\test.ps1 -Unit      단위만
#   .\tools\test.ps1 -E2e       e2e만
#   .\tools\test.ps1 -E2e -Scenario portal_roundtrip -Windowed -Shots   창 띄우고 스크린샷
#   .\tools\test.ps1 -Export    내보낸 빌드 = 원본 대조만 (#376 — export_check.py: 캐시 지우고 PCK 내보내 원본과 대조, 약 12초.
#                               PCK 약 380MB는 끝나면 지운다). 기본 실행엔 없다 — 출시 전 필수. 전부 + 내보내기 = -Unit -E2e -Export
#   .\tools\test.ps1 -SelfTestTimeout   test.ps1 자기검사만 — 제한 시간(#181: 멈추는 대본을 짧은 제한으로 FAIL·자식 정리·잠금 풀림)
#                                       + -Export 스위치(#376: 가짜 도구로 층 고르기·판정·PCK 정리·종료 코드, 진짜 내보내기 없음)
#                                       + 단위 층 오류 줄(#401: 가짜 단위 시험 — 합격 줄 + SCRIPT ERROR = FAIL · 허용 목록 줄만 = PASS)
#                                       + 단위 층 종료 코드(#368: 합격 줄 + 오류 줄 0개라도 종료 코드 ≠ 0 이면 FAIL)
#                                       + 자리 간 e2e 칸(#553: 공유 둘·다 참·단독이 공유를 기다림·단독이 막음·문·N이 다른
#                                         자리·옛 test.ps1·죽으면 풀림·나누기·단독 묶음 이름)
#   .\tools\test.ps1 -Slots 3   자리 간 e2e 칸 수 (#553 — 기본 $E2E_SLOTS_DEFAULT · 환경 변수 JOSEON_E2E_SLOTS 도 된다. 1 = 옛 한 줄)
# 자리 간 e2e = N칸 (#553, parallel_sessions §5): 헤드리스 e2e 는 빈 칸 하나에서 다른 자리와 같이 돌고, 창 모드와 시간 민감
# 「단독 묶음」($E2E_SOLO)은 다른 자리 e2e 없이 혼자 돈다 — 착륙 시험(all)은 공유(all − 단독 묶음) + 단독(단독 묶음) 두 판으로 나뉜다.
# 자식 프로세스(godot·python)는 하나마다 제한 시간 안에 돈다 (#181) — 넘으면 자식의 자식까지 죽이고 「⏱ … 넘음 — 멈춤」 FAIL.
# 단위 층의 godot 대본은 합격 줄(「fails=0 PASS」)만 보지 않는다 (#401) — 출력에 오류 줄(SCRIPT ERROR·Parse Error·Compile Error·
# SHADER ERROR·줄 머리 ERROR:·Compilation failed)이 있으면 합격 줄이 있어도 FAIL, **종료 코드도 0이어야 PASS**(#368 — 합격
# 줄만 보고 종료 코드·오류 줄을 안 보면 컴파일이 깨져도 PASS로 잘못 알린다). 거르는 줄 = $UNIT_ERROR_IGNORE (이유와 함께).
param(
    [switch]$Unit,
    [switch]$E2e,
    [string]$Scenario = "all",
    [switch]$Windowed,
    [switch]$Shots,
    [switch]$Export,
    [switch]$SelfTestTimeout,
    [int]$Slots = 0
)
$ErrorActionPreference = "Continue"

# 제한 시간(초) — 자식 하나마다 (#181, 근거·실측 표 = testing.md #181 절). 멈춤을 빨리 잡는 값이 아니라 느린 날(다른 자리
# 시험과 겹침·재부팅 뒤 첫 실행)에도 거짓 FAIL이 안 나는 값 = 가장 느린 것의 6배 이상, 60초 아래로는 안 내린다.
# 줄 끝에 걸린 초가 찍힌다 — 실측이 제한의 1/3을 넘으면 올린다.
# 120은 #181(2026-09-22) 실측 13.9초 기준 8.6배였다 — 자리가 여럿(#436 실측, 본진 test.ps1 한 번 돌리는 동안 다른 자리들이
# 같이 돌아 powershell 17개·godot 26개)일 때 test_affixes.gd 120.5초·test_balance.gd 122.5초로 둘 다 겨우 넘겨 FAIL 찍혔다
# (도구 자체는 각각 113.8·112~초에 이미 PASS를 찍은 뒤였다 — 느려서가 아니라 여유가 없어서). 200으로 올린다(실측의 6배대 유지).
$LIMIT_STEP = 200   # 단위 대본·도구 셀프테스트·외형 표·러너 자기검사 하나 (실측 최대 13.9초 test_balance, 부하에서 최대 122.5초, 러너 자기검사 1.8초)
# wt.py --selftest 만 따로: 임시 저장소에 진짜 git(착륙·union·줄끝·겹침·prune)을 돌려(#396) 다른 셀프테스트보다 훨씬 느리고,
# git 은 디스크·자리 경합에 특히 약하다 — 공유 $LIMIT_STEP(120)의 6배 규칙을 이 하나만 못 지켰다(#181 실측 45~56초 대비 2.4배뿐).
# 자리 여럿이 동시에 test.ps1(#436 실측 — powershell 7개)을 돌리면 120초를 넘겨 착륙을 막았다. 재실측(#436, 자리 하나가 부하
# 낀 채): 145.6초·157.1초 — 1/3 규칙(줄 끝 초가 제한의 1/3을 넘으면 올린다)대로 300초도 모자라 $LIMIT_EXPORT(600)와 맞춘다.
$LIMIT_WT_SELFTEST = 600
$LIMIT_E2E = 3600   # #449: 현재97대본은900.4초에 마지막system_menu 진행 중. 전체 그물에1/3 실측 여유를 두며 개별 대본60초/timeout_sec은 유지.
$LIMIT_EXPORT = 600 # 내보낸 빌드 대조 -Export (#376, 실측 12초 = 내보내기 9.4 + 덤프 둘). 자리 준비 임포트(47초)만큼 다시 가져오기가
                    # 끼어도 넉넉한 그물. export_check.py 안의 제한(내보내기 1800·덤프 300초)은 따로 부를 때 몫 — 여기선 이게 먼저 걸린다

# 자리 간 e2e 칸 (#553, parallel_sessions §5) — 칸 수 기본값. -Slots > 환경 변수 JOSEON_E2E_SLOTS > 이 값. 1 = 옛 한 줄(나누지 않음).
# 실측(docs/art/553_e2e_slots/results.md, 2026-10-02 — 헤드리스 e2e 1·2·3·4개 동시): 흔들림 0(4개 동시 398판 다 PASS) · 벽시계
# 그대로(전부 1142초 → 1142~1145초, e2e 는 게임 시간을 기다리는 일이라 하나가 0.4코어) · 메모리 = e2e 하나 0.95 GB(4개 3.3 GB).
# 4 = 흔들림 0인 가장 큰 값 — 기본은 3(지휘 2026-10-02: PD가 같은 PC로 다른 일도 해 남은 메모리가 2~7.6 GB를 오간다 → 여유 한 칸). 한가한 날 JOSEON_E2E_SLOTS=4 · 붐비는 날 2 (자리마다 같은 값을 쓴다).
$E2E_SLOTS_DEFAULT = 3
# 단독 묶음 = 시간 민감 대본 (#553, testing.md §1) — 벽시계·프레임 시간·실전 명중 굴림으로 재서, 다른 자리 e2e 와 같이 돌면 CPU 를
# 나눠 흔들린다. 다른 자리 e2e 없이 혼자 돈다(나머지는 칸 하나에서 같이). 새 대본이 그렇게 재면 여기에 이름을 넣는다 — 이름이 러너
# SCENARIOS 에 없으면 자기검사(-SelfTestTimeout)와 단독 판(「없는 시나리오」)이 FAIL 로 알린다.
$E2E_SOLO = @(
    "balance_room",   # 실전 명중 굴림(sure_hit 끔) · 싸움 시간 · 덤빈 횟수 (#75·#97)
    "balance_boss",   # 같은 것 — 보스전 3판 안 · 탕약 · 이긴 판 시간 (#97)
    "hit_stagger",    # 경직·넉백을 짧은 타이머(0.14~0.35초)로 잰다 (combat_v2 §6.2)
    "pack_perf",      # 프레임 처리 시간(Performance.TIME_PROCESS) 표 — 같이 돌면 숫자가 남의 몫까지 먹는다 (#475)
    "bodies_cap",     # 벽시계 0.5초에 프레임 ≥ 15 (몸 36)
    "gimmicks",       # 같은 것 (몸 36 동시)
    "item_showcase",  # 이름표 다시 쌓기 ms 문턱 — 벽시계 중앙값 (#408)
    "footsteps",      # 발소리 간격을 벽시계로 — 보이는 발 디딤 ±10%
    "audio_cues",     # 추임새 = 레벨업 450~1200 ms 뒤 (벽시계)
    "sfx_limiter"     # 실시간 믹스 캡처 (벽시계 초 동안 받는다)
)

# 단위 층 오류 줄 허용 목록 (#401) — 여기 든 줄만 판정에서 거른다. 없는 오류 줄은 전부 FAIL 사유다(Find-ErrorLines).
# Text = 오류 줄에 든 글자 · Test = 어느 시험에서(-like, * = 전부) · Why = 이유. 기준 = e2e 러너 ERROR_IGNORE(#175)와 같다 —
# 게임이 틀린 게 아니라 엔진·실행 환경이 내는 소리, 또는 시험이 일부러 내는 오류(그 시험에만). 이유를 못 적으면 넣지 말고 원인을
# 고친다(새 카드). SCRIPT ERROR 는 넣지 않는다(절이 끊긴 것이다). 조사 표 = design/testing.md #401 절.
$UNIT_ERROR_IGNORE = @(
    [pscustomobject]@{ Text = "resources still in use at exit"; Test = "*"; Why = "종료 정리 보고(ResourceCache) — quit 뒤라 판정 줄 다음에 찍힌다. e2e ERROR_IGNORE 와 같은 줄" },
    [pscustomobject]@{ Text = "DungeonGen.from_layout: "; Test = "test_dungeon_gen.gd"; Why = "망가진 글자 지도 셋(닿지 않는 바닥·계단 둘·줄 길이)을 일부러 넣어 거부를 본다 — 시험이 null 을 확인하고, 진짜 보스 층 지도는 같은 시험이 따로 읽어 null 이면 FAIL" }
)
# 오류 줄 (#401, Compilation failed 는 #368) — SCRIPT ERROR(런타임·파스)·SHADER ERROR·Parse Error·Compile Error·Compilation failed
# 는 줄 어디든, 엔진 ERR_PRINT·push_error 는 줄 머리 「ERROR:」(USER ERROR 도). 대소문자 가림(-cmatch) · 줄 머리만 보는 까닭 =
# 시험이 제 문장 안에 「ERROR:」를 적어도 오류가 아니다. WARNING 은 세지 않는다(e2e 러너와 같다 — 종료 때 「ObjectDB instances
# were leaked」도 WARNING).
$ERROR_LINE = 'SCRIPT ERROR|SHADER ERROR|Parse Error|Compile Error|Compilation failed|^\s*(USER )?ERROR:'

# 콘솔 표 열 맞춤 — 한글은 두 칸 폭 (#121 외형 표)
function Get-CellWidth([string]$s) {
    $w = 0
    foreach ($ch in $s.ToCharArray()) { $u = [int]$ch; if (($u -ge 0x1100 -and $u -le 0x115F) -or ($u -ge 0x3130 -and $u -le 0x318F) -or ($u -ge 0xAC00 -and $u -le 0xD7A3)) { $w += 2 } else { $w += 1 } }
    return $w
}

# 인자 하나를 윈도우 명령줄 규칙으로 — 공백·따옴표가 있을 때만 감싼다
function ConvertTo-CmdArg([string]$a) {
    if ($a -eq "") { return '""' }
    if ($a -notmatch '[\s"]') { return $a }
    return '"' + (($a -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
}

# 프로세스와 그 자식·손자까지 (#181) — godot.bat 이면 띄운 것은 cmd.exe 고 godot.exe 는 그 자식이라, 띄운 것만 죽이면 게임이 남는다.
# .NET 호출만 쓴다 — Ctrl+C로 멈추는 중(finally)에도 돈다.
function Stop-Tree([System.Diagnostics.Process]$P) {
    try {
        $k = [System.Diagnostics.ProcessStartInfo]::new("taskkill.exe", "/PID $($P.Id) /T /F")
        $k.UseShellExecute = $false
        $k.CreateNoWindow = $true
        $k.RedirectStandardOutput = $true
        $k.RedirectStandardError = $true
        [void][System.Diagnostics.Process]::Start($k).WaitForExit(15000)
    } catch { }
    try { if (-not $P.HasExited) { $P.Kill() } } catch { }
}

function Test-Alive([int]$ProcId) {
    if ($ProcId -le 0) { return $false }
    try { return -not [System.Diagnostics.Process]::GetProcessById($ProcId).HasExited } catch { return $false }
}

function Format-Sec($r) { return ("  ({0:0.0}초)" -f $r.Sec) }

# 자식 하나를 제한 시간 안에 돌린다 (#181). stdout·stderr를 줄 단위로 같이 읽고(-OnLine 이 있으면 줄마다 부른다 — e2e 러너 줄 거르기),
# 제한을 넘으면 자식의 자식까지 죽이고 「⏱ <단계> 제한 시간 N초 넘음 — 멈춤」 FAIL 한 줄 + 마지막 출력 몇 줄을 찍고 **여기서 FAIL로 센다**
# — 부르는 쪽은 TimedOut 이면 자기 PASS/FAIL 줄을 건너뛴다.
# 반환 = Out(합친 출력) · Code(종료 코드) · TimedOut · Sec(걸린 초) · Pid(띄운 프로세스) · Note(⏱ 줄)
function Invoke-Step {
    param([string]$Label, [string]$Exe, [string[]]$ArgList, [int]$Limit, [scriptblock]$OnLine = $null, [System.Text.Encoding]$Encoding = $null)
    # 전체 경로로 — .NET 은 PATH 에서 .exe 만 찾는다(godot = ~/bin/godot.bat). 확장자 없는 것(~/bin/godot = Git Bash용 sh)은 뺀다
    $cmd = Get-Command $Exe -CommandType Application -ErrorAction SilentlyContinue | Where-Object { [System.IO.Path]::GetExtension($_.Source) -ne "" } | Select-Object -First 1
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = if ($cmd) { $cmd.Source } else { $Exe }
    $psi.Arguments = (@($ArgList | ForEach-Object { ConvertTo-CmdArg $_ }) -join " ")
    $psi.WorkingDirectory = $root
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    # 글자: 안 주면 PowerShell 이 & 로 부를 때와 같은 콘솔 인코딩(파이썬은 콘솔 코드페이지로 쓴다). godot 은 파이프에 늘 UTF-8 이라 $UTF8
    if (-not $Encoding) { $Encoding = [Console]::OutputEncoding }
    $psi.StandardOutputEncoding = $Encoding
    $psi.StandardErrorEncoding = $Encoding
    $buf = New-Object System.Text.StringBuilder
    $timedOut = $false
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try { $p = [System.Diagnostics.Process]::Start($psi) }
    catch { return [pscustomobject]@{ Out = "실행 못 함: $($psi.FileName) — $($_.Exception.Message)"; Code = -1; TimedOut = $false; Sec = 0.0; Pid = 0; Note = "" } }
    try {
        $rd = @($p.StandardOutput, $p.StandardError)
        $t = @($rd[0].ReadLineAsync(), $rd[1].ReadLineAsync())   # 줄 읽기 대기 — 그 줄기가 끝나면 $null
        $until = -1.0   # 이 시각(초)까지만 남은 출력을 더 읽는다 — 끊은 뒤, 또는 자식은 끝났는데 손자가 관을 물고 있을 때
        while ($null -ne $t[0] -or $null -ne $t[1]) {
            $k = -1
            if ($null -ne $t[0] -and $null -ne $t[1]) { $k = [System.Threading.Tasks.Task]::WaitAny([System.Threading.Tasks.Task[]]$t, 200) }
            else { $j = $(if ($null -ne $t[0]) { 0 } else { 1 }); try { if ($t[$j].Wait(200)) { $k = $j } } catch { $k = $j } }
            if ($k -ge 0) {
                $line = $null
                try { $line = $t[$k].Result } catch { }
                if ($null -eq $line) { $t[$k] = $null }
                else {
                    [void]$buf.AppendLine($line)
                    if ($OnLine) { $null = & $OnLine $line }   # 콜백이 뭘 내놓아도 반환값에 안 섞이게
                    $t[$k] = $rd[$k].ReadLineAsync()
                }
            }
            $now = $sw.Elapsed.TotalSeconds
            if (-not $timedOut -and $now -ge $Limit) { $timedOut = $true; Stop-Tree $p; $until = $now + 5 }
            elseif ($until -lt 0 -and $p.HasExited) { $until = $now + 10 }
            if ($until -ge 0 -and $now -ge $until) { break }
        }
        if (-not $p.WaitForExit(10000)) { Stop-Tree $p; [void]$p.WaitForExit(5000) }
    }
    finally {
        # Ctrl+C·예외로 빠져나가도 자식을 남기지 않는다 (e2e 잠금의 finally 보다 먼저 돈다)
        if (-not $p.HasExited) { Stop-Tree $p }
    }
    $sw.Stop()
    $note = ""
    if ($timedOut) {
        # 실제 걸린 초도 찍는다(#436) — 제한을 겨우 넘겼는지 훨씬 오래 걸렸는지(부하가 얼마나 심했는지) 로그만 보고 가른다.
        $note = "⏱ $Label 제한 시간 ${Limit}초 넘음 — 멈춤 (실제 {0:0.0}초)" -f $sw.Elapsed.TotalSeconds
        Write-Host ("  FAIL  " + $note) -ForegroundColor Red
        $tail = @($buf.ToString() -split "`r?`n" | Where-Object { $_.Trim() -ne "" } | Select-Object -Last 12)
        if ($tail.Count -gt 0) {
            Write-Host "        마지막 출력 (어디서 멈췄나):" -ForegroundColor DarkGray
            foreach ($s in $tail) { Write-Host ("        " + $s) -ForegroundColor DarkGray }
        }
        $script:fail++
    }
    return [pscustomobject]@{ Out = $buf.ToString(); Code = $(if ($p.HasExited) { $p.ExitCode } else { -1 }); TimedOut = $timedOut; Sec = $sw.Elapsed.TotalSeconds; Pid = $p.Id; Note = $note }
}

# 오류가 난 자리 (#401) — 오류 줄 다음의 「at: 함수 (파일:줄)」. 그 자리가 엔진 소스(.cpp·.h — push_error·ERR_PRINT)거나
# 비었으면(셰이더) GDScript 역추적 첫 칸 「[0] 함수 (파일:줄)」(e2e 러너 _where 와 같은 뜻). 파스 오류는 at: 이 망가진 파일을 가리킨다.
# 출력은 stdout·stderr 두 줄기를 섞은 것이라 사이에 딴 줄이 낄 수 있다 → 다음 오류·경고 줄 전까지 8줄 안에서 찾는다. 파일은 이름만.
function Find-ErrorWhere([string[]]$Lines, [int]$Index) {
    # 변수 이름은 대소문자를 안 가린다 — 인자를 $At 로 두고 $at 을 쓰니 인자가 덮였다(#401 첫 실행). 그래서 $Index·$atLine·$btLine
    $atLine = $null; $btLine = $null
    for ($j = $Index + 1; $j -lt [math]::Min($Lines.Count, $Index + 9); $j++) {
        $s = $Lines[$j]
        if ($s -cmatch $ERROR_LINE -or $s -cmatch '^\s*WARNING:') { break }
        if ($null -eq $atLine -and $s -match '^\s+at: .*\(([^()]*):(\d+)\)\s*$') { $atLine = @($Matches[1], $Matches[2]) }
        elseif ($null -eq $btLine -and $s -match '^\s+\[0\] .*\(([^()]*):(\d+)\)\s*$') { $btLine = @($Matches[1], $Matches[2]) }
    }
    $pick = $atLine
    if (($null -eq $atLine -or $atLine[0] -eq "" -or $atLine[0] -match '\.(cpp|h|c|inc)$') -and $null -ne $btLine) { $pick = $btLine }
    if ($null -eq $pick) { return "" }
    $f = [string]$pick[0]
    return $f.Substring($f.LastIndexOfAny([char[]]@('/', '\')) + 1) + ":" + $pick[1]
}

# 출력의 오류 줄($ERROR_LINE)을 센 것(Hit)과 허용 목록으로 거른 것(Skip)으로 가른다 (#401). $Name = 시험 이름(허용 목록 Test 와 맞춘다).
# 줄 순서는 안 본다 — 판정 줄 뒤(종료 때)에 찍힌 오류도 센다. 두 줄기가 섞여 읽혀 「판정 줄 앞」을 믿을 수 없고, 종료 보고는 허용 목록이 거른다.
function Find-ErrorLines([string]$Out, [string]$Name, $Ignore) {
    $lines = @($Out -split "`r?`n" | ForEach-Object { $_ -replace '\x1b\[[0-9;]*[A-Za-z]', '' })   # 색 글자(ANSI)는 벗기고 본다
    $hit = @(); $skip = @()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $s = $lines[$i]
        if ($s -cnotmatch $ERROR_LINE) { continue }
        $rule = $null
        foreach ($g in @($Ignore)) { if ($s.Contains($g.Text) -and $Name -like $g.Test) { $rule = $g; break } }
        $e = [pscustomobject]@{ Line = $s.Trim(); Where = (Find-ErrorWhere $lines $i); Rule = $rule }
        if ($rule) { $skip += $e } else { $hit += $e }
    }
    return [pscustomobject]@{ Hit = $hit; Skip = $skip }
}

function Format-ErrorLine($e) { if ($e.Where) { return $e.Line + "  (" + $e.Where + ")" }; return $e.Line }

# 합격 글자로 판정하는 단계 하나 — PASS(요약 줄 + 걸린 초) / FAIL(출력 전부) / 제한 시간 넘음(⏱ 줄은 Invoke-Step 이 찍고 센다)
# PASS 는 셋 다 — ① 종료 코드 0 ② 합격 글자($Pass) ③ (-ScanErrors 면) 예기치 않은 오류 줄 없음 (#368 — 전엔 $r.Code 를 어디서도
# 안 봐서 합격 글자만 있으면 종료 코드가 무엇이든 PASS 였다: test_balance.gd 가 SCRIPT ERROR·Compilation failed 와 종료 코드
# ≠0 을 받고도 「fails=0 PASS」 글자만 보고 PASS 로 찍힌 실측, #156). -ScanErrors (#401 — godot 대본) = 합격 글자가 있어도
# 출력에 오류 줄이 있으면 FAIL: SCRIPT ERROR 는 그 함수(절)만 끊고 _init 은 이어서 「fails=0 PASS」를 찍는다(#377 실측, 종료
# 코드는 0인 채로) — 그래서 오류 줄 검사와 종료 코드 검사는 서로 다른 구멍을 막는 별개 그물. 허용 목록($Ignore, 기본
# $UNIT_ERROR_IGNORE)에 든 줄은 거르고 PASS 줄에 수를 붙인다. 판정은 $script:lastCheck 에도 남긴다(자기검사가 본다). 한
# 단계에 FAIL 은 한 번만 센다.
function Invoke-Check([string]$Name, [string]$Exe, [string[]]$ArgList, [int]$Limit, [string]$Pass, [string]$Tag, [System.Text.Encoding]$Encoding = $null, [switch]$ScanErrors, $Ignore = $null) {
    $script:lastCheck = $null
    $r = Invoke-Step -Label $Name -Exe $Exe -ArgList $ArgList -Limit $Limit -Encoding $Encoding
    if ($r.TimedOut) { $script:lastCheck = [pscustomobject]@{ Verdict = "TIMEOUT"; PassText = $false; Hit = @(); Skip = @(); First = ""; Sec = $r.Sec; Code = $r.Code }; return }
    $err = [pscustomobject]@{ Hit = @(); Skip = @() }
    if ($ScanErrors) {
        if ($null -eq $Ignore) { $Ignore = $UNIT_ERROR_IGNORE }
        $err = Find-ErrorLines $r.Out $Name $Ignore
    }
    $passText = [bool]($r.Out -match $Pass)
    $codeOk = ($r.Code -eq 0)
    $sum = ("" + (@($r.Out -split "`r?`n" | Where-Object { $_ -match $Tag }) | Select-Object -First 1)).Trim()
    $first = if (@($err.Hit).Count -gt 0) { Format-ErrorLine $err.Hit[0] } else { "" }
    if ($passText -and @($err.Hit).Count -eq 0 -and $codeOk) {
        $note = if (@($err.Skip).Count -gt 0) { " · 허용 목록 오류 줄 {0} 거름" -f @($err.Skip).Count } else { "" }
        Write-Host ("  PASS  " + $Name + "  " + $sum + (Format-Sec $r) + $note) -ForegroundColor Green
        $verdict = "PASS"
    }
    elseif ($passText -and @($err.Hit).Count -gt 0) {
        # 합격 줄은 있는데 오류 줄이 있다 — 절이 끊겼거나(SCRIPT ERROR) 호출이 조용히 실패했다(ERROR). 오류 줄과 자리만 보인다
        Write-Host ("  FAIL  " + $Name + "  오류 줄 " + @($err.Hit).Count + " — 합격 줄이 있어도 FAIL (#401): " + $first) -ForegroundColor Red
        foreach ($e in @($err.Hit | Select-Object -Skip 1 -First 9)) { Write-Host ("        " + (Format-ErrorLine $e)) -ForegroundColor Red }
        if (@($err.Hit).Count -gt 10) { Write-Host ("        … 그 밖 " + (@($err.Hit).Count - 10) + "줄") -ForegroundColor Red }
        Write-Host ("        합격 줄: " + $sum + (Format-Sec $r)) -ForegroundColor DarkGray
        $verdict = "FAIL"; $script:fail++
    }
    elseif ($passText) {
        # 오류 줄은 없다(또는 허용 목록으로 다 걸렀다) — 그런데 종료 코드가 0이 아니다. 판정 줄 뒤에서 조용히 죽은 것도 FAIL (#368)
        Write-Host ("  FAIL  " + $Name + "  합격 줄은 있는데 종료 코드 " + $r.Code + " — FAIL (#368): " + $sum) -ForegroundColor Red
        Write-Host ("        " + $sum + (Format-Sec $r)) -ForegroundColor DarkGray
        $verdict = "FAIL"; $script:fail++
    }
    else {
        Write-Host ("  FAIL  " + $Name + $(if ($first) { "  — 첫 오류: " + $first } else { "" })) -ForegroundColor Red
        Write-Host $r.Out
        $verdict = "FAIL"; $script:fail++
    }
    $script:lastCheck = [pscustomobject]@{ Verdict = $verdict; PassText = $passText; Hit = @($err.Hit); Skip = @($err.Skip); First = $first; Sec = $r.Sec; Code = $r.Code }
}

# 단위 대본 하나 (#401, 종료 코드는 #368) — godot --headless -s <대본>, 합격 = 「fails=0 PASS」 + 오류 줄 없음 + 종료 코드 0. 본
# 실행(tests\test_*.gd)과 자기검사(가짜 시험)가 같은 함수를 지난다. $Name 은 허용 목록의 Test 와 맞추는 이름(기본 = 파일 이름) ·
# $Ignore 는 자기검사만 바꾼다.
function Invoke-UnitScript([string]$Path, [string]$Name = "", $Ignore = $null) {
    if (-not $Name) { $Name = Split-Path $Path -Leaf }
    Invoke-Check $Name $godot @("--headless", "-s", $Path) $LIMIT_STEP "fails=0 PASS" "_TEST " $UTF8 -ScanErrors -Ignore $Ignore
}

# 자리 간 e2e 칸 (#553 — 전엔 한 번에 하나, D-078). 정본 = parallel_sessions §5. 파일 = 공용 .git 안(모든 자리가 같은 것을 본다):
#   큰 잠금 joseon-e2e.lock (옛 이름 그대로) — 공유 = 읽기 손잡이(여럿이 같이 쥔다) · 단독 = 쓰기 손잡이(혼자). 옛 test.ps1 은 이
#     파일을 쓰기로 잡으니 새 공유·단독과 저절로 서로 막는다 — 옛 것은 시간 민감 대본까지 「혼자」 도는 줄 알고 돌아서(rebase 전 자리).
#   칸 joseon-e2e.1.lock … joseon-e2e.N.lock — 공유가 하나씩 쥔다(같이 도는 수 = N).
#   문 joseon-e2e.gate.lock — 단독이 기다리는 동안 쥐고 있어 새 공유를 막는다(공유는 지나가며 잠깐 쥔다 — 단독이 굶지 않게).
# 막힘 없음 = 기다리며 쥐고 있는 것은 단독의 문 하나뿐이고, 공유는 손에 쥔 채 기다리지 않는다. 자리마다 N이 달라도 단독은 큰
# 잠금으로 가린다(칸 수와 무관). 푸는 쪽 = 돌려준 것을 finally 에서 Exit-E2eSlots. 이 프로세스가 죽으면 OS가 풀어 준다.
# 기다림엔 제한이 없다(-WaitSec 은 자기검사와 「비어 있으면 단독 먼저」만) — 잡은 쪽이 자식마다 제한 시간 안에 끝나니 길어야
# 러너 자기검사 + e2e 제한이다 (#181).
function Get-BigLockPath([string]$Dir) { return (Join-Path $Dir "joseon-e2e.lock") }
function Get-SlotPath([string]$Dir, [int]$K) { return (Join-Path $Dir ("joseon-e2e.{0}.lock" -f $K)) }
function Get-GatePath([string]$Dir) { return (Join-Path $Dir "joseon-e2e.gate.lock") }

# 칸 파일 가운데 가장 큰 번호 (없으면 0) — 단독이 기다리며 「누가 도나」를 보일 때 다른 자리가 더 큰 N 으로 만든 칸까지 본다
function Get-SlotMax([string]$Dir) {
    $m = 0
    foreach ($f in @(Get-ChildItem -LiteralPath $Dir -Filter "joseon-e2e.*.lock" -ErrorAction SilentlyContinue)) {
        if ($f.Name -match '^joseon-e2e\.(\d+)\.lock$') { $m = [Math]::Max($m, [int]$Matches[1]) }
    }
    return $m
}

function Get-SlotMark([int]$K) { if ($K -ge 1 -and $K -le 20) { return [string][char](0x2460 + $K - 1) }; return "($K)" }

# 잠금 파일을 쓰기로 잡는다 — 쓰기는 혼자, 읽기는 남도(누가 쥐었나 보이게). 남이 쥐었으면(읽기·쓰기 손잡이 어느 것이든) $null
function Open-LockFile([string]$Path) {
    try { return [System.IO.File]::Open($Path, 'OpenOrCreate', 'ReadWrite', 'Read') } catch { return $null }
}

# 큰 잠금의 읽기 손잡이 — 읽기 손잡이끼리는 같이 쥔다, 쓰기 손잡이(단독·옛 test.ps1)가 있으면 $null
function Open-LockRead([string]$Path) {
    try { return [System.IO.File]::Open($Path, 'OpenOrCreate', 'Read', 'Read') } catch { return $null }
}

# 누가 쥐고 있나만 본다 — 혼자 열었다 바로 닫는다(파일이 없거나 열리면 빈 것)
function Test-LockHeld([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    try { $s = [System.IO.File]::Open($Path, 'Open', 'ReadWrite', 'None'); $s.Close(); return $false } catch { return $true }
}

function Set-LockText($Stream, [string]$Text) {
    $Stream.SetLength(0)
    if ($Text) { $b = [System.Text.Encoding]::UTF8.GetBytes($Text); $Stream.Write($b, 0, $b.Length) }
    $Stream.Flush()
}

function Get-LockMe([string]$Mode) { return "$root · pid $PID · $(Get-Date -Format 'HH:mm') · $Mode" }

# 잠금 파일에 쥔 쪽이 적은 글 그대로 (못 읽으면 $null)
function Read-LockText([string]$Path) {
    try {
        $r = [System.IO.File]::Open($Path, 'Open', 'Read', 'ReadWrite')
        try { return (New-Object System.IO.StreamReader($r)).ReadToEnd().Trim() } finally { $r.Close() }
    } catch { return $null }
}

# 쥔 쪽 — 자리 경로는 worktrees\ 뒤만(codex 자리는 …\worktrees\<자리>\joseon). 못 읽으면 「?」, 비었으면 ""
function Read-LockOwner([string]$Path) {
    $s = Read-LockText $Path
    if ($null -eq $s) { return "?" }
    return ($s -replace '^.*[\\/]worktrees[\\/]', '')
}

# 찬 칸 한 칸 — 「② <쥔 쪽>」 (쥔 쪽이 글을 안 남겼으면 「?」)
function Format-SlotBusy([int]$K, [string]$Path) {
    $o = Read-LockOwner $Path
    if (-not $o) { $o = "?" }
    return ((Get-SlotMark $K) + " " + $o)
}

# 칸 잡기 (#553). 공유 = 문을 지나가며 큰 잠금 읽기 손잡이 + 빈 칸 하나 · 단독(-Exclusive) = 문을 쥐고 큰 잠금 쓰기 손잡이.
# 돌려주는 것 = 쥔 것(Exit-E2eSlots 로 푼다 — Slots = 쥔 칸 번호, 단독은 없음) 또는 $null(-WaitSec 안에 못 잡음 — 쥔 것은 다 놓고
# 돌아온다). 기다리는 동안 「몇 칸 중 몇 칸이 누구로 찼는지」를 바뀔 때마다 한 줄 찍는다(-Quiet 면 안 찍는다) — 자기검사가 보게
# $script:e2eWaitLines 에도 남긴다. $Why = 단독 까닭(줄에 붙는다).
$script:e2eWaitLines = @()
function Enter-E2eSlots([string]$Dir, [int]$N, [switch]$Exclusive, [string]$Why = "", [double]$WaitSec = -1, [switch]$Quiet) {
    if ($N -lt 1) { $N = 1 }
    $gatePath = Get-GatePath $Dir
    $bigPath = Get-BigLockPath $Dir
    $poll = if ($WaitSec -ge 0) { 0.25 } else { 5.0 }
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $said = ""
    $gate = $null
    $done = $false
    try {
        while ($true) {
            $line = ""
            $retry = $poll
            if ($Exclusive) {
                if ($null -eq $gate) {
                    $gate = Open-LockFile $gatePath
                    if ($gate) { Set-LockText $gate (Get-LockMe ("단독 대기" + $Why)) }
                }
                if ($null -eq $gate) {
                    $who = Read-LockOwner $gatePath
                    if ($who) { $line = "⏳ 다른 자리가 먼저 단독 차례 ($who) — 그 뒤에 이어서 돈다" }
                    else { $retry = 0.2; $line = $said }   # 공유가 문을 지나가는 찰나 — 곧 다시
                }
                else {
                    $big = Open-LockFile $bigPath
                    if ($big) {
                        Set-LockText $big (Get-LockMe ("단독" + $Why))
                        Set-LockText $gate (Get-LockMe ("단독" + $Why))
                        $done = $true
                        return [pscustomobject]@{ Exclusive = $true; Gate = $gate; Big = $big; Streams = @(); Slots = @() }
                    }
                    # 큰 잠금을 누가 쥐었나 — 공유 판(칸) 아니면 옛 test.ps1. 문을 쥐었으니 새 공유는 못 들어온다 → 돌던 것만 기다린다
                    $m = [Math]::Max($N, (Get-SlotMax $Dir))
                    $busy = @()
                    for ($k = 1; $k -le $m; $k++) {
                        $p = Get-SlotPath $Dir $k
                        if (Test-LockHeld $p) { $busy += (Format-SlotBusy $k $p) }
                    }
                    if ($busy.Count -gt 0) {
                        $line = ("⏳ 단독{0} — 공유 칸 {1}/{2} 아직 도는 중: {3} — 끝나면 혼자 돈다 (새 공유는 막아 둠)" -f $Why, $busy.Count, $m, ($busy -join " · "))
                    }
                    else {
                        $o = Read-LockOwner $bigPath
                        if (-not $o) { $o = "?" }
                        $line = ("⏳ 단독{0} — 옛 test.ps1 이 e2e 중 ({1}) — 끝나면 혼자 돈다 (새 공유는 막아 둠)" -f $Why, $o)
                    }
                    if ($retry -gt 1.0) { $retry = 1.0 }   # 문을 쥐었으니 자주 본다 — 큰 잠금이 비는 찰나를 옛 test.ps1(5초마다)에 뺏기지 않게
                }
            }
            else {
                $g = Open-LockFile $gatePath
                if ($null -eq $g) {
                    $who = Read-LockOwner $gatePath
                    if ($who) { $line = "⏳ 다른 자리의 단독 차례 ($who) — 끝나면 이어서 돈다" }
                    else { $retry = 0.2; $line = $said }   # 다른 공유가 문을 지나가는 찰나 — 곧 다시
                }
                else {
                    try {
                        $rd = Open-LockRead $bigPath
                        if ($null -eq $rd) {
                            # 쓰기 손잡이가 있다 — 단독은 문을 쥐고 도니(지금 문은 내 손) 옛 test.ps1 이다
                            $o = Read-LockOwner $bigPath
                            if (-not $o) { $o = "?" }
                            $line = "⏳ 옛 test.ps1 이 e2e 중 ($o) — 옛 것은 혼자 도는 줄 알고 돌아서 끝나면 이어서 돈다"
                        }
                        else {
                            $owners = @()
                            for ($k = 1; $k -le $N; $k++) {
                                $p = Get-SlotPath $Dir $k
                                $s = Open-LockFile $p
                                if ($s) {
                                    Set-LockText $s (Get-LockMe "공유")
                                    $done = $true
                                    return [pscustomobject]@{ Exclusive = $false; Gate = $null; Big = $rd; Streams = @($s); Slots = @($k) }
                                }
                                $owners += (Format-SlotBusy $k $p)
                            }
                            $rd.Close()
                            $line = ("⏳ e2e 칸 {0}/{0} 참 — {1} — 빈 칸이 나면 이어서 돈다" -f $N, ($owners -join " · "))
                        }
                    }
                    finally { $g.Close() }
                }
            }
            if ($line -and $line -ne $said) {
                if (-not $Quiet) { Write-Host ("  " + $line) -ForegroundColor Yellow }
                $script:e2eWaitLines += $line
                $said = $line
            }
            if ($WaitSec -ge 0 -and $sw.Elapsed.TotalSeconds -ge $WaitSec) { return $null }
            Start-Sleep -Milliseconds ([int]($retry * 1000))
        }
    }
    finally {
        # 못 잡고 나가면(-WaitSec 넘음 · Ctrl+C) 쥐었던 문을 놓는다 — 단독이 문을 쥔 채 남지 않게
        if (-not $done -and $gate) { try { Set-LockText $gate "" } catch { }; try { $gate.Close() } catch { } }
    }
}

# 칸 풀기 — 칸 → 큰 잠금(단독이면 글을 비우고) → 문(글을 비우고 — 문이 잠겼는데 글이 비면 「공유가 지나가는 찰나」로 읽는다)
function Exit-E2eSlots($H) {
    if ($null -eq $H) { return }
    foreach ($s in @($H.Streams)) { try { $s.Close() } catch { } }
    if ($H.Big) {
        if ($H.Exclusive) { try { Set-LockText $H.Big "" } catch { } }
        try { $H.Big.Close() } catch { }
    }
    if ($H.Gate) { try { Set-LockText $H.Gate "" } catch { }; try { $H.Gate.Close() } catch { } }
}

# e2e 나누기 (#553) — Shared = 공유 칸에서 돌 --e2e 값(Skip = 그때 --e2e-skip 이름) · Solo = 단독으로 돌 --e2e 값. 없으면 $null.
# 창 모드·칸 1개 = 나누지 않고 통째로 단독(옛 한 줄과 같다). all = 공유 all − 단독 묶음(러너가 뺀다) + 단독 묶음. 이름 목록 = 두 쪽으로.
function Get-E2ePlan([string]$Scenario, [string[]]$SoloList, [bool]$IsWindowed, [int]$N) {
    $sc = if ($Scenario) { $Scenario.Trim() } else { "" }
    if ($sc -eq "") { $sc = "all" }
    $solo = @($SoloList | Where-Object { $_ })
    if ($IsWindowed -or $N -le 1) { return [pscustomobject]@{ Shared = $null; Skip = @(); Solo = $sc } }
    if ($sc -eq "all") {
        if ($solo.Count -eq 0) { return [pscustomobject]@{ Shared = "all"; Skip = @(); Solo = $null } }
        return [pscustomobject]@{ Shared = "all"; Skip = $solo; Solo = ($solo -join ",") }
    }
    $names = @($sc -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
    $sh = @($names | Where-Object { $solo -notcontains $_ })
    $so = @($names | Where-Object { $solo -contains $_ })
    $shared = $null; $soloArg = $null
    if ($sh.Count -gt 0) { $shared = $sh -join "," }
    if ($so.Count -gt 0) { $soloArg = $so -join "," }
    return [pscustomobject]@{ Shared = $shared; Skip = @(); Solo = $soloArg }
}

# 칸 수 (#553) — -Slots > 환경 변수 JOSEON_E2E_SLOTS > $E2E_SLOTS_DEFAULT. 숫자가 아니면 기본값(한 줄 알림)
function Get-E2eSlotCount([int]$Param) {
    if ($Param -gt 0) { return $Param }
    $e = $env:JOSEON_E2E_SLOTS
    if ($e) {
        if ($e -match '^\s*(\d+)\s*$' -and [int]$Matches[1] -ge 1) { return [int]$Matches[1] }
        Write-Host ("  ⚠ JOSEON_E2E_SLOTS=" + $e + " — 1 이상 숫자가 아니라 기본 " + $E2E_SLOTS_DEFAULT + "칸") -ForegroundColor Yellow
    }
    return $E2E_SLOTS_DEFAULT
}

# 어느 층을 돌리나 (#376) — 스위치가 하나도 없으면 단위 + e2e (전과 같다 · 착륙 시험). 내보내기는 기본에 안 든다:
# -Export 만 주면 그것만, -Unit·-E2e 와 같이 주면 같이. 본 실행과 자기검사가 같은 함수를 쓴다.
function Get-Layers([bool]$U, [bool]$E, [bool]$X) {
    if (-not $U -and -not $E -and -not $X) { $U = $true; $E = $true }
    return [pscustomobject]@{ Unit = $U; E2e = $E; Export = $X }
}

# 층 이름 줄 — 목록을 += 로 쌓는다. @($(if …), $(if …), "c") 처럼 빈 $(…) 둘 뒤에 값이 오면 그 배열을 파이프에 넣었을 때
# 원소가 하나도 안 나왔다(PowerShell 5.1 실측 — Count 는 3 · Where-Object 는 0개, 빈 것 하나 뒤는 나왔다). 빈 값을 배열에 안 넣는다.
function Format-Layers($L) {
    $n = @()
    if ($L.Unit) { $n += "단위" }
    if ($L.E2e) { $n += "e2e" }
    if ($L.Export) { $n += "내보내기" }
    return $n -join "·"
}

# 내보낸 빌드 = 원본 대조 층 (#376, testing.md #376 절) — export_check.py(#349)를 제한 시간 안에 돌린다.
# 판정 = 도구의 끝 줄 「EXPORT_CHECK files=… PASS」 와 종료 코드 0 둘 다 — 하나만이면 FAIL (판정 없는 초록 금지).
# 도구 줄은 흐르는 대로 찍고(내보내기 초·PCK 크기·덤프·doho 줄, ✗·FAIL 줄은 빨강) 끝에 PASS/FAIL 줄 + 걸린 초·제한.
# 제한을 넘으면 ⏱ 줄은 Invoke-Step 이 찍고 센다. 끝나면(PASS·FAIL·멈춤·Ctrl+C) <OutDir>\game.pck 를 지운다 — 도구도 스스로
# 지우지만(try/finally) 자식째 죽이면 도구의 정리가 못 돈다. 도구는 stdout 을 UTF-8 로 바꿔 쓴다 → UTF-8 로 읽는다.
function Invoke-ExportCheck([string]$Tool, [string]$OutDir, [int]$Limit) {
    $pck = Join-Path $OutDir "game.pck"
    $r = $null
    try {
        $r = Invoke-Step -Label "export_check.py" -Exe python -ArgList @($Tool, "--out", $OutDir) -Limit $Limit -Encoding $UTF8 -OnLine {
            param($s)
            if ($s.Trim() -eq "" -or $s -match "^== |^EXPORT_CHECK ") { return }   # 도구 머리 줄 = 층 머리 줄 · 끝 줄 = 아래 판정 줄
            Write-Host ("  " + $s.TrimEnd()) -ForegroundColor $(if ($s -match "✗|FAIL|Traceback|Error") { "Red" } elseif ($s -match "⚠") { "Yellow" } else { "DarkGray" })   # 한 칸 들여 (판정 줄보다 안쪽)
        }
    }
    finally {
        if (Test-Path -LiteralPath $pck) {
            Remove-Item -LiteralPath $pck -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $pck) { Write-Host ("  ⚠ PCK 를 못 지웠다 — " + $pck) -ForegroundColor Yellow }
            else { Write-Host ("  · 남은 PCK 지움 — " + $pck) -ForegroundColor DarkGray }
        }
    }
    if ($r.TimedOut) { return $r }
    $sum = ("" + (@($r.Out -split "`r?`n" | Where-Object { $_ -match "^EXPORT_CHECK " }) | Select-Object -Last 1)).Trim()
    $okLine = $sum -match '^EXPORT_CHECK files=\d+ .*PASS$'
    $took = " ({0:0.0}초 — 제한 {1}초)" -f $r.Sec, $Limit
    if ($r.Code -eq 0 -and $okLine) { Write-Host ("  PASS  export_check.py  " + $sum + $took) -ForegroundColor Green }
    else {
        $why = if (-not $sum) { "끝 줄 EXPORT_CHECK 없음 (종료 코드 $($r.Code)) — 판정 전에 끝났다" }
               elseif ($okLine) { "끝 줄은 PASS인데 종료 코드 $($r.Code)" }
               else { $sum }
        Write-Host ("  FAIL  export_check.py  " + $why + $took) -ForegroundColor Red
        if ($r.Pid -eq 0) { Write-Host ("        " + $r.Out) -ForegroundColor Red }   # python 을 못 띄웠다 (출력이 흐르지 않았다)
        $script:fail++
    }
    return $r
}

$root = Split-Path -Parent $PSScriptRoot
$godot = if ($env:GODOT_BIN) { $env:GODOT_BIN } else { "godot" }
$UTF8 = New-Object System.Text.UTF8Encoding $false   # godot 출력은 파이프에서 늘 UTF-8 (#181 실측)
$fail = 0
# 내보낸 빌드 대조 (#376) — 도구와 PCK 자리. 자리 = 도구를 따로 부를 때의 기본(%TEMP%\joseon_export_check_<자리 폴더 이름>)과
# 같은 곳이라 자리마다 한 곳뿐이다. 환경 변수는 자기검사가 가짜 도구·임시 자리로 바꿀 때만 쓴다 (GODOT_BIN 과 같은 모양).
$exportTool = if ($env:JOSEON_EXPORT_TOOL) { $env:JOSEON_EXPORT_TOOL } else { "tools\export_check.py" }
$exportOut = if ($env:JOSEON_EXPORT_OUT) { $env:JOSEON_EXPORT_OUT } else { Join-Path $env:TEMP ("joseon_export_check_" + (Split-Path $root -Leaf)) }

# 제한 시간 자기검사 (#181) — 끝나지 않는 대본(tests/fixtures/hang.gd)을 짧은 제한으로 돌려 ① FAIL로 센다(→ 종료 코드 1)
# ② 자식의 자식까지 죽인다 ③ 칸이 풀린다 를 본다. 칸은 임시 폴더(다른 자리의 진짜 e2e 칸과 안 부딪게) — 잡고 푸는 코드는 e2e 와 같다.
# 이어서 자리 간 e2e 칸 (#553) · -Export 스위치 (#376) · 단위 층 오류 줄 (#401) — 임시 폴더의 칸 파일·가짜(도구·단위 시험)로,
# 부르는 함수는 본 실행과 같은 것.
if ($SelfTestTimeout) {
    Write-Host "== test.ps1 자기검사 — 제한 시간 (#181, 부하에서 실제 걸린 초 #436) · e2e 칸 (#553) · -Export 스위치 (#376) · 단위 층 오류 줄 (#401) ==" -ForegroundColor Cyan
    $script:ok = 0; $script:bad = 0
    function Confirm-That([bool]$c, [string]$what) {
        if ($c) { $script:ok++; Write-Host ("  ✓ " + $what) -ForegroundColor Green } else { $script:bad++; Write-Host ("  ✗ " + $what) -ForegroundColor Red }
    }
    $tmp = Join-Path $env:TEMP ("joseon_timeout_selftest_" + $PID)
    New-Item -ItemType Directory -Force $tmp | Out-Null
    $pidFile = Join-Path $tmp "hang.pid"
    $slotDir = Join-Path $tmp "slots_hang"
    New-Item -ItemType Directory -Force $slotDir | Out-Null
    $hang = Join-Path $root "tests\fixtures\hang.gd"
    # #449: GODOT_BIN이 exe여도 실제 자식 구조를 만들어 손자 정리를 검사한다.
    $childLauncher = Join-Path $tmp "godot_child.cmd"
    $childTarget = (Get-Command $godot -ErrorAction Stop).Source
    Set-Content -LiteralPath $childLauncher -Value @("@echo off", ('call "' + $childTarget + '" %*'), "exit /b %errorlevel%") -Encoding ASCII

    # 대조군 — 멈추지 않는 대본은 제한 안에 그대로 끝나고, 종료 코드가 godot.bat(cmd.exe) 너머로 온다
    $f0 = $fail
    $r = Invoke-Step -Label "hang.gd --quit=3" -Exe $childLauncher -ArgList @("--headless", "-s", $hang, "--", "--quit=3") -Limit 60 -Encoding $UTF8
    Confirm-That ((-not $r.TimedOut) -and $r.Code -eq 3 -and $r.Out -match "HANG_FIXTURE quit 3" -and $fail -eq $f0) ("대조군: 멈추지 않는 대본은 그대로 — 종료 코드 {0} · 출력 받음 · {1:0.0}초" -f $r.Code, $r.Sec)

    # 멈추는 godot — e2e 와 같은 칸 안에서(공유 칸 하나), 제한 8초 (godot 이 뜨는 데 1~2초)
    $lim = 8
    $f0 = $fail
    $lock = Enter-E2eSlots -Dir $slotDir -N 2
    try { $r = Invoke-Step -Label "hang.gd" -Exe $childLauncher -ArgList @("--headless", "-s", $hang, "--", "--pid-file=$pidFile") -Limit $lim -Encoding $UTF8 }
    finally { Exit-E2eSlots $lock }
    # 실제 걸린 초(#436)가 붙어 뒤가 달라지니 접두사만 본다 — 값은 바로 아래 $r.Sec 검사가 잰다.
    Confirm-That ($r.TimedOut -and $fail -eq $f0 + 1 -and $r.Note.StartsWith("⏱ hang.gd 제한 시간 ${lim}초 넘음 — 멈춤")) ("넘으면 FAIL로 센다(→ 종료 코드 1) · 줄 = 「" + $r.Note + "」")
    Confirm-That ($r.Sec -ge $lim -and $r.Sec -lt $lim + 10) ("제한에서 끊음 — {0:0.0}초 (제한 {1}초)" -f $r.Sec, $lim)
    $gpid = 0
    if (Test-Path $pidFile) { $gpid = [int]((Get-Content $pidFile -Raw).Trim()) }
    Confirm-That ($gpid -gt 0 -and $gpid -ne $r.Pid) ("godot.exe(pid $gpid)는 띄운 것(pid $($r.Pid), godot_child.cmd → cmd.exe)의 자식이었다 — 손자까지 죽여야 하는 경우")
    Confirm-That ((-not (Test-Alive $r.Pid)) -and (-not (Test-Alive $gpid))) "자식까지 정리 — 띄운 것·godot.exe 둘 다 사라짐"
    $free = (Test-Path -LiteralPath (Get-BigLockPath $slotDir)) -and -not (Test-LockHeld (Get-BigLockPath $slotDir)) -and -not (Test-LockHeld (Get-SlotPath $slotDir 1))
    Confirm-That $free "칸 풀림 — finally 뒤 큰 잠금·칸 ① 을 혼자(FileShare.None) 다시 잡음"

    # 멈추는 python — 감싸는 cmd 없는 자식도 같은 길, 끊기 전 출력은 남는다(마지막 출력)
    $f0 = $fail
    $r = Invoke-Step -Label "python sleep" -Exe python -ArgList @("-c", "import time; print('PY_HANG', flush=True); time.sleep(600)") -Limit 4
    Confirm-That ($r.TimedOut -and $fail -eq $f0 + 1 -and (-not (Test-Alive $r.Pid)) -and $r.Out -match "PY_HANG") ("python 도 같은 길 — FAIL · 정리 · 끊기 전 출력 남음 ({0:0.0}초)" -f $r.Sec)

    # 자리 간 e2e 칸 (#553) — 임시 폴더의 칸 파일로. 잡고 푸는 함수(Enter-E2eSlots · Exit-E2eSlots)·나누기(Get-E2ePlan)는 본 실행과
    # 같은 것. 파일 공유 모드는 한 프로세스 안에서도 핸들마다 걸리니(위 「칸 풀림」과 같은 셈) 다른 자리를 흉내 낼 수 있다.
    # -WaitSec = 못 잡으면 그만큼 기다리다 $null(쥐었던 것은 놓고) — 본 실행은 끝없이 기다린다.
    Write-Host "-- 자리 간 e2e 칸 (#553) — 임시 폴더의 칸 파일로 --" -ForegroundColor Cyan
    $sd = Join-Path $tmp "slots"
    New-Item -ItemType Directory -Force $sd | Out-Null
    $pb = Get-BigLockPath $sd; $p1 = Get-SlotPath $sd 1; $p2 = Get-SlotPath $sd 2; $p3 = Get-SlotPath $sd 3; $pg = Get-GatePath $sd
    # 옛 test.ps1(#553 전)이 잡는 꼴 — 큰 잠금을 쓰기로(ReadWrite · 남은 읽기만). 잡히면 그 손잡이, 못 잡으면 $null
    function Open-OldStyle([string]$p) { try { return [System.IO.File]::Open($p, 'OpenOrCreate', 'ReadWrite', 'Read') } catch { return $null } }
    # ① 공유 = 큰 잠금 읽기 손잡이 + 빈 칸 하나 — 첫째 칸 ①, 둘째 칸 ② (같이 돈다) · 큰 잠금 = 옛 이름 · 옛 test.ps1 은 못 들어온다
    $sa = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 2
    $sb = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 2
    $oldIn = Open-OldStyle $pb
    if ($oldIn) { $oldIn.Close() }
    Confirm-That ($sa -and $sb -and (@($sa.Slots) -join ",") -eq "1" -and (@($sb.Slots) -join ",") -eq "2" -and (Split-Path $pb -Leaf) -eq "joseon-e2e.lock" -and (Test-LockHeld $p1) -and (Test-LockHeld $p2) -and $null -eq $oldIn) "공유 둘이 같이 — 칸 ①·② · 큰 잠금(옛 이름 joseon-e2e.lock) 읽기 손잡이 둘 → 옛 test.ps1(쓰기)은 못 들어온다"
    # ② 다 차면 기다린다 — 기다리는 줄 = 몇 칸 중 몇 칸이 누구로
    $script:e2eWaitLines = @()
    $tw = [System.Diagnostics.Stopwatch]::StartNew()
    $sc3 = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 1.5
    $waited = $tw.Elapsed.TotalSeconds
    $wl = (@($script:e2eWaitLines) -join " | ")
    Confirm-That ($null -eq $sc3 -and $waited -ge 1.5 -and $wl -match "칸 2/2 참" -and $wl.Contains((Get-SlotMark 1) + " ") -and $wl.Contains((Get-SlotMark 2) + " ") -and ([regex]::Matches($wl, "pid $PID")).Count -ge 2) ("다 차면 기다린다 ({0:0.0}초) · 줄 = 「{1}」" -f $waited, $wl)
    # ③ 칸이 비면 기다리던 쪽이 그 칸을
    Exit-E2eSlots $sa
    $sc3 = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 2
    Confirm-That ($sc3 -and (@($sc3.Slots) -join ",") -eq "1") "칸 ① 이 비면 기다리던 쪽이 잡는다"
    Exit-E2eSlots $sc3
    # ④ 단독은 돌던 공유가 끝나기를 기다린다 — 못 잡고 나가면 쥐었던 문을 놓는다
    $script:e2eWaitLines = @()
    $sx = Enter-E2eSlots -Dir $sd -N 2 -Exclusive -Why "(시험)" -WaitSec 1.5
    $wl = (@($script:e2eWaitLines) -join " | ")
    Confirm-That ($null -eq $sx -and $wl -match "공유 칸 1/2 아직 도는 중" -and $wl.Contains((Get-SlotMark 2) + " ") -and -not (Test-LockHeld $pg)) ("단독은 공유 칸 ② 가 끝나기를 기다린다 · 못 잡으면 문을 놓는다 · 줄 = 「" + $wl + "」")
    Exit-E2eSlots $sb
    # ⑤ 다 비면 단독 = 문 + 큰 잠금 쓰기 손잡이 · ⑥ 단독이 도는 동안 공유도 옛 test.ps1 도 기다린다 · 풀면 다 빔
    $sx = Enter-E2eSlots -Dir $sd -N 2 -Exclusive -WaitSec 2
    $oldIn = Open-OldStyle $pb
    if ($oldIn) { $oldIn.Close() }
    Confirm-That ($sx -and (Test-LockHeld $pb) -and (Test-LockHeld $pg) -and $null -eq $oldIn -and (Read-LockOwner $pb) -match "단독") "단독 = 문 + 큰 잠금 쓰기 손잡이(글 = 단독) — 옛 test.ps1 도 못 들어온다"
    $script:e2eWaitLines = @()
    $sc3 = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 1.5
    $wl = (@($script:e2eWaitLines) -join " | ")
    Confirm-That ($null -eq $sc3 -and $wl -match "단독 차례") ("단독이 도는 동안 공유는 기다린다 · 줄 = 「" + $wl + "」")
    Exit-E2eSlots $sx
    Confirm-That (-not (Test-LockHeld $pb) -and -not (Test-LockHeld $pg) -and -not (Test-LockHeld $p1) -and (Read-LockOwner $pg) -eq "" -and (Read-LockOwner $pb) -eq "") "단독 풀림 — 큰 잠금·문·칸 다 빔 · 글을 지운다(문이 잠겼는데 글이 비면 「공유가 지나가는 찰나」)"
    # ⑦ 문 — 단독이 공유가 끝나기를 기다리는 동안 새 공유는 빈 칸이 있어도 안 들어온다(단독이 굶지 않게)
    $gw = Open-LockFile $pg
    Set-LockText $gw (Get-LockMe "단독 대기(시험)")
    $sc3 = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 1.5
    Set-LockText $gw ""
    $gw.Close()
    Confirm-That ($null -eq $sc3 -and -not (Test-LockHeld $p1) -and -not (Test-LockHeld $p2)) "문이 잠긴 동안(단독이 기다리는 중) 새 공유는 빈 칸이 있어도 안 들어온다"
    # ⑧ 자리마다 N이 달라도 — N=3 자리의 공유 셋(칸 ①②③)이 돌면 N=2 자리의 단독도 큰 잠금으로 기다리고, 줄에 칸 ③ 까지 보인다
    $w3 = @(1..3 | ForEach-Object { Enter-E2eSlots -Dir $sd -N 3 -WaitSec 2 })
    $script:e2eWaitLines = @()
    $sx = Enter-E2eSlots -Dir $sd -N 2 -Exclusive -WaitSec 1
    $wl = (@($script:e2eWaitLines) -join " | ")
    foreach ($w in $w3) { Exit-E2eSlots $w }
    Confirm-That ((@($w3 | Where-Object { $_ }).Count -eq 3) -and $null -eq $sx -and $wl -match "공유 칸 3/3 아직 도는 중" -and $wl.Contains((Get-SlotMark 3) + " ")) ("N=3 공유 셋이 돌면 N=2 단독도 기다린다 · 줄 = 「" + $wl + "」")
    # ⑨ 옛 test.ps1 이 큰 잠금(쓰기)을 쥐면 — 공유도 단독도 기다린다(옛 것은 시간 민감 대본까지 혼자 도는 줄 알고 돈다)
    $oldLock = Open-OldStyle $pb
    Set-LockText $oldLock ("C:\옛\worktrees\old-site · pid 1 · 05:00")
    $script:e2eWaitLines = @()
    $sc3 = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 1.5
    $sx = Enter-E2eSlots -Dir $sd -N 2 -Exclusive -WaitSec 1.5
    $wl = (@($script:e2eWaitLines) -join " | ")
    $oldLock.Close()
    Confirm-That ($null -eq $sc3 -and $null -eq $sx -and $wl -match "옛 test.ps1 이 e2e 중 \(old-site" -and -not (Test-LockHeld $p1) -and -not (Test-LockHeld $pg)) ("옛 test.ps1 이 큰 잠금을 쥐면 공유도 단독도 기다린다 · 줄 = 「" + $wl + "」")
    # ⑩ 「비어 있으면 단독 먼저」 = 한 번만 해 본다(-WaitSec 0) — 공유가 돌면 곧바로 그만(문 놓음), 다 비면 곧바로 잡는다
    $sa = Enter-E2eSlots -Dir $sd -N 2
    $tq = [System.Diagnostics.Stopwatch]::StartNew()
    $q1 = Enter-E2eSlots -Dir $sd -N 2 -Exclusive -WaitSec 0 -Quiet
    $q1s = $tq.Elapsed.TotalSeconds
    $q1free = -not (Test-LockHeld $pg)
    Exit-E2eSlots $sa
    $q2 = Enter-E2eSlots -Dir $sd -N 2 -Exclusive -WaitSec 0 -Quiet
    Confirm-That ($null -eq $q1 -and $q1s -lt 1.0 -and $q1free -and $q2 -and $q2.Exclusive) ("「비어 있으면 단독 먼저」 — 공유가 돌면 {0:0.00}초에 그만 · 문 놓음 · 다 비면 곧바로 잡음" -f $q1s)
    Exit-E2eSlots $q2
    # ⑪ 프로세스가 죽으면 OS 가 푼다 — 다른 PowerShell 이 큰 잠금을 쓰기로 쥔 채 죽는다
    $mark = Join-Path $tmp "holder.ready"
    $holdArgs = '-NoProfile -NonInteractive -Command "$f = [System.IO.File]::Open(''' + $pb + ''', ''OpenOrCreate'', ''ReadWrite'', ''Read''); Set-Content -LiteralPath ''' + $mark + ''' -Value held; Start-Sleep -Seconds 60"'
    $hpsi = [System.Diagnostics.ProcessStartInfo]::new((Get-Process -Id $PID).Path, $holdArgs)
    $hpsi.UseShellExecute = $false
    $hpsi.CreateNoWindow = $true
    $hp = [System.Diagnostics.Process]::Start($hpsi)
    $tw = [System.Diagnostics.Stopwatch]::StartNew()
    while (-not (Test-Path -LiteralPath $mark) -and -not $hp.HasExited -and $tw.Elapsed.TotalSeconds -lt 30) { Start-Sleep -Milliseconds 200 }
    $k1 = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 1
    Stop-Tree $hp
    [void]$hp.WaitForExit(10000)
    $k2 = Enter-E2eSlots -Dir $sd -N 2 -WaitSec 5
    Confirm-That ((Test-Path -LiteralPath $mark) -and $null -eq $k1 -and $k2) ("다른 프로세스(pid {0})가 큰 잠금을 쥔 동안 못 잡음 · 쥔 채 죽으면 OS 가 풀어 잡음" -f $hp.Id)
    Exit-E2eSlots $k1
    Exit-E2eSlots $k2
    # ⑫ 나누기 — [Scenario, 창 모드, N, 기대 공유, 기대 --e2e-skip, 기대 단독]
    $soloT = @("s_one", "s_two")
    $planCases = @(
        @("all", $false, 2, "all", "s_one,s_two", "s_one,s_two"),
        @("", $false, 2, "all", "s_one,s_two", "s_one,s_two"),
        @("portal_roundtrip", $false, 2, "portal_roundtrip", "", ""),
        @("s_two", $false, 2, "", "", "s_two"),
        @("a, s_two ,b", $false, 3, "a,b", "", "s_two"),
        @("all", $true, 2, "", "", "all"),
        @("portal_roundtrip", $true, 2, "", "", "portal_roundtrip"),
        @("all", $false, 1, "", "", "all"))
    $planWrong = @()
    foreach ($pc in $planCases) {
        $pl = Get-E2ePlan $pc[0] $soloT $pc[1] $pc[2]
        $got = @(("" + $pl.Shared), (@($pl.Skip) -join ","), ("" + $pl.Solo))
        if ($got[0] -ne $pc[3] -or $got[1] -ne $pc[4] -or $got[2] -ne $pc[5]) { $planWrong += ("「{0}」 창 {1} N {2} → {3} / {4} / {5}" -f $pc[0], $pc[1], $pc[2], $got[0], $got[1], $got[2]) }
    }
    Confirm-That ($planWrong.Count -eq 0) ("나누기 {0}/{1} — all = 공유(all − 단독 묶음) + 단독 묶음 · 이름 목록은 두 쪽으로 · 창 모드·칸 1개는 통째로 단독{2}" -f ($planCases.Count - $planWrong.Count), $planCases.Count, $(if ($planWrong.Count) { " — 틀림: " + ($planWrong -join " · ") } else { "" }))
    # ⑬ 단독 묶음 이름이 러너 SCENARIOS 에 다 있다 — 이름이 바뀌면 여기서 먼저(godot 없이 글자로)
    $runnerSrc = [System.IO.File]::ReadAllText((Join-Path $root "tests\e2e\e2e_runner.gd"), [System.Text.Encoding]::UTF8)
    $soloMissing = @($E2E_SOLO | Where-Object { $runnerSrc -notmatch ('"' + [regex]::Escape($_) + '":\s*"res://') })
    Confirm-That ($E2E_SOLO.Count -gt 0 -and $soloMissing.Count -eq 0) ("단독 묶음 {0}개가 러너 SCENARIOS 에 다 있다{1}" -f $E2E_SOLO.Count, $(if ($soloMissing.Count) { " — 없음: " + ($soloMissing -join ", ") } else { " (" + ($E2E_SOLO -join ", ") + ")" }))

    # -Export 스위치 (#376) — 진짜 내보내기 없이. 가짜 도구 = 임시 폴더의 작은 .py (export_check.py 의 끝 줄·종료 코드만 흉내),
    # 부르는 함수(Get-Layers · Invoke-ExportCheck)는 본 실행과 같은 것. 가짜 PCK = 몇 바이트짜리 game.pck.
    Write-Host "-- -Export 스위치 (#376) — 가짜 도구로 --" -ForegroundColor Cyan
    $want = [ordered]@{ "(없음)" = "단위·e2e"; "-Export" = "내보내기"; "-Export -Unit" = "단위·내보내기"; "-Export -E2e" = "e2e·내보내기"; "-Unit" = "단위" }
    $sw = @{ "(없음)" = @($false, $false, $false); "-Export" = @($false, $false, $true); "-Export -Unit" = @($true, $false, $true); "-Export -E2e" = @($false, $true, $true); "-Unit" = @($true, $false, $false) }
    $seen = @(); $same = $true
    foreach ($k in $want.Keys) {
        $got = Format-Layers (Get-Layers $sw[$k][0] $sw[$k][1] $sw[$k][2])
        if ($got -ne $want[$k]) { $same = $false }
        $seen += "$k = $got"
    }
    Confirm-That $same ("스위치 → 층: " + ($seen -join " · ") + " (기본에 내보내기 없음)")

    $xo = Join-Path $tmp "export_out"
    New-Item -ItemType Directory -Force $xo | Out-Null
    $xpck = Join-Path $xo "game.pck"
    $stub = @{}
    foreach ($s in @(
            @("pass", @('print("EXPORT_CHECK files=1 lines=1 changed=0 missing=0 extra=0 PASS")')),
            @("fail", @('import sys', 'print("EXPORT_CHECK files=1 lines=1 changed=1 missing=0 extra=0 FAIL")', 'sys.exit(1)')),
            @("nosum", @('print("stub: no verdict line")')),
            @("liar", @('import sys', 'print("EXPORT_CHECK files=1 lines=1 changed=0 missing=0 extra=0 PASS")', 'sys.exit(1)')),
            @("hang", @('import time', 'print("EXPORT_HANG", flush=True)', 'time.sleep(600)')))) {
        $stub[$s[0]] = Join-Path $tmp ("export_stub_" + $s[0] + ".py")
        Set-Content -LiteralPath $stub[$s[0]] -Value $s[1] -Encoding ASCII
    }

    # 대조군 — 끝 줄 PASS + 종료 0 → PASS, FAIL 안 늚. 도구가 안 지운 PCK 는 test.ps1 이 지운다
    Set-Content -LiteralPath $xpck -Value "fake pck" -Encoding ASCII
    $f0 = $fail
    $r = Invoke-ExportCheck -Tool $stub["pass"] -OutDir $xo -Limit 60
    Confirm-That ((-not $r.TimedOut) -and $r.Code -eq 0 -and $fail -eq $f0 -and -not (Test-Path -LiteralPath $xpck)) ("대조군: 끝 줄 PASS + 종료 코드 0 → PASS · FAIL 안 늚 · 남은 PCK 지움 ({0:0.0}초)" -f $r.Sec)
    $f0 = $fail
    $r = Invoke-ExportCheck -Tool $stub["fail"] -OutDir $xo -Limit 60
    Confirm-That ($r.Code -eq 1 -and $fail -eq $f0 + 1) "도구 FAIL(끝 줄 FAIL · 종료 코드 1) → FAIL로 센다(→ 종료 코드 1)"
    $f0 = $fail
    [void](Invoke-ExportCheck -Tool $stub["nosum"] -OutDir $xo -Limit 60)
    $n1 = $fail - $f0
    $f0 = $fail
    [void](Invoke-ExportCheck -Tool $stub["liar"] -OutDir $xo -Limit 60)
    $n2 = $fail - $f0
    Confirm-That ($n1 -eq 1 -and $n2 -eq 1) "판정 없는 초록 금지 — 끝 줄 없음(종료 코드 0) → FAIL · 끝 줄 PASS인데 종료 코드 1 → FAIL"
    # 멈춤 — 제한에서 ⏱ FAIL · 자식 정리 · PCK 지움 (자식째 죽이면 도구의 정리가 못 도는 길)
    Set-Content -LiteralPath $xpck -Value "fake pck" -Encoding ASCII
    $f0 = $fail
    $r = Invoke-ExportCheck -Tool $stub["hang"] -OutDir $xo -Limit 4
    # 실제 걸린 초(#436)가 붙어 뒤가 달라지니 접두사만 본다.
    Confirm-That ($r.TimedOut -and $fail -eq $f0 + 1 -and $r.Note.StartsWith("⏱ export_check.py 제한 시간 4초 넘음 — 멈춤") -and (-not (Test-Alive $r.Pid)) -and -not (Test-Path -LiteralPath $xpck)) ("멈추면 ⏱ FAIL · 자식 정리 · PCK 지움 ({0:0.0}초, 제한 4초)" -f $r.Sec)

    # 진짜 명령줄 — 자식 PowerShell 로 「test.ps1 -Export」 (환경 변수로 가짜 도구·임시 자리 → 진짜 PCK 자리는 안 건드린다).
    # 자식 출력은 숨은 새 콘솔의 코드페이지로 나와 한글이 깨져 읽힐 수 있다 → ASCII 표식만 본다.
    $psExe = (Get-Process -Id $PID).Path
    $psArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $root "tools\test.ps1"), "-Export")
    $c0 = $null; $c1 = $null
    $env:JOSEON_EXPORT_OUT = $xo
    try {
        Set-Content -LiteralPath $xpck -Value "fake pck" -Encoding ASCII
        $env:JOSEON_EXPORT_TOOL = $stub["pass"]
        $c0 = Invoke-Step -Label "test.ps1 -Export (가짜 PASS)" -Exe $psExe -ArgList $psArgs -Limit 120
        $env:JOSEON_EXPORT_TOOL = $stub["fail"]
        $c1 = Invoke-Step -Label "test.ps1 -Export (가짜 FAIL)" -Exe $psExe -ArgList $psArgs -Limit 120
    }
    finally { Remove-Item Env:JOSEON_EXPORT_TOOL, Env:JOSEON_EXPORT_OUT -ErrorAction SilentlyContinue }
    $onlyExport = { param($o) ($o -match "EXPORT_CHECK files=1 ") -and ($o -notmatch "motion_audit|E2E_SELFTEST|fails=0 PASS") }
    Confirm-That ((-not $c0.TimedOut) -and $c0.Code -eq 0 -and (& $onlyExport $c0.Out) -and -not (Test-Path -LiteralPath $xpck)) ("진짜 명령줄 test.ps1 -Export · 가짜 PASS → 종료 코드 {0} · 내보내기 층만(단위·e2e 표식 없음) · PCK 지움 ({1:0.0}초)" -f $c0.Code, $c0.Sec)
    Confirm-That ((-not $c1.TimedOut) -and $c1.Code -eq 1 -and (& $onlyExport $c1.Out)) ("진짜 명령줄 test.ps1 -Export · 가짜 FAIL → 종료 코드 {0} (도구 FAIL 이 test.ps1 종료 코드로) ({1:0.0}초)" -f $c1.Code, $c1.Sec)

    # 단위 층 오류 줄 (#401, 종료 코드는 #368) — 합격 줄만 보던 단위 층이 시험 안 오류 줄·종료 코드로 FAIL 하는가. ① 글자 규칙
    # (godot 없이 — 줄 모양마다 센다·안 센다·거른다·자리) ② 진짜 godot — 임시 폴더의 가짜 단위 시험을 본 실행과 같은 함수
    # (Invoke-UnitScript)로. -s 대본은 자리 밖 경로도 돈다(작업 폴더 = 자리라 오토로드도 뜬다). 가짜 대본은 ASCII·스페이스
    # 들여쓰기. 허용 목록 = 진짜 목록 + 이 검사 전용 한 줄(그 시험에만).
    Write-Host "-- 단위 층 오류 줄·종료 코드 (#401·#368) — 가짜 단위 시험으로 --" -ForegroundColor Cyan
    $selfIgnore = @($UNIT_ERROR_IGNORE) + @([pscustomobject]@{ Text = "UNIT_SELFTEST_SCOPED"; Test = "unit_scoped.gd"; Why = "자기검사 전용 — 그 시험에만" })
    $esc = [string][char]27
    $cases = @(
        # [보기 줄, 시험 이름, 셀 줄, 거를 줄, 뜻]
        @("SCRIPT ERROR: Cannot call method 'call' on a null value.", "t.gd", 1, 0, "SCRIPT ERROR"),
        @('SCRIPT ERROR: Parse Error: Unexpected "Indent" in class body.', "t.gd", 1, 0, "SCRIPT ERROR: Parse Error = 한 줄"),
        @("Parse Error: Expected end of statement", "t.gd", 1, 0, "Parse Error"),
        @("Compile Error: Identifier not found: gone", "t.gd", 1, 0, "Compile Error"),
        @("Compilation failed: a dependency did not build", "t.gd", 1, 0, "Compilation failed (#368)"),
        @("SHADER ERROR: Invalid arguments to operator '+'", "t.gd", 1, 0, "SHADER ERROR"),
        @("ERROR: Error calling from signal 'probe' to callable", "t.gd", 1, 0, "줄 머리 ERROR:"),
        @("USER ERROR: probe", "t.gd", 1, 0, "USER ERROR"),
        @(($esc + "[1;31mERROR:" + $esc + "[0m colored"), "t.gd", 1, 0, "색 글자 ERROR:"),
        @('WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).', "t.gd", 0, 0, "WARNING 안 셈"),
        @("   at: push_error (core/variant/variant_utility.cpp:1023)", "t.gd", 0, 0, "at: 줄 안 셈"),
        @("  - probe line quoting ERROR: in the middle", "t.gd", 0, 0, "문장 속 ERROR: 안 셈"),
        @("error: lower case", "t.gd", 0, 0, "소문자 error: 안 셈"),
        @("ERROR: 1 resources still in use at exit (run with --verbose for details).", "t.gd", 0, 1, "종료 보고 = 허용 목록(전부)"),
        @("ERROR: UNIT_SELFTEST_SCOPED probe", "unit_scoped.gd", 0, 1, "그 시험의 허용 줄"),
        @("ERROR: UNIT_SELFTEST_SCOPED probe", "unit_other.gd", 1, 0, "딴 시험엔 안 거름"))
    # 자리 — push_error 는 엔진 소스 at: 대신 역추적 첫 칸 · 런타임 오류는 at: · 파스 오류는 at:(망가진 파일) · 사이에 딴 줄(두 줄기 섞임)
    $wcases = @(
        @(@("ERROR: boom", "   at: push_error (core/variant/variant_utility.cpp:1023)", "   GDScript backtrace (most recent call first):", "PROBE_TEST checks=1 fails=0 PASS", "       [0] from_layout (res://world/dungeon_gen.gd:172)"), "dungeon_gen.gd:172"),
        @(@("SCRIPT ERROR: Cannot call method 'call' on a null value.", "   at: _cut_short (C:/tmp/unit_cut.gd:11)", "       [0] _cut_short (C:/tmp/unit_cut.gd:11)"), "unit_cut.gd:11"),
        @(@('SCRIPT ERROR: Parse Error: Unexpected "Indent" in class body.', "   at: GDScript::reload (C:/tmp/unit_broken.gd:3)", "       [0] _init (C:/tmp/unit_parse.gd:4)"), "unit_broken.gd:3"))
    $wrong = @()
    foreach ($c in $cases) {
        $x = Find-ErrorLines $c[0] $c[1] $selfIgnore
        if (@($x.Hit).Count -ne $c[2] -or @($x.Skip).Count -ne $c[3]) { $wrong += $c[4] }
    }
    foreach ($w in $wcases) {
        $x = Find-ErrorLines ($w[0] -join "`n") "t.gd" $selfIgnore
        $got = if (@($x.Hit).Count -gt 0) { $x.Hit[0].Where } else { "(없음)" }
        if (@($x.Hit).Count -ne 1 -or $got -ne $w[1]) { $wrong += ("자리 " + $w[1] + " ≠ " + $got) }
    }
    $nc = $cases.Count + $wcases.Count
    Confirm-That ($wrong.Count -eq 0) ("글자 규칙 {0}/{1} — 센다: SCRIPT ERROR·Parse Error·Compile Error·Compilation failed(#368)·SHADER ERROR·줄 머리 ERROR:·USER ERROR·색 글자 / 안 센다: WARNING·at: 줄·문장 속·소문자 / 거른다: 허용 목록(전부·그 시험만) / 자리 = 역추적·at:{2}" -f ($nc - $wrong.Count), $nc, $(if ($wrong.Count) { " — 틀림: " + ($wrong -join " · ") } else { "" }))

    $ux = Join-Path $tmp "unit"
    New-Item -ItemType Directory -Force $ux | Out-Null
    $fake = [ordered]@{
        # 대조군 — 오류 없이 합격 줄
        "unit_clean.gd"  = @('extends SceneTree', 'func _init() -> void:', '    print("UNIT_FAKE_TEST checks=1 fails=0 PASS")', '    quit(0)')
        # #377 모양 — 절(함수) 하나가 SCRIPT ERROR 로 끊기고 _init 은 이어서 합격 줄을 찍는다(종료 코드 0)
        "unit_cut.gd"    = @('extends SceneTree', 'var checks := 0', 'func _init() -> void:', '    _cut_short()', '    checks += 1', '    print("UNIT_FAKE_TEST checks=%d fails=0 PASS" % checks)', '    quit(0)', 'func _cut_short() -> void:', '    checks += 1', '    var gone: Object = null', '    gone.call("nothing")', '    checks += 100')
        # 망가진 대본(아래 unit_broken.gd)을 읽고도 합격 줄 — SCRIPT ERROR: Parse Error + ERROR: Failed to load script
        "unit_parse.gd"  = @('extends SceneTree', 'func _init() -> void:', '    var dir := (get_script() as Script).resource_path.get_base_dir()', '    var broken = load(dir.path_join("unit_broken.gd"))', '    print("UNIT_FAKE_TEST checks=1 fails=0 PASS loaded=%s" % [broken != null])', '    quit(0)')
        "unit_broken.gd" = @('extends RefCounted', 'func broken() -> void', '    var x = = 3')
        # 종료 보고만 — 경로 붙은 자원을 쥔 노드를 안 지운다 → quit 뒤 「ERROR: 1 resources still in use at exit」(허용 목록) + ObjectDB WARNING
        "unit_leak.gd"   = @('extends SceneTree', 'func _init() -> void:', '    var dir := (get_script() as Script).resource_path.get_base_dir()', '    var keep := Node.new()', '    keep.set_meta("res", load(dir.path_join("unit_leak.tres")))', '    print("UNIT_FAKE_TEST checks=1 fails=0 PASS")', '    quit(0)')
        # 이 검사 전용 허용 줄 — 그 시험 이름이면 거르고 딴 이름이면 센다
        "unit_scoped.gd" = @('extends SceneTree', 'func _init() -> void:', '    push_error("UNIT_SELFTEST_SCOPED probe")', '    print("UNIT_FAKE_TEST checks=1 fails=0 PASS")', '    quit(0)')
        # 합격 줄 없음 + 오류 — FAIL 은 한 번만
        "unit_nopass.gd" = @('extends SceneTree', 'func _init() -> void:', '    push_error("UNIT_FAKE failing check")', '    print("UNIT_FAKE_TEST checks=1 fails=1 FAIL")', '    quit(1)')
        # 오류 줄은 0개, 표식은 있는데 종료 코드만 어긋난다 (#368 — 실측 #156 모양: 판정 줄 뒤에서 조용히 죽어도 표식만 보면 PASS 였다)
        "unit_pass_bad_exit.gd" = @('extends SceneTree', 'func _init() -> void:', '    print("UNIT_FAKE_TEST checks=1 fails=0 PASS")', '    quit(7)')
        # SCRIPT ERROR·줄 머리 ERROR: 없이 맨 print 로만 「Compilation failed」 — #368 이 $ERROR_LINE 에 더하기 전엔 오류 줄로도 안 걸렸다
        "unit_bare_compile_fail.gd" = @('extends SceneTree', 'func _init() -> void:', '    print("Compilation failed: a dependency did not build")', '    print("UNIT_FAKE_TEST checks=1 fails=0 PASS")', '    quit(0)')
    }
    foreach ($n in $fake.Keys) { Set-Content -LiteralPath (Join-Path $ux $n) -Value $fake[$n] -Encoding ASCII }
    Set-Content -LiteralPath (Join-Path $ux "unit_leak.tres") -Value @('[gd_resource type="Resource" format=3]', '', '[resource]') -Encoding ASCII

    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_clean.gd")
    $k = $script:lastCheck
    Confirm-That ($k.Verdict -eq "PASS" -and $fail -eq $f0 -and @($k.Hit).Count -eq 0 -and @($k.Skip).Count -eq 0) ("대조군: 오류 없는 가짜 시험 → PASS · FAIL 안 늚 ({0:0.0}초)" -f $k.Sec)
    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_cut.gd")
    $k = $script:lastCheck
    $cutAt = "unit_cut.gd:" + ([array]::IndexOf($fake["unit_cut.gd"], '    gone.call("nothing")') + 1)
    Confirm-That ($k.PassText -and $k.Verdict -eq "FAIL" -and $fail -eq $f0 + 1 -and $k.First -cmatch "^SCRIPT ERROR" -and $k.First.EndsWith("(" + $cutAt + ")")) ("#377 모양 — 절이 SCRIPT ERROR 로 끊겨도 합격 줄이 찍힌다 → FAIL 한 번 · 첫 오류 = 「" + $k.First + "」")
    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_parse.gd")
    $k = $script:lastCheck
    Confirm-That ($k.PassText -and $k.Verdict -eq "FAIL" -and $fail -eq $f0 + 1 -and $k.First -cmatch "Parse Error" -and $k.First -match "\(unit_broken\.gd:\d+\)$") ("망가진 대본을 읽고 합격 줄 → FAIL 한 번 · 오류 줄 {0} · 첫 오류 = 「{1}」" -f @($k.Hit).Count, $k.First)
    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_leak.gd")
    $k = $script:lastCheck
    $exitSkip = @($k.Skip | Where-Object { $_.Line -match "resources still in use at exit" }).Count
    Confirm-That ($k.Verdict -eq "PASS" -and $fail -eq $f0 -and @($k.Hit).Count -eq 0 -and $exitSkip -ge 1) ("허용 목록 줄만(판정 줄 뒤 종료 보고 「resources still in use at exit」 · ObjectDB 는 WARNING) → PASS · 거른 줄 {0}" -f @($k.Skip).Count)
    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_scoped.gd") -Ignore $selfIgnore
    $k1 = $script:lastCheck
    Invoke-UnitScript (Join-Path $ux "unit_scoped.gd") -Name "unit_other.gd" -Ignore $selfIgnore
    $k2 = $script:lastCheck
    Confirm-That ($k1.Verdict -eq "PASS" -and @($k1.Skip).Count -eq 1 -and $k2.Verdict -eq "FAIL" -and @($k2.Hit).Count -eq 1 -and $fail -eq $f0 + 1) "그 시험에만 거르는 허용 줄 — 제 이름이면 PASS(거름 1) · 딴 이름이면 같은 줄로 FAIL"
    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_nopass.gd")
    $k = $script:lastCheck
    Confirm-That ((-not $k.PassText) -and $k.Verdict -eq "FAIL" -and $fail -eq $f0 + 1 -and @($k.Hit).Count -eq 1) "합격 줄 없음 + 오류 줄 → FAIL 은 한 번만(겹쳐 세지 않음)"

    # #368 — 기본 실행 목록(tests\test_*.gd)엔 안 들어가는 새 fixture 둘. 이 자기검사에서만 FAIL로 잡히는지 본다
    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_pass_bad_exit.gd")
    $k = $script:lastCheck
    Confirm-That ($k.PassText -and $k.Verdict -eq "FAIL" -and $fail -eq $f0 + 1 -and @($k.Hit).Count -eq 0 -and $k.Code -eq 7) ("#368 — 오류 줄 0개 + 합격 줄만 있어도 종료 코드 {0} ≠ 0 이면 FAIL 한 번(고치기 전엔 PASS 였다)" -f $k.Code)
    $f0 = $fail
    Invoke-UnitScript (Join-Path $ux "unit_bare_compile_fail.gd")
    $k = $script:lastCheck
    Confirm-That ($k.PassText -and $k.Verdict -eq "FAIL" -and $fail -eq $f0 + 1 -and @($k.Hit).Count -eq 1 -and $k.First -cmatch "^Compilation failed" -and $k.Code -eq 0) ("#368 — SCRIPT ERROR·줄 머리 ERROR: 없이 「Compilation failed」만 있어도 FAIL 한 번 · 첫 오류 = 「" + $k.First + "」")

    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    # 위의 FAIL 은 일부러 낸 것 — 이 실행의 판정은 확인 줄로 한다
    if ($script:bad -gt 0) { Write-Host ("TIMEOUT_SELFTEST FAIL (확인 {0}/{1})" -f $script:ok, ($script:ok + $script:bad)) -ForegroundColor Red; exit 1 }
    Write-Host ("TIMEOUT_SELFTEST PASS (확인 {0}/{1})" -f $script:ok, $script:ok) -ForegroundColor Green
    exit 0
}

$layers = Get-Layers ([bool]$Unit) ([bool]$E2e) ([bool]$Export)

Push-Location $root
try {
    if ($layers.Unit) {
        Write-Host "== 단위 테스트 ==" -ForegroundColor Cyan
        # 합격 = 「fails=0 PASS」 + 오류 줄 없음 (#401 — Invoke-UnitScript). 아래 godot 셀프테스트 셋도 같은 판정(-ScanErrors)
        Get-ChildItem "tests\test_*.gd" | ForEach-Object { Invoke-UnitScript $_.FullName }
        # 설정 영속화: 쓰고 종료한 뒤 별도 Godot 프로세스로 부팅 적용을 검증 (#156).
        foreach ($phase in @("write", "read")) {
            Invoke-Check "settings restart $phase" $godot @("--headless", "-s", "tests/settings_restart_probe.gd", "--", "--settings-path=user://settings_restart_e2e.cfg", "--settings-probe=$phase") $LIMIT_STEP "SETTINGS_RESTART_TEST.*fails=0 PASS" "SETTINGS_RESTART_TEST" $UTF8 -ScanErrors
        }
        # 동작 실측 눈금 셀프테스트 (godot만 — 합성 동작의 답을 손으로 셀 수 있게 만들어 계산식을 검산) — combat_anim_reference §7, #139
        Invoke-Check "motion_audit.gd --selftest" $godot @("--headless", "-s", "tools/motion_audit.gd", "--", "--selftest") $LIMIT_STEP "MOTION_AUDIT_TEST checks=\d+ fails=0 PASS" "MOTION_AUDIT_TEST" $UTF8 -ScanErrors
        # 외형 셈법 셀프테스트 (godot만 — 합성 표면으로 텍스처×틴트·단색·면적 가중·밴드 판정을 손셈과 대조) — asset_pipeline_consistency §7, #121
        # 셈법이 틀리면 FAIL이다. 아래 외형 표는 출력만 하므로, 표를 믿을 근거는 이 검산이다.
        Invoke-Check "look_audit.gd --selftest" $godot @("--headless", "-s", "tools/look_audit.gd", "--", "--selftest") $LIMIT_STEP "LOOK_AUDIT_TEST checks=\d+ fails=0 PASS" "LOOK_AUDIT_TEST" $UTF8 -ScanErrors
        # 자락 눈금 셀프테스트 (godot만 — 반경·선분 거리·상위평균·떨림 계산식 + 합성 뼈대 스키닝) — art_3d_pipeline §12.3, #143
        Invoke-Check "robe_probe.gd --selftest" $godot @("--headless", "-s", "tools/robe_probe.gd", "--", "--selftest") $LIMIT_STEP "ROBE_PROBE_TEST checks=\d+ fails=0 PASS" "ROBE_PROBE_TEST" $UTF8 -ScanErrors
        # 밀도 도구 셀프테스트 (godot만 — 길 길이·어그로 안 몸·분당·밴드·손 지도 탐색 경로를 손셈과 대조) — monsters_v2 §5.5 · §9.3 M8, #294
        Invoke-Check "dungeon_stats.gd --selftest" $godot @("--headless", "-s", "tools/dungeon_stats.gd", "--", "--selftest") $LIMIT_STEP "DUNGEON_STATS_TEST checks=\d+ fails=0 PASS" "DUNGEON_STATS_TEST" $UTF8 -ScanErrors
        # 이펙트 시트 도구 셀프테스트 (python+PIL 있을 때만, 임시 폴더) — design/vfx.md §3
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "vfx_sheet.py --selftest" python @("tools/vfx_sheet.py", "--selftest") $LIMIT_STEP "VFX_SHEET_TEST fails=0 PASS|VFX_SHEET_TEST SKIP" "VFX_SHEET_TEST"
        }
        # 오디오 반입 도구 셀프테스트 (python+ffmpeg 있을 때만, 임시 폴더) — design/audio.md §4.2
        if ((Get-Command python -ErrorAction SilentlyContinue) -and (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
            Invoke-Check "audio_intake.py --selftest" python @("tools/audio_intake.py", "--selftest", "--out", (Join-Path $env:TEMP "audio_intake_selftest")) $LIMIT_STEP "AUDIO_INTAKE_TEST fails=0 PASS" "AUDIO_INTAKE_TEST"
        }
        # 명령판 도구 셀프테스트 (python만, 네트워크 0 — 헤더 파싱·정렬·보류 큐·한도 중 동작) — AGENTS §8-11, #89
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "board.py --selftest" python @("tools/board.py", "--selftest") $LIMIT_STEP "BOARD_TEST fails=0 PASS" "BOARD_TEST"
        }
        # 효과음 생성 도구 셀프테스트 (python만, 네트워크 0 — 번호·wav 포장·.env 파싱) — design/audio.md §4.5
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "sfx_gen.py --selftest" python @("tools/sfx_gen.py", "--selftest") $LIMIT_STEP "SFX_GEN_TEST fails=0 PASS" "SFX_GEN_TEST"
        }
        # 작업 트리 도구 셀프테스트 (python+git, 임시 저장소 — 착륙·union 병합·줄 끝 되돌림·겹침 막기·정리) — D-078, design/parallel_sessions.md
        # 제한 = $LIMIT_WT_SELFTEST(다른 셀프테스트보다 훨씬 느린 git 작업이라 $LIMIT_STEP 따로 안 쓴다, #436)
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "wt.py --selftest" python @("tools/wt.py", "--selftest") $LIMIT_WT_SELFTEST "WT_TEST checks=\d+ fails=0 PASS" "WT_TEST"
        }
        # 문서 예산 셀프테스트 (python만 — 자동 import 세 문서 AGENTS·DECISIONS·STATE ≤ 예산 · STATE 줄 길이 · 사양서 60KB 넘으면 WARN) — design/cleanup_plan_2026-09-24.md §1, #412
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "doc_budget.py --selftest" python @("tools/doc_budget.py", "--selftest") $LIMIT_STEP "DOC_BUDGET_TEST checks=\d+ fails=0 PASS" "DOC_BUDGET_TEST" $UTF8
        }
        # 인물 알베도·재질 도구 셀프테스트 (python+numpy+PIL, 합성 메시 — GLB 이미지 끼우기·비금속·몸 위 빛 빼기·이음새 없음·다시 돌려도 그대로) — art_3d_pipeline §23, #119
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "albedo_ops.py --selftest" python @("tools/albedo_ops.py", "--selftest") $LIMIT_STEP "ALBEDO_OPS_TEST checks=\d+ fails=0 PASS" "ALBEDO_OPS_TEST"
        }
        # Comfy 인물 길 도구 셀프테스트 (python+numpy, 합성 뼈대 GLB · godot 없이 — 정면 +X·−X·−Z·+Z → yaw · 발끝 없으면 허벅지 · 뿌리 관절 굽기(부모 회전 감싸기·matrix 칸)·스킨 정점 같이 돎·동작 뺌 · 리타깃·검수 출력 읽기) — comfy_3d_pipeline §2, #532
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "comfy_char.py --selftest" python @("tools/comfy_char.py", "--selftest") $LIMIT_STEP "COMFY_CHAR_TEST checks=\d+ fails=0 PASS" "COMFY_CHAR_TEST" $UTF8
        }
        # 애니 v2 시간 셈 셀프테스트 (python만, Blender 없이 — 자르기·다시 재기·W·S·F·H·R 경계·이음새·제자리·칼 궤적 시간표·두 마디 IK·칼끝 바닥 막이·발 디딤·GLB 채널 확인·들어 있는 계획) — anim_v2 §6, #222
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "anim_retime.py --selftest" python @("tools/blender/anim_retime.py", "--selftest") $LIMIT_STEP "ANIM_RETIME_TEST checks=\d+ fails=0 PASS" "ANIM_RETIME_TEST"
        }
        # GLB 애니 값 고치기 셀프테스트 (python+numpy, 합성 뼈대 GLB — 손가락 쥐기·무기 소켓·입 가리기 IK·클립 갈아 끼우기·BIN 다시 싸기) — anim_v2 §8.3, #225
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "glb_pose.py --selftest" python @("tools/glb_pose.py", "--selftest") $LIMIT_STEP "GLB_POSE_TEST checks=\d+ fails=0 PASS" "GLB_POSE_TEST"
        }
        # 네발 절차 리그 v2 클립 셀프테스트 (python+numpy, 합성 네발 GLB — 쉰 자세 왕복·발 고정 지면 속도·닿는 때·루프 이음새·갤러리 흉내(미끄러짐·물기·맞기·대기)·몸 크기 배율·덮치기·죽기·keep) — monster_motion_v2 §4, #501
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "quad_gait.py --selftest" python @("tools/quad_gait.py", "--selftest") $LIMIT_STEP "QUAD_GAIT_TEST checks=\d+ fails=0 PASS" "QUAD_GAIT_TEST" $UTF8
        }
        # 내보낸 빌드 = 원본 대조 셀프테스트 (python만, 내보내기 없이 — 덤프 가르기·다름·빠짐·남음·doho 길이 줄) — testing.md #349
        # 진짜 대조(PCK 내보내기 한 번 ≈ 12초·PCK ≈ 380MB)는 여기서 안 돈다: .\tools\test.ps1 -Export (#376, 출시 전 필수·데이터 칸 형을 바꾼 뒤)
        # 도구는 stdout 을 UTF-8 로 바꿔 쓴다 → UTF-8 로 읽는다 (콘솔 인코딩으로 읽으면 cp949 콘솔에서 FAIL 출력의 한글이 깨진다)
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "export_check.py --selftest" python @("tools/export_check.py", "--selftest") $LIMIT_STEP "EXPORT_CHECK_TEST checks=\d+ fails=0 PASS" "EXPORT_CHECK_TEST" $UTF8
        }
        # 빌드 도구 셀프테스트 (python+git, 임시 저장소 — 태그에서 다음 버전 셈·이름·BUILDS.md 줄 모양, 진짜 내보내기 없음) — D-092, design/builds.md §4
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Invoke-Check "build.py --selftest" python @("tools/build.py", "--selftest") $LIMIT_STEP "BUILD_TEST checks=\d+ fails=0 PASS" "BUILD_TEST" $UTF8
        }
        # 외형 표 (#121, asset_pipeline_consistency §4·§7) — 14가족 알베도 밝기·채도·텍셀 밀도.
        # **출력만** 한다: 밴드 밖이 있어도 실패로 세지 않는다(인물 색 #119·밀도 #120이 모이는 중, PD 판정 전). 주간 리뷰에서 추세를 본다.
        # 단 제한 시간을 넘으면(멈춤) FAIL이다 — 밴드 밖은 판정 전 값이지만 멈춤은 도구 고장이다 (#181).
        Write-Host "== 외형 표 (look_audit — 출력만, 실패로 세지 않음) ==" -ForegroundColor Cyan
        $r = Invoke-Step -Label "look_audit.gd (외형 표)" -Exe $godot -ArgList @("--headless", "-s", "tools/look_audit.gd") -Limit $LIMIT_STEP -Encoding $UTF8
        if (-not $r.TimedOut) {
            $out = $r.Out
            $rows = @($out -split "`r?`n" | Where-Object { ($_ -split "`t").Count -ge 8 } | ForEach-Object { , ($_ -split "`t") })
            if ($rows.Count -gt 0) {
                $wid = @(0) * 8
                foreach ($row in $rows) { for ($c = 0; $c -lt 8; $c++) { $wid[$c] = [math]::Max($wid[$c], (Get-CellWidth $row[$c])) } }
                foreach ($row in $rows) {
                    $cells = for ($c = 0; $c -lt 8; $c++) { $row[$c] + (" " * ($wid[$c] - (Get-CellWidth $row[$c]))) }
                    Write-Host ("    " + ($cells -join "  ").TrimEnd()) -ForegroundColor $(if ($row[7] -match "^X") { "DarkYellow" } else { "Gray" })
                }
            }
            $sum = $out -split "`r?`n" | Where-Object { $_ -match "^LOOK_AUDIT " } | Select-Object -First 1
            if ($sum) { Write-Host ("    " + $sum.Trim() + "  (출력만)" + (Format-Sec $r)) -ForegroundColor Gray }
            else { Write-Host "    ⚠ look_audit 표를 못 냈다 — 출력만이라 실패로 세지 않는다(셈법은 위 셀프테스트가 본다)" -ForegroundColor Yellow }
        }
    }
    # 자리 (D-078): 작업 트리면 user:// 가 override.cfg 로 갈라져 있어야 한다 — 없으면 세이브·e2e 스크린샷이 본진과 섞인다
    $common = (& git -C $root rev-parse --path-format=absolute --git-common-dir 2>$null)
    $isWt = $common -and ([System.IO.Path]::GetFullPath((Split-Path $common -Parent)) -ne [System.IO.Path]::GetFullPath($root))
    $userDir = Join-Path $env:APPDATA "Godot\app_userdata\Joseon Hunters"
    $ovr = Join-Path $root "override.cfg"
    if (Test-Path $ovr) {
        $m = Select-String -Path $ovr -Pattern 'custom_user_dir_name="([^"]+)"' | Select-Object -First 1
        if ($m) { $userDir = Join-Path $env:APPDATA ($m.Matches[0].Groups[1].Value -replace "/", "\") }
    } elseif ($isWt) {
        Write-Host "  ⚠ 작업 트리인데 override.cfg 없음 — user:// 를 본진과 같이 쓴다 → python tools/wt.py setup" -ForegroundColor Yellow
    }
    if ($layers.E2e) {
        # 자리 간 e2e 칸 (#553, parallel_sessions §5) — 공유 판(빈 칸 하나)·단독 판(다른 자리 e2e 없이)으로 나눈다(Get-E2ePlan). 다
        # 비어 있으면 단독 먼저(기다림 없음), 아니면 공유 먼저 → 단독(돌던 공유가 끝나기를 기다린다). 러너 자기검사는 첫 판 안에서.
        $nSlots = Get-E2eSlotCount $Slots
        $plan = Get-E2ePlan $Scenario $E2E_SOLO ([bool]$Windowed) $nSlots
        $why = if ($Windowed) { "(창 모드)" } elseif ($nSlots -le 1) { "(칸 1개)" } else { "(시간 민감 묶음)" }
        $phases = @()
        if ($plan.Shared) { $phases += [pscustomobject]@{ Exclusive = $false; Arg = $plan.Shared; Skip = @($plan.Skip) } }
        if ($plan.Solo) { $phases += [pscustomobject]@{ Exclusive = $true; Arg = $plan.Solo; Skip = @() } }
        $pre = $null
        if ($common -and $phases.Count -gt 1) {
            $pre = Enter-E2eSlots -Dir $common -N $nSlots -Exclusive -Why $why -WaitSec 0 -Quiet
            if ($pre) { $phases = @($phases[1], $phases[0]) }
        }
        $order = @($phases | ForEach-Object { if ($_.Exclusive) { "단독(" + $_.Arg + ")" } elseif (@($_.Skip).Count) { "공유(" + $_.Arg + " − 단독 묶음 " + @($_.Skip).Count + ")" } else { "공유(" + $_.Arg + ")" } })
        Write-Host ("  · 자리 간 e2e 칸 {0}개 (#553 — -Slots · JOSEON_E2E_SLOTS) · 판 {1}" -f $nSlots, ($order -join " → ")) -ForegroundColor DarkGray
        $runnerDone = $false
        $runnerStuck = $false
        $sums = @()
        try {
            foreach ($ph in $phases) {
                if ($runnerStuck) {
                    # 자기검사가 제한을 넘었다 = 러너가 안 켜졌거나(파스 오류 → e2e 모드 없이 게임만 돈다, #175) 멈췄다. 본 실행도 같은 자리에서 멈춘다 (#181)
                    Write-Host ("== e2e (" + $ph.Arg + ") ==") -ForegroundColor Cyan
                    Write-Host "  건너뜀 — 러너 자기검사가 멈췄다 (러너 파스 오류면 e2e 모드가 안 켜진다). 본 실행도 같은 자리에서 멈추니 돌리지 않는다" -ForegroundColor Red
                    continue
                }
                $h = $null
                if ($ph.Exclusive -and $pre) { $h = $pre; $pre = $null }
                elseif ($common) { $h = Enter-E2eSlots -Dir $common -N $nSlots -Exclusive:([bool]$ph.Exclusive) -Why $why }
                try {
                    if (-not $runnerDone) {
                        # 러너 자기검사 (#95) — 망가진 대본은 FAIL, 멀쩡한 대본은 PASS로 나와야 아래 결과를 믿을 수 있다.
                        # 일부러 SCRIPT ERROR를 내는 대본이 있으므로 이 실행의 출력은 SCRIPT ERROR 개수에 넣지 않는다.
                        Write-Host "== e2e 러너 자기검사 ==" -ForegroundColor Cyan
                        $r = Invoke-Step -Label "e2e 러너 자기검사" -Exe $godot -ArgList @("--path", $root, "--headless", "--", "--e2e-selftest") -Limit $LIMIT_STEP -Encoding $UTF8
                        $runnerDone = $true
                        $runnerStuck = $r.TimedOut
                        if (-not $r.TimedOut) {
                            if ($r.Out -match "E2E_SELFTEST PASS") { Write-Host ("  PASS  " + (($r.Out -split "`n" | Where-Object { $_ -match "E2E_SELFTEST" } | Select-Object -First 1).Trim()) + (Format-Sec $r)) -ForegroundColor Green }
                            else { Write-Host "  FAIL  러너 자기검사 — 러너 판정을 못 믿는다" -ForegroundColor Red; Write-Host $r.Out; $fail++ }
                        }
                    }
                    $kind = if (-not $h) { "칸 없이" }
                            elseif ($ph.Exclusive) { "단독" + $why + " — 다른 자리 e2e 없이" }
                            else { "공유 칸 " + (Get-SlotMark ([int](@($h.Slots)[0]))) + "/" + $nSlots }
                    $what = if (@($ph.Skip).Count) { $ph.Arg + " − 단독 묶음 " + @($ph.Skip).Count } else { $ph.Arg }
                    Write-Host ("== e2e (" + $what + " · " + $kind + ") ==") -ForegroundColor Cyan
                    if ($runnerStuck) {
                        Write-Host "  건너뜀 — 러너 자기검사가 멈췄다 (러너 파스 오류면 e2e 모드가 안 켜진다). 본 실행도 같은 자리에서 멈추니 돌리지 않는다" -ForegroundColor Red
                        continue
                    }
                    $eArgs = @("--path", $root)
                    if (-not $Windowed) { $eArgs += "--headless" }
                    $eArgs += @("--", ("--e2e=" + $ph.Arg))
                    if (@($ph.Skip).Count) { $eArgs += ("--e2e-skip=" + (@($ph.Skip) -join ",")) }
                    if ($Shots) { $eArgs += "--e2e-shots" }
                    $script:scriptErr = 0
                    $r = Invoke-Step -Label ("e2e (" + $what + ")") -Exe $godot -ArgList $eArgs -Limit $LIMIT_E2E -Encoding $UTF8 -OnLine {
                        param($s)
                        # 러너가 이제 SCRIPT ERROR를 스스로 FAIL로 센다(#95). 이 줄은 러너 밖(로드 전·종료 후) 오류까지 잡는 두 번째 그물
                        if ($s -match "SCRIPT ERROR|Parse Error") { Write-Host $s -ForegroundColor Red; $script:scriptErr++ }
                        if ($s -match "^E2E |^  [·✗]") {
                            if ($s -match "FAIL|✗") { Write-Host $s -ForegroundColor Red } elseif ($s -match "PASS") { Write-Host $s -ForegroundColor Green } else { Write-Host $s }
                        }
                    }
                    if (-not $r.TimedOut -and ($r.Code -ne 0 -or $script:scriptErr -gt 0)) { $fail++ }
                    if ($script:scriptErr -gt 0) { Write-Host ("  SCRIPT ERROR " + $script:scriptErr + "건 — 시나리오 코드 오류 (PASS 표시여도 실패)") -ForegroundColor Red }
                    Write-Host ("  e2e" + (Format-Sec $r) + " — 제한 ${LIMIT_E2E}초") -ForegroundColor DarkGray
                    if ($r.Out -match "E2E SUMMARY: (\d+)/(\d+) PASS") { $sums += [pscustomobject]@{ Kind = $(if ($ph.Exclusive) { "단독" } else { "공유" }); Pass = [int]$Matches[1]; Total = [int]$Matches[2]; Sec = $r.Sec } }
                }
                finally { Exit-E2eSlots $h }
            }
        }
        finally { Exit-E2eSlots $pre }
        if ($sums.Count -gt 1) {
            $sp = ($sums | Measure-Object -Property Pass -Sum).Sum
            $st = ($sums | Measure-Object -Property Total -Sum).Sum
            $parts = @($sums | ForEach-Object { "{0} {1}/{2} ({3:0}초)" -f $_.Kind, $_.Pass, $_.Total, $_.Sec })
            Write-Host ("  e2e 합 {0}/{1} PASS — {2}" -f $sp, $st, ($parts -join " · ")) -ForegroundColor $(if ($sp -eq $st) { "Green" } else { "Red" })
        }
        if ($Shots) { Write-Host ("  스크린샷 = " + (Join-Path $userDir "e2e")) -ForegroundColor Cyan }
    }
    # 내보낸 빌드 = 원본 (#349 도구 · #376 층) — -Export 를 줄 때만. e2e 칸은 안 잡는다(시간을 재지 않고 CPU 한 줄기 — 단위 층과 같은 무게)
    if ($layers.Export) {
        Write-Host "== 내보낸 빌드 = 원본 (export_check.py — #349·#376) ==" -ForegroundColor Cyan
        if (-not $isWt) { Write-Host "  ⚠ 본진에서 내보내기 — 헤드리스 편집기가 본진 .godot 을 쓴다. PD 편집기를 닫고 돌리거나 작업 트리에서 (export_check.py 머리말)" -ForegroundColor Yellow }
        if (Get-Command python -ErrorAction SilentlyContinue) { [void](Invoke-ExportCheck -Tool $exportTool -OutDir $exportOut -Limit $LIMIT_EXPORT) }
        else { Write-Host "  FAIL  export_check.py  python 없음 — 대조를 못 한다 (출시 전 필수 층이라 건너뛰지 않는다)" -ForegroundColor Red; $fail++ }
    }
}
finally { Pop-Location }

if ($fail -gt 0) { Write-Host "실패 $fail" -ForegroundColor Red; exit 1 }
Write-Host "전부 PASS" -ForegroundColor Green
exit 0
