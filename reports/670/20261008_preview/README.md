# #670 단일 연타 검수 영상

코드 후보 `306222b6` + UID 보완 `ec187232`. 게임 main에는 아직 착륙하지 않았다.

1280×720, 30fps Godot MovieWriter 원본에서 프레임 표식으로 잘랐다. 게임 화면과 게임 음성을 담았으며 데스크톱 녹화가 아니다. 고정 FPS는 동작 검수용으로 성능 비교에 쓰지 않는다. 보스 HP·AI는 동작 확인용으로 고정했다.

| 파일 | 길이 | 확인한 동작 |
|---|---:|---|
| [single_boss.mp4](single_boss.mp4) | 5.50초 | Lv10 보스 한 명에 5타 · 연속 시전 |
| [packed_three.mp4](packed_three.mp4) | 2.567초 | Lv5 밀집 3마리 가운데만 4타 · 이웃 둘 피해 0 |

single_flurry 96검사 PASS. CAPTURE single_boss는 frame254~419, packed_three는436~513. 전체 영상·음성 스트림 디코드 PASS; 음성 mean/max는 보스 −16.0/−0.4dB, 밀집 −16.1/−0.8dB이며 음량을 바꾸지 않았다. 프레임·크기·SHA256은 manifest.json, 검증 전문은 *_verify.log, 원래 엔진 출력은 capture_raw.log에 있다.

10MB 이상 원본은 git에 넣지 않는다. [OGV 원본 Release](https://github.com/genesiskoo/joseon-assets/releases/tag/art-670-20261008-preview) — capture_master.ogv **10,239,020 bytes**, SHA256 `64fe18101b41b4f59d8d2f124681a70ca57d3dd56c6a24c79cc04389bf152d53`. 로컬 원본은 이 폴더의 capture_master.ogv에 그대로 있다.

일반 창 모드 aoe_skills_2는 62검사 PASS, 일반 focused single_flurry/single_flurry_dps는96+13검사 PASS 및 기존 종료3ObjectDB/2resources. MovieWriter 원본은96검사 PASS 뒤 종료17ObjectDB/9resources를 출력했다. 아래 원문과 전체 capture_raw.log를 보존하며 촬영 모드 구버전 대조를 별도로 수행한다.

```text
WARNING: 17 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
ERROR: 9 resources still in use at exit (run with --verbose for details).
   at: clear (core/io/resource.cpp:822)
```

스킬 이름 3안 = 연속 베기(추천) / 몰아 베기 / 잇단 베기. 아이콘 A는 workbench/icons/670_flurry의 별도 후보이며 게임 반입 전이다. 이름·아이콘·동작은 PD 확인 대상이다.

Agent: Codex (GPT-6)
