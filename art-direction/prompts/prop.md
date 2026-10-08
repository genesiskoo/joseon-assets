# Prop Prompt Template v1

## 용도

무기, 부적, 탈, 장승, 제기, 아이템, 던전 소품의 컨셉과 픽셀아트 변환용 레퍼런스를 만든다.

## Reference Set

- style-ref: approved style anchor 1장
- prop-ref: 같은 재질이나 문양 앵커가 있으면 1장

## Template

```text
[COMMON_PROJECT_STYLE_BLOCK]
[REFERENCE_ROLE_BLOCK]

Create a production-ready prop concept for [PROP_NAME], [PROP_FUNCTION] in a Joseon dark fantasy action RPG.

Prop identity:
- Shape: [SILHOUETTE]
- Material: [WOOD_METAL_PAPER_CLOTH_BONE_STONE]
- Age and wear: [WEATHERING]
- Cultural motif: [JOSEON_MOTIF]
- Supernatural detail: [TALISMAN_GHOST_FIRE_CURSE_MARK]

Presentation:
- Single centered object.
- Neutral background.
- Add one small side view or material callout if useful.
- Shape must remain readable at 32x32 and 64x64.

[OUTPUT_DISCIPLINE_BLOCK]
[NEGATIVE_BLOCK]
```

## Review Checklist

- 32px로 축소해도 실루엣이 남는가
- 재질이 한눈에 보이는가
- 과한 장식이 기능을 흐리지 않는가
- 탑다운, 인벤토리 아이콘, 배경 소품 중 어디에 쓸지 명확한가
