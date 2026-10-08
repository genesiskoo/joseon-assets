# #596 찌르기 준비 배분 후보 — PD 검수 전

같은 클립·무기·타격 비율0.51·길이0.633초·2.4배속. 준비구간만 시간 배분을 바꾼 후보다. Native창 anim_commit 전65/fail1(기존찌르기) → 후65/fail0. 뒤 확인은 부모#595의 실제 피해 관측 보수와 합친 자연 시계 전체 검사다. 아직 채택·main착륙·게임push 없음.

thrust_before/after: 같은 anim_commit 무대/카메라의 피해 사진. before는 코드 SHA가 일치하는595 보수 전 실제창 원본을 재사용했다. 타격 포즈 자체를 유지했으므로 정지 사진은 준비속도 차이를 보여주지 않는다. curve_before/after: 같은 축의 import클립60Hz·2.4배속 독립진단(블렌드/히트스톱 없음); 최고속0.356→0.514. 두 종류의 속도는 시간 분모가 달라 숫자를 서로 대체하지 않는다.

JPG4 <=1280폭·300KB/장. FullPNG·실패/진단 원문·실제 엔진phase·전후ModelDef·도구는 `G:/내 드라이브/JoseonHunters_raw/596/2026-10-03_thrust_sync/`에 보존. 드라이브 로컬 readback SHA만 확인, cloudsync 미확인. 기존 전후모션 형상이 변하지 않고 준비 시간만 변한 이유·기각 대안은 thrust_sync_596.md §5.

시계595/관측 보수를 결합한 후보 `e42f139a`의 자연focused2회 각30·전체 `121/121 PASS`·실제창65/65도 확인했다. thrust_after는 그 최신 실제 창으로 갱신(같은 시나리오/카메라, main의 승인 그림자·스킬 아이콘 포함); 기존 before와 두 곡선은 원본 그대로다. 원문과 최초 after는 드라이브에 보존, 부모536 미완료·최종채택/착륙 전이다.

Review commit 1b53c98729181a4c2773dcec7cd960df055b120d; tested runtime e42f139a0b7a0cfaaf2e40826f06088429dee75f. Natural focused2 ×30, full121/121, native65. Candidate only; PD adoption/game main/game push pending. Raw/failed attempts privately retained.
