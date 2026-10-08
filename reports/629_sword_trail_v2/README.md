# #629 검광 v2 실제 전투 영상 — 2026-10-05

PD 지시: 이펙트는 영상으로 보고. 실제 Godot MovieMaker 전투 렌더, 정상1×/기록60fps. 실시간 성능 측정이 아니다.

- video/629_sword_trail_before_after_60fps.mp4: 왼쪽 수정전 / 오른쪽 수정후. 평타3타·참격2회·회오리2회·치명3타, 각4.5초(총18초), 개선본 게임 소리.
- video/629_sword_trail_actual_60fps.mp4: 전체 게임 화면의 개선본 동일 네 구간18초, 게임 소리.
- video/*_engine_capture_60fps.mp4: 자막·크롭 이전 엔진 전체 촬영 전/후 각25.983초. AVI는 74MB의 로컬 인코딩 중간 파일이며 이 저장소에 넣지 않는다.

기준 소스76a5661e. 동일 카메라·무기·위치·시드(GameState20260916, PlayerCombat/Vfx629). 치명 구간만 QA용 crit_chance1이며 실제 게임 밸런스 수정이 아니다. 표적은 AI만 frozen/hp100000의 산적이며 실제 무기 애니·표본·피격·전투 판정을 쓴다. 입력은 기존 자동공격/스킬 경로. before/after 각19/19 PASS.

전후 타격프레임·공격간격·피해·MP debit·전투 RNG.state·리본 표시 프레임 수 모두 일치한다. 치명 명중 뒤 살아 있는 리본의 gold_frames만 달라진다. 피해량19/20/18/30, MP debit0/8/16/0. 캡처 범위와 원본 SHA, 전체디코딩 결과는 video_manifest.json·archive_manifest.json·logs/. 영상 각10MB미만, 카드50MB미만, H264·8bit4:2:0·60fps(full-range yuvj420p), 전체디코딩 오류0. 비교/적용은1080프레임/18초이며 AAC 패딩을 포함한 컨테이너18.021초, 연결 경계 AAC 약1.33ms DTS 보정 경고는 원문에 보존했고 영상 프레임 동기는 그대로다.

reproduce/ 파일을 게임 ._tmp/629_sword_trail_v2/에 복사하고 게임 루트에서 아래를 실행한다. BEFORE는 기준76a5661e, AFTER는 #629 구현 소스에서 따로 촬영한다.

```powershell
godot --path . --scene res://._tmp/629_sword_trail_v2/capture_scene.tscn --windowed --resolution 1280x720 --fixed-fps 60 --disable-vsync --quit-after 3000 --write-movie <작업트리절대경로>/._tmp/629_sword_trail_v2/before.avi --log-file <작업트리절대경로>/._tmp/629_sword_trail_v2/before.engine.log -- --new --phase=before *> ._tmp/629_sword_trail_v2/before.raw.log
# after.avi / after.engine.log / --phase=after / after.raw.log로 개선본 촬영
python ._tmp/629_sword_trail_v2/encode_video.py
python ._tmp/629_sword_trail_v2/archive_report.py
```

초기 촬영의 DamageCalc 정적 클래스를 오토로드 노드로 조회한 오류는 정상 정적 클래스 호출로 수정했다. 초기 오류 원문 발췌와 전투시드 고정 전 진단 로그도 logs/에 보존했다. 최종 촬영은 구문/셰이더/실행 오류0이며 기존 종료 리소스 정리 보고 원문은 포함한다. push는 하지 않는다.

## 최종 소스와 검증

게임 소스 커밋 `b5cdcaf0ac4ae27b8e0311c429c4fb1cd94271d9`. 영상 적용 런타임의 SHA256은 `video/video_manifest.json`에 기록했다.

최초 전체 검사: 단위97·설정 재시작2·도구23·러너5/5 PASS, E2E139/140의 기존 body_arts 피격 fixture만 실패. 산적 몸 시드가 고정되지 않은 시험을 첫 물리 공격 전 seed248로 고정하고 실패 진단을 추가했다. 실제 AI·명중·방패 경로와 게임 런타임은 유지한다. 보완 뒤 단독2회66검사 PASS, 최종 `test.ps1 -E2e` 종료0·140/140 PASS. 최초 실패와 최종 성공 원문 및 E2E 각 phase 상세 원문을 logs/에 함께 보존했다.
