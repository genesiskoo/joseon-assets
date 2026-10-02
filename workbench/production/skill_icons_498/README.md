# #498 신규 스킬 아이콘 후보 패킹

정사각 1024px Comfy 원본 10장과 기록된 보완 4장을 보존한다. 읽기 검수 후 부적 진·칼바람·조식·부적 주머니만 보완본을 골라 `game/<id>.png` 128×128 RGBA 후보로 축소한다. 축소는 전체 그림의 Lanczos 한 번이며 크롭·알파 제거·색 보정·새 그림은 없다. 이 폴더는 미승인 후보이며 게임 반입은 0종이다.

검수 화면은 독립 `qa/project.godot`에서 기존 승인 참격·돌진 베기·회오리 3종을 신규10종 옆에 둔다. 원화 전체128, 이미지30/48/60, HUD30(여백3)/60(여백5), 스킬창48(여백3)을 구분해 표시한다. 4보완의 before/after는 `revisions` 한 장 안에서 같은 슬롯·같은 크기로 비교한다. 나머지6장은 이 변경 비교에 섞지 않는다.

왜 이 구조인가: 게임에 반입하기 전 원본/후보/렌더를 분리하면 실제 SkillDef와 저장파일을 바꾸지 않고 기능과 작은 크기의 읽기를 검수할 수 있다. 게임을 직접 실행하거나 UI를 새로 흉내 내는 대안 대신, 독립 Godot 프로젝트에 현재 `UiSkin`과 슬롯 PNG를 바이트 그대로 보존해 쓰며 그림은 메모리에만 등록한다. 사용 폰트는 Windows의 Malgun Gothic이며 게임의 UI 폰트 재현은 목적이 아니다.

```powershell
python workbench/production/skill_icons_498/pack_candidates.py --game-root C:/workspace/joseon
python workbench/production/skill_icons_498/pack_candidates.py --check
godot --headless --path workbench/production/skill_icons_498/qa --import --log-file C:/workspace/joseon/._tmp/assets_498/reports/498/native_qa/import.raw.log
godot --headless --path workbench/production/skill_icons_498/qa -s res://qa_godot.gd --log-file C:/workspace/joseon/._tmp/assets_498/reports/498/native_qa/verify.raw.log -- --verify-only
```

Native 캡처는 지휘 세션이 창 모드로 실행한다. `--mode`에 `overview`, `sizes_a`, `sizes_b`, `revisions`를 차례로 지정한다. 화면은 1280×720이며 캡처 후 종료한다. 출력은 `reports/498/native_qa/native_<mode>.png`; 마지막 줄의 PASS와 실제 파일을 함께 확인한다.

```powershell
godot --path C:/workspace/joseon/._tmp/assets_498/workbench/production/skill_icons_498/qa -s res://qa_godot.gd --log-file C:/workspace/joseon/._tmp/assets_498/reports/498/native_qa/capture_revisions.raw.log -- --mode=revisions
python workbench/production/skill_icons_498/pack_candidates.py --compress-native
```

`--compress-native`는 Native PNG를 폭1280·JPG≤300KB로만 압축한다. 원본 PNG는 유지한다. 게임 프로젝트에 중첩되더라도 `qa/project.godot` 표식 때문에 QA 스크립트가 본 프로젝트에 들어가지 않는다. `user://`도 별도 이름으로 고립되어 게임 세이브를 쓰지 않는다.

`manifest.json`은 선택본·원본14장·요청ID·프롬프트·참조SHA·패킹SHA·기존승인3종·UI 스냅샷을 연결한다. `visual_review.json`은 사람의 읽기 판정과 남은 유보점을 기록한다. 정량 무결성 결과는 `reports/498/packing_qa.json`이다. Native 렌더 검수와 PD 최종 채택은 별도 단계다.
