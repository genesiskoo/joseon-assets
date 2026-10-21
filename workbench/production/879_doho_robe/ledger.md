# 879 도호 도포 자락 동작 점검 장부 (/motion-pass, 화면 픽셀 기준)
- 카드: https://github.com/genesiskoo/joseon-hunters/issues/879 · 크레딧 0 · 가중치만 손질(뼈·동작·텍스처 그대로)
- 원본 `doho_before.glb`(sha256 36c5e119…) · 채택 `doho_sash_gat_sleeve.glb`(sha256 709f2517…) = `joint_band.py --pairs "" --smooth SashTail+Hem_L+Hem_R,mixamorig_LeftForeArm+Sleeve_L,mixamorig_RightForeArm+Sleeve_R --smooth-n 8 --below mixamorig_Head:mixamorig_Spine2:mixamorig_Neck:0:0.25`
- 자 = 게임 안(`tools/skin_stretch_probe.gd`, 옷 물리 켬) — 파일 자(Blender)는 스프링이 꼬리를 흔든 몫을 못 본다(공격 28.7 vs 게임 47.9cm)
- 되풀이 5회: 허리끈↔자락 펴기 8 → 20(나빠짐, 8로) → 갓끈 머리 무게를 목 아래로 → 경사 0.05:0.15(같음) → 양 소매 펴기
- 게임 안 화면 px 전→후: 참격 32.6→14.8 · 공격 31.4→15.2 · 찌르기 36.2→18.9 · 회오리 33.4→18.2 · 돌려차기 34.1→15.5 · 달리기 21.7→10.3 · 대기 7.6 그대로
- L2: robe_probe 같음(회오리 퍼짐 +3.0% FAIL = 원래부터) · 대기 떨림 2.06→3.67mm(판정선 안) · 단위·e2e 7종 PASS
- L3: 두 판독 PASS · 막는 것 0 · 찌르기 후가 조금 더 깔끔 · 띠는 옷 물리 끔 그림이라 L4 영상으로 보탬
