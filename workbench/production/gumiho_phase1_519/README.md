# #519 구미호 1페이즈 — R4 구조 확장 후보

PD가 채택한 C 주막 안주인의 눈빛·P1 복식·P5 낮은 인간형 자세와 P3 접객 보조 연출을 유지한다. Comfy Cloud GPT Image 2.5 Flare로 정면/후면/측면/낮은 자세/도호 2샷을 전개했다. 새 R4 선택 5장은 **candidate_pending_pd**다. 모델링·리깅·게임 반입·main 착륙은 미완료이며, 기존 선택 기록 `reports/519/gpt_model_selection_2026_10_01.json`을 수정하지 않았다.

실제 생성 계획은 [batch_R4.json](batch_R4.json), 새 선택 목록과 원본 SHA는 [structural_selection_R4.json](structural_selection_R4.json)이다. 원본 PNG·프롬프트·API 그래프·성공 history·job 기록은 `reports/519/batch_R4_structure/`에 8작업 그대로 보존한다. reference PNG와 작업 기록의 SHA를 대조했으며, 시드·참조·프롬프트가 같아도 서비스의 결정적 재현은 보장하지 않는다.

| 선택 원본 | 확인된 범위 | 남은 한계 |
|---|---|---|
| `R4_front_v2.png` | 화면 왼쪽 4 + 오른쪽 5 = 꼬리 끝 9, 인간 손 2·발 2 | 개별 뿌리 부착은 이 뷰에서 검증하지 못함 |
| `R4_rear.png` | 끝 9, 허리 아래 뿌리군, 인간 손 2·발 2 | 각 9부착점의 독립 분리는 미확정 |
| `R4_side.png` | 복식·관절의 측면, 인간 손 2·발 2 | 끝 6만 노출되므로 9꼬리 독립 증명이 아님 |
| `R4_low_v2.png` | 화면 왼쪽 4 + 오른쪽 5 = 끝 9, 인간 손 2, 앞 발 1 | 뒤 발은 치마 아래 가려져 양발을 확인했다고 판정하지 않음 |
| `R4_duo_v2.png` | 화면 왼쪽 4 + 오른쪽 5 = 끝 9, 구미호 손 2·발 2, H1 도호와 톤/비례 대조 | 실제 인게임 아이소 크기의 검수가 아님 |

최초 `R4_front.png`·`R4_low.png`·`R4_duo.png`는 끝 10개 오류로 기각했다. 이 세 원본과 생성 기록도 유지한다. 정면 보정 전후는 같은 배치에 전신을 잘리지 않게 놓은 검수판으로 비교한다. 원화 사이의 형상·관절은 CAD처럼 정확히 일치하지 않는다. 개별 9뿌리와 부착, 관절 정합, 복식/꼬리 리깅·충돌, 실제 아이소 판독은 후속 3D 단계에서 확인해야 한다.

검수 결과는 `reports/519/batch_R4_structure/structural_review_R4.json`, JPG 6장은 같은 폴더의 `review/`와 game `docs/art/519_gumiho_phase1/`에 있다. 폭 1280 이하·각 300KB 이하로 원본을 비율 유지해 축소했고 설명은 검수판 밖에 배치했다. 이미지 픽셀에 꼬리나 인체를 추가하지 않았다.

보존/검증 기록은 다음과 같다.

- `raw_preservation_R4.json`: 기존 PNG/API/job **88기록**의 원래 Git blob 및 raw SHA와 새 8작업의 원본/응답/프롬프트/history SHA. 요청 범위 86보다 넓은 실제 추적 목록 88을 모두 보존했다.
- `git_blob_verification_R4.json`: 기존 원본 88·새 raw 40·옛 갤러리/문서 10·입력 PNG 4·두 저장소 JPG 각 6·보호된 선택 기록 2, 합계 156파일의 raw SHA와 Git blob SHA를 따로 기록한다. 커밋 후 `python reports/519/batch_R4_structure/verify_git_blobs_R4.py --game <game 작업 트리 절대 경로>`로 HEAD와 대조한다. Git의 텍스트 줄끝 필터가 있으면 raw/Git SHA 차이를 명시하며 원본이 바뀐 것으로 오인하지 않는다.
- `credential_audit_R4.json`: 텍스트/JSON과 PNG 원시 바이트·디코딩된 metadata를 검사했다. 로컬 자격 증명 값은 메모리에서만 대조하며 출력·기록하지 않는다.
- `reports/519/archive_game_previews_before_R4/preservation.json`: 기존 game JPG 6장과 당시 문서 4개를 바이트 그대로 보관하고 SHA를 대조했다. 당시 main은 이 갤러리를 추적하지 않았으므로 main 파일을 삭제하지 않았다. 이전 game Git `4e2ccbc5655fe9c2182cb6a26cd3df89ea3fd398`에도 같은 후보가 남아 있다.
- 재검증/패키징: `python reports/519/batch_R4_structure/package_review_R4.py --game <card519 game 작업 트리 절대 경로>`.

왜 이 구성인가: 앞·뒤·옆의 복식과 뿌리 참고, 낮은 전투 자세, 도호와의 대조를 함께 두면 인간형 연속성과 남은 3D 문제를 구분할 수 있다. 끝 9개만 보고 부착/관절 정합이나 리깅 완료까지 확정하는 대안은 원화가 입증하는 범위를 넘어가므로 기각한다. 기존 모델별 카탈로그와 R3 원본/기각 이력은 아카이브와 이전 Git 기록에서 계속 확인할 수 있다.
