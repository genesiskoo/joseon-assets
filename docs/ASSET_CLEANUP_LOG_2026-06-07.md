# Asset Cleanup Log — 2026-06-07

## 목적

승인된 공식 자산, 생성 후보, 화풍 프로브, API 테스트, 외부 레퍼런스와 배포 복제본이 같은 폴더에 섞인 상태를 정리했다.

## 안전 원칙

- `landing/`과 `2026/`는 공개 URL이 사용 중이므로 이동하거나 삭제하지 않았다.
- `C:\workspace\joseon\assets`는 수정하지 않았다.
- 공식 `concept/`, `sheets/`, `sprites/`, `maps/`, `magazine/`, `video/` 자산은 테스트 파일을 제외하고 유지했다.
- 중복 파일은 삭제하지 않고 `archive/duplicates/`에 격리했다.
- 정리 전후 SHA-256 manifest와 전체 이동표를 남겼다.

## 조사 결과

- 정리 전 스냅샷: 미디어 165개, `270,966,696` bytes
- 초기 조사 기준 완전 중복: 12그룹, 추가 복제본 13개
- 완전 중복 정리 시 잠재 회수량: 약 `34.22MB`
- `tools/.venv`: 1,323개 파일, 약 `29.34MB`
- `tools/rd-api-examples` 안에는 별도 `.git`과 로컬 가상환경이 있으나 이번 정리에서는 실행 환경 보존을 위해 이동하지 않았다.

## 적용한 구조

```text
inbox/                  새 파일 단기 드롭존
workbench/
  candidates/           미승인 생성 후보
  probes/               화풍·맵·구도 비교 실험
  smoke-tests/          API 연결과 최소 생성 검증
  tests/                제작 테스트 파일
archive/
  duplicates/exact/     SHA-256 완전 중복
  duplicates/variants/  이름은 중복이나 내용이 다른 변형
reference/
  internal/             프로젝트 내부 참고 자료
  external/unclassified 외부 수집·미분류 자료
catalog/                스냅샷·이동표·중복 관계
```

## 주요 이동

- `concept/probe/` → `workbench/probes/gpt-image2/legacy-numbered-batch/`
- 정리 중 발견한 GPT Image 2 맵·화풍 테스트 → `workbench/probes/gpt-image2/*-tests-2026-06-07/`
- PixelLab/RD 비교 생성 → `workbench/smoke-tests/2026-06-07/generation-comparison/`
- RD 약초상 NPC 후보 → `workbench/candidates/npc/herbalist-rd-plus-2026-06-07/`
- 도호 테스트 스프라이트와 Aseprite → `workbench/tests/sprites/doho/`
- RD API 예제 출력 → `workbench/smoke-tests/2026-06-07/rd-api-example/`
- 외부 해시명 JPG 30개 → `reference/external/unclassified/`
- 프로젝트 UI·스프라이트 참고 자료 → `reference/internal/`
- 검증된 완전 중복과 변형본 → `archive/duplicates/`

전체 59건의 상세 source/target은 `catalog/moves-2026-06-07.csv`에 있다.

## 유지한 의도적 복제

다음은 완전 중복이지만 공개 경로를 유지하기 위해 보존했다.

- `landing/art/` 랜딩 페이지 의존 파일
- `2026/06/` SNS raw URL 의존 파일

canonical 관계는 `catalog/duplicates-2026-06-07.csv`에 기록했다.

## 정리 중 발견 사항

초기 디렉터리 조사 후 `inbox/concept-art/`의 GPT Image 2 테스트 12개 파일을 발견했다. 해당 파일은 정리 전 manifest에 포함되어 있었으며, 삭제하지 않고 prompt 문서와 함께 `workbench/probes/gpt-image2/`로 편입했다.

## 최종 검증

- 정리 전 미디어 파일: 165개, `270,966,696` bytes
- 정리 후 미디어 파일: 165개, `270,966,696` bytes
- 정리 전 해시가 정리 후 사라진 그룹: 0개
- 기록된 이동: 59건
- 파일 삭제: 없음
- `inbox/concept-art/` 테스트 결과: PNG 10개와 prompt 문서 2개, 모두 `workbench/probes/`로 이동
- PNG/JPG 디코딩 검사: 160개 중 실패 0개
- 운영 문서와 스크립트 1,513개에서 이전 경로 참조 검사: 0건
- `inbox/`에는 사용 규칙을 설명하는 `README.md`만 유지

## 후속 작업

1. `reference/external/unclassified/` 30개에 의미 있는 이름·출처·라이선스 태그를 부여한다.
2. `archive/duplicates/exact/` 삭제는 별도 승인 후 진행한다.
3. `tools/.venv`와 중첩 `.git`은 필요 시 저장소 밖 캐시로 이전한다.
4. 공식 승격 자동화를 만들 때는 dry-run과 SHA-256 검증을 기본으로 한다.
