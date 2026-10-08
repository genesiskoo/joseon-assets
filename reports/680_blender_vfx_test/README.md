# #680 Blender + Godot VFX 시험

실제 화염부와 나찰녀 살 구슬에 Blender 볼륨 질감을 연결한 프로토타입이다. 게임 브랜치 `codex/680-blender-vfx`, 기준 `bc7b48c5`. 시험 스위치 `Vfx.blender_test_enabled`는 기본 false이며 캡처와 새 E2E에서 켠다.

## 결과 영상

![약불 → 강불 → 약살 → 강살 · 정상 속도 · 2배 확대](680_blender_vfx_before_after_60fps.mp4)

- [실제 게임 카메라·원음, 24초](680_blender_vfx_actual_60fps.mp4)
- [Blender에서 구운 재료 미리보기, 4초](680_blender_baked_atlas_preview_24fps.mp4)
- [BEFORE 엔진 전체 기록](680_blender_vfx_before_engine_capture_60fps.mp4) / [최종 AFTER04 엔진 전체 기록](680_blender_vfx_after_engine_capture_60fps.mp4)
- 같은 프레임의 전후 JPG 3쌍: [촬영 보고서](CAPTURE_README.md).

A/B는 동일 원본 프레임을 2배 확대해 정상 1× 속도로 재생한다. 실제 게임 편집본과 전체 기록은 원래 카메라/원음이다. Godot MovieMaker 60fps로 제작했으며 실시간 성능 측정 결과로 사용하지 않는다. 음원 변주는 각 master에 보존하고 A/B의 AFTER AUDIO를 화면에 표시했다.

## 제작 방식과 편집 가능한 원본

Blender 5.2.2 LTS/Eevee/RTX4070에서 Principled Volume과 주기적인 4D Noise·왜곡으로 실제 3D 참여매질을 렌더했다. 화염은 휘는 심과 갈라진 꼬리, 살은 다섯 타원 연무 덩어리다. 유체 solver/cache를 사용한 제작은 아니며 로컬 제작만 사용했다.

- [화염 Blender 원본](blender_source/blends/fire_jet.blend), [살 Blender 원본](blender_source/blends/sal_mist.blend): 재질·카메라·29프레임 키프레임 포함.
- [제작 Python·렌더 원문·재현 명령](blender_source/README.md), [원본/결과 SHA256](blender_source/manifest.json).
- 실제 RGBA 384×384 각 28장 → premult 알파 겹침 4프레임 → 각 24장/24fps. 공통 크롭 후 화염 312×90, 살 292×158이다. 원시 색/알파를 그대로 보존하며 Godot에서 색띠와 농도를 조정한다.
- 불씨 GLB 12정점/20삼각형, 방울 GLB 42정점/80삼각형도 Blender에서 만들었다.

Godot은 시트의 먹/안개 mix 재질, 화염의 좁은 밝은 심, 실제 GPUParticles3D, .12초 AnimationPlayer를 조합한다. 실제 투사체가 위치와 방향을 소유하고 후류만 대체한다. 약/중/강은 시트 크기·농도와 입자 4/8/12개로 구분한다. 화염 3패스·살 2패스, 외곽 반경 최대 1.2u, 기존 루프 128/원소후류 16 상한을 유지한다.

이 구조를 쓴 이유는 Blender의 내부 질감과 Godot의 실제 비행·명중·정지·회수 제어를 함께 쓰기 위해서다. 전부 코드 메시로 만드는 대안은 이번에 필요한 불/안개 내부 결을 조정하기 어렵고, 전체 공격을 동영상으로 대체하는 대안은 방향과 판정 시점을 제어하기 어려워 선택하지 않았다.

## 검수와 재현

BEFORE 48/48, 최종 AFTER04 48/48 PASS. 실제 약/강 벨트 화염부·나찰녀 AI 네 장면에서 피해·소모·MP·HP·절대 DOT 시계·binary64 상태·발사/명중 프레임·배우 동작·카메라·RNG 전체가 동일하다. 화염 birth64/hit83, 살 birth63/hit117이다. 촬영 fixture·독립 음원·원본 바이트 증거는 [촬영 보고서](CAPTURE_README.md)와 [video_manifest.json](video_manifest.json)에 있다.

혼합 모듈 단위 158/158, 새 실제 E2E 67/67 PASS. 전체 검사의 최초 단위 단계에서 기존 배송 검사 1종이 4FAIL을 냈다. 모든 VFX 폴더를 일반 큐 시트로 간주한 가정을 보완하여 실제 factory 자료·소비 노드에서 소유권을 검증한다. 테스트만 수정했고 단독 재검수는 exit0/공통 unit_verdict PASS다. 나머지 단위 113종·설정 재시작 2종·도구 23종은 PASS이며, 최초 전체 exit와 보완 재검수 결과를 구분해 기록한다. 전체 E2E는 151/151 PASS(단독10/공유141)다. 최초 전체 exit1과 배송 보완 재검수 exit0를 구분한 원문·판정은 verification_manifest.json에 기록한다. LF 메타데이터 최종본 혼합 단위158/158도 exit0로 재확인했다. [검수 원문 ZIP](verification_raw_originals.zip)은 최초 실패와 보완 후 성공을 함께 보존한다.

```powershell
# 실제 시험 시나리오: 게임 자체 벨트 입력·적 AI·명중·메뉴/회수 검수
.\tools\test.ps1 -E2e -Scenario blender_vfx_test_v1 -Windowed -Shots

# 전체 검사
.\tools\test.ps1

# 최종 촬영 리소스와 게임 Git blob 대조
python ._tmp/680_blender_vfx_test/capture/verify_commit.py <game_commit> after04
```

원본 대조 helper는 [capture_tools](capture_tools/)에도 복사했다. 실행 경로는 게임 작업 트리이며 private user://를 사용한다. 본진 착륙과 push는 이 시험 결과의 PD 채택 후 진행한다.

## 기각본과 보존

첫 Blender 렌더의 직각 꼬리/구형 구름을 보완했고 실제 화염 density 부족은 재렌더했다. Godot AFTER01은 투명 여백으로 너무 가늘어 기각했다. 동일 픽셀의 공통 크롭/anchor/gain을 적용한 AFTER02는 강불이 긴 노란 전선처럼 보여 기각했다. 최종 AFTER03은 주홍 density 색띠와 저농도 외곽, 탄두 쪽 좁은 core로 보완했다. 기각된 실제 영상·runtime 원본·원문도 보존한다.

모든 공유 영상 전체 decode 오류 0. report 파일은 개별 10MB 미만, 카드 합계 50MB 미만으로 관리한다. 대형 AVI·원시 프레임은 로컬 중간물이며 [intermediate_avi_manifest.json](intermediate_avi_manifest.json) 및 제작 manifest에 경로·크기·SHA256를 남겼다. 작은 편집 가능한 .blend 사본 두 개는 이 보고서에 포함한다.

메타데이터 두 파일의 JSON 값은 그대로 두고 제작 source/report/game 사본을 저장소 LF 정책에 맞췄다. 구판 CRLF와 SHA는 blender_source/revisions/pack_v2_crlf에 보존했고 LF 최종본으로 AFTER04를 실제 재촬영했다. 엄격한 index 대조는 893개 중 873개 raw exact, 기준에 이미 존재했던 메타 CRLF 20개만 예외다. 새 예외는 추가하지 않았다.

최종 게임 커밋: 3f079166e86481794d2bd834b69eb42c0af48335. AFTER04 실제 촬영893리소스를 이 커밋과 대조하여873개 raw byte exact, 기존 기준 메타 CRLF20개만 예외인 것을 확인했다(exit0). core .gd/shader/data/scene와 신규 Blender 자료는 raw exact다. 결과는 video_manifest.json의 source_after_commit_verification과 검수 원문 ZIP에 보존한다.
