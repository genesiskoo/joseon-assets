# Character Concept Prompt Template v1

## 용도

주요 캐릭터, NPC, 보스의 컨셉아트와 마스터 시트 후보를 만든다.

## Reference Set

- style-ref: approved style anchor 1장
- character-ref: 기존 캐릭터가 있으면 승인본 1~2장
- prop-ref: 시그니처 무기나 부적이 있으면 1장

## Template

```text
[COMMON_PROJECT_STYLE_BLOCK]
[REFERENCE_ROLE_BLOCK]

Create a production-ready character concept for [CHARACTER_NAME], [ROLE_OR_CLASS] in a Joseon dark fantasy action RPG.

Character identity:
- Age and presence: [AGE_AND_ATTITUDE]
- Silhouette: [KEY_SHAPE_LANGUAGE]
- Face and hair: [FACE_HAIR]
- Costume: [HANBOK_ARMOR_LAYERING]
- Signature item: [WEAPON_OR_PROP]
- Supernatural motif: [GHOST_TALISMAN_CURSE_MOTIF]

Sheet requirements:
- Full body front view as the main figure.
- Add 2 to 3 small callout details for weapon, talisman, mask, fabric pattern, or accessory.
- Keep pose calm and readable, not a battle splash illustration.
- Use a neutral simple background.

[OUTPUT_DISCIPLINE_BLOCK]
[NEGATIVE_BLOCK]
```

## Review Checklist

- 기존 캐릭터와 얼굴, 헤어, 복식이 충돌하지 않는가
- 전신 실루엣이 작은 썸네일에서도 읽히는가
- 무기와 소품이 픽셀 스프라이트로 줄여도 남는 형태인가
- 배경이 캐릭터 판독을 방해하지 않는가
