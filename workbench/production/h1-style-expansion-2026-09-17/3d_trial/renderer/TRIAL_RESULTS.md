# H1 독립 3D 시험 · 2026-09-17

실제 H1 도호·상인 GLB, 24본 리그, 기존 게임 idle/walk/attack 3클립을 제작했다. **그립 교정·3클립/재질 보존·기술 검사는 통과했으며, 최종 시각 승인과 메인 게임 반입은 보류**다. 손끝 조형의 거침, 도포 겹침, 계약 예산, 상인 얼굴/신발 해석과 전투형 idle이 남아 있다.

결과 루트: `C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/`.

| 결과 | 도호 | 김 영감 |
|---|---|---|
| root 후보 파일 | `H1_doho.glb` | `H1_merchant.glb` |
| 높이 / 삼각형 / 본 | 1.70m / 10,827 / 24 | 1.60m / 10,620 / 24 |
| 텍스처 | 2,048×2,048 | 2,048×2,048, retexture 1회 |
| 클립 | idle 1.88s / walk 1.08s / attack 1.54s | 같음. NPC 동작은 기술 시험용 |
| 수치 검수 | RESULT PASS | RESULT PASS |

### 계약 예산과 기술 PASS는 별개

`docs/design/art_3d_pipeline.md §2.1`의 정본은 **도호≤12k / NPC≤8k / 텍스처≤1024²**다. 도호 폴리만 이 예산 안에 들어가며, **상인 10,620 tri는 8k보다 2,620(32.75%) 많고 양쪽 2K는 1K 제한을 초과한다**. `model_check`는 공통 12k 경고값을 사용하고 텍스처 상한을 강제하지 않으므로 RESULT PASS가 계약 예산 합격을 뜻하지 않는다.

후반 §4의 이미지 경로는 target11k로 적혀 있고 §10~11에는 도호 11k/2K 실측 기록이 있으나, NPC 8k·텍스처1K를 영구 해제하는 예외는 명시되어 있지 않다. 이번 **11k 발주·2K는 부모가 지정한 소규모 시험 규격**이다. 실제 반입 전 예산에 맞춘 최적화 또는 명시적 계약 변경이 필요하다. 추가 유료 remesh/리깅은 하지 않았다.

현재 `data/models/merchant.tres`와 pipeline §3의 김 영감 목표 키는 **1.5m**다. 이번 후보 **1.6m**는 부모의 명시 시험 지시 `NPCheight1.6`을 따른 값으로 현행보다 0.1m(6.67%) 크며, 메인 ModelDef는 그대로다. 최종 높이 승인과 정체성 합격을 따로 받아야 한다. 도호도 시험 요구인 3동작만 적용했으므로 §2.2의 5종 전체 계약(hit/die 포함)은 아직 충족하지 않는다.

도호 프록시 검은 GLB에 합치지 않고 현재 `ActorVisual`의 `BoneAttachment3D`로 별도 배치한다. 검 포함 런타임 삼각형은 11,619다. 기존 `rig_fix.py --fist`를 적용해 손가락 본 없이 손 정점을 말고, 실제 손아귀 JSON으로 소켓을 계산했다. 초기 열린 손/GT1 임시 소켓은 `pre_fist/`와 이전 캡처에만 남겼다.

### 주먹 교정과 데이터 보존

- 현재 helper를 독립 프로젝트에 그대로 복사해 `--fist=both --palm=down`을 실행했다. 치마·허리끈·머리 재웨이트는 임계값으로 제외하여 모두 0건이다. 오른손 finger90/별도 thumb0, 왼손 finger80/thumb14가 선택됐다. 오른손 thumb0은 이 형상에서 helper의 엄지 분리 임계값에 잡힌 정점이 없다는 뜻이다.
- Blender 전체 재출력은 JPEG 재인코딩과 클립 끝에 1/24초 추가를 동반했다. 이 출력은 `fist/H1_doho_fist.glb`에 진단용으로 보존하고, **최종판에는 helper가 바꾼 손 위치 180개와 주변 normal262개만 원래 GLB에 적용**했다. 접힌 손의 normal seam에만 12정점을 복제했다. 삼각형10,827/24본은 그대로이며 모든 삼각형의 winding-normal 정합을 확인했다.
- 최종 재질·이미지·원래 스킨/클립 버퍼, nodes/skins/animations JSON을 보존했다. idle1.875 / walk1.083333 / attack1.541667초도 동일하다. 증명은 `fist/H1_doho_preserved.glb.fist-transfer.json`이다.
- `weapon_socket.gd` 결과: **pos=(0.0053,0.0703,0.0260), rot_deg=(1.80,-174.82,97.77)**. RightHand 기준 왕복 검산은 원점0.0000m/칼끝0.00°. `fist/H1_doho_fist_fist.json`과 `fist/H1_doho_socket.json`을 실제 분리검 담당에게 전달했고 같은 최종 모델로 검 소켓을 연동했다.
- idle/walk/attack 각각 12·45·78% 시점에서 손잡이 접촉과 검 방향 개선을 확인했다. 확대 시 손끝의 거친 모서리, walk 후반의 도포/몸 가림은 남아 있어 **모든 자세의 손가락 접촉·옷 충돌까지 시각 합격한 것은 아니다**. 손가락 본 부재를 교정 불가 사유로 삼지 않는다.

최종 도호 SHA256은 `E5FEA5C6383180D1369D5F1975F804C4F3A2DD70A608918E26593D94C2511749`, 수정 전 SHA256은 `AEEDB3148D40492614106F02DEA9E818B54BE01E6D2DC3271B316CE4676B25CE`다. 상인 GLB는 주먹 작업에서 변경하지 않았다. 로컬 후처리의 추가 비용은 **0 credits**다.

## 비용과 시도

| 작업 | 횟수 | 결과 | credits |
|---|---:|---|---:|
| 최초 multi-image 생성 | 2 | 둘 다 service_unavailable, FAILED | 0 |
| 명시 승인 후 동일 입력 재시도 | 2 | 둘 다 SUCCEEDED | 60 |
| Meshy 리깅 | 2 | 둘 다 SUCCEEDED | 10 |
| 상인 텍스트 기반 retexture | 1 | SUCCEEDED | 10 |
| 합계 | | 잔액 **2623 → 2543** | **80** |

`task_ledger.json`에 실제 task ID·응답 파일·비용·승인 경과를 기록한다. `input_manifest.json`은 최초 요청 당시 기록이며, 최초 실패 후 추가 승인된 1회 재시도는 ledger에 구분한다. 생성 원본 네 장의 SHA256을 보존했다.

상인 이미지를 새로 전송하는 retexture 요청은 자동 승인 심사에서 실행 전 거절되었다. 이후 계획 승인·기전송된 가공 캐릭터 근거를 확인하고 **새 이미지/파일/URL 없이 기존 task ID와 텍스트만 보내는 별도 요청**이 심사를 통과했다. 거절된 이미지 방식은 실행되지 않았고 비용도 발생하지 않았다.

## 검수 결과

- `captures/fist_final_baseline/`: 최종 주먹/소켓판. 실제 게임 camera **ortho11 / pitch35.264 / yaw45 / distance30**, 실제 던전 Environment·플레이어 반경광·횃불을 복제한 1280×720 캡처 9장. 상인은 idle, 도호는 idle/walk/attack 각각 3시점. 게임 전투/충돌 통합 시험은 아니다.
- `captures/fist_final_neutral/`: 최종 근접 중립 조명 **ortho3.3 / pitch10**, 시각 결함 확인용 9장. 게임광 판정과 분리한다.
- `captures/fist_final_grip/`: 최종 손 확대 **ortho0.5**, 손을 따라가는 진단 카메라 9장. 기본광 합격 판정용이 아니다.
- `captures/final_baseline/`, `final_neutral/`: 주먹 교정 전 보존판. `fist_grip/`, `fist_neutral/`은 Blender 전체 재출력 중간 후보이며 최종판은 위 `fist_final_*` 세 묶음이다.
- `captures/pc_matte_candidate/`, `pc_matte_fill_candidate/`: 도호만 metallic0·roughness0.8, 선택적으로 PC 레이어에만 energy0.65/range3 국소광을 추가한 비교 후보. 전체광·NPC·바닥은 올리지 않았다. 이 두 판의 상인은 retexture 전 상태다.
- `captures/diagnostic_raw_{neutral,unshaded,solid,nearest}/`: 검은 파편 원인 분리. 상인의 얼룩은 unshaded/nearest에도 남고 텍스처 제거 시 사라졌다. 새 Meshy 원형의 모든 삼각형은 winding과 normal이 일치한다.
- `captures/retexture_{neutral,unshaded}/`: retexture 후 소매·바지의 큰 검은 파편 제거. 얼굴 묘사 단순화·신발/허리 색 해석 변화는 정체성 승인 보류 사유다.

`clip_sampling_gate_passed`는 요청된 클립을 샘플링할 수 있다는 뜻이다. **`animation_visual_qa_status`는 별도 미승인**이며 기술 PASS를 시각 합격으로 바꾸지 않는다. 초기 탐색 캡처의 `animation_gate_passed`도 클립 가용성 의미였고 최종 보고서에서는 혼동을 없앴다.

### 재질과 winding 진단

raw Meshy는 metallic0 / roughness0.8 / emission0다. **Meshy 리깅 출력은 albedo를 emission에도 연결해 emission1·metallic1·roughness1로 바뀐다.** 현재 게임 도호 GLB도 같은 조건이다. 최종 기본판은 리깅 재질을 보존했으며 전체광 변경으로 어두움을 숨기지 않았다.

기존 게임 floor/wall은 GLB CCW 인덱스와 normal의 내적이 각각 **12/12, 20/20 음수**다. two-sided만 켜면 면은 나타나지만 검다. `_flipped_winding_mesh`가 런타임 복제 메시의 각 triangle index1/index2만 교환하면 표면과 조명이 정상화된다. 원본 GLB·텍스처·계단은 바꾸지 않았다. 최종 캡처 HUD와 report에 `RUNTIME WINDING FLIP` 진단임을 표시한다. 메인 게임은 이 수정이 적용된 상태가 아니다.

### 상인 텍스처 연결

retexture 결과와 원형의 **POSITION·indices·UV가 바이트 동일**함을 확인했다. normal 바이트는 달라졌으나 사용하지 않았다. `apply_retexture.mjs`는 새 albedo만 기존 24본/3클립 모델에 연결하고 원래 형상·normal·skin·animation 버퍼를 그대로 보존한다. 증명 파일은 `models/H1_merchant_retextured.glb.texture-transfer.json`. 감사용 이전 이미지 바이트를 GLB 안에 보존하여 상인 후보는 약10.2MB이며, 실제 반입 전 불필요 데이터 제거가 가능하다.

## 재현

`renderer/`는 독립 Godot 프로젝트 스냅샷이다. 주 프로젝트 에디터·Blender를 종료하거나 수정할 필요가 없다.

```powershell
godot --headless --path C:/workspace/joseon/tmp/h1_3d_trial --editor --import --quit
& ./tmp/h1_3d_trial/capture_trial.ps1 -Mode h1_trial -Doho C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/H1_doho.glb -Merchant C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/H1_merchant.glb -SwordProxy -Socket C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17/3d_trial/fist/H1_doho_socket.json -TilesFlipWinding -Output C:/workspace/joseon/tmp/h1_3d_trial/captures/review
```

별도 실행은 `Start-Process -WindowStyle Hidden`을 사용하고 자신의 프로세스만 기다린다. `capture_trial.ps1`은 exit code 외에도 raw stderr의 SCRIPT ERROR/ERROR와 report 생성 여부를 검사한다.

`references/CURRENT_REFERENCE_NOT_H1.glb`는 기존 게임 모델의 불변 시험 사본이다. H1 결과로 세지 않는다. `references/source_fingerprints.json`은 실제 카메라/광원/도구/석실 자산의 원본 해시를 기록한다.

기존 게임의 카메라·ActorVisual·ModelDef·리타겟 코드를 독립 프로젝트에 스냅샷해 비교 조건을 맞췄다. 별도 간이 렌더러를 쓰면 Godot의 재질·스킨·검 소켓 처리가 달라지므로 재사용 구조를 선택했다. 독립 리타겟 도구에만 `file.glb#clip` 선택 기능을 추가했으며, 기존 posture/yaw 보정이 들어간 현행 게임 클립을 그대로 소스로 사용했다.

Meshy 요청은 공식 MCP0.5.1로 실행했다. rigging download는 공식 서버가 `save_to` 대신 서명 URL만 반환해, 그 URL의 **GLB만** `download_rigged.mjs`로 내려받고 해시를 기록했다. 재텍스처 입력 규격은 [공식 Meshy 문서](https://docs.meshy.ai/en/api/retexture)를 확인했다. 추가 생성·리깅·retexture 재시도는 수행하지 않았다.

### 공유 응답의 임시 서명 제거

성공 응답 사본 10개에서 임시 다운로드 URL의 서명 쿼리를 `[REDACTED_TEMPORARY_DOWNLOAD_QUERY]`로 제거했다. `content.text` 안에 중첩된 JSON도 처리했고 URL 기본 경로·task ID·status·raw 오류 메시지는 보존했다. 응답24개/요청17개를 검사해 서명 쿼리·Bearer 값·API키 값·data URI가 남은 파일은 각각 0개다. `response_redaction.json`은 파일별 원본/정리 후 SHA256과 정리된 응답 hash manifest를 기록한다.

원 실행 응답은 메인 저장소의 `tmp/h1_3d_trial/private_original_responses/`에만 보관하며 이 폴더의 `.gitignore`가 모든 내용을 제외한다. 외부 아트 패키지에는 포함하지 않는다. 생성 입력 네 장과 메인 게임 원본의 SHA 검증은 응답 정리로 변경된 SHA와 **별도 기록**이다. 재현은 보존된 로컬 GLB/PNG와 SHA를 사용한다.
