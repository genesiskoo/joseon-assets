# #549 봉밀굴 문 열기 — 검수 후보

Cursor/grok-4.7-xhigh 구현 `1eedeaed`를 Codex가 코드·정본·실제 게임 화면으로 교차 검수했다. **미채택·미착륙 후보**이며 main의 현재 화면으로 표시하지 않는다. 세 사진은 신규 컷의 진행 상태다. 구버전과의 before/after 비교가 아니다.

| 실제 상태 | 사진 |
|---|---|
| 봉인된 문 | [01_gate_sealed.jpg](01_gate_sealed.jpg) |
| 할매와 도호의 네 줄 중 도호 2번 | [02_gate_dialogue.jpg](02_gate_dialogue.jpg) |
| 문 열림 직후 | [03_gate_opening.jpg](03_gate_opening.jpg) |

문 열림 사진은 하강을 시작한 직후다. 문이 완전히 내려갔다는 사진으로 해석하지 않는다. 이후 완전 하강·통과 가능 여부는 실행 검사로 확인했다. 현 자리의 기존 idle 초상이며 새로 착륙한 #465 정지 초상과 합친 모습은 후속 통합 검사 대상이다. 위쪽 개발 단축키 문구 잘림은 별도 #405 범위다.

독립 실행: `tools/test.ps1 -Unit` → 단위 PASS 90개·도구 자기검사 PASS 22개·전체 exit 0. `tools/test.ps1 -E2e -Scenario bongmil_walk -Windowed -Shots` → 124 PASS, 러너 자기검사 5/5, exit 0. 보스·층 1~4·조각 소모·컷 건너뛰기·열린 문 재사용 검증을 포함한다. 기존 허용 목록 종료 누수 및 look_audit 밴드 밖 9/14 출력은 원본 로그에 보존했다. '모든 경고 0'이나 최신 main 전체 검사를 주장하지 않는다.

왜 이 구조인가: CP-04 네 줄은 기존 DialogueRunner/Cut로 실행하고 Seal의 개방을 명령으로 연결한다. 할매의 컷 임시 위치·회전은 종료·실패 때 복원하므로 마을 NPC의 원위치를 바꾸지 않는다. 별도의 카메라/대화 루프를 만드는 대안은 기존 입력 잠금·Esc 건너뛰기를 이중 구현해야 하므로 쓰지 않았다. 대화 표시 실패 시 기존 문 열기 경로로 돌아간다.

JPG는 원본 PNG를 RGB·quality 82로 압축한 것뿐(1280×720, 각 300KB 이하)이다. 바이트 원본 7 PNG 및 stdout/stderr/명령/exit와 SHA-256은 joseon-assets `reports/549/2026-10-04_candidate/raw/`에 보존했다. 원본 합 4,792,946B, 개별 10MB·합 50MB 미만. `manifest.json`을 참고한다.
