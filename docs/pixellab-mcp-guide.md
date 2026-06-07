# PixelLab MCP Guide

이 문서는 다음 세션이 PixelLab 도구 이름, 필드, 기본 모드와 검증 이력을 바로 확인하기 위한 저장소 로컬 가이드다.

- 저장소 작업 원칙: [`../AGENTS.md`](../AGENTS.md)
- 원본 라이브 JSON Schema: [`pixellab-mcp-tools-schema-2026-06-07.json`](pixellab-mcp-tools-schema-2026-06-07.json)
- PixelLab 공식 문서: <https://api.pixellab.ai/mcp/docs>

## 확인 기준

- 라이브 스키마 확인 일시: `2026-06-07 18:38:41 +09:00` (`Asia/Seoul`)
- MCP endpoint: `https://api.pixellab.ai/mcp`
- MCP protocol: `2025-03-26`
- 서버: `PixelLab MCP Server 0.2.0`
- 라이브 `tools/list` 도구 수: `38`
- 표기법: `*`는 JSON Schema의 필수 필드, `=값`은 서버 기본값이다.

공식 문서와 라이브 스키마가 다르면 현재 세션에서 다시 받은 `tools/list`를 우선한다. 이 문서에 없는 세부 타입, 길이, 범위, 중첩 객체 정의는 원본 JSON Schema 스냅샷에서 확인한다.

## 인증과 진단

프로젝트 MCP 설정은 `.codex/config.toml`, 토큰은 Windows 사용자 환경변수 `PIXELLAB_API_TOKEN`을 사용한다.

```powershell
[Environment]::SetEnvironmentVariable("PIXELLAB_API_TOKEN", "<token>", "User")
codex mcp get pixellab
codex mcp list
```

토큰 등록이나 설정 변경 뒤에는 Codex를 완전히 재시작한다. 정상 등록값은 다음과 같다.

```text
transport: streamable_http
url: https://api.pixellab.ai/mcp
bearer_token_env_var: PIXELLAB_API_TOKEN
status: enabled
auth: Bearer token
```

도구가 세션에 나타나지 않으면 생성 요청을 보내지 말고 환경변수, 프로젝트 신뢰 상태, Codex 재시작 여부부터 확인한다.

## 저장소 v3 정책

PixelLab 전체에 공통인 단일 `mode` 필드는 없다. 도구마다 v3 지원 여부가 다르다.

| 작업 | 저장소 기본값 | 정확한 동작 |
| --- | --- | --- |
| 캐릭터 생성 | `create_character.mode: "v3"` | 서버 기본은 `standard`지만 이 저장소는 v3를 명시한다. v3는 2-9 generations, 항상 8방향이다. |
| 커스텀 캐릭터 애니메이션 | `animate_character.mode: "v3"` | `template_animation_id`를 쓰는 템플릿 애니메이션은 `template` 모드를 유지한다. |
| 오브젝트 애니메이션 | `animate_object.mode: "v3"` | 서버 기본도 v3지만 재현성을 위해 명시한다. |
| 오브젝트 생성 | mode 없음 | `create_1_direction_object`, `create_8_direction_object`, `create_map_object`에는 mode 필드가 없다. |
| 타일/타일셋 생성 | mode 없음 | 각 타일 도구의 전용 필드만 사용한다. |

`pro`는 비용 확인이 필요한 예외 모드다. `confirm_cost: true`를 첫 호출에 넣지 않는다. 먼저 비용 응답을 사용자에게 보여주고 명시적 승인 후에만 다시 호출한다.

### v3 캐릭터 생성 예

```json
{
  "description": "Joseon hunter in dark durumagi carrying a short bow",
  "name": "Hunter",
  "body_type": "humanoid",
  "mode": "v3",
  "size": 48,
  "outline": "single color black outline",
  "detail": "medium detail",
  "view": "low top-down"
}
```

v3에서는 `n_directions`, `shading`, `proportions`, `text_guidance_scale`가 무시된다. 항상 8방향이다.

## Character Tools

### `create_character`

캐릭터의 4/8방향 기본 회전을 생성한다. 저장소 기본은 `mode: "v3"`다.

- 필수: `description*`
- 선택: `name=null`
- `body_type="humanoid"`: `humanoid | quadruped`
- `template=null`: quadruped일 때 `bear | cat | dog | horse | lion`
- `mode="standard"`: `standard | pro | v3`
- `n_directions=8`: `4 | 8`
- `proportions="{\"type\":\"preset\",\"name\":\"default\"}"`
- `size=48`: `16..128`
- `outline="single color black outline"`: `single color black outline | single color outline | selective outline | lineless`
- `shading="basic shading"`: `flat shading | basic shading | medium shading | detailed shading`
- `detail="medium detail"`: `low detail | medium detail | high detail`
- `text_guidance_scale=8.0`: `1.0..20.0`
- `view="low top-down"`: `low top-down | high top-down | side | oblique`

### `create_character_state`

완료된 캐릭터의 정체성과 회전을 유지한 상태 변형을 만든다.

- 필수: `character_id*`, `edit_description*`
- 선택: `seed=null`, `use_color_palette_from_reference=false`

### `animate_character`

템플릿 또는 커스텀 캐릭터 애니메이션을 생성한다.

- 필수: `character_id*`
- 선택: `template_animation_id=null`, `action_description=null`, `animation_name=null`, `directions=null`
- `mode=null`: `template | v3 | pro`
- `frame_count=8`: v3에서 `4..16`, 짝수
- `confirm_cost=false`: pro 전용 승인 필드
- `template_animation_id`가 있으면 자동 `template`, 없으면 자동 `v3`
- 방향: `south | north | east | west | south-east | south-west | north-east | north-west`

### `get_character`

- 필수: `character_id*`
- `include_preview=true`

처리 중이면 진행률, 완료되면 회전·애니메이션·다운로드 정보를 반환한다.

### `list_characters`

- `limit=10`
- `offset=0`
- `tags=null`

### `delete_character`

- 필수: `character_id*`
- `confirm=false`

### `delete_animation`

- 필수: `character_id*`, `animation_type*`
- 선택: `direction=null`
- `confirm=false`

## Object Tools

### `create_1_direction_object`

단일 방향 오브젝트 후보를 생성한다. mode 필드는 없다.

- 필수: `description*`
- `size=null`: `32..256`, 생략 시 64
- `view="top-down"`: `top-down | sidescroller`
- `style_images`: `{type:"base64", base64:"...", format:"png"}` 배열
- `item_descriptions=null`

크기에 따라 여러 후보가 생성되면 `review` 상태가 되며 `select_object_frames` 또는 `dismiss_review`로 마무리한다.

### `create_8_direction_object`

동일 오브젝트를 8방향으로 생성한다. mode 필드는 없다.

- 필수: `description*`
- `size=null`: `32..256`, 생략 시 64
- `view="low top-down"`: `low top-down | high top-down | side`
- `reference_image_base64=null`
- `style_image_base64=null`

두 이미지 필드는 상호 배타적이다. 이미지 입력 시 이미지 크기가 출력 크기를 결정한다.

### `get_object`

- 필수: `object_id*`
- `include_preview=true`

상태는 보통 `processing | review | completed | failed`다.

### `list_objects`

- `limit=10`
- `offset=0`
- `tags=null`
- `status_filter=null`

### `animate_object`

완료된 1방향 또는 8방향 오브젝트를 애니메이션한다. 저장소 기본은 명시적 `mode: "v3"`다.

- 필수: `object_id*`
- `mode="v3"`: `pro | v3`
- `animation_description=null`
- `directions=null`
- `frame_count=null`: v3는 짝수 `4..16`, 기본 8
- `animation_group_id=null`
- `display_name=null`
- `replace_existing=false`
- `confirm_cost=false`
- `custom_start_frame_base64=null`
- `end_frame_base64=null`

1방향 오브젝트에는 `directions`를 전달하지 않는다. 8방향 커스텀 시작/종료 프레임은 정확히 한 방향만 허용하므로 사용자가 방향을 선택해야 한다. v3의 8프레임 출력은 입력 기준 프레임을 포함해 조회 시 9프레임으로 보일 수 있다.

### `create_object_state`

- 필수: `object_id*`, `edit_description*`
- `seed=null`

### `delete_object`

- 필수: `object_id*`
- `confirm=false`

### `select_object_frames`

- 필수: `object_id*`, `indices*`
- `common_tag=null`

review 후보의 선택 인덱스를 각각 완료 오브젝트로 승격한다.

### `dismiss_review`

- 필수: `object_id*`

review 후보 전체를 폐기한다.

## Map Object Tools

### `create_map_object`

투명 배경 맵 소품 또는 배경 인페인팅 소품을 생성한다. mode 필드는 없으며 약 8시간 뒤 자동 삭제된다.

- 필수: `description*`
- `width=null`: `32..400`
- `height=null`: `32..400`
- `view="high top-down"`: `low top-down | high top-down | side`
- `outline="single color outline"`: `single color outline | selective outline | lineless`
- `shading="medium shading"`: `flat shading | basic shading | medium shading | detailed shading`
- `detail="medium detail"`: `low detail | medium detail | high detail`
- `background_image=null`: JSON 문자열
- `inpainting=null`: JSON 문자열

기본 생성에서는 `width`, `height`를 지정한다. 배경 이미지가 있으면 크기를 자동 감지할 수 있다.

### `get_map_object`

- 필수: `object_id*`

완료 즉시 반환된 `/download` URL에서 저장한다.

## Top-Down Tileset Tools

### `create_topdown_tileset`

- 필수: `lower_description*`, `upper_description*`
- `transition_size=0.0`
- `transition_description=null`
- `tile_size={"width":16,"height":16}`
- `outline=null`, `shading=null`, `detail=null`
- `view="high top-down"`: `low top-down | high top-down`
- `tile_strength=1.0`
- `lower_base_tile_id=null`, `upper_base_tile_id=null`
- `tileset_adherence=100.0`
- `tileset_adherence_freedom=500.0`
- `text_guidance_scale=8.0`

16개 Wang 타일을 만든다. 연속 지형은 이전 결과의 base tile ID를 다음 호출에 연결한다.

### `get_topdown_tileset`

- 필수: `tileset_id*`

### `list_topdown_tilesets`

- `limit=10`
- `offset=0`

### `delete_topdown_tileset`

- 필수: `tileset_id*`

## Sidescroller Tileset Tools

### `create_sidescroller_tileset`

- 필수: `lower_description*`, `transition_description*`
- `transition_size=0.0`
- `tile_size={"width":16,"height":16}`
- `outline=null`, `shading=null`, `detail=null`
- `tile_strength=1.0`
- `base_tile_id=null`
- `tileset_adherence=100.0`
- `tileset_adherence_freedom=500.0`
- `text_guidance_scale=8.0`
- `seed=null`

### `get_sidescroller_tileset`

- 필수: `tileset_id*`

### `list_sidescroller_tilesets`

- `limit=20`
- `offset=0`

### `delete_sidescroller_tileset`

- 필수: `tileset_id*`

## Isometric Tile Tools

### `create_isometric_tile`

- 필수: `description*`
- `size=32`
- `tile_shape="block"`: `thick tile | thin tile | block`
- `outline="lineless"`
- `shading="basic shading"`
- `detail="medium detail"`
- `text_guidance_scale=8.0`
- `seed=null`

### `get_isometric_tile`

- 필수: `tile_id*`

### `list_isometric_tiles`

- `limit=10`
- `offset=0`

### `delete_isometric_tile`

- 필수: `tile_id*`

## Pro Tile Tools

### `create_tiles_pro`

- 필수: `description*`
- `tile_type="isometric"`: `hex | hex_pointy | isometric | octagon | square_topdown`
- `tile_size=32`
- `tile_height=null`
- `tile_view="low top-down"`: `top-down | high top-down | low top-down | side`
- `tile_view_angle=null`
- `tile_depth_ratio=null`
- `seed=null`
- `style_images=null`
- `style_options=null`
- `outline_mode="outline"`: `outline | segmentation`

### `get_tiles_pro`

- 필수: `tile_id*`

### `list_tiles_pro`

- `limit=10`
- `offset=0`

### `delete_tiles_pro`

- 필수: `tile_id*`

## Account, Project, Support Tools

### `get_balance`

필드 없음. 잔여 USD credit, subscription generation 사용량과 tier를 반환한다.

### `list_projects`

필드 없음. 접근 가능한 PixelLab 프로젝트를 반환한다.

### `agent_help`

- 필수: `question*`

PixelLab 사용법을 공식 지식 에이전트에 질문한다.

### `agent_feedback`

- 필수: `tool_name*`, `feedback_type*`, `message*`
- `feedback_type`: `bug | confusing | suggestion | missing_feature`

## 라이브 목록에 없는 공개 문서 도구

공식 문서에는 chat 및 sandbox 도구가 설명되어 있지만, `2026-06-07 18:38:41 +09:00`의 인증된 `tools/list`에는 노출되지 않았다. 다음 도구가 필요하면 이름을 추정해 호출하지 말고 먼저 새 `tools/list` 스냅샷을 받는다.

- `chat_list_conversations`, `chat_get_messages`, `chat_send_message`
- `sandbox_create_session`, `sandbox_destroy_session`, `sandbox_bash`
- `sandbox_read`, `sandbox_write`, `sandbox_edit`, `sandbox_deploy`, `sandbox_sync`

## 검증 이력

### MCP 인증

- 실시: `2026-06-07 18:30:36 +09:00`
- 결과: `HTTP 200`, `text/event-stream`
- 서버: `PixelLab MCP Server 0.2.0`
- `get_balance`: 성공
- 당시 잔여 subscription generations: `2556`

### PixelLab 생성

- 실시: `2026-06-07 18:33 +09:00`
- 도구: `create_map_object`
- 규격: `32x32`, `high top-down`, 1개
- object ID: `dbbe2209-a282-450c-bcef-bcf1719baedd`
- 상태: `completed`
- 결과: [`../workbench/smoke-tests/2026-06-07/generation-comparison/pixellab_map_object_jangseung_32.png`](../workbench/smoke-tests/2026-06-07/generation-comparison/pixellab_map_object_jangseung_32.png)
- 비고: 이 도구에는 v3 필드가 없다.

### Retro Diffusion 비교 생성

- 실시: `2026-06-07 18:36:19 +09:00`
- API: Retro Diffusion REST
- 스타일: `rd_plus__topdown_item`
- 모델 필드: `RD_FLUX`
- 규격: `32x32`, 1개, seed `20260607`
- 1회 응답 비용: `$0.025`
- 결과: [`../workbench/smoke-tests/2026-06-07/generation-comparison/rd_plus_topdown_item_jangseung_32.png`](../workbench/smoke-tests/2026-06-07/generation-comparison/rd_plus_topdown_item_jangseung_32.png)
- 주의: 중단된 이전 동기 요청이 서버에서 계속 실행되어 총 잔액 감소는 `$0.050`이었다.

## 스키마 갱신 절차

PixelLab 서버 버전이나 도구 필드가 바뀌었으면 다음 순서로 문서를 갱신한다.

1. MCP `initialize`로 서버 버전과 protocol version을 확인한다.
2. 인증된 `tools/list`를 호출한다.
3. 응답의 `result.tools` 전체를 새 날짜의 JSON 파일로 저장한다.
4. 이 문서의 확인 일시, 도구 수, 필드 표와 v3 정책을 갱신한다.
5. `AGENTS.md`의 상세 가이드 링크가 새 문서를 가리키는지 확인한다.
6. 생성 테스트는 사용자가 명시적으로 요청한 경우에만 비용을 알리고 실행한다.
