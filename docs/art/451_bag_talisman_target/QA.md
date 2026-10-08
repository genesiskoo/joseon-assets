# #451 가방 부적 표적 모드 — 실제 게임 검수

기준: main `eaf57bc2`. 후보: `codex/451-bag-talisman-target`. 아직 main 미착륙·미push.

| 같은 구도 | 변경 전 | 변경 후 | 직접 확인 |
|---|---|---|---|
| 가방 화염부 툴팁 | bag_tooltip_before.jpg | bag_tooltip_after.jpg | 우클릭 표적 선택·확정 안내 추가, 기존 들기/벨트/버리기 안내 유지 |
| 화염부 적 겨눔 | fire_target_before.jpg | fire_target_after.jpg | 원본 금색 칸·기존 아이콘·산적 이름·월드 확정/취소 안내 |
| 빙결부 바닥 겨눔 | ice_ground_before.jpg | ice_ground_after.jpg | 원본 유지·바닥 명시·커서 미리보기, 최근접 산적 자동 겨눔 없음 |

6장 모두 실제 게임 1280×720 JPG, 각 ≤300KB. 원본 PNG·캡처 시각/SHA256·raw 로그는 joseon-assets `reports/451/2026-09-27/`에 보존한다. 변경 전은 여섯 생산 스크립트를 main `eaf57bc2` 내용으로 실행한 캡처이며, 후보 스크립트는 SHA256으로 바이트 단위 복원을 확인했다. 기존 엔진 렌더·UiSkin·궁서 제목/본문 폰트·승인된 아이콘을 사용했다. 새 원화/유료 생성/모델·애니·밸런스 변경 없음.

`talisman_targeting` 실제 입력 headless·창모드 각각 73검사 PASS. 선택과 확인을 분리해 가방 원본을 유지하고, 선택/무효 클릭/취소/버퍼 대기에서 소비하지 않는다. 시전 몸짓 시작 때 한 장 소비·도력0·벨트와 공용쿨1초. 가방에는 부적 아끼기를 적용하지 않는다(item_system_v2 §7.4). 무효 바닥/NPC 클릭·오래 누른 좌/우 버튼의 이동/공격 누수0, 원본 이동/적 해제/불러오기/새 판 버퍼 재검증, I/X/Esc/벨트/마을/사망/판매를 확인했다.

최종 검수: 단위 53종, 설정 재실행 2단계, Godot 도구 자기검사 4종, Python 도구 자기검사 10종 PASS. 러너 판정 자기검사 5/5와 전체 E2E **98/98종·5256검사 PASS**. 별도 실제 입력 headless/창모드 각각 73검사 PASS. 최종 raw 로그의 SCRIPT ERROR/ERROR 0. 검수 후 주요 코드·대본 8파일의 SHA256/Git blob 보존을 확인했다. 이후 커밋 공백 검사에서 대본의 마지막 빈 줄 하나만 제거했으며, 전후 해시는 `post_validation_whitespace.json`에 기록했다. 실행 코드 변경 없음.

원본 결과: `reports/451/2026-09-27/451_unit_100554.log`, `451_all_100757.log`, `451_target_100522.log`, `451_windowed_100656.log`; 기계 판정/해시/시나리오별 검사 수는 같은 폴더 `verification.json`. 러너/카메라 무대 보정의 초기 실패도 `initial_runner_output.txt`·`451_target_100315.log`로 보존한다. 사양: `docs/design/bag_talisman_target_451.md`. PD 「합쳐」 뒤 main 착륙.
