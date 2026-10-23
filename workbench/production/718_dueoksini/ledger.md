# #718 두억시니 — 훅 · 강타 · 맞기 새 동작 (PD 10-24)

- 서비스 = Meshy(동작 라이브러리 animate · text-to-motion prime + 입히기) · 리그 = 기존 두억시니 Meshy 리그(`01a0d3db…`) · 생성 = 지휘 · 반입·손질 = 일꾼(#718 자리 `claude/718-dueoksini-intake`)
- 크레딧 합 = **48** = 1차 라이브러리 **9**(3 × 3동작 — 193 · 86 · 175) + 강타 글로 만든 A/B **26** + 낮은 훅 **13**
- 작업 id = 지휘가 일꾼에게 넘긴 만큼(뒤가 「…」인 것은 앞자리만 받음 — 지휘가 전부 채운다). GLB 안에는 작업 id가 없다(Blender 내보내기 머리말뿐).

| 차 | 칸 | 동작 | 클립 이름(GLB 안) | 받은 파일 | 길이 | SHA-256 | 작업 id | 쓰임 |
|---|---|---|---|---|---|---|---|---|
| 1 | 훅 `attack_punch` | 라이브러리 193 Left Hook from Guard | `Armature\|Left_Hook_from_Guard\|baselayer` | `clips/hook_193.glb` | 1.03초 | `0e56da5ab5c1c1569cb5733398c6374463f25ad0e5e915e1139b08c2e6dc0c57` | (지휘 기록 — 받지 못함) | ✗ 갈음(제 머리 높이 2.33m를 쳐 도호 위로 지남) |
| 1 | 강타 `slam` | 라이브러리 86 Jump Attack | `Armature\|Basic_Jump\|baselayer` ⚠ 이름이 Basic_Jump | `clips/slam_86.glb` | 5.93초 | `f311e6e112e2e7e99aea8f0ada2a1727705dae4247660e04395de9c5f40c2207` | (지휘 기록 — 받지 못함) | ✗ 갈음(PD 「글로 만든 B」) |
| 1 | 맞기 `hit` | 라이브러리 175 Face Punch Reaction 1 | `Armature\|Face_Punch_Reaction_1\|baselayer` | `clips/hit_175.glb` | 4.53초 | `d22b7000937288ef7be4f872d7fd23dec5ba6921bbe31bb9611acf0fd976afcb` | (지휘 기록 — 받지 못함) | ○ 게임에 들어감 |
| 2 | 강타 후보 A | text-to-motion prime → 입히기 | (반입 안 함) | `clips/slam_t2m_a.glb` | — | `221483bfd445a4041b9ad845581e58558df11b059b17e18e5b935298107e979c` | (지휘 기록 — 받지 못함) | ✗ PD가 B를 고름 |
| 2 | 강타 `slam` B | text-to-motion prime `01a16976-2b2f…` → 입히기 `01a16976-87a8…` · 한 주먹 망치질 | `retarget_clip` (트랙 21) | `clips/slam_t2m_b.glb` | 3.47초 | `4b3ad8197b9cf0bf433e0f0617d7634b5c41ff7601ebccb4b5d9cde83843fe7c` | `01a16976-2b2f…` · `01a16976-87a8…` | ○ 게임에 들어감 |
| 2 | 훅 `attack_punch` 낮은 훅 | text-to-motion `01a1699f-717a…` → 입히기 `01a1699f-c7a9…` · 가슴~허리 큰 왼 훅 | `retarget_clip` (트랙 21) | `clips/hook_t2m_low.glb` | 2.47초 | `b32332cec76447ef29f240ff6e9739a72855cee3939ee71874a704fd21d24fee` | `01a1699f-717a…` · `01a1699f-c7a9…` | ○ 게임에 들어감 |

## 반입 (게임 저장소 `assets/models/dueoksini/dueoksini.glb`, `tools/merge_anims.gd --keep`)

| 판 | 바꾼 클립 | GLB SHA-256 | 크기 |
|---|---|---|---|
| #891 주먹 반영본(반입 전) | — | `8e8576168a608603a8449f8f86cd78ca50055f82294db2117c27b03da278ad41` | — |
| 1차 (커밋 `27753ac4`) | attack_punch ← hook_193 · slam ← slam_86 · hit ← hit_175 | `a4d6017ce9e4d275ab1fe22a76b8d0e0b0393e815a853c7989c725e1465af2fa` | 3,728,484 B |
| **2차 (지금)** | attack_punch ← hook_t2m_low · slam ← slam_t2m_b (hit 175 그대로) | `6e6927f7a5087777c5ba18caada12490a24332db201b7fcd81eea4613ed79a07` | 3,643,612 B |

- 대조(스크래치 GLTFDocument, 1차 → 2차): 메시 꼭짓점 21,979개 · 좌표 합 · 무게 합 같음(#891 주먹 그대로) · 안 바꾼 클립 여섯(attack · die · hit · idle · run · walk) 길이·트랙·키 해시 같음 · 바꾼 둘 = attack_punch 1.03 → 2.47초 · slam 5.93 → 3.47초.
- 글로 만든 두 클립은 트랙 21개(라이브러리 34~45) — 키 없는 뼈는 쉰 자세. 프로브에서 눈에 띄는 어긋남 없음.
- 게임 손질(GLB 안 건드림 — `data/models/dueoksini.tres`): 훅 창 0~1.1 → 1.0초 + 골반 붙들기 · 강타 창 0~2.6 → 2.4초 + 골반 붙들기 · 맞기 창 2.2~2.6 → 0.3초 — 값·근거 = 게임 `docs/design/monster_motion_v2.md §5.9`.

## Meshy 작업 id (지휘 채움, 10-24)
| 쓰임 | 생성 | 입히기(리그 01a0d3db-0600-73fe-a70b-ccc094013b72) | 크레딧 | 결과 |
|---|---|---|---|---|
| 훅 193 Left Hook from Guard | 창고 | 01a1695f-0b93-774b-9d7c-a818e90d6271 | 3 | 갈음됨(머리 높이) |
| 강타 86 Jump Attack | 창고 | 01a1695f-0ed6-71d1-b215-dcfbfd470fa3 | 3 | 갈음됨(PD 「새로 뽑자」) |
| 맞기 175 Face Punch Reaction 1 | 창고 | 01a1695f-1275-7616-8253-6d883a09ae9b | 3 | **채택** |
| 강타 A(두 주먹) | t2m prime 01a16976-24d9-7668-ae9a-86caed8c499d | 01a16976-8363-74b8-b14d-87b5a9322628 | 10+3 | 기각 |
| 강타 B(한 주먹 망치질) | t2m prime 01a16976-2b2f-7405-b39d-e49af459459a | 01a16976-87a8-756c-801e-fbb3f378615c | 10+3 | **채택** |
| 낮은 훅 | t2m prime 01a1699f-717a-7534-abd9-53c02dc97686 | 01a1699f-c7a9-72c4-9ea1-8c4bbd3b0e20 | 10+3 | **채택** |
합계 48크레딧(창고 9 + 글 동작 39).
