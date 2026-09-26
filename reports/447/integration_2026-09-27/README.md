# #447 게임 반입 검수 — 2026-09-27

제작 #446 f7483c3556cb94c416454fc51bf8140b8655fe07은 PD 「병합 다음」 승인 뒤 assets main에 fast-forward했다. 여기는 그 다음 별도 게임 반입 카드 #447의 검수 기록이다. 게임 기준 ed0fd67d, 자리293/393을 재사용한다.

- 8상태×전후 PNG16: 기존 #439 물체/held/스킬3트리 및 T1 가방/held/좌판+인장 툴팁.
- T1 전후 JPG6: 1280폭·300KB 이하, 게임 docs/art/447_d1_icons_intake에도 정확 복사.
- captures_before/after.json: 실제 user:// 파일과 캡처 SHA-256/크기/mtime.
- intake_manifest.json·verification.json: 승인 PNG6/기존439 PNG17 해시, 알파/점유, 다른 ItemDef 필드 보존, 승인 기준물체3의 동일 픽셀.
- 447_before.log/errors.log: 직접 창 모드 기준 캡처 stdout/stderr, 58검사 PASS·stderr0.
- 447_after.log: test.ps1 창 모드 E2E8종374검사·자기검사5/5 PASS; stdout/stderr 합본.
- 447_unit.log: test.ps1 전체 단위 및 도구 층 결과, stdout/stderr 합본.
- 447_import_after.log·447_site_gate.log: 반입 임포트와 부팅/자기검사.
- tools/: 실제 사용한 반입·사진 축소·해시/픽셀 검증 스크립트. 상태 경로가 이 검수 자리에 고정되어 있으므로 재실행은 목적을 확인한 뒤 한다.

모든 입력은 E2e의 표식 있는 InputEvent다. 기본 ItemDef는 icon 선언 외 수치/점유/요구치/가격/드랍 필드가 보존된다. 테스트가 만든 매직 피주·미식별 인장·재고는 ItemInstance 표본이며 제품 데이터를 바꾸지 않는다. 인장 툴팁은 텍스트 전용; 실제 그림은 가방·장비·held·좌판에서 판정한다.
