# #1222 귀새 G4 — 동작 16 (Tripo 웹)

**바이블 칸** = 인물 동작(§2 · D-087 동작마다 고른다) · **서비스** = Tripo 웹 Animate(작업 `8a95ac26-a47e-4d25-85d8-221f96f40da8`, 귀새 몸 · Mixamo 65뼈) · **예산** = **PD 승인 2026-11-08 「160까지 승인」** → **쓴 것 140크레딧**(잔액 1,705 → 1,565 · 남은 예산 20).

## 출처

| 게임 클립 | 출처 | 종류 | 크레딧 |
|---|---|---|---:|
| idle · walk · run · hit · die | Tripo 프리셋 idle · walk · run · hit_to_body_01 · fall | 프리셋 | 0 |
| skill_roll | 프리셋 dive | 프리셋 | 0 |
| skill_heavy | 프리셋 chop | 프리셋 | 0 |
| skill_toss | 계정에 있던 AI 「Needle Throw Motion」 | 옛 AI(다시 걸기 무료) | 0 |
| skill_leap_strike | 계정에 있던 AI 「Sword Strike Leap」(도호 ai_leap_slash와 같은 것) | 옛 AI | 0 |
| attack | AI 「Dagger Slash」(문장 = Dagger slash A …, 2초) | 새 AI | 20 |
| attack2 | AI 「Backhand Dagger Slash」(Dagger slash B …, 2초) | 새 AI | 20 |
| skill_kkekki | AI 「Dagger Stabbing Motion」(Twin dagger stabs …, 2초) | 새 AI | 20 |
| skill_throw | AI 「Fan Knife Throw」(2초) | 새 AI | 20 |
| skill_finisher | AI 「Assassin Plunge Attack」(Execution plunge …, 3초) | 새 AI | 20 |
| skill_net | AI 「Rope Net Throw」(Net throw …, 2초) | 새 AI | 20 |
| mask_swap | AI 「Mask Swap」(2초) | 새 AI | 20 |
| | | **합계** | **140** |

- 크레딧 흐름: 1,705 → 1,685(평타 A) → 1,585(다섯) → 1,565(탈 바꿈). 이미 만든 AI 동작은 다른 몸에 다시 걸어도 0(실측 — 바늘 던지기 걸고 1,705 그대로).
- 내보내기 = Export FBX(Blender 프리셋 · 2k · 뼈대 · 동작 49 Select All · stay in place) — 무료.

## 파일

| 파일 | SHA-256 | 비고 |
|---|---|---|
| `src/gwisae_all_49.fbx` | `ec01b7861fd78dfaec3e9b517d95148f92eb5e1926430c9b7002135ee08c815c` | Tripo 내보내기 원본(동작 49 = 프리셋 19 + 옛 AI 23 + 새 AI 7 · 8,064KB) |
| `tripo_gwisae_anim_v2.json` | (게임 저장소 `tools/plans/` 사본) | 클립 16 계획 — 구간·길이·타격 |
| `gwisae_v2_clips.json` | — | tripo_anim 보고(길이·타격 비율·칼끝 빠르기) |
| 게임 `assets/models/gwisae/gwisae.glb` | `86cf76ee4f58d513ee7cf709965f7e229fccd8579685e8389d5912934ad0842d` | 뼈 68(포니테일) · 클립 16 · 60fps · 1024 무광 · 2,032KB |

## 굽기 사슬 (게임 저장소에서)

`tripo_anim.py --plan=tools/plans/tripo_gwisae_anim_v2.json --tex=1024`(키 원본 그대로 · 칼 방향: 깨끼·무거운 칼 = forearm · 막 내림 = arm · 나머지 keep) → `hair_tail.py`(Pony1~3 · 정점 773) → `hand_grip.py`(주먹 80·95·60° · 엄지 35°) → `albedo_ops.py shrink --name basecolor` → `matte` → 재질 한쪽 면.
- 함정: hair_tail·hand_grip이 Blender 기본 24fps로 다시 구워 60fps 키가 줄었다(평타 34키 → 14키) → 두 도구에 `--fps`(기본 60) 장면 맞추기 넣음(reskin_rig #681과 같은 함정).
- 주먹 손아귀 = 이전(#1222 1단계)과 소수점까지 같음 → ModelDef 단검 보정값 그대로.
