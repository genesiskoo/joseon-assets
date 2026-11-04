# #1155 종이 병사 (paper_soldier) — 장부

> 정본 사양 = joseon `docs/design/doho_skills_v3_2026-11-03.md` §6 · §12 A1 · 바이블 `modeling_bible.md` · 순서 `/monster-make`(`monster_pipeline.md`).
> 지금 게임 = #1150 대역(도호 GLB + 한지 셰이더 `actors/shaders/paper_body.gdshader`) → 이 몸이 오면 `actors/ally.gd` SOLDIER 몸만 바꾼다.

## 기획서 (§5.1)

| 칸 | 내용 |
|---|---|
| 이름 · id | 종이 병사 · `paper_soldier` (아군 소환체 — EnemyDef 아님, ModelDef만) |
| 부류 · 쪽 | 도호 편 술법 몸(종이) — 적·역병과 색이 겹치지 않게 |
| 몸 형태 | 사람형 → Tripo Humanoid · Mixamo 65 |
| 동작 | 대기 · 달리기 · 벰(평타 1~2) · 맞음 · 쓰러짐(종이로 흩어짐은 이펙트) · 시전 등장(선택) |
| 이펙트 큐 | 서기(먹 연기 + 도장 물결 — #1150 그대로) · 쓰러짐 종이 흩날림 · 종이 숙련 5점 터짐 |
| 소리 | #1150 그대로(talisman_throw) · 새 소리는 따로 |
| 바이블 칸 · 면 수 | 인물·사람형 = Tripo · Polycount 12,000 · 반입 8,000~15,000 · 텍스처 1024 |
| 칼 | 따로(weapon_socket) — A포즈엔 빼고 |
| 예산 | PD — 가안 Tripo 120(3D 40 + 리깅 20 + 여유 1회 60) · Codex 원화 ≤ 12장 |

### 외형 3안 (narrative-world 초안 · 11-04)
- **A 오려 세운 종이 인형** — 납작한 두 장 판 · 키 1.45 · 점 눈 · 오린 칼 · 위험 = 시키가미(왜색)와 가장 가까움 · 신장으로 잇기 약함.
- **B 지갑(紙甲) 군졸** (추천) — 넓은 전립 + 각진 어깨 판 + 접힌 종이 갑옷 · 키 1.55 · 먹으로 그린 무표정 눈매 · 먹칠 종이 환도 · 쓰러지면 접힌 판이 펼쳐지며 터짐(숙련 터짐과 맞음) · 신장 = 같은 갑옷을 키운 지갑 장군 · 87px 실루엣이 도호(좁은 흑립·긴 도포)와 갈림.
- **C 종이죽 꼭두 졸개** — 3등신 · 키 1.30 · 장승풍 큰 눈 · 둥근 방패 · 비율이 달라 도호 동작 옮기기 어긋남.

### 피할 것
무속 공포(D-012) · 웃기는 얼굴 · 왜색(시키가미·에보시·사무라이 갑옷) · 실명·상표·실제 부적 글귀 · 적 색(검푸른·회녹·병든 보라) · 도호와 같음(남색·흑립·붉은 띠·푸른 패) · 금속 광택 · 금빛(구미호와 겹침).

## 생성 기록

| 날짜 | 물건 | 서비스 | 작업 · 파일 | 설정 | 결과 | 판정 | 차감 |
|---|---|---|---|---|---|---|---|
| 11-04 | 원화 시안 A1·A2 | Codex gpt-5.6-sol image_gen | art/paper_soldier_A1.png(701a2920…) · A2(d000b6d0…) | 참조 H1 보드(화풍만) | 한지 바지저고리 · 점 눈 · 조선 윤곽 또렷 · A2 칼 코등이 왜색 | 대기 ① | 구독(주간 30→35%) |
| 11-04 | 원화 시안 B1·B2 | Codex | art/paper_soldier_B1.png(b8810d07…) · B2(c2dc2c46…) | 같음 | 종이 갑옷 실루엣 강함 · 사람 얼굴 · 원뿔 모자(중국풍) · 겹 치마 | 대기 ① | 〃 |
| 11-04 | 원화 시안 C1·C2 | Codex | art/paper_soldier_C1.png(5cc42c93…) · C2(95df5b43…) | 같음 | 3등신 종이죽 · 귀여움 · 비율 다름 | 대기 ① | 〃 |

| 11-04 | 다듬기 R1·R2 | Codex | art/paper_soldier_R1.png(f75fd8bf…) · R2(f0dfdbb4…) | 참조 A1 | 종이 가슴 갑옷 · 작은 전립 · 곧은 환도 | **R1 고름**(PD 「A1 추천대로」 · 갈매기 접힘) | 구독 |
| 11-04 | A포즈 P1·P2 | Codex | art/paper_soldier_P1.png(e203751d…) · P2(1c2632dc…) | 참조 R1 · §5.3 문장 | 독립 판독 ✗ 4번(통 넓은 바지 → 다리 붙음) · P1 손가락 붙음 | 버림 | 구독 |
| 11-04 | A포즈 Q1·Q2 | Codex | art/paper_soldier_Q1.png(2c095a3d…) · Q2(5216104e…) | 참조 P2 + 바지 좁게 · 행전 납작 · 다리 틈 | Q2 = 9칸 통과 · Q1 = ✗ 4번(앞자락이 허벅지 덮음) | **Q2 = 3D 입력** | 구독(주간 남음 64%) |

| 11-04 | 3D 몸 | Tripo 웹 HD Model(한 장) | 작업 `5831ed56-6fd2-4572-b2d0-7f79bdc7d6ee` · 입력 Q2 | H3.1 · Triangle · 12,000 · Ultra · 2K · 조명 지우기 · PBR 끔 · Private (PD 11-04 「승인, 네가 눌러」 · 상한 120) | Triangle · Faces 11,600 · Vertices 7,478 · 손가락·다리 갈라짐 · 옆 = 앞자락 접힘 조각 하나(허벅지 앞) · 렌더 art/tripo_front.png · tripo_side.png | **버림**(PD 「바지가 왜저러냐」 — Q2에서 바지를 좁히라 해 바지저고리가 쫄바지 + 날카로운 접힘 조각이 됨) | 40 · 잔액 2,120 → 2,080 |
| 11-04 | A포즈 S1·S2 | Codex | art/paper_soldier_S1.png(0f9788b2…) · S2(598dc7b4…) | 참조 P2 · 바지 = 넉넉하게 곧게 떨어짐 · 다리 사이 넓게 · 행전 납작 | 독립 판독 S2 9칸 통과 · S1 ✗ 4번(사타구니~무릎 붙음) | **S2 = 3D 입력 v2** | 구독 |
| 11-04 | 3D 몸 v2 | Tripo 웹 HD Model(한 장) | 작업 `73b44b69-178f-450b-bfb2-199f76be563e` · 입력 S2 | 같은 설정(다시 확인) · PD 「추천대로 다시뽑아」 | Triangle · Faces 11,621 · Vertices 8,255 · 넉넉한 바지저고리 · 두 다리 갈라짐 · 날카로운 조각 없음 · art/tripo_v2_front·side.png · 비교 tripo_v1_v2.jpg | 멈춤 ③ 대기(리깅 전) | 40 · 잔액 2,080 → 2,040 |

| 11-04 | 리깅 | Tripo 웹 Rig · Humanoid · Mixamo | 같은 작업 73b44b69 · 「Not Ready for Auto-Rigging」 경고(통 넓은 바지) → Try Rigging Anyway | — | 뼈 55 · 4영향 · 다리 가중치 바지 다리마다 따로(rig_inspect) · GLB glb/paper_soldier_tripo_rig.glb(968d58ee…) | 채택 | 20 · 잔액 2,040 → 2,020 (누계 100/120) |
| 11-04 | 뼈대 굽기 · 동작 · 반입 | Blender flatten(부모 빈 노드 90° → 굽기) · retarget_mixamo(산적 5 + 도호 벰 3) · albedo_ops 1024·무광 · intake_model -Height 1.45 | glb/paper_soldier_rig_flat.glb → paper_soldier_anim.glb → paper_soldier_intake.glb → joseon assets/models/paper_soldier/ | scale 1.482 | 클립 8 · look_audit 밝기 0.66·채도 0.48 밴드 밖(한지 바탕 — 경고만) | 반입 | 0 |

- **착륙 11-04** = joseon main 364143500 (#1150과 함께, PD 「합쳐」 · 커밋 62843c7e) · 영상 reports/1150/ · 후속 = 손가락 주먹 · 한지 색(굴에서 살색) · 신장 몸 · 자료관 등록(D-109)은 지휘.
- 멈춤 ② = 같은 판정판 v2 · Tripo 입력 사본 = joseon `.claude/worktrees/1150-ally-ai/tmp/1155/paper_soldier_apose.png`(Chrome 올리기용, git 밖).
- 판정판 ① = https://claude.ai/artifact/BDf8xYQ6L3oBkVZZYvQP4v · 비교 = art/compare_ABC.jpg · 추천 = A1 바탕 + 종이 가슴 갑옷 · 작은 종이 전립 · 곧은 환도(코등이 없음) 다듬기.
- 자료관(D-109): 고른 안이 정해지면 같은 카드에서 등록(시안 6 unreviewed + 고른 것 승인).
