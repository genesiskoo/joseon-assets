
## #873 국악기 후보

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100. 구독 크레딧 1000.
`<큐>_vN.wav` = 손질본(끝 딸깍 자름 · 25 Hz 고역 통과, 32-bit float) · 날것 = `<큐>/_raw/` (design/audio.md §4.5.1, #399). 길이·LUFS·피크 = 손질본.

| 큐 | 변주 | 길이 | LUFS | 피크 | 손질·흠 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|---|
| jing_boss | v1 | 4.97s | -13.5 | -3.6 | 끝 −27 ms · 25 Hz(+0.8 LU) · 20 Hz 아래 0 → 0 % | - | One single strike on a large Korean jing gong with a padded mallet: deep warm booming fund… |
| jing_boss | v2 | 4.99s | -17.1 | -5.4 | 끝 −10 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | One single strike on a large Korean jing gong with a padded mallet: deep warm booming fund… |
| jing_boss | v3 | 4.99s | -13.8 | -4.0 | 끝 −10 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | One single strike on a large Korean jing gong with a padded mallet: deep warm booming fund… |
| jing_triple | v1 | 5.99s | -12.0 | -2.4 | 끝 −11 ms · 25 Hz(+0.9 LU) · 20 Hz 아래 0 → 0 % | - | Three slow solemn strikes on a large Korean jing gong, each strike deep and booming with a… |
| jing_triple | v2 | 5.98s | -15.7 | -5.1 | 끝 −22 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | Three slow solemn strikes on a large Korean jing gong, each strike deep and booming with a… |
| kkwaenggwari_alarm | v1 | 1.99s | -9.7 | 0.2 | 끝 −12 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 44** | - | Korean kkwaenggwari small handheld brass gong played frantically: a fast shrill rolling tr… |
| kkwaenggwari_alarm | v2 | 1.97s | -7.9 | 0.2 | 끝 −32 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 23** | - | Korean kkwaenggwari small handheld brass gong played frantically: a fast shrill rolling tr… |
| kkwaenggwari_alarm | v3 | 1.99s | -7.0 | 0.3 | 끝 −12 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 181** | - | Korean kkwaenggwari small handheld brass gong played frantically: a fast shrill rolling tr… |
| kkwaenggwari_hit | v1 | 0.76s | -31.2 | -13.0 | 끝 −38 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.4 → 0 % | - | One sharp bright clang on a Korean kkwaenggwari small brass gong struck with a hard wooden… |
| kkwaenggwari_hit | v2 | 0.80s | -32.6 | -14.9 | 끝 −5 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 0.9 → 0 % | - | One sharp bright clang on a Korean kkwaenggwari small brass gong struck with a hard wooden… |
| kkwaenggwari_hit | v3 | 0.79s | -18.8 | -0.1 | 끝 −13 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | One sharp bright clang on a Korean kkwaenggwari small brass gong struck with a hard wooden… |
| samul_finale | v1 | 3.99s | -15.6 | 0.4 | 끝 −9 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % · **CLIP 6** | - | Korean samulnori percussion quartet short climactic ending: kkwaenggwari small gong, jangg… |
| samul_finale | v2 | 3.99s | -10.9 | 0.1 | 끝 −12 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0 → 0 % · **CLIP 171** | - | Korean samulnori percussion quartet short climactic ending: kkwaenggwari small gong, jangg… |
| samul_finale | v3 | 3.99s | -11.0 | 0.9 | 끝 −8 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 0 → 0 % · **CLIP 33** | - | Korean samulnori percussion quartet short climactic ending: kkwaenggwari small gong, jangg… |
| samul_hwimori | v1 | 2.99s | -14.2 | -0.1 | 끝 −12 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | Korean samulnori percussion burst in fast hwimori rhythm: shrill kkwaenggwari, cracking ja… |
| samul_hwimori | v2 | 2.99s | -16.9 | -0.1 | 끝 −7 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 9** | - | Korean samulnori percussion burst in fast hwimori rhythm: shrill kkwaenggwari, cracking ja… |
| janggu_deong | v1 | 0.79s | -46.6 | -33.8 | 끝 −8 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.1 → 0 % | - | One deep resonant deong hit on a Korean janggu hourglass drum, both heads struck at once, … |
| janggu_deong | v2 | 0.79s | -38.7 | -22.5 | 끝 −6 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.5 → 0 % | - | One deep resonant deong hit on a Korean janggu hourglass drum, both heads struck at once, … |
| janggu_deong | v3 | 0.79s | -38.7 | -25.3 | 끝 −7 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 0.3 → 0.3 % | - | One deep resonant deong hit on a Korean janggu hourglass drum, both heads struck at once, … |
| janggu_phrase | v1 | 1.46s | -27.5 | -6.8 | 끝 −22 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | Short Korean janggu hourglass drum phrase: deong, kung, then a crisp double tap dak-dak en… |
| janggu_phrase | v2 | 1.46s | -22.7 | -3.6 | 끝 −20 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % | - | Short Korean janggu hourglass drum phrase: deong, kung, then a crisp double tap dak-dak en… |
| janggu_phrase | v3 | 1.47s | -14.7 | 0.2 | 끝 −8 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0 → 0 % · **CLIP 154** | - | Short Korean janggu hourglass drum phrase: deong, kung, then a crisp double tap dak-dak en… |
| buk_heavy | v1 | 1.19s | -43.5 | -29.8 | 끝 −12 ms · 25 Hz(+0.6 LU) · 20 Hz 아래 0.1 → 0 % | - | One heavy powerful hit on a large Korean buk barrel drum with a thick wooden stick, deep b… |
| buk_heavy | v2 | 1.19s | -37.3 | -24.8 | 끝 −8 ms · 25 Hz(+0.8 LU) · 20 Hz 아래 2.9 → 0 % | - | One heavy powerful hit on a large Korean buk barrel drum with a thick wooden stick, deep b… |
| bak_clap | v1 | 0.59s | -63.4 | -49.6 | 끝 −13 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 32.2 → 0.6 % | - | One single sharp crack of a Korean bak wooden clapper made of six hardwood slats snapped s… |
| bak_clap | v2 | 0.58s | -19.1 | 0.6 | 끝 −22 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.4 → 0 % · **CLIP 20** | - | One single sharp crack of a Korean bak wooden clapper made of six hardwood slats snapped s… |
| bak_clap | v3 | 0.59s | -70.0 | -59.1 | 끝 −7 ms · 25 Hz · 20 Hz 아래 93.1 → 4.3 % | - | One single sharp crack of a Korean bak wooden clapper made of six hardwood slats snapped s… |
| daegeum_breath | v1 | 3.99s | -26.1 | -19.2 | 끝 −6 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | Korean daegeum large bamboo transverse flute playing one long mournful breathy note with s… |
| daegeum_breath | v2 | 3.99s | -22.5 | -14.5 | 끝 −9 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % | - | Korean daegeum large bamboo transverse flute playing one long mournful breathy note with s… |
| daegeum_breath | v3 | 3.99s | -27.4 | -20.1 | 끝 −8 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | Korean daegeum large bamboo transverse flute playing one long mournful breathy note with s… |
| haegeum_eerie | v1 | 2.99s | -11.8 | -0.8 | 끝 −12 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | Korean haegeum two-string fiddle playing an eerie ghostly sliding glissando that bends dow… |
| haegeum_eerie | v2 | 2.98s | -13.5 | -1.6 | 끝 −21 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | Korean haegeum two-string fiddle playing an eerie ghostly sliding glissando that bends dow… |
| haegeum_eerie | v3 | 2.99s | -9.6 | 0.1 | 끝 −11 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 11** | - | Korean haegeum two-string fiddle playing an eerie ghostly sliding glissando that bends dow… |
| taepyeongso_call | v1 | 2.48s | -4.6 | 0.3 | 끝 −5 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 22** | - | Korean taepyeongso shrill conical double-reed horn playing a short loud triumphant ascendi… |
| taepyeongso_call | v2 | 2.48s | -4.7 | 0.6 | 끝 −4 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % · **CLIP 1269** | - | Korean taepyeongso shrill conical double-reed horn playing a short loud triumphant ascendi… |
| yoryeong_bell | v1 | 1.45s | -14.4 | -4.8 | 끝 −27 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | Korean shaman ritual hand bell yoryeong, a cluster of small brass bells on a handle shaken… |
| yoryeong_bell | v2 | 1.46s | -11.7 | 0.1 | 끝 −25 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | Korean shaman ritual hand bell yoryeong, a cluster of small brass bells on a handle shaken… |
| yoryeong_bell | v3 | 1.45s | -12.8 | 0.1 | 끝 −27 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | Korean shaman ritual hand bell yoryeong, a cluster of small brass bells on a handle shaken… |
| geomungo_pluck | v1 | 1.47s | -43.6 | -27.7 | 끝 −12 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.9 → 0.9 % | - | Korean geomungo six-string zither struck hard with a bamboo stick: one deep heavy plucked … |
| geomungo_pluck | v2 | 1.47s | -46.1 | -29.8 | 끝 −10 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % | - | Korean geomungo six-string zither struck hard with a bamboo stick: one deep heavy plucked … |
| pyeonjong_chime | v1 | 2.45s | -22.9 | -8.2 | 끝 −29 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | One clear strike on a Korean pyeonjong bronze bell from a court bell rack, pure solemn met… |
| pyeonjong_chime | v2 | 2.45s | -25.4 | -13.7 | 끝 −27 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | One clear strike on a Korean pyeonjong bronze bell from a court bell rack, pure solemn met… |
| beomjong_temple | v1 | 5.98s | -12.4 | -0.4 | 끝 −24 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 0.6 → 0.1 % | - | One toll of a huge Korean Buddhist temple bronze bell beomjong struck by a log, very deep … |
| beomjong_temple | v2 | 5.99s | -21.6 | -7.1 | 끝 −12 ms · 25 Hz(+0.8 LU) · 20 Hz 아래 0.1 → 0 % | - | One toll of a huge Korean Buddhist temple bronze bell beomjong struck by a log, very deep … |
| jabara_crash | v1 | 1.99s | -9.2 | 0.3 | 끝 −7 ms · 25 Hz 안 걺(-0.5 LU) · 20 Hz 아래 0 → 0 % · **CLIP 293** | - | One big crash of Korean jabara large brass cymbals clapped together, bright explosive spla… |
| jabara_crash | v2 | 1.99s | -17.7 | 0.4 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 10** | - | One big crash of Korean jabara large brass cymbals clapped together, bright explosive spla… |

## 저장소에 든 것 (#873)
- 원본 wav(손질본 + `_raw/`) 46개 = 61MB → 카드 합 50MB 넘어 **git에 안 넣음**. 자리 = 이 폴더(로컬 C:\workspace\joseon-assets\workbench\audio\873_gugak, 미추적) — PD 채택 뒤 반입분만 게임 저장소로, 나머지는 보관 때 D:\joseon_archive로.
- git = 프롬프트·측정 메타(`<큐>/<큐>_vN.json`) · 대조표 `contact_873.png` · 배치 `../batch_873_gugak.json` · 듣기용 `listen/*.mp3`(−16 LUFS 맞춤, 64 kbps 모노).
- 판정판 = https://claude.ai/artifact/Nza8hLfN8r6uT4mPVCXkFz · 사양 = joseon `docs/design/gugak_sfx_plan.md`.
