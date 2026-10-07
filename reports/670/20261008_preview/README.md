# #670 단일 연타 검수 영상

코드 후보 `306222b6` + UID 보완 `ec187232`. 게임 main에는 아직 착륙하지 않았다.

1280×720, 30fps Godot MovieWriter 원본에서 프레임 표식으로 잘랐다. 게임 화면과 게임 음성을 담았으며 데스크톱 녹화가 아니다. 고정 FPS는 동작 검수용으로 성능 비교에 쓰지 않는다. 보스 HP·AI는 동작 확인용으로 고정했다.

| 파일 | 길이 | 확인한 동작 |
|---|---:|---|
| [single_boss.mp4](single_boss.mp4) | 5.50초 | Lv10 보스 한 명에 5타 · 연속 시전 |
| [packed_three.mp4](packed_three.mp4) | 2.567초 | Lv5 밀집 3마리 가운데만 4타 · 이웃 둘 피해 0 |

single_flurry 96검사 PASS. CAPTURE single_boss는 frame254~419, packed_three는436~513. 전체 영상·음성 스트림 디코드 PASS; 음성 mean/max는 보스 −16.0/−0.4dB, 밀집 −16.1/−0.8dB이며 음량을 바꾸지 않았다. 프레임·크기·SHA256은 manifest.json, 검증 전문은 *_verify.log, 원래 엔진 출력은 capture_raw.log에 있다.

10MB 이상 원본은 git에 넣지 않는다. [OGV 원본 Release](https://github.com/genesiskoo/joseon-assets/releases/tag/art-670-20261008-preview) — capture_master.ogv **10,239,020 bytes**, SHA256 `64fe18101b41b4f59d8d2f124681a70ca57d3dd56c6a24c79cc04389bf152d53`. 로컬 원본은 이 폴더의 capture_master.ogv에 그대로 있다.

일반 창 모드 aoe_skills_2는 62검사 PASS, 일반 focused single_flurry/single_flurry_dps는96+13검사 PASS 및 기존 종료3ObjectDB/2resources. MovieWriter 원본은96검사 PASS 뒤 종료17ObjectDB/9resources를 출력했다. 아래 원문과 전체 capture_raw.log를 보존한다. 촬영 모드 구버전 대조 결과는 아래 표에 따로 기록한다.

```text
WARNING: 17 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
ERROR: 9 resources still in use at exit (run with --verbose for details).
   at: clear (core/io/resource.cpp:822)
```

스킬 이름 3안 = 연속 베기(추천) / 몰아 베기 / 잇단 베기. 아이콘 A는 workbench/icons/670_flurry의 별도 후보이며 게임 반입 전이다. 이름·아이콘·동작은 PD 확인 대상이다.

## 촬영 모드 구버전 대조

같은 엔진·1280×720·30fps MovieWriter로 #649 코드 `7d187989`를 촬영했다. 부팅만 60프레임 실행한 경우는 기존 3ObjectDB/2resources다. 오래된 실제 대본을 따로 촬영한 결과는 다음과 같다.

| 촬영 | 대본 검사 | 종료 ObjectDB / resources | 프로세스 종료 |
|---|---:|---:|---:|
| 구버전 부팅만 | 대본 없음 | 3 / 2 | 0 |
| 구버전 aoe_skills_2 | 68 PASS | 11 / 6 | 0 |
| 이 카드 후보 | 96 PASS | 17 / 9 | 0 |

전체 원문은 `baseline_boot_raw.log`와 `baseline_scenario_raw.log`, 파일 해시는 manifest.json에 있다. 후보와 구버전은 준비한 적·자원·검사 수가 다르므로 위 개수만으로 같은 원인, 증가·감소의 원인 또는 제품 회귀를 확정하지 않는다. MovieWriter 부팅만으로 경고 증가를 설명할 수도 없다. 일반 집중 실행의 종료 3/2와 촬영 시나리오의 종료 진단을 구분해 보존한다.

처음 구버전 두 대본을 함께 촬영했을 때는 대본 2/2 PASS 뒤 PowerShell의 native stderr Stop 처리로 wrapper가 exit1을 냈고 shutdown 원문이 잘렸다. 같은 helper의 stderr 수집만 고쳐 위 두 촬영을 각각 재실행했으며, 초기 실패 원문은 게임 저장소의 `._tmp/writer_baseline_scenarios`에 별도로 보존했다. 그 불완전한 종료 로그를 합격 대조 자료로 세지 않는다.

Agent: Codex (GPT-6)
