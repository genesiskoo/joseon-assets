# workbench/audio — 효과음·BGM 원본 (보드 #34·#42, 오디오 사양 joseon/docs/design/audio.md)

생성 = 배치 1·2(#34): Comfy Cloud 파트너 노드 `elevenlabs/sound-generation`(MCP `submit_batch`, Comfy 크레딧) / **배치 3부터(#35): ElevenLabs Sound Effects v2 직접 API** — `joseon/tools/sfx_gen.py`(키 = `joseon/.env` `ELEVENLABS_API_KEY`, 구독 크레딧, 배치 JSON = 이 폴더 `batch_*.json`). PD 확인 2026-09-18: 구독이 있는데 Comfy 크레딧을 쓴 건 키가 세션에 없어서였고, 이후는 직접 API.
비용 = 클립당 약 0.34 크레딧(0.7초 프로브 실측) + GPU 3초. 최소 길이 0.5초(0.45초 요청은 거부됨).
톤 = narrative.md "검광 SFX 톤": 묵직한 금속음 대신 가야금 현 퉁김 + 짧은 공기 절단음, lo-fi. 목소리·비명은 넣지 않음(D-017 EA 음성 0, #41 판정 대기 — 피격은 몸·천 충격음).
프롬프트 뼈대: "<사건> : <재질 충격> + <꼬리>, short, dry, isolated, no music, no voice" + 변주마다 무게·길이 수식어 하나.
반입 = `joseon/tools/intake_audio.ps1 -Src <큐 폴더> -Cue <큐> -Sub combat` (앞뒤 무음 트림 → −16 LUFS → 44.1k 모노 wav `<큐>_N.wav`).

## 배치 1 (2026-09-18, 31편, batch = 카드 #34 댓글)

프로브: hit/hit_probe.flac (job 661ad00f-61d3-478d-ac92-a9a5235feff9, 0.68s, 0.34 크레딧) — 채택 후보.

| 큐 | 변주 | 길이 | job | 프롬프트 요지 |
|---|---|---|---|---|
| sword_swing | v1 | 0.5s | 74128bbd-1dd8-4051-9491-646fabd3a7de | Fast single sword swing through air, a sharp short whoosh with a faint plucked Korean gaya… |
| sword_swing | v2 | 0.5s | d6911d47-0afd-4e9b-95e0-8ec323b45249 | Fast single sword swing through air, a sharp short whoosh with a faint plucked Korean gaya… |
| sword_swing | v3 | 0.5s | 0788d10c-0e68-49c4-a24e-df2c0f142181 | Fast single sword swing through air, a sharp short whoosh with a faint plucked Korean gaya… |
| sword_swing | v4 | 0.5s | 3b9d8ec7-6330-4870-9bca-dce25cf237aa | Fast single sword swing through air, a sharp short whoosh with a faint plucked Korean gaya… |
| hit | v1 | 0.7s | 1f53ea1c-d647-4dd1-94cb-d6fee86ac247 | Sword blade striking a body once: a quick air-cut whoosh into a wet punchy impact thud, fo… |
| hit | v2 | 0.7s | 659d2b81-1bc8-4f50-83f0-690234019cd6 | Sword blade striking a body once: a quick air-cut whoosh into a wet punchy impact thud, fo… |
| hit | v3 | 0.7s | 427d14eb-622d-48c8-9b9a-390832e51192 | Sword blade striking a body once: a quick air-cut whoosh into a wet punchy impact thud, fo… |
| hit_crit | v1 | 0.9s | ee291eb6-d080-4904-a640-84f08bb22d44 | Heavy critical sword blow landing: deep crunchy impact thud with a sharp snapped Korean ga… |
| hit_crit | v2 | 0.9s | 05b97e9e-1804-4ff7-a564-7e3f95d40893 | Heavy critical sword blow landing: deep crunchy impact thud with a sharp snapped Korean ga… |
| whiff | v1 | 0.5s | f689d108-8ee9-457f-9f51-adf9e238d8c4 | Sword swing missing entirely, cutting only air: a short breathy whoosh with a faint whistl… |
| whiff | v2 | 0.5s | 288d3510-9f56-41f4-9700-3bd17d2f2a6e | Sword swing missing entirely, cutting only air: a short breathy whoosh with a faint whistl… |
| player_hurt | v1 | 0.6s | fadfdad9-c5de-44f6-8705-b29333fe5905 | A blow landing on a person wearing a cloth robe and leather: dull blunt body impact thud w… |
| player_hurt | v2 | 0.6s | 1c4c2a7e-41cc-429e-a75d-aff46a3d4d42 | A blow landing on a person wearing a cloth robe and leather: dull blunt body impact thud w… |
| player_hurt | v3 | 0.6s | 94f5997d-af83-4de5-8ae6-e98ecfdbc579 | A blow landing on a person wearing a cloth robe and leather: dull blunt body impact thud w… |
| player_die | v1 | 1.6s | 20695a79-a9cb-4b03-b9d2-6e9c8659e3f8 | A man in a cloth robe collapses onto a stone floor: heavy body fall thud, cloth rustle, a … |
| enemy_attack | v1 | 0.6s | eb696b8b-c9e4-4e28-b6a3-6d011015b21c | A bandit winding up a strike: quick leather creak and a rough cloth swish as a wooden club… |
| enemy_attack | v2 | 0.6s | 47ad7273-bc1e-42a7-852d-d9bac7227d9a | A bandit winding up a strike: quick leather creak and a rough cloth swish as a wooden club… |
| shoot | v1 | 0.7s | 72994265-ff1a-4db3-8eb5-ed5e9f6cbab0 | A paper talisman thrown with a sharp wrist snap: paper flutter whoosh and a faint mystical… |
| shoot | v2 | 0.7s | 63f99888-0c1c-442a-8533-b38857917a74 | A paper talisman thrown with a sharp wrist snap: paper flutter whoosh and a faint mystical… |
| enemy_hurt | v1 | 0.6s | 9fecc2af-c466-4227-b5de-c46425336e2c | A sword cut landing on a ragged bandit: dull thud with leather and torn cloth, short and d… |
| enemy_hurt | v2 | 0.6s | 6045555e-f293-4cb0-ae52-8f7dc92be992 | A sword cut landing on a ragged bandit: dull thud with leather and torn cloth, short and d… |
| enemy_hurt | v3 | 0.6s | 58217ec6-b82b-4c5d-bb3c-84fedc29083a | A sword cut landing on a ragged bandit: dull thud with leather and torn cloth, short and d… |
| enemy_die | v1 | 1.2s | 413bb0dd-ecb7-42cf-8353-fc05311b616a | A body falling dead onto a stone dungeon floor: heavy thud, short slide, cloth and leather… |
| enemy_die | v2 | 1.2s | 215663d5-04a0-4600-ae1b-766afdadc2c6 | A body falling dead onto a stone dungeon floor: heavy thud, short slide, cloth and leather… |
| boss_roar | v1 | 2.5s | 5ac00bbc-3d9b-410f-bd99-455c31904e63 | A huge black wolf monster roaring: deep guttural growl rising into a snarling roar, echoin… |
| boss_roar | v2 | 2.5s | 69dfbc98-0f60-45f4-97b6-5aee24685101 | A huge black wolf monster roaring: deep guttural growl rising into a snarling roar, echoin… |
| boss_die | v1 | 2.5s | ec8c2362-5590-4354-865e-e1a568aff778 | A huge wolf monster dying: a final deep whimpering growl fading, then its heavy body colla… |
| step_stone | v1 | 0.5s | fc2fe927-fbc7-4333-bf74-dafad33ba6bf | A single footstep on a stone dungeon floor, soft leather shoe sole, dry and short, subtle … |
| step_stone | v2 | 0.5s | 49c4001c-8143-4eec-a834-02a74a868b70 | A single footstep on a stone dungeon floor, soft leather shoe sole, dry and short, subtle … |
| step_stone | v3 | 0.5s | 55afc077-7aec-4c80-a887-8e9e92eb8220 | A single footstep on a stone dungeon floor, soft leather shoe sole, dry and short, subtle … |
| step_stone | v4 | 0.5s | 94158486-4dc0-438e-ac45-b470b8524eb9 | A single footstep on a stone dungeon floor, soft leather shoe sole, dry and short, subtle … |

파일 = `sfx/<큐>/<큐>_vN.flac`(원본 44.1k 스테레오 flac). 파형 대조 = `sfx/contact_batch1.png`.

## 배치 2 (재생성 6편) · 채택 결과

| 큐 | job | 요지 | 결과 |
|---|---|---|---|
| step_stone v5 | 193c6f46-d053-42cd-89bd-def3fdc09e65 | close-up 가죽 부츠 돌바닥, 굽→바닥 | 채택 (step_stone_3) |
| step_stone v6 | e0732e8e-e105-45e8-b596-35bff4ed6707 | 자갈 긁힘 | 기각 (−41 LUFS, 흐림) |
| step_stone v7 | 2e954db0-f283-4717-a2ee-396c7dae48a5 | 단단한 발구름 + 자갈 | 채택 (step_stone_1) |
| step_stone v8 | 1ac83e55-046f-4097-b335-7efae4e77bf6 | 가벼운 탭 | 채택 (step_stone_2) |
| shoot v3 | ea8590ae-42f9-4e10-b4a7-4f634985711c | 세게 던진 부적, 종이 펄럭+종소리 | 채택 (shoot_2) |
| player_hurt v4 | a6b06d4c-d0bc-4284-887e-19690dd1b6f6 | 두꺼운 도포 위 묵직한 충격 | 채택 (player_hurt_3) |

배치 1 채택: sword_swing v1~v4 → sword_swing_1~4 · hit 프로브+v1~v3 → hit_1~4 · hit_crit v1·v2 · whiff v1·v2 · player_hurt v1·v3 → _1·_2 · player_die v1 · enemy_attack v1·v2 · shoot v2 → shoot_1 · enemy_hurt v1~v3 · enemy_die v1·v2 · boss_roar v1·v2 · boss_die v1 · step_stone v1 → step_stone_4.
배치 1 기각: shoot v1(−40 LUFS 무음), step_stone v2·v3·v4(−39/−53/−56 LUFS 무음). 반입 LUFS 목표는 joseon `docs/design/audio.md §4.3`.

## BGM 후보 (보드 #42, 2026-09-18) — ACE-Step 1.5 turbo (Comfy Cloud 템플릿 `audio_ace_step_1_5_split`, API 크레딧 0·GPU 초만)

Suno는 공식 API가 없어 세션이 못 돌린다 → 오픈 모델 후보를 먼저 넣고 PD가 Suno 수동 제작으로 교체할지 판정. 입력 = `94.tags`(스타일)·`94.lyrics="[instrumental]"`·`94.bpm/keyscale/duration=90`·`98.seconds=90`·seed.

| id | job | seed | 태그 요지 |
|---|---|---|---|
| town | da8afd4c-8903-4773-8a28-a0da8336ab9c | 101 | 가야금·대금 + mellow lo-fi hip hop, 80 bpm D minor, 저녁 산골 마을 |
| dungeon | 922bfa23-7caa-4fa7-aaae-d20f4b9d20fc | 202 | dark ambient lo-fi, 드문 가야금, 서브 베이스·동굴 드론, 70 bpm E minor |
| dungeon_tense | 92fd09cd-3beb-4ffa-8fb8-b8f99f0435a8 | 303 | tense trap, 가야금 트레몰로·해금, 808, 95 bpm F minor |
| boss | 1cd97fae-0bda-4237-a284-b0f1d2dcc178 | 404 | aggressive trap, 디스토션 가야금·북, 무속 타악, 140 bpm G minor |
| kumiho | 914d5d16-20c9-4f34-b386-4d9c659fb39c | 505 | epic dark final boss, 해금 리드·태평소·합창 패드, 120 bpm C minor |

파일 = `bgm/<id>_v1.mp3`(90s, 원본 −12~−14.5 LUFS), 스펙트로그램 대조 = `bgm/contact_bgm.png`. 반입 = `intake_audio.ps1 -Src <mp3> -Cue <id> -Kind bgm`(−18 LUFS, ogg q5) — 5곡 모두 반입, 채택 여부는 PD 판정(#42).

## 배치 3 (보드 #35 월드·UI, 2026-09-18, 프로브 1 + 31편)

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100 (16-bit 스테레오 인터리브 → wav). 구독 크레딧 337 (구독 카운터 차이, 31편).

| 큐 | 변주 | 길이 | LUFS | 피크 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|
| step_dirt | v1 | 0.48s | -28.8 | -10.2 | - | Single footstep of a straw sandal on a dry packed dirt path with a little gravel: soft cru… |
| step_dirt | v2 | 0.48s | -29.5 | -8.6 | - | Single footstep of a straw sandal on a dry packed dirt path with a little gravel: soft cru… |
| step_dirt | v3 | 0.48s | -28.1 | -6.2 | - | Single footstep of a straw sandal on a dry packed dirt path with a little gravel: soft cru… |
| step_dirt | v4 | 0.48s | -18.3 | 0.2 | - | Single footstep of a straw sandal on a dry packed dirt path with a little gravel: soft cru… |
| pickup | v1 | 0.48s | -35.5 | -19.0 | - | Picking up a small item from a stone floor: quick cloth rustle and a light leather-and-woo… |
| pickup | v2 | 0.48s | -26.3 | -7.2 | - | Picking up a small item from a stone floor: quick cloth rustle and a light leather-and-woo… |
| pickup_coin | v1 | 0.60s | -18.9 | -4.5 | - | A small handful of old Korean brass coins scooped up and dropped into a cloth pouch: brigh… |
| pickup_coin | v2 | 0.60s | -20.1 | -2.9 | - | A small handful of old Korean brass coins scooped up and dropped into a cloth pouch: brigh… |
| drop | v1 | 0.60s | -54.3 | -38.7 | - | A small leather-and-wood item dropped onto a stone floor: a compact clatter with one short… |
| drop | v2 | 0.60s | -22.5 | -1.1 | - | A small leather-and-wood item dropped onto a stone floor: a compact clatter with one short… |
| potion | v1 | 1.00s | -26.9 | -9.0 | - | Drinking herbal medicine from a small ceramic bottle: a cork pop, a quick liquid swig, and… |
| potion | v2 | 1.00s | -13.6 | 0.0 | - | Drinking herbal medicine from a small ceramic bottle: a cork pop, a quick liquid swig, and… |
| level_up | v1 | 2.00s | -6.6 | 0.1 | - | Level-up chime with a Korean flavor: a bright ascending gayageum arpeggio ending on a smal… |
| level_up | v2 | 2.00s | -6.9 | 0.1 | - | Level-up chime with a Korean flavor: a bright ascending gayageum arpeggio ending on a smal… |
| portal_open | v1 | 2.00s | -14.1 | 0.0 | - | A paper talisman igniting with a soft whoosh, then an ink-black vortex portal tearing open… |
| portal_open | v2 | 2.00s | -16.3 | 0.1 | - | A paper talisman igniting with a soft whoosh, then an ink-black vortex portal tearing open… |
| portal_use | v1 | 1.20s | -11.1 | 0.4 | - | Stepping through a swirling magic portal: a fast rising whoosh that flips into a soft fall… |
| waypoint_wake | v1 | 1.76s | -25.2 | -6.7 | - | An old stone cairn shrine awakening: small stones settling and grinding, then a soft brass… |
| waypoint_wake | v2 | 1.76s | -19.5 | -1.4 | - | An old stone cairn shrine awakening: small stones settling and grinding, then a soft brass… |
| waypoint_use | v1 | 1.20s | -7.9 | -1.3 | - | Teleporting from a stone shrine: a soft airy whoosh sweeping upward with a single small br… |
| stairs | v1 | 1.00s | -42.0 | -19.8 | - | Two quick footsteps going down worn stone stairs inside a cave with a short echo, close-up… |
| revive | v1 | 2.48s | -20.4 | -10.0 | - | Waking up gently in a quiet village: a soft warm breath of wind and a single plucked gayag… |
| revive | v2 | 2.48s | -19.7 | -8.4 | - | Waking up gently in a quiet village: a soft warm breath of wind and a single plucked gayag… |
| ui_open | v1 | 0.48s | -18.9 | 0.1 | - | A paper scroll snapping open with a quick crisp paper flick and a small wooden click, clos… |
| ui_open | v2 | 0.48s | -26.5 | -7.4 | - | A paper scroll snapping open with a quick crisp paper flick and a small wooden click, clos… |
| ui_open | v3 | 0.48s | -33.4 | -7.3 | - | A paper scroll snapping open with a quick crisp paper flick and a small wooden click, clos… |
| ui_close | v1 | 0.48s | -28.0 | -9.5 | - | A paper scroll rolling shut quickly: a soft paper roll and a small wooden tap, close-up, s… |
| ui_close | v2 | 0.48s | -23.6 | -5.5 | - | A paper scroll rolling shut quickly: a soft paper roll and a small wooden tap, close-up, s… |
| coin | v1 | 0.68s | -15.8 | -1.8 | - | A few old brass coins counted and dropped onto a wooden merchant counter: short bright cli… |
| coin | v2 | 0.68s | -14.0 | -1.8 | - | A few old brass coins counted and dropped onto a wooden merchant counter: short bright cli… |
| equip | v1 | 0.68s | -18.9 | 0.5 | - | Strapping on gear: a leather strap pulled tight with a buckle click, a short cloth shift a… |
| equip | v2 | 0.68s | -22.3 | -3.3 | - | Strapping on gear: a leather strap pulled tight with a buckle click, a short cloth shift a… |

## 배치 3b (재생성 8편 — 무음·약한 것 교체: pickup·drop·potion·stairs)

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100. 구독 크레딧 0.

| 큐 | 변주 | 길이 | LUFS | 피크 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|
| pickup | v3 | 0.48s | -28.0 | -13.7 | - | Grabbing a small leather pouch off a stone floor and stuffing it into a satchel: a loud cr… |
| pickup | v4 | 0.48s | -40.0 | -23.6 | - | Grabbing a small leather pouch off a stone floor and stuffing it into a satchel: a loud cr… |
| drop | v3 | 0.60s | -21.3 | 0.1 | - | A small wooden and leather item falls onto a stone floor: a loud compact clatter with one … |
| drop | v4 | 0.60s | -34.3 | -12.2 | - | A small wooden and leather item falls onto a stone floor: a loud compact clatter with one … |
| potion | v3 | 1.00s | -24.8 | -5.2 | - | Quickly gulping a swig of liquid medicine from a small ceramic bottle: two wet gulps then … |
| potion | v4 | 1.00s | -28.5 | -4.8 | - | Quickly gulping a swig of liquid medicine from a small ceramic bottle: two wet gulps then … |
| stairs | v2 | 1.00s | -27.4 | -3.3 | - | Two loud quick footsteps of straw sandals going down worn stone stairs in a cave with a sh… |
| stairs | v3 | 1.00s | -32.8 | -10.7 | - | Two loud quick footsteps of straw sandals going down worn stone stairs in a cave with a sh… |

## 배치 4 (기합·신음 6편, 보드 #66)

생성 = ElevenLabs Sound Effects v2 직접 API (`joseon/tools/sfx_gen.py`, 키 `joseon/.env`), 출력 pcm_44100. 구독 크레딧 0.

| 큐 | 변주 | 길이 | LUFS | 피크 | request | 프롬프트 요지 |
|---|---|---|---|---|---|---|
| doho_kiai | v1 | 0.68s | -58.4 | -37.8 | - | Single short male exertion grunt while swinging a sword, sharp exhale through clenched tee… |
| doho_kiai | v2 | 0.68s | -9.4 | 0.3 | - | Single short male exertion grunt while swinging a sword, sharp exhale through clenched tee… |
| doho_kiai | v3 | 0.68s | -10.4 | 0.1 | - | Single short male exertion grunt while swinging a sword, sharp exhale through clenched tee… |
| doho_hurt | v1 | 0.80s | -11.6 | 0.1 | - | Single short male pain grunt after taking a hit, sharp inward gasp then low groan, no word… |
| doho_hurt | v2 | 0.80s | -18.7 | 0.2 | - | Single short male pain grunt after taking a hit, sharp inward gasp then low groan, no word… |
| doho_die | v1 | 1.60s | -19.8 | -6.7 | - | Male death groan, long falling exhale fading into silence, no words, dry close-up recordin… |
