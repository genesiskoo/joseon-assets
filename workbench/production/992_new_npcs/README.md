# #992 새 NPC 둘 — 고아 여자아이 · 젊은 남자 (D-120)

외형 규칙 = 게임 저장소 `docs/design/new_npc_looks_992.md`(브랜치 `claude/992-npc-art`) · 이야기 정본 = `docs/design/story_depth_2026-10-29.md` §4 · §5. 이름은 #989가 정한다(임시 id `orphan_girl` · `smitten_youth`).

## 원화 시안 (2026-10-29 · PD 판정 대기)

도구 = Codex CLI `exec` · `gpt-5.6-sol` · 내장 image_gen(모델 버전 미노출). 참조 = H1 시트(왼쪽 인물 화풍만) · 주모 b4 원화 · 억쇠 B 원화(마을 NPC 결). 어린 판(c·d)은 처음 판(a·b)을 둘째 참조로 넣고 나이만 낮췄다. 프롬프트 = `concept/<이름>.prompt.txt`.

| 파일 | 무엇 | SHA-256 |
|---|---|---|
| `concept/child_a.png` | 아이 A — 댕기 머리끝 · 흙빛 저고리 · 쪽빛 치마 (**열서너 살로 보여 나이 기각 → c**) | `1ab84fa8f00df9a2c8cb3ff2b2232ab1268b49810ac538e90371f80129e439de` |
| `concept/child_b.png` | 아이 B — 댕기 손목 · 쪽빛 저고리(주모 닮음) · 갈색 치마 (**나이 기각 → d**) | `e3e9dc4b6ea5f8254eb6e57c4be983c42a081d8edb6637b9e0c560ec81cac786` |
| `concept/child_c.png` | 아이 C = A 어린 판 (후보) | `aec3fff195e3fe81933c915a7631c2affc8680efd881375ee6b6c97b7b3c4f6a` |
| `concept/child_d.png` | 아이 D = B 어린 판 (후보) | `c6a4ea5fec51ac472d6e115fc1a18251218f04db06f19bcb8676a7fd1c7eafe9` |
| `concept/youth_a.png` | 젊은 남자 A — 총각 땋은 머리 · 옥색 쾌자 · 은비녀 선물 (**PD 10-29 기각 「너무 미소년」**) | `544bbbae9386289599b674bffdf49c6228cf2f0af773d3cbf9f7dfe19ee580f6` |
| `concept/youth_b.png` | 젊은 남자 B — 상투·망건(어른 흉내) · 긴 옥색 두루마기 · 은비녀 + 동백 (**PD 10-29 기각 「너무 미소년」**) | `3002ffce47fdda4969e05288ca404a17f1e6bdac4acb263c1865b20bee41108c` |
| `concept/youth_c.png` | 젊은 남자 C = B 차림 · 평범하고 얼빠진 얼굴 · 안 맞는 두루마기 (후보) | `72a5619a01a3049bc6171f15288c87b6ea3981810fc2472d329b2775c88a6a3b` |
| `concept/youth_d.png` | 젊은 남자 D = A 차림 · 평범하고 얼빠진 얼굴 · 배가 끼는 쾌자 (후보) | `d9be11d73e0815c66d41104a19dbd6cc39035638fd792690eb4fb4a127ef6ce4` |

PD 10-29 「남자가 너무 미소년임. 평범하고 살짝얼빠지게 나와야됨.(구미호한테 홀리는 캐릭터니까. 캐릭터 설명 잘 읽고 만들어)」 → c·d는 억쇠 원화를 얼굴 결 참조로, 기각된 a·b를 「이렇게 하지 말 것」 참조로 넣었다.

같은 얼굴 표지(아이): 가운데 가르마 한 갈래 땋은 머리 · 왼쪽 눈 밑 점 · 어미의 붉은 댕기 — 감염된 모습(#993)이 이어받는다.

## 다음 (채택 뒤)

정면 A포즈 원화(modeling_bible §4.3) → 대화 정지 초상 neutral + 표정 하나 → Tripo 웹 3D(인물 칸 Polycount 12,000 · 60크레딧/인물 · PD 예산 뒤) · 장부 = `ledger.md`.
