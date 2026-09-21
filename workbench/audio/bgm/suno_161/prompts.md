# Suno BGM 2차 — 조선 다크 판타지 프롬프트 (보드 #161, 2026-09-21)

사양·방향 = joseon `docs/design/audio.md §4.6`. 여기는 Suno 입력 원문(그대로 붙여 넣은 값).

## 결과 (2026-09-21, 8회 × 2곡, 크레딧 2,480 → 2,400)

곡 id = `https://suno.com/song/<id>`. 다운로드는 PD 판정 뒤 채택분만(Pro 월 20곡 한도, 남은 27).

| 후보 | v1 | v2 |
|---|---|---|
| town A 못골 해질녘 | 65098377-4d39-45e7-82b4-a1dcc4158c0a (2:59) | 0a3109df-813a-4985-a3bb-c93c55c4a081 (3:00) |
| town B 빈 저잣거리 | 6d829d97-e048-46d7-a5c2-0eace9128412 (3:00) | 41955224-f9eb-48ac-8e09-8fdcd70e466c (3:00) |
| dungeon A 봉인굴 | 3ae27eaf-1b2c-4577-a54f-2d3749909cc3 (3:30) | 952fac3b-cbd5-466d-ac0b-74dffadcf9ed (3:30) |
| dungeon B 곡소리 나는 굴 | 519f8df2-89c8-426a-a64f-661b4375421c (3:29) | e4f2086e-e1a3-40c6-bf79-f552b4550d5c (3:30) |
| tense 미궁 | d17f96b0-ac09-4a82-ac55-38000d0f7437 (2:30) | 2d6c3863-cd5a-40b6-897f-2b7eafef2cce (2:30) |
| boss A 굿판 | c854cc33-e677-4996-b3bd-ce659e0ab397 (2:30) | aaccf484-54dd-4777-83d9-add91b04359a (2:30) |
| boss B 무당 칼춤 | 5531a81e-2b97-45b8-9403-cfbae248d96c (2:30) | 7a492909-358f-438d-85bb-68b4533a12c6 (2:30) |
| kumiho 여우의 웃음 | b1023f53-882c-48ad-87a1-98938c69c9b7 (3:00) | df9dc8e0-3776-4ffb-84d1-64e7d04a6f33 (2:59) |
| **던전 재생성 (2026-09-22, 2,400 → 2,370)** | | |
| dungeon C 고요한 굴 | 19e1ec4e-8140-4de8-8887-8899e27c2766 (4:00) | 0d32587a-a831-4f45-a149-9ca640f722b0 (4:00) |
| dungeon D 느린 맥박 | 447c60ae-acb8-4d0c-bf98-74c4c9a73981 (4:00) | 20dee3c7-63b6-4c0b-a7e3-f2b5a56d8e07 (4:00) |
| dungeon E 먼 허밍 | 503d3b87-5a6c-4bfd-a7e0-2258d6a9beef (4:00) | 11ab73a4-3e55-45b3-8a8b-8777990fda74 (3:59) |

## 입력 요령 (Chrome 제어, 다음 세션용)

- 스타일·제외 스타일·제목 = 네이티브 value setter + `input` 이벤트로 넣는다(React 상태에 들어가는지는 `NNN/1000` 글자 수 표시로 확인). 긴 스타일을 키보드로 치면 페이지가 30초 넘게 멈춘다.
- **가사 칸은 특수 편집기(contenteditable)** — `execCommand('insertText')`는 줄바꿈이 사라지고 `insertParagraph`도 안 먹는다. 칸을 클릭 → Ctrl+A → Backspace → 한 줄씩 타이핑 + Enter 키. 빈 가사 = 인스트루멘털.
- 슬라이더(`role=slider`)는 JS로 focus한 뒤 화살표 키: Weirdness·Style Influence 1%씩, Duration 5초씩(10~360초).
- Vocal Gender 버튼은 누를 때마다 켜고 끈다(인스트 곡에선 끔). Max Mode = 2배 크레딧.
- 곡은 비공개로 생긴다(목록의 Publish 버튼 = 아직 비공개). Publish는 누르지 않는다.
- Create 뒤 페이지가 새로 고쳐지며 입력칸·More Options(접힘)·길이(Auto)가 초기화될 때가 있다 → 매번 글자 수·슬라이더 값을 확인하고 누른다. 길이 Custom 버튼은 More Options를 펼치고 패널을 내려야 보인다.
- 슬라이더 focus는 값 넣는 JS와 **따로** 호출해야 화살표가 먹는다(같은 호출 끝에 focus하면 다시 그리면서 풀린다).

공통 설정: Suno **v6** · Advanced(Custom) · Max Mode **Off**(켜면 2배 크레딧) · Variety Normal · Personalize Off · Save to My Workspace(비공개 — Publish 누르지 않음).
가사 칸이 비어 있으면 인스트루멘털. 목소리 후보는 **가사 없는 소리만**(D-017 — 가사 있는 가창은 음성). `[대괄호]` = 연출 지시(안 부름), `(소괄호)` = 부르는 소리.

---

## town_A — 못골 해질녘 (가야금 산조 독주)

- 제목: `JH161 town A 못골 해질녘` · 길이 3:00 · Weirdness 40% · Style Influence 70% · 가사 없음
- Styles:
  > dark fantasy RPG town theme, Korean traditional gugak, solo gayageum (Korean zither) in slow sanjo style, deep string bends and trembling vibrato, lonely modal melody with long pauses, daegeum (bamboo flute) with breathy buzzing tone answering from far away, soft buk drum like a slow heartbeat, low geomungo plucks, cold evening wind, distant temple bell, haunted village after a broken seal, sorrowful but calm, sparse, spacious reverb, free slow tempo, ends softly for seamless looping, instrumental game underscore
- Exclude: `pop, k-pop, ballad, lo-fi hip hop, trap, drum kit, piano, acoustic guitar, synth lead, vocals, cheerful, upbeat`

## town_B — 빈 저잣거리 (아쟁·생황 황량형)

- 제목: `JH161 town B 빈 저잣거리` · 길이 3:00 · Weirdness 50% · Style Influence 70% · 가사 없음
- Styles:
  > haunting dark fantasy village underscore, Korean traditional instruments, ajaeng (bowed Korean zither) playing a slow low lament with raspy bow friction, daegeum long breathy tones, sparse gayageum harmonics, low saenghwang (mouth organ) drone, soft jing (gong) swells, faint shaman bells far away, wind through empty streets, desolate and mournful, uneasy calm, very slow and sparse, lots of silence, wide cinematic reverb, instrumental
- Exclude: `pop, k-pop, ballad, lo-fi hip hop, trap, drum kit, piano, acoustic guitar, synth lead, vocals, cheerful, upbeat`

## dungeon_A — 봉인굴 (드론·물방울, 선율 없음)

- 제목: `JH161 dungeon A 봉인굴` · 길이 3:30 · Weirdness 60% · Style Influence 70% · 가사 없음
- Styles:
  > dark ambient horror score for an underground sealed dungeon, Korean traditional, deep ajaeng drones with raspy scraping bow, low geomungo plucks echoing through a cave, slow jing (gong) swells, water dripping in stone halls, sub-bass rumble, faint metallic scrapes, reversed breaths, a distant daegeum cry now and then, no melody, no beat, slowly evolving dread, claustrophobic, immense reverb, sparse and patient, instrumental
- Exclude: `pop, k-pop, trap, hip hop, EDM, drum kit, piano, guitar, synth lead, vocals, cheerful`

## dungeon_B — 곡소리 나는 굴 (먼 곡소리)

- 제목: `JH161 dungeon B 곡소리 나는 굴` · 길이 3:30 · Weirdness 65% · Style Influence 70% · Vocal Gender Female
- Styles:
  > dark ambient horror, Korean funeral lament echoing from deep underground, distant wordless female mourning wails and sobs, raw hoarse pansori-style cries without words, far away and drenched in cave reverb, low ajaeng drone, slow buk heartbeat, jing (gong) swells, shaman bells, dripping water, cold wind, sparse, eerie dread, very slow, dungeon game underscore
- Exclude: `pop, k-pop, ballad, trap, hip hop, drum kit, piano, guitar, synth lead, rap, spoken word`
- Lyrics:
  ```
  [Intro]
  [low ajaeng drone, dripping water]

  [Verse]
  (아... 아아...)
  (어... 어허...)

  [Break]
  [silence, distant gong]

  [Verse]
  (흐으... 흐으...)
  (아아아...)

  [Outro]
  [drone fades into dripping water]
  ```

## dungeon_tense — 미궁 (아방가르드)

- 제목: `JH161 tense 미궁` · 길이 2:30 · Weirdness 85% · Style Influence 60% · Vocal Gender Female
- Styles:
  > avant-garde Korean experimental horror, gayageum played with a cello bow, scraped and struck strings, prepared zither clusters, sudden sharp plucks after long silences, shrill haegeum (Korean fiddle) glissandi, piri cries, irregular janggu hits, rattling shaman bells, female voice extended techniques: whispers, gasps, moans, sobbing and eerie laughter without words, unsettling tension, ritual madness, close and dry then vast reverb, dark dungeon combat underscore
- Exclude: `pop, k-pop, ballad, trap, EDM, drum kit, piano, guitar, synth, rap, spoken word`
- Lyrics:
  ```
  [Intro]
  [bowed gayageum scrape, silence]

  [Verse]
  (흐...)
  (아... 아아...)
  [whispering]

  [Build]
  (흐으으...)
  [sobbing turns into laughter]

  [Break]
  [sudden silence, single plucked string]

  [Verse]
  (하... 하하...)
  (아아악!)

  [Outro]
  [breath fades]
  ```

## boss_A — 굿판 (휘모리 굿 광란, 인스트)

- 제목: `JH161 boss A 굿판` · 길이 2:30 · Weirdness 45% · Style Influence 70% · 가사 없음
- Styles:
  > dark ritual boss battle music, Korean shamanic gut ceremony turned into combat, fast hwimori rhythm on janggu and buk war drums, clanging kkwaenggwari and crashing jing (gong), shrieking taepyeongso (Korean shawm) melody, raspy ajaeng ostinato, haegeum stabs, deep thunderous drums, low strings and brass for weight, frenzy and dread, relentless driving groove, rising intensity, cinematic game boss fight, instrumental
- Exclude: `pop, k-pop, trap, hip hop, EDM, electric guitar, rock, metal, synth lead, vocals, cheerful`

## boss_B — 무당 칼춤 (자진모리 + 외침)

- 제목: `JH161 boss B 무당 칼춤` · 길이 2:30 · Weirdness 50% · Style Influence 70% · Vocal Gender 지정 안 함
- Styles:
  > Korean shamanic battle trance, fast jajinmori 12/8 groove on janggu, pounding buk, clanging kkwaenggwari and jing, taepyeongso war cry, wordless ritual shouts and chanting vocables from a shaman choir, primal and hypnotic, heavy low drums, raspy ajaeng, dark cinematic boss fight, rising tension
- Exclude: `pop, k-pop, trap, hip hop, EDM, electric guitar, rock, rap, spoken word`
- Lyrics:
  ```
  [Intro]
  [jing crash, drums rising]

  [Chant]
  (어이! 어이!)
  (허어! 허어!)

  [Instrumental]
  [taepyeongso lead]

  [Chant]
  (어허어! 어허어!)

  [Breakdown]
  [only drums and ajaeng]

  [Chant]
  (어이! 어이!)
  (하아!)

  [Outro]
  [jing crash]
  ```

## 던전 재생성 (2026-09-22, PD 판정 1 — 「으스스하되 시끄럽지 않게, 템포·노이즈 거슬림」)

원칙 = joseon `audio.md §4.6.2`: 템포 고정 · 노이즈(긁힘·금속·물방울·바람·저음 웅웅) 빼기 · 음량 고르게 · 4분.

### dungeon_C — 고요한 굴 (드론, 타악 없음)

- 제목: `JH161 dungeon C 고요한 굴` · 길이 4:00 · Weirdness 35% · Style Influence 80% · 가사 없음
- Styles:
  > quiet eerie underscore for exploring sealed underground ruins, Korean traditional instruments played softly, low saenghwang (mouth organ) holding a sustained unresolved chord, ajaeng (bowed zither) long smooth low tones, soft breathy daegeum phrases far away, rare single gayageum harmonics, minor mode, lingering tension, steady and even from start to finish, soft dynamics, no build-up, no climax, no percussion, clean warm tone, lots of space, gentle reverb, calm but uneasy, stays in the background, instrumental
- Exclude: `drums, percussion, beat, crescendo, build-up, climax, epic, cinematic, noise, harsh, distortion, glitch, industrial, scraping, fast tempo, vocals, pop, k-pop, trap, synth lead`

### dungeon_D — 느린 맥박 (일정한 박)

- 제목: `JH161 dungeon D 느린 맥박` · 길이 4:00 · Weirdness 40% · Style Influence 80% · 가사 없음
- Styles:
  > subdued eerie exploration music for sealed underground ruins, Korean traditional, soft muffled buk drum like a slow steady heartbeat at a constant 60 BPM that never speeds up, low geomungo plucks with long decay, quiet ajaeng drone underneath, a sparse haunting gayageum motif in a minor mode repeating patiently, restrained even dynamics, soft and low in the mix, no build-up, no climax, clean tone, calm tension, spacious reverb, loopable game background, instrumental
- Exclude: `crescendo, build-up, climax, accelerando, fast tempo, epic, cinematic, taiko, war drums, noise, harsh, distortion, glitch, scraping, vocals, pop, k-pop, trap, EDM, synth lead`

### dungeon_E — 먼 허밍 (희미한 목소리 두 번)

- 제목: `JH161 dungeon E 먼 허밍` · 길이 4:00 · Weirdness 40% · Style Influence 80% · Vocal Gender Female
- Styles:
  > quiet haunted underscore for sealed underground ruins, Korean traditional, low ajaeng and saenghwang sustained drone, soft daegeum answering phrases, a faint distant wordless female humming that appears rarely and softly like a memory, never wailing, minor mode, steady even dynamics throughout, no build-up, no climax, no percussion, clean tone, gentle reverb, calm but haunted, stays in the background
- Exclude: `drums, percussion, crescendo, build-up, climax, epic, cinematic, noise, harsh, distortion, scraping, wailing, screaming, choir, pop, k-pop, ballad, trap, synth lead, rap, spoken word`
- Lyrics:
  ```
  [Intro]
  [soft drone]

  [Instrumental]
  [daegeum far away]

  [Verse]
  (음...)

  [Instrumental]
  [drone continues softly]

  [Verse]
  (음... 음...)

  [Outro]
  [soft drone fades]
  ```

## kumiho — 여우의 웃음 (구미호)

- 제목: `JH161 kumiho 여우의 웃음` · 길이 3:00 · Weirdness 65% · Style Influence 70% · Vocal Gender Female
- Styles:
  > final boss theme of a nine-tailed fox demon, seductive and terrifying, eerie female vocalise, wordless moans, sighs and cruel laughter, hoarse pansori-style wailing high notes without words, bowed gayageum and haegeum weaving a hypnotic melody, then a full shamanic ensemble: fast janggu and buk, clanging kkwaenggwari, shrieking taepyeongso, deep jing, dark orchestral strings and low choir, beautiful yet horrifying, rising dread, cinematic climax
- Exclude: `pop, k-pop, ballad, trap, hip hop, EDM, electric guitar, synth lead, rap, spoken word`
- Lyrics:
  ```
  [Intro]
  [soft laughter, bowed gayageum]

  [Verse]
  (아... 아아...)
  (흠... 흐음...)

  [Build]
  (아아아...)
  [drums gather]

  [Chorus]
  (아아아! 아아아!)
  (하하하...)

  [Break]
  [whispers, silence]

  [Chorus]
  (아아아! 아아아!)

  [Outro]
  [laughter fades into wind]
  ```
