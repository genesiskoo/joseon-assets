# #558 기본 시계 전투 trace 실측·검증 기록

실행 시작 **2026-10-02**, 분석 보고·문서 고정 **2026-10-03**. 첫 선언 묶음의 후보는 **`f1bf88f05a8eb48dd7d12510011245f3f6631e76`**이며 이후 도구 보완 커밋과 구분한다. 구현 계약은 [combat_trace_558.md](combat_trace_558.md), 시간 정책 정본은 [combat_clock_536.md §1~3·5~6](combat_clock_536.md)이다.

**상태: `main_landed=false`, `parent_536_complete=false`.** 본 기록 시점에는 main 착륙 전이다. 공식 검사·착륙·보드 처리는 root 담당이며, 이 문서 고정 작업은 게임 실행·시험 재실행·정식 비교 재실행 0회다. 코드·도구·테스트·GameState 수치·시드·준비/전투 입력 간격·승패/탕약/대가 기준과 원문은 수정하지 않았다.

## 1. 첫 선언 묶음과 실제 판 전체

root가 같은 동결 후보·같은 준비·원래 시드/판정으로 **기본 focused2 + 기본 full1**을 사전에 선언하고 실행했다. FixedFps0, 기본 Slots3, 실제 물리60Hz, time_scale `1.00000000000000000`이다. 고정60 진단 실행을 이 묶음에 넣지 않았다. `]` 준비6틱을 두 번, `V`5틱과 전투 입력6물리틱은 실제 raw 및 `input_ticks_ok`에서 유지됐다. GameState·스탯·45초 상한·최소8초·최대3판·원래 승패/탕약/대가 기준을 바꾸지 않았고 성공 시드 검색·추가 판 재뽑기·실패 삭제도 없다.

| 실행 | 실제 판 | 결과 | 전체 검증 |
|---|---|---|---|
| focused_1 | Lv3/1, Lv5/1 | 두 판 처치 | balance_boss 30검사 PASS |
| focused_2 | Lv3/1, Lv5/1 | 두 판 처치 | balance_boss 30검사 PASS |
| full_1 | Lv3/1, Lv5/1 | 두 판 처치 | 단위·도구 PASS, E2E **118/118**(공유108+단독10), return0·stderr0, 1723.8433811664581초 |

실제 **총6판·재시도0·누락0**이다. 각 Lv의 원문 TRIES는 `[처치]`라 실패 판이 실제로 없었다. 성공 판만 골라 만든 표가 아니다. 실제 초기4몸(도호·흑랑·파수 둘)과 이후 소환 둘, 최종6 stream·`not_spawned=[]`를 기록했다. 미생성 actor를 만들어 넣지 않았다.

정식 `combat_trace_compare.py` 비교는 **focused1↔focused2, focused1↔full1, focused2↔full1 세 건 모두 exit0·stderr0**다. 이는 실제 판 보존/검증 성공이며 전투 결과 동일성 PASS가 아니다. 입력은 trace 폴더 대신 각 `tmp/e2e_raw/<run>/` archive root다. full의 balance 판은 **phase_2_solo**(앞에 balance_room 실행), phase_1_shared의 원문도 별도로 보존했다. 실제 argv/skip/FixedFps→ENV PID·CLI→FILE saved/PID/path/Lv/attempt/eventcount→exact ATTEMPT·순차 TRIES→실제 JSON 집합과 raw byte SHA를 연결했다.

## 2. 원문·실행 경로·환경 증거

| 실행 | test PID / Godot launcher PID / engine PID | archive root | balance phase Godot raw SHA256 |
|---|---|---|---|
| focused_1 | 26024 / 48644 / **65412** | `20261002T1351502942221_26024/phase_1_solo` | `79fcc7f8896957a233ca734841d5bd25f4c390f8764e150c7c8633ca04b76827` |
| focused_2 | 62096 / 39436 / **53444** | `20261002T1415238741716_62096/phase_1_solo` | `cb60f07f8dabbfe51785e4dea3f7311002e4e983e9707385d4514f8dc8f6e779` |
| full_1 | 60640 / 65888 / **11816** | `20261002T1426594457684_60640/phase_2_solo` | `fe5a79cb936a859deed4ac17bea8f79253315af05a5b5abb099136f0fde4d335` |

archive base = `C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon/tmp/e2e_raw/`. 실제 phase argv는 `--path <WT> --headless --` 뒤 focused의 `--e2e=balance_boss`, full solo의 `--e2e=balance_room,balance_boss,hit_stagger,pack_perf,bodies_cap,gimmicks,item_showcase,footsteps,audio_cues,sfx_limiter`, 공통 `--combat-trace --combat-trace-dir=<실제 고유 phase 폴더>`다. **`--fixed-fps`는 없다.** 전체 인자 토큰·launch 시각/PID·ENV·FILE 목록은 다음 실제 파일에서 보존한다.

- [focused1 phase/argv](<C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon/tmp/e2e_raw/20261002T1351502942221_26024/phase_1_solo/phase.json>) · [Godot raw](<C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon/tmp/e2e_raw/20261002T1351502942221_26024/phase_1_solo/godot.raw.log>)
- [focused2 phase/argv](<C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon/tmp/e2e_raw/20261002T1415238741716_62096/phase_1_solo/phase.json>) · [Godot raw](<C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon/tmp/e2e_raw/20261002T1415238741716_62096/phase_1_solo/godot.raw.log>)
- [full solo phase/argv](<C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon/tmp/e2e_raw/20261002T1426594457684_60640/phase_2_solo/phase.json>) · [Godot raw](<C:/Users/FORYOUCOM/.codex/worktrees/558-combat-clock-trace/joseon/tmp/e2e_raw/20261002T1426594457684_60640/phase_2_solo/godot.raw.log>)
- [full RUN](<C:/workspace/joseon/._tmp/trace_558_20261002/cohort/full_1/RUN.json>) · [stdout 전문](<C:/workspace/joseon/._tmp/trace_558_20261002/cohort/full_1/stdout.raw.log>) · [stderr 전문](<C:/workspace/joseon/._tmp/trace_558_20261002/cohort/full_1/stderr.raw.log>)
- [ENV/seed/DT/CLOCK/FILE·RUN 전부](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/cohort_audit_01.json>) · [6개 실제 trace와 원문 SHA 무변경 확인](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/evidence_integrity_01.json>)

seed 공식은 `20260916 + level*1000003 + attempt*10007 + role*1009 + ordinal*101`로 모두 동일했다. seed/initial/final/state는 **signed64 십진문자열**로 원문과 연결하여 검증했다. 각 판 `physics_dt_min=max=0.01666666666666667`, process_dt는 자연 실행에 따라 달랐다. **14행은 이번 실행 각각의 최종 RNG 요약12+ATTEMPT2 실측일 뿐 완전성 조건이 아니다.** 최초 RNG12·DT·전체 이벤트 행을 빼고 고정14행으로 자연 실행을 판정하지 않았다.

## 3. 결과와 최초 관측을 구분

| Lv5 실행 | 공격 / 명중 | 탕약 | HP / 최저HP | 시간 원문 |
|---|---|---|---|---|
| focused1 | **33 / 21** | **3** | **68 / 47** | `25.69999999999854300` |
| focused2 | **28 / 18** | **2** | **53 / 51** | `24.59999999999860500` |
| full1 | **31 / 19** | **3** | **87 / 47** | `24.59999999999860900` |

Lv3은 세 실행의 공격41·명중25·탕약3·HP34·최저HP32와 RNG6 final/관측 변화 값열이 같다. focused pair는 exact outcome도 같다. full은 input_polls278 대277, sec `27.79999999999842300` 대 `27.69999999999967600` 등 시간 원문이 달라 exact outcome은 다르다.

focused pair 최초 state/payload는 Lv3 **seq3/tick0**(process delta·idle clip_position), Lv5 **seq4/tick0**(process delta)다. 최초 order/tick은 Lv3 seq7(player_physics tick2 대resource_process_before tick1), Lv5 seq25(hitstop_restore tick8 대player_physics tick9)다. focused/full은 seq2/tick0 body_bound부터 상태가 달랐다. 같은 배열 인덱스의 최초 clock 차이는 이미 다른 이벤트/tick을 가리키므로 순수 float 오차나 최초 원인으로 표시하지 않았다.

같은 actor/callsite/physics/tick의 별도 exact17 clock 비교도 유지했다. focused Lv3 pair의 같은 player_physics tick clock 차이는 없고, Lv5 pair의 최초는 tick216 `3.59999999999979890` 대 `3.59999999999979540`다. focused/full Lv3은 tick1 `0.01666666666666666` 대 `0.01666666666666572`다. 이미 전체 이벤트 순서가 다른 뒤 관측 키를 연결한 비교이며, 전체 이전 경로 동일성이나 인과를 뜻하지 않는다. 절대 epoch/frame/swing·raw collision 이름도 삭제하지 않았고 숫자 반올림·허용오차 확대는 하지 않았다.

## 4. 준비 상태 수렴과 첫 타격

도호는 **role1/ordinal0**, 흑랑은 role2/ordinal0, 파수2는 **role4/ordinal2**, 소환2는 role3/ordinal2다.

full Lv3 binding seq2/tick0은 stopped=true·clip_speed0·stagger_remaining `0.10000000000001208`, focused는 false/1/0이었다. full seq21/tick7의 Player._physics_process에서 경직0, seq41/tick10에서 stopped=false·speed1로 **준비 중 수렴**했다. 첫 입력seq187/tick21→승인cast189/tick21→실제 첫 mark_fire795/impact_range_check796/흑랑 receive_before797(tick56)까지 이 경직·멈춤 차이는 남아 있지 않았다. 첫 승인 직전 focused/full 상태 차이는 유휴 clip_position만이며 위치·속도·HP/MP/CD/busy/committed/target/RNG는 같다. 시작 경직이 그대로 첫 시전을 막았다는 결론은 지지되지 않는다.

Lv5 body_bound의 충돌 차이는 이전 move_and_slide의 캐시다. 실제 도호 위치·속도는 같고 full의 raw_name=freed인 과거 측면 충돌 캐시는 **seq7/tick1 combat_physics**에서 ClickFloor 위쪽 법선 캐시로 교체된다. focused 콜라이더가 freed로 표시만 바뀌는 것은 새 충돌로 취급하지 않았다. 첫 입력tick28에는 세 실행 모두 도호 위치(10.5,0.00039062649011612,8.5)·속도0·이번 FloorBody 충돌점/법선/depth까지 같다. 이전 캐시를 이번 판의 새 충돌이나 원인으로 단정하지 않는다. [TRACE._body_state](../../core/combat_trace.gd)는 캐시를 읽으며 이동을 새로 수행하지 않고, [Player._physics_process](../../actors/player.gd)의 hook은 move_and_slide 이전이다.

Lv5 첫 승인 cast는 focused1 seq209, focused2 seq212, full seq221로 모두 tick28이다. 첫 실제 doho mark_fire→impact_range_check→흑랑 receive_before는 focused1 seq821→822→823/tick63, focused2 836→837→838/tick64, full827→828→829/tick63이다. 당시 실제 표적/공격 인자/RNG는 같고 clip/CD/MP 일부가 달랐다. [첫 입력·승인 시전·실제 타격 직전 snapshot 전부](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/cohort_preparation_and_first_impact_01.json>) · [준비 원문 창](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/cohort_preparation_original_evidence_01.json>).

## 5. 같은 입력의 CD 정책 분기와 이후 실제 사건

Lv5 **poll141/tick868**의 도호 위치·흑랑 target·거리 `1.69333457946777340`·RNG `-8936760622420917439`·커밋/busy가 같다. focused pair의 직전 state 차이는 **CD·MP 두 필드뿐**, MP는 모두 비용5 이상이다.

| 실행 | input→attempt→result seq | 직전 CD | 결과 |
|---|---|---|---|
| focused1 | 14507→14508→14509 | `0.00098355555555510` | cooldown_blocked=true·mp_blocked=false로 반려 |
| focused2 | 14510→14511→14512 | `0.00000000000000000` | 참격 승인 |
| full1 | 14510→14511→14512 | `0.00356799999999738` | cooldown_blocked=true·mp_blocked=false로 반려 |

앞선140 poll의 승인/반려 종류·사유는 같다. 이전 모든 process snapshot이 같다는 뜻은 아니다. [PlayerCombat._process](../../actors/player_combat.gd)(f1bf88f0 기준257~261)는 process delta로 CD를 감소시키고 cast_active(807~810)는 CD>0이면 반려한다. **이 gate는 그 요청의 승인 차이를 설명한다. 전체 전투의 최초 인과는 미확정이다.** focused1/full의 첫 poll 분기는 poll157/tick964의 CD0 승인 대 `0.00356799999999738` 반려다.

focused pair의 도호 실제 위치는 **tick874**(player_physics seq14621/14624, x10.10000038146972700 대10.16666698455810500), 파수2의 실제 위치는 **tick875**(enemy_physics_after_move seq14635/14638)부터 다르다. 파수2의 tick874 차이는 먼저 target 위치/거리였다. outgoing receiver 순서의 최초 차이는 15번째: focused1 소환2 seq17127/tick1000 대focused2 흑랑seq17887/tick1035(full은 흑랑17890/tick1036). incoming source 순서 최초 차이는 18번째: focused1 파수2 seq17826/tick1034 대focused2 흑랑seq18014/tick1041(full은 파수2 17831/tick1034).

| Lv5 incoming source | focused1 호출/명중 | focused2 호출/명중 | full 호출/명중 |
|---|---|---|---|
| 흑랑 | 16/11 | 15/10 | 15/10 |
| 파수1 | 9/6 | 9/6 | 9/6 |
| 소환1 | 4/2 | 4/2 | 4/2 |
| **파수2** | **4/2** | **0/0** | **3/1** |

모든 before/after 호출과 양수 dealt를 원 outcome attacks/hits에 대조해 정확히 일치시켰다. focused pair의5공격·3명중 차이는 흑랑1공격·1명중과 파수2 4공격·2명중 차이다. 단순 epoch 표시 차이가 아니다.

최초 도호 RNG 값 소비는 Lv5 focused1 seq825/tick63, focused2 seq840/tick64, full seq831/tick63으로 같은 `5600093101942189313→-3276735553772873825`를 다른 시점에 관측했다. focused pair의 최초 stream 값열 차이는 파수2 focused1 seq17827/tick1034의 `5723061790796302234→-2294790372600408388`; focused2에는 이 소비가 없고 initial=final이다. full은 같은 소비를 seq17832/tick1034에서 관측한다. 기존 hook에서 관측된 상태 변화 수이며 내부 RNG draw 수가 아니다.

## 6. 진단 한계·별도 도구 보완·문서 고정

수집 시간은 battle wall의 약6.50~6.98%(판당1.65~2.00초), full Lv3 직렬화1010065usec·Lv5 837801usec는 종료 후 별도 측정이다. 무관측 baseline 없이 실제 slowdown 비율이나 영향0을 주장하지 않는다. 외부 hard kill 때 메모리 trace를 저장하지 못할 수 있는 한계도 유지한다.

**`c85149ee44c6c7b1183fcdeefb92a3912705d039`는 첫 묶음 이후의 별도 진단 도구 수정**이다. `balance_replay.py` 고정60 비교에서 실행마다 달라지는 launch.launcher_pid/launched_utc만 equality 키에서 분리하고 원문·보고서에는 보존했다. 실제 argv/engine/environment/seed/stats/기준 비교는 엄격하게 유지한다. pure Python 자기검사 **57/57**이며 [SELFTEST 메타](<C:/workspace/joseon/._tmp/trace_558_20261002/worker/selftest_20261002T151356_627542Z_54912/SELFTEST.json>) · [stdout](<C:/workspace/joseon/._tmp/trace_558_20261002/worker/selftest_20261002T151356_627542Z_54912/balance_replay.stdout.raw.log>) · [stderr](<C:/workspace/joseon/._tmp/trace_558_20261002/worker/selftest_20261002T151356_627542Z_54912/balance_replay.stderr.raw.log>)를 보존한다. 기존 첫 cohort를 새 후보의 실행으로 재분류하지 않았고 게임을 다시 실행하지 않았다.

문서 전후 게임 소스/자산/설정의 git blob 목록 SHA256은 `8e64e08d7bac84e421ff7394f2c0839fd320c24e4265845725b096457f48cfdb`(actors/core/world/ui/data/assets/addons/shaders/project.godot, 2778행), docs 제외 전체 목록은 `ab7931a1c664a38c2d44fa72788326c4f20a95755aba8c9d95c78d89a6869cb4`(3419행)로 동일하다. GameState blob은 `73d6b5a46452d6c4d97794435eb43f00d018df4f`이다. [문서 작성 전](<C:/workspace/joseon/._tmp/trace_558_20261002/worker/docs_record_01/before.json>) · [커밋 후](<C:/workspace/joseon/._tmp/trace_558_20261002/worker/docs_record_01/after.json>)에 기록한다. docs2개만 명시적으로 커밋하며 main 착륙·보드·push·유료 생성은 이 작업에서 하지 않는다.

실제 실행 매니페스트에 판 전체를 연결하고 event/tick/state·clock·RNG를 나눈 것은 추가 시도나 원문을 잃지 않으면서 국소 분기와 전체 인과를 구분하기 위해서다. 고정14행이나 성공 판만의 표는 자연 시계 진단에 사용하지 않는다. **#536 기본 focused/full 재현·결과 동일성은 여전히 미완료**이며 준비 수렴만으로 해결됐거나 AnimationPlayer callback 하나가 단독 원인이라고 결론내리지 않는다.

추가 증거: [focused pair 정식 보고서](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/focused_pair/comparison.json>) · [focused1/full](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/focused_1_vs_full_1/comparison.json>) · [focused2/full](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/focused_2_vs_full_1/comparison.json>) · [최초 관측 분리](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/cohort_first_divergence_01.json>) · [같은 tick exact clock](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/cohort_aligned_clock_01.json>) · [6판 RNG 변화 전부](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/cohort_observed_rng_01.json>) · [상세 결론](<C:/workspace/joseon/._tmp/trace_558_20261002/analysis/cohort_conclusion_01.txt>).
