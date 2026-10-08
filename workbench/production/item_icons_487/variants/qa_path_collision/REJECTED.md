# #487 검수도구 첫 렌더: 최종 결과 아님

자동 렌더/계약 검사는 PASS였으나 직접 검수에서 첫 운검이 짧게 찌그러지는 문제를 발견했다. 같은 배치 운검을 운룡검 비교로 다시 ImageTexture.take_over_path 호출하며 기존 운검 후보의 resource_path가 지워졌다. UiSkin이 작은 공용그림 fallback을 사용한 검수도구 문제다. 원화나 게임런타임을 수정하지 않고 같은 배치 비교는 기존후보 Texture2D를 공유한다. 재렌더 전 모든 후보/참조의 art resource_path를 검사한다. 첫 검수의 PNG/JPG/raw/script/verification를 여기 보존하고 현재 qa/verification를 최종 결과로 재작성한다.
