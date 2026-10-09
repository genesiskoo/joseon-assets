# #703 P0 원장 — 헤드리스 기준선 (G2 「전」)

- 게임 커밋: `7a4dbe54` (claude/703-vfx-plan, main a56e1b8d 위 — #693 판 B 착륙 **전** 평타 박자)
- 명령: `godot --headless --path . --fixed-fps 60 -- --e2e=_vfx_ledger [--vfx-fixed-seed]` → user://vfx_ledger_703.json·.md
- 무대: 흑랑 굴 1층(go_down 1)에서 사방 6u 트인 방 · 허수아비 산적(움직임 0) · 카메라 IsoCamera 직교 11 → 1유닛 = 65.45px(1280×720)
- 사양 = 게임 저장소 `docs/design/vfx_production_v3.md` §4.4·§6 P0·§7 · 요약 = `vfx_production_v3_log.md` §9·§10

| 파일 | 내용 |
|---|---|
| `vfx_ledger_703_base.json` | 녹화 모드 끔 — 20항목 × 프레임별 표본(면적·폭·높이·무리별·입자·패스·빛)·효과음·재질 열쇠·데우기 열쇠 |
| `vfx_ledger_703_base.md` | 위의 표 두 개(항목 · 무리별 위 3) + 데우기 밖 열쇠 목록 |
| `vfx_ledger_703_base_lines.txt` | 출력 줄 `LEDGER\|` `LEDGERG\|` `WARMCOV\|` 원문 |
| `body_summary.txt` | 항목마다 몸통 무리 둘(검광 봉투·범위 판·자국 뺌) — 폭×높이 · 첫/절정 · 절정−피해 · 다 보임 |
| `vfx_ledger_703_rec1.json` · `rec2.json` | `--vfx-fixed-seed` 두 번 — 20/20 항목 입자 씨앗 53개 같음, 면적 차 ≤0.3% |

## 읽는 법
- 프레임 = 게임 시계 × 60 (히트스톱 동안은 같은 번호). 「다 보임」 = 그 항목(또는 무리) 최대 면적의 80% 이상인 프레임 수.
- 면적 = 노드 화면 사각형 × 무게. 시트(AnimatedSprite3D)는 그 칸 원본 PNG의 평균 알파와 알파 > 0.08 상자로 잰다 = 실제 잉크.
  메시는 AABB 봉투(셰이더 안 침식·u 스크롤은 못 봄) — 검광(SwordTrail)·범위 판(Vfx_skill_area)·부적 진 판이 봉투로 크게 잡힌다.
- 입자(GPUParticles3D)는 넓이 없음 — 방출 중 노드 수·amount만.
- 재질 열쇠: `S:<파일>:<const>[render_mode]` = 문자열 셰이더 · `S:x.gdshader` · `M:std …` = StandardMaterial3D 기능 조합 · `P:ppm` = 입자 처리 재질.

## 한계
헤드리스 더미 렌더라 루마·실제 칠한 면적·GPU 시간은 없다 → P0-2b(창 모드 몸통 마스크) · P0-4(GPU 기준선)는 다른 Godot 창 측정이 끝난 뒤.
