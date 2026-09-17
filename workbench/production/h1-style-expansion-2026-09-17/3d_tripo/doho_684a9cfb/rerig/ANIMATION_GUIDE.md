# 도호 6종 애니메이션 제작 가이드

선택 모델: 684a9cfb-7c6b-49c9-bdd5-999b81cce3b3. 기존 73b5a120은 이전 비교 자료로 보존.

## 1. 원본 확보와 경량화
Tripo Export에서 FBX, Mixamo, 1K, Skeleton 포함으로 원본을 저장한다. 원본은 별도 보존한다.
현재 웹 표시값은 1,888,037 triangles로 게임용으로는 경량화가 필요하다. 리깅된 모델은 Tripo Retopo에서 지원하지 않는다는 메시지를 확인했다.
Blender에서 원본의 UV·텍스처·웨이트를 유지하며 12,000 / 20,000 triangles 후보를 만든다. 12k는 게임용 비교 기준, 20k는 외형 보존 비교 후보이며 최종 채택값은 아니다. 키 1.7m, 발바닥 0을 맞춘다. 무릎·팔꿈치·소매·갓의 형태와 움직일 때의 찌그러짐을 확인한다.

## 2. Tripo 동작
Animate에서 아래 클립을 각각 적용한다. 첫 클릭은 준비 단계일 수 있으므로 완료 체크 후 다시 눌러 실제 재생을 확인한다.

|게임 이름|Tripo 후보|검수 포인트|
|---|---|---|
|walk|walk|발 미끄러짐, 도포 관통, 루프 연결|
|run|run|걷기와 구분되는 속도감, 무릎 들림|
|attack|slash|검 손잡이 위치, 타격 순간, 복귀 시간|
|hit|hit_to_body_01|짧고 읽히는 반응|
|die|fall|사망 대용 후보일 뿐: 다시 일어나는지, 마지막 자세 확인|
|cast|cast_a_spell|부적 사용 동작에 적합한지 확인|

Export에서 Skeleton을 켜고 Animation Count에서 위 6개를 명시적으로 선택한다. 0개 상태로 내보내면 리깅만 들어가므로 주의한다. 저장된 파일의 실제 클립 개수를 검사해야 완료다.

## 3. Mixamo 비교
같은 경량화 메시로 리깅 없는 텍스처 FBX 사본을 만들고 Mixamo Upload Character에 업로드한다. 턱·손목·팔꿈치·사타구니·무릎 마커를 실제 관절에 맞춘 뒤 자동 리깅한다. 손이 주먹 형태면 손가락 없는 옵션을 우선 시험한다.
Walking / Running / 검 베기 / Hit Reaction / Dying / Casting에 해당하는 후보를 검색하고 모델에 적용한다. 검색 결과의 실제 자세를 보고 선택하며 이름만으로 채택하지 않는다.
이동은 In Place 옵션이 있는 후보를 우선 사용한다. 다운로드는 FBX Binary, 30fps, Keyframe Reduction None을 기준으로 하되 표시되는 설정을 확인한다. 첫 파일은 With Skin, 후속 동작은 같은 캐릭터의 Without Skin으로 저장한다.

## 4. 게임 반입 전 판정
두 방식에서 동일한 6종을 같은 카메라·속도로 비교한다. walk/run만 반복한다. attack/hit/cast는 한 번 재생하고, die는 마지막 자세를 유지한다. cast는 소비형 부적 연출용이며 새 도술 액티브 스킬을 뜻하지 않는다.
스켈레톤·텍스처·클립 목록·실측 삼각형 수를 검사하고, 발 미끄러짐·소매와 다리 관통·갓 변형·무기 소켓을 시각 검수한다. 채택 전에는 기존 게임 모델을 교체하지 않는다.

## 현재 상태 (2026-09-18)
새 모델의 Tripo walk/run/slash/hit_to_body_01/fall/cast_a_spell 6종을 웹에서 준비했다. Export에서 6/9 선택, Skeleton ON, In Place ON, FBX·Mixamo·1K를 확인했다. 파일명은 doho_684a9cfb_tripo_6clips_1k로 준비했다. 6종 파일 내보내기 완료나 Mixamo 비교 완료를 뜻하지 않는다.
새 원본의 자동화 탭 다운로드는 ERR_BLOCKED_BY_CLIENT로 막혔다. 사용자의 직접 다운로드를 기다리는 중이다. 파일이 확보되면 준비된 prepare_candidates.py로 경량화 후보를 만들고 Mixamo 비교를 진행한다.

