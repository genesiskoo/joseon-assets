# #777 이벤트·대사 전수 개선 및 ElevenLabs 음성 재제작

원본·요청·receipt·immutable plans·정규화 WAV·실측 QA·제외/보존 목록 = audio/. raw 실행 전문 = qa/. 최초 실패 사진은 photos_initial/, 최종 대화 jpg는 photos/. 게임에 쓰는 277 WAV와 SHA 요약은 작업 트리 assets/audio/voice 및 docs/design/audio_777_result.json.

청취: 이 폴더의 audio/를 HTTP 서버 루트로 열고 listen/index.html에 접속한다. 예: python -m http.server 8777 --bind 127.0.0.1 --directory audio

506MB 임시 검증 PCK는 보존 대상에 넣지 않는다. 그 내보내기·원본 대조 및 실제 음성 재생 raw는 qa/에 남긴다. 전체 플레이 최종 집계 170/170갈래10523검사 PASS. 최초 실패와 대기 중단 전문도 보존한다.

원본 비공개 백업: https://drive.google.com/drive/folders/116nqpoLYtDtp55pQv9I1GCpxMXYpl7aj . ZIP2개(59362255B·55529866B)의 URL·SHA256은 drive_originals.json에 기록. 업로드 크기/부모/비공개 확인, 원격 체크섬은 도구 미반환. Git 보관은 README·작은 SHA/검증 요약 및 자료관 재사용 증거만. 원본·스테이징·대량 raw는 git 밖 보존.

최종 QA ZIP(원본 사진/초기 실패/최종 실행 전문/자료관 후보) = https://drive.google.com/file/d/1uUsDv2bCBGun7tG4TG4Bj1Y5zJlVWFiO/view
크기 22989721B · SHA256 `99d8718b768760181772d47d69cebb31757ab7993023b2c9f90595e819927e2c`. 독립 압축 무결성·업로드 크기/부모폴더/비공개 확인.
