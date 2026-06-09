# _asset_review — 게임(godot) 미사용 자산 격리 (PD 직접 검수·폐기용)

생성: 2026-06-10 · HQ 정리팀
지시: PD "godot이 사용하는 asset은 두고 나머지는 한군데로 옮겨놔 내가 보고 직접 폐기".

## 판정 기준
- 코드(.gd)/씬(.tscn)/리소스(.tres)/project.godot에서 res:// 참조 0 = "게임 미사용".
- 게임이 직접·동적으로 쓰는 sprites/·audio/·cutscenes/·themes/ 는 손대지 않음(원위치 보존).
- godot은 이 폴더를 .gdignore 로 무시 → 빌드 영향 0. import 검증 통과 확인됨(게임 안 깨짐).

## 되돌리기(보존 결정 시)
- 살릴 것은 원위치로 mv 하면 됨(아래 "← 출처" 참조). 아직 git 커밋 안 함 = 복구 자유.

────────────────────────────────────────────────────────
## 격리 내용 · 출처 · 권고

### illustrations/   ← assets/illustrations/   (36M)  ※AI 재생성 비용 큼
  concept/doho_v4/   도호 화풍 컨셉아트 (24M). 화풍 기준점·D-018 마케팅 자산.
  npc/halmae/        무당할매 일러 (13M). 게임 DialogueUI는 sprites rotations만 쓰고
                     일러(portrait/nobg/bg/effect)는 아직 화면에 연결 안 됨.
  → [권고] 보존 신중. GPT Image 2 재생성 비용 크다. 폐기 전 화풍 락 여부 확인.

### image/   ← assets/image/   (4M)  AI 입력용 레퍼런스(게임 자산 아님)
  cref1.png / cref2.png / cref3.png   캐릭터 레퍼런스 (cref1=도호 cref2=귀새 cref3=청연, D-025)
  cref1_gpt_ref*.png                  도호 GPT 톤 레퍼런스
  → [권고] 위 cref·gpt_ref = Pixellab/GPT 재발주 입력. 보존 권장.
  moba1.png / moba2.png / moba3.png   외부 MOBA 시각 참고. 문서·코드 참조 0.
  06-inv / 07-dialog / 07-tooltip / 10-choices / 11-cooldown / debug5 / inv-redesign .png
                                      UI 스크린샷·목업.
  → [권고] moba*·UI 스크린샷 = 폐기 후보.

### map2_samples/   ← assets/sprites/env/map2_samples/   (64K)
  옛 박스맵 타일 샘플(dirt_grass·dirt_path·grass_clean·grass_dense).
  현행 타일셋 = joseon_village(Map.gd 사용). 완전 고아.
  → [권고] 폐기.

### tilesets/   ← assets/tilesets/joseon_village_v2/   (28K)
  joseon_village_v2 타일셋(tileset.png + metadata.json). 코드 참조 0.
  현행은 assets/sprites/env/tileset/joseon_village.tres.
  → [권고] 폐기(중복/고아 의심). 단 'v2'라 더 최신 실험본일 가능성 — 아트팀 확인 권장.

────────────────────────────────────────────────────────
## 한눈에
  폐기 권장 : map2_samples · tilesets · image/moba* · image/UI스크린샷
  보존 권장 : illustrations(doho_v4·halmae 일러) · image/cref*·gpt_ref  (AI 재생성 비용)
