# Godot 에셋 배포 파이프라인

> 작성: **OpenAI Codex**
>
> 작성일: 2026-06-07

## 저장소 역할

- `joseon-assets`: 제작 원본, 발주 기록, 생성 결과, 검수와 승인
- `joseon-hunters`: 게임이 실제로 사용하는 런타임 에셋

Godot 프로젝트는 형제 경로인 `../joseon-hunters`에 있다. 에셋 저장소에서
승인한 파일만 manifest를 통해 Godot의 기존 `assets/` 경로로 배포한다.

## 파일

```text
manifests/godot.json       # 사람이 관리하는 배포 목록
manifests/godot.lock.json  # 마지막 publish 결과와 SHA-256
tools/publish_godot.py     # 검사, 변경 계획, 복사, Godot import
```

## Manifest 항목

```json
{
  "id": "icon.item.hp-potion",
  "status": "approved",
  "source": "approved/icons/items/hp_potion.png",
  "target": "assets/sprites/ui/icons/hp_potion.png",
  "kind": "item_icon",
  "generator": "pixellab",
  "director": "openai-codex",
  "constraints": {
    "format": "png",
    "width": 64,
    "height": 64,
    "alpha": true
  }
}
```

### 필드 원칙

- `id`: 경로와 무관한 영구 식별자
- `status`: `approved` 또는 `published`만 배포 대상
- `source`: `joseon-assets` 루트 기준 상대 경로
- `target`: Godot 루트 기준이며 반드시 `assets/` 아래
- `constraints`: 최종 런타임 파일의 형식과 PNG 규격
- `.import`: manifest에 넣지 않는다. Godot이 관리한다.

`draft`, `generated`, `review`, `rejected` 상태는 publish 대상에서 자동으로
제외된다.

## 사용법

### 1. Manifest와 원본 검사

```bash
python3 tools/publish_godot.py check
```

검사 항목:

- source와 target 경로가 각 저장소 밖으로 빠져나가지 않는지
- target이 Godot의 `assets/` 아래인지
- 원본 파일이 존재하는지
- PNG 형식, 너비, 높이, 알파 채널이 제약과 맞는지
- 에셋 ID가 중복되지 않는지

### 2. 변경 계획

```bash
python3 tools/publish_godot.py plan
```

각 항목을 다음 중 하나로 표시한다.

- `SAME`: Godot 파일과 SHA-256이 동일
- `ADD`: Godot에 없는 파일
- `UPDATE`: Godot 파일과 내용이 다름

특정 에셋만 확인할 수 있다.

```bash
python3 tools/publish_godot.py plan \
  --asset icon.item.hp-potion \
  --asset skill.doho.ilsam
```

### 3. 배포

```bash
python3 tools/publish_godot.py publish
```

변경된 파일만 임시 파일을 거쳐 원자적으로 복사하고 SHA-256을 다시
검사한다. 변경이 있으면 마지막에 다음 명령을 실행한다.

```bash
godot --headless --path ../joseon-hunters --import
```

Godot import를 별도로 실행하려면:

```bash
python3 tools/publish_godot.py publish --skip-import
```

다른 checkout을 대상으로 시험할 때는:

```bash
python3 tools/publish_godot.py plan --target /path/to/joseon-hunters
```

## 안전 규칙

- 이 도구는 manifest에 적힌 파일만 복사한다.
- 대상 파일을 자동 삭제하거나 prune하지 않는다.
- Godot 프로젝트의 `.import` 파일과 `.godot/`는 건드리지 않는다.
- 원본과 대상의 SHA-256이 같으면 복사하지 않는다.
- target은 반드시 Godot 프로젝트의 `assets/` 아래여야 한다.
- 기존 Godot 코드와 씬은 publish 도구의 소유 범위가 아니다.

## 승인 및 커밋 순서

1. `joseon-assets`에서 생성본을 검수한다.
2. 승인본을 안정된 source 경로에 둔다.
3. manifest에 `approved` 항목을 추가한다.
4. `check`, `plan`, `publish`를 차례로 실행한다.
5. Godot import 결과와 실제 게임 화면을 검수한다.
6. `joseon-assets`의 manifest, lock, 원본을 커밋한다.
7. `joseon-hunters`의 배포된 런타임 파일을 별도 커밋한다.

두 저장소의 커밋 메시지에는 같은 에셋 ID를 넣어 추적 가능하게 한다.

```text
joseon-assets:
feat(asset): approve icon.item.hp-potion

joseon-hunters:
feat(asset): publish icon.item.hp-potion
```

## 현재 샘플

기존에 두 저장소에 동일하게 존재하는 다음 파일을 manifest에 등록해
파이프라인의 무변경 검증 기준으로 사용한다.

- `cutscene.title.trio`
- `map.prototype.field-map2`

두 항목은 현재 `plan` 결과가 `SAME`이어야 한다.
