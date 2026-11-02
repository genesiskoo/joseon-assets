# 1109_act1_scroll — 1막 두루마리판 겹 (#1109 · D-121 갱신)

정본 = joseon 저장소 `docs/design/act1_scroll_2026-11-02.md` · 장면 = `tools/scroll_lab/act1_scroll.tscn` · 판 0 겹 = `../1099_story_scroll/`.
생성 = Codex CLI `gpt-5.6-sol` 내장 image_gen (2026-11-02, 장당 한 번 · 저장소 밖 스크래치) · 주간 창 2% 사용 → 98% 남음(리셋 11-09).

| 겹 | 파일 | 판정 |
|---|---|---|
| A1 쇠사슬 감긴 돌문 | A1_chain_seal | 2차 채택 — 1차(layers/A1_chain_seal_v1_rejected) = 서양 맹꽁이 자물쇠 · 사진 결이라 버림 → 「조선 가로 빗장 자물쇠 · 먹 붓질」로 다시 |
| A2 산군 범(앉음, 흐린 먹) | A2_sansin_tiger | 1차 |
| A3 들길 한 폭 | A3_road | 1차 (판 0 L01 을 결 참조) |
| A4 먼 고을 한 폭 | A4_far_village | 1차 (판 0 L01 결 참조) |
| A5 먼 고을 사람 여섯 | A5_far_people → pieces/_0~_5 | 1차 |
| A6 연기 여우 | A6_smoke_fox | 1차 |
| A7 연기 모양 셋(아낙 · 어미 · 말동무, 그림자만 여우) | A7_smoke_shapes → pieces/_0~_2 | 1차 |
| A8 연기 자취 | A8_smoke_trail | 1차 (가는 실연기 · 굵은 자취 둘 다 이것을 늘여 씀) |
| A9 마른 발자국 | A9_footprints | 1차 (발자국이 커서 340 폭으로 줄여 열 장 잇고 고개 오르막은 돌린 두 장) |

- `layers/` = 원본 · `clean/` = 흰 종이에 눌러 편 흑백(L) · `pieces/` = 묶음 겹 덩어리 · `layout.json` = 두루마리 좌표 4608×1024 자리 · 셰이더 칸 · 시간표(_cues).
- 다시 만들기 = `python -E -P build.py <스크래치 act1_A> <이 폴더>` (자리 수치는 build.py 안) · 생성 = `run.sh [겹…]` · 프롬프트 = `prompts/`.
- 녹화(작은 판 960×540 · 3.6MB) = `reports/1109/1109_act1_scroll_small.mp4` · 큰 판(1280×720 · 54MB)은 저장소 밖 `D:/joseon_archive/2026-11-03/1109/`.
