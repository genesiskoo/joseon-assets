# #630 회오리/칼바람 구조 v1 — 실제 전투 영상

PD 지시: 이펙트는 영상으로 보고. 실제 Godot MovieMaker 60fps·정상1×. 회오리베기/칼바람 Lv1·5·10 각각240프레임(4초), 비교/실제 적용 총24초. 기록60fps는 실시간 성능 측정이 아니다. 비교는 왼쪽 기존/오른쪽 개선, 동일 crop(280,80,720,540)·640×480축소와 개선본 게임 소리. 실제 적용은 전체1280×720 화면, 엔진 보존본은 자막·크롭 이전 전체 촬영.

| 영상 | 길이 | bytes |
|---|---:|---:|
| video/630_whirl_structure_before_after_60fps.mp4 | 24.000000초 | 8610854 |
| video/630_whirl_structure_actual_60fps.mp4 | 24.000000초 | 9303528 |
| video/630_whirl_structure_before_engine_capture_60fps.mp4 | 38.216667초 | 7444714 |
| video/630_whirl_structure_after_engine_capture_60fps.mp4 | 38.216667초 | 8994009 |

먹 몸통은 blend_mix·안개 적용·opacity .26(잔상 .12), 밝은 심은 blend_add·fog_disabled·opacity .86(잔상 .58)이며 개선본의 현재 구현값이다. 모든 영상 H264·8bit4:2:0·60fps. 실제 pix_fmt/color_range는 video_manifest.json probe에 표기한다. 전체디코딩 오류0, 각 파일10MB미만·카드50MB미만. 큰 AVI는 로컬 인코딩 중간파일이며 전체 엔진 MP4를 보존한다. 로컬 AVI의 절대 위치·크기·SHA256은 metadata/local_intermediates_manifest.json에 기록한다.

기준 소스 b5cdcaf0ac4ae27b8e0311c429c4fb1cd94271d9. 전후 실제 촬영 각73/73PASS. 같은 넓은 방(흑랑굴1층), 도호·철검·camera(-35.264°,45°,ortho11), 힘15/민첩15/체력20/정기20·산적8명(1.7u/3.1u 고리)·HP100000·AI frozen·crit0/sure_hit. 캐릭터Lv30은 학습 요구 충족용이며 능력치를 올리지 않는다. 회오리 한 번 실제시전(frame30), 칼바람은 실제 우클릭 frame30→180홀드(2.5초)·해제 뒤 도는 바퀴까지 정상 종료. 도호 발밑 cursor고정으로 제자리회전; 무기/클립/수명/판정은 실제 게임 경로.

global/Vfx/PlayerCombat 시드630·GameState20260916. 전후 기록 필드가 정확히 같다: 타격프레임/대상/피해·MP debit/net·전투/GameState RNG.state·리본 표시 프레임·칼바람 바퀴/명중합·반경·스탯·240프레임 도호/카메라 좌표. 서로 다른 스킬레벨 사이 피해·반경·MP차이는 기존 게임 수치다.

| 구간 | 피해 | MP debit | 맞힌 대상 | 바퀴 |
|---|---:|---:|---:|---:|
| whirl1 | 33.0 | 8.000000 | 4 | 0 |
| whirl5 | 125.0 | 8.800000 | 8 | 0 |
| whirl10 | 392.0 | 9.800000 | 8 | 0 |
| storm1 | 150.0 | 18.000000 | 4 | 9 |
| storm5 | 223.0 | 23.142857 | 4 | 9 |
| storm10 | 612.0 | 29.571429 | 8 | 9 |

metadata/에 source/대본SHA·rawSHA·fixture·bounds·combat 전체, reproduce/에 촬영/검증/인코딩/아카이브 대본. BEFORE는 기준소스, AFTER는#630구현소스. 파일해시·길이는 archive_manifest.json. initial_visual_review와 after01 원문/메타는 메뉴 정지 예약 타이머 수정 전 최초 검수본이며, 최종 영상은 process_always=false를 반영한 AFTER02(after.*)다. 비정지 전투 메타는 두 개선본에서도 정확히 같다. 6장1280폭 JPG는 회오리Lv1/5/10의 동일 절대 엔진프레임을 추출한 보조자료.

정상 scene 촬영은 실행/셰이더 오류0. VIDEO630 PASS·Done recording 뒤 종료단계의 기존 ObjectDB11/리소스6 정리 보고는 raw전체보존. #629기준before와 동일하며 tools/test.ps1:924,986-987의 기존 종료보고 허용목록 자기검사와 일치한다. 최초 --check-only/--script 진입은 autoload GameState가 없는 독립실행이라 컴파일오류를 기록했고, 정상projectscene 최종촬영은 모두 통과했다. parse.raw.log/parse.engine.log도 보존했다.

재현: reproduce 파일을 게임 ._tmp/630_whirl_structure/에 복사한 뒤 기준/개선작업트리 각각에서 호출. 경로는 작업트리절대경로.

```powershell
godot --path . --scene res://._tmp/630_whirl_structure/capture_scene.tscn --windowed --resolution 1280x720 --fixed-fps 60 --disable-vsync --quit-after 3600 --write-movie <작업트리>/._tmp/630_whirl_structure/before.avi --log-file <작업트리>/._tmp/630_whirl_structure/before.engine.log -- --new --phase=before *> ._tmp/630_whirl_structure/before.raw.log
python ._tmp/630_whirl_structure/validate_capture.py before
# AFTER: after.avi/after.engine.log/--phase=after/after.raw.log
python ._tmp/630_whirl_structure/validate_capture.py after
python ._tmp/630_whirl_structure/encode_video.py
python ._tmp/630_whirl_structure/archive_report.py
```

<!-- FINAL_CHECKS630_BEGIN -->

게임 최종 commit: 8914e7c0633dfb45b8450f9c3218081cf46cc51a. AFTER 촬영 source SHA와 현재 runtime/해당 commit의 모든 원문이 일치한다.
종합 최종 결과: 단위 대본 98개, 설정 재시작 2단계, 도구 셀프테스트 23개. E2E 141/141 PASS.
창 모드 6/6종의 마지막 개별 실측 PASS. 묶음 실패를 합격으로 바꾸지 않고, 후속 개별 재검증을 시나리오별 마지막 결과로 기록했다.
원문 및 세부 실측은 logs/final_checks/final_checks.json과 console/에 보존한다. 최초 E2E 실패도 그 실행의 godot.raw.log·phase.json byte-exact 원문으로 함께 보존한다. console.merged.raw.log는 같은 원문이므로 추가하지 않는다. 기존 logs/의 진행 중 스냅샷과 구분하여 final_checks/를 최종 검증 근거로 쓴다.

<!-- FINAL_CHECKS630_END -->
