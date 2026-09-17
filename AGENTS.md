# Joseon Assets Agent Guide

이 저장소는 조선헌터스 시각 에셋 저장소다. 픽셀아트 제작 시 아래 두 도구를 구분해서 사용한다.

## 세션 시작 필독

- PixelLab 상세 사용법과 전체 도구 필드: [`docs/pixellab-mcp-guide.md`](docs/pixellab-mcp-guide.md)
- PixelLab 라이브 JSON Schema 스냅샷: [`docs/pixellab-mcp-tools-schema-2026-06-07.json`](docs/pixellab-mcp-tools-schema-2026-06-07.json)
- Retro Diffusion 상세 API 예제: [`tools/rd-api-examples/README.md`](tools/rd-api-examples/README.md)
- GPT Image 컨셉아트 스타일·프롬프트 세트: [`art-direction/README.md`](art-direction/README.md)
- 반사광, 림라이트, 블룸 억제 프롬프트: [`docs/image-generation-lighting-prompt-guide.md`](docs/image-generation-lighting-prompt-guide.md)

PixelLab 작업 전에는 상세 가이드의 **저장소 v3 정책**, **도구 범주**, **검증 이력**을 먼저 확인한다. 필드가 불확실하면 이름을 추정하지 말고 JSON Schema 스냅샷 또는 새 `tools/list`를 확인한다.

GPT Image 계열로 컨셉아트, 키아트, 캐릭터, 배경을 만들 때는 `art-direction/STYLE_BIBLE.md`와 `art-direction/prompts/`의 템플릿을 먼저 사용한다. `character-ref`, `style-ref`, `environment-ref`는 API 필드명이 아니라 프로젝트 내부 역할 구분이며, 실제 호출에서는 참조 이미지를 배열로 전달하고 프롬프트에 각 이미지 역할을 명시한다.

## PixelLab MCP

PixelLab은 **MCP 도구**로 사용한다. 캐릭터 일관성, 방향별 스프라이트, 애니메이션, 정식 타일셋 제작에 우선 사용한다.

### 설치와 인증

- 공식 MCP 문서: `https://api.pixellab.ai/mcp/docs`
- 프로젝트 설정: `.codex/config.toml`
- MCP URL: `https://api.pixellab.ai/mcp`
- 인증 환경변수: `PIXELLAB_API_TOKEN`
- 토큰은 `.env`, `.env.txt`, `config.toml`에 기록하지 않는다. Windows 사용자 환경변수에 저장한다.

```powershell
[Environment]::SetEnvironmentVariable("PIXELLAB_API_TOKEN", "<token>", "User")
```

환경변수를 등록하거나 프로젝트 MCP 설정을 변경한 뒤에는 Codex를 완전히 재시작한다. 다음 명령으로 등록 상태를 확인한다.

```powershell
codex mcp get pixellab
codex mcp list
```

정상 상태는 `enabled`, transport `streamable_http`, auth `Bearer token`이다. 도구가 현재 세션에 보이지 않으면 생성 호출부터 시도하지 말고 재시작과 환경변수 등록 상태를 먼저 확인한다.

### 주요 도구

- 잔액 확인: `get_balance`
- 캐릭터 생성: `create_character`
- 단방향 오브젝트: `create_1_direction_object`
- 다방향 오브젝트: `create_8_direction_object`
- 캐릭터 애니메이션: `animate_character`
- 오브젝트 애니메이션: `animate_object`
- 후보 조회 및 선택: `get_object`, `select_object_frames`
- 캐릭터/오브젝트 조회: `get_character`, `get_object`
- 맵 오브젝트: `create_map_object`, `get_map_object`
- 탑다운 타일셋: `create_topdown_tileset`, `get_topdown_tileset`
- 목록 조회: `list_characters`, `list_objects`, `list_topdown_tilesets`

### 기본 흐름

1. `get_balance`로 생성량을 확인한다.
2. 생성 도구를 호출하고 반환된 `character_id` 또는 `object_id`를 기록한다.
3. `get_character` 또는 `get_object`로 작업 상태를 조회한다.
4. review 후보가 나오면 `select_object_frames`로 사용할 프레임을 확정한다.
5. 확정된 자산 ID로 `animate_character` 또는 `animate_object`를 호출한다.
6. 완성본을 내려받아 `sprites/`, `maps/` 등 목적 폴더에 정리한다.

### PixelLab v3 기본 규칙

- 이 저장소의 캐릭터 생성 기본값은 `create_character`의 `"mode": "v3"`다. 서버 자체 기본값은 `standard`이므로 반드시 명시한다.
- 커스텀 캐릭터 애니메이션은 `animate_character`의 `"mode": "v3"`를 명시한다. `template_animation_id`를 사용하는 애니메이션은 `template` 모드를 유지한다.
- 오브젝트 애니메이션은 `animate_object`의 `"mode": "v3"`를 명시한다. 서버 기본도 v3지만 재현성을 위해 생략하지 않는다.
- `create_map_object`, `create_1_direction_object`, `create_8_direction_object`에는 `mode` 인자가 없다.
- v3 기본 프레임 수는 방향당 8개다. 입력 기준 프레임까지 저장되어 `get_object`에는 9개로 보일 수 있다.
- 1방향 오브젝트를 애니메이션할 때는 `directions`를 전달하지 않는다.
- 8방향 오브젝트에 커스텀 시작/종료 프레임을 넣을 때는 사용자가 방향을 선택해야 한다.
- `pro`는 사용자가 다른 화풍을 명시적으로 요구한 경우에만 사용한다. 첫 호출에서 `confirm_cost: true`를 넣지 말고 비용을 확인한 뒤 승인을 받는다.

```json
{
  "object_id": "<completed-object-id>",
  "mode": "v3",
  "animation_description": "subtle idle sway",
  "frame_count": 8
}
```

### 검증된 최소 생성 예

`create_map_object`는 빠른 연결 점검에 적합하다. 다음 규격은 2026-06-07에 실제 생성과 PNG 다운로드까지 검증했다.

```json
{
  "description": "small Joseon-era Korean wooden jangseung village guardian totem, single object",
  "width": 32,
  "height": 32,
  "view": "high top-down",
  "outline": "single color outline",
  "shading": "medium shading",
  "detail": "medium detail"
}
```

- 생성 도구: `create_map_object`
- 상태 도구: `get_map_object`
- 테스트 ID: `dbbe2209-a282-450c-bcef-bcf1719baedd`
- 결과: `workbench/smoke-tests/2026-06-07/generation-comparison/pixellab_map_object_jangseung_32.png`
- 실시 시각: `2026-06-07 18:33 +09:00`
- 이 테스트 도구에는 v3 필드가 없다. v3 정책 검증은 라이브 `tools/list` 스키마를 기준으로 한다.
- 맵 오브젝트는 약 8시간 후 자동 삭제되므로 완료 즉시 `download` URL을 저장한다.

### 중요 제약

- 큰 base64 이미지를 MCP 도구 인자에 직접 전달하지 않는다. 약 5 KB 이상은 잘림이나 문자열 손상 위험이 있다.
- `reference_image_base64`, `style_images`, `custom_start_frame_base64`, `background_image`처럼 큰 이미지가 필요한 호출은 `https://api.pixellab.ai/mcp`에 JSON-RPC `tools/call` 형식으로 직접 POST한다.
- HTTP 직호출도 등록된 PixelLab MCP의 동일 Bearer 토큰을 사용한다. 토큰을 코드나 저장소에 기록하지 않는다.
- 레퍼런스 이미지는 검증된 안전 상한인 `128x128` 이하를 사용한다. `256x256` 입력은 작업이 정체된 사례가 있다.
- 개별 Backblaze 프레임 URL은 인증 문제로 직접 다운로드하지 않는다.
- MCP가 반환한 `/download` URL을 사용한다. 공식 MCP 문서상 다운로드 URL 자체에는 별도 인증이 필요하지 않다.
- 서쪽 방향은 가능한 경우 동쪽 프레임의 `flip_h` 재사용을 우선 검토한다.

## Retro Diffusion REST API

Retro Diffusion은 이 저장소에서 **MCP가 아니라 REST API**로 사용한다. 빠른 소품 시안, 탑다운 맵과 아이템, 스킬 아이콘, 배경 제거, 팔레트 및 색상 후처리에 적합하다.

### 인증과 엔드포인트

- API 키: 저장소 루트 `.env`의 `RD_API_KEY`
- 인증 헤더: `X-RD-Token: <RD_API_KEY>`
- 서비스 상태: `GET https://api.retrodiffusion.ai/v1/status`
- 이미지 생성: `POST https://api.retrodiffusion.ai/v1/inferences`
- 편집 도구 목록: `GET https://api.retrodiffusion.ai/v1/edit/tools`
- 편집 실행: `POST https://api.retrodiffusion.ai/v1/edit/tools/{tool_id}`

### 조선헌터스 추천 스타일

- 탑다운 소품: `rd_plus__topdown_asset`
- 탑다운 맵: `rd_plus__topdown_map`
- 작은 탑다운 아이템: `rd_plus__topdown_item`
- 스킬 아이콘: `rd_plus__skill_icon`
- 고품질 범용 에셋: `rd_pro__default`
- 고품질 탑다운 에셋: `rd_pro__topdown`
- 동일 화풍 소품 모음: `rd_pro__spritesheet`

### 생성 요청 규칙

- 핵심 payload: `prompt`, `prompt_style`, `width`, `height`, `num_images`, `seed`
- 이 저장소의 RD 생성 기본 계열은 **RD Plus**다. `prompt_style`은 `rd_plus__...`를 사용한다.
- 모델 필드를 명시해야 할 때는 `RD_FLUX` 또는 `RD_CLASSIC`을 사용한다.
- `rd_plus`, `rd_pro`, `rd_fast` 같은 이름은 모델 필드가 아니라 주로 `prompt_style` 접두사로 사용한다.
- 실제 생성 전에 최종 payload에 `"check_cost": true`만 추가해 비용을 확인한다.
- 승인 후에는 같은 payload에서 `check_cost`만 제거하거나 `false`로 바꾼다. 비용 확인과 실제 생성 사이에 크기, 이미지 수, 스타일을 바꾸지 않는다.
- 배경 제거가 필요하면 `"remove_bg": true`를 사용한다.
- 심리스 텍스처는 `"tile_x": true`, `"tile_y": true`를 사용한다.
- 반환된 `base64_images`를 디코딩해 PNG로 저장한다.
- 긴 작업은 `"async_process": true`로 요청하고 `/v1/inferences/tasks/{task_id}`를 폴링한다.

### 검증된 RD Plus 최소 생성 예

다음 payload는 2026-06-07에 비용 확인과 실제 PNG 생성을 검증했다.

```json
{
  "prompt": "small Joseon-era Korean wooden jangseung village guardian totem, single object, centered",
  "prompt_style": "rd_plus__topdown_item",
  "model": "RD_FLUX",
  "width": 32,
  "height": 32,
  "num_images": 1,
  "seed": 20260607,
  "remove_bg": true
}
```

- 비용 확인: 위 payload에 `"check_cost": true` 추가
- 확인된 1회 비용: `$0.025`
- 응답 모델: `rd_plus`
- 결과: `workbench/smoke-tests/2026-06-07/generation-comparison/rd_plus_topdown_item_jangseung_32.png`
- 생성 응답 전체를 로그에 출력하지 않는다. `base64_images`를 제외한 메타데이터만 출력한다.

### 중단과 재시도

- 동기 생성 명령이 로컬에서 중단돼도 서버 작업과 과금은 계속될 수 있다.
- 중단 직후 같은 요청을 바로 재실행하지 않는다.
- 먼저 응답 파일 생성 여부, 비동기 `task_id`, 잔액 변화를 확인한다.
- 2026-06-07 테스트에서 중단된 RD 요청이 서버에서 계속 실행되어 재시도분과 합쳐 `$0.050`이 차감됐다. 이 사례를 중복 과금 방지 기준으로 삼는다.
- 2026-06-07 `rd_plus__character_turnaround`, `128x128`, 1장 테스트에서 `async_process: true` 요청은 `Internal Server Error`를 반환했으며 `task_id`와 과금은 없었다. 동일 payload의 동기 요청은 성공했다. 이 스타일에서 async 500이 나면 잔액과 task ID 부재를 확인한 뒤 동기 방식으로 한 번만 재시도한다.

### 편집 도구

- `image_edit`: 프롬프트 기반 이미지 수정
- `background_remover`: 배경 제거
- `color_reducer`: 색상 수 축소와 디더링
- `palette_converter`: 지정 팔레트로 변환
- `color_style_transfer`: 레퍼런스의 색감 전이
- `k_centroid_downscale`: 픽셀아트용 다운스케일

### 로컬 예제

- 설정 확인: `tools/rd-api-examples/verify_setup.py`
- text/img2img: `tools/rd-api-examples/img2img.py`
- 편집 API: `tools/rd-api-examples/edit_tools.py`
- RD Plus 생성 예제: `tools/rd-api-examples/test_rd_plus.py`
- 상세 API 문서: `tools/rd-api-examples/README.md`

## 작업 원칙

- 사용자가 생성 실행을 요청하지 않았다면 유료 생성 호출을 하지 않는다.
- 비용이 발생하는 호출 전에는 도구, 스타일, 해상도, 이미지 수를 명확히 한다.
- API 키, Bearer 토큰, base64 원문을 로그나 문서에 남기지 않는다.
- 생성 결과는 먼저 비교 가능한 시안으로 보존하고, 승인 전 기존 공식 에셋을 덮어쓰지 않는다.
- 캐릭터 공식 레퍼런스는 `sheets/`, 승인된 픽셀 결과는 `sprites/`, 승인된 맵 결과는 `maps/`에 둔다.
- 새 결과는 `inbox/`에 임시 저장하고 같은 세션 안에 분류한다. 미승인 후보·프로브·테스트는 `workbench/`로 이동한다.
- 정리 규칙과 현재 구조는 `README.md`, 정리 이력은 `docs/ASSET_CLEANUP_LOG_2026-06-07.md`를 따른다.
