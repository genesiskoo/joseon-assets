
## #559 신규 효과음

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100. 구독 크레딧 0.
`<큐>_vN.wav` = 손질본(끝 딸깍 자름 · 25 Hz 고역 통과, 32-bit float) · 날것 = `<큐>/_raw/` (design/audio.md §4.5.1, #399). 길이·LUFS·피크 = 손질본.

| 큐 | 변주 | 길이 | LUFS | 피크 | 손질·흠 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|---|
| sword_swing | v1 | 0.47s | -14.0 | 0.7 | 끝 −11 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 28.7 → 29.1 % · **CLIP 34 · DC +0.017** | - | Single sharp steel sword slash through air, fast dry airy whoosh, close clean mono-compati… |
| sword_swing | v2 | 0.47s | -13.2 | 0.2 | 끝 −6 ms · 25 Hz 안 걺(-2.7 LU) · 20 Hz 아래 5.8 → 6.1 % · **CLIP 12** | - | Single sharp steel sword slash through air, fast dry airy whoosh, close clean mono-compati… |
| sword_swing | v3 | 0.47s | -15.2 | 0.3 | 끝 −7 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 7.9 → 8.1 % · **CLIP 4** | - | Single sharp steel sword slash through air, fast dry airy whoosh, close clean mono-compati… |
| hit | v1 | 0.45s | -22.2 | -2.4 | 끝 −29 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 6.2 → 0 % | - | One weighty sword hit into a monster body, tight wet thud with a short steel bite, punchy … |
| hit | v2 | 0.45s | -14.4 | -0.0 | 끝 −32 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 1** | - | One weighty sword hit into a monster body, tight wet thud with a short steel bite, punchy … |
| hit | v3 | 0.47s | -23.2 | -4.9 | 끝 −12 ms · 25 Hz(+2.2 LU) · 20 Hz 아래 39.2 → 10.2 % | - | One weighty sword hit into a monster body, tight wet thud with a short steel bite, punchy … |
| hit_crit | v1 | 0.67s | -12.1 | 0.5 | 끝 −15 ms · 25 Hz 안 걺(-2.9 LU) · 20 Hz 아래 21.4 → 26.9 % · **CLIP 130** | - | One powerful critical sword strike, crisp steel crack and deep compact flesh impact, satis… |
| hit_crit | v2 | 0.66s | -19.3 | 0.1 | 끝 −17 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.5 → 0 % | - | One powerful critical sword strike, crisp steel crack and deep compact flesh impact, satis… |
| skill_slash | v1 | 0.59s | -9.9 | 0.4 | 끝 −9 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 3** | - | One forceful sword draw and fast sweeping air cut, accented with a tiny plucked string sna… |
| skill_slash | v2 | 0.58s | -9.7 | 0.4 | 끝 −19 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 8** | - | One forceful sword draw and fast sweeping air cut, accented with a tiny plucked string sna… |
| skill_dash_strike | v1 | 0.67s | -14.3 | 1.7 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 2.4 → 0 % · **CLIP 1** | - | Rapid forward sword lunge, rushing air then sharp steel slash, compact dry close effect, n… |
| skill_dash_strike | v2 | 0.67s | -10.6 | 0.5 | 끝 −12 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 5** | - | Rapid forward sword lunge, rushing air then sharp steel slash, compact dry close effect, n… |
| skill_whirl | v1 | 1.19s | -12.7 | -4.9 | 끝 −6 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | Short circular spinning sword sweep, two smooth closely spaced air cuts with crisp steel e… |
| skill_whirl | v2 | 1.20s | -13.3 | -0.0 | 끝 −5 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | Short circular spinning sword sweep, two smooth closely spaced air cuts with crisp steel e… |
| talisman_throw | v1 | 0.47s | -31.0 | -7.0 | 끝 −13 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 1.6 → 0.4 % | - | A stiff paper talisman flicked sharply through air, papery snap and brief airy flutter, cr… |
| talisman_throw | v2 | 0.47s | -17.9 | 0.2 | 끝 −9 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 4** | - | A stiff paper talisman flicked sharply through air, papery snap and brief airy flutter, cr… |
| talisman_fire_hit | v1 | 0.78s | -22.1 | -0.4 | 끝 −23 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 15.3 → 1.4 % | - | Paper talisman ignites with a quick compact flame burst and short crackle, clean punchy fi… |
| talisman_fire_hit | v2 | 0.79s | -27.5 | -10.4 | 끝 −7 ms · 25 Hz(+0.6 LU) · 20 Hz 아래 1.7 → 0.4 % | - | Paper talisman ignites with a quick compact flame burst and short crackle, clean punchy fi… |
| talisman_cold_burst | v1 | 0.79s | -17.3 | 0.8 | 끝 −9 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 4** | - | Sudden localized freezing burst, crisp ice crack with a short crystalline tail and cold ai… |
| talisman_cold_burst | v2 | 0.79s | -15.8 | 0.7 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 29** | - | Sudden localized freezing burst, crisp ice crack with a short crystalline tail and cold ai… |
| step_dirt | v1 | 0.47s | -52.3 | -27.9 | 끝 −13 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 2.5 → 0.1 % | - | One soft leather shoe step on compact earth, muted natural footfall, no gravel scrape, no … |
| step_dirt | v2 | 0.47s | -54.0 | -32.4 | 끝 −7 ms · 25 Hz(+0.7 LU) · 20 Hz 아래 14.2 → 0.1 % | - | One soft leather shoe step on compact earth, muted natural footfall, no gravel scrape, no … |
| step_dirt | v3 | 0.47s | -48.3 | -29.9 | 끝 −7 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 0.6 → 0.6 % | - | One soft leather shoe step on compact earth, muted natural footfall, no gravel scrape, no … |
| pickup_coin | v1 | 0.47s | -17.1 | -2.2 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | Small handful of old brass Korean coins gently collected, short soft metallic clinks, dry … |
| pickup_coin | v2 | 0.45s | -16.1 | -0.4 | 끝 −26 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | Small handful of old brass Korean coins gently collected, short soft metallic clinks, dry … |
| seal_release | v1 | 1.47s | -27.8 | -13.7 | 끝 −15 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % | - | Ancient paper seal being peeled from stone, dry paper tear then low resonant ceremonial br… |
| stone_door_sink | v1 | 2.45s | -10.1 | 1.1 | 끝 −26 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 0 → 0 % · **CLIP 12** | - | Heavy ancient stone door sinks into the floor, slow gritty stone friction and final deep s… |
