# Asset Catalog

저장소 정리와 이동을 검증하기 위한 기계 생성 manifest를 보관한다.

- `assets-before-2026-06-07.csv`: 정리 전 미디어 경로·크기·SHA-256
- `assets-after-2026-06-07.csv`: 정리 후 미디어 경로·크기·SHA-256
- `moves-2026-06-07.csv`: 적용한 source → target 이동표
- `duplicates-2026-06-07.csv`: canonical과 의도적·격리 복제본 관계

CSV는 감사와 복구용이다. 직접 편집하기보다 새 정리 작업마다 날짜가 붙은 새 파일을 만든다.
