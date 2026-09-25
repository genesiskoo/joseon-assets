# 못골 건축·우물 제작 원본

기존 #316(집)·#317(우물)의 미추적 제작 파일을 #129에서 보존했다. 새 모델 생성이나 승인 변경은 없다. 제작 승인·Meshy 7 작업 ID·선택 원화는 `manifest.json`을 참조한다.

| 모델 | 선택 원화 | 원본 | 게임 반입 원천 | 게임 연결 | 삼각형·텍스처 |
|---|---|---|---|---|---|
| 초가 | `concept/choga_b.png` | `glb/choga.glb` | `glb_graded/choga.glb` | `joseon/assets/models/buildings/choga.glb` | 14,808 · 1024² |
| 기와집 | `concept/giwa_a.png` | `glb/giwa.glb` | `glb_graded/giwa.glb` | `joseon/assets/models/buildings/giwa.glb` | 18,469 · 1024² |
| 우물 | `concept/well_a.png` | `glb/well.glb` | `glb_graded/well.glb` | `joseon/assets/models/buildings/well.glb` | #317 기록 참조 |

`glb/`는 Meshy 원본, `glb_1024/`는 텍스처만 축소한 중간본, `glb_graded/`는 채도·밝기를 H1 마을 범위에 맞춘 반입본이다. `prep.ps1`·`grade_intake.ps1`은 당시 사용한 명령 기록이며, 내부의 과거 Claude 작업 트리 절대 경로는 재실행 전에 현재 작업 트리로 바꿔야 한다. 게임의 두 집 GLB는 반입본과 SHA-256이 각각 완전히 같다.

게임 쪽 배치·카메라 검수 및 해시 전문: `joseon/docs/design/hanok_asset_audit_129.md`. 현재 한옥은 한 메시로 구워진 전체 집 2종이므로 지붕·벽·문·담을 서로 갈아 끼우는 독립 GLB 모듈이라고 부르지 않는다. 재사용 단위는 `Hanok` 씬 계약(초가/기와집 선택, 배율, 벽 충돌, 처마 가림)과 별도 담·소품이다.
