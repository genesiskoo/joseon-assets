# #703 P0 원장 — 헤드리스 기준선 v2 (G2 「전」, 검수 반영)

- 게임: claude/703-vfx-plan 「fix(#703): 검수 반영」 커밋 (#693 판 B 착륙 **전** 평타 박자) — v1(이 폴더의 60188b52 판)은 측정 오류로 버림
- 명령: `godot --headless --path . --fixed-fps 60 -- --e2e=_vfx_ledger [--vfx-fixed-seed]` → user://vfx_ledger_703.json·.md
- 무대: 흑랑 굴 1층(go_down 1)에서 사방 6u 트인 방 · 허수아비 산적(움직임 0) · 도호 → +x · 카메라 IsoCamera 직교 11 → 1유닛 = 65.45px(1280×720)
- 사양 = 게임 저장소 `docs/design/vfx_production_v3.md` §4.4·§6 P0·§7 · 요약 = `vfx_production_v3_log.md` §9·§10 · 측정 규칙 정본 = `tests/e2e/scenarios/_vfx_ledger.gd` 머리말

| 파일 | 내용 |
|---|---|
| `vfx_ledger_703_base.json` | 녹화 모드 끔 — 20항목 × 프레임별 표본(면적·폭·높이·노드별·입자·패스·빛)·피해 프레임 전부·효과음·재질 열쇠·데우기 열쇠·몸통(body)·방향(dir) |
| `vfx_ledger_703_base.md` | 표 셋(항목 · 몸통 BODY · 노드별 위 3) + 데우기 밖 열쇠 목록 |
| `vfx_ledger_703_base_lines.txt` | 출력 줄 `LEDGER\|` `BODY\|` `LEDGERG\|` `WARMCOV\|` + 자기 검사 3줄 원문 |
| `vfx_ledger_703_rec1.json` · `rec2.json` | `--vfx-fixed-seed` 두 번 |
| `rec_compare.txt` | rec1↔rec2: 20/20 항목 입자 씨앗 배정 34개 같음 · 최대 면적 차 0% · 프레임별 최대 차 0.08%(입자 넓이는 안 셈) |

## 읽는 법
- 프레임 = 게임 시계 × 60, 표본 = physics_frame(직전 틱에 그린 그림). 「다 보임」 = 최대 면적의 80% 이상 프레임 수 · 「95%」 = 처음 최대의 95%에 닿은 프레임.
- 피해 비교 = 그 프레임 앞의 가장 가까운 타(여러 번 때리는 항목). 노드 열쇠 끝 `#k` = 그 이름의 k번째 노드(겹친 사본을 합치지 않는다).
- 넓이: 시트 = get_item_rect 판 × 칸 평균 알파 × modulate(잉크 상자 = 폭·높이만) · 누운 판 = 내접 타원 · 메시 = 정점 실루엣 상자(봉투, 셰이더 침식·u 스크롤 못 봄) · 입자 = 넓이 없음(노드 수·amount만).
- 몸통(BODY) = 검광·범위 판·자국·핏방울·외곽선 사본을 뺀 넓이 위 둘 — 대본 `_body`.
- 재질 열쇠: `S:<파일>:<const>[render_mode]` = 문자열 셰이더 · `S:x.gdshader` · `M:std …` = StandardMaterial3D 기능 조합 · `P:ppm` = 입자 처리 재질.

## v1에서 바뀐 것 (검수 #703)
빌보드 시트 크기(Godot 4.7 빌보드 AABB = 정육면체 → 참격 폭 130 → 95) · 누운 판 AABB 꼭짓점 √2(회오리 462×267 → 327×189) · 넓이 정의(상자 × 평균 → 판 × 평균) · process_frame +1 치우침 · 두 동강 항목이 실제로 갈라짐 · 회오리 둘째 바퀴 사본 합산 · 몸통 규칙을 대본 안으로(옛 body_summary.txt 삭제).

## 한계
헤드리스 더미 렌더라 루마·실제 칠한 면적·GPU 시간·입자 그림은 없다 → P0-2b(창 모드 몸통 마스크) · P0-3(PSNR) · P0-4(GPU 기준선)는 다른 Godot 창 측정이 끝난 뒤.
