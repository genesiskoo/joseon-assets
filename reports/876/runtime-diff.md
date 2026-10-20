# #876 자료관 runtime 다시 맞추기 (2026-10-20)

정본 `catalog/characters/catalog.json`에 `--check`를 돌리면 오류가 89건(#820 때 86 + #840 뒤 같은 원인) 났다. 모두 `assets[*].runtime.bindings[*].dependencies`에 남은 옛 해시였다. 10-13 이후 다른 착륙에서 의존 파일이 바뀌었기 때문이다. 추가 등록분의 오류는 없었다.

## 한 일 (ops §1·§3·§4)

1. `--refresh-runtime --output <새 파일>`로 runtime_inventory를 새로 뽑았다(정본은 덮어쓰지 않음).
2. 옛 목록과 비교했다. 연결 대상(`runtime_id`·`resource_path`)은 바인딩 55와 초상 10 그대로이고, 늘거나 준 것은 없다. 바뀐 것은 의존 해시이며, 일부는 설정 본문도 함께 바뀌었다.
   - 공통: `actors/actor_visual.gd` · `actors/model_def.gd` · `actors/enemy_def.gd`
   - 보스 4: `definition_config`(boss_*.tres)와 `boss*.gd`
   - 도호: `model_config`(`doho_run_stop0~13.res` 추가) · `player.gd` · `player_combat.gd`
   - 마을 NPC: `world/town.tscn` · 각 `.dialogue`
   - GLB 재반입: bandit_v2 · bat · talisman_master_v2 · boss_bulgasari · plague_dog · spider
   - 초상 `speaker_usage`: 도호에 ending·gumiho 대본 추가 · 무당에 ending 추가 · **gumiho_f03는 `event/gumiho.dialogue` 화자가 생겨 definition_only → connected**
3. 정본 반영:
   - `runtime_inventory`를 새 목록으로 바꿨다.
   - 각 asset의 `runtime.bindings` 사본 29개를 새 목록의 같은 바인딩으로 바꿨다.
   - `runtime-gumiho_f03-idle-atlas`의 `runtime.connection`을 connected로 바꾸고 메모를 남겼다. 로드와 월드 표시는 not_checked 그대로다.
   - 캡처 최신성은 `freshness()` 결과를 따랐다. `card744-render-*` 7개를 current → **stale**로 바꾸고, 바뀐 캡처 의존성을 메모에 적었다(`project.godot` · `world/iso_camera.gd` 포함).
   - `card744-world-*` 6개는 원래 indeterminate였고 그대로 뒀다.
   - `issues`에 `card876-runtime-refresh` 1건을 추가했다.
4. 보존: decision·capture(옛 dependencies와 fingerprint)·file·provenance·runtime.load/world_display/evidence는 손대지 않았다(HEAD 대조 스크립트로 확인). load success 증거는 옛 의존성을 기준으로 한 기록이며, 이번에 재로드나 재촬영은 하지 않았다.

## 결과

- `catalogue-checks.before.json`: 반영 전 dry-run(오류 89)
- `catalogue-checks.json`: 반영 후 `--check` — **ok · errors 0 · warnings 0** · capture stale 7 / indeterminate 6
- 미확인 범위: stale 캡처 7개(도호·상인·무당·촌장·억쇠·주모·구미호 보스 렌더)는 다시 찍지 않았다. 필요하면 별도 카드에서 다시 찍는다.
