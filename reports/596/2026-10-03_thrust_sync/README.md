# #596 찌르기 준비 배분 후보 — PD 검수 전

같은 클립·무기·타격 비율0.51·길이0.633초·2.4배속. 준비구간만 시간 배분을 바꾼 후보다. Native창 anim_commit 전65/fail1(기존찌르기) → 후65/fail0. 뒤 확인은 부모#595의 실제 피해 관측 보수와 합친 자연 시계 전체 검사다. 아직 채택·main착륙·게임push 없음.

thrust_before/after: 같은 anim_commit 무대/카메라의 피해 사진. before는 코드 SHA가 일치하는595 보수 전 실제창 원본을 재사용했다. 타격 포즈 자체를 유지했으므로 정지 사진은 준비속도 차이를 보여주지 않는다. curve_before/after: 같은 축의 import클립60Hz·2.4배속 독립진단(블렌드/히트스톱 없음); 최고속0.356→0.514. 두 종류의 속도는 시간 분모가 달라 숫자를 서로 대체하지 않는다.

JPG4 <=1280폭·300KB/장. FullPNG·실패/진단 원문·실제 엔진phase·전후ModelDef·도구는 `G:/내 드라이브/JoseonHunters_raw/596/2026-10-03_thrust_sync/`에 보존. 드라이브 로컬 readback SHA만 확인, cloudsync 미확인. 기존 전후모션 형상이 변하지 않고 준비 시간만 변한 이유·기각 대안은 thrust_sync_596.md §5.

Game candidate: 0edc75a804f9c38a93e19781f5973ede01245c41. No paid generation. Game main not integrated. Four compact review images; raw104files11,213,718B preserved privately with readback SHA.
