# #534 단계 위계 보완 R3 — 2026-10-02

PD의 단계별 판독 피드백으로 상위 HP/MP 4장을 새로 제작했다. 기본2 승인 원화와 현재 게임 PNG·정의·UI는 보존했다. 후보이며 아직 채택/실반입되지 않았다. 이전 R2 생산물은 상위 폴더와 보고서에 유지하고, 이전 게임 JPG6은 보고서 previous_gallery에 바이트 그대로 보존했다.

단계1 소박한 병 → 단계2 넓은 몸통·목재 마개·금속 봉인1줄 → 단계3 육중한 몸통·금속 뚜껑·봉인2줄과 큰 문장. HP는 적갈색 약단지/붉은 끈, MP는 청자 이중 호리병/남색 끈 계열이다. 현재 모든 효능 단계는 ItemDef.tier1/1×1/스택10이며 HP40/80/140·MP25/50/90·ilvl1/6/13을 유지한다.

Comfy Cloud GPT Image 2.5 Flare high 1024² 텍스트 생성4회 + 같은 그래프 BiRefNet-general 알파 분리. 기존 이미지 업로드0. native/clean RGB 차이0, clean alpha0~255. 정확한 prompt/API graph/job ID/history/native/clean PNG와 SHA를 reports/534/2026-10-02_comfy_rank_v3에 보존했다. alpha 수정·수작업 픽셀 그리기·등급 배경·글자·발광은 사용하지 않았다. production game/items의 80px 패킹은 premultiplied Lanczos로 비율을 유지한다.

중요: 현 UiSkin은 알파 여백을 제거하므로 PNG 여백만으로 크기 위계가 적용되지 않는다. 검수판은 현재 UiSkin을 호출하면서 미리보기의 표시 영역에만 단계별0.75/0.86/1.0을 적용했다. 이 정책은 프로덕션 UI에 아직 설치하지 않았다. 채택 뒤 별도 반입 카드에서 아이콘4 연결과 같은 표시 비율을 가방·좌판·벨트·커서에 함께 적용하고 실제 입력·수치·다른 그림 보존을 검수해야 한다. 기본 PNG는 교체할 필요가 없다.

검수: 현 가방40/여백8, 좌판48/여백3, 벨트42/여백8, 축소30/36, 검정·무채색, 이름/숫자를 숨겨 섞은 판6모드. 자동 PASS는 파일 계약과 렌더 실행이며 사람의 판독 정확도를 측정한 결과가 아니다. 매우 작은30px 검수에서 미세 문장·끈은 약하므로 크기·마개·굵은 봉인을 주요 식별점으로 삼는다. JPG6은 게임 docs/art/534_potion_grade에 보존한다.

처음 임포트의 OPENING class-cache 오류는 raw stdout/stderr 전문을 별도로 보존했다. 추가 코드 수정 없이 두 번째 import_cache_retry1이 통과했고 이후6모드는 SCRIPT ERROR/ERROR0이다. runtime_before.json과 verification.json은 그림·정의·UI191파일 SHA 불변, 원본/패킹/SHA, 각 렌더 로그를 대조한다.

재현 자료: qa_godot.gd/qa_godot_blind.gd는 현재 UiSkin·기존 ItemDef를 로드한다. renderer는 정확한 작업 트리/생산 경로와 Godot 실행 파일을 상수로 사용한다. 보고서 reproduction에 당시 준비·큐·생성·패킹·렌더·검증 Python 원본을 그대로 동결했으며 다른 컴퓨터에서는 상수를 실제 경로로 바꿔야 한다. 기존 cloud job을 다시 제출하지 않는다. 같은 이름의 원본·로그·검증 파일이 있으면 준비/렌더/동결 스크립트가 중단한다. 새 검수가 필요하면 별도 run label/출력 폴더로 보존한다.

왜 이 구조인가: 작은 슬롯에서도 부피와 금속 봉인이라는 독립 단서가 남도록 원화와 실제 표시 비율을 함께 고정한다. 패킹 여백만 늘리는 대안은 현 UiSkin에서 효과가 없고 회복 수치 변경은 이 시각 피드백의 범위를 벗어나므로 사용하지 않는다.
