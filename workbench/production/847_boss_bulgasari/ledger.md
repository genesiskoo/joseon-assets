# 847 불가살이 동작 점검 장부 (/motion-pass)

- 카드: https://github.com/genesiskoo/joseon-hunters/issues/847 · 스킬 정본 = 게임 저장소 `docs/design/motion_pass.md`
- 서비스·크레딧: 없음(기존 GLB 가중치만 다시 칠함 — `tools/quad_rig.py reweight`)
- 원본 = `boss_bulgasari_before.glb` (sha256 56e28dac…4a46 · 게임 main `assets/models/boss_bulgasari/boss_bulgasari.glb`와 같음)

## 문제
달리기 배 한 변 13.8cm(모델 단위, × scale 2.86 = 화면 ≈39cm). 배 밑 정점이 몸통 0.36 + 앞왼다리 위 0.27 · 아래 0.19 + 앞오른다리 위 0.18처럼 다리 무게를 크게 쥐고, 이웃 정점은 뒷다리·앞다리를 같이 쥔다 → 걸음이 다리 뿌리 뼈(_Up)를 최대 9.5cm 밀 때 변 양 끝이 갈라진다.

## 되풀이 (자 = `quad_rig.py stretch`, 모델 cm · 가장 큰 클립)
| 회 | 처방 | 달리기 | 비고 |
|---|---|---|---|
| 0 | 같은 인자로 다시 칠함 | 13.8 | 원본 재현(기준 확인) |
| 1 | 다른 다리·꼬리 무게 → 몸통 뼈 | 15.4 | 꼬리↔뒷다리 경계가 새로 찢김 · 버리기 판 24.3 |
| 2 | 다리끼리만 → 몸통 | 13.3 | 섞임 셈(≥0.25)에 안 잡히는 작은 다리 무게가 원인 |
| 3 | 배(몸통 주인) 정점의 다리 무게를 smoothstep으로 몸통에 | 13.2 | 최악 정점은 다리 합 0.64라 그대로 남음 |
| 4 | 몸통 굵기 body_reach 2.2 · 2.6 · 3.0 | 9.5 · 8.8 · 9.2 | |
| 5 | 2.6 + 3회 넘기기 · **2.4** | 10.8 · **8.6** | **채택 후보 = 2.4** |

## 채택 후보 `boss_bulgasari_reach24.glb` (sha256 f7d1d43f…0169)
`python tools/quad_rig.py reweight --glb <before> --out <after> --body-reach 2.4` (나머지 기본: paw-frac 0.05 · cluster · limb · smooth 8)
| 클립 | 전 | 후 |
|---|---|---|
| idle | 1.6 | 1.4 |
| walk | 10.2 | 7.8 |
| run | 13.8 | 8.6 |
| attack | 4.0 | 3.4 |
| hit | 4.4 | 3.2 |
| pounce | 8.3 | 4.9 |
| pounce_air | 9.5 | 5.4 |
| pounce_land | 11.5 | 5.3 |
| die | 10.1 | 6.3 |
섞임 정점 49 → 20. Blender `mesh_audit` 자와 2% 안에서 같음(달리기 13.56 vs 13.8 — 자 보정).

## 남은 층
L3 그림(다리 윗살이 몸통에 끌려 다리가 덜 움직여 보이나) · L4 게임 안 · L5 PD
