# Environment Concept Prompt Template v1

## 용도

마을, 산성, 사당, 무덤, 던전, 시장 등 배경 컨셉과 맵 스타일 앵커를 만든다.

## Reference Set

- style-ref: approved style anchor 1장
- environment-ref: 같은 지역권 또는 건축 언어 앵커 1장

## Template

```text
[COMMON_PROJECT_STYLE_BLOCK]
[REFERENCE_ROLE_BLOCK]

Create a production-ready environment concept for [LOCATION_NAME], [LOCATION_TYPE] in a Joseon dark fantasy action RPG.

Environment identity:
- Setting: [VILLAGE_TOMB_SHRINE_FORTRESS_FOREST_MARKET]
- Time and weather: [TIME_WEATHER]
- Architecture and props: [KOREAN_ARCHITECTURE_MATERIALS]
- Supernatural threat: [GHOST_CURSE_MONSTER_PRESENCE]
- Gameplay readability: clear walkable areas, readable entrance and exit paths, strong focal point.

Composition:
- Camera: [EYE_LEVEL_OR_HIGH_TOPDOWN_OR_WIDE_ESTABLISHING]
- Foreground, midground, background are separated by value.
- Keep key shapes simple enough to translate into tiles, props, and in-game backgrounds.

[OUTPUT_DISCIPLINE_BLOCK]
[NEGATIVE_BLOCK]
```

## Review Checklist

- 조선 건축과 소품이 지역 정체성을 만드는가
- 플레이 가능 구역과 막힌 구역이 구분되는가
- 배경이 너무 회화적으로만 흐르지 않고 에셋화 가능한가
- 같은 지역의 후속 이미지와 조명, 팔레트가 이어지는가
