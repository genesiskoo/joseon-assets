# 조선헌터스 SNS 마케팅 소재 · 2026-10-14

현 게임 영상 14개, 무UI 4K 스크린샷 16장, 가방·물건 UI 3장, 못골 일상 대화 4장, 기존 공개 확정 아트 8장을 모았습니다. [그림 갤러리](gallery.html) · [파일 대응표](manifest.csv) · [메타데이터](manifest.json) · [검증 결과](validation.json) · [ZIP SHA256](SHA256SUMS.txt) · [GitHub 업로드 해시 대조](upload_validation.json) · [아트 Git blob 대조](art_blob_verification.json).

## 원본 다운로드

| 묶음 | 소재 수 | ZIP 바이트 |
|---|---:|---:|
| [joseon-hunters-2026-10-14-images.zip](https://github.com/genesiskoo/joseon-assets/releases/download/marketing-2026-10-14/joseon-hunters-2026-10-14-images.zip) | 31 | 165,370,484 |
| [joseon-hunters-2026-10-14-video-ui-off.zip](https://github.com/genesiskoo/joseon-assets/releases/download/marketing-2026-10-14/joseon-hunters-2026-10-14-video-ui-off.zip) | 7 | 62,291,420 |
| [joseon-hunters-2026-10-14-video-ui-on.zip](https://github.com/genesiskoo/joseon-assets/releases/download/marketing-2026-10-14/joseon-hunters-2026-10-14-video-ui-on.zip) | 7 | 59,958,454 |
| [joseon-hunters-2026-10-14-qa.zip](https://github.com/genesiskoo/joseon-assets/releases/download/marketing-2026-10-14/joseon-hunters-2026-10-14-qa.zip) | 0 | 180,084 |

ZIP 내부 경로는 `marketing/2026-10-14/`입니다. 저장소에는 최대 1280 폭·300KB 이하 JPG 미리보기와 인덱스를 둡니다. PNG/JPG 원본의 해상도·투명도·바이트는 보존했습니다. 개별 파일과 ZIP의 SHA256은 manifest와 SHA256SUMS에 있습니다.

## 먼저 꺼내 쓸 소재

| 용도 | 소재 | 공개 등급 |
|---|---|---|
| 전투 릴스·짧은 클립 | 현 게임 MP4 UI on/off, 1920×1080·60fps·게임 소리 | 각 파일 manifest 확인 |
| 마을·세계관 이미지 | 현 게임 무UI 4K 장면·못골 타이틀 배경 | 각 파일 manifest 확인 |
| 인물·대화 캐러셀 | 김 영감·무당 할매·촌장·주모의 일상 인사 | none |
| 장비 UI 소개 | 물건 상세창·가락지 비교 | none |
| 키 비주얼·제목 카드 | 키 비주얼·갈필·농묵 브랜드 마스터·한글 로고 | none |
| 도호 소개 | 투명 PNG 기본·능청 초상 | none |

새 영상·4K 캡처의 게임 원본은 `072fd76c`입니다. 효과 트랙은 **현재 게임의 고정 표적 효과 시연**, 던전 트랙은 **촬영용 준비·자동 조작**으로 구분합니다. Godot 고정 프레임 촬영이므로 실시간 성능 측정값으로 쓰지 않습니다. 불·한기·벼락은 무기·부적 속성 타격 소개에 쓰세요. 대표 이미지에는 불·한기·벼락 타격 컷을 우선 추천하며, 어두운 조우·연속 베기·치명타 순간 사진은 파일별 편집 메모를 따라 보충 자료로 선택하세요.

UI 세 장은 #781 최종 가방 UI 검수 촬영입니다. 시험용 긴 물건 이름·장비 상태·스크롤 위치가 들어 있어 기능 소개에 적합합니다. 대화 네 장은 #777의 정상 인사 화면이며 이미지에 담긴 한 줄을 직접 읽어 none으로 판정했습니다. 기존 검수 사진의 원래 촬영 commit은 미기록으로 `source_commit: null`을 유지하고, evidence가 착륙한 commit을 `source_context_commit`에 따로 적었습니다.

확정 아트 8장은 #721 공개 manifest의 SHA256과 동일합니다. 키 비주얼의 도호·귀새·청연은 캐스트이며 EA 플레이 가능 인물은 도호 한 명입니다. 갈필·농묵 PNG는 배경을 포함한 RGB 브랜드 마스터, 게임 한글 로고는 알파가 있는 PNG입니다. 원본 제작 시점과 인게임 검수 사진 시점이 서로 다를 수 있습니다.

각 파일 `public_allowed`, `approval_status`, `spoiler`, `visual_review`와 `editorial_note`를 먼저 확인하세요. 원본 승인 상태와 SNS에 올릴 컷의 편집 판단은 따로 기록합니다. 이 패키지는 소재 전달이며 SNS 게시를 실행하지 않았습니다.

캡처 QA ZIP에는 원문 실행·인코딩·전체 디코딩 로그와 촬영 도구 사본을 보존합니다. 시나리오 성공, MP4 전체 디코딩, 소리 가청 검사와 엔진 종료 정리 메시지는 구분했습니다. 일부 캡처 종료의 ObjectDB·resource 정리 메시지도 원문에 남아 있으며 `validation.json`에 종류를 기록합니다.

## 이전 공개 소재도 한곳에서

- [2026-10-10 전체 자료](../2026-10-10/README.md): 기존 확정·후보 아트, 원본 게임 영상과 4K 이미지.
- [아트·표정 대응표](../2026-10-10/art/README.md): 추가 초상과 배경의 확정/후보 상태.
- [음악·효과음·공개 음성](../2026-10-10/audio/README.md): 이전 공개 음성 196줄·BGM·SFX. 음성은 10/10 버전이며 10/14 현 음성 전체와 동일하다고 소개하지 않습니다.
- [이전 영상 목록](../2026-10-10/video/clips_public.csv): UI on/off·전체 원본 ZIP.
- [이전 ZIP 다운로드·SHA256](../2026-10-10/release_archives.json).

## 구조 선택 이유

날짜별 `marketing/YYYY-MM-DD`와 같은 날짜 Release를 묶으면 촬영 시점·게임 버전·확정 상태를 함께 찾을 수 있습니다. 대량 원본을 git에 넣는 방식은 저장소 이력과 복제를 크게 만들기 때문에, 이번 묶음은 원본을 Release ZIP에 보존하고 git에는 작은 개별 미리보기·갤러리·검증 가능한 대응표를 둡니다. 이전 공개 자료는 연결하고 새 촬영과 재사용 아트의 출처를 구분해 같은 화면을 최신 버전으로 잘못 소개하는 일을 줄였습니다.

© 2026 KOOSHA studio. Public marketing materials; approval and spoiler status remain per file.
