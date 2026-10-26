
## #942 전투 효과음 후보 S1~S6

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100. 구독 크레딧 1459.
`<큐>_vN.wav` = 손질본(끝 딸깍 자름 · 25 Hz 고역 통과, 32-bit float) · 날것 = `<큐>/_raw/` (design/audio.md §4.5.1, #399). 길이·LUFS·피크 = 손질본.

| 큐 | 변주 | 길이 | LUFS | 피크 | 손질·흠 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|---|
| sword_swing | v1 | 0.47s | -15.0 | 1.3 | 끝 −10 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 6.3 → 1.5 % · **CLIP 55** | - | Single fast steel sword slash cutting through air, sharp dry airy whoosh with a thin blade… |
| sword_swing | v2 | 0.45s | -12.1 | 4.8 | 끝 −27 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 2.5 → 0.5 % · **CLIP 383** | - | Single fast steel sword slash cutting through air, sharp dry airy whoosh with a thin blade… |
| sword_swing | v3 | 0.47s | -18.2 | 0.3 | 끝 −7 ms · 25 Hz 안 걺(-3.5 LU) · 20 Hz 아래 10.4 → 11.4 % · **CLIP 351 · DC -0.014** | - | Single fast steel sword slash cutting through air, sharp dry airy whoosh with a thin blade… |
| sword_swing | v4 | 0.47s | -14.1 | 0.6 | 끝 −10 ms · 25 Hz 안 걺(-2.5 LU) · 20 Hz 아래 58.8 → 60.3 % · **CLIP 393 · SUB20 60% · DC -0.027** | - | Single fast steel sword slash cutting through air, sharp dry airy whoosh with a thin blade… |
| hit | v1 | 0.45s | -11.2 | 0.1 | 끝 −33 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 2.1 → 0.1 % | - | One sword blade slicing into a monster's flesh body: tight wet meaty thud with a short sha… |
| hit | v2 | 0.47s | -11.4 | -0.5 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.2 → 0 % | - | One sword blade slicing into a monster's flesh body: tight wet meaty thud with a short sha… |
| hit | v3 | 0.47s | -12.0 | -0.1 | 끝 −10 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.9 → 0.1 % | - | One sword blade slicing into a monster's flesh body: tight wet meaty thud with a short sha… |
| hit | v4 | 0.48s | -12.1 | 0.2 | 끝 그대로 · 25 Hz(-0.0 LU) · 20 Hz 아래 1.9 → 0.3 % | - | One sword blade slicing into a monster's flesh body: tight wet meaty thud with a short sha… |
| hit_crit | v1 | 0.67s | -9.8 | 2.3 | 끝 −11 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 8.7 → 1 % · **CLIP 52** | - | One powerful critical sword strike tearing through a body: crisp steel crack layered on a … |
| hit_crit | v2 | 0.67s | -8.1 | 1.1 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 37** | - | One powerful critical sword strike tearing through a body: crisp steel crack layered on a … |
| hit_crit | v3 | 0.67s | -8.3 | 0.8 | 끝 −10 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 17** | - | One powerful critical sword strike tearing through a body: crisp steel crack layered on a … |
| whiff | v1 | 0.47s | -36.9 | -14.5 | 끝 −13 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 44.1 → 19.6 % | - | A sword swing missing its target and cutting only empty air: short breathy whoosh with a f… |
| whiff | v2 | 0.47s | -14.4 | 0.4 | 끝 −7 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 28** | - | A sword swing missing its target and cutting only empty air: short breathy whoosh with a f… |
| whiff | v3 | 0.47s | -17.7 | 2.2 | 끝 −10 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 3 → 0.7 % · **CLIP 64** | - | A sword swing missing its target and cutting only empty air: short breathy whoosh with a f… |
| doho_kiai | v1 | 0.47s | -9.3 | -0.2 | 끝 −10 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % | - | A confident young Korean swordsman's single short sharp battle kiai shout as he swings, on… |
| doho_kiai | v2 | 0.48s | -8.3 | 0.5 | 끝 −5 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 187** | - | A confident young Korean swordsman's single short sharp battle kiai shout as he swings, on… |
| doho_kiai | v3 | 0.46s | -8.0 | 0.4 | 끝 −25 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 178** | - | A confident young Korean swordsman's single short sharp battle kiai shout as he swings, on… |
| doho_kiai | v4 | 0.44s | -7.9 | 0.3 | 끝 −43 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 122** | - | A confident young Korean swordsman's single short sharp battle kiai shout as he swings, on… |
| player_hurt | v1 | 0.41s | -24.6 | -6.9 | 끝 −69 ms · 25 Hz(+3.9 LU) · 20 Hz 아래 86.1 → 22.4 % · **CLIP 5** | - | A heavy blow landing on a man wearing a thick cloth robe: dull blunt body impact thud with… |
| player_hurt | v2 | 0.47s | -21.1 | -2.4 | 끝 −14 ms · 25 Hz(+1.2 LU) · 20 Hz 아래 20.9 → 6.9 % | - | A heavy blow landing on a man wearing a thick cloth robe: dull blunt body impact thud with… |
| player_hurt | v3 | 0.47s | -22.3 | -3.0 | 끝 −10 ms · 25 Hz(+2.1 LU) · 20 Hz 아래 51.5 → 16.7 % · **CLIP 176** | - | A heavy blow landing on a man wearing a thick cloth robe: dull blunt body impact thud with… |
| player_hurt | v4 | 0.41s | -16.3 | 0.3 | 끝 −69 ms · 25 Hz 안 걺(-6.1 LU) · 20 Hz 아래 29.5 → 37.6 % · **CLIP 725 · SUB20 38%** | - | A heavy blow landing on a man wearing a thick cloth robe: dull blunt body impact thud with… |
| enemy_attack | v1 | 0.59s | -10.1 | 0.1 | 끝 −15 ms · 25 Hz 안 걺(-1.9 LU) · 20 Hz 아래 1.2 → 1.2 % · **CLIP 187** | - | A monster rearing back to strike: deep low guttural snarl-breath and a heavy limb whooshin… |
| enemy_attack | v2 | 0.59s | -9.3 | 0.1 | 끝 −14 ms · 25 Hz 안 걺(-3.6 LU) · 20 Hz 아래 0.6 → 0.6 % · **CLIP 324** | - | A monster rearing back to strike: deep low guttural snarl-breath and a heavy limb whooshin… |
| enemy_attack | v3 | 0.58s | -10.5 | 0.1 | 끝 −25 ms · 25 Hz 안 걺(-1.5 LU) · 20 Hz 아래 0.1 → 0.1 % · **CLIP 31** | - | A monster rearing back to strike: deep low guttural snarl-breath and a heavy limb whooshin… |
| enemy_attack | v4 | 0.53s | -11.6 | 0.0 | 끝 −68 ms · 25 Hz 안 걺(-2.0 LU) · 20 Hz 아래 0.9 → 1 % · **CLIP 48** | - | A monster rearing back to strike: deep low guttural snarl-breath and a heavy limb whooshin… |
| enemy_hurt | v1 | 0.45s | -14.5 | -1.4 | 끝 −27 ms · 25 Hz(+0.5 LU) · 20 Hz 아래 0.3 → 0.1 % | - | A dark creature struck by a blade: one short pained guttural grunt-growl with a wet flinch… |
| enemy_hurt | v2 | 0.47s | -13.1 | -1.8 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A dark creature struck by a blade: one short pained guttural grunt-growl with a wet flinch… |
| enemy_hurt | v3 | 0.46s | -15.3 | -1.9 | 끝 −25 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.1 → 0 % | - | A dark creature struck by a blade: one short pained guttural grunt-growl with a wet flinch… |
| enemy_hurt | v4 | 0.46s | -13.8 | -0.3 | 끝 −24 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.9 → 0.1 % | - | A dark creature struck by a blade: one short pained guttural grunt-growl with a wet flinch… |
| enemy_die | v1 | 0.88s | -15.9 | -4.8 | 끝 −5 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A dark creature dying: one low ragged dying groan that chokes off into a last rattling bre… |
| enemy_die | v2 | 0.85s | -16.7 | -2.2 | 끝 −28 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.1 → 0 % | - | A dark creature dying: one low ragged dying groan that chokes off into a last rattling bre… |
| enemy_die | v3 | 0.86s | -17.2 | -3.8 | 끝 −19 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % | - | A dark creature dying: one low ragged dying groan that chokes off into a last rattling bre… |
| shoot | v1 | 0.46s | -11.2 | 0.8 | 끝 −23 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 4.7 → 1.1 % · **CLIP 28** | - | A projectile released hard toward the player: quick sharp release snap and a short rushing… |
| shoot | v2 | 0.45s | -20.2 | 0.4 | 끝 −27 ms · 25 Hz 안 걺(-2.0 LU) · 20 Hz 아래 57.1 → 67 % · **CLIP 397 · SUB20 67% · DC -0.018** | - | A projectile released hard toward the player: quick sharp release snap and a short rushing… |
| shoot | v3 | 0.44s | -11.1 | 0.5 | 끝 −42 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.8 → 0.8 % · **CLIP 29** | - | A projectile released hard toward the player: quick sharp release snap and a short rushing… |
| shoot | v4 | 0.48s | -16.0 | 0.4 | 끝 −3 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 6 → 6.2 % · **CLIP 44** | - | A projectile released hard toward the player: quick sharp release snap and a short rushing… |
| skill_slash | v1 | 0.58s | -10.3 | 0.7 | 끝 −22 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 6** | - | One forceful sword draw and wide sweeping air cut, accented with a tiny plucked Korean gay… |
| skill_slash | v2 | 0.58s | -9.2 | 0.7 | 끝 −23 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 11** | - | One forceful sword draw and wide sweeping air cut, accented with a tiny plucked Korean gay… |
| skill_slash | v3 | 0.57s | -11.8 | 0.6 | 끝 −33 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 9** | - | One forceful sword draw and wide sweeping air cut, accented with a tiny plucked Korean gay… |
| skill_slash_impact | v1 | 0.48s | -10.8 | -0.4 | 끝 −2 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A wide sword arc slicing through several bodies at once: layered sharp steel bites over a … |
| skill_slash_impact | v2 | 0.45s | -11.0 | 1.1 | 끝 −26 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 14** | - | A wide sword arc slicing through several bodies at once: layered sharp steel bites over a … |
| skill_slash_impact | v3 | 0.45s | -12.9 | 0.7 | 끝 −29 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 2** | - | A wide sword arc slicing through several bodies at once: layered sharp steel bites over a … |
| skill_dash_strike | v1 | 0.58s | -10.7 | -0.9 | 끝 −23 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A swordsman lunging forward at high speed: rushing air burst and cloth flutter ending in a… |
| skill_dash_strike | v2 | 0.58s | -11.9 | 0.5 | 끝 −23 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 1** | - | A swordsman lunging forward at high speed: rushing air burst and cloth flutter ending in a… |
| skill_dash_strike | v3 | 0.58s | -10.0 | 0.8 | 끝 −22 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.2 → 0 % | - | A swordsman lunging forward at high speed: rushing air burst and cloth flutter ending in a… |
| skill_dash_strike_impact | v1 | 0.47s | -10.9 | 1.2 | 끝 −8 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 8** | - | A charging sword thrust ramming into a body: heavy punchy stab impact with a crisp steel c… |
| skill_dash_strike_impact | v2 | 0.45s | -10.8 | 0.7 | 끝 −26 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 6** | - | A charging sword thrust ramming into a body: heavy punchy stab impact with a crisp steel c… |
| skill_dash_strike_impact | v3 | 0.47s | -10.5 | 0.4 | 끝 −11 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.7 → 0.8 % · **CLIP 67** | - | A charging sword thrust ramming into a body: heavy punchy stab impact with a crisp steel c… |
| skill_whirl_impact | v1 | 0.47s | -17.1 | -0.5 | 끝 −12 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 3.3 → 0 % | - | A spinning sword sweep cutting into surrounding bodies: fast rolling series of two or thre… |
| skill_whirl_impact | v2 | 0.47s | -13.1 | 0.5 | 끝 −10 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 17** | - | A spinning sword sweep cutting into surrounding bodies: fast rolling series of two or thre… |
| skill_whirl_impact | v3 | 0.41s | -16.2 | -1.0 | 끝 −72 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 2.7 → 0.2 % | - | A spinning sword sweep cutting into surrounding bodies: fast rolling series of two or thre… |
| talisman_cold_burst | v1 | 0.78s | -16.7 | 0.4 | 끝 −25 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.5 → 0 % · **CLIP 6** | - | Sudden localized freezing burst from a paper talisman: crisp ice crack and crystalline cru… |
| talisman_cold_burst | v2 | 0.79s | -11.0 | 0.9 | 끝 −10 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 23** | - | Sudden localized freezing burst from a paper talisman: crisp ice crack and crystalline cru… |
| talisman_cold_burst | v3 | 0.79s | -14.7 | 0.5 | 끝 −9 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 13** | - | Sudden localized freezing burst from a paper talisman: crisp ice crack and crystalline cru… |
| boss_heukrang_attack | v1 | 0.87s | -21.4 | 0.8 | 끝 −10 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 8.3 → 1.5 % | - | A huge black fire wolf gathering itself to lunge and bite: deep guttural rumbling snarl wi… |
| boss_heukrang_attack | v2 | 0.86s | -15.0 | -0.5 | 끝 −25 ms · 25 Hz 안 걺(-1.2 LU) · 20 Hz 아래 6.2 → 7.2 % | - | A huge black fire wolf gathering itself to lunge and bite: deep guttural rumbling snarl wi… |
| boss_heukrang_attack | v3 | 0.86s | -19.2 | -1.3 | 끝 −19 ms · 25 Hz 안 걺(-1.4 LU) · 20 Hz 아래 0 → 0.1 % | - | A huge black fire wolf gathering itself to lunge and bite: deep guttural rumbling snarl wi… |
| bandit_attack | v1 | 0.59s | -17.2 | -0.2 | 끝 −8 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 71.9 → 16.5 % · **CLIP 327** | - | A ragged bandit heaving a heavy wooden club over his shoulder to strike: deep low whoosh o… |
| bandit_attack | v2 | 0.59s | -18.6 | -1.9 | 끝 −7 ms · 25 Hz(+0.9 LU) · 20 Hz 아래 27.4 → 14.7 % · **CLIP 3** | - | A ragged bandit heaving a heavy wooden club over his shoulder to strike: deep low whoosh o… |
| bandit_attack | v3 | 0.59s | -16.4 | -1.2 | 끝 −15 ms · 25 Hz(+2.8 LU) · 20 Hz 아래 75.3 → 22.2 % · **CLIP 60** | - | A ragged bandit heaving a heavy wooden club over his shoulder to strike: deep low whoosh o… |
| talisman_master_attack | v1 | 0.59s | -22.7 | -2.7 | 끝 −13 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.3 → 0 % | - | A dark sorcerer snapping paper talismans out of a wide silk sleeve: quick dry paper flutte… |
| talisman_master_attack | v2 | 0.59s | -23.0 | -5.5 | 끝 −12 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 0.2 → 0 % | - | A dark sorcerer snapping paper talismans out of a wide silk sleeve: quick dry paper flutte… |
| talisman_master_attack | v3 | 0.60s | -17.4 | -2.8 | 끝 −5 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.4 → 0.1 % | - | A dark sorcerer snapping paper talismans out of a wide silk sleeve: quick dry paper flutte… |
| hit_iron | v1 | 0.47s | -12.6 | 1.1 | 끝 −11 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 4.7 → 0.7 % · **CLIP 17** | - | A sword blade striking a monster made of rusty iron: hard metallic clang with a gritty scr… |
| hit_iron | v2 | 0.45s | -12.0 | 0.7 | 끝 −30 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 0.4 → 0 % · **CLIP 12** | - | A sword blade striking a monster made of rusty iron: hard metallic clang with a gritty scr… |
| hit_iron | v3 | 0.45s | -11.7 | 0.7 | 끝 −29 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 16** | - | A sword blade striking a monster made of rusty iron: hard metallic clang with a gritty scr… |
| hit_iron | v4 | 0.45s | -11.8 | 1.2 | 끝 −27 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 2.8 → 0.1 % · **CLIP 45** | - | A sword blade striking a monster made of rusty iron: hard metallic clang with a gritty scr… |
| hit_crit_iron | v1 | 0.67s | -10.2 | 2.9 | 끝 −10 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 22.2 → 0.2 % · **CLIP 72** | - | A powerful critical sword blow smashing into thick iron armor plates: heavy metallic crunc… |
| hit_crit_iron | v2 | 0.65s | -10.8 | 1.7 | 끝 −33 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 13.5 → 2.4 % · **CLIP 93** | - | A powerful critical sword blow smashing into thick iron armor plates: heavy metallic crunc… |
| hit_crit_iron | v3 | 0.67s | -11.1 | 1.2 | 끝 −10 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 57.1 → 57.2 % · **CLIP 140 · SUB20 57% · DC +0.068** | - | A powerful critical sword blow smashing into thick iron armor plates: heavy metallic crunc… |
| hit_soul | v1 | 0.48s | -10.2 | 2.3 | 끝 그대로 · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 14** | - | A sword cutting through a ghost's misty spirit body: airy ghostly swish tearing through co… |
| hit_soul | v2 | 0.48s | -12.8 | -2.5 | 끝 그대로 · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A sword cutting through a ghost's misty spirit body: airy ghostly swish tearing through co… |
| hit_soul | v3 | 0.47s | -9.6 | 0.4 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 18** | - | A sword cutting through a ghost's misty spirit body: airy ghostly swish tearing through co… |
| hit_soul | v4 | 0.48s | -11.4 | -1.3 | 끝 −5 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A sword cutting through a ghost's misty spirit body: airy ghostly swish tearing through co… |
| hit_crit_soul | v1 | 0.67s | -9.6 | 1.5 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 1.8 → 0.1 % · **CLIP 68** | - | A powerful sword blow ripping a ghost's spirit body apart: sharp tearing airy rip with a h… |
| hit_crit_soul | v2 | 0.67s | -13.4 | 1.0 | 끝 −11 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 8.9 → 0.6 % · **CLIP 4** | - | A powerful sword blow ripping a ghost's spirit body apart: sharp tearing airy rip with a h… |
| hit_crit_soul | v3 | 0.62s | -10.2 | 0.7 | 끝 −64 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 1.3 → 0.1 % · **CLIP 13** | - | A powerful sword blow ripping a ghost's spirit body apart: sharp tearing airy rip with a h… |
| hit_plague | v1 | 0.44s | -14.7 | 0.3 | 끝 −41 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 15.7 → 0 % · **CLIP 2** | - | A sword slicing into a bloated plague-rotted corpse body: thick squelching wet impact with… |
| hit_plague | v2 | 0.45s | -13.7 | 1.3 | 끝 −27 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 35.4 → 0 % · **CLIP 7** | - | A sword slicing into a bloated plague-rotted corpse body: thick squelching wet impact with… |
| hit_plague | v3 | 0.46s | -15.2 | 0.2 | 끝 −23 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 67.8 → 4.5 % · **CLIP 22** | - | A sword slicing into a bloated plague-rotted corpse body: thick squelching wet impact with… |
| hit_plague | v4 | 0.48s | -12.6 | 0.7 | 끝 −3 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.8 → 0 % · **CLIP 29** | - | A sword slicing into a bloated plague-rotted corpse body: thick squelching wet impact with… |
| blade_deflect | v1 | 0.58s | -13.5 | 1.1 | 끝 −23 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 2.3 → 0 % · **CLIP 9** | - | A sword glancing off impenetrable iron hide and being knocked back: sharp high metallic pi… |
| blade_deflect | v2 | 0.59s | -48.5 | -31.4 | 끝 −10 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 29.3 → 0.1 % | - | A sword glancing off impenetrable iron hide and being knocked back: sharp high metallic pi… |
| blade_deflect | v3 | 0.58s | -12.1 | 0.8 | 끝 −24 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 3.3 → 0 % · **CLIP 20** | - | A sword glancing off impenetrable iron hide and being knocked back: sharp high metallic pi… |
| talisman_fire_burst | v1 | 0.87s | -12.1 | 0.1 | 끝 −6 ms · 25 Hz 안 걺(-2.3 LU) · 20 Hz 아래 3 → 3 % · **CLIP 163** | - | A paper talisman bursting into a ball of fire on impact: sudden whooshing flame burst with… |
| talisman_fire_burst | v2 | 0.86s | -17.2 | 1.1 | 끝 −22 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 62.5 → 9.3 % · **CLIP 437** | - | A paper talisman bursting into a ball of fire on impact: sudden whooshing flame burst with… |
| talisman_fire_burst | v3 | 0.86s | -14.0 | 0.1 | 끝 −22 ms · 25 Hz 안 걺(-4.0 LU) · 20 Hz 아래 1.2 → 1.3 % · **CLIP 110** | - | A paper talisman bursting into a ball of fire on impact: sudden whooshing flame burst with… |
| talisman_fire_burst | v4 | 0.85s | -18.2 | 0.3 | 끝 −27 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 54.6 → 9.4 % · **CLIP 117** | - | A paper talisman bursting into a ball of fire on impact: sudden whooshing flame burst with… |
| talisman_lightning_hit | v1 | 0.65s | -7.5 | 1.7 | 끝 −34 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 7.4 → 7.5 % · **CLIP 236 · DC +0.043** | - | A bolt of lightning striking the ground instantly: violent sharp electric crack and snappi… |
| talisman_lightning_hit | v2 | 0.61s | -10.0 | 1.1 | 끝 −67 ms · 25 Hz 안 걺(-0.5 LU) · 20 Hz 아래 6.5 → 6.7 % · **CLIP 115 · DC +0.027** | - | A bolt of lightning striking the ground instantly: violent sharp electric crack and snappi… |
| talisman_lightning_hit | v3 | 0.61s | -7.9 | 1.2 | 끝 −74 ms · 25 Hz 안 걺(-0.9 LU) · 20 Hz 아래 5.2 → 5.6 % · **CLIP 126 · DC -0.025** | - | A bolt of lightning striking the ground instantly: violent sharp electric crack and snappi… |
| talisman_lightning_hit | v4 | 0.67s | -7.3 | 1.8 | 끝 −7 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 0.7 → 0.7 % · **CLIP 220 · DC -0.012** | - | A bolt of lightning striking the ground instantly: violent sharp electric crack and snappi… |
| talisman_salpuri | v1 | 1.17s | -10.8 | -1.8 | 끝 −26 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A shaman's purification talisman released: a single bright brass bell shake with a rising … |
| talisman_salpuri | v2 | 1.19s | -9.9 | 0.1 | 끝 −6 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 3** | - | A shaman's purification talisman released: a single bright brass bell shake with a rising … |
| talisman_salpuri | v3 | 1.18s | -12.9 | -0.7 | 끝 −24 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A shaman's purification talisman released: a single bright brass bell shake with a rising … |
| fire_field_loop | v1 | 3.00s | -38.3 | -12.9 | 끝 그대로 · 25 Hz(+0.2 LU) · 20 Hz 아래 0.5 → 0.1 % | - | A patch of ground burning steadily: continuous low crackling flames and soft roaring fire … |
| fire_field_loop | v2 | 3.00s | -36.7 | -5.6 | 끝 그대로 · 25 Hz(+0.1 LU) · 20 Hz 아래 1.1 → 0.1 % | - | A patch of ground burning steadily: continuous low crackling flames and soft roaring fire … |
| elem_fire_hit | v1 | 0.47s | -17.8 | 0.4 | 끝 −9 ms · 25 Hz 안 걺(-1.4 LU) · 20 Hz 아래 84.1 → 84.2 % · **CLIP 321 · SUB20 84% · DC +0.035** | - | A short burst of flame searing flesh as a fiery blade strikes: quick hot sizzle and a smal… |
| elem_fire_hit | v2 | 0.44s | -12.2 | 0.8 | 끝 −39 ms · 25 Hz 안 걺(-1.2 LU) · 20 Hz 아래 18.7 → 17.6 % · **CLIP 16 · DC +0.014** | - | A short burst of flame searing flesh as a fiery blade strikes: quick hot sizzle and a smal… |
| elem_fire_hit | v3 | 0.47s | -12.1 | 0.4 | 끝 −6 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 1.5 → 1.6 % · **CLIP 19** | - | A short burst of flame searing flesh as a fiery blade strikes: quick hot sizzle and a smal… |
| elem_cold_hit | v1 | 0.41s | -17.2 | -0.9 | 끝 −69 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 33.6 → 0.5 % | - | A frost-enchanted blade striking: quick crisp ice crackle of frost spreading on contact wi… |
| elem_cold_hit | v2 | 0.47s | -13.1 | 0.6 | 끝 −9 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 3.8 → 0.1 % · **CLIP 12** | - | A frost-enchanted blade striking: quick crisp ice crackle of frost spreading on contact wi… |
| elem_cold_hit | v3 | 0.47s | -22.9 | 0.4 | 끝 −7 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 12.5 → 0 % · **CLIP 1** | - | A frost-enchanted blade striking: quick crisp ice crackle of frost spreading on contact wi… |
| elem_lightning_hit | v1 | 0.45s | -8.7 | 1.5 | 끝 −28 ms · 25 Hz 안 걺(-1.1 LU) · 20 Hz 아래 46.1 → 47 % · **CLIP 328 · SUB20 47% · DC -0.035** | - | A lightning-charged blade striking: quick sharp electric zap and snapping crackle on conta… |
| elem_lightning_hit | v2 | 0.47s | -8.5 | 2.6 | 끝 −6 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 17.6 → 0.7 % · **CLIP 106** | - | A lightning-charged blade striking: quick sharp electric zap and snapping crackle on conta… |
| elem_lightning_hit | v3 | 0.48s | -8.0 | 1.7 | 끝 −4 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 3.7 → 3.7 % · **CLIP 142 · DC +0.026** | - | A lightning-charged blade striking: quick sharp electric zap and snapping crackle on conta… |
| sal_rot | v1 | 1.07s | -19.3 | -3.9 | 끝 −11 ms · 25 Hz(+4.3 LU) · 20 Hz 아래 80.9 → 16.6 % | - | A cursed body rotting and dissolving away in seconds: wet sizzling decay hiss, soft crumbl… |
| sal_rot | v2 | 1.07s | -12.7 | 0.7 | 끝 −10 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 4** | - | A cursed body rotting and dissolving away in seconds: wet sizzling decay hiss, soft crumbl… |
| sal_rot | v3 | 1.07s | -22.6 | -4.2 | 끝 −11 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A cursed body rotting and dissolving away in seconds: wet sizzling decay hiss, soft crumbl… |
| boss_heukrang_hurt | v1 | 0.57s | -24.7 | -4.7 | 끝 −33 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0.5 → 0 % | - | A huge black fire wolf struck by a blade: one short savage pained snarl-yelp with a burst … |
| boss_heukrang_hurt | v2 | 0.57s | -18.7 | -0.9 | 끝 −28 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 32.7 → 0.2 % | - | A huge black fire wolf struck by a blade: one short savage pained snarl-yelp with a burst … |
| boss_heukrang_hurt | v3 | 0.58s | -22.5 | -2.9 | 끝 −21 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 3 → 0.2 % | - | A huge black fire wolf struck by a blade: one short savage pained snarl-yelp with a burst … |
| boss_heukrang_die | v1 | 1.99s | -5.8 | 0.6 | 끝 −13 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 0 → 0 % · **CLIP 261** | - | A huge black fire wolf dying: long anguished howl breaking into a choking whine, its inner… |
| boss_heukrang_die | v2 | 1.99s | -11.3 | 0.1 | 끝 −12 ms · 25 Hz 안 걺(-2.3 LU) · 20 Hz 아래 3.8 → 3.8 % · **CLIP 285** | - | A huge black fire wolf dying: long anguished howl breaking into a choking whine, its inner… |
| boss_heukrang_wake | v1 | 1.47s | -13.3 | 0.0 | 끝 −10 ms · 25 Hz 안 걺(-1.3 LU) · 20 Hz 아래 3.3 → 3.4 % · **CLIP 271** | - | A huge black fire wolf noticing an intruder in its den: deep threatening rumbling growl ri… |
| boss_heukrang_wake | v2 | 1.47s | -11.1 | 2.0 | 끝 −10 ms · 25 Hz(+1.2 LU) · 20 Hz 아래 1 → 0.2 % · **CLIP 1018** | - | A huge black fire wolf noticing an intruder in its den: deep threatening rumbling growl ri… |
| boss_heukrang_charge_tell | v1 | 0.79s | -11.9 | 0.6 | 끝 −8 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 0 → 0 % · **CLIP 66** | - | A huge wolf crouching to charge: sharp intake snort and claws digging and scraping hard in… |
| boss_heukrang_charge_tell | v2 | 0.79s | -16.3 | -2.3 | 끝 −12 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.2 → 0 % | - | A huge wolf crouching to charge: sharp intake snort and claws digging and scraping hard in… |
| boss_heukrang_charge_tell | v3 | 0.79s | -13.7 | -0.4 | 끝 −12 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 0.1 → 0 % | - | A huge wolf crouching to charge: sharp intake snort and claws digging and scraping hard in… |
| boss_jangsanbeom_attack | v1 | 0.79s | -26.0 | -5.3 | 끝 −8 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A huge white-furred tiger-like mountain beast rearing to pounce: deep breathy tiger chuff … |
| boss_jangsanbeom_attack | v2 | 0.79s | -22.0 | -7.3 | 끝 −8 ms · 25 Hz(+0.6 LU) · 20 Hz 아래 3.2 → 0.5 % | - | A huge white-furred tiger-like mountain beast rearing to pounce: deep breathy tiger chuff … |
| boss_jangsanbeom_attack | v3 | 0.79s | -18.0 | -3.3 | 끝 −9 ms · 25 Hz(+2.0 LU) · 20 Hz 아래 1.2 → 0.1 % | - | A huge white-furred tiger-like mountain beast rearing to pounce: deep breathy tiger chuff … |
| boss_jangsanbeom_hurt | v1 | 0.59s | -18.3 | -3.1 | 끝 −8 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 0 → 0 % | - | A huge white-furred mountain beast struck by a blade: short furious pained tiger snarl wit… |
| boss_jangsanbeom_hurt | v2 | 0.58s | -16.1 | 0.1 | 끝 −23 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 3** | - | A huge white-furred mountain beast struck by a blade: short furious pained tiger snarl wit… |
| boss_jangsanbeom_hurt | v3 | 0.59s | -15.7 | -0.9 | 끝 −6 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0.2 → 0 % | - | A huge white-furred mountain beast struck by a blade: short furious pained tiger snarl wit… |
| boss_jangsanbeom_die | v1 | 1.99s | -6.0 | 0.0 | 끝 −10 ms · 25 Hz 안 걺(-1.6 LU) · 20 Hz 아래 0.3 → 0.3 % · **CLIP 510** | - | A huge white-furred mountain beast dying: a long tiger roar decaying into an unsettling hu… |
| boss_jangsanbeom_die | v2 | 1.99s | -4.9 | 0.0 | 끝 −9 ms · 25 Hz 안 걺(-1.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 536** | - | A huge white-furred mountain beast dying: a long tiger roar decaying into an unsettling hu… |
| boss_jangsanbeom_wake | v1 | 1.75s | -9.8 | 0.0 | 끝 −12 ms · 25 Hz 안 걺(-1.2 LU) · 20 Hz 아래 0.2 → 0.2 % · **CLIP 6** | - | A huge white-furred mountain beast revealing itself in the dark: an eerie distant whisperi… |
| boss_jangsanbeom_wake | v2 | 1.75s | -4.4 | 0.1 | 끝 −10 ms · 25 Hz 안 걺(-2.4 LU) · 20 Hz 아래 0.2 → 0.2 % · **CLIP 1641** | - | A huge white-furred mountain beast revealing itself in the dark: an eerie distant whisperi… |
| boss_jangsanbeom_bite | v1 | 0.45s | -14.1 | 0.2 | 끝 −27 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 12.1 → 19 % · **CLIP 64** | - | A large beast's powerful jaws snapping shut on prey: fast heavy wet bite crunch with a sho… |
| boss_jangsanbeom_bite | v2 | 0.43s | -15.7 | 0.5 | 끝 −48 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 4.4 → 0.8 % · **CLIP 5** | - | A large beast's powerful jaws snapping shut on prey: fast heavy wet bite crunch with a sho… |
| boss_jangsanbeom_bite | v3 | 0.47s | -13.2 | 0.4 | 끝 −10 ms · 25 Hz 안 걺(-1.1 LU) · 20 Hz 아래 4.2 → 4.5 % · **CLIP 78** | - | A large beast's powerful jaws snapping shut on prey: fast heavy wet bite crunch with a sho… |
| boss_bulgasari_attack | v1 | 0.78s | -14.4 | -2.8 | 끝 −23 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 7.3 → 7.3 % | - | A massive iron-eating monster winding up to strike: grinding metal plates shifting, a deep… |
| boss_bulgasari_attack | v2 | 0.77s | -14.8 | 0.1 | 끝 −32 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 4.8 → 4.9 % · **CLIP 2** | - | A massive iron-eating monster winding up to strike: grinding metal plates shifting, a deep… |
| boss_bulgasari_attack | v3 | 0.79s | -16.2 | 0.0 | 끝 −10 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.9 → 0.1 % · **CLIP 1** | - | A massive iron-eating monster winding up to strike: grinding metal plates shifting, a deep… |
| boss_bulgasari_hurt | v1 | 0.58s | -14.4 | 0.3 | 끝 −21 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 8** | - | A massive iron-skinned monster struck: low angry metallic groan with clanking scales and a… |
| boss_bulgasari_hurt | v2 | 0.58s | -15.8 | 0.2 | 끝 −22 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 18** | - | A massive iron-skinned monster struck: low angry metallic groan with clanking scales and a… |
| boss_bulgasari_hurt | v3 | 0.59s | -13.8 | 0.6 | 끝 −10 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % · **CLIP 35** | - | A massive iron-skinned monster struck: low angry metallic groan with clanking scales and a… |
| boss_bulgasari_die | v1 | 2.18s | -18.1 | 0.3 | 끝 −16 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 0.1 → 0 % | - | A massive iron monster collapsing in death: a long deep metallic groan, iron spikes clatte… |
| boss_bulgasari_die | v2 | 2.18s | -11.8 | 0.4 | 끝 −17 ms · 25 Hz 안 걺(-0.9 LU) · 20 Hz 아래 0.1 → 0.1 % · **CLIP 230** | - | A massive iron monster collapsing in death: a long deep metallic groan, iron spikes clatte… |
| boss_bulgasari_wake | v1 | 1.45s | -11.9 | 0.0 | 끝 −26 ms · 25 Hz 안 걺(-2.0 LU) · 20 Hz 아래 1.4 → 1.8 % · **CLIP 2** | - | A massive iron monster stirring awake: creaking grinding iron plates, a deep rumbling snor… |
| boss_bulgasari_wake | v2 | 1.46s | -20.1 | -5.0 | 끝 −23 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 2.6 → 0.6 % | - | A massive iron monster stirring awake: creaking grinding iron plates, a deep rumbling snor… |
| boss_bulgasari_charge_tell | v1 | 0.79s | -14.6 | -4.5 | 끝 −9 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0.3 → 0 % | - | A massive iron beast lowering its head to charge: harsh metal scraping on stone, iron spik… |
| boss_bulgasari_charge_tell | v2 | 0.79s | -15.9 | -3.1 | 끝 −12 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.3 → 0 % | - | A massive iron beast lowering its head to charge: harsh metal scraping on stone, iron spik… |
| boss_bulgasari_charge_tell | v3 | 0.78s | -22.0 | -7.6 | 끝 −21 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0 → 0 % | - | A massive iron beast lowering its head to charge: harsh metal scraping on stone, iron spik… |
| boss_gumiho_attack | v1 | 0.58s | -14.4 | -2.6 | 끝 −19 ms · 25 Hz(+2.3 LU) · 20 Hz 아래 58.2 → 2.1 % | - | A giant nine-tailed fox demon slashing with claws: fast vicious claw swipe whoosh with a s… |
| boss_gumiho_attack | v2 | 0.55s | -15.3 | 2.5 | 끝 −46 ms · 25 Hz(-0.5 LU) · 20 Hz 아래 60.3 → 10.1 % · **CLIP 145** | - | A giant nine-tailed fox demon slashing with claws: fast vicious claw swipe whoosh with a s… |
| boss_gumiho_attack | v3 | 0.58s | -13.1 | 1.2 | 끝 −19 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 53.2 → 7.9 % · **CLIP 81** | - | A giant nine-tailed fox demon slashing with claws: fast vicious claw swipe whoosh with a s… |
| boss_gumiho_hurt | v1 | 0.60s | -7.2 | 0.3 | 끝 −3 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 188** | - | A giant nine-tailed fox demon struck by a blade: short shrill pained fox scream with a fem… |
| boss_gumiho_hurt | v2 | 0.59s | -7.6 | 0.5 | 끝 −9 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.7 → 0 % · **CLIP 209** | - | A giant nine-tailed fox demon struck by a blade: short shrill pained fox scream with a fem… |
| boss_gumiho_hurt | v3 | 0.56s | -7.8 | 0.6 | 끝 −44 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 227** | - | A giant nine-tailed fox demon struck by a blade: short shrill pained fox scream with a fem… |
| boss_gumiho_die | v1 | 2.45s | -6.4 | 0.2 | 끝 −26 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 1.8 → 1.8 % · **CLIP 495** | - | A giant nine-tailed fox demon dying: a long anguished fox shriek that warps into a woman's… |
| boss_gumiho_die | v2 | 2.45s | -9.3 | 0.1 | 끝 −27 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 1.1 → 1.1 % · **CLIP 519** | - | A giant nine-tailed fox demon dying: a long anguished fox shriek that warps into a woman's… |
| boss_gumiho_unmask | v1 | 1.99s | -8.6 | 0.5 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 67** | - | A beautiful woman's human mask tearing away to reveal a fox demon: wet ripping of skin and… |
| boss_gumiho_unmask | v2 | 1.99s | -9.1 | 0.5 | 끝 −7 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % · **CLIP 17** | - | A beautiful woman's human mask tearing away to reveal a fox demon: wet ripping of skin and… |
| boss_gumiho_claw_tell | v1 | 0.79s | -10.2 | 0.1 | 끝 −10 ms · 25 Hz 안 걺(-1.9 LU) · 20 Hz 아래 0.2 → 0.2 % · **CLIP 146** | - | A fox demon drawing back its claws to strike: rising sharp hiss and slow scrape of long cl… |
| boss_gumiho_claw_tell | v2 | 0.76s | -9.9 | 0.6 | 끝 −42 ms · 25 Hz(-0.4 LU) · 20 Hz 아래 6.2 → 0.1 % · **CLIP 73** | - | A fox demon drawing back its claws to strike: rising sharp hiss and slow scrape of long cl… |
| boss_gumiho_claw_tell | v3 | 0.79s | -10.7 | 0.1 | 끝 −6 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 3.9 → 0.4 % · **CLIP 1** | - | A fox demon drawing back its claws to strike: rising sharp hiss and slow scrape of long cl… |
| boss_gumiho_leap_tell | v1 | 0.87s | -8.9 | 0.1 | 끝 −10 ms · 25 Hz 안 걺(-1.5 LU) · 20 Hz 아래 2 → 2 % · **CLIP 23** | - | A giant fox demon crouching low to leap: deep coiled growl, nine tails whooshing and rustl… |
| boss_gumiho_leap_tell | v2 | 0.87s | -10.8 | 0.0 | 끝 −8 ms · 25 Hz 안 걺(-1.7 LU) · 20 Hz 아래 0.7 → 0.7 % · **CLIP 84** | - | A giant fox demon crouching low to leap: deep coiled growl, nine tails whooshing and rustl… |
| boss_gumiho_leap_tell | v3 | 0.87s | -9.6 | 0.1 | 끝 −8 ms · 25 Hz 안 걺(-1.9 LU) · 20 Hz 아래 0.1 → 0.1 % · **CLIP 40** | - | A giant fox demon crouching low to leap: deep coiled growl, nine tails whooshing and rustl… |
| boss_gumiho_foxfire_tell | v1 | 0.99s | -12.7 | 0.0 | 끝 −14 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 0.2 → 0.2 % · **CLIP 15** | - | Eerie blue foxfire flames igniting and gathering in the air: soft ghostly ignition whoosh … |
| boss_gumiho_foxfire_tell | v2 | 0.99s | -13.6 | -0.5 | 끝 −11 ms · 25 Hz(+0.7 LU) · 20 Hz 아래 0.4 → 0 % · **CLIP 11** | - | Eerie blue foxfire flames igniting and gathering in the air: soft ghostly ignition whoosh … |
| boss_gumiho_foxfire_tell | v3 | 0.99s | -13.2 | 0.0 | 끝 −7 ms · 25 Hz 안 걺(-1.7 LU) · 20 Hz 아래 0.6 → 0.6 % · **CLIP 14** | - | Eerie blue foxfire flames igniting and gathering in the air: soft ghostly ignition whoosh … |
| boss_gumiho_wave_tell | v1 | 1.18s | -8.2 | 2.0 | 끝 −25 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 778** | - | A dark curse gathering power before releasing a shockwave: deep low droning swell with whi… |
| boss_gumiho_wave_tell | v2 | 1.19s | -8.4 | -0.4 | 끝 −9 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 0.1 → 0.1 % | - | A dark curse gathering power before releasing a shockwave: deep low droning swell with whi… |
| boss_gumiho_wave_tell | v3 | 1.19s | -8.8 | 0.0 | 끝 −8 ms · 25 Hz 안 걺(-1.0 LU) · 20 Hz 아래 0.1 → 0.1 % · **CLIP 172** | - | A dark curse gathering power before releasing a shockwave: deep low droning swell with whi… |
| skill_flurry | v1 | 0.44s | -12.2 | 1.1 | 끝 −43 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0.4 → 0 % · **CLIP 8** | - | One very fast short sword flick in a rapid flurry of cuts: tight crisp thin air slice, qui… |
| skill_flurry | v2 | 0.45s | -14.1 | -0.1 | 끝 −28 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 1** | - | One very fast short sword flick in a rapid flurry of cuts: tight crisp thin air slice, qui… |
| skill_flurry | v3 | 0.45s | -13.4 | -0.2 | 끝 −29 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % | - | One very fast short sword flick in a rapid flurry of cuts: tight crisp thin air slice, qui… |
| skill_flurry_impact | v1 | 0.47s | -12.3 | 1.1 | 끝 −10 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 0.2 → 0 % · **CLIP 9** | - | A quick light sword cut landing on a body during a rapid flurry: short crisp slice with a … |
| skill_flurry_impact | v2 | 0.47s | -16.2 | -2.0 | 끝 −8 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A quick light sword cut landing on a body during a rapid flurry: short crisp slice with a … |
| skill_flurry_impact | v3 | 0.47s | -16.7 | -0.8 | 끝 −14 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A quick light sword cut landing on a body during a rapid flurry: short crisp slice with a … |
| skill_leap_slash | v1 | 0.59s | -13.9 | 0.1 | 끝 −8 ms · 25 Hz 안 걺(-5.7 LU) · 20 Hz 아래 42.4 → 44 % · **CLIP 641 · SUB20 44% · DC +0.024** | - | A swordsman leaping high into the air: strong push-off cloth whoosh and rising wind rush, … |
| skill_leap_slash | v2 | 0.59s | -19.6 | 0.0 | 끝 −12 ms · 25 Hz 안 걺(-0.6 LU) · 20 Hz 아래 52.4 → 53.2 % · **CLIP 218 · SUB20 53% · DC -0.058** | - | A swordsman leaping high into the air: strong push-off cloth whoosh and rising wind rush, … |
| skill_leap_slash | v3 | 0.58s | -21.0 | -1.6 | 끝 −22 ms · 25 Hz(+0.5 LU) · 20 Hz 아래 68.5 → 34.1 % · **SUB20 34%** | - | A swordsman leaping high into the air: strong push-off cloth whoosh and rising wind rush, … |
| skill_leap_slash_impact | v1 | 0.86s | -32.9 | -9.0 | 끝 −16 ms · 25 Hz 안 걺(-1.3 LU) · 20 Hz 아래 66.7 → 69.5 % · **SUB20 70%** | - | A swordsman crashing down from a leap and slamming his blade into the ground: heavy ground… |
| skill_leap_slash_impact | v2 | 0.87s | -21.8 | -1.3 | 끝 −9 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 34.6 → 12.7 % · **CLIP 7** | - | A swordsman crashing down from a leap and slamming his blade into the ground: heavy ground… |
| skill_leap_slash_impact | v3 | 0.86s | -20.2 | -0.0 | 끝 −20 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 28.6 → 19.7 % | - | A swordsman crashing down from a leap and slamming his blade into the ground: heavy ground… |
| skill_blade_storm_loop | v1 | 2.25s | -6.2 | 0.5 | 끝 그대로 · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 17** | - | A continuous whirling storm of spinning sword blades: steady rapid circular whooshing wind… |
| skill_blade_storm_loop | v2 | 2.25s | -10.2 | 0.4 | 끝 그대로 · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 12** | - | A continuous whirling storm of spinning sword blades: steady rapid circular whooshing wind… |
| skill_blade_storm_end | v1 | 0.79s | -12.9 | 0.9 | 끝 −10 ms · 25 Hz 안 걺(-6.3 LU) · 20 Hz 아래 9.9 → 10.5 % · **CLIP 817 · DC +0.013** | - | A spinning blade whirlwind coming to an abrupt stop: final wide whoosh, a sharp sword snap… |
| skill_blade_storm_end | v2 | 0.77s | -10.9 | 0.7 | 끝 −28 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 17.2 → 17.3 % · **CLIP 16 · DC -0.014** | - | A spinning blade whirlwind coming to an abrupt stop: final wide whoosh, a sharp sword snap… |
| skill_blink | v1 | 0.59s | -18.1 | -1.6 | 끝 −7 ms · 25 Hz(+1.9 LU) · 20 Hz 아래 22.5 → 7.5 % · **CLIP 2** | - | A Taoist master vanishing and reappearing in an instant: quick ink-smoke puff and a sharp … |
| skill_blink | v2 | 0.60s | -19.2 | -0.4 | 끝 −4 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 43.4 → 43.7 % · **SUB20 44%** | - | A Taoist master vanishing and reappearing in an instant: quick ink-smoke puff and a sharp … |
| skill_blink | v3 | 0.59s | -18.8 | -3.2 | 끝 −15 ms · 25 Hz(+0.3 LU) · 20 Hz 아래 75.3 → 2.6 % | - | A Taoist master vanishing and reappearing in an instant: quick ink-smoke puff and a sharp … |
| skill_mana_shield | v1 | 0.99s | -11.2 | -5.1 | 끝 −9 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | A shimmering protective spirit barrier forming around a person: rising soft glassy hum and… |
| skill_mana_shield | v2 | 0.99s | -20.3 | -7.7 | 끝 −7 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % | - | A shimmering protective spirit barrier forming around a person: rising soft glassy hum and… |
| skill_mana_shield | v3 | 0.99s | -10.1 | -1.5 | 끝 −12 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A shimmering protective spirit barrier forming around a person: rising soft glassy hum and… |
| mana_shield_absorb | v1 | 0.47s | -21.6 | -4.7 | 끝 −10 ms · 25 Hz 안 걺(-1.0 LU) · 20 Hz 아래 0.1 → 0.1 % | - | A blow absorbed by a magical spirit barrier: muffled resonant energy thump with a short gl… |
| mana_shield_absorb | v2 | 0.48s | -21.3 | -7.5 | 끝 −5 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.9 → 0.1 % | - | A blow absorbed by a magical spirit barrier: muffled resonant energy thump with a short gl… |
| mana_shield_absorb | v3 | 0.47s | -28.1 | -11.4 | 끝 −12 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 6.7 → 0.3 % | - | A blow absorbed by a magical spirit barrier: muffled resonant energy thump with a short gl… |
| mana_shield_break | v1 | 0.77s | -15.9 | -0.1 | 끝 −27 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % | - | A magical spirit barrier shattering: sharp crystalline energy crack bursting apart with a … |
| mana_shield_break | v2 | 0.77s | -13.0 | -1.6 | 끝 −29 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 0.2 → 0 % | - | A magical spirit barrier shattering: sharp crystalline energy crack bursting apart with a … |
| skill_seal_array | v1 | 0.99s | -17.7 | 0.1 | 끝 −9 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 3** | - | A circle of paper talismans slapping onto the ground and activating a magic seal: several … |
| skill_seal_array | v2 | 0.99s | -22.2 | -6.1 | 끝 −8 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.2 → 0 % | - | A circle of paper talismans slapping onto the ground and activating a magic seal: several … |
| skill_seal_array | v3 | 0.99s | -26.0 | -11.0 | 끝 −9 ms · 25 Hz(+0.6 LU) · 20 Hz 아래 0.2 → 0.1 % | - | A circle of paper talismans slapping onto the ground and activating a magic seal: several … |
| skill_talisman_rain | v1 | 0.99s | -15.4 | -0.5 | 끝 −10 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 0.7 → 0.1 % · **CLIP 1** | - | A handful of paper talismans flung high into the sky: big papery whoosh and many sheets fl… |
| skill_talisman_rain | v2 | 0.99s | -18.9 | 0.7 | 끝 −8 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 5.5 → 1 % · **CLIP 1** | - | A handful of paper talismans flung high into the sky: big papery whoosh and many sheets fl… |
| skill_talisman_rain | v3 | 0.99s | -19.8 | -3.5 | 끝 −8 ms · 25 Hz(+0.2 LU) · 20 Hz 아래 0 → 0 % | - | A handful of paper talismans flung high into the sky: big papery whoosh and many sheets fl… |
| enemy_heavy_windup | v1 | 0.99s | -8.7 | 0.4 | 끝 −11 ms · 25 Hz 안 걺(-1.7 LU) · 20 Hz 아래 12 → 12.6 % · **CLIP 305** | - | A huge brute raising a massive weapon high for a crushing overhead blow: long slow heavy c… |
| enemy_heavy_windup | v2 | 0.99s | -6.2 | 0.4 | 끝 −15 ms · 25 Hz 안 걺(-1.5 LU) · 20 Hz 아래 0.6 → 0.6 % · **CLIP 732** | - | A huge brute raising a massive weapon high for a crushing overhead blow: long slow heavy c… |
| enemy_heavy_windup | v3 | 0.99s | -9.0 | 0.9 | 끝 −11 ms · 25 Hz 안 걺(-1.3 LU) · 20 Hz 아래 6 → 6.3 % · **CLIP 436** | - | A huge brute raising a massive weapon high for a crushing overhead blow: long slow heavy c… |
| enemy_slam | v1 | 0.87s | -21.5 | 0.0 | 끝 −12 ms · 25 Hz 안 걺(-1.3 LU) · 20 Hz 아래 77.7 → 78.2 % · **CLIP 73 · SUB20 78%** | - | A massive weapon slamming down onto a stone floor: huge heavy ground impact boom with crac… |
| enemy_slam | v2 | 0.87s | -14.8 | 0.1 | 끝 −8 ms · 25 Hz 안 걺(-1.9 LU) · 20 Hz 아래 8.9 → 9 % · **CLIP 177** | - | A massive weapon slamming down onto a stone floor: huge heavy ground impact boom with crac… |
| enemy_slam | v3 | 0.86s | -22.3 | -4.0 | 끝 −22 ms · 25 Hz(+1.1 LU) · 20 Hz 아래 3.6 → 1.1 % | - | A massive weapon slamming down onto a stone floor: huge heavy ground impact boom with crac… |
| enemy_melee_hit | v1 | 0.47s | -59.7 | -38.1 | 끝 −8 ms · 25 Hz(-0.0 LU) · 20 Hz 아래 98.8 → 6.8 % | - | A monster's claw or club connecting hard: short heavy punchy whack, tight, close-up, dry, … |
| enemy_melee_hit | v2 | 0.47s | -14.6 | 0.4 | 끝 −11 ms · 25 Hz 안 걺(-2.6 LU) · 20 Hz 아래 14.4 → 14.5 % · **CLIP 102 · DC -0.020** | - | A monster's claw or club connecting hard: short heavy punchy whack, tight, close-up, dry, … |
| enemy_melee_hit | v3 | 0.48s | -63.7 | -42.4 | 끝 −2 ms · 25 Hz(+1.8 LU) · 20 Hz 아래 92.8 → 1.6 % | - | A monster's claw or club connecting hard: short heavy punchy whack, tight, close-up, dry, … |
| doho_dodge | v1 | 0.47s | -24.0 | -6.6 | 끝 −8 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.1 → 0.1 % | - | A swordsman nimbly sidestepping an attack: quick light cloth robe swish and a soft airy du… |
| doho_dodge | v2 | 0.43s | -17.7 | 0.0 | 끝 −52 ms · 25 Hz 안 걺(-1.1 LU) · 20 Hz 아래 85.4 → 85.5 % · **CLIP 319 · SUB20 86% · DC +0.071** | - | A swordsman nimbly sidestepping an attack: quick light cloth robe swish and a soft airy du… |
| doho_dodge | v3 | 0.46s | -16.9 | 0.1 | 끝 −23 ms · 25 Hz 안 걺(-0.5 LU) · 20 Hz 아래 45 → 49.8 % · **CLIP 290 · SUB20 50% · DC -0.014** | - | A swordsman nimbly sidestepping an attack: quick light cloth robe swish and a soft airy du… |
| skill_denied | v1 | 0.45s | -37.1 | -17.4 | 끝 −28 ms · 25 Hz(+0.4 LU) · 20 Hz 아래 24.5 → 10.6 % | - | A short dull muted wooden knock with a soft fizzling-out spark, a failed spell cue, subtle… |
| skill_denied | v2 | 0.47s | -62.8 | -42.0 | 끝 −8 ms · 25 Hz(+2.0 LU) · 20 Hz 아래 55.7 → 22.7 % | - | A short dull muted wooden knock with a soft fizzling-out spark, a failed spell cue, subtle… |
| skill_denied | v3 | 0.47s | -57.2 | -38.2 | 끝 −9 ms · 25 Hz(+3.1 LU) · 20 Hz 아래 75.9 → 36.5 % · **SUB20 36%** | - | A short dull muted wooden knock with a soft fizzling-out spark, a failed spell cue, subtle… |
| doho_chill | v1 | 0.67s | -18.2 | -6.0 | 끝 −14 ms · 25 Hz 안 걺(-1.0 LU) · 20 Hz 아래 4.6 → 4.9 % | - | A person suddenly chilled by freezing magic: quick frost crackle spreading over cloth with… |
| doho_chill | v2 | 0.66s | -11.7 | 0.3 | 끝 −22 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 24.3 → 26.1 % · **CLIP 3 · DC -0.014** | - | A person suddenly chilled by freezing magic: quick frost crackle spreading over cloth with… |
| doho_curse | v1 | 0.87s | -18.0 | -5.2 | 끝 −6 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0.3 → 0.1 % | - | A dark curse latching onto a person: low ominous whispering swell and a sinister hollow th… |
| doho_curse | v2 | 0.87s | -37.7 | -20.7 | 끝 −7 ms · 25 Hz 안 걺(-0.8 LU) · 20 Hz 아래 0.3 → 0.3 % | - | A dark curse latching onto a person: low ominous whispering swell and a sinister hollow th… |
| mana_drain | v1 | 0.67s | -11.3 | -1.3 | 끝 −8 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | Spiritual energy being sucked out of a person: reverse airy draining whoosh with a thin fa… |
| mana_drain | v2 | 0.67s | -12.3 | -0.7 | 끝 −6 ms · 25 Hz(+0.0 LU) · 20 Hz 아래 0 → 0 % | - | Spiritual energy being sucked out of a person: reverse airy draining whoosh with a thin fa… |
| projectile_fly | v1 | 0.58s | -10.1 | 0.9 | 끝 −17 ms · 25 Hz(+0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 41** | - | An arrow flying fast past the listener: short sharp whistling whiz passing by, close-up, d… |
| projectile_fly | v2 | 0.59s | -10.5 | 0.6 | 끝 −8 ms · 25 Hz(-0.1 LU) · 20 Hz 아래 0 → 0 % · **CLIP 87** | - | An arrow flying fast past the listener: short sharp whistling whiz passing by, close-up, d… |
| projectile_fly | v3 | 0.59s | -9.6 | 0.6 | 끝 −7 ms · 25 Hz(-0.3 LU) · 20 Hz 아래 0.1 → 0 % · **CLIP 105** | - | An arrow flying fast past the listener: short sharp whistling whiz passing by, close-up, d… |
| projectile_impact_wall | v1 | 0.43s | -20.2 | 0.2 | 끝 −53 ms · 25 Hz 안 걺(-0.7 LU) · 20 Hz 아래 0.7 → 0.7 % · **CLIP 46** | - | An arrow hitting a stone wall: short hard thunk and a small wooden snap, close-up, dry, is… |
| projectile_impact_wall | v2 | 0.45s | -14.6 | 0.7 | 끝 −29 ms · 25 Hz 안 걺(-1.2 LU) · 20 Hz 아래 11 → 13 % · **CLIP 96** | - | An arrow hitting a stone wall: short hard thunk and a small wooden snap, close-up, dry, is… |
| projectile_impact_wall | v3 | 0.48s | -51.2 | -26.7 | 끝 −5 ms · 25 Hz(-0.2 LU) · 20 Hz 아래 78.3 → 5.3 % | - | An arrow hitting a stone wall: short hard thunk and a small wooden snap, close-up, dry, is… |
| elite_death_burst | v1 | 0.86s | -5.1 | 0.8 | 끝 −25 ms · 25 Hz 안 걺(-4.6 LU) · 20 Hz 아래 0.3 → 0.4 % · **CLIP 2019** | - | A cursed monster's corpse erupting in a burst of dark energy: sharp concussive whump with … |
| elite_death_burst | v2 | 0.86s | -5.4 | 0.5 | 끝 −24 ms · 25 Hz 안 걺(-5.7 LU) · 20 Hz 아래 0.5 → 0.5 % · **CLIP 2567** | - | A cursed monster's corpse erupting in a burst of dark energy: sharp concussive whump with … |
| elite_death_burst | v3 | 0.85s | -6.2 | 0.3 | 끝 −26 ms · 25 Hz 안 걺(-4.4 LU) · 20 Hz 아래 0.5 → 0.5 % · **CLIP 1705** | - | A cursed monster's corpse erupting in a burst of dark energy: sharp concussive whump with … |

## #942 메모 (2026-10-26)
- 배치 = `../batch_940_combat.json`(S1~S6, 78큐 231클립) + `../batch_942_redo.json`(거의 빈 소리 다시 뽑기 7클립) · 차감 1,459 크레딧 · 원본 wav 94MB는 로컬(git 밖, D-100).
- 거의 빈 소리(−45 LUFS 아래)는 판정판에서 뺌: blade_deflect_v2 · enemy_melee_hit_v1·v3 · skill_denied_v2·v3 · projectile_impact_wall_v3·v4.
- `preview/` = 판정판 듣기용 mp3(지금 게임 큐 크기에 맞춤, 새 큐는 −18 LUFS). 판정판 https://claude.ai/artifact/ETXuUbGzeKtp7en4NyHon8 「새 후보」 탭 · 정본 joseon `docs/design/combat_sfx_audit_2026-10-26.md`.
