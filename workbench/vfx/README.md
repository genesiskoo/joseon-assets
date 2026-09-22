# workbench/vfx — 이펙트 시트 원본 (D-075: 먹선 기본 + 영상→시트)

생성 = Comfy Cloud 템플릿 `video_wan2_2_14B_t2v` (Wan 2.2 14B fp8 + lightx2v 4-step, 640², 2s, 16fps, API 크레딧 0 · GPU ~120초/클립).
프롬프트 뼈대: "Sumi-e … a single bold **white** ink brush stroke … on a pure black background … appears, holds, then fades and dissolves … high contrast monochrome, no objects, no text, centered, static camera." (흰 먹 = 검은 배경 키잉용, 게임에서 큐 색으로 틴트)
반입 = `joseon/tools/intake_vfx.ps1 -Src <mp4> -Cue <큐> -Fps 8 -PlayFps 36 [-Start 초] -Key black` — 루프는 `-Loop -LoopBlend 3~4`(끝↔첫 크로스페이드, seam_z 로그)

| 큐 | 파일 | job | 프롬프트 요지 | 반입 |
|---|---|---|---|---|
| slash_arc | slash_arc/slash_arc_v1.mp4 | cb0c3237-c272-45da-985d-d1d8bc76f4cf | 좌상→우하 반달 붓 획 | v1 채택 (-Fps 8 -PlayFps 36 -Start 0.35) |
| hit | hit/hit_v1.mp4 | 590799bb-2b2f-44fa-9c7e-e9421d756b85 | 중앙 먹 튐(가시 돌기+방울) | v1 채택 (-Fps 12 -PlayFps 40 -End 1.1 -Units 0.8) — hit_crit·talisman_hit이 빌려 씀 |
| whirl_ring | whirl_ring/whirl_ring_v1.mp4 | 404d1954-3615-48f7-baf9-9573ae76da53 | 위에서 본 원형 붓 획 | v1 채택 (-Fps 8 -PlayFps 30 -Start 0.2) |
| enemy_windup | enemy_windup/enemy_windup_v1.mp4 | 8aad3798-b6cd-40ae-8b29-f0108cf12045 | 위에서 본 얇은 링 펄스 | **기각** — 너무 흐림 |
| enemy_windup | enemy_windup/enemy_windup_v2a.mp4 | fcad2f0b-bddf-40bf-a4ad-9713d554ba27 | 굵은 원 획 한 번에 + 펄스 1회 ("very thick heavy white ink brush stroke … bold solid ring … swells once … fades") | 예비 — 굵고 선명하나 거의 정지(펄스·페이드 없음) |
| enemy_windup | enemy_windup/enemy_windup_v2b.mp4 | 120d7b69-af53-47ef-975c-92ccbc067f81 | 두꺼운 먹 원 즉시 + 두근 2회 ("bold thick white ink circle appears instantly … heavy solid ring with ink drips and spikes … throbs twice … dissolves") | **v2b 채택** (#56, -Fps 12 -End 1.9 -Units 1.8 -Key black) — 나타나 버티다 가늘어지며 사라짐, 게임에서 재생 속도를 선딜에 맞춤 |
| talisman_paper | talisman_paper/talisman_paper_v1.mp4 | a73c0543-42c4-490d-8236-9d17848e2810 | 노란 부적 종이 회전(루프) | v1 채택 (-Fps 12 -Loop -Units 0.5 -Max 128 -LoopBlend 3, seam_z 1.47→0.75) — 투사체 본체 |
| boss_roar | boss_roar/boss_roar_v1.mp4 | 8e10db8c-6a6d-47d4-a3c8-1702325201d1 | 위에서 본 이중 링 충격파+먹 튐 | v1 채택 (-Fps 12 -PlayFps 30 -End 1.2) — 바닥, 3u |
| torch_flame | torch_flame/torch_flame_v1.mp4 | 813b7dc5-765f-47e4-866e-c0e34e9f41a3 | 촛불형 불꽃(루프) | v1 — 사진 같은 촛불, v2a로 교체 |
| torch_flame | torch_flame/torch_flame_v2a.mp4 | ba6542f7-cc54-4e57-a424-cc7bf6c7df69 | 마른 붓 불꽃 혀 + 먹 점 불씨 ("single tall tapering tongue of white ink flame painted with a dry brush … not photographic, no candle, no wick") | **v2a 채택** (#57, -Fps 12 -Loop -LoopBlend 4 -Units 0.55 -Max 128 -Crop 0,0,0,80) — 흰 먹 실루엣, 아래 심지 80px 크롭 |
| torch_flame | torch_flame/torch_flame_v2b.mp4 | 6494cb55-57b7-48b2-b9fd-dc0952d6248a | 겹친 붓 획 서예 불꽃 ("two or three overlapping white brush strokes shaped like a flame") | 기각 — 사진풍 불길로 나옴 |
| portal_idle | portal_idle/portal_idle_v1.mp4 | 1e7e8344-1009-4d44-9ba8-613f1dc28b6e | 붓 소용돌이(루프) | v1 채택 (-Fps 12 -Loop -Units 1.6 -LoopBlend 4, seam_z 1.19→0.88) — 발광 고리 대체, MANA 틴트 |


## #214 공방 6종 (2026-09-22) — 바닥 진 · 검광 마스크 · 타격 스파크 · 먼지 · 화염 폭발 · 살(독) 구름

PD 지시: 「comfy cloud mcp를 이용해서 네크로 마법진·검격 슬래시 마스크·타격 스파크·먼지 임팩트·화염 폭발 8프레임·독구름 burst 8프레임 같은 vfx를 제작하고 적용 티켓 생성해」
- 영상 = `video_wan2_2_14B_t2v`(640² · 먼지는 832×480, 2초, 16fps 33장) / 정지 = `image_z_image_turbo`(1024², 띠는 1280×320, 8 steps, seed 고정). 오픈 모델뿐 → API 크레딧 0, GPU 시간만.
- 고르기·미리보기 = `_tools/vfx_workshop.py` (키잉은 `joseon/tools/vfx_sheet.py`의 key_alpha 그대로 — 미리보기 = 게임 알파): `contact`(전 프레임 대조표+먹 양 곡선) · `pick`(원본 33장 중 N장, ease>1 = 터지는 앞을 촘촘히, `--crop`·`--black`) · `preview`/`strip`(게임 바닥색·2배 척도·도호 키 막대, 틴트 또는 색띠 `fire|sal|necro`) · `still`(정지 텍스처 키잉·트림) · `decal`(바닥 진 그려짐→회전·맥동→사라짐 시연, 아이소 ×0.577) · `trail`(띠 마스크를 칼 궤적 호에 감은 시연) · `bend`(띠 → 반달) · `spark8`(정지 섬광 → 8프레임, 예비). 검토판 = `_tools/review_board.py` → `_review_214.png`.
- **8프레임 폴더 `<cue>_<v>_8f/`가 반입 입력**이다(검은 바탕 RGB, 반입 때 `-Key black`으로 다시 키잉). 반입 명령은 적용 카드에.

| 큐 | 파일 | job | 프롬프트 요지 | 판정 · 반입 인자 |
|---|---|---|---|---|
| fire_burst | fire_burst/fire_burst_v1a.mp4 | 49bd71e4-af01-41fc-943a-7801a334a5f5 | 흰 먹 붓 불꽃 혀가 둥근 불덩이로 터짐 → 불티 → 연기로 흩어짐 ("white-hot core with grey smoky edges, dry brush") | **★ 채택** — 8f = 원본 [2,4,7,10,14,18,22,27] (`pick --start 2 --end 27 --ease 1.3`), 18fps 0.44s · 1.3u. 색은 색띠(#198)가 틴트보다 훨씬 낫다 |
| fire_burst | fire_burst/fire_burst_v1b.mp4 | 23d1e340-a009-4b59-90bf-9912843a236a | 둥근 불덩이 폭발, 흰 속 → 회색 가장자리 | 예비 — 가시 없이 둥글다. 8f 폴더 있음 |
| fire_burst | fire_burst/fire_burst_v1c.mp4 | 70adb8c0-4727-4dec-b715-4c6c292c3218 | 동양화 붓 불꽃(말린 불꽃 모양) | 예비 — 화풍은 가장 H1답지만 처음부터 타오르는 모양(터짐 없음) → #185 「타서 재」·화상 루프 후보 |
| sal_burst | sal_burst/sal_burst_v1a.mp4 | fc198353-3df6-4671-9ec7-b84ccea8e285 | 흰 연기 뭉치가 둥글게 터져 굴러 퍼짐 → 덩어리로 흩어짐 | **★ 채택** — 8f = [3,5,8,12,15,19,23,27] (`--start 3 --end 27 --ease 1.2`), 14fps 0.57s · 1.5u. 독 = 살(D-081) |
| sal_burst | sal_burst/sal_burst_v1b.mp4 | 4333afb9-993d-439b-ab6c-60116916b2ea | 무거운 안개 고리가 부풀어 흩어짐 | 예비 — 천천히 부푼다(터짐 약함) |
| sal_burst | sal_burst/sal_burst_v1c.mp4 | 6e7472fd-3780-4e08-9406-771dd3291a4c | 동양화 구름 말림(운문) 번짐 | 예비 — 조선 구름무늬가 나왔다. 독보다 **살풀이·도술 연기** 후보 |
| hit_spark | hit_spark/hit_spark_v1a.mp4 | 895c8445-ab74-4733-b2cf-65e27703908d (첫 시도 e22c6737… = 플랫폼 「Job has stagnated」 실패 → 재제출) | 흰 섬광 → 굵은 가시 별 → 불티가 흩어짐 | **★ 채택** — 8f = [1,3,5,8,10,13,16,19] (`--start 1 --end 19 --ease 1.15`), 32fps 0.25s · 1.0u |
| hit_spark | hit_spark/hit_spark_v1b.mp4 | c7470991-8e9d-4ad1-a2b9-e8b8e76b728e | 칼이 돌에 닿는 불티 별 | 기각 — 계속 타는 스파클러 + 끝에 막대가 보인다 |
| hit_spark | hit_spark/hit_spark_v2.mp4 | 17866217-7c38-467c-8622-54e2366ada94 | 네 갈래 섬광 한 번 | 기각 — 여섯 모 별 + 막대(반짝임), 터짐 아님 |
| hit_spark | hit_spark/hit_spark_still_s1.png | 1afbe298-6982-4108-a798-898ce3351d0e (seed 101) | 네 갈래 섬광 + 바늘 빛살(정지) | 예비 — `spark8`로 8프레임 가능하나 빛살이 게임 크기에서 0.5px(안 보임) |
| hit_spark | hit_spark/hit_spark_still_s2.png | c7d7a159-0699-49d8-a836-7c6429842c2d (seed 102) | 같음 | 기각 — 사진 같은 스파클러 (512px로 줄여 보관) |
| dust_impact | dust_impact/dust_impact_v1b.mp4 | 1545dbbc-e2cd-4e16-add7-88f2dc4c4cda | 옆에서 본 바닥 충격 먼지 고리 | **★ 채택** — 반사 바닥이 비쳐서 `--crop 0,0,0,112 --black 40`(바닥선 y≈360 아래 자름·회색 바닥 제거), 8f = [1,3,5,8,11,14,18,22] (`--start 1 --end 22 --ease 1.35`), 16fps 0.5s · 1.4u. **바닥 기준점 필요**(가운데 기준이면 반이 바닥에 묻힘) |
| dust_impact | dust_impact/dust_impact_v1a.mp4 | e9ce3e1b-c5a0-4f59-8f18-71d6eef5a03a | 흰 먼지 뭉치가 바닥을 따라 퍼짐(먹 붓) | 기각 — 처음부터 퍼져 있고 흰 바닥선이 끝까지 남는다 |
| necro_circle | necro_circle/necro_circle_c_s51.png | 359acaf2-b098-41f9-a798-3d6760856fed (seed 51) | 위에서 본 소환 진: 거친 겹 고리 + 안쪽 가시 고리 + 할퀸 자국 ("No letters, no runes, no animals") | **★ 채택** — `still --circle --max 512` → `necro_circle_c_s51_tex.png`, 2.2u 바닥 데칼 |
| necro_circle | necro_circle/necro_circle_b_s33.png | 357f418d-16aa-4f5f-aeee-035df39d7018 (seed 33) | 겹 고리 + 초승달·점 + 가운데 연기 소용돌이 | **★ 둘째 안** — 가운데 연기가 옅은 회색이라 색띠에서 층이 산다. `_tex.png` 있음 |
| necro_circle | necro_circle/necro_circle_c_s52.png | bed59130-0902-4e11-ac9a-a7ccc7c1d908 (seed 52) | c와 같음 | 예비 — 더 단순 |
| necro_circle | necro_circle_a_s11 / a_s22 | 5402ff1c-f186-4edf-8a7a-7c2549b39825 / a9b378f4-6624-41c8-b0aa-663fb6c81e94 | 가시 고리 + 부적 문양 8개 | 기각 — 문양이 알파벳·한글 글자처럼 나온다 |
| necro_circle | necro_circle_b_s44 | b53dd21f-98bf-4f72-906e-0a24461a5e06 | 「cursed seal circle」 | 기각 — **seal을 동물 물범으로 읽어** 가운데에 물범 |
| necro_circle | necro_circle_d_s61 / d_s62 | fc82144a-d129-401f-b925-4d7cf517cbf0 / 0b382679-6357-4355-967f-4ba47e5fa417 | 겹 원 + 가시 12 + 초승달 고리 | 기각 — 조타륜·과녁·나침반처럼 읽힌다 |
| slash_mask | slash_mask/slash_mask_strip_s7.png | b7788b44-b4f8-44cb-9999-b5281885027f (seed 7) | 가로 마른 붓 한 획, 오른쪽 뭉툭·왼쪽 붓결 꼬리 | **★ 채택(띠)** — `still --max 1024` → `slash_mask_strip_s7_tex.png` 1024×198. 머리 = 오른쪽, 꼬리 = 왼쪽, 위 = 칼끝 |
| slash_mask | slash_mask/slash_mask_strip_s8.png | 90674ebd-a5da-4a2d-a21c-a6ab6a09322b (seed 8) | 같음 | **★ 채택(반달)** — 뾰족한 꼬리 → `bend --tail -75 --head 75` → `slash_mask_arc_s8_tex.png` 614×271. 띠 예비 |
| slash_mask | slash_mask_arc_s5 / s6 | 5fcd47d0-e5ca-45a8-a468-a95640c61e11 / 76dd7cbd-7b23-4611-bdba-9e47242dc07c | 「crescent-shaped sword slash」 | 기각 — 매끈한 초승달(달)로 나온다 |
| slash_mask | slash_arc_v2_s71 / s72 | aa830074-990f-45f6-acf2-a7da94040b1a / 64b92932-e621-467d-89f2-7cf9cabe3351 | 애니풍 반원 슬래시 속도선 | s71 예비(붓결 고리 — 회오리 링 마스크 후보) · s72 기각. 둘 다 반원 대신 **고리 전체**가 나왔다 |

**재밟지 말 것 (#214)**: ① Z-Image는 말을 곧이곧대로 읽는다 — 「seal」 = 물범, 「crescent」 = 초승달, 「half circle slash」 = 고리. 모양은 「single horizontal dry brush stroke」처럼 **물건 이름 없이 붓 동작으로** 말하고, 호는 띠를 `bend`로 구부려 만든다 ② 진·부적 문양은 「talisman glyph」라고만 해도 글자가 나온다 → 「No letters, no alphabet, no runes, no writing」 + 가시·할퀸 자국·점 같은 **도형만** ③ Wan 「spark」는 스파클러(막대 달린 불꽃놀이)로 가기 쉽다 → 「one single quick impact … not continuous, no stick」 ④ Wan 먼지는 반사 바닥을 같이 그린다 → 바닥선 아래 크롭 + 검정점 ⑤ Comfy Cloud 영상은 계정당 한 번에 한 건씩 돌고(이미지는 여러 건 동시), 드물게 「Job has stagnated」로 실패 → 같은 인자로 재제출 ⑥ 이미지 결과 링크(`/api/s/…?raw=1`)는 몇 분 안에 만료 — 받자마자 내려받는다.

## #231 이펙트 시안 — 먹물·한자 (2026-09-22)

PD 「시안으로 만들어봐 before/after보고 결정」. 실제 게임 화면을 두 번 찍어(지금 이펙트 / 이펙트만 숨김) 숨긴 판 위에 시안을 합성했다. 합성 스크립트·한 장짜리 before/after·글자판은 게임 저장소 `docs/art/231_vfx_mockup/`, 사양 `design/vfx.md §8.7`.

| 파일 (`mock_231/`) | 무엇 |
|---|---|
| `pair_levelup/drops/roar/boss/portal.gif` | 지금 \| 시안 나란히 (움직임) |
| `glyph_sheet_231.png` | Z-Image 한자·낙관 18장 전부 (기각본 포함) |
| `contact_gold_column/ink_vortex/ink_ripple/ink_bloom.png` | Wan 먹 영상 4편 33장씩 |
| `raw/` | 생성 원본 — 고른 것 원본 크기, 기각·예비는 512px |

| 원본 | 판정 | 쓰임 |
|---|---|---|
| glyph_do_s2 · glyph_seung_s1 · glyph_bong_s1 · glyph_no_s1 · glyph_hwa_s1 · glyph_bing_s1 · glyph_wan_s1 · glyph_bo_s1 | 채택 후보 | 道(레벨업)·昇(둘째)·封·怒·火·冰(氷 대신)·完·寶 |
| stamp_bo_s2 · stamp_wan_s1 · stamp_bong_s1 | 채택 후보 (도장 면만 떠서) | 寶 낙관(유니크)·完 낙관·封 낙관(봉인 조각) |
| glyph_do_s1 | 기각 — 흰 테두리 | |
| glyph_hwa_s2 | 기각 — 다른 글자 | |
| glyph_seung_s2 · glyph_bong_s2 · glyph_no_s2 · glyph_bing_s2 · stamp_bo_s1 | 예비 | |
| wan_gold_column | 채택 — 앞 0~10장 가시 분수(레벨업·유니크), 12~22장 가는 기둥(Magic·Rare) | |
| wan_ink_vortex | 채택 — 돌기만 하고 모이지 않아 줄이며 돌리는 건 코드 | 흑랑 처치 |
| wan_ink_ripple | 채택 — 광택 고리지만 금니로 물들이면 쓸 만 | 착지·레벨업 파문 |
| wan_ink_bloom | 기각 — 반사 바닥이 같이 나옴 | 화면 전환은 잡음 셰이더 |

재밟지 말 것: Z-Image는 한자를 정자로 쓴다(氷만 冰으로) · 「seal stamp impression」 = 입체 돌도장 사진 · 마른 붓 띠(#214 s7)를 세운 광선은 게임 크기(폭 20px)에서 판자.

### #231 2차 — 한자를 획 단위로 쓰는 스프라이트 (2026-09-22)

PD 「붓글씨 획단위로 쓰는걸 스프라이트로」. 첫 프레임 = 빈 검정(`flf/flf_black.png`), 끝 프레임 = Z-Image 글자(`flf/flf_do_end.png`·`flf_bong_end.png`)로 박은 영상(FLF2V) → 쓰는 구간 15장.

| 파일 (`mock_231/flf/`) | 모델 | 쓰기 지수 | 판정 |
|---|---|---|---|
| `wanflf_do_a.mp4` → `do_a_14f/` | Wan 2.2 14B FLF2V 49장 (API 0) | 0.50 | **채택 후보** — 首 → 책받침(교본 순서) |
| `wanflf_do_b.mp4` → `do_b_14f/` | Wan 2.2 | 0.50 | 예비 — 책받침 먼저 |
| `wanflf_bong_a.mp4` → `bong_14f/` | Wan 2.2 | 0.50 | **채택 후보** — 圭 → 寸 |
| `wanflf_bong_b.mp4` | Wan 2.2 | 0.50 | 예비 |
| `sd25flf_do.mp4` → `sd_do_14f/` | Seedance 2.5 FLF2V 121장 (약 352크레딧) | 0.50 | 예비 — 책받침 먼저·획 사이 멈춤(`--by cover`) |
| `sd25flf_bong.mp4` | Seedance 2.5 | 0.50 | 예비 |

- 비교판 = `flf/write_board.png`, 영상별 대조표 = `flf/check_*.png`, 게임 합성 = `pair_levelup2.gif`·`pair_boss2.gif`.
- 도구: `_tools/stroke_check.py`(쓰기 지수 = 글자 자리 밝기 흩어짐 최댓값, 0.35↑ = 획으로 씀), `_tools/stroke_sprite.py`(첫 먹 3%~완성 97%를 N장 + 끝 1장, `--by cover` = 먹 양 기준).
- 결론: 쓰기 품질은 Wan = Seedance → 제작은 Wan(무료).
