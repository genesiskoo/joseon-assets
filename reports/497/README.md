# INDIE Live Expo 2026.12.1 엔트리 (#497)

2026-09-29 05:50 KST 제출 완료(마감 같은 날 11:59). 폼 = https://forms.gle/UYJKkA3mCvvcEj5t8 · 제출 답안 전문 = [entry_answers.md](entry_answers.md).

## 제출 자료 (구글 드라이브 `내 드라이브/JoseonHunters_ILE2026`, 링크 있는 모든 사용자 · 뷰어 — **12월 31일까지 지우지 말 것**)

| 파일 | 내용 |
|---|---|
| [final/joseonhunters.mp4](final/joseonhunters.mp4) | 15.0초 — 못골 → 회오리 → 전투 → 흑랑 처치·전리품 → 흑랑 송곳니 |
| [final/joseonhunters_full.mp4](final/joseonhunters_full.mp4) | 33.5초 — #456 30초 구성(마을·대화·들녘·굴·전투·성장·흑랑·전리품) + 끝 카드 3.5초 |
| [final/main.jpg](final/main.jpg) | 키 비주얼 — 도호 단독 키 아트(archive 21_doho_keyart) + 궁서 제목 |
| final/ss1~3.jpg | 회오리 베기 / 흑랑 보스전 / 도호·무당 할매 대화 |

규격(폼 요구): 1920×1080 · 30fps · H.264 약 23Mbps(권장 20 이상) · AAC 48kHz 스테레오 · 통합 −14.5 LUFS(요구 −15 ±1) · 트루 피크 −1.9 dBFS. 검증 = [edit_15.log](edit_15.log) · [edit_full.log](edit_full.log) · 1초 대조표 [qa/](qa/).

## 촬영

- [capture_1080.avi](capture_1080.avi) = main `bab6766f`를 **1080p로 다시 찍은 원본**(Movie Maker MJPEG + PCM, 4,019프레임 · 2분 14초) — #455 대본 `_slice_capture`, 검사 33 PASS. 장면 표식 = [capture_1080_out.log](capture_1080_out.log)의 `CAPTURE <장면> BEGIN/END <프레임>`. 스팀 페이지 트레일러 등에 다시 쓸 수 있다.
- **#455 영상은 1080p가 아니라 1280×720이었다**(manifest는 1920×1080이라 적힘). Movie Maker는 `--resolution`을 무시하고 프로젝트 창 크기로 녹화한다 → `override.cfg`에 `[display] window/size/window_width_override=1920`·`window_height_override=1080`을 두고 찍었다(시작 때만 읽으므로 게임이 뜬 직후 지움). 명령:
  `godot --path <프로젝트> --windowed --position 0,0 --fixed-fps 30 --disable-vsync --write-movie capture_1080.avi -- --e2e=_slice_capture`
- 편집 = [tools/edit.py](tools/edit.py) `plan.json out.mp4`(컷 = 장면 표식 + 장면 안 프레임, 라우드니스 2패스, x264 2패스 24M). 계획 = tools/plan_15.json · plan_full.json. tools/ 는 `joseon/tmp/ile_497/work`에서 돌린 그대로라 경로가 그 폴더 기준이다.

## 약속한 것 (방송 12/1 기준)

- 「2026/12/2~2027/4/30 (JST) 데모 배포 예정」 + 출시 예정 2027 — 4월 말까지 Steam 페이지와 데모가 필요하다.
- 영상 방송 외 사용 허가 · 실황 무조건 허가 · 생성형 AI 사용 = 예(에셋 생성 + 개발 지원, 게임 안 동적 생성 없음).
