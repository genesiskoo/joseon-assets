
## #301 몬스터 가족 소리 · 깨어남 북·징 · 드랍 소리 (두 벌)

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100. 구독 크레딧 658.
`<큐>_vN.wav` = 손질본(끝 딸깍 자름 · 25 Hz 고역 통과, 32-bit float) · 날것 = `<큐>/_raw/` (design/audio.md §4.5.1, #399). 길이·LUFS·피크 = 손질본.

| 큐 | 변주 | 길이 | LUFS | 피크 | 손질·흠 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|---|
| bandit_hurt | v1 | 0.46s | -10.9 | 0.4 | 끝 −23 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 64** | - | A rough grown man struck in a fight: one short gruff pained grunt through clenched teeth a… |
| bandit_hurt | v2 | 0.47s | -11.1 | 0.5 | 끝 −6 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 0.8 → 0 % · **CLIP 44** | - | A rough grown man struck in a fight: one short gruff pained grunt through clenched teeth a… |
| bandit_die | v1 | 1.19s | -6.1 | 0.5 | 끝 −11 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % · **CLIP 800** | - | A rough grown man collapsing in death: one low ragged groan that fades into a last breath,… |
| bandit_die | v2 | 1.14s | -7.1 | 0.3 | 끝 −56 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 334** | - | A rough grown man collapsing in death: one low ragged groan that fades into a last breath,… |
| bandit_wake | v1 | 0.79s | -12.8 | 0.1 | 끝 −8 ms · 25 Hz 안 걺(-1.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 196** | - | A rough outlaw spotting an intruder: a sharp hostile snort and a heavy wooden club lifted … |
| bandit_wake | v2 | 0.77s | -10.5 | 0.4 | 끝 −27 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % · **CLIP 7** | - | A rough outlaw spotting an intruder: a sharp hostile snort and a heavy wooden club lifted … |
| talisman_master_hurt | v1 | 0.44s | -11.8 | 0.4 | 끝 −36 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0.4 → 0 % · **CLIP 7** | - | A robed sorcerer struck: a sharp hissed intake of breath and wide silk sleeves snapping, a… |
| talisman_master_hurt | v2 | 0.47s | -11.1 | 0.4 | 끝 −11 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 13** | - | A robed sorcerer struck: a sharp hissed intake of breath and wide silk sleeves snapping, a… |
| talisman_master_die | v1 | 1.27s | -15.6 | 0.1 | 끝 −13 ms · 25 Hz 안 걺(-1.0 LU) · 20 Hz 아래 12.3 → 12.6 % · **CLIP 8** | - | A robed sorcerer falling dead: one long trembling exhale, a body slumping in heavy silk ro… |
| talisman_master_die | v2 | 1.24s | -13.3 | -1.8 | 끝 −39 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 0.7 → 0 % | - | A robed sorcerer falling dead: one long trembling exhale, a body slumping in heavy silk ro… |
| talisman_master_wake | v1 | 0.88s | -10.9 | 0.3 | 끝 −4 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 4.5 → 1 % · **CLIP 15** | - | A dark sorcerer noticing an enemy: a low wordless hum through closed lips and a single pap… |
| talisman_master_wake | v2 | 0.88s | -13.8 | 0.1 | 끝 −3 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 1.5 → 1.5 % · **CLIP 49** | - | A dark sorcerer noticing an enemy: a low wordless hum through closed lips and a single pap… |
| plague_folk_attack | v1 | 0.59s | -17.6 | 0.1 | 끝 −6 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 2** | - | A plague-sick villager lunging to claw: a wet rasping breath pushed out with effort and ra… |
| plague_folk_attack | v2 | 0.58s | -20.0 | -0.9 | 끝 −24 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A plague-sick villager lunging to claw: a wet rasping breath pushed out with effort and ra… |
| plague_folk_hurt | v1 | 0.48s | -28.1 | -8.9 | 끝 −2 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 3.7 → 0 % | - | A plague-sick villager hit: a choked wet cough and a sick rattling breath, no words, close… |
| plague_folk_hurt | v2 | 0.44s | -23.0 | -8.0 | 끝 −39 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 0.9 → 0 % | - | A plague-sick villager hit: a choked wet cough and a sick rattling breath, no words, close… |
| plague_folk_die | v1 | 1.25s | -24.5 | -10.2 | 끝 −27 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.9 → 0.1 % | - | A plague-sick villager dying: a long rattling wet breath that sinks into silence and a lim… |
| plague_folk_die | v2 | 1.27s | -12.3 | -3.1 | 끝 −15 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A plague-sick villager dying: a long rattling wet breath that sinks into silence and a lim… |
| plague_folk_wake | v1 | 0.88s | -23.5 | -9.4 | 끝 −5 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 8.1 → 0.1 % | - | A plague-sick villager turning toward a sound: a slow hoarse wheezing inhale and shuffling… |
| plague_folk_wake | v2 | 0.87s | -14.2 | -3.0 | 끝 −8 ms · 25 Hz(+0.6 LU) · 20 Hz 아래 0.2 → 0 % | - | A plague-sick villager turning toward a sound: a slow hoarse wheezing inhale and shuffling… |
| hollin_yeogung_bow_attack | v1 | 0.52s | -22.3 | -7.8 | 끝 −2 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.3 → 0 % | - | A hunter drawing and releasing a horn bow: creaking bow limbs, a sharp bowstring twang and… |
| hollin_yeogung_bow_attack | v2 | 0.51s | -26.1 | -14.1 | 끝 −13 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 0.8 → 0.1 % | - | A hunter drawing and releasing a horn bow: creaking bow limbs, a sharp bowstring twang and… |
| hollin_yeogung_bow_hurt | v1 | 0.47s | -35.3 | -20.0 | 끝 −8 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.3 → 0 % | - | A bewitched woman archer struck: one sharp breathy gasp, cold and hollow, and a bow knocki… |
| hollin_yeogung_bow_hurt | v2 | 0.47s | -25.9 | -9.4 | 끝 −7 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A bewitched woman archer struck: one sharp breathy gasp, cold and hollow, and a bow knocki… |
| hollin_yeogung_bow_die | v1 | 1.18s | -9.2 | 0.3 | 끝 −21 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.2 → 0.1 % · **CLIP 7** | - | A bewitched woman archer falling dead: a long hollow fading breath, a wooden bow clatterin… |
| hollin_yeogung_bow_die | v2 | 1.19s | -12.1 | -0.3 | 끝 −8 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A bewitched woman archer falling dead: a long hollow fading breath, a wooden bow clatterin… |
| hollin_yeogung_bow_wake | v1 | 0.79s | -19.9 | -9.6 | 끝 −6 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 0.7 → 0.2 % | - | A bewitched archer sensing prey: a slow cold inhale and an arrow drawn from a quiver with … |
| hollin_yeogung_bow_wake | v2 | 0.77s | -17.3 | -7.8 | 끝 −26 ms · 25 Hz(+0.6 LU) · 20 Hz 아래 16.8 → 2.5 % | - | A bewitched archer sensing prey: a slow cold inhale and an arrow drawn from a quiver with … |
| hollin_yeogung_spear_attack | v1 | 0.51s | -14.7 | 0.1 | 끝 −9 ms · 25 Hz 안 걺(-3.3 LU) · 20 Hz 아래 36.5 → 37.9 % · **CLIP 824 · SUB20 38%** | - | A spear thrust hard forward: a fast tight whoosh of a long wooden spear shaft and a short … |
| hollin_yeogung_spear_attack | v2 | 0.49s | -12.6 | 0.1 | 끝 −27 ms · 25 Hz 안 걺(-5.1 LU) · 20 Hz 아래 26.7 → 21.4 % · **CLIP 790 · DC +0.011** | - | A spear thrust hard forward: a fast tight whoosh of a long wooden spear shaft and a short … |
| hollin_yeogung_spear_hurt | v1 | 0.47s | -19.8 | -1.1 | 끝 −8 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 24.5 → 0 % | - | A bewitched woman spear fighter struck: one sharp hollow gasp and a spear shaft knocking a… |
| hollin_yeogung_spear_hurt | v2 | 0.43s | -11.9 | 0.3 | 끝 −53 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.4 → 0.1 % · **CLIP 43** | - | A bewitched woman spear fighter struck: one sharp hollow gasp and a spear shaft knocking a… |
| hollin_yeogung_spear_die | v1 | 1.18s | -8.8 | 0.3 | 끝 −24 ms · 25 Hz 안 걺(-3.2 LU) · 20 Hz 아래 20.8 → 21.2 % · **CLIP 311 · DC +0.014** | - | A bewitched woman spear fighter collapsing: a long hollow fading breath and a heavy wooden… |
| hollin_yeogung_spear_die | v2 | 1.18s | -8.7 | 0.2 | 끝 −22 ms · 25 Hz 안 걺(-1.1 LU) · 20 Hz 아래 10.4 → 10.4 % · **CLIP 61** | - | A bewitched woman spear fighter collapsing: a long hollow fading breath and a heavy wooden… |
| hollin_yeogung_spear_wake | v1 | 0.79s | -10.9 | 0.2 | 끝 −7 ms · 25 Hz 안 걺(-4.0 LU) · 20 Hz 아래 32.7 → 34.9 % · **CLIP 964 · SUB20 35%** | - | A bewitched spear fighter turning to fight: a cold slow inhale and a long spear swung leve… |
| hollin_yeogung_spear_wake | v2 | 0.80s | -12.9 | 0.3 | 끝 −3 ms · 25 Hz 안 걺(-4.0 LU) · 20 Hz 아래 56 → 56.2 % · **CLIP 528 · SUB20 56%** | - | A bewitched spear fighter turning to fight: a cold slow inhale and a long spear swung leve… |
| wolf_attack | v1 | 0.59s | -20.8 | -2.0 | 끝 −10 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % | - | A sick feral dog lunging to bite: a vicious snarl and a hard wet snap of jaws, claws scrap… |
| wolf_attack | v2 | 0.59s | -23.3 | -3.8 | 끝 −6 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | A sick feral dog lunging to bite: a vicious snarl and a hard wet snap of jaws, claws scrap… |
| wolf_hurt | v1 | 0.47s | -10.1 | 0.5 | 끝 −10 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % · **CLIP 171** | - | A sick feral dog hit: one short harsh yelp cut into a growl, close-up, dry, isolated, no m… |
| wolf_hurt | v2 | 0.47s | -14.0 | -0.7 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A sick feral dog hit: one short harsh yelp cut into a growl, close-up, dry, isolated, no m… |
| wolf_die | v1 | 1.04s | -11.2 | 0.3 | 끝 −37 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 39** | - | A sick feral dog dying: a choked rasping growl that fades into a last breath and a body dr… |
| wolf_die | v2 | 1.06s | -10.6 | 0.2 | 끝 −21 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 32** | - | A sick feral dog dying: a choked rasping growl that fades into a last breath and a body dr… |
| wolf_wake | v1 | 0.88s | -8.2 | 0.1 | 끝 그대로 · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.2 → 0.2 % · **CLIP 337** | - | A sick feral dog noticing an intruder: a low rumbling growl rising with wet breath, close-… |
| wolf_wake | v2 | 0.88s | -11.0 | 0.3 | 끝 −5 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 62** | - | A sick feral dog noticing an intruder: a low rumbling growl rising with wet breath, close-… |
| bat_hurt | v1 | 0.46s | -17.3 | -5.3 | 끝 −25 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A large cave bat struck: a short piercing shrill squeak and a jolt of leathery wings, clos… |
| bat_hurt | v2 | 0.47s | -16.8 | -1.6 | 끝 −9 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A large cave bat struck: a short piercing shrill squeak and a jolt of leathery wings, clos… |
| bat_die | v1 | 0.85s | -5.6 | 1.6 | 끝 −26 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 286** | - | A large cave bat killed: a strangled squeak, wings beating weakly and the small body dropp… |
| bat_die | v2 | 0.85s | -12.4 | 1.1 | 끝 −27 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.3 → 0.1 % · **CLIP 31** | - | A large cave bat killed: a strangled squeak, wings beating weakly and the small body dropp… |
| bat_wake | v1 | 0.78s | -18.8 | -8.3 | 끝 −21 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | Cave bats disturbed from a ceiling: sudden leathery wing flutter and rapid high clicking c… |
| bat_wake | v2 | 0.79s | -19.9 | -5.5 | 끝 −8 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | Cave bats disturbed from a ceiling: sudden leathery wing flutter and rapid high clicking c… |
| fox_attack | v1 | 0.46s | -13.5 | 0.8 | 끝 −62 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 49** | - | A shapeshifting demon fox lunging: a quick snapping bite and a twisted eerie fox cry, unna… |
| fox_attack | v2 | 0.50s | -15.5 | 0.5 | 끝 −25 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 21** | - | A shapeshifting demon fox lunging: a quick snapping bite and a twisted eerie fox cry, unna… |
| fox_hurt | v1 | 0.47s | -10.1 | 0.2 | 끝 −6 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 24** | - | A demon fox struck: a short warped yelp with an unnatural metallic edge, close-up, dry, is… |
| fox_hurt | v2 | 0.47s | -18.2 | 0.0 | 끝 −9 ms · 25 Hz 안 걺(-0.9 LU) · 20 Hz 아래 48.8 → 49.2 % · **CLIP 17 · SUB20 49% · DC -0.089** | - | A demon fox struck: a short warped yelp with an unnatural metallic edge, close-up, dry, is… |
| fox_die | v1 | 1.18s | -5.2 | 0.7 | 끝 −24 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 554** | - | A demon fox dying: a distorted fading fox cry that thins into a hiss of breath, then a lig… |
| fox_die | v2 | 1.18s | -4.9 | 0.5 | 끝 −25 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 1110** | - | A demon fox dying: a distorted fading fox cry that thins into a hiss of breath, then a lig… |
| fox_wake | v1 | 0.99s | -8.4 | 0.2 | 끝 −12 ms · 25 Hz 안 걺(-1.2 LU) · 20 Hz 아래 15.6 → 15.6 % · **CLIP 658 · DC +0.039** | - | A demon fox sensing prey in the dark: a single eerie distorted fox bark with an unnatural … |
| fox_wake | v2 | 0.99s | -9.0 | 0.4 | 끝 −10 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 171** | - | A demon fox sensing prey in the dark: a single eerie distorted fox bark with an unnatural … |
| yacha_attack | v1 | 0.63s | -9.8 | 0.3 | 끝 −13 ms · 25 Hz 안 걺(-2.1 LU) · 20 Hz 아래 0.2 → 0.2 % · **CLIP 177** | - | A hulking demon swinging heavy claws: a deep guttural warped growl and a powerful low whoo… |
| yacha_attack | v2 | 0.62s | -6.3 | 0.2 | 끝 −16 ms · 25 Hz 안 걺(-1.4 LU) · 20 Hz 아래 0.5 → 0.5 % · **CLIP 202 · DC -0.016** | - | A hulking demon swinging heavy claws: a deep guttural warped growl and a powerful low whoo… |
| yacha_hurt | v1 | 0.47s | -10.2 | 0.0 | 끝 −15 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.4 → 0.4 % · **CLIP 35** | - | A hulking demon struck: a short deep distorted bellow of pain, guttural and inhuman, close… |
| yacha_hurt | v2 | 0.47s | -10.4 | 0.0 | 끝 −13 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.1 → 0.1 % · **CLIP 24** | - | A hulking demon struck: a short deep distorted bellow of pain, guttural and inhuman, close… |
| yacha_die | v1 | 1.35s | -7.0 | 0.2 | 끝 −11 ms · 25 Hz 안 걺(-2.6 LU) · 20 Hz 아래 0.1 → 0.1 % · **CLIP 1208** | - | A hulking demon dying: a long deep warped groan collapsing into a rattle, then a massive b… |
| yacha_die | v2 | 1.35s | -8.5 | 0.1 | 끝 −11 ms · 25 Hz 안 걺(-1.5 LU) · 20 Hz 아래 0.2 → 0.2 % · **CLIP 861** | - | A hulking demon dying: a long deep warped groan collapsing into a rattle, then a massive b… |
| yacha_wake | v1 | 0.99s | -16.7 | -2.5 | 끝 −9 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 0.2 → 0.2 % | - | A hulking demon rousing: a deep slow inhuman rumbling growl and heavy feet shifting on sto… |
| yacha_wake | v2 | 0.99s | -14.1 | -2.2 | 끝 −10 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 5.2 → 1.6 % | - | A hulking demon rousing: a deep slow inhuman rumbling growl and heavy feet shifting on sto… |
| agwi_attack | v1 | 0.59s | -18.1 | -4.8 | 끝 −11 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.6 → 0 % | - | A starving hungry ghost lunging to bite: wet ravenous gnashing teeth and a hollow rasping … |
| agwi_attack | v2 | 0.59s | -15.4 | -1.7 | 끝 −8 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % | - | A starving hungry ghost lunging to bite: wet ravenous gnashing teeth and a hollow rasping … |
| agwi_hurt | v1 | 0.47s | -14.3 | -0.3 | 끝 −9 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A starving hungry ghost struck: a dry hollow choking rasp, close-up, dry, isolated, no mus… |
| agwi_hurt | v2 | 0.44s | -13.1 | 0.6 | 끝 −40 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.4 → 0.1 % · **CLIP 22** | - | A starving hungry ghost struck: a dry hollow choking rasp, close-up, dry, isolated, no mus… |
| agwi_die | v1 | 1.18s | -13.0 | -0.8 | 끝 −25 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A starving hungry ghost dying: a long hollow empty-stomach groan that withers into a dry r… |
| agwi_die | v2 | 1.19s | -15.1 | -1.9 | 끝 −13 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A starving hungry ghost dying: a long hollow empty-stomach groan that withers into a dry r… |
| agwi_wake | v1 | 0.86s | -14.8 | -3.3 | 끝 −17 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | A starving hungry ghost smelling food: a slow wet sniffing and a hollow growling stomach w… |
| agwi_wake | v2 | 0.88s | -9.4 | 0.3 | 끝 −5 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 13** | - | A starving hungry ghost smelling food: a slow wet sniffing and a hollow growling stomach w… |
| centipede_attack | v1 | 0.49s | -9.9 | 1.1 | 끝 −28 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 0.3 → 0 % · **CLIP 104** | - | A giant centipede striking: rapid skittering legs on stone and a sharp hard mandible snap … |
| centipede_attack | v2 | 0.51s | -11.7 | 0.6 | 끝 −6 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 7.2 → 8 % · **CLIP 20** | - | A giant centipede striking: rapid skittering legs on stone and a sharp hard mandible snap … |
| centipede_hurt | v1 | 0.48s | -18.5 | 0.3 | 끝 −2 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0.3 → 0 % · **CLIP 5** | - | A giant centipede struck: a cracking chitin shell and a harsh dry hiss, close-up, dry, iso… |
| centipede_hurt | v2 | 0.47s | -16.4 | 1.0 | 끝 −9 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 12** | - | A giant centipede struck: a cracking chitin shell and a harsh dry hiss, close-up, dry, iso… |
| centipede_die | v1 | 1.18s | -15.6 | -0.0 | 끝 −17 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 1** | - | A giant centipede dying: frantic legs scrabbling on stone that slow to a few last twitches… |
| centipede_die | v2 | 1.19s | -13.6 | -4.8 | 끝 −12 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % | - | A giant centipede dying: frantic legs scrabbling on stone that slow to a few last twitches… |
| centipede_wake | v1 | 0.87s | -19.4 | -0.8 | 끝 −15 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 7.4 → 0.3 % | - | A giant centipede stirring: a ripple of many legs clicking on stone rising in speed and a … |
| centipede_wake | v2 | 0.85s | -26.5 | -4.6 | 끝 −34 ms · 25 Hz(+0.9 LU) · 20 Hz 아래 1.3 → 0.1 % | - | A giant centipede stirring: a ripple of many legs clicking on stone rising in speed and a … |
| locust_attack | v1 | 0.56s | -11.2 | 2.3 | 끝 −42 ms · 25 Hz(+0.7 LU) · 20 Hz 아래 45.5 → 15.2 % · **CLIP 85** | - | A swarm of locusts rushing in: a sudden surge of dense buzzing wings sweeping past, close-… |
| locust_attack | v2 | 0.59s | -15.7 | 0.7 | 끝 −12 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 87.1 → 87.4 % · **CLIP 341 · SUB20 87% · DC -0.104** | - | A swarm of locusts rushing in: a sudden surge of dense buzzing wings sweeping past, close-… |
| locust_hurt | v1 | 0.48s | -21.6 | -2.1 | 끝 그대로 · 25 Hz(+0.0 LU) · 20 Hz 아래 22.2 → 0.1 % | - | A locust swarm struck: the buzzing breaks apart with sharp crackling clicks, close-up, dry… |
| locust_hurt | v2 | 0.48s | -13.9 | 0.9 | 끝 −5 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 5.9 → 0 % · **CLIP 3** | - | A locust swarm struck: the buzzing breaks apart with sharp crackling clicks, close-up, dry… |
| locust_die | v1 | 1.07s | -9.5 | -0.6 | 끝 −10 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A locust swarm scattering and dying: buzzing dispersing into silence and dry husks patteri… |
| locust_die | v2 | 1.07s | -8.2 | 0.9 | 끝 −7 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.4 → 0 % · **CLIP 5** | - | A locust swarm scattering and dying: buzzing dispersing into silence and dry husks patteri… |
| locust_wake | v1 | 0.99s | -15.8 | -6.2 | 끝 −10 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A locust swarm rising: a low insect drone swelling quickly into dense buzzing wings, close… |
| locust_wake | v2 | 0.99s | -12.1 | -3.0 | 끝 −12 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A locust swarm rising: a low insect drone swelling quickly into dense buzzing wings, close… |
| spider_attack | v1 | 0.48s | -14.6 | -0.4 | 끝 −39 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 1.2 → 0.1 % | - | A huge old spider pouncing: fast hard legs tapping stone and a sharp fang strike with a we… |
| spider_attack | v2 | 0.51s | -16.8 | 0.2 | 끝 −6 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 1.8 → 1.8 % · **CLIP 29** | - | A huge old spider pouncing: fast hard legs tapping stone and a sharp fang strike with a we… |
| spider_hurt | v1 | 0.42s | -12.7 | 1.0 | 끝 −63 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 3.6 → 0 % · **CLIP 3** | - | A huge spider struck: a dry chitin crack and a sharp hiss, close-up, dry, isolated, no mus… |
| spider_hurt | v2 | 0.47s | -18.9 | 0.0 | 끝 −8 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 1.1 → 0 % · **CLIP 2** | - | A huge spider struck: a dry chitin crack and a sharp hiss, close-up, dry, isolated, no mus… |
| spider_die | v1 | 1.20s | -21.4 | 0.4 | 끝 그대로 · 25 Hz(+0.0 LU) · 20 Hz 아래 2.3 → 0 % · **CLIP 4** | - | A huge spider dying: legs curling with dry cracking and twitching taps, a fading hiss and … |
| spider_die | v2 | 1.19s | -18.8 | 0.6 | 끝 −7 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 4.6 → 0.2 % · **CLIP 3** | - | A huge spider dying: legs curling with dry cracking and twitching taps, a fading hiss and … |
| spider_wake | v1 | 0.86s | -19.6 | 1.2 | 끝 −20 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 1** | - | A huge spider stirring in its web: taut silk threads creaking and slow leg taps on stone, … |
| spider_wake | v2 | 0.82s | -18.4 | -2.3 | 끝 −59 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.3 → 0 % | - | A huge spider stirring in its web: taut silk threads creaking and slow leg taps on stone, … |
| soemeogi_attack | v1 | 0.60s | -15.7 | -0.8 | 끝 −5 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 1.4 → 0 % | - | An iron-eating demon biting: grinding iron teeth and a harsh metal scrape, heavy and gritt… |
| soemeogi_attack | v2 | 0.58s | -13.5 | -0.4 | 끝 −20 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.9 → 0.1 % | - | An iron-eating demon biting: grinding iron teeth and a harsh metal scrape, heavy and gritt… |
| soemeogi_hurt | v1 | 0.48s | -14.3 | -0.1 | 끝 −5 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | An iron-eating demon struck: a clanking metal hide and a short grinding screech of iron, c… |
| soemeogi_hurt | v2 | 0.47s | -14.4 | 0.3 | 끝 −6 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 9** | - | An iron-eating demon struck: a clanking metal hide and a short grinding screech of iron, c… |
| soemeogi_die | v1 | 1.27s | -8.5 | 0.1 | 끝 −7 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 0 → 0 % · **CLIP 73** | - | An iron-eating demon dying: a long iron groan like bending metal, scraps of iron clatterin… |
| soemeogi_die | v2 | 1.26s | -6.6 | 0.1 | 끝 −17 ms · 25 Hz 안 걺(-0.9 LU) · 20 Hz 아래 0 → 0 % · **CLIP 952** | - | An iron-eating demon dying: a long iron groan like bending metal, scraps of iron clatterin… |
| soemeogi_wake | v1 | 0.86s | -23.9 | -10.2 | 끝 −22 ms · 25 Hz(+1.6 LU) · 20 Hz 아래 0 → 0 % | - | An iron-eating demon rousing: slow grinding teeth on iron and a low metallic rumble, close… |
| soemeogi_wake | v2 | 0.86s | -18.3 | -0.5 | 끝 −23 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 2.9 → 0.7 % | - | An iron-eating demon rousing: slow grinding teeth on iron and a low metallic rumble, close… |
| imugi_attack | v1 | 0.67s | -11.6 | 0.1 | 끝 −12 ms · 25 Hz 안 걺(-2.1 LU) · 20 Hz 아래 2.4 → 2.4 % · **CLIP 106** | - | A giant serpent striking: a heavy coiled body lunging with a deep hiss and wet scales slid… |
| imugi_attack | v2 | 0.68s | -13.6 | 0.0 | 끝 −4 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0 → 0 % · **CLIP 36** | - | A giant serpent striking: a heavy coiled body lunging with a deep hiss and wet scales slid… |
| imugi_hurt | v1 | 0.47s | -18.2 | -2.0 | 끝 −11 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.3 → 0 % | - | A giant serpent struck: a short deep pained hiss and thick scales jolting, close-up, dry, … |
| imugi_hurt | v2 | 0.45s | -16.0 | 0.6 | 끝 −29 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 16** | - | A giant serpent struck: a short deep pained hiss and thick scales jolting, close-up, dry, … |
| imugi_die | v1 | 1.47s | -10.8 | 0.2 | 끝 −9 ms · 25 Hz 안 걺(-0.9 LU) · 20 Hz 아래 0.3 → 0.3 % · **CLIP 284** | - | A giant serpent dying: a long deep hiss draining away, a massive body thrashing then slidi… |
| imugi_die | v2 | 1.46s | -8.7 | 0.7 | 끝 −25 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % · **CLIP 292** | - | A giant serpent dying: a long deep hiss draining away, a massive body thrashing then slidi… |
| imugi_wake | v1 | 1.07s | -17.9 | -5.9 | 끝 −9 ms · 25 Hz(+0.7 LU) · 20 Hz 아래 0.3 → 0 % | - | A giant serpent waking in dark water: a deep low rumble, water stirring and heavy scales d… |
| imugi_wake | v2 | 1.07s | -20.1 | -0.5 | 끝 −10 ms · 25 Hz(+1.0 LU) · 20 Hz 아래 30 → 8 % | - | A giant serpent waking in dark water: a deep low rumble, water stirring and heavy scales d… |
| nachalnyeo_attack | v1 | 0.58s | -5.2 | 0.3 | 끝 −17 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 261** | - | A female demon slashing with long claws: a fast whoosh and a cold breathy hiss, menacing n… |
| nachalnyeo_attack | v2 | 0.59s | -8.6 | 0.4 | 끝 −7 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 335** | - | A female demon slashing with long claws: a fast whoosh and a cold breathy hiss, menacing n… |
| nachalnyeo_hurt | v1 | 0.45s | -12.2 | -0.8 | 끝 −35 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | A female demon struck: a sharp cold hiss through teeth, inhuman, wordless, close-up, dry, … |
| nachalnyeo_hurt | v2 | 0.42s | -12.1 | 0.1 | 끝 −59 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.3 → 0 % · **CLIP 1** | - | A female demon struck: a sharp cold hiss through teeth, inhuman, wordless, close-up, dry, … |
| nachalnyeo_die | v1 | 1.27s | -5.4 | 0.7 | 끝 −14 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 806** | - | A female demon dying: a long warped hissing breath that frays into a dry rattle, bone orna… |
| nachalnyeo_die | v2 | 1.26s | -7.5 | 0.5 | 끝 −17 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 194** | - | A female demon dying: a long warped hissing breath that frays into a dry rattle, bone orna… |
| nachalnyeo_wake | v1 | 0.99s | -10.1 | 0.3 | 끝 −10 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 39** | - | A female demon noticing prey: a slow cold breathy inhale and a faint rattle of bone orname… |
| nachalnyeo_wake | v2 | 0.97s | -6.3 | 0.3 | 끝 −35 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 63** | - | A female demon noticing prey: a slow cold breathy inhale and a faint rattle of bone orname… |
| honbul_attack | v1 | 0.51s | -14.7 | 1.7 | 끝 −7 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.4 → 0.1 % · **CLIP 33** | - | A ghostly spirit flame darting to strike: a soft rushing whoosh of fire with an eerie airy… |
| honbul_attack | v2 | 0.51s | -15.2 | -1.0 | 끝 −15 ms · 25 Hz 안 걺(-1.2 LU) · 20 Hz 아래 6.5 → 6.5 % · **DC -0.014** | - | A ghostly spirit flame darting to strike: a soft rushing whoosh of fire with an eerie airy… |
| honbul_hurt | v1 | 0.47s | -16.4 | -1.4 | 끝 −11 ms · 25 Hz 안 걺(-1.3 LU) · 20 Hz 아래 9.8 → 9.7 % · **DC -0.010** | - | A ghostly spirit flame struck: a sputtering flicker of fire and a thin eerie whine, close-… |
| honbul_hurt | v2 | 0.45s | -14.6 | -0.6 | 끝 −31 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 12 → 0.1 % | - | A ghostly spirit flame struck: a sputtering flicker of fire and a thin eerie whine, close-… |
| honbul_die | v1 | 1.03s | -10.8 | 1.6 | 끝 −47 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0 → 0 % · **CLIP 127** | - | A ghostly spirit flame going out: a fading breathy whoosh of fire guttering into a soft hi… |
| honbul_die | v2 | 1.06s | -11.7 | 0.5 | 끝 −22 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 0 → 0 % · **CLIP 11** | - | A ghostly spirit flame going out: a fading breathy whoosh of fire guttering into a soft hi… |
| honbul_wake | v1 | 0.87s | -24.3 | -9.0 | 끝 −8 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0.1 → 0 % | - | A ghostly spirit flame igniting in the dark: a soft flare of fire and a low eerie hovering… |
| honbul_wake | v2 | 0.87s | -17.1 | -3.4 | 끝 −9 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0 → 0 % | - | A ghostly spirit flame igniting in the dark: a soft flare of fire and a low eerie hovering… |
| wonhon_attack | v1 | 0.59s | -14.6 | 0.3 | 끝 −10 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 12.8 → 2.4 % · **CLIP 1** | - | A vengeful ghost lashing out: a cold sudden gust of wind with a faint metal bell shiver, e… |
| wonhon_attack | v2 | 0.60s | -15.5 | -0.3 | 끝 −3 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % | - | A vengeful ghost lashing out: a cold sudden gust of wind with a faint metal bell shiver, e… |
| wonhon_hurt | v1 | 0.45s | -8.8 | 0.3 | 끝 −27 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 31** | - | A vengeful ghost struck: a hollow whistling wind jolt and a small bell rattle, eerie, clos… |
| wonhon_hurt | v2 | 0.47s | -10.1 | 0.3 | 끝 −12 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 6** | - | A vengeful ghost struck: a hollow whistling wind jolt and a small bell rattle, eerie, clos… |
| wonhon_die | v1 | 1.27s | -24.2 | -10.3 | 끝 −12 ms · 25 Hz(+0.8 LU) · 20 Hz 아래 0 → 0 % | - | A vengeful ghost dispersing: a long hollow wind sighing away with a fading small bell, eer… |
| wonhon_die | v2 | 1.27s | -39.4 | -27.7 | 끝 −12 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.3 → 0.3 % | - | A vengeful ghost dispersing: a long hollow wind sighing away with a fading small bell, eer… |
| wonhon_wake | v1 | 0.99s | -25.2 | -9.2 | 끝 −9 ms · 25 Hz(+1.1 LU) · 20 Hz 아래 7.2 → 1.1 % | - | A vengeful ghost stirring: a cold low wind rising through a cave and a faint single bell, … |
| wonhon_wake | v2 | 0.99s | -23.2 | -15.0 | 끝 −8 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 8.1 → 0.3 % | - | A vengeful ghost stirring: a cold low wind rising through a cave and a faint single bell, … |
| sobok_gwisin_attack | v1 | 0.58s | -6.4 | -0.4 | 끝 −24 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A white-robed female ghost reaching out: a cold rush of wind, wet hemp cloth flapping and … |
| sobok_gwisin_attack | v2 | 0.58s | -11.3 | 0.1 | 끝 −20 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 7** | - | A white-robed female ghost reaching out: a cold rush of wind, wet hemp cloth flapping and … |
| sobok_gwisin_hurt | v1 | 0.48s | -13.2 | -1.4 | 끝 −4 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.5 → 0 % | - | A white-robed female ghost struck: a hollow breathy gasp in the wind and a splash of dripp… |
| sobok_gwisin_hurt | v2 | 0.47s | -19.4 | -6.8 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A white-robed female ghost struck: a hollow breathy gasp in the wind and a splash of dripp… |
| sobok_gwisin_die | v1 | 1.27s | -12.4 | -4.5 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A white-robed female ghost fading away: a long cold sigh of wind, wet cloth settling and w… |
| sobok_gwisin_die | v2 | 1.26s | -18.1 | -9.3 | 끝 −19 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 0 → 0 % | - | A white-robed female ghost fading away: a long cold sigh of wind, wet cloth settling and w… |
| sobok_gwisin_wake | v1 | 0.99s | -26.3 | -15.7 | 끝 −10 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.7 → 0 % | - | A white-robed female ghost appearing: a faint cold wind, slow water dripping in a dark cav… |
| sobok_gwisin_wake | v2 | 0.99s | -34.5 | -19.7 | 끝 −11 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.4 → 0 % | - | A white-robed female ghost appearing: a faint cold wind, slow water dripping in a dark cav… |
| elite_wake | v1 | 1.19s | -45.4 | -31.8 | 끝 −7 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 0.2 → 0 % | - | A single deep low hit on a large Korean barrel drum (buk), one strike with a short dark re… |
| elite_wake | v2 | 1.19s | -45.8 | -30.3 | 끝 −7 ms · 25 Hz(+0.7 LU) · 20 Hz 아래 0.1 → 0 % | - | A single deep low hit on a large Korean barrel drum (buk), one strike with a short dark re… |
| leader_wake | v1 | 1.99s | -6.3 | 1.2 | 끝 −10 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 0 → 0 % · **CLIP 844** | - | A single strike on a large Korean jing gong, deep and dark with a long shimmering wavering… |
| leader_wake | v2 | 1.99s | -12.1 | 0.3 | 끝 −15 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 4** | - | A single strike on a large Korean jing gong, deep and dark with a long shimmering wavering… |
| drop_magic | v1 | 0.46s | -18.0 | -3.1 | 끝 −20 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.1 → 0 % | - | A small jade bead dropping onto stone: one clear bright crystalline tink with a tiny glass… |
| drop_magic | v2 | 0.45s | -23.8 | -11.0 | 끝 −28 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % | - | A small jade bead dropping onto stone: one clear bright crystalline tink with a tiny glass… |
| drop_rare | v1 | 0.99s | -25.2 | -14.3 | 끝 −13 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A single small brass temple wind bell struck once: a warm golden ding with a 0.8 second ri… |
| drop_rare | v2 | 0.99s | -13.0 | -2.8 | 끝 −13 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A single small brass temple wind bell struck once: a warm golden ding with a 0.8 second ri… |
| drop_unique | v1 | 1.35s | -45.8 | -30.7 | 끝 −8 ms · 25 Hz(+1.1 LU) · 20 Hz 아래 0.1 → 0 % | - | A short dark ceremonial reveal: one deep Korean buk drum hit, a bright brass temple bell a… |
| drop_unique | v2 | 1.34s | -39.4 | -22.6 | 끝 −23 ms · 25 Hz(+0.7 LU) · 20 Hz 아래 1.6 → 0.1 % | - | A short dark ceremonial reveal: one deep Korean buk drum hit, a bright brass temple bell a… |
