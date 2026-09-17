# workbench/vfx — 이펙트 시트 원본 (D-075: 먹선 기본 + 영상→시트)

생성 = Comfy Cloud 템플릿 `video_wan2_2_14B_t2v` (Wan 2.2 14B fp8 + lightx2v 4-step, 640², 2s, 16fps, API 크레딧 0 · GPU ~120초/클립).
프롬프트 뼈대: "Sumi-e … a single bold **white** ink brush stroke … on a pure black background … appears, holds, then fades and dissolves … high contrast monochrome, no objects, no text, centered, static camera." (흰 먹 = 검은 배경 키잉용, 게임에서 큐 색으로 틴트)
반입 = `joseon/tools/intake_vfx.ps1 -Src <mp4> -Cue <큐> -Fps 8 -PlayFps 36 [-Start 초] -Key black`

| 큐 | 파일 | job | 프롬프트 요지 | 반입 |
|---|---|---|---|---|
| slash_arc | slash_arc/slash_arc_v1.mp4 | cb0c3237-c272-45da-985d-d1d8bc76f4cf | 좌상→우하 반달 붓 획 | v1 채택 (-Fps 8 -PlayFps 36 -Start 0.35) |
| hit | hit/hit_v1.mp4 | 590799bb-2b2f-44fa-9c7e-e9421d756b85 | 중앙 먹 튐(가시 돌기+방울) | v1 채택 (-Fps 12 -PlayFps 40 -End 1.1 -Units 0.8) — hit_crit·talisman_hit이 빌려 씀 |
| whirl_ring | whirl_ring/whirl_ring_v1.mp4 | 404d1954-3615-48f7-baf9-9573ae76da53 | 위에서 본 원형 붓 획 | v1 채택 (-Fps 8 -PlayFps 30 -Start 0.2) |
| enemy_windup | enemy_windup/enemy_windup_v1.mp4 | 8aad3798-b6cd-40ae-8b29-f0108cf12045 | 위에서 본 얇은 링 펄스 | **기각** — 너무 흐림 |
| enemy_windup | enemy_windup/enemy_windup_v2a.mp4 | fcad2f0b-bddf-40bf-a4ad-9713d554ba27 | 굵은 원 획 한 번에 + 펄스 1회 ("very thick heavy white ink brush stroke … bold solid ring … swells once … fades") | 예비 — 굵고 선명하나 거의 정지(펄스·페이드 없음) |
| enemy_windup | enemy_windup/enemy_windup_v2b.mp4 | 120d7b69-af53-47ef-975c-92ccbc067f81 | 두꺼운 먹 원 즉시 + 두근 2회 ("bold thick white ink circle appears instantly … heavy solid ring with ink drips and spikes … throbs twice … dissolves") | **v2b 채택** (#56, -Fps 12 -End 1.9 -Units 1.8 -Key black) — 나타나 버티다 가늘어지며 사라짐, 게임에서 재생 속도를 선딜에 맞춤 |
| talisman_paper | talisman_paper/talisman_paper_v1.mp4 | a73c0543-42c4-490d-8236-9d17848e2810 | 노란 부적 종이 회전(루프) | v1 채택 (-Fps 12 -Loop -Units 0.5 -Max 128) — 투사체 본체 |
| boss_roar | boss_roar/boss_roar_v1.mp4 | 8e10db8c-6a6d-47d4-a3c8-1702325201d1 | 위에서 본 이중 링 충격파+먹 튐 | v1 채택 (-Fps 12 -PlayFps 30 -End 1.2) — 바닥, 3u |
| torch_flame | torch_flame/torch_flame_v1.mp4 | 813b7dc5-765f-47e4-866e-c0e34e9f41a3 | 촛불형 불꽃(루프) | v1 채택 (-Fps 12 -Loop -Units 0.55 -Max 128) — 발광 구 대체, FIRE 틴트. 붓 느낌은 약함(후보 재생성) |
| portal_idle | portal_idle/portal_idle_v1.mp4 | 1e7e8344-1009-4d44-9ba8-613f1dc28b6e | 붓 소용돌이(루프) | v1 채택 (-Fps 12 -Loop -Units 1.6) — 발광 고리 대체, MANA 틴트 |

