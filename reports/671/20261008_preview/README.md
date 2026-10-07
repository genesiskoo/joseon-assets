# #671 빈 부적 실제 입력 검수 영상

#671 미커밋 작업 트리 후보의 실제 F4 선택·우클릭 입력을 담았다. #670 ec187232 코드 의존이 포함되며 게임 main 착륙 전이다. 최종 커밋과 UI before/after는 별도 검수한다.

1280×720, 30fps Godot MovieWriter 게임 화면·게임 음성 원본이다. 프레임 표식으로 클립을 잘랐으며 음량을 바꾸지 않았다. 고정 FPS는 동작 검수용이며 성능 비교에 쓰지 않는다.

| 파일 | 길이 | 확인한 동작 | 원본 프레임 |
|---|---:|---|---|
| [talisman_fire.mp4](talisman_fire.mp4) | 1.100초 | 화염 선택·단일 투척·빈 부적 1장 소비 | 23~56 |
| [seal_fire.mp4](seal_fire.mp4) | 0.867초 | 화염 진법 실제 우클릭·1장 소비 | 1083~1109 |
| [rain_fire.mp4](rain_fire.mp4) | 2.967초 | 화염 난사 실제 우클릭·15장 일괄 소비 | 902~991 |
| [ammo_zero.mp4](ammo_zero.mp4) | 0.467초 | 0장 HUD·우클릭 거부·피해 없음 | 140~154 |

talisman_targeting 147검사 PASS. 진법의 전체 지속 시간·난사 자원 원자성·빙결·저장 이행은 시나리오/순수 검사에서 따로 판정한다. 짧은 클립만으로 모든 계약의 통과를 주장하지 않는다.

영상과 음성 전체 디코드 PASS. 음성 mean/max dB: 화염 −37.1/−11.8, 진법 −24.4/−0.0, 난사 −22.4/−2.3, 잔량0 −25.2/−16.3. 크기·SHA256·ffprobe 메타는 manifest.json, 디코드 전문은 각 *_verify.log, 엔진 출력 전문은 capture_raw.log에 있다.

원본 capture_master.ogv는 **9,130,896 bytes**이며 10MB 미만이라 이 아트 저장소 reports에 보존한다. SHA256 `f8baf55b64477529f7bd928de6f464716fe8c53c5553e0ad0fc9485104fea98c`. 1255프레임, 41.833초이다. 카드 원본 총합은 50MB 미만이다.

시나리오 PASS 후 MovieWriter 종료 진단은 아래와 같다. 일반 실행의 기존 3ObjectDB/2resources보다 많으므로 구버전 MovieWriter 대조를 기다린다. 원인을 확정하지 않았으며 raw를 보존한다.

```text
WARNING: 13 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
ERROR: 7 resources still in use at exit (run with --verbose for details).
   at: clear (core/io/resource.cpp:822)
```

프레임 표식을 쓰는 이유는 실제 게임 입력과 효과가 나온 구간을 같은 원본에서 재현하기 위해서다. 데스크톱 녹화는 OS 커서·창 배치가 섞이므로 사용하지 않았고, 고정 FPS 녹화의 한계는 위에 명시했다.

빈 부적 아이콘 A는 workbench/icons/671_blank_talisman의 별도 파일 선택 후보이며 게임 반입 전이다. PD 파일 지목과 최종 화면의 "합쳐"를 기다린다.

Agent: Codex (GPT-6)
