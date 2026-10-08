# #198 VFX 영상 검수 — 2026-10-05

PD 지시: 이펙트는 영상으로 만들어서 보고. 실제 Godot MovieMaker 렌더이며 정상 재생 속도 1×, 기록 60fps다. 실시간 60fps 성능 측정 자료가 아니다.

| 영상 | 내용 | 길이 |
|---|---|---|
| [198_vfx_before_after_60fps.mp4](198_vfx_before_after_60fps.mp4) | 왼쪽 변경 전 / 오른쪽 변경 후, 불·냉기·살 각 3회 | 12.000초 |
| [198_vfx_actual_60fps.mp4](198_vfx_actual_60fps.mp4) | 실제 기본 큐 크기의 불 폭발·살 구름·화염부 명중 각 3회, 게임 소리 포함 | 12.021초(영상720프레임+AAC 패딩) |
| [198_vfx_engine_capture_60fps.mp4](198_vfx_engine_capture_60fps.mp4) | 자막·크롭 이전 전체 엔진 촬영, 게임 소리 포함 | 39.950초 |

전후 비교는 같은 fire_burst 시트·위치·카메라·크기2.8·HDR3·native 재생이며 opts.ramp만 다르다. 동일한 (320,110,480,360) 크롭을 양쪽에 적용해 640×480으로 확대했다. 불→냉기→살 각4초. 냉기/살은 화염 모양의 팔레트 진단이며 실제 기술 형상이 아니라고 영상에 표시했다. 실제 적용 영상은 Vfx.play(cue,pos)만 호출하여 기본 큐 크기·섞기·수명·곁들이를 유지했다.

촬영63/63 PASS, 세 MP4 전체 디코딩 오류0, H264/yuv420p/60fps. 코드·프레임 범위·원본 해시 = video_manifest.json / archive_manifest.json. 원래 구현은 게임 ff11d37f, 자산 사진 기록 d0b04a0. 실패한 독립 --script 초기화 대본의 오류 원문까지 logs/에 보존했다. 정상 프로젝트 씬으로 오토로드를 먼저 등록한 촬영이 최종본이다. 종료 리소스 정리 보고는 기존 허용 정책을 따랐다.

재현: 게임 ff11d37f에서 reproduce/의 capture_video.gd, capture_scene.tscn, encode_video.py를 ._tmp/198_vfx_d2r/에 복사하고 video/ 폴더를 만든다. 프로젝트 루트에서 아래 명령을 실행한다. 게임 코드 변경은 없다.

```powershell
godot --path . --scene res://._tmp/198_vfx_d2r/capture_scene.tscn --windowed --resolution 1280x720 --fixed-fps 60 --disable-vsync --quit-after 3000 --write-movie C:/Users/FORYOUCOM/.codex/worktrees/d454/joseon/._tmp/198_vfx_d2r/video/capture_master_corrected.avi --log-file C:/Users/FORYOUCOM/.codex/worktrees/d454/joseon/._tmp/198_vfx_d2r/video/capture_corrected.engine.log -- --new *> ._tmp/198_vfx_d2r/video/capture_corrected.raw.log
python ._tmp/198_vfx_d2r/encode_video.py
```

원본 보존본은 전체 엔진 MP4(9.40MB)다. 큰 AVI는 인코딩 중간 파일로 로컬 ._tmp에만 있으며 git에 넣지 않았다. MP4 각각10MB미만, 이전 사진44장 포함 카드 전체50MB미만. 검증 기록이므로 PD 지시 전 push하지 않는다.
