# 새 도호 재리깅 작업 — 2026-09-18

사용자 선택: Tripo 684a9cfb. 사용자 판정: Tripo 자동 리깅 불합격. 메시와 텍스처만 채택 후보로 유지하고 Mixamo 재리깅 + Blender 변형 보정 진행.

원본: C:/Users/FORYOUCOM/Downloads/traditional+hanbok+3d+model.zip
실측: 50,001 triangles, 24,965 vertices, Tripo 41 bones, animation 0.
텍스처: BaseColor 1024², metallic/roughness 512², normal 256². 웹의 고밀도 원본 표시와 다운로드 파일의 밀도는 다르다.

준비 완료:
- 11,999 / 19,999 triangles 후보. 키 1.7m, 발바닥 0. 원본 SHA 유지.
- 12k 정면·측면·후면 렌더 확인: 흑립·도포·적색 끈·주먹 유지.
- doho_684a9cfb_12k_textured_static_mixamo.fbx: 기존 Armature와 vertex groups 제거, 텍스처 포함.
- rigged 이름의 GLB 및 blend는 기존 Tripo 리그 비교/복구용이며 채택본이 아니다.

Mixamo:
- 새 static FBX 업로드 완료. 정면 T포즈 확인.
- 턱·손목·팔꿈치·무릎·사타구니 마커 지정, 대칭 ON.
- 손이 주먹이므로 No Fingers (25) 선택.
- Auto-Rigging 요청 완료, 결과 대기.
- Mixamo 미리보기 재질이 과도하게 반짝인다. 리깅 결과를 받을 때 원본 PBR 재질을 Blender에서 복원하고 다시 검수할 것.

다음 검수: 걷기·검 베기에서 어깨/팔꿈치/소매/도포 변형 확인. 이후 walk/run/attack/hit/die/cast 완성. 의상 웨이트 보정 필요 여부를 실제 포즈로 판정한다. 게임 파일 교체 없음.

결과: Mixamo Auto-Rigging 성공, Review 확인 및 Next 적용 완료. 캐릭터 이름 DOHO_684A9CFB_12K_TEXTURED_STATIC_MIXAMO. T-pose FBX 다운로드 시 Chrome ERR_BLOCKED_BY_CLIENT 발생. 직접 다운로드 요청 중. 원본 재질 복원 및 변형 검수는 아직 미완료.
