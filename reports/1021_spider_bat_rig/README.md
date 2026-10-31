# #1021 거미·박쥐 이동 동작 — 영상

- git에 든 것: `before_after_spider.mp4` · `before_after_bat.mp4`(전 = #1025 인게임 녹화 · 후 = 이번 리그) · `manifest.json` · `audit.json`(기계 점검 초록 5).
- 인게임 원본 다섯 편(`v/*.mp4`, 합 약 45MB)은 카드 합 50MB 규칙(D-100)으로 git에 넣지 않았다 — 자리 = 이 PC `C:\workspace\joseon-assets\reports\1021_spider_bat_rig\v\`(로컬). 다시 뽑기 = 게임 저장소 `python tools/enemy_tour_videos.py ingame --out <폴더> --only spider,wang_geomi,bat,cave_bat,vampire_bat`.

| 파일 | 바이트 | sha256 |
|---|---|---|
| bat.mp4 | 8,841,758 | `f67f4e0de6f4b4751585b3b870bc077e6eebec15409ad0488e0fffb719e886d7` |
| cave_bat.mp4 | 8,800,630 | `f49ae9562538128ad2060b3f637a5c1708767851ab82cfeaa6a710c0336e97a6` |
| spider.mp4 | 9,634,269 | `522d2c32f9b65205911ded409c22c24a0320c0f5861ac0ef0b64c81d620ca8a6` |
| vampire_bat.mp4 | 8,905,596 | `87cc49c8fc346bd449931e4d8b267b488736b4f43b91fdb261afdfd2faee9fab` |
| wang_geomi.mp4 | 9,270,958 | `e9f081ff41974da73d1a0cfc2345d5a88a993e925be5edf6cfcf6f188fb835ee` |
