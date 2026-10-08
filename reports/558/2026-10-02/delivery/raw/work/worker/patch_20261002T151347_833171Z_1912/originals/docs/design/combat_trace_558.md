# #558 기본 시계 전투 trace 구현 계약

정본 범위 = `combat_clock_536.md §1~3·5~6`. 런타임 전투 시계·선공권·수치·시드·입력 간격은 이 카드에서 고치지 않는다. #536 기본 focused/full 동일성은 후속 실제 선언 묶음의 결과로 판단하며 trace 구현만으로 완료하지 않는다.

## 1. 켜기와 실제 실행 증거

기본 `CombatTrace.enabled()`는 false다. `tools/test.ps1 -E2e -Scenario balance_boss -CombatTrace -TraceOut <고유폴더>`는 focused, `-Unit -E2e -CombatTrace -TraceOut <고유폴더>`는 기본 전체 단위·도구·공유/단독이다. FixedFps 기본0·Slots 기본3을 유지한다. 고정60은 기존 focused headless guard 안의 별도 진단이며 full·단위·창모드·내보내기에 넣을 수 없다.

실제 `$ph.Arg` 토큰·skip·exclusive·argv와 시작 직후 launcher PID를 LAUNCH에 남긴다. 보스 phase의 ENV engine PID는 종료 뒤 `phase.json`에 별도 기록한다. 각 실제 phase가 끝난 직후 다음 Godot 프로세스 전에 `tmp/e2e_raw/<UTC+testPID>/phase_<순서>_<solo|shared>/`에 `.NET`이 줄 단위로 합친 `console.merged.raw.log`, 원본 바이트 그대로 복사한 `godot.raw.log`, SHA256·판정·launch `phase.json`을 저장한다. 실패·timeout도 같은 경로로 보존하고 이전 폴더/trace 파일을 덮지 않는다.

## 2. 판과 몸의 기록

Fixture begin은 층 입장 전에 trace를 시작하고 원래 시드식으로 실제 몸이 바인딩될 때 role/ordinal을 받는다. 도호·흑랑·파수 둘의 실제4몸과 P2 소환 둘까지 최대6몸이며 미생성은 `not_spawned`에 표시한다. runtime ObjectID는 raw 증거이고 비교 키가 아니다. seed/initial/final/state는 GDScript signed64에서 `str(int)`로 직접 바꾼 십진 문자열이다.

메모리 이벤트는 판 기준 event_seq·물리 tick, 실제 callsite·`Engine.is_in_physics_frame()`, 상대 process frame과17소수 GameClock 상대값, 원 절대 epoch/frame을 함께 보존한다. busy/stagger의 절대 deadline과 inactive sentinel은 raw로 보존하고 남은 시간(max(0, deadline-now))·deadline_future와 분리한다. 원 swing/hitstop/session 카운터는 재설정하지 않고 상대 swing/hitstop과 generation applies를 따로 기록한다. ActorVisual의 실제 Mixer callback mode·process/physics priority·current clip/position, busy/MP/CD, 실제 target/거리·position·velocity/slide collision과 공격 RNG 전후를 읽는다. 아직 재생되지 않은 animation position은 `not_playing`, 유효하지만 트리에서 빠진 몸/타깃은 detached로 표시하며 전역 위치를 읽지 않는다. 충돌체 자동 생성 이름은 raw_name으로 남기고 정상 역할/위치/normal/depth 비교와 분리한다.

입력 poll/우클릭 held, cast attempt/success/rejected 사유, 실제 물리 entry, 자원 process 전후, swing begin·mark register/fire/cancel/immediate/timer due·mixer_applied·hitstop start/restore·impact generation/range 검사·receive_attack 전후를 그 호출 위치에서 동기로 기록한다. 관측이 신호 연결 순서·애니 구동 방식·타이머 옵션·난수 draw·await·이동/AI/대상을 바꾸지 않는다. 기존 receive_attack 본문은 같은 인자와 반환값으로 동기 한 번만 호출하고 앞뒤에서 읽는다.

## 3. 종료와 오버헤드

finish/close/대상 층 tree_exiting/다른 level_loaded/fixture exit/scenario dispose·PREDELETE와 러너 timeout 직후 정리 모두 한 번만 저장하고 disabled로 돌린다. 저장 전에 disabled로 바꾸며 원 fixture의 seed/state 복원·관찰 신호 정리를 유지한다. 진단 세대 소유권을 확인해 끝난 A fixture의 늦은 exit_tree/중복 finish가 새 B 판을 닫지 못하게 한다. 게임의 RNG/애니/세션 카운터는 재설정하지 않는다. 러너는 scenario timeout에서 PREDELETE를 기다리지 않고 fixture를 명시적으로 정리한다. 외부 강제 프로세스 종료는 메모리 버퍼의 끝 JSON을 저장할 수 없으며 phase raw·timeout 메타만 보존된다.

새 trace 이벤트는 메모리에 모아 판 끝에 JSON을 저장한다. 수집 bind/event 시간과 실제 wall 시간·event 개수를 문서에, 직렬화 시간을 FILE 행에 별도로 기록한다. 이 값은 관측 전체가 무영향이라는 증거가 아니며 수집 외 script 호출/스냅샷 복사/IO·기존 diagnostic note 비용까지0이라고 주장하지 않는다. 기존0.5초 파수 note는 남기고 추가 DT metadata는 모아 끝에 출력한다.

## 4. 비교와 검증

`python tools/combat_trace_compare.py <왼쪽 runArchive> <오른쪽 runArchive> --out <새 파일>`은 실제 phase argv의 --e2e/skip/FixedFps와 메타를 대조하고, 원본 raw ENV의 engine PID·user CLI, FILE saved/path/level/attempt와 모든 ATTEMPT·TRIES를 저장 trace와 연결한다. 원문 SHA/바이트 수를 확인하고 첫 패배·추가 시도의 파일이 양쪽에서 빠져도 누락을 실패로 잡는다. 정상 완료는 두 레벨의 TRIES가 필요하며 중단 phase의 미완료 레벨과 빈 outcome은 별도로 표시한다. trace 폴더만 주면 provenance 미제공·실제 판 전체 보존 미검증으로 명시한다. 첫 실패·추가2/3판·중단 기록을 버리지 않고 존재하지 않는 상대 판도 따로 출력한다. 12RNG/2combat/14행이나 첫판 승리를 요구하지 않는다.

판마다 사건 순서, 상대 physical tick,17소수 상대 GameClock float, state/payload, RNG 스트림 seed/initial/final, 원 outcome을 별도로 정확 비교한다. raw epoch·ObjectID·절대 swing/hitstop/session·충돌체 자동 이름은 비교 키에서만 제외하며 원문은 유지한다. 숫자를 반올림하거나 허용오차를 넓혀 성공으로 만들지 않는다. 최초 event/tick/state 차이는 float-only 시계 관측과 별도 표기한다. 정확한17소수 시계 비교는 유지하며 앞선 epoch float 차이만을 전투 최초 원인으로 표시하지 않는다. 최초 관측 차이와 원인 확정을 구분한다. 비교 보고서는 #536 완료로 자동 판정하지 않는다.

단위 = signed64 extrema/2^53 초과/음수 JSON 문자열, 기본off·위치/RNG 불변, 상대 카운터·미생성, 빈 애니·detached, 모든 cleanup 경로 idempotence·A 종료/B 시작/A 지연 종료, 실제 도호/흑랑/박쥐 receive_attack off/on 결과와 종료 RNG 일치다. 도구 자기검사는 failed/extra attempts·actual phase/PID/hash·원문 변조·fixed60 금지 조합·앞 phase 로그 회전 보존을 검사한다. 실제 최초 묶음은 root가 선언한 기본focused2+full1이며 일꾼이 별도로 보스전/전체를 재뽑지 않는다.

## 5. 왜 이 구조인가

기존 callback 안에서 읽어 실제 타격/입력/애니 순서를 관찰하고, 판 끝의 출력으로 새 파일 IO를 전투 도중에서 뺐다. 별도 Player-first 관리자나 시험 전용 수동 animation 운전은 실전 경로와 선공권을 바꾸고, 성공한 판만 추리는 fixed60 전용 비교기는 자연 시계 실패·재시도를 잃으므로 이 카드에 쓰지 않는다. 진단 결과를 확인한 경계의 런타임 수정은 별도 카드로 남긴다.
