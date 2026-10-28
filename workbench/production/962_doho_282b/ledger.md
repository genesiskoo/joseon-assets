# #962 도호 새로 만들기 — Tripo 282b0028 몸 다시 굽기 (2026-10-28, PD ①)

- 카드: https://github.com/genesiskoo/joseon-hunters/issues/962 · **크레딧 0**(생성·리깅 없음 — 받아 둔 원본 다시 굽기)
- 바이블 칸 = 인물 · 서비스 = Tripo 웹(이미 만든 282b0028) · 반입 상한 삼각형 15,000 · 텍스처 1024 · 노멀 512 · `-Budget char`

## 재료 (src/)
- `hi_hanbok_run_test_1007.glb` = Tripo 282b0028 원본 내보내기(10-07 Downloads `hanbok_run_test.glb` — 리깅 78뼈 · 47,389 tri · 그림 4096). Tripo 상세 = Quad 27,327면 · P2.0 · 8K.
  같은 몸 확인: ④ 메시와 거리 중앙 0.04cm · 95% 0.14cm(rebake_body 출력).
- `direct_282b0028_8k.glb` = 10-28 PD 질문(「tripo모델 아니지?」) 뒤 Tripo 웹 282b0028 Animate 페이지에서 직접 내보냄(ego lite · GLB · 8k · 애니 0 · 크레딧 0). 위 10-07 파일과 대조: 삼각형 47,389 같음 · 고유 정점 24,597 같음(페이지 표시 Vertices 24597) · 0.01mm 반올림 위치 98% 일치(나머지 = 반올림 경계) · bbox 1e-7 · 색 그림 8192 vs 4096, 512로 줄여 평균 차 0.28/255 → **같은 모델, 그림 해상도만 다름**. 파일 안 메시 이름(86f9caea·0dea971a)은 내보낼 때마다 새로 붙는 번호라 작업 번호가 아님.
- `doho_t3.glb` = #681 ④(원본을 Tripo가 11,992 tri로 깎음 · 그림 2048 한 장 · 노멀 없음 · 클립 18).
- `game_doho_957.glb` = 게임 도호(#681 A안 + #879 + #957 가중치) — 옷 보조 뼈 5 · 클립 17.

## 만드는 법 (게임 저장소 tools/blender/)
1. `rebake_body.py --hi=src/hi… --rig=src/doho_t3.glb --cloth=src/game_doho_957.glb --out=try4/body.glb`
   - 원본 → collapse 11,999 tri(비율 0.253) · 새 UV(smart project 80°) · **색 = 원본 그림 베끼기**(텍셀마다 원본 표면 가장 가까운 점 → 원본 UV) · **노멀 = Cycles 굽기**(2048 → 512)
   - 가중치 = ④ 메시에서 가까운 면 보간 · 옷 보조 뼈 5 = 게임 뼈대의 부모 대비 자리 그대로 · 옷 무게 = 게임 몸 메시에서 가까운 면(정점 1,282)
2. `reskin_rig.py --map=identity --body=try4/body.glb --rig=src/game_doho_957.glb --out=try4/doho_b2.glb` — 게임 클립 17을 새 몸 관절 자리로(최대 13.9cm) · 땅 높이 클립별
3. 게임: `intake_model.ps1 -Src try4/doho_b2.glb -Id doho -Budget char` → `pose_edit`(doho_idle_posture_957.json) → `pack_clip` 대기 IP · `stop_clip`(R_Hand · R_Clavicle,R_Upperarm,R_Forearm · 0.5667 · 14) → `pack_clip` ×14

## 판(try*)
| 판 | 색 | 판정 |
|---|---|---|
| try1 | Cycles DIFFUSE · UV 66° | 버림 — UV 조각 많음 · 6% 어두움 |
| try2 | Cycles DIFFUSE · UV 80° | 버림 — 원본 대비 밝기 0.178/0.190(면적 기준) |
| try3 | Cycles 실수 버퍼 | 버림 — 같음(색 공간 탓 아님) |
| try4 | **베끼기** · UV 80° | 원본 대비 0.190/0.190 · 차 평균 0.014 — test_doho_moves 2 실패(대기 발 간격 1.70 · 시전 손 끌림 2.5cm) |
| try5 | try4 + 대기 계획 962(발 반폭 0.085) | 발 간격 1.24 통과 · 손 끌림 2.2cm(손목까지 y만 셈 — 틀림) |
| **try6** | try5 + 손목 너머 손 무게 줄임(거리 기준 1.0cm, 정점 251) | **채택 후보 = 게임 반입본** — test_doho_moves 61/61 · test_models PASS |

- 다시 굽기 한 판 = scratchpad `rebuild.sh <try>` 순서(위 「만드는 법」 1~3) · 약 3분.

- look_audit 밝기 0.144(WARN, 밴드 0.18~) — 이 도구는 3D 면적이 아니라 텍셀마다 같은 무게로 센다. Tripo 원래 펼침은 얼굴·피부에 텍셀을 많이 줘 0.219로 읽혔다. 표면 밝기는 원본과 같다.
- 결과: 11,999 tri · 정점 16,659 · 텍스처 1024 + 노멀 512 · 뼈 83 · 클립 17 · model_check PASS

## rig_stress (10-28, #957 착륙 뒤)
- `tools/blender/rig_stress.py` 지금(main d5acfb8f = A안 + 957 가중치) vs 새 몸 — 목 숙임·젖힘·돌림 · 팔 내림·들기·앞: 새 몸은 Tripo가 자기 몸에 준 가중치라 목 경첩·깃 박힘 없음 → 957 가중치 계획(doho_weights_957) 다시 안 씀. 사진 `stress/stress_now_vs_new.jpg`.

## 어깨 솟음 (10-28, PD 「어깨가 너무 올라갔는데 뭐가 문제냐」 → 「둘 다 해」)
- 원인 ① 동작: 대기·시전·막기 클립이 숨을 어깨로 쉬어 쇄골 +12~+32°(쉰 −10.6° · 걷기 −30°) — 어깨관절이 목밑 높이(−3~+2cm, 걷기 −10cm). pose_edit 팔 IK는 쇄골을 안 건드림 → Tripo 원래 대기 탓.
- 원인 ② 리깅: 쉰(바인드) 자세 = 팔 거의 수평 + 넓은 소매 → 팔을 내리면 소매 윗면이 위팔 따라 돌아 어깨 모서리가 각짐. 어깨 윗면 가중치 = x 8~12cm 쇄골 77% · 12~16cm 위팔 54%/쇄골 44% · 20cm~ 위팔 99%.
- 고침 ① = `pose_edit` 새 op `shoulder`(elev −18 · w 0.85) → 대기 IP 쇄골 −13.6~−10.8° · 어깨관절 목밑 −5.5cm · 숨 폭 18° → 3° · 게임 반입(대기 IP + 멈춤 14) · test_doho_moves 61/61 · test_models PASS.
- 시험 ② = `tools/blender/rebind_apose.py --deg=40 --smooth=0 --lap=0.6 --lap_it=8 --wsmooth=14 --radius=0.18 --neck=0.08` → `shrug/` (미반입, PD 판정 대기)
  - 같은 가중치로 다시 붙이기만(--smooth 0.5) = 거의 같음(클립이 세계 자세를 지키므로) · 클립 17 뼈 자리 대조 0.00cm
  - 바뀌는 몫 = 굳힌 A포즈에서 어깨 둘레 자리·가중치 문지르기(덩이 단위 — 정점 단위는 UV 솔기에서 찢어짐, 깃·목 ±8cm 빼야 흰 깃이 안 뭉개짐) → 어깨 모서리가 둥글어짐 · 공격·회오리·도약·시전·달리기·막기 깨짐 없음
- 사진·영상: 게임 `docs/art/962_doho_282b/shoulder_*.jpg` · `reports/962/shoulder_idle_3way.mp4` · `shoulder_rebind_clips.jpg`
