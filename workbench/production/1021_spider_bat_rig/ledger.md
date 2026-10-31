# #1021 거미·박쥐 리그 장부

- 서비스 = 없음(생성·다시 뽑기 안 함) · 크레딧 0 · 지금 게임 메시에 뼈·클립만 구웠다.
- `spider_static.glb` = 리그 전 묵은거미(spider·왕거미 공유) 정지 메시 · `bat_static.glb` = 리그 전 박쥐(bat·굴 박쥐·흡혈 박쥐 공유) 정지 메시 — 다시 구울 때 입력.
- 거미 = `python tools/arachnid_rig.py rig --glb spider_static.glb --plan tools/plans/spider_rig.json --out <out> --windup 0.3`(다리 10 · 뼈 25 · IK 빗나감 0, 달리기 2.8mm).
- 박쥐 = `python tools/wing_rig.py rig --glb bat_static.glb --plan tools/plans/bat_rig.json --out <out> --windup 0.3`(날개 FK · 날갯짓·덮치기·맞기·떨어져 엎드림).
- 반입 = `assets/models/spider/spider.glb` · `assets/models/bat/bat.glb` 자리 바꿈 · PD 「합쳐」 2026-10-31.
