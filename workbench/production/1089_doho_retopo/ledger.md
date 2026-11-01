# #1089 도호 사각형 리토폴로지 시험 — 장부

- 카드: https://github.com/genesiskoo/joseon-hunters/issues/1089 (PD 2026-11-01)
- 바이블 칸 = 인물 · 서비스 = 생성 없음(Blender 5.2 헤드리스 · QuadriFlow) · 크레딧 0 · 반입 삼각형 상한 8,000~15,000
- 원본 = joseon `assets/models/doho/doho.glb` (삼각형 11,999 · 사각형 0 · 뼈 83 · 클립 17)
- 도구 = joseon `tools/blender/retopo_quad.py` → `tools/glb_swap_mesh.py`(동작 바이트는 원본 그대로) · 시험 = `tools/blender/topo_compare.py`

| 판 | QuadriFlow 목표 | 결과 | 삼각형(내보냄) | 사각형 비율 | 메모 |
|---|---:|---:|---:|---:|---|
| v1 | 5,000 | 4,513 | 9,210 | 93% | 얼굴·갓끈·자락 뭉개짐, 굽기 광선 0.06 = 흰 줄 |
| v2 | 7,000 | 5,313 | 10,776 | 94% | + 원본 표면 붙이기 · 광선 0.025 |
| v3 | 9,300 | 8,566 | 17,369 | 95% | 예산 넘음 |
| **v4 → v4s** | 7,800 | 6,858 | **13,946** | **94%** | 예산 안 · 관절 루프 3줄 × 13관절 · 시험 대상 |
| v5 | 7,800 | = v4 | 13,946 | 94% | 굽기 시작점 2.5cm 바깥 — 흰 얼룩 그대로(틈 막힘이 원인) |

- `doho_retopo_v4s.glb` = 원본 GLB에 v4 몸 메시·그림 3장만 바꿔 끼운 것(반입 후보 아님 — PD 판정 전) · 2,469,720 바이트
- `retopo_report_v4.json` = 면·관절별 루프 변 수 · `deform_metrics_v4.json` = 굽힘 자세 눈금(원본 vs v4)
- 영상 = `reports/1089/` (왼 원본 · 오른 v4s, 게임 카메라)
