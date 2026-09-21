# 못골 광장 H1 기준 화면 — #128

**B 추천 · A/B 모두 PD 미채택.** 생성한 목표 원화이며 실제 Godot 반입 결과가 아니다. 아트 제작은 #128, 게임 반입·재질값·조명·실제 입력/동선 검증은 #151(claude).

[원본/A/B 비교 화면](index.html) · [제작 사양](PRODUCTION_SPEC.md) · [최종 프롬프트](PROMPTS.md) · [해시·참조·검수 manifest](manifest.json)

## 결과

| 파일 | 역할 | 크기 | 판정 |
|---|---|---|---|
| references/01_current_plaza_with_ui.png | 최신 실제 게임 | 1280×720 | 0aba611 / DevMode off / UI 포함 |
| references/02_current_plaza_clean.png | 동일 실제 장면, UI·이름표 제외 | 1280×720 | A 편집 대상 |
| A_matte_material_target.png | H1 무광 재질·큰 색면 목표 | 1672×941 | 참고 원화로 검수, PD 선택 대기 |
| B_local_light_target.png | A의 주변 명도·국소 등불 비교 | 1672×941 | 추천, PD 선택 대기 |

내장 `image_gen`으로 A 생성 1회 + B 조명 편집 1회. 요청 규격은 1536×864였으나 실제 반환은 두 장 모두 1672×941. 원본을 리사이즈/페인트로 수정하지 않았으며 비교 페이지에서만 같은 16:9 표시 영역에 맞춰 보여준다. 모델 버전 식별자는 노출되지 않았다.

## 직접 검수와 잔여 차이

- PC/NPC 4명, 우물·좌판·서낭단·집·못의 관계와 이동 공간이 유지된다. H1의 무광 목재·기와·한지와 큰 명암으로 서로 다른 자산의 표현이 가까워졌다.
- 도호 흑립·남색 겹도포·붉은 띠·검/칼집, NPC 역할·고유 복식이 유지된다. 실제 게임의 어깨검은 비스듬한 날 각도까지 이 그림으로 다시 판정하지 않는다.
- A→B에서 추가 배치/디자인 이탈은 보이지 않으며 주변 명도와 등불 대비 변화가 중심이다. B에서도 도호의 갓·남색/적색·발 주변 지면이 읽힌다.
- **실제 원본→A에서 정규화 좌표가 완전히 같지는 않다.** 인물/우물이 다소 위로 이동했고 하단 중앙 울타리 노출이 늘었다. A/B를 배치 도면·좌표/충돌 데이터로 사용하면 안 된다. 실제 원본의 발 위치·건물 영역·길을 정본으로 유지한다.
- 기와·지면·풀의 세부 밀도는 아직 높은 편이다. 게임 크기의 재질로 옮길 때 작은 때/돌 무늬를 낮추고 큰 면을 남긴다.
- 독립 narrative-world 검수: B 추천, 원화 단계 조건부 적합. 픽셀 단위 배치 보존이나 Godot 구현 합격으로 판정하지 않았다.

## #151 게임 인계 기준

1. PD가 A/B 중 지목한 파일·해시를 카드에 기록한다. 원본 그림을 배경판으로 깔아 게임 개선 완료로 처리하지 않는다.
2. 발 위치·NPC3·우물/좌판/집 footprint·기존 길은 실제 캡처/게임 좌표를 따른다. 새로 드러난 하단 중앙 울타리를 원화만 보고 추가하지 않는다.
3. 목재는 넓고 어두운 건조한 면, 기와는 청회색 큰 지붕 덩어리, 회벽/한지는 탁한 따뜻한 중간톤, 바닥은 저대비 흙 패치로 정리한다. 도호·상호작용 대상보다 재질 무늬가 먼저 읽히지 않게 한다.
4. B 선택 시 주변 지붕/외곽 명도와 기존 등불의 작은 광역을 기준으로 적용한다. 배우 발광을 되살리지 않고, 실제 Godot 광원 세기/반경/거칠기 값은 검증 후 기록한다.
5. 처마·기둥·기단·문살의 새 형태는 #129 제작/반입과 연결한다. 이번 PNG는 텍스처 아틀라스나 3D 메시가 아니다.
6. #119 인물 색 정합 결과를 반영하고, 동일 1280×720/size11/광장 위치에서 스크린샷과 실제 이동·상점·귀환 검증을 진행한다. 성능/클릭/충돌은 아직 미검증이다.

## 촬영 재현과 raw 로그

별도 worktree `plaza-art-128` / 기준 0aba611에서 독립 저장 경로 `res://._tmp/plaza128_save.json`을 사용했다. Main을 띄우고 (0,0,1)에서 3초 대기한 뒤 두 컷 모두 Main 처리를 잠깐 멈춰 자세/스크립트 광원을 동일하게 유지했다. 셰이더 TIME은 프레임마다 진행할 수 있다. 두 캡처의 실제 카메라·플레이어 좌표는 동일하다.

Clean에서 숨긴 것은 Main/HUD와 Merchant/Shaman/Elder/Waypoint의 Label3D 네 개뿐이다. 모델·재질·광원·카메라 속성은 바꾸지 않았다. 정확한 목록은 [촬영 manifest](references/capture_manifest.json), 드라이버는 `references/plaza128_capture.gd.txt`와 `.tscn.txt`.

촬영 exit0, `PLAZA128 COMPLETE 2`, SCRIPT ERROR 없음. 종료 시 아래 엔진 리소스 로그가 남았으며 성공 검증에서 숨기지 않는다. [원문](logs/plaza128_capture.txt). 최초 캐시 import에서는 cursor.svg 로딩 오류 뒤 import가 끝났다. [최초 import 전문](logs/plaza128_import.txt). 이번 원화 작업에서 엔진 종료/임포트 문제를 수정했다고 주장하지 않는다.

```text
ERROR: 1 RID allocations of type 'N10RendererRD14TextureStorage7TextureE' were leaked at exit.
ERROR: Parameter "RenderingServer::get_singleton()" is null.
   at: ~CompressedTexture2D (scene/resources/compressed_texture.cpp:464)
WARNING: 2 RIDs of type "Texture" were leaked.
   at: finalize (servers/rendering/rendering_device.cpp:8900)
```

최초 import의 오류 원문:

```text
ERROR: No loader found for resource: res://assets/sprites/ui/skin/cursor.svg (expected type: unknown)
   at: _load (core/io/resource_loader.cpp:332)
```

로그 시작의 `[DevMode] ON`은 오토로드 초기 출력이다. 드라이버가 Main 생성 전에 false로 바꾸었으며 촬영 manifest에 기록했다. 사용자 저장 및 다른 세션 E2E 저장은 사용하지 않았다.
