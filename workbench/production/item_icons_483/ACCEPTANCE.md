# #483 PD 채택 기록 (2026-09-28)

PD의 「승인 나머지 작업 리스트업」에 따라 흑랑 송곳니·장산범의 눈(v2)·여우구슬 세 후보를 모두 채택했다. 원화 후보 커밋은 `36832dd`, 게임 사양·검토판은 `4dd017e6`이다. 실제 게임 연결과 전용 유니크 그림 선택 경로는 #484에서 #481 반입 뒤 진행한다.

| 이름 | 채택 파일 | SHA-256 |
|---|---|---|
| 흑랑 송곳니 | `game/items/u_heukrang_fang.png` | `c54e5ab91d0549e079c313828c51c1e397637345c0877a8dca3bd32fa5aa7928` |
| 장산범의 눈 v2 | `game/items/u_jangsanbeom_eye.png` | `670987907a4cb1ac1713c23d47fe813a4607c982d29f88e379fa3a8539c2f1d8` |
| 여우구슬 | `game/items/u_fox_bead.png` | `21b9148faa1a80a2d9b829b6ccc77f0fba78dedb08f89750bc461cfbe93cb940` |

내장 imagegen의 native 원화3+눈빛 편집1, 정확한 프롬프트, 원본/패킹/렌더/raw 해시는 generation_sources.json·PROMPTS.md·manifest.json·verification.json에 보존했다. 장산범의 눈 v1 원화/프롬프트/패킹/검수는 source/items/u_jangsanbeom_eye.png·variants/v1/에 남기고 최종 후보는 v2다. 실제 UiSkin4모드/오류0, 기존PNG42·런타임135파일 내용 동일을 검수했다. 이 기록은 원화 채택이며 게임 반입 완료를 뜻하지 않는다.

#274 최초 핵심73 중 승인핵심34 = 잔여39. 신규베이스9·상위물약4·부첩0·호리병1·대표유니크5·오방옥20이며 실제정의8/설계만31이다. 추가 승인6과 퀘스트 봉인3은 원핵심 밖으로 별도 집계한다. 후속 폴리싱 때 좋은 장비·고효능 물약의 재질/마감/실루엣을 더 좋게 보이도록 한다는 기조를 유지하며 기존 그림을 지금 수정하지 않는다.
