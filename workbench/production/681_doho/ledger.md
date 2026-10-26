# #681 도호 몸 A — 지금 몸 + ④ Tripo 뼈대·동작 (2026-10-26)

- doho_a1.glb = `tools/blender/reskin_rig.py --body=<게임 assets/models/doho/doho.glb> --rig=workbench/production/doho_t_681/doho_t3.glb`
  - 몸(메시 11,999 tri · 텍스처 1024 + 노멀 256 + 거칠기 1024 · 가중치 · 옷 보조 뼈 Hem_L/R·Sleeve_L/R·SashTail) = 지금 도호
  - 뼈대 83(Tripo 78 + 보조 5) · 클립 18 = ④(Tripo 282b0028 → doho_t3) · 관절 23개를 지금 몸 자리로(최대 13.9cm, 뼈 방향·롤 그대로)
- doho_a2.glb (10-26, PD 「0:05 살짝 밀리는 느낌」) = a1 + 땅 높이 맞춤 — 다리가 지금 몸 길이로 바뀌어 달리기 발끝이 바닥 밑 3.7cm로 묻혔다 →
  run +3.7 · walk +1.7 · idle·idle_out +0.4cm(골반 위치 트랙, 발 관절 최저 = 쉰 자세 높이). 공격·스킬·죽기는 안 건드림(guard −19.7 · whirl −17.3 등 따로 볼 것)
- doho_a3.glb (10-26, PD 「안고쳐짐 뚝뚝끊겨」) = a2 + Blender 장면 60fps(24면 달리기 39키 → 16키·길이 +5%) + 클립 0초 시작(export_anim_slide_to_zero — 한 칸 늦게 시작해 루프마다 멈춤).
  ModelDef(실험장 판 L·M): loop_end run 0.5667 · walk 1.1 — Tripo 달리기 끝 4키가 늦춰 닫혀(움직임 38→23→11→2°) 루프마다 멈칫, #696과 같은 원인.
  멈칫 묶음(꾸준히 달리기, 몸 자세 변화가 한가운데 35% 밑): 지금 0 · ④ 원본 7 · A 자르기 전 7 · A 자른 뒤 0
- a4 (10-26) = 땅 높이 기준을 「몸 GLB 같은 이름 클립」으로(공격·스킬 2~5cm · 죽음 8.8cm 묻힘 고침).
- **a7 = 게임 반입본** (10-26, PD 「A안 확정」) = a4 + 늘 1인 크기 채널 지움(GLB 후처리 — 시전 손 소품 50배 문제) + 몸에 없는 클립(kick) 버림.
  게임 assets/models/doho/doho.glb (작업 트리 681-doho-run2, 미착륙). 대기 IP·멈춤 14는 게임 저장소 쪽에서 pose_edit·stop_clip·pack_clip.
  다시 굽기 순서 = 게임 저장소 커밋 f1019d97 설명 · a1~a6은 중간본(지워도 됨, git 미추적).
- 크레딧 0 (생성·리깅 없음 — 기존 모델 재조립)
- 왜: PD 10-26 ④ 동작 채택 → 「모델링 디테일은 기존이 더 좋았는데」 원인 = ④ 메시·텍스처 품질 → A안(PD 「보여줘」)
