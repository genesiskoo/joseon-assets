# #491 검수 스크립트 최초 파싱 실패

최초 검수 스크립트에서 Image.duplicate의 자료형이 명시되지 않아 픽셀 Color와 명도 float 추론이 실패했다. 원본 그림이나 게임 UiSkin 변경과 관계없는 검수 도구 오류다. 이 폴더에 당시 스크립트와 stdout/stderr 전문을 보존하고 Image/Color/float를 명시해 고친 뒤 전체 5모드를 다시 실행한다. 이 로그는 최종 통과 결과가 아니다.
