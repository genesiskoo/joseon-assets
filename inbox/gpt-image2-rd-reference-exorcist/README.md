# GPT Image 2 Front Exorcist Postprocess

원본:
- `gpt_image2_front_pixel_exorcist_source.png`

후처리 산출물:
- `gpt_image2_front_pixel_exorcist_source_256.png`
  - 256px 다운스케일 보존본
- `gpt_image2_front_pixel_exorcist_source_256_nn.png`
  - 256px nearest-neighbor
- `gpt_image2_front_pixel_exorcist_source_128.png`
  - 128px 다운스케일 보존본
- `gpt_image2_front_pixel_exorcist_source_128_nn.png`
  - 128px nearest-neighbor
- `gpt_image2_front_pixel_exorcist_source_128_16color.png`
  - 16색 팔레트 축소
- `gpt_image2_front_pixel_exorcist_source_128_32color.png`
  - 32색 팔레트 축소
- `gpt_image2_front_pixel_exorcist_source_128_transparent.png`
  - 매트 배경 제거 후 투명 PNG

방법:
- 128px는 원본에서 `NearestNeighbor`로 리샘플했다.
- 16색과 32색은 128px 이미지를 기준으로 `FASTOCTREE` 팔레트 축소했다.
- 투명본은 128px 매트 배경을 edge flood fill로 제거했다.

기록:
- `gpt_image2_front_pixel_exorcist_source_256.png`가 현재 스프라이트 전처리 기준 우선본이다.
- `gpt_image2_front_pixel_exorcist_source_128.png`는 2차 비교본으로 남겨둔다.
- `gpt_image2_front_pixel_exorcist_source_256_nn.png`은 256px 기준 비교용으로 추가했다.
- `image_gen` 산출물을 스프라이트로 쓰려면, 후처리만 볼 게 아니라 생성 단계부터 다운스케일을 염두에 둬야 한다. 요소 수를 줄이고 눈, 코, 입, 실루엣의 핵심 판독 요소를 더 크게 설계하는 편이 낫다.
- 이 테스트 소스는 얼굴, 눈, 갓, 칼 실루엣이 충분히 커서 다운스케일 친화적이다.

주의:
- 원본은 그대로 유지한다.
- 이 폴더의 파일들은 픽셀 스프라이트용 참고본이다. 공식 승격 전에는 `sprites/`로 복사하지 않는다.
