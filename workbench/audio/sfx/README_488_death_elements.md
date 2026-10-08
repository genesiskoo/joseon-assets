
## 배치

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100. 구독 크레딧 0.
`<큐>_vN.wav` = 손질본(끝 딸깍 자름 · 25 Hz 고역 통과, 32-bit float) · 날것 = `<큐>/_raw/` (design/audio.md §4.5.1, #399). 길이·LUFS·피크 = 손질본.

| 큐 | 변주 | 길이 | LUFS | 피크 | 손질·흠 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|---|
| burn | v1 | 1.16s | -23.5 | -1.8 | 끝 −41 ms · 25 Hz(+3.6 LU) · 20 Hz 아래 87.1 → 43.3 % · **CLIP 118 · SUB20 43%** | - | A body catching fire and burning away to ash: sudden low whoosh of flame igniting, crackli… |
| burn | v2 | 1.19s | -22.5 | 0.7 | 끝 −10 ms · 25 Hz(+2.4 LU) · 20 Hz 아래 80.4 → 14.9 % · **CLIP 264** | - | A body catching fire and burning away to ash: sudden low whoosh of flame igniting, crackli… |
| burn | v3 | 1.18s | -21.1 | 0.0 | 끝 −21 ms · 25 Hz 안 걺(-1.0 LU) · 20 Hz 아래 85.6 → 86.2 % · **CLIP 379 · SUB20 86%** | - | A body catching fire and burning away to ash: sudden low whoosh of flame igniting, crackli… |
| freeze | v1 | 0.48s | -35.0 | -9.6 | 끝 −4 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.2 → 0 % | - | Ice rapidly forming over a body: sharp crystalline crackle and creak of frost spreading an… |
| freeze | v2 | 0.47s | -39.2 | -14.9 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.8 → 0 % | - | Ice rapidly forming over a body: sharp crystalline crackle and creak of frost spreading an… |
| freeze | v3 | 0.48s | -23.2 | 0.1 | 끝 −2 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 2** | - | Ice rapidly forming over a body: sharp crystalline crackle and creak of frost spreading an… |
| shatter | v1 | 0.67s | -34.2 | -17.9 | 끝 −8 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A frozen body shattering into ice shards: sharp glassy ice break with small shards scatter… |
| shatter | v2 | 0.67s | -23.2 | 0.1 | 끝 −7 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 4** | - | A frozen body shattering into ice shards: sharp glassy ice break with small shards scatter… |
| shatter | v3 | 0.67s | -26.3 | -4.1 | 끝 −10 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A frozen body shattering into ice shards: sharp glassy ice break with small shards scatter… |
| soul_scatter | v1 | 1.18s | -22.3 | -9.9 | 끝 −17 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.7 → 0 % | - | A ghostly spirit dissolving into ink smoke: soft airy breathy whoosh rising and fading awa… |
| soul_scatter | v2 | 1.19s | -17.8 | -6.1 | 끝 −8 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % | - | A ghostly spirit dissolving into ink smoke: soft airy breathy whoosh rising and fading awa… |
| soul_scatter | v3 | 1.19s | -14.1 | -3.0 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A ghostly spirit dissolving into ink smoke: soft airy breathy whoosh rising and fading awa… |
