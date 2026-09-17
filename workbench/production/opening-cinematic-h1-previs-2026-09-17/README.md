# H1 opening previs v001

샘플 = **edit/joseon_h1_opening_previs_50s_v001.mp4** · 50.000초 · 1280×720 · 24fps · 1,200프레임.

도호 중심, 귀새·청연 각 3초. 새 키아트 H1-K01r1 기반 Seedance 2.5 새 영상 11건(마지막 컷 교정 1건 포함), 기존 r3 도호 8초 재사용. 사설 6개와 임시 타이틀. 음성 없음. 47–50초는 현행 GT1/임시 지형 Godot 실제 캡처이며 H1 모델 교체나 게임 인계 구현이 아니다.

음악과 Foley는 외부 샘플을 쓰지 않은 원본 절차 합성 임시 음원이다. 최종 국악 연주가 아니며 정상 속도 전체 시청·청취 판정은 사용자 검토 단계다.

- 재현: edit/assemble_local.py --ffmpeg <ffmpeg> --ffprobe <ffprobe> (Python + Pillow). 출력과 검수 파일을 다시 만든다.
- 타이밍: edit/edl.json. 사설/타이틀: edit/saseol_title.ass. 임시음원 소스: edit/temp_soundtrack.py.
- 폰트: edit/fonts/NanumMyeongjo-Regular.ttf, OFL 동봉.
- 원본/견적/작업 ID: metadata/production.json. QA: metadata/qa_*.json, render_audit.json, review/.
- H05_shadow_rejected_7tips.png와 H10.mp4는 탈락 비교본. 선택본은 H05_shadow_9tips.png / H10_r2.mp4.
- edit.mjs/build_remote.sh는 준비했던 Higgsedit 구성이다. 원격 render tool 응답 오류로 최종 MP4는 로컬 FFmpeg로 렌더했다. 완성 native project.json 또는 hosted editor 프로젝트라고 주장하지 않는다.

게임 반입 없음. 최종 게임 H1 외형/지형, 입력 잠금 해제, 첫 대사 연결은 별도 작업이다.

