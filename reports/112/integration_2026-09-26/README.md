# #112 최신 UI 기준 줍기 전후 (2026-09-26)

main c6e12b3d 기준, 갱신 후보 008ca6e5. 목조 UI·A 아이콘·9칸 장비/HUD 벨트를 유지했다.
고정 `pickup_feedback_view` 4상태(dropped,pull_mid,bag_pulse,reject_mid) 전후 8JPG.
줍기/거절 후 0.075초에 게임 시간을 정지해 촬영한다. before는 기능 파일 7종을 main과 대조한 내용에서 실제로 촬영했으며 이후 후보 바이트를 해시 그대로 복원했다.
일반 게임 입력/상태 검증은 pickup_equip와 audio_cues 등 E2E가 별도로 수행한다. 원본 로그는 게임 본진 tmp/112_*.log에 보존한다.
