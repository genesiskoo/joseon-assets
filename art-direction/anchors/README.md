# Anchor Policy

앵커 이미지는 이 폴더에 복제하지 않는다. 중복 이미지가 늘어나면 어떤 파일이 승인본인지 흐려지기 때문이다.

대신 `art-direction/manifests/reference-sets.yaml`에서 기존 공식 경로를 참조한다.

- style anchor: `concept/`, `workbench/probes/`의 승인 후보 중 선택
- character anchor: `sheets/`의 캐릭터 ref sheet 또는 승인된 `concept/` 이미지
- environment anchor: `maps/`, `concept/`, `workbench/probes/`의 지역별 승인 후보
- prop anchor: `sprites/`, `maps/`, `workbench/candidates/`의 승인 후보

새 앵커 후보는 먼저 `workbench/`에 두고 리뷰 후 manifest에 추가한다. 공식 승격 전에는 `approved: false`를 유지한다.
